# Hot-band desk test, benzene ν₁₁ — 2026-09-28 18:34 (pre-registration 2026-09-28 §2)

Record `qff_benzene_pyscf_analytic_d010_2026-09-21.npz`; DFT ν₁₁ 685.034 against 673.97465 cm⁻¹ measured. DFT-anharmonic offsets (B3LYP/6-31G*, two-route QFF) on the DFT fundamental; the corrected harmonic part is not yet applied to benzene.

| band | measured offset | predicted (χ_sym) | predicted (χ_raw) | component spread | sign | size | noise |
|---|---|---|---|---|---|---|---|
| nu11+nu6-nu6 | -0.466 | +0.128 | +0.128 | 0.000 | WRONG | miss | ok |
| nu11+nu16-nu16 | -1.099 | +0.115 | +0.115 | 0.000 | WRONG | miss | ok |
| 2nu11-nu11 | +0.127 | -0.598 | -0.598 | 0.000 | WRONG | miss | ok |

**Verdict:** P1 sign fail (0/3); P2 size fail (0/3); P3 noise pass (3/3).

## Reported output: sequence bands of ν₁₁ (lower levels ω_b ≤ 1,000 cm⁻¹), 300 K

| lower level | ω_b | g | offset χ | position | Boltzmann weight |
|---|---|---|---|---|---|
| nu16 | 414.5 | 2 | +0.115 | 685.149 | 0.2740 |
| nu6 | 621.6 | 2 | +0.128 | 685.162 | 0.1015 |
| nu4 | 718.0 | 1 | -0.570 | 684.464 | 0.0319 |
| nu11 (overtone sequence) | 695.1 | 1 | -0.598 | 684.437 | 0.0357 |
