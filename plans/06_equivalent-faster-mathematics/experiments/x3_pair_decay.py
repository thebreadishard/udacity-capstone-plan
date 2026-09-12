#!/usr/bin/env python
"""Plan 06, experiment X3 (direction S1): how fast do pair correlation energies decay with the distance between
localised occupied orbitals in an aromatic molecule?  First own number for the locality question.

Method (cheap, DFT-free, CC-free): RHF/cc-pVTZ with density fitting, Pipek-Mezey localisation of the active occupied
orbitals (same as plan 05's LNO engine uses), then the MP2 pair energies e_ij in the LMO basis (semicanonical pair
formula via the full canonical amplitudes rotated to LMOs), and the LMO centroid distances r_ij.  Prints the pair
energies against distance, an exponential fit ln|e_ij| = a - r_ij/lambda on the tail, and the share of the
correlation energy carried by pairs beyond 2, 3, 4 Angstrom.  MP2 pair energies are the quantity LNO thresholds are
built on, so this is the locality LNO sees.

Run inside WSL (~/qc05):   python x3_pair_decay.py --molecule naphthalene   (geometry from plan 05 results_dryrun)
Rules: no run while an anchor job is active (one anchor job at a time); output JSON + Markdown beside this script.
"""
import argparse, json, math, sys, time
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
PLAN05 = HERE.parents[2] / "05_delta-probed-ir-pipeline"


