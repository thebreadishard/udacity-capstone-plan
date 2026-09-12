"""X7 (defined 2026-09-12; script written the same evening, NOT RUN — needs PySCF in WSL, after the anchor job) — does the pair-energy decay
length λ scale with the HOMO–LUMO gap, benzene → naphthalene → pyrene? (direction S1: the rate-∝-gap prediction of the decay theorems)

For each molecule (geometries: benzene and naphthalene from plan 05's dry-run files, pyrene from plan 02's stored B3LYP/6-31G* geometry in
git 57a7910), at cc-pVDZ:
  1. DF-RHF, then Pipek–Mezey localisation of the valence occupied orbitals (frozen core = number of carbons), LMO centroids;
  2. DF-MP2 pair energies e_ij (the same quantity X3b read from the naphthalene LNO log), tabulated against the centroid distance r_ij;
  3. a log-linear fit of the median |e_ij| per distance shell for r ≥ R_MIN gives λ (Å per factor e), as in X3b;
  4. the HOMO–LUMO gap from a B3LYP/6-31G* single point at the same geometry (the DFT gap of the T3 statement) and the RHF gap.
Printed per molecule: λ, the gap(s), λ·gap, and the fraction of the correlation energy beyond 3 Å (X3b's second number).
Pre-stated losing condition for "rate ∝ gap" (Orientation §7): λ·gap varies by more than a factor two across the three molecules.

Runs in WSL:  wsl ~/qc05/bin/python plans/06_equivalent-faster-mathematics/experiments/x7_decay_vs_gap.py [--threads 8] [--basis cc-pvdz]
Windows self-test (numpy only):  python x7_decay_vs_gap.py --geometries-only
Every number printed comes from the files or the run; constants in CONSTANTS."""
import argparse
import json
import os
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PLAN05 = REPO / "plans/05_delta-probed-ir-pipeline"
BOHR_TO_A = 0.529177210903
HARTREE_TO_EV = 27.211386245988
CONSTANTS = {"basis_default": "cc-pvdz", "dft_functional": "b3lyp", "dft_basis": "6-31g*", "R_MIN_A": 1.0, "shell_width_A": 0.5, "far_cut_A": 3.0,
             "git_commit_pyrene": "57a7910", "pyrene_file": "plans/02_coupled-cluster-anharmonic-ir/probes/batch_results/06_freq_pyrene.npz",
             "losing_condition": "lambda*gap varies by more than a factor 2 across benzene, naphthalene, pyrene"}


def geometries():
    a = json.load(open(PLAN05 / "probes/results_dryrun/benzene/stageA.json"))
    g = json.load(open(PLAN05 / "probes/results_dryrun/naphthalene/geometry.json"))
    mols = {"benzene": (a["symbols"], np.array(a["coords_bohr"])), "naphthalene": (g["symbols"], np.array(g["coords_bohr"]))}
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "pyrene.npz"
        with open(out, "wb") as f:
            subprocess.run(["git", "-C", str(REPO), "show", f"{CONSTANTS['git_commit_pyrene']}:{CONSTANTS['pyrene_file']}"], check=True, stdout=f)
        with np.load(out) as z:
            m = z["masses_amu"]; X = z["coords_bohr"].copy()
    mols["pyrene"] = (["C" if x > 6 else "H" for x in m], X)
    return mols


