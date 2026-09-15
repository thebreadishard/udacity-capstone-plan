#!/usr/bin/env python
"""M4 — the cation price (mandate-ledger obstacle 9; decision 39: cations at rungs 1–2). Written 2026-09-15.

Question: what does one unrestricted LNO-CCSD(T) energy (pyscf-forge `ULNOCCSD_T`, whose (T) part is a NumPy
reference kernel) cost against the restricted energy of the same molecule at the same geometry, basis and
thresholds?  The ratio c prices the cation rows of P27 §5.  Nothing here is a deck energy; the sealed-energy rule
of the benzene decks is respected anyway: at benzene the log prints times and diagnostics, not energies.

Stages (one new thing per machine slot, the 2026-09-14 rule):
  --stage smoke    (1) the shipped unit test `pyscf/lno/test/test_ulnoccsd.py` (water dimer, minutes);
                   (2) the methyl radical CH3 (doublet) in cc-pVDZ: ULNOCCSD_T at the tight thresholds against
                       canonical UCCSD(T) — the check that the unrestricted local path reproduces the canonical
                       one on a radical, with <S^2> printed.  Memory well under 1 GB.
  --stage timing   the molecule of results_dryrun/<molecule>/ at its stage-A geometry: (a) the neutral, RHF +
                   PM + LNOCCSD_T (the restricted path of the decks, fresh localiser); (b) the cation at the same
                   geometry (vertical), UHF (with a stability round) + PM per spin + ULNOCCSD_T.  Prints wall
                   times, resident memory, the UHF <S^2>, fragment counts and c.

Usage (WSL, quiet machine, through launch_detached.sh for the heartbeat):
  launch_detached.sh results_m4/smoke.log  m4_cation_timing.py --stage smoke
  launch_detached.sh results_m4/benzene.log m4_cation_timing.py --stage timing --molecule benzene --thresh tight
"""
import argparse
import json
import os
import platform
import resource
import subprocess
import sys
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_m4")
THRESH = {"normal": [1e-5, 1e-6], "tight": [1e-6, 1e-7], "xtight": [1e-7, 1e-8]}   # as m1_frozen_spaces.py


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2


def pm_localise(mol, orbocc):
    """Pipek–Mezey with the Jacobi stability sweep of the shipped test (avoids a saddle point)."""
    from pyscf import lo
    mlo = lo.PipekMezey(mol, orbocc)
    c = mlo.kernel()
    for _ in range(100):
        # pyscf 2.14: stability_jacobi(return_status=True) returns (mo_coeff, stable); the shipped pyscf-forge test still
        # unpacks the older (stable, mo_coeff) and therefore fails on this pyscf (found 2026-09-15, Software Changes Ledger)
        c1, stable = mlo.stability_jacobi(return_status=True)
        if stable:
            break
        mlo = lo.PipekMezey(mol, c1)
        mlo.init_guess = None
        c = mlo.kernel()
    return c


def run_uhf(mol, conv_tol=1e-11, max_stability_rounds=3):
    """DF-UHF with up to three internal-stability rounds (a cation at a degenerate geometry may first land on a saddle)."""
    from pyscf import scf
    mf = scf.UHF(mol).density_fit()
    mf.conv_tol = conv_tol
    mf.max_cycle = 200
    mf.kernel()
    rounds = 0   # stability rounds actually taken
    for _ in range(max_stability_rounds):
        mo_new, _, stable, _ = mf.stability(return_status=True)
        if stable:
            break
        rounds += 1
        mf.kernel(dm0=mf.make_rdm1(mo_new, mf.mo_occ))
    if not mf.converged:
        raise RuntimeError("UHF did not converge")
    return mf, rounds


def run_rhf(mol, conv_tol=1e-11):
    from pyscf import scf
    mf = scf.RHF(mol).density_fit()
    mf.conv_tol = conv_tol
    mf.kernel()
    if not mf.converged:
        raise RuntimeError("RHF did not converge")
    return mf


def ulno_energy(mf, frozen, thresh, verbose_imp=2):
    """ULNOCCSD_T with one fragment per PM LMO in each spin, as the shipped test does; returns energies and counts."""
    from pyscf.lno.ulnoccsd import ULNOCCSD_T
    mol = mf.mol
    orbloc, frag = [], []
    for s in range(2):
        nocc_s = int(np.count_nonzero(mf.mo_occ[s]))
        occ = mf.mo_coeff[s][:, frozen:nocc_s]
        orbloc.append(pm_localise(mol, occ))
    frag = [[[i], []] for i in range(orbloc[0].shape[1])] + [[[], [i]] for i in range(orbloc[1].shape[1])]
    mlno = ULNOCCSD_T(mf, orbloc, frag, frozen=frozen)
    mlno.lno_thresh = list(thresh)
    mlno.verbose_imp = verbose_imp
    mlno.kernel()
    return {"e_corr_lno_ccsd": float(mlno.e_corr_ccsd), "e_corr_lno_ccsd_t": float(mlno.e_corr_ccsd_t),
            "e_corr_lno_pt2": float(mlno.e_corr_pt2), "n_frag_alpha": orbloc[0].shape[1], "n_frag_beta": orbloc[1].shape[1]}


