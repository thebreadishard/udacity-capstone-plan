# Quartic force field from 7 displaced Hessians — C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\s1_anharmonic_benzene_2026-10-13\s1_smoke_water\R\hess

Reference file `ref.json`; 3 vibrational modes; displacement 0.1 in reduced coordinates; assignment residual max 7.19e-16.
Harmonic ω (cm⁻¹): 1710.9, 3721.1, 3844.9

## Noise diagnostics

Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; displace i and read H_jj). Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate pairs (a, b) must give equal φ_aa,jj and φ_bb,jj for every totally symmetric j; their difference is a second estimate.

- route disagreement |φ_iijj(a) − φ_iijj(b)|: median 0.2, 90th percentile 0.2, max 0.2 cm⁻¹ (max |φ_iijj| 803.8)
- cubic route spread (max − min of the three routes): median 0.00, max 0.4 cm⁻¹
- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): [(0, 1710.9), (1, 3721.1)]

| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |
|---|---|---|---|---|---|

## VPT2 fundamentals (deperturbation window 200.0 cm⁻¹, min K 0.0; 0 resonances deperturbed; polyad diagonalisation not applied)

| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |
|---|---|---|---|---|---|---|---|
| 0 | 1710.9 | 1660.3 | -50.6 | 1660.3 | -50.6 | — |  |
| 1 | 3721.1 | 3551.1 | -169.9 | 3551.1 | -169.9 | — |  |
| 2 | 3844.9 | 3653.4 | -191.5 | 3653.4 | -191.5 | — |  |

## Provenance

- timestamp_utc: `2026-11-04 07:38:09`
- host: `Asus18`
- python: `3.14.6`
- numpy: `2.5.1`
- command: `qff.py C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\s1_anharmonic_benzene_2026-10-13\s1_smoke_water\R\hess --disp 0.10 --out C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\s1_anharmonic_benzene_2026-10-13\s1_smoke_water\R\qff_report.md`
- commit: `648a001eb6cfa32df774b73c6e2f0d91dadb87c4`
- dirty: `yes`
