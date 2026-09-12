#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Decision 26 (P12), input (ii) and the P18 input: the cheap basis-set line — DF-RHF and full-space DF-MP2 (frozen core)
at the SAME 27 benzene geometries as probe M1 (the tight cc-pVTZ run's (mode, q) list), in larger bases (default
cc-pVQZ; cc-pV5Z SCF-only if asked). No coupled cluster. Reuses probe M1's geometry construction, SCF and MP2 helpers.

Printed (results_m1/BASIS_LINE_scf_mp2.md): per mode the frequency change Δω = ½·Δ(2·a2) of the SCF part and of the MP2
correlation part from cc-pVTZ to each larger basis, in cm⁻¹, with the DZ→TZ step from m1_basis_sensitivity.py beside it,
so the convergence of the two composite-anchor terms (SCF extrapolation, MP2-level correlation correction) is read per
mode. Absolute energies are stored in results_m1/basis_line_scf_mp2.json for the fit but NOT printed (sealed-value rule:
they are not CC values, but the same habit applies).

Runs in WSL (one anchor job at a time; this is light but not free — a DF-MP2/cc-pVQZ point on benzene is minutes):
  wsl ~/qc05/bin/python plans/05_delta-probed-ir-pipeline/probes/m1_basis_scf_mp2_line.py [--bases cc-pvqz] [--scf-only-bases cc-pv5z] [--threads 8]
