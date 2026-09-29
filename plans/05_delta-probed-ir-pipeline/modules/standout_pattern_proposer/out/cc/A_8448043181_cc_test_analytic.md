# CC-level test — A_8448043181 (2026-09-29 05:18; pre-registration 2026-09-28 Standout_CC_Level_Test)

CC Hessian `probes/results_m1/e8_benzene_ccpvdz/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 6, 'step': 0.005}); low level pyscf analytic B3LYP (grid 99/590); proxy exports `out\exports_analytic`; deck 0932211bc5a8 (same as the proxy export); M = 30, 334 patterns, 61 held out; stride 9; Δ₂ off-diagonal Frobenius CC / proxy = 2.36; in-band share CC 0.04 vs proxy 0.30.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | None | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | None | — | 1.17 | 2.28 |
| CC | P1_seed1 | None | — | 1.17 | 2.29 |
| CC | P1_seed2 | None | — | 1.17 | 2.21 |
| CC | P3_oracle | None | — | 1.13 | 2.18 |
| CC | **P1 median** | — | None | 1.17 | 2.28 |
| proxy | P0 | None | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | None | — | 1.17 | 1.78 |
| proxy | P1_seed1 | None | — | 1.13 | 1.87 |
| proxy | P1_seed2 | None | — | 1.13 | 2.02 |
| proxy | P3_oracle | None | — | 1.17 | 2.34 |
| proxy | **P1 median** | — | None | 1.13 | 1.87 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): FAIL. **C2** (same direction as the proxy, within a factor 1.5): FAIL. **C3** oracle K_off(0.3) on CC None, P1 / oracle None (not near the ceiling). **Label for the plan line:** proxy (C1 failed on CC).
