# Route 2 — naphthalene VPT2 fundamentals (B97-1 / TZ2P, analytic Hessians, QFF step 0.10) against the rotationally resolved band origins (2026-09-25)

Source files: `probes/results_m1/route2/qff_naphthalene_d010.npz` (dpir.qff; 48 modes, 97 Hessians), `modules/03_lab_scoreboard/out/origin_columns_naphthalene.csv` (module 03, items 72–73), `modules/03_lab_scoreboard/out/naphthalene_dft_modes.md` (module 03 mode table for the family assignment).

Two-route disagreement of the semi-diagonal quartic constants (1128 pairs): median 0.03, 90th percentile 0.22, max 3.6 cm⁻¹ — the finite-difference noise that made benzene's route-1 quartics unusable on 21 September is absent on route 2.

VPT2 as `dpir.qff` computes it: second-order perturbation theory on the cubic and semi-diagonal quartic constants, resonances within 200 cm⁻¹ deperturbed, no polyad diagonalisation (the three fundamentals below are far from any resonance partner, so this choice does not move them). Assignment on the route-2 mode vectors: B1u out-of-plane modes (share > 0.9, z-pattern symmetric under both in-plane mirrors) are modes [0, 5, 13, 19]; the three lowest are nu48, nu47, nu46 (b3u in Pirali's axes). Module 03's B3LYP/6-31G* mode table is shown beside them as the check that the same modes are meant.

| band | route-2 mode | ω B97-1/TZ2P | ν VPT2 | module 03 DFT mode (ω B3LYP/6-31G*) | ω ratio | laboratory origins as printed (source, year) | Pirali 2009 position | most precise origin | ν − origin |
|---|---|---|---|---|---|---|---|---|---|
| nu48 | 0 | 170.3 | 166.3 | 0 (175.6) | 0.970 | 167.00 (Pirali 2013) | 166.40 | 167.00 | **-0.7** |
| nu47 | 5 | 482.3 | 475.9 | 5 (491.5) | 0.981 | 474.00 (Pirali 2013) | 473.33 | 474.00 | **+1.9** |
| nu46 | 13 | 797.6 | 782.6 | 13 (803.9) | 0.992 | 782.33 (Albert 2011); 782.00 (Pirali 2013) | 782.33 | 782.33 | **+0.2** |

RMS of ν − origin over the three bands: **1.2 cm⁻¹**; harmonic ω − origin for the same three: +3.3, +8.3, +15.3 cm⁻¹.

What this decides and what it does not: route 2 reproduces the three rotationally resolved CH-oop origins of naphthalene to a few wavenumbers with clean quartics; that is the prerequisite (Gate E, item 2) for the Mackie 2021 question, not its answer — the answer needs the same route on a PAH where their instabilities appeared (the four-ring molecule after the 28th), and the second step size (0.05) that was planned but not run on hel1-14.