def rlno_energy(mf, frozen, thresh, verbose_imp=2):
    from pyscf.lno import LNOCCSD_T
    mol = mf.mol
    nocc = int(np.count_nonzero(mf.mo_occ))
    lo0 = pm_localise(mol, mf.mo_coeff[:, frozen:nocc])
    frag = [[i] for i in range(lo0.shape[1])]
    mlno = LNOCCSD_T(mf, lo0, frag, frozen=frozen)
    mlno.lno_thresh = list(thresh)
    mlno.verbose_imp = verbose_imp
    mlno.kernel()
    return {"e_corr_lno_ccsd": float(mlno.e_corr_ccsd), "e_corr_lno_ccsd_t": float(mlno.e_corr_ccsd_t),
            "e_corr_lno_pt2": float(mlno.e_corr_pt2), "n_frag": lo0.shape[1]}


def stage_smoke(args):
    from pyscf import gto, mp, cc, lno as _lno
    rec = {"stage": "smoke", "date": f"{datetime.now():%Y-%m-%d %H:%M}", "node": platform.node(), "threads": args.threads}
    # (1) the shipped unit test, run as a subprocess so its /dev/null output handling cannot touch ours
    test = os.path.join(os.path.dirname(_lno.__file__), "test", "test_ulnoccsd.py")
    t0 = time.time()
    log(f"shipped test: {test}")
    p = subprocess.run([sys.executable, test], capture_output=True, text=True)   # the file runs unittest.main() itself
    tail = (p.stderr or p.stdout).strip().splitlines()[-6:]
    rec["shipped_test"] = {"returncode": p.returncode, "wall_s": time.time() - t0, "tail": tail}
    log(f"shipped test: returncode {p.returncode}, {time.time()-t0:.0f} s; last lines: {' | '.join(tail)}")
    # (2) CH3 radical, cc-pVDZ, doublet: canonical UCCSD(T) against ULNOCCSD_T at the chosen thresholds
    mol = gto.M(atom="C 0 0 0; H 0 1.079 0; H 0.9345 -0.5395 0; H -0.9345 -0.5395 0", basis="cc-pvdz", spin=1,
                charge=0, verbose=0, max_memory=4000, symmetry=False)
    frozen = 1
    t0 = time.time(); mf, rounds = run_uhf(mol); t_scf = time.time() - t0
    s2, mult = mf.spin_square()
    log(f"CH3 UHF: {t_scf:.1f} s, stability rounds {rounds}, <S^2> {s2:.4f} (2S+1 = {mult:.4f})")
    t0 = time.time()
    mmp = mp.UMP2(mf, frozen=frozen).run()
    mcc = cc.UCCSD(mf, frozen=frozen); eris = mcc.ao2mo(); mcc.kernel(eris=eris)
    e_t = mcc.ccsd_t(eris=eris); t_can = time.time() - t0
    t1diag = None
    try:
        t1diag = float(mcc.get_t1_diagnostic())
    except Exception:  # noqa: BLE001
        pass
    log(f"CH3 canonical: UMP2 {mmp.e_corr:.8f}, UCCSD {mcc.e_corr:.8f}, (T) {e_t:.8f} E_h; {t_can:.1f} s; T1 diag {t1diag}")
    t0 = time.time(); u = ulno_energy(mf, frozen, THRESH[args.thresh]); t_ulno = time.time() - t0
    d_ccsd = (u["e_corr_lno_ccsd"] - mcc.e_corr) * 1e6
    d_ccsd_t = (u["e_corr_lno_ccsd_t"] - (mcc.e_corr + e_t)) * 1e6
    log(f"CH3 ULNOCCSD_T {args.thresh}: {u['n_frag_alpha']}+{u['n_frag_beta']} fragments, {t_ulno:.1f} s; "
        f"LNO − canonical: CCSD {d_ccsd:+.2f} µE_h, CCSD(T) {d_ccsd_t:+.2f} µE_h; peak RSS {rss_gb():.2f} GB")
    rec["ch3"] = {"basis": "cc-pvdz", "thresh": args.thresh, "frozen": frozen, "t_scf_s": t_scf, "stability_rounds": rounds,
                  "s2": float(s2), "e_corr_ump2": float(mmp.e_corr), "e_corr_uccsd": float(mcc.e_corr), "e_t": float(e_t),
                  "t1_diagnostic": t1diag, "t_canonical_s": t_can, "ulno": u, "t_ulno_s": t_ulno,
                  "lno_minus_canonical_ccsd_uEh": d_ccsd, "lno_minus_canonical_ccsd_t_uEh": d_ccsd_t, "peak_rss_gb": rss_gb()}
    return rec


