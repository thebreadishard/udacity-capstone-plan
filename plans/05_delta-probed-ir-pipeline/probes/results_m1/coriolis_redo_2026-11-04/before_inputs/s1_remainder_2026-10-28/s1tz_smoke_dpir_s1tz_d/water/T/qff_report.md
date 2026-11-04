# Quartic force field from 7 displaced Hessians — /root/s1tz_smoke_dpir_s1tz_d/water/T/hess

Reference file `ref.json`; 3 vibrational modes; displacement 0.1 in reduced coordinates; assignment residual max 4.89e-16.
Harmonic ω (cm⁻¹): 1616.9, 3785.7, 3890.9

## Noise diagnostics

Off-diagonal semi-diagonal quartic constants φ_iijj have two independent finite-difference routes (displace j and read H_ii; displace i and read H_jj). Their difference is a direct estimate of the numerical error of that constant. Exactly degenerate pairs (a, b) must give equal φ_aa,jj and φ_bb,jj for every totally symmetric j; their difference is a second estimate.

- route disagreement |φ_iijj(a) − φ_iijj(b)|: median 1.8, 90th percentile 10.0, max 12.1 cm⁻¹ (max |φ_iijj| 730.2)
- cubic route spread (max − min of the three routes): median 0.08, max 0.7 cm⁻¹
- totally symmetric modes (|φ_iii| > 5 cm⁻¹, non-degenerate): [(0, 1616.9), (1, 3785.7)]

| degenerate pair (ω) | j (ω) | φ_aa,jj | φ_bb,jj | difference | route disagreement a / b |
|---|---|---|---|---|---|

## VPT2 fundamentals (deperturbation window 200.0 cm⁻¹, min K 0.0; 0 resonances deperturbed; polyad diagonalisation not applied)

| mode | ω | ν raw quartics | ν − ω | ν symmetry-averaged quartics | ν − ω | pyVPT2 ν | pair |
|---|---|---|---|---|---|---|---|
| 0 | 1616.9 | 1592.6 | -24.3 | 1592.6 | -24.3 | — |  |
| 1 | 3785.7 | 3617.4 | -168.3 | 3617.4 | -168.3 | — |  |
| 2 | 3890.9 | 3733.9 | -157.0 | 3733.9 | -157.0 | — |  |

## Provenance

- timestamp_utc: `2026-10-19 07:23:21`
- host: `ubuntu-32gb-hel1-6`
- python: `3.12.15`
- numpy: `2.5.4`
- command: `qff.py /root/s1tz_smoke_dpir_s1tz_d/water/T/hess --disp 0.10 --allow-noisy --out /root/s1tz_smoke_dpir_s1tz_d/water/T/qff_report.md`
