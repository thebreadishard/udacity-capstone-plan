#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Probe M1, truth line — canonical CCSD(T) (frozen core, same DF-RHF reference as the three arms) at the
same 27 benzene geometries as `m1_frozen_spaces.py`, so each arm's smoothness AND bias can be read
against the exact answer in that basis instead of against another arm. Affordable only at cc-pVDZ
(27 s per point in the timing probe); at cc-pVTZ one canonical point costs 755 s.

Prints, per mode and arm, the residual σ of (E_arm − E_canonical) about a degree-4 fit in q and the
even-part coefficients a2 (q²) and a4 (q⁴) of that difference; 2·a2 is the bias the arm would put on the
CC curvature of that mode (E = ½ ω q² in the dimensionless normal coordinate), given in cm⁻¹. Absolute
energies are sealed, not printed (they would make Δ₂ diagonal elements readable before the note).

Runs in WSL:  wsl ~/qc05/bin/python plans/05_delta-probed-ir-pipeline/probes/m1_canonical_truth.py [--basis cc-pvdz] [--thresh normal] [--threads 8]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import time
from datetime import datetime

import numpy as np

import m1_frozen_spaces as M1

HARTREE_CM = 219474.6313632


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis", default="cc-pvdz")
    ap.add_argument("--thresh", default="normal")
    ap.add_argument("--tag", default="")
    ap.add_argument("--threads", type=int, default=8)
    ap.add_argument("--energy", default="lno_ccsd_t", choices=["lno_ccsd_t", "composite"],
                    help="arm energy compared: the bare LNO-CCSD(T) correlation energy, or the composite "
                         "LNO-CCSD(T) + [MP2(full) − MP2(LNO)] that the LNO literature reports")
    args = ap.parse_args()
    from pyscf import lib, cc
    from pyscf.cc.ccsd_t import kernel as CCSD_T
    lib.num_threads(args.threads)
    out = os.path.join(M1.OUT, f"benzene_{args.basis}_{args.thresh}{args.tag}")
    a = json.load(open(os.path.join(M1.DRYRUN, "stageA.json")))
    z = np.load(os.path.join(M1.DRYRUN, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols, freq, fam = a["symbols"], np.array(a["freq_low_cm"]), a["families"]
    sealed_path = os.path.join(out, "canonical_truth_sealed.json")
    truth = json.load(open(sealed_path)) if os.path.exists(sealed_path) else {"points": []}
    done = {(p["mode"], round(p["q"], 6)) for p in truth["points"]}
    arms = json.load(open(os.path.join(out, "m1_sealed_energies.json")))
    wanted = [(p["mode"], p["q"]) for p in arms["points"]]
    M1.log(f"canonical truth line: benzene {args.basis}, {len(wanted)} arm points, {len(done)} already done, {args.threads} threads")
    for m, q in wanted:
        if (m, round(q, 6)) in done:
            continue
        t0 = time.time()
        v = np.zeros(len(omega)); v[m] = q
        x = coords0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
        mol = M1.make_mol(symbols, x, args.basis)
        mf = M1.run_scf(mol)
        mycc = cc.CCSD(mf, frozen=M1.FROZEN_CORE)
        mycc.conv_tol = 1e-10
        eris = mycc.ao2mo()
        mycc.kernel(eris=eris)
        if not mycc.converged:
            raise RuntimeError(f"CCSD did not converge at mode {m} q={q}")
        et = CCSD_T(mycc, eris=eris, verbose=0)
        truth["points"].append({"mode": int(m), "q": float(q), "e_scf": float(mf.e_tot), "e_corr_ccsd": float(mycc.e_corr),
                                "e_corr_ccsd_t": float(mycc.e_corr + et)})
        json.dump(truth, open(sealed_path, "w"))
        open(sealed_path.replace(".json", ".sha256"), "w").write(hashlib.sha256(json.dumps(truth, sort_keys=True).encode()).hexdigest())
        M1.log(f"mode {m} q={q:+.2f}: canonical CCSD(T) done, {time.time()-t0:.0f} s")

    # ---------------- comparison (differences only)
    tr = {(p["mode"], round(p["q"], 6)): p for p in truth["points"]}
    ekey = {"lno_ccsd_t": "e_corr_lno_ccsd_t", "composite": "e_corr_composite"}[args.energy]
    suffix = "" if args.energy == "lno_ccsd_t" else "_composite"
    lines = [f"# Probe M1 — arms against canonical CCSD(T) — benzene {args.basis}, arm energy = {ekey}, {datetime.now():%Y-%m-%d %H:%M}, {platform.node()} (WSL)",
             "", "Difference E_arm − E_canonical (same DF-RHF reference, frozen core) at each point; fitted per mode as a degree-4 "
             "polynomial in q. σ = residual about that fit (the arm's roughness against the truth). a2, a4 = even-part coefficients "
             "of the difference (a0 + a2 q² + a4 q⁴ fitted to ½[d(q)+d(−q)]); **2·a2 is the bias the arm puts on the CC curvature** "
             "of the mode, given also in cm⁻¹ (E = ½ ω q²). Absolute energies sealed (`canonical_truth_sealed.json`), not printed.",
             "", "| mode | family | ω (cm⁻¹) | arm | n | σ about deg-4 fit (µE_h) | a2 (µE_h) | a4 (µE_h) | curvature bias 2·a2 (µE_h) | ≈ Δω (cm⁻¹) | d(±1) even (µE_h) | d(±0.5) even (µE_h) |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    summary = {}
    for m in sorted({p["mode"] for p in arms["points"]}):
        pts = [p for p in arms["points"] if p["mode"] == m and (m, round(p["q"], 6)) in tr]
        pts.sort(key=lambda p: p["q"])
        q = np.array([p["q"] for p in pts])
        for arm in "ABC":
            d = np.array([p[arm][ekey] - tr[(m, round(p["q"], 6))]["e_corr_ccsd_t"] for p in pts]) * 1e6
            rec = {"n": len(q)}
            if len(q) >= 6:
                res = d - np.polyval(np.polyfit(q, d, 4), q)
                rec["sigma4_uEh"] = float(np.sqrt(np.sum(res ** 2) / (len(q) - 5)))
                qa = np.array(sorted(set(np.round(np.abs(q), 6))))
                ev = np.array([0.5 * (d[np.isclose(q, qq)][0] + d[np.isclose(q, -qq)][0]) for qq in qa])
                A = np.vstack([np.ones_like(qa), qa ** 2, qa ** 4]).T
                c, *_ = np.linalg.lstsq(A, ev, rcond=None)
                rec.update(a2_uEh=float(c[1]), a4_uEh=float(c[2]), curvature_bias_uEh=float(2 * c[1]),
                           delta_omega_cm=float(2 * c[1] * 1e-6 * HARTREE_CM),
                           even_q1_uEh=float(ev[np.isclose(qa, 1.0)][0] - ev[np.isclose(qa, 0.0)][0]) if np.any(np.isclose(qa, 1.0)) else None,
                           even_q05_uEh=float(ev[np.isclose(qa, 0.5)][0] - ev[np.isclose(qa, 0.0)][0]) if np.any(np.isclose(qa, 0.5)) else None)
                lines.append(f"| {m} | {fam[m]} | {freq[m]:.0f} | {arm} | {len(q)} | {rec['sigma4_uEh']:.3f} | {c[1]:+.2f} | {c[2]:+.2f} | "
                             f"{2*c[1]:+.2f} | {rec['delta_omega_cm']:+.2f} | {rec['even_q1_uEh']:+.2f} | {rec['even_q05_uEh']:+.2f} |")
            else:
                lines.append(f"| {m} | {fam[m]} | {freq[m]:.0f} | {arm} | {len(q)} | (fewer than 6 points) | | | | | | |")
            summary[f"mode{m}_{arm}"] = rec
    lines += ["", "Reading aid: an arm with small σ is smooth; an arm with small |2·a2| is unbiased. The pipeline needs both. "
              "Arm A holds the reference frozen spaces at every q; B transports the occupied LMOs and re-selects LNOs; C is fresh. "
              "No verdict (the τ it would be judged against does not exist yet). Printed by probes/m1_canonical_truth.py."]
    txt = "\n".join(lines)
    open(os.path.join(out, f"CANONICAL_COMPARISON{suffix}.md"), "w", encoding="utf-8").write(txt)
    json.dump(summary, open(os.path.join(out, f"canonical_comparison{suffix}.json"), "w"), indent=1)
    print("\n" + txt)


if __name__ == "__main__":
    main()