def stage_timing(args):
    from pyscf import gto
    dry = os.path.join(HERE, "results_dryrun", args.molecule)
    a = json.load(open(os.path.join(dry, "stageA.json")))
    coords = np.load(os.path.join(dry, "stageA_hessians.npz"))["coords"]
    symbols = a["symbols"]
    frozen = sum(1 for s in symbols if s != "H")
    rec = {"stage": "timing", "molecule": args.molecule, "basis": args.basis, "thresh": args.thresh, "frozen": frozen,
           "date": f"{datetime.now():%Y-%m-%d %H:%M}", "node": platform.node(), "threads": args.threads,
           "geometry": "stage-A reference geometry of the neutral (the cation point is vertical)"}
    atom = [(s, tuple(c)) for s, c in zip(symbols, coords)]

    def make(charge, spin):
        return gto.M(atom=atom, unit="Bohr", basis=args.basis, charge=charge, spin=spin, verbose=0,
                     max_memory=args.max_memory, symmetry=False)

    if not args.skip_neutral:
        mol = make(0, 0)
        t0 = time.time(); mf = run_rhf(mol); t_scf = time.time() - t0
        t0 = time.time(); r = rlno_energy(mf, frozen, THRESH[args.thresh]); t_r = time.time() - t0
        log(f"{args.molecule} neutral RHF {t_scf:.0f} s; LNOCCSD_T {args.thresh}: {r['n_frag']} fragments, {t_r:.0f} s; peak RSS {rss_gb():.2f} GB")
        rec["neutral"] = {"t_scf_s": t_scf, "t_lno_s": t_r, "n_frag": r["n_frag"], "peak_rss_gb": rss_gb(),
                          "energies_not_printed": r}   # kept in the JSON only
    mol = make(1, 1)
    t0 = time.time(); mf, rounds = run_uhf(mol); t_scf = time.time() - t0
    s2, mult = mf.spin_square()
    log(f"{args.molecule}+ UHF {t_scf:.0f} s, stability rounds {rounds}, <S^2> {s2:.4f} (2S+1 = {mult:.4f})")
    t0 = time.time(); u = ulno_energy(mf, frozen, THRESH[args.thresh]); t_u = time.time() - t0
    log(f"{args.molecule}+ ULNOCCSD_T {args.thresh}: {u['n_frag_alpha']}+{u['n_frag_beta']} fragments, {t_u:.0f} s; peak RSS {rss_gb():.2f} GB")
    rec["cation"] = {"t_scf_s": t_scf, "stability_rounds": rounds, "s2": float(s2), "t_ulno_s": t_u,
                     "n_frag_alpha": u["n_frag_alpha"], "n_frag_beta": u["n_frag_beta"], "peak_rss_gb": rss_gb(),
                     "energies_not_printed": u}
    if "neutral" in rec:
        c = t_u / rec["neutral"]["t_lno_s"]
        rec["c_cation_over_neutral"] = c
        log(f"c = t(cation ULNOCCSD_T) / t(neutral LNOCCSD_T) = {c:.2f}  (same geometry, basis {args.basis}, thresholds {args.thresh})")
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", choices=["smoke", "timing"], required=True)
    ap.add_argument("--molecule", default="benzene")
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--thresh", default="tight", choices=list(THRESH))
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--max-memory", type=int, default=20000, help="pyscf max_memory in MB (22 GB cap for the laptop's WSL)")
    ap.add_argument("--skip-neutral", action="store_true", help="timing stage: cation only (the neutral's time is known)")
    args = ap.parse_args()
    from pyscf import lib
    lib.num_threads(args.threads)
    os.makedirs(OUT, exist_ok=True)
    log(f"M4 {args.stage}: {args.molecule} {args.basis} {args.thresh}, {args.threads} threads, pyscf {__import__('pyscf').__version__}")
    t_start = time.time()
    rec = stage_smoke(args) if args.stage == "smoke" else stage_timing(args)
    rec["wall_total_s"] = time.time() - t_start
    name = "m4_smoke.json" if args.stage == "smoke" else f"m4_timing_{args.molecule}_{args.basis}_{args.thresh}.json"
    json.dump(rec, open(os.path.join(OUT, name), "w"), indent=1)
    log(f"written {name}")


if __name__ == "__main__":
    main()
