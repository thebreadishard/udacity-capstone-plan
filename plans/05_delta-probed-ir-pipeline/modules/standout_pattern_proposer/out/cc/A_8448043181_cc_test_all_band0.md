# CC-level test — A_8448043181 (2026-09-28 21:53; pre-registration 2026-09-28 Standout_CC_Level_Test) — EXPLORATORY, not a registered line: pool all, solver band 0 cm⁻¹

CC Hessian `probes/results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 6, 'step': 0.005}); deck 0932211bc5a8 (same as the proxy export); M = 30, 1020 patterns, 61 held out; stride 31; Δ₂ off-diagonal Frobenius CC / proxy = 0.33; in-band share CC 0.04 vs proxy 0.52.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | 558 | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | 806 | 1.44 | 0.29 | 0.82 |
| CC | P1_seed1 | 744 | 1.33 | 0.57 | 0.79 |
| CC | P1_seed2 | 806 | 1.44 | 0.43 | 0.73 |
| CC | P3_oracle | 372 | 0.67 | 0.29 | 0.41 |
| CC | **P1 median** | — | 1.44 | 0.43 | 0.79 |
| proxy | P0 | 310 | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | 496 | 1.60 | 2.67 | 1.32 |
| proxy | P1_seed1 | 682 | 2.20 | 3.67 | 1.67 |
| proxy | P1_seed2 | 930 | 3.00 | 5.00 | 2.01 |
| proxy | P3_oracle | 124 | 0.40 | 0.33 | 0.41 |
| proxy | **P1 median** | — | 2.20 | 3.67 | 1.67 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): FAIL. **C2** (same direction as the proxy, within a factor 1.5): FAIL. **C3** oracle K_off(0.3) on CC 372, P1 / oracle 2.17 (not near the ceiling). **Label for the plan line:** proxy (C1 failed on CC).
