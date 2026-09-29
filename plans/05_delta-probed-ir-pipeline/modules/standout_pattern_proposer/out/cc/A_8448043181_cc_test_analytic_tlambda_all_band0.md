# CC-level test — A_8448043181 (2026-09-29 23:12; pre-registration 2026-09-28 Standout_CC_Level_Test) — EXPLORATORY, not a registered line: pool all, solver band 0 cm⁻¹

CC Hessian `probes/results_m1/e8_benzene_ccpvdz_tlambda/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 6, 'step': 0.005}); low level pyscf analytic B3LYP (grid 99/590); proxy exports `out\exports_analytic`; deck 0932211bc5a8 (same as the proxy export); M = 30, 1020 patterns, 61 held out; stride 31; Δ₂ off-diagonal Frobenius CC / proxy = 2.68; in-band share CC 0.10 vs proxy 0.30.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | 806 | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | 496 | 0.62 | 0.29 | 0.52 |
| CC | P1_seed1 | 248 | 0.31 | 0.57 | 0.47 |
| CC | P1_seed2 | 434 | 0.54 | 0.57 | 0.51 |
| CC | P3_oracle | 124 | 0.15 | 0.14 | 0.17 |
| CC | **P1 median** | — | 0.54 | 0.57 | 0.51 |
| proxy | P0 | 620 | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | 496 | 0.80 | 0.67 | 0.76 |
| proxy | P1_seed1 | 248 | 0.40 | 0.44 | 0.69 |
| proxy | P1_seed2 | 434 | 0.70 | 0.56 | 0.74 |
| proxy | P3_oracle | 124 | 0.20 | 0.22 | 0.36 |
| proxy | **P1 median** | — | 0.70 | 0.56 | 0.74 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): pass. **C2** (same direction as the proxy, within a factor 1.5): pass. **C3** oracle K_off(0.3) on CC 124, P1 / oracle 3.50 (not near the ceiling). **Label for the plan line:** confirmed on this molecule (CC).