def geometry(molecule):
    """Bohr coordinates from plan 05's dry-run stage A (benzene) or geometry.json (naphthalene)."""
    if molecule == "benzene":
        a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
        return a["symbols"], np.array(a["coords_bohr"])
    g = json.load(open(PLAN05 / f"probes/results_dryrun/{molecule}/geometry.json"))
    for k in ("coords_bohr", "coords"):
        if k in g:
            return g["symbols"], np.array(g[k])
    raise SystemExit(f"no coordinates in geometry.json for {molecule}: keys {list(g)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", default="naphthalene")
    ap.add_argument("--basis", default="cc-pvtz")
    ap.add_argument("--threads", type=int, default=8)
    a = ap.parse_args()
    from pyscf import gto, scf, lo, mp, lib
    lib.num_threads(a.threads)
    symbols, coords = geometry(a.molecule)
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords)], unit="Bohr", basis=a.basis, verbose=3)
    n_core = sum(1 for s in symbols if s == "C")          # frozen core: 1s per carbon (plan 05 convention)
    t0 = time.time()
    mf = scf.RHF(mol).density_fit().run()
    t_scf = time.time() - t0
    nocc = mol.nelectron // 2
    occ_act = mf.mo_coeff[:, n_core:nocc]
    lmo = lo.PipekMezey(mol, occ_act).kernel()             # (nao, n_act)
    # canonical MP2 amplitudes, then rotate the occupied indices to LMOs
    pt = mp.dfmp2.DFMP2(mf) if hasattr(mp, "dfmp2") else mp.MP2(mf)
    pt.frozen = n_core
    pt.run()
    t2 = pt.t2                                              # (i, j, a, b) canonical active occupied
    S = mf.get_ovlp()
    U = occ_act.T @ S @ lmo                                 # canonical -> LMO rotation, (n_act, n_act)
    e_ia = mf.mo_energy[n_core:nocc]; e_ab = mf.mo_energy[nocc:]
    # pair energies in the canonical basis, then transform: e_ij(LMO) = sum_kl U_ki U_lj e_kl-like requires the
    # amplitude-integral contraction per pair; do it explicitly via the antisymmetrised contraction in LMO basis
    from pyscf.ao2mo import general
    n_act = U.shape[1]; nvir = e_ab.size
    t2_l = np.einsum("ki,lj,klab->ijab", U, U, t2, optimize=True)
    # (ia|jb) in LMO-occ / canonical-vir basis
    eri = general(mol if not hasattr(mf, "with_df") else mf.with_df, (lmo, mf.mo_coeff[:, nocc:], lmo, mf.mo_coeff[:, nocc:]), compact=False) \
        if not hasattr(mf, "with_df") else mf.with_df.ao2mo((lmo, mf.mo_coeff[:, nocc:], lmo, mf.mo_coeff[:, nocc:]), compact=False)
    eri = np.asarray(eri).reshape(n_act, nvir, n_act, nvir)
    e_pair = np.einsum("iajb,ijab->ij", eri, 2 * t2_l - t2_l.transpose(0, 1, 3, 2), optimize=True)
    e_corr_check = float(e_pair.sum())
    # LMO centroids and distances (Angstrom)
    with mol.with_common_orig((0, 0, 0)):
        r_ao = mol.intor("int1e_r", comp=3)
    cent = np.einsum("xpq,pi,qi->ix", r_ao, lmo, lmo) * 0.529177210903
    d = np.linalg.norm(cent[:, None, :] - cent[None, :, :], axis=-1)
    iu = np.triu_indices(n_act, 1)
    pairs = sorted(zip(d[iu], np.abs(2 * e_pair[iu]) if False else np.abs(e_pair[iu] + e_pair[iu[1], iu[0]])), key=lambda x: x[0])
    r = np.array([p[0] for p in pairs]); e = np.array([p[1] for p in pairs])
    tail = r > 2.0
    slope, inter = np.polyfit(r[tail], np.log(e[tail] + 1e-30), 1) if tail.sum() > 3 else (np.nan, np.nan)
    lam = -1.0 / slope if slope < 0 else float("inf")
    total_offdiag = e.sum(); diag = float(np.abs(np.diag(e_pair)).sum())
    shares = {f">{x} A": float(e[r > x].sum() / (total_offdiag + diag)) for x in (2.0, 3.0, 4.0, 5.0)}
    out = dict(molecule=a.molecule, basis=a.basis, n_active_occ=int(n_act), n_pairs=int(len(r)), e_corr_mp2_pyscf=float(pt.e_corr),
               e_corr_from_pairs=e_corr_check, t_scf_s=round(t_scf, 1), t_total_s=round(time.time() - t0, 1),
               decay_length_angstrom_tail_gt_2A=float(lam), fit_points=int(tail.sum()),
               share_of_correlation_beyond=shares, max_pair_distance_A=float(r.max()),
               pairs=[dict(r_A=round(float(x), 3), abs_e_pair_mEh=round(float(y) * 1000, 4)) for x, y in zip(r, e)],
               date=f"{datetime.now():%Y-%m-%d %H:%M}", printed_by="plans/06_equivalent-faster-mathematics/experiments/x3_pair_decay.py")
    json.dump(out, open(HERE / f"x3_{a.molecule}_{a.basis}.json", "w"), indent=1)
    L = [f"# X3 — MP2 pair-energy decay with LMO distance — {a.molecule}, {a.basis} — {out['date']}", "",
         f"Active occupied LMOs {n_act}, pairs {len(r)}; E_corr(MP2) = {pt.e_corr:.6f} E_h (sum of pair energies {e_corr_check:.6f}); SCF {t_scf:.0f} s, total {out['t_total_s']} s.", "",
         f"Exponential fit on pairs with r > 2 Å ({tail.sum()} pairs): decay length λ = {lam:.2f} Å (|e_ij| ∝ exp(−r/λ)).", "",
         "Share of the correlation energy in pairs beyond a distance: " + ", ".join(f"{k}: {v:.1%}" for k, v in shares.items()), "",
         "| r (Å) | |e_ij| (mE_h) |", "|---|---|"] + [f"| {x:.2f} | {y*1000:.4f} |" for x, y in zip(r, e)]
    (HERE / f"x3_{a.molecule}_{a.basis}.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:8]))


if __name__ == "__main__":
    main()
