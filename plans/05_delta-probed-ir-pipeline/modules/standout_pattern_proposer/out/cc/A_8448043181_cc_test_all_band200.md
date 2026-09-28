# CC-level test — A_8448043181 (2026-09-28 20:37; pre-registration 2026-09-28 Standout_CC_Level_Test) — EXPLORATORY, not a registered line: pool all, solver band 200 cm⁻¹

CC Hessian `probes/results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 6, 'step': 0.005}); deck 0932211bc5a8 (same as the proxy export); M = 30, 1020 patterns, 61 held out; stride 31; Δ₂ off-diagonal Frobenius CC / proxy = 0.33; in-band share CC 0.04 vs proxy 0.52.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | 1116 | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | 1426 | 1.28 | 0.22 | 1.45 |
| CC | P1_seed1 | 1240 | 1.11 | 0.44 | 1.01 |
| CC | P1_seed2 | 1302 | 1.17 | 2.33 | 1.14 |
| CC | P3_oracle | 434 | 0.39 | 0.22 | 0.33 |
| CC | **P1 median** | — | 1.17 | 0.44 | 1.14 |
| proxy | P0 | 496 | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | 682 | 1.38 | 3.67 | 1.60 |
| proxy | P1_seed1 | 868 | 1.75 | 3.67 | 1.77 |
| proxy | P1_seed2 | 930 | 1.88 | 5.00 | 2.06 |
| proxy | P3_oracle | 124 | 0.25 | 0.33 | 0.41 |
| proxy | **P1 median** | — | 1.75 | 3.67 | 1.77 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): FAIL. **C2** (same direction as the proxy, within a factor 1.5): pass. **C3** oracle K_off(0.3) on CC 434, P1 / oracle 3.00 (not near the ceiling). **Label for the plan line:** proxy (C1 failed on CC).
