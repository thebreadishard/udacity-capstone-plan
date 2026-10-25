# CC-level test — A_01f3186607 (2026-10-04 02:54; pre-registration 2026-09-28 Standout_CC_Level_Test) — EXPLORATORY, not a registered line: pool all, solver band 0 cm⁻¹

CC Hessian `probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/hessian_ccsd_t.npz` ({'basis': 'cc-pvdz', 'frozen': 10, 'step': 0.005}); low level pyscf analytic B3LYP (grid 99/590); proxy exports `out\exports_analytic`; deck b7b789e3dfb0 (same as the proxy export); M = 48, 2496 patterns, 124 held out; stride 78; Δ₂ off-diagonal Frobenius CC / proxy = 2.74; in-band share CC 0.30 vs proxy 0.28.

| response | ordering | K_off(0.3) | ratio vs P0 | n_half ratio | AUC ratio |
|---|---|---|---|---|---|
| CC | P0 | 1716 | 1.00 | 1.00 | 1.00 |
| CC | P1_seed0 | 780 | 0.45 | 0.67 | 0.69 |
| CC | P1_seed1 | 780 | 0.45 | 0.83 | 0.70 |
| CC | P1_seed2 | 780 | 0.45 | 0.67 | 0.72 |
| CC | P3_oracle | 156 | 0.09 | 0.17 | 0.18 |
| CC | **P1 median** | — | 0.45 | 0.67 | 0.70 |
| proxy | P0 | 1872 | 1.00 | 1.00 | 1.00 |
| proxy | P1_seed0 | 1092 | 0.58 | 0.11 | 0.74 |
| proxy | P1_seed1 | 1092 | 0.58 | 0.11 | 0.76 |
| proxy | P1_seed2 | 1248 | 0.67 | 0.11 | 0.79 |
| proxy | P3_oracle | 312 | 0.17 | 0.11 | 0.27 |
| proxy | **P1 median** | — | 0.58 | 0.11 | 0.76 |

**C1** (P1 vs P0 on CC: K_off ratio ≤ 0.80 and n_half ratio ≤ 0.80): pass. **C2** (same direction as the proxy, within a factor 1.5): pass. **C3** oracle K_off(0.3) on CC 156, P1 / oracle 5.00 (not near the ceiling). **Label for the plan line:** confirmed on this molecule (CC).
