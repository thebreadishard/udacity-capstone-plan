# X1 / X2 on the benzene dry-run tensor (b3lyp -> bhhlyp, 6-31g*, M = 30) — 2026-09-12 10:29

## X2 — which elements of Δ₂ move a band position (exact harmonic positions from diag(ω²) + Δ₂)

- Diagonal alone shifts bands by -18.2 to +81.1 cm⁻¹; dropping **all** off-diagonal elements changes the largest band by 19.58 cm⁻¹.
- Drop-one: of 435 off-diagonal pairs, **6 move any band by more than 0.5 cm⁻¹** (16 by more than 0.1); largest single effect 19.58 cm⁻¹, median 0.0000.
- Largest pairs: (15,18) ω 1185.7/1356.5 → 19.582; (11,12) ω 1020.0/1020.4 → 1.689; (17,22) ω 1207.9/1655.9 → 0.983; (16,23) ω 1207.8/1656.0 → 0.94; (14,21) ω 1069.1/1531.5 → 0.809; (13,20) ω 1069.1/1531.5 → 0.799; (14,20) ω 1069.1/1531.5 → 0.462; (13,21) ω 1069.1/1531.5 → 0.456.
- Noise-level perturbation (one element by σ_E/2 per q²): σ_E = 0.5 µE_h: 0 diagonal and 0 off-diagonal elements move a band > 0.5 cm⁻¹ (max 0.03); σ_E = 1.0 µE_h: 0 diagonal and 0 off-diagonal elements move a band > 0.5 cm⁻¹ (max 0.05).

## X1 — exact-query schemes against plan 05's K = 448 energies

- Singular values (µE_h, top 10): [786.316, 786.266, 762.139, 730.254, 711.898, 711.825, 591.417, 590.466, 590.126, 569.813]; off-diagonal elements above 1 µE_h: 53 of 435.
- Dense symmetric lower bound in mode E: 930 energies (M(M+1)/2 unknowns, ± pairs); plan 05 measured 448.

| noise σ_E (µE_h) | θ | off-diag elements > θ | colouring bound (gradients for exact sparse recovery) | as energies (2M each) | rank r at θ | low-rank products r + p |
|---|---|---|---|---|---|---|
| 0.5 | 0.25 | 87 | 5 | 300 | 30 | 35 |
| 0.5 | 0.50 | 66 | 4 | 240 | 30 | 35 |
| 0.5 | 1.25 | 51 | 4 | 240 | 30 | 35 |
| 0.5 | 2.50 | 45 | 4 | 240 | 30 | 35 |
| 1.0 | 0.50 | 66 | 4 | 240 | 30 | 35 |
| 1.0 | 1.00 | 53 | 4 | 240 | 30 | 35 |
| 1.0 | 2.50 | 45 | 4 | 240 | 30 | 35 |
| 1.0 | 5.00 | 44 | 4 | 240 | 30 | 35 |

Reading rules: a 'gradient' here is one exact Hessian–vector product (a pair of analytic gradients at ±d); plan 05's engine has no local-CC analytic gradient, and a canonical one cost ≈ 50 energies at DZ, so the 'as energies' column is the honest comparison unless gradients become available. The colouring number is a greedy upper bound. Nothing here is a plan-05 decision; it is the first test of directions S4 and S5.

Printed by `experiments/x1_x2_benzene.py`; inputs sealed in plan 05's dry run (2026-09-05).