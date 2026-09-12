# X10 — which off-diagonal pairs must be measured, and can DFT alone say which (benzene, 2026-09-12 19:45)

Same-irrep pairs: 57 of 435, of which 10 join the two components of one degenerate level (no independent element; plan 05's prior file counts 11 such pairs and 12 allowed pairs in the deck) — ranked here: the remaining **47**; forbidden: 378. Keeping the diagonal and all 47 ranked pairs, zeroing everything else: max band shift 0.002 cm⁻¹ (the symmetry prior is exact to that level). Dropping every off-diagonal element: 19.58 cm⁻¹.

Rank correlation (Spearman) of the DFT-only denominator with the measured drop-one effect over the allowed pairs: **0.754**; of the oracle magnitude: 0.825.

| predictor | pairs needed for ≤ 0.5 cm⁻¹ | energies (2M + 2n) | pairs needed for ≤ 0.1 cm⁻¹ | energies |
|---|---|---|---|---|
| P1 DFT-only 1/|w_i^2-w_j^2| | **19** | 98 | 19 | 98 |
| P2 oracle |Delta_ij| | **17** | 94 | 19 | 98 |
| P3 oracle drop-one effect | **6** | 72 | 16 | 92 |

Against plan 05's measured deck K = 448 (2M = 60 diagonal energies plus K_off under the stopping rule). The energies column is the naive symmetric-pattern count and ignores that the dry run's deck also buys its noise column and stopping test; it is a lower bound on any real deck.

Top 10 by P1 DFT-only 1/|w_i^2-w_j^2| — (i, j), predictor value, measured effect (cm⁻¹), ω_i, ω_j (cm⁻¹):

- (11, 12) · 5.854e+07 · effect 1.689 · 1020.0 / 1020.4
- (15, 18) · 1.109e+05 · effect 19.582 · 1185.7 / 1356.5
- (5, 10) · 9.506e+04 · effect 0.061 · 717.5 / 1010.7
- (1, 8) · 6.280e+04 · effect 0.015 · 415.1 / 969.2
- (1, 9) · 6.280e+04 · effect 0.166 · 415.1 / 969.2
- (0, 8) · 6.280e+04 · effect 0.139 · 415.0 / 969.2
- (0, 9) · 6.280e+04 · effect 0.013 · 415.0 / 969.2
- (3, 16) · 4.495e+04 · effect 0.206 · 622.2 / 1207.8
- (3, 17) · 4.494e+04 · effect 0.169 · 622.2 / 1207.9
- (2, 16) · 4.493e+04 · effect 0.127 · 622.0 / 1207.8

Top 10 by P2 oracle |Delta_ij| — (i, j), predictor value, measured effect (cm⁻¹), ω_i, ω_j (cm⁻¹):

- (15, 18) · 2.450e-06 · effect 19.582 · 1185.7 / 1356.5
- (17, 22) · 1.165e-06 · effect 0.983 · 1207.9 / 1655.9
- (16, 23) · 1.164e-06 · effect 0.940 · 1207.8 / 1656.0
- (13, 20) · 8.958e-07 · effect 0.799 · 1069.1 / 1531.5
- (14, 21) · 8.956e-07 · effect 0.809 · 1069.1 / 1531.5
- (13, 21) · 4.884e-07 · effect 0.456 · 1069.1 / 1531.5
- (14, 20) · 4.879e-07 · effect 0.462 · 1069.1 / 1531.5
- (23, 26) · 4.772e-07 · effect 0.022 · 1656.0 / 3183.7
- (22, 25) · 4.771e-07 · effect 0.022 · 1655.9 / 3183.6
- (11, 24) · 3.771e-07 · effect 0.019 · 1020.0 / 3174.1

Top 10 by P3 oracle drop-one effect — (i, j), predictor value, measured effect (cm⁻¹), ω_i, ω_j (cm⁻¹):

- (15, 18) · 1.958e+01 · effect 19.582 · 1185.7 / 1356.5
- (11, 12) · 1.689e+00 · effect 1.689 · 1020.0 / 1020.4
- (17, 22) · 9.834e-01 · effect 0.983 · 1207.9 / 1655.9
- (16, 23) · 9.396e-01 · effect 0.940 · 1207.8 / 1656.0
- (14, 21) · 8.093e-01 · effect 0.809 · 1069.1 / 1531.5
- (13, 20) · 7.989e-01 · effect 0.799 · 1069.1 / 1531.5
- (14, 20) · 4.616e-01 · effect 0.462 · 1069.1 / 1531.5
- (13, 21) · 4.564e-01 · effect 0.456 · 1069.1 / 1531.5
- (3, 16) · 2.064e-01 · effect 0.206 · 622.2 / 1207.8
- (17, 23) · 2.005e-01 · effect 0.201 · 1207.9 / 1656.0

Reading: P3 is the best any ordering can do; P2 is what a perfect element-size prior (Module 05's target) would do; P1 is what DFT knows for free. Losing condition for the DFT-only rule (pre-stated): n(P1) at 0.5 cm⁻¹ above half the allowed pairs. One molecule, one stand-in functional pair; a rule, if any, is proposed for naphthalene, not adopted.

Constants: {"tolerances_cm": [0.5, 0.1], "K_measured_plan05": 448, "energies_per_diag_mode": 2, "energies_per_off_pair": 2}