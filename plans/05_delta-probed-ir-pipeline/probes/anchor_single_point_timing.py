#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probe 4 — single-point timing at the anchor level (plan 05, probes/README item 4; Budget §4.4).

One LNO-CCSD(T) energy of benzene (pyscf-forge, PM-localised occupied orbitals, one fragment
per LMO, frozen core) at the B3LYP/6-31G* geometry of the dry run, in cc-pVDZ and cc-pVTZ,
with wall-clock per stage, peak resident memory, basis size and the correlation energies
printed. Also one canonical CCSD(T) at cc-pVDZ as the cheap reference point. A timing only:
no Δ, no displaced geometry, no frozen-space object (that is probe M1).

Runs in WSL:  wsl ~/qc05/bin/python plans/05_delta-probed-ir-pipeline/probes/anchor_single_point_timing.py
              [--basis cc-pvdz cc-pvtz] [--threads 8] [--thresh tight|normal] [--no-canonical]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import sys
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STAGEA = os.path.join(HERE, "results_dryrun", "benzene", "stageA.json")
OUT = os.path.join(HERE, "results_timing")
THRESH = {"normal": [1e-5, 1e-6], "tight": [1e-6, 1e-7]}   # [occ, vir] LNO thresholds; γ = 10 as in the code's tests


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def peak_rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2   # kB → GB on Linux


def load_geometry():
    a = json.load(open(STAGEA))
    return a["symbols"], np.array(a["coords_bohr"])