def lam_fit(r, e):
    """λ from a log-linear fit of the median |e| per shell of width shell_width_A for r ≥ R_MIN (X3b's rule)."""
    w = CONSTANTS["shell_width_A"]; shells = {}
    for ri, ei in zip(r, e):
        if ri >= CONSTANTS["R_MIN_A"]:
            shells.setdefault(round(ri / w) * w, []).append(abs(ei))
    xs = np.array(sorted(shells)); ys = np.log([np.median(shells[x]) for x in xs])
    slope, icpt = np.polyfit(xs, ys, 1)
    return float(-1.0 / slope), [(float(x), len(shells[x]), float(np.exp(y))) for x, y in zip(xs, ys)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default=CONSTANTS["basis_default"]); ap.add_argument("--threads", type=int, default=8); ap.add_argument("--geometries-only", action="store_true")
    args = ap.parse_args()
    mols = geometries()
    if args.geometries_only:
        for name, (sym, X) in mols.items():
            D = np.linalg.norm(X[:, None] - X[None], axis=2); cc = [D[i, j] for i in range(len(sym)) for j in range(i + 1, len(sym)) if sym[i] == sym[j] == "C" and D[i, j] < 3.0]
            print(f"{name}: C{sym.count('C')}H{sym.count('H')}, {len(cc)} C–C bonds, mean {np.mean(cc)*BOHR_TO_A:.3f} Å")
        print("geometries OK (numpy only; PySCF not touched)")
        return
    os.environ.setdefault("OMP_NUM_THREADS", str(args.threads))
    from pyscf import gto, scf, mp, lo, dft
    out = {"date": f"{datetime.now():%Y-%m-%d %H:%M}", "constants": CONSTANTS, "basis": args.basis, "molecules": []}
    for name, (sym, X) in mols.items():
        t0 = time.time()
        mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, X)], unit="Bohr", basis=args.basis, verbose=0, max_memory=8000)
        mf = scf.RHF(mol).density_fit(); mf.conv_tol = 1e-10; mf.kernel()
        ncore = sym.count("C"); nocc = mol.nelectron // 2
        gap_hf = float((mf.mo_energy[nocc] - mf.mo_energy[nocc - 1]) * HARTREE_TO_EV)
        C_val = mf.mo_coeff[:, ncore:nocc]
        C_loc = lo.PipekMezey(mol, C_val).kernel()
        # LMO centroids
        r_ao = mol.intor("int1e_r"); S = mf.get_ovlp()
        cent = np.array([[float(C_loc[:, i] @ r_ao[k] @ C_loc[:, i]) for k in range(3)] for i in range(C_loc.shape[1])])
        # canonical MP2 amplitudes, then the pair-energy matrix rotated exactly into the localised occupied basis (E_ij is bilinear in i, j)
        ptc = mp.MP2(mf, frozen=ncore); e_corr, t2 = ptc.kernel()
        eris_ovov = ptc.ao2mo(mf.mo_coeff)  # (ia|jb)
        nvir = mol.nao - nocc; nact = nocc - ncore
        ovov = np.asarray(eris_ovov.ovov).reshape(nact, nvir, nact, nvir)
        # pair energy matrix in canonical basis: E_ij = sum_ab t2[i,j,a,b] * (2 (ia|jb) - (ib|ja))
        Eij = np.einsum("ijab,iajb->ij", t2, 2 * ovov - ovov.transpose(0, 3, 2, 1))
        U = C_val.T @ S @ C_loc                      # canonical → localised rotation (nact × nact)
        Eloc = U.T @ Eij @ U                         # bilinear transform of the pair-energy matrix
        r = np.array([np.linalg.norm(cent[i] - cent[j]) * BOHR_TO_A for i in range(nact) for j in range(i + 1, nact)])
        e = np.array([Eloc[i, j] + Eloc[j, i] for i in range(nact) for j in range(i + 1, nact)])
        lam, shells = lam_fit(r, e)
        far = float(np.sum(np.abs(e[r > CONSTANTS["far_cut_A"]])) / np.sum(np.abs(e)))
        # DFT gap at the same geometry
        mold = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, X)], unit="Bohr", basis=CONSTANTS["dft_basis"], verbose=0, max_memory=8000)
        mk = dft.RKS(mold).density_fit(); mk.xc = CONSTANTS["dft_functional"]; mk.kernel()
        no = mold.nelectron // 2; gap_dft = float((mk.mo_energy[no] - mk.mo_energy[no - 1]) * HARTREE_TO_EV)
        out["molecules"].append({"molecule": name, "nC": sym.count("C"), "e_corr_mp2": float(e_corr), "trace_check_pair_sum_vs_e_corr": float(Eloc.sum() - e_corr),
                                 "lambda_A": lam, "shells": shells, "frac_corr_beyond_3A": far, "gap_hf_eV": gap_hf, "gap_dft_eV": gap_dft,
                                 "lambda_times_gap_dft": lam * gap_dft, "seconds": time.time() - t0})
        print(f"{name}: lambda {lam:.3f} A, DFT gap {gap_dft:.2f} eV, HF gap {gap_hf:.2f} eV, lambda*gap {lam*gap_dft:.3f}, beyond 3 A {far*100:.1f} %, pair-sum check {Eloc.sum()-e_corr:.1e} [{time.time()-t0:.0f} s]", flush=True)
    vals = [m["lambda_times_gap_dft"] for m in out["molecules"]]
    out["lambda_gap_ratio_max_over_min"] = float(max(vals) / min(vals)); out["losing_condition_met"] = out["lambda_gap_ratio_max_over_min"] > 2.0
    json.dump(out, open(HERE / "x7_decay_vs_gap.json", "w"), indent=1)
    L = [f"# X7 — pair-energy decay length λ against the HOMO–LUMO gap ({args.basis} MP2; B3LYP/6-31G* gap; {out['date']})", "",
         "| molecule | C | λ (Å) | DFT gap (eV) | HF gap (eV) | λ·gap_DFT | correlation beyond 3 Å | pair-sum check |", "|---|---|---|---|---|---|---|---|"]
    for m in out["molecules"]:
        L.append(f"| {m['molecule']} | {m['nC']} | **{m['lambda_A']:.3f}** | {m['gap_dft_eV']:.2f} | {m['gap_hf_eV']:.2f} | **{m['lambda_times_gap_dft']:.3f}** | {100*m['frac_corr_beyond_3A']:.1f} % | {m['trace_check_pair_sum_vs_e_corr']:.1e} |")
    L += ["", f"λ·gap max/min across the three: **{out['lambda_gap_ratio_max_over_min']:.2f}** — losing condition (> 2) {'MET' if out['losing_condition_met'] else 'not met'}.",
          "", f"Losing condition (pre-stated): {CONSTANTS['losing_condition']}. Rate ∝ gap predicts λ ∝ 1/gap, i.e. constant λ·gap.", "", "Constants: " + json.dumps(CONSTANTS)]
    (HERE / "x7_decay_vs_gap.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L).encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
