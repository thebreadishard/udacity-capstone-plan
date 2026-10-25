# CC-level test — A_01f3186607 (2026-10-04 02:41; pre-registration 2026-09-28 Standout_CC_Level_Test)

CC Hessian `probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 10, 'step': 0.005}); low level pyscf analytic B3LYP (grid 99/590); proxy exports `out\exports_analytic`; deck b7b789e3dfb0 (same as the proxy export); M = 48, 666 patterns, 124 held out; stride 17; Δ₂ off-diagonal Frobenius CC / proxy = 2.74; in-band share CC 0.30 vs proxy 0.28.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | None | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | None | — | 0.19 | 0.99 |
| CC | P1_seed1 | None | — | 0.19 | 1.05 |
| CC | P1_seed2 | None | — | 0.19 | 0.98 |
| CC | P3_oracle | None | — | 0.04 | 1.53 |
| CC | **P1 median** | — | None | 0.19 | 0.99 |
| proxy | P0 | None | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | None | — | 0.09 | 0.92 |
| proxy | P1_seed1 | None | — | 0.09 | 0.94 |
| proxy | P1_seed2 | None | — | 0.09 | 0.95 |
| proxy | P3_oracle | None | — | 0.09 | 1.04 |
| proxy | **P1 median** | — | None | 0.09 | 0.94 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): FAIL. **C2** (same direction as the proxy, within a factor 1.5): FAIL. **C3** oracle K_off(0.3) on CC None, P1 / oracle None (not near the ceiling). **Label for the plan line:** proxy (C1 failed on CC).
