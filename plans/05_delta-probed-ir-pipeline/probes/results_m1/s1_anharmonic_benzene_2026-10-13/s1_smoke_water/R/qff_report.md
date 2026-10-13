# Quartic force field from 7 displaced Hessians — /root/s1_smoke_water/R/hess

Reference file `ref.json`; 3 vibrational modes; displacement 0.1 in reduced coordinates; assignment residual max 6.79e-16.
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
| 0 | 1710.9 | 1683.3 | -27.6 | 1683.3 | -27.6 | — |  |
| 1 | 3721.1 | 3551.2 | -169.9 | 3551.2 | -169.9 | — |  |
| 2 | 3844.9 | 3676.4 | -168.5 | 3676.4 | -168.5 | — |  |

## Provenance

- timestamp_utc: `2026-10-13 18:06:59`
- host: `ubuntu-32gb-hel1-6`
- python: `3.12.15`
- numpy: `2.5.4`
- command: `qff.py /root/s1_smoke_water/R/hess --disp 0.10 --out /root/s1_smoke_water/R/qff_report.md`