def run_one(basis, threads, thresh_name, canonical, out):
    from pyscf import gto, scf, lo, lib
    from pyscf.lno import LNOCCSD_T
    lib.num_threads(threads)
    symbols, coords = load_geometry()
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords)], unit="Bohr", basis=basis,
                verbose=0, max_memory=24000, symmetry=False)
    rec = {"basis": basis, "nbf": mol.nao_nr(), "natom": mol.natm, "threads": threads,
           "lno_thresh": THRESH[thresh_name], "thresh_name": thresh_name,
           "machine": platform.node(), "python": sys.version.split()[0]}
    log(f"{basis}: {mol.nao_nr()} basis functions")
    t0 = time.time()
    mf = scf.RHF(mol).density_fit()
    mf.conv_tol = 1e-10
    mf.kernel()
    rec["t_scf_s"] = time.time() - t0
    rec["e_scf"] = float(mf.e_tot)
    rec["scf_converged"] = bool(mf.converged)
    log(f"{basis}: RHF(DF) {rec['t_scf_s']:.1f} s, E = {mf.e_tot:.8f}")

    frozen = 6  # carbon 1s
    t0 = time.time()
    nocc = int(np.count_nonzero(mf.mo_occ))
    orbocc = mf.mo_coeff[:, frozen:nocc]
    mlo = lo.PipekMezey(mol, orbocc)
    lo_coeff = mlo.kernel()
    for _ in range(100):   # Jacobi sweeps until stable (the code's own test recipe)
        lo1, stable = mlo.stability_jacobi(return_status=True)   # pyscf 2.14: (mo_coeff, stable)
        if stable:
            break
        mlo = lo.PipekMezey(mol, lo1)
        mlo.init_guess = None
        lo_coeff = mlo.kernel()
    rec["t_localise_s"] = time.time() - t0
    rec["n_lmo"] = int(lo_coeff.shape[1])
    log(f"{basis}: PM localisation {rec['t_localise_s']:.1f} s, {lo_coeff.shape[1]} LMOs")

    frag_lolist = [[i] for i in range(lo_coeff.shape[1])]
    t0 = time.time()
    mcc = LNOCCSD_T(mf, lo_coeff, frag_lolist, frozen=frozen)
    mcc.lno_thresh = THRESH[thresh_name]
    mcc.verbose = 3
    mcc.kernel()
    rec["t_lno_ccsd_t_s"] = time.time() - t0
    rec["e_corr_pt2"] = float(mcc.e_corr_pt2)
    rec["e_corr_ccsd"] = float(mcc.e_corr_ccsd)
    rec["e_corr_ccsd_t"] = float(mcc.e_corr_ccsd_t)
    rec["e_tot_lno_ccsd_t"] = float(mf.e_tot + mcc.e_corr_ccsd_t)
    rec["peak_rss_gb_after_lno"] = peak_rss_gb()
    log(f"{basis}: LNO-CCSD(T) {rec['t_lno_ccsd_t_s']:.1f} s, E_corr(T) = {mcc.e_corr_ccsd_t:.8f}, "
        f"peak RSS {rec['peak_rss_gb_after_lno']:.2f} GB")

    if canonical:
        from pyscf import cc
        from pyscf.cc.ccsd_t import kernel as CCSD_T
        t0 = time.time()
        try:
            mycc = cc.CCSD(mf, frozen=frozen)
            eris = mycc.ao2mo()
            mycc.kernel(eris=eris)
            et = CCSD_T(mycc, eris=eris, verbose=0)
            rec["t_canonical_ccsd_t_s"] = time.time() - t0
            rec["e_corr_canonical_ccsd"] = float(mycc.e_corr)
            rec["e_corr_canonical_ccsd_t"] = float(mycc.e_corr + et)
            rec["lno_minus_canonical_ccsd_t_uEh"] = (rec["e_corr_ccsd_t"] - rec["e_corr_canonical_ccsd_t"]) * 1e6
            rec["peak_rss_gb_after_canonical"] = peak_rss_gb()
            log(f"{basis}: canonical CCSD(T) {rec['t_canonical_ccsd_t_s']:.1f} s, "
                f"LNO − canonical = {rec['lno_minus_canonical_ccsd_t_uEh']:.1f} µE_h, peak RSS {rec['peak_rss_gb_after_canonical']:.2f} GB")
        except Exception as e:  # noqa: BLE001
            rec["canonical_error"] = f"{type(e).__name__}: {str(e)[:200]}"
            log(f"{basis}: canonical CCSD(T) failed: {rec['canonical_error']}")
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, f"benzene_{basis}_{thresh_name}.json"), "w"), indent=1)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", nargs="+", default=["cc-pvdz", "cc-pvtz"])
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--thresh", default="tight", choices=list(THRESH))
    ap.add_argument("--no-canonical", action="store_true")
    ap.add_argument("--canonical-basis", default="cc-pvdz", help="run the canonical CCSD(T) reference only in this basis")
    args = ap.parse_args()
    log(f"anchor single-point timing on {platform.node()}, {args.threads} threads, thresholds {args.thresh} = {THRESH[args.thresh]}")
    results = []
    for b in args.basis:
        results.append(run_one(b, args.threads, args.thresh, canonical=(not args.no_canonical and b == args.canonical_basis), out=OUT))
    print("\n# Anchor single-point timing — benzene at the dry-run B3LYP/6-31G* geometry — "
          f"{datetime.now():%Y-%m-%d %H:%M}, {platform.node()} (WSL), {args.threads} threads, LNO thresholds {THRESH[args.thresh]}")
    print("| basis | nbf | RHF(DF) s | PM s | LNO-CCSD(T) s | peak RSS GB | E_corr LNO-CCSD(T) | canonical CCSD(T) s | LNO − canonical µE_h |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in results:
        print(f"| {r['basis']} | {r['nbf']} | {r['t_scf_s']:.0f} | {r['t_localise_s']:.0f} | {r['t_lno_ccsd_t_s']:.0f} | "
              f"{r.get('peak_rss_gb_after_canonical', r['peak_rss_gb_after_lno']):.2f} | {r['e_corr_ccsd_t']:.6f} | "
              f"{r.get('t_canonical_ccsd_t_s', float('nan')):.0f} | {r.get('lno_minus_canonical_ccsd_t_uEh', float('nan')):.1f} |")
    print("\nPrinted by probes/anchor_single_point_timing.py. A timing; no Δ, no displaced geometry.")


if __name__ == "__main__":
    main()
