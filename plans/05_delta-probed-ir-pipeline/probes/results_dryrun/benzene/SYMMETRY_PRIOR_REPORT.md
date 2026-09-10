# Dry run — benzene — the symmetry prior (decision 22 / P14) and the forbidden-coupling null (decision 23 / P15)

Full point group D6h built from the geometry (largest atom-mapping deviation 0.0001 bohr). Modes grouped as degenerate within 1 cm⁻¹: 19 irreducible blocks for 30 modes. B1/B2 labels follow the convention C2' through atoms.

| mode | ω_DFT (cm⁻¹) | family | irrep |
|---|---|---|---|
| 0 | 415.0 | CH-oop | E2u |
| 1 | 415.1 | CH-oop | E2u |
| 2 | 622.0 | ring-ip | E2g |
| 3 | 622.2 | ring-ip | E2g |
| 4 | 694.7 | CH-oop | A2u |
| 5 | 717.5 | CH-oop | B2g |
| 6 | 864.7 | CH-oop | E1g |
| 7 | 864.7 | CH-oop | E1g |
| 8 | 969.2 | CH-oop | E2u |
| 9 | 969.2 | CH-oop | E2u |
| 10 | 1010.7 | CH-oop | B2g |
| 11 | 1020.0 | CH-ip-bend | A1g+B1u |
| 12 | 1020.4 | CH-ip-bend | A1g+B1u |
| 13 | 1069.1 | CH-ip-bend | E1u |
| 14 | 1069.1 | CH-ip-bend | E1u |
| 15 | 1185.7 | CH-ip-bend | B2u |
| 16 | 1207.8 | CH-ip-bend | E2g |
| 17 | 1207.9 | CH-ip-bend | E2g |
| 18 | 1356.5 | CC-stretch | B2u |
| 19 | 1387.4 | CC-stretch | A2g |
| 20 | 1531.5 | CC-stretch | E1u |
| 21 | 1531.5 | CC-stretch | E1u |
| 22 | 1655.9 | CC-stretch | E2g |
| 23 | 1656.0 | CC-stretch | E2g |
| 24 | 3174.1 | CH-stretch | B1u |
| 25 | 3183.6 | CH-stretch | E2g |
| 26 | 3183.7 | CH-stretch | E2g |
| 27 | 3199.4 | CH-stretch | E1u |
| 28 | 3199.4 | CH-stretch | E1u |
| 29 | 3210.0 | CH-stretch | A1g |

Irrep count (blocks): A1g × 1, A1g+B1u (mixed) × 1, A2g × 1, A2u × 1, B1u × 1, B2g × 2, B2u × 2, E1g × 1, E1u × 3, E2g × 4, E2u × 2; worst table match 0.000, worst within-class spread 0.000.

**Free elements under the prior:** 57 same-irrep off-diagonal pairs out of 435 (of which 11 are the two components of a degenerate pair); 12 of them have a two-mode pattern in the dry run's 200 cm⁻¹ deck. Unknowns fitted: 30 diagonal + 57 off-diagonal = 87, against 273 training patterns.

**The null (decision 23), DFT surrogate.** Direct Δ₂ (from the two Hessians): forbidden pairs max |Δ_ij| = 2.029 µE_h (RMS 0.278), allowed pairs max 423.9 µE_h (RMS 79.5); diagonal RMS 446.1 µE_h. From the two-mode ± responses (92 deck pairs): forbidden max 1.573 µE_h (RMS 0.276), allowed max 420.1 µE_h. Forbidden couplings are zero to the Hessians' numerical noise: the irrep assignment is consistent with the surrogate.

**Recovery under the symmetry prior (mode E, same deck, same hold-out, no ℓ₁ penalty):**

| family | n modes | RMS Δω error, symmetry prior (cm⁻¹, first-order / full rediag) | banded prior w = 25.0 (dry run) | diagonal only |
|---|---|---|---|---|
| CC-stretch | 6 | 0.28 / 0.30 | 0.29 / 0.36 | 0.42 / 6.90 |
| CH-ip-bend | 7 | 0.08 / 0.34 | 0.08 / 0.43 | 0.05 / 7.47 |
| CH-oop | 9 | 0.17 / 0.18 | 0.19 / 0.21 | 0.19 / 0.62 |
| CH-stretch | 6 | 0.04 / 0.04 | 0.08 / 0.11 | 0.05 / 0.04 |
| ring-ip | 2 | 0.07 / 0.07 | 0.14 / 0.31 | 0.09 / 0.37 |

ρ (hold-out, all training) = 0.0013; ρ_off = 0.0539; RMS_resp/RMS_off = 41.65; **K_off at ρ_off ≤ 0.3 = 210** energies (dry run, banded prior: 388).

Noise column (P1/P2 reading on the off-diagonal residual; K_off in energies):

| σ_E (µE_h) | ρ_noise,off | c = 1.0 | c = 1.5 | c = 2.0 | c = 3.0 |
|---|---|---|---|---|---|
| 0.5 | 0.068 | 352 | 296 | 274 | 266 |
| 1.0 | 0.137 | 278 | 266 | 210 | 210 |
| 2.0 | 0.274 | 266 | 210 | at-noise | at-noise |
| 5.0 | 0.685 | at-noise | at-noise | at-noise | at-noise |
| 10.0 | 1.370 | at-noise | at-noise | at-noise | at-noise |
| 20.0 | 2.739 | at-noise | at-noise | at-noise | at-noise |

ρ_dry,off (model floor) = 0.0539. The dry run's banded prior: see stageC_recovery.json. Printed by probes/dryrun_symmetry_prior.py from the cached stage-B responses; no new DFT energy. No verdict.