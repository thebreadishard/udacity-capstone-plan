#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""factory → stage A adapter (2026-09-14; mandate ledger idea I10, and the input probe M3 needs tonight).

Writes results_dryrun/<molecule>/stageA.json and stageA_hessians.npz in exactly the layout of
dryrun_dft_delta_recovery.py's stage A, from the Module 05 corpus factory's stored Hessians
(modules/05_support_predictor/corpus/molecules/<id>/{geometry.json, hessian_b3lyp.npz, hessian_wb97x.npz}).
The "low" arm is B3LYP/6-31G* as in stage A; the "high" arm is the factory's ωB97X (recorded as such in the
JSON: functionals {"low": "b3lyp", "high": "wb97x"}), i.e. the SECOND DFT–DFT stand-in of I10, not the BHHLYP
one of queue item 5 — stage A proper (BHHLYP) still runs there. The mode basis (L, omega_au, Minv, families)
depends only on the low arm, so probes that need the DFT modes (M1/M3's displacement directions) are unaffected
by which high arm sits beside it. Reuses stage A's own functions (assign_families, pick_totally_symmetric) so
the labels are identical by construction. Numpy only; no quantum chemistry.

Usage: python factory_to_stageA.py --molecule naphthalene --id A_01f3186607 [--force]
"""
import argparse
import json
import os
import sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dryrun_dft_delta_recovery import AMU_TO_ME, HARTREE_TO_CM, BASIS, assign_families, pick_totally_symmetric  # noqa: E402

CORPUS = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus", "molecules")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", required=True)
    ap.add_argument("--id", required=True, help="manifest id of the factory job, e.g. A_01f3186607")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    src = os.path.join(CORPUS, a.id)
    out = os.path.join(HERE, "results_dryrun", a.molecule)
    os.makedirs(out, exist_ok=True)
    if os.path.exists(os.path.join(out, "stageA.json")) and not a.force:
        sys.exit(f"{out}/stageA.json exists (a real stage A?) — refusing to overwrite without --force")
    g = json.load(open(os.path.join(src, "geometry.json")))
    symbols = list(g["symbols"]); coords = np.array(g["coords_bohr"], float); masses_amu = np.array(g["masses_amu"], float)
    natom = len(symbols)
    hess = {"low": np.load(os.path.join(src, "hessian_b3lyp.npz"))["H_raw"], "high": np.load(os.path.join(src, "hessian_wb97x.npz"))["H_raw"]}
    res_factory = json.load(open(os.path.join(src, "result.json")))
    # --- identical to stage A from here (dryrun_dft_delta_recovery.py, "mass-weighted Hessian of the low arm → modes")
    m_me = np.repeat(masses_amu * AMU_TO_ME, 3)
    Minv = 1.0 / np.sqrt(m_me)
    F_low = hess["low"] * np.outer(Minv, Minv)
    F_high = hess["high"] * np.outer(Minv, Minv)
    lam, L = np.linalg.eigh(F_low)
    order = np.argsort(np.abs(lam)); keep = np.sort(order[6:])
    lam_v, L_v = lam[keep], L[:, keep]
    omega_au = np.sqrt(np.abs(lam_v)); freq_cm = omega_au * HARTREE_TO_CM
    srt = np.argsort(freq_cm); omega_au, freq_cm, L_v = omega_au[srt], freq_cm[srt], L_v[:, srt]
    M = len(freq_cm)
    D2_direct_Q = L_v.T @ (F_high - F_low) @ L_v
    s = 1.0 / np.sqrt(omega_au); D2_direct = D2_direct_Q * np.outer(s, s)
    dfreq_first_order_cm = (np.diag(D2_direct_Q) / (2.0 * omega_au)) * HARTREE_TO_CM
    lam_h = np.linalg.eigvalsh(F_high); lam_h = np.sort(lam_h[np.argsort(np.abs(lam_h))[6:]])
    freq_high_cm = np.sqrt(np.abs(lam_h)) * HARTREE_TO_CM
    families = assign_families(freq_cm, L_v, symbols, Minv, coords)
    ts_index = pick_totally_symmetric(L_v, Minv, coords, symbols, freq_cm)
    # --- end of the copied block
    # consistency with the factory's own projected frequencies (it projects translations/rotations before diagonalising)
    f_fac = np.sort(np.array(np.load(os.path.join(src, "hessian_b3lyp.npz"))["freq_cm"]))[6:]
    max_dev = float(np.max(np.abs(np.sort(freq_cm) - f_fac))) if len(f_fac) == M else float("nan")
    res = {
        "molecule": a.molecule, "symbols": symbols, "coords_bohr": coords.tolist(), "masses_amu": masses_amu.tolist(),
        "natom": natom, "M": M, "functionals": {"low": "b3lyp", "high": "wb97x"}, "basis": BASIS,
        "timing": {"source": "corpus factory", **{k: v for k, v in res_factory.get("timings_s", {}).items()}},
        "freq_low_cm": freq_cm.tolist(), "freq_high_direct_cm": freq_high_cm.tolist(), "dfreq_first_order_cm": dfreq_first_order_cm.tolist(),
        "families": families, "totally_symmetric_index": int(ts_index),
        "machine": res_factory.get("machine", ""), "threads": None, "psi4": None,
        "adapter": {"script": "factory_to_stageA.py", "date": f"{datetime.now():%Y-%m-%d %H:%M}", "factory_id": a.id,
                    "note": "high arm = wB97X (I10 second stand-in), not BHHLYP; low-arm modes identical to a stage A run on the same Hessian",
                    "max_abs_dev_vs_factory_projected_freq_cm": max_dev},
    }
    np.savez(os.path.join(out, "stageA_hessians.npz"), H_low=hess["low"], H_high=hess["high"], L=L_v, omega_au=omega_au,
             D2_direct=D2_direct, D2_direct_Q=D2_direct_Q, Minv=Minv, coords=coords)
    json.dump(res, open(os.path.join(out, "stageA.json"), "w"), indent=1)
    print(f"{a.molecule}: M = {M} modes, families {dict((f, families.count(f)) for f in sorted(set(families)))}, totally symmetric index {ts_index} ({freq_cm[ts_index]:.1f} cm-1); max |dev| vs factory projected frequencies {max_dev:.3f} cm-1")
    print("| i | nu_low (cm-1) | family | dnu first-order wB97X-B3LYP (cm-1) |"); print("|---|---|---|---|")
    for i in range(M):
        print(f"| {i} | {freq_cm[i]:.1f} | {families[i]} | {dfreq_first_order_cm[i]:.1f} |")


if __name__ == "__main__":
    main()