Resumable: points already in the JSON are skipped.
"""
import argparse, json, os, time
from datetime import datetime
import numpy as np

import m1_frozen_spaces as M1
from m1_basis_sensitivity import curvature, HARTREE_CM, FAM

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results_m1")
JSON = os.path.join(OUT, "basis_line_scf_mp2.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bases", default="cc-pvqz", help="comma list: SCF + MP2 at each")
    ap.add_argument("--scf-only-bases", default="", help="comma list: SCF only (e.g. cc-pv5z)")
    ap.add_argument("--ref", default="benzene_cc-pvtz_tight", help="M1 run whose (mode, q) points define the 27 geometries")
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    from pyscf import lib
    lib.num_threads(args.threads)
    a = json.load(open(os.path.join(M1.DRYRUN, "stageA.json")))
    z = np.load(os.path.join(M1.DRYRUN, "stageA_hessians.npz"))
    L, omega, Minv, coords0 = z["L"], z["omega_au"], z["Minv"], z["coords"]
    symbols = a["symbols"]
    arms = json.load(open(os.path.join(OUT, args.ref, "m1_sealed_energies.json")))
    wanted = [(p["mode"], p["q"]) for p in arms["points"]]
    data = json.load(open(JSON)) if os.path.exists(JSON) else {"points": [], "machine": M1.machine() if hasattr(M1, "machine") else "", "started": f"{datetime.now():%Y-%m-%d %H:%M}"}
    done = {(p["basis"], p["mode"], round(p["q"], 6)) for p in data["points"]}
    jobs = [(b, True) for b in args.bases.split(",") if b] + [(b, False) for b in args.scf_only_bases.split(",") if b]
    M1.log(f"basis line: {len(wanted)} points × {len(jobs)} bases; {len(done)} already done")
    for basis, with_mp2 in jobs:
        for m, q in wanted:
            if (basis, m, round(q, 6)) in done:
                continue
            t0 = time.time()
            v = np.zeros(len(omega)); v[m] = q
            x = coords0 + ((L @ (v / np.sqrt(omega))) * Minv).reshape(-1, 3)
            mol = M1.make_mol(symbols, x, basis)
            mf = M1.run_scf(mol)
            rec = {"basis": basis, "mode": int(m), "q": float(q), "e_scf": float(mf.e_tot), "nbas": int(mol.nao), "t_scf_s": round(time.time() - t0, 1)}
            if with_mp2:
                t1 = time.time(); rec["e_corr_mp2"] = M1.full_mp2(mf); rec["t_mp2_s"] = round(time.time() - t1, 1)
            data["points"].append(rec)
            json.dump(data, open(JSON, "w"), indent=1)
            M1.log(f"{basis} mode {m} q={q:+.2f}: nbas {rec['nbas']}, SCF {rec['t_scf_s']} s" + (f", MP2 {rec['t_mp2_s']} s" if with_mp2 else ""))
    # ---- report: Δω TZ → basis per mode, SCF and MP2 parts, beside the DZ → TZ step already printed
    tz_truth = json.load(open(os.path.join(OUT, args.ref, "canonical_truth_sealed.json")))["points"]
    tz_arms = arms["points"]
    prev = json.load(open(os.path.join(OUT, "basis_sensitivity_dz_tz.json"))) if os.path.exists(os.path.join(OUT, "basis_sensitivity_dz_tz.json")) else {}
    modes = sorted({m for m, _ in wanted})
    lines = [f"# Probe M1 — the cheap basis line: DF-RHF and DF-MP2 at the 27 benzene points, cc-pVTZ → larger bases — {datetime.now():%Y-%m-%d %H:%M}", "",
             f"Reference points: `{args.ref}` (same geometries, same DF-RHF reference, frozen core {M1.FROZEN_CORE}). Δω = ½·Δ(2·a2) per mode in cm⁻¹; even-part fit a0 + a2 q² + a4 q⁴. Absolute energies not printed.", "",
             "| mode | family | part | DZ → TZ (from m1_basis_sensitivity) | " + " | ".join(f"TZ → {b.upper()}" for b, _ in jobs) + " |", "|---|---|---|---|" + "---|" * len(jobs)]
    summary = {}
    for m in modes:
        for part, key_tz, key_new, prev_key in (("SCF", lambda p: p["e_scf"], lambda p: p["e_scf"], "SCF (DF-RHF)"),
                                                ("MP2 correlation", lambda p: p["A"]["e_corr_mp2_full"], lambda p: p.get("e_corr_mp2"), "MP2 correlation (full space, from the arms' files)")):
            src_tz = tz_truth if part == "SCF" else tz_arms
            c_tz, _, _ = curvature([p for p in src_tz if p["mode"] == m], key_tz)
            cells = []
            for basis, with_mp2 in jobs:
                pts = [p for p in data["points"] if p["basis"] == basis and p["mode"] == m and (part == "SCF" or p.get("e_corr_mp2") is not None)]
                if len(pts) < 6 or (part == "MP2 correlation" and not with_mp2):
                    cells.append("—"); continue
                c_new, _, _ = curvature(pts, key_new)
                dw = 0.5 * (c_new - c_tz) * HARTREE_CM; cells.append(f"{dw:+.1f}")
                summary.setdefault(f"mode{m}", {})[f"{part} TZ->{basis}"] = dw
            dz = prev.get(f"mode{m}", {}).get(prev_key, {}).get("delta_omega_cm")
            lines.append(f"| {m} | {FAM.get(m, '?')} | {part} | {f'{dz:+.1f}' if dz is not None else '—'} | " + " | ".join(cells) + " |")
    lines += ["", "Reading: if the TZ → QZ step is small next to the DZ → TZ step, the SCF and MP2 parts of a composite anchor are near their limits at TZ and the "
              "remaining basis error sits in the CC correlation part beyond MP2; if not, the composite (P18) must carry the SCF/MP2 basis correction explicitly. "
              "No verdict; decision 26 input (ii). Printed by probes/m1_basis_scf_mp2_line.py."]
    txt = "\n".join(lines)
    open(os.path.join(OUT, "BASIS_LINE_scf_mp2.md"), "w", encoding="utf-8").write(txt)
    json.dump(summary, open(os.path.join(OUT, "basis_line_summary.json"), "w"), indent=1)
    print(txt)


if __name__ == "__main__":
    main()
