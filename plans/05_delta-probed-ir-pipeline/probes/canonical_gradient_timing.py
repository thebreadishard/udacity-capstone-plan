#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probe 1b, gradient branch — one canonical CCSD(T) analytic gradient of benzene at cc-pVTZ on the
B2 laptop (plan 05, Ladder §3 anchor-basis bullet; Budget §4.1b). Prints wall-clock per stage,
peak resident memory and the gradient norm, so the 72-gradient full-reference count can be
extrapolated from a measured gradient-to-energy factor instead of a typed one.

Runs in WSL:  wsl ~/qc05/bin/python plans/05_delta-probed-ir-pipeline/probes/canonical_gradient_timing.py [--basis cc-pvtz] [--threads 8]
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import resource
import time
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
STAGEA = os.path.join(HERE, "results_dryrun", "benzene", "stageA.json")
OUT = os.path.join(HERE, "results_timing")


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def rss_gb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default="cc-pvtz")
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    from pyscf import gto, scf, cc, lib
    lib.num_threads(args.threads)
    a = json.load(open(STAGEA))
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(a["symbols"], np.array(a["coords_bohr"]))], unit="Bohr",
                basis=args.basis, verbose=0, max_memory=24000, symmetry=False)
    rec = {"basis": args.basis, "nbf": mol.nao_nr(), "threads": args.threads, "machine": platform.node()}
    log(f"canonical CCSD(T) gradient, benzene {args.basis}, {mol.nao_nr()} bf, {args.threads} threads")
    t0 = time.time()
    mf = scf.RHF(mol)          # conventional integrals: the CC gradient code needs the exact ERIs
    mf.conv_tol = 1e-10
    mf.kernel()
    rec["t_scf_s"] = time.time() - t0
    log(f"RHF {rec['t_scf_s']:.1f} s")
    t0 = time.time()
    mycc = cc.CCSD(mf, frozen=6)
    mycc.conv_tol = 1e-9
    mycc.kernel()
    rec["t_ccsd_s"] = time.time() - t0
    rec["e_corr_ccsd"] = float(mycc.e_corr)
    log(f"CCSD {rec['t_ccsd_s']:.1f} s, peak {rss_gb():.2f} GB")
    t0 = time.time()
    try:
        from pyscf.grad import ccsd_t as ccsd_t_grad
        g = ccsd_t_grad.Gradients(mycc).kernel()
        rec["t_gradient_ccsd_t_s"] = time.time() - t0
        rec["grad_norm"] = float(np.linalg.norm(g))
        rec["grad_max_abs"] = float(np.max(np.abs(g)))
        rec["peak_rss_gb"] = rss_gb()
        log(f"CCSD(T) gradient {rec['t_gradient_ccsd_t_s']:.1f} s ({rec['t_gradient_ccsd_t_s']/60:.1f} min), "
            f"|g| = {rec['grad_norm']:.2e}, peak {rec['peak_rss_gb']:.2f} GB")
    except Exception as e:  # noqa: BLE001
        rec["gradient_error"] = f"{type(e).__name__}: {str(e)[:300]}"
        rec["peak_rss_gb"] = rss_gb()
        log(f"CCSD(T) gradient failed after {time.time()-t0:.0f} s: {rec['gradient_error']}")
    os.makedirs(OUT, exist_ok=True)
    json.dump(rec, open(os.path.join(OUT, f"benzene_{args.basis}_canonical_gradient.json"), "w"), indent=1)
    print(json.dumps(rec, indent=1))
    print("Printed by probes/canonical_gradient_timing.py. A timing at the equilibrium geometry; the gradient is Δ₁-class information only.")


if __name__ == "__main__":
    main()
