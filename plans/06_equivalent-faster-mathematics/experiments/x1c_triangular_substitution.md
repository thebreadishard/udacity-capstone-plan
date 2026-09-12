# X1c — the triangular-substitution count on the benzene Δ₂ pattern (2026-09-12 16:25)

Powell & Toint's lower triangular substitution method as characterised by Coleman & Moré (1982 TR / 1984): the count is a proper colouring of the column-intersection graph of the lower triangular part L_π of the permuted matrix (their Theorem 6.1); maxr = the maximum number of non-zeros in a row of L_π is a lower bound (their Theorem 6.2). π = smallest-last ordering of the pattern graph. The recovery is verified numerically on a random symmetric matrix with the pattern (substitution (6.1), decreasing position). Same tensor and θ grid as X1/X1b; K = 448.

| σ_E (µE_h) | θ (µE_h) | off-diag > θ | maxr (lower bound) | (d) triangular colours | colouring | max abs recovery error | energies at 2M per product |
|---|---|---|---|---|---|---|---|
| 0.5 | 0.25 | 87 | 6 | **7** | largest-first | 2.2e-16 | 420 |
| 0.5 | 0.50 | 66 | 6 | **6** | largest-first | 2.8e-16 | 360 |
| 0.5 | 1.25 | 51 | 6 | **6** | largest-first | 2.2e-16 | 360 |
| 0.5 | 2.50 | 45 | 6 | **6** | largest-first | 2.8e-17 | 360 |
| 1.0 | 0.50 | 66 | 6 | **6** | largest-first | 2.2e-16 | 360 |
| 1.0 | 1.00 | 53 | 6 | **6** | largest-first | 2.2e-16 | 360 |
| 1.0 | 2.50 | 45 | 6 | **6** | largest-first | 1.1e-16 | 360 |
| 1.0 | 5.00 | 44 | 6 | **6** | largest-first | 2.2e-16 | 360 |

Reading: (d) is an upper bound on the triangular chromatic number for this ordering (two sequential colourings tried), maxr a lower bound; the reconstruction error shows the substitution is exact up to rounding on noise-free data. Substitution can magnify measurement noise (Coleman & Moré §6, after Powell & Toint 1979) — for plan 05's noisy probes that magnification would have to be measured before the count is used.

Constants: {"sigma_E_uEh": [0.5, 1.0], "theta_multiples_of_noise": [1, 2, 5, 10], "K_measured_plan05": 448, "ordering_pi": "smallest-last ordering of the pattern graph H (Matula\u2013Beck; Coleman & Mor\u00e9 1982 \u00a76)", "colourings_tried_on_Gu_L": ["largest-first sequential", "smallest-last sequential"], "random_seed": 0}