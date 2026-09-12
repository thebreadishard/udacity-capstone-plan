# X1b — the three colouring counts on the benzene Δ₂ tensor (2026-09-12 16:02)

Same tensor and θ grid as X1. (a) = X1's printed number (a proper colouring of the pattern graph H); (b) = the CPR-valid count (proper colouring of the column-intersection graph); (c) = the symmetric-direct count (one-sided readability, T1b note). 'valid' columns are exact checks of the readability definitions on the whole pattern; only verified colourings count. K = 448 is plan 05's measured mode-E deck.

| σ_E (µE_h) | θ (µE_h) | off-diag > θ | Δ(H) | Δ(H_cpr) | (a) X1 colours | (a) symm-valid? | (a) unreadable entries / total | (b) CPR colours | (b) verified | (c) symmetric colours | (c) verified | energies (a / b / c) at 2M per product |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0.5 | 0.25 | 87 | 15 | 26 | 5 | **no** | 122 / 204 | **18** | yes | **14** | yes | 300 / 1080 / 840 |
| 0.5 | 0.50 | 66 | 12 | 23 | 4 | **no** | 100 / 162 | **15** | yes | **12** | yes | 240 / 900 / 720 |
| 0.5 | 1.25 | 51 | 10 | 18 | 4 | **no** | 70 / 132 | **11** | yes | **9** | yes | 240 / 660 / 540 |
| 0.5 | 2.50 | 45 | 6 | 7 | 4 | **no** | 72 / 120 | **8** | yes | **7** | yes | 240 / 480 / 420 |
| 1.0 | 0.50 | 66 | 12 | 23 | 4 | **no** | 100 / 162 | **15** | yes | **12** | yes | 240 / 900 / 720 |
| 1.0 | 1.00 | 53 | 11 | 19 | 4 | **no** | 72 / 136 | **12** | yes | **10** | yes | 240 / 720 / 600 |
| 1.0 | 2.50 | 45 | 6 | 7 | 4 | **no** | 72 / 120 | **8** | yes | **7** | yes | 240 / 480 / 420 |
| 1.0 | 5.00 | 44 | 6 | 7 | 4 | **no** | 72 / 118 | **8** | yes | **7** | yes | 240 / 480 / 420 |

Reading: (a) is a lower bound for both schemes (a proper colouring of H is necessary for either); the honest CPR count is (b); the symmetric direct scheme (c) sits between them when the greedy finds a verified colouring. The greedy of (c) is a heuristic — a smaller symmetric colouring may exist; the T1b note discusses the exact characterisation, which is to be read from Coleman & Moré (1984) and Powell & Toint (1979), not recalled.

Constants: {"sigma_E_uEh": [0.5, 1.0], "element_uncertainty_rule": "delta(D2_direct_ij) = sigma_E / 2 (as X1)", "theta_multiples_of_noise": [1, 2, 5, 10], "K_measured_plan05": 448, "greedy_order": "largest degree first (as X1)"}