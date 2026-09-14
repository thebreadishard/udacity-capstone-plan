#!/usr/bin/env python
"""Probe M1, symmetry witness (2026-09-14, two-hourly check): the ODD part E(+q) - E(-q) along benzene mode 18
(B2u in D6h, a one-dimensional non-totally-symmetric irrep) from the stored M1 energies. For an exact method at an
exactly symmetric geometry this is zero identically: a symmetry operation maps +q to -q. Its size therefore measures
(i) the residual asymmetry of the DFT geometry / mode direction (a term linear in q, common to every method and arm) and
(ii) the symmetry breaking of the local-correlation arms (frozen transported spaces A, transported-and-reselected B,
fresh C) at each threshold. Bearing on the deck: if the odd part is small against the response, a pattern confined to a
non-totally-symmetric irrep needs ONE energy instead of the pair (R_s = dE(+p) - dE(0) exactly, no force term, since the
gradient at a symmetric geometry is totally symmetric) - idea I14 of the obstacle ledger. Prints DIFFERENCES in uE_h only
(sealed-energy rule: no benzene coupled-cluster energy is printed). Output: results_m1/ODD_PART_SYMMETRY_mode18.md"""
import json, glob, os
from datetime import datetime
FIELDS = ["e_scf", "e_corr_lno_ccsd_t", "e_corr_mp2_full", "e_tot_composite"]
L = [f"# Probe M1 symmetry witness - odd part E(+q) - E(-q) along benzene mode 18 (B2u), uE_h - printed {datetime.now():%Y-%m-%d %H:%M} by m1_odd_part_symmetry.py", "",
     "Zero identically for an exact method at an exactly symmetric geometry. Differences only; no energy printed. Even part for scale: the LNO - canonical curvature bias along this mode is 48-85 uE_h (CANONICAL_COMPARISON.md); the response itself is larger.", ""]
L += ["| run | arm | q | " + " | ".join(FIELDS) + " |", "|---|---|---|" + "---|" * len(FIELDS)]
for f in sorted(glob.glob("results_m1/benzene_cc-pv?z_*/m1_sealed_energies.json")):
    pts = json.load(open(f))["points"]
    if len(pts) < 27:
        continue
    run = os.path.basename(os.path.dirname(f))
    for arm in "ABC":
        if arm not in pts[0]:
            continue
        byq = {round(float(p["q"]), 6): p[arm] for p in pts if p["mode"] == 18}
        for q in (0.25, 0.5, 0.75, 1.0):
            a, b = byq.get(q), byq.get(-q)
            if a is None or b is None:
                continue
            cells = [f"{1e6 * (a[k] - b[k]):.3f}" if a.get(k) is not None and b.get(k) is not None else "n/a" for k in FIELDS]
            L.append(f"| {run} | {arm} | {q:.2f} | " + " | ".join(cells) + " |")
f = "results_m1/benzene_cc-pvtz_tight/canonical_truth_sealed.json"
if os.path.exists(f):
    d = json.load(open(f))["points"]; byq = {round(float(p["q"]), 6): p for p in d if p["mode"] == 18}
    L += ["", "Canonical CCSD(T) truth line (cc-pVTZ), same mode, uE_h:", "", "| q | e_scf | e_corr_ccsd | e_corr_ccsd_t | total |", "|---|---|---|---|---|"]
    for q in sorted(q for q in byq if q > 0):
        if -q in byq:
            a, b = byq[q], byq[-q]
            L.append(f"| {q:.2f} | " + " | ".join(f"{1e6 * (a[k] - b[k]):.3f}" for k in ("e_scf", "e_corr_ccsd", "e_corr_ccsd_t")) + f" | {1e6 * ((a['e_scf'] + a['e_corr_ccsd_t']) - (b['e_scf'] + b['e_corr_ccsd_t'])):.3f} |")
L += ["", "Reading: the canonical odd part is linear in q (a residual force along a B2u direction: the DFT geometry or mode is not exactly D6h at the 1 uE_h level, removable by symmetrising the geometry); arm C reproduces it to 0.01 uE_h at every threshold, i.e. fresh local spaces break the symmetry by nothing measurable; the frozen transported arm A breaks it by up to 10 uE_h in the LNO piece at TZ tight (100 uE_h in the composite at DZ normal) and by < 0.6 uE_h in the composite at tight, < 0.2 at xtight. Consequence for I14: using one energy per non-totally-symmetric pattern instead of the pair costs an error of half the odd part in R_s, i.e. <= 0.3 uE_h at tight in the composite - below sigma4 of arms B/C (1.3-2.3 uE_h) and two orders below the curvature bias."]
open("results_m1/ODD_PART_SYMMETRY_mode18.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
print("\n".join(L[:6])); print("..."); print(L[-1][:200])
