# Probe M1 — frozen spaces — benzene_r0 cc-pvtz, LNO thresholds [1e-07, 1e-08], arms A, 2026-09-22 12:10, ubuntu-32gb-hel1-14 (WSL), 16 threads

- reference: 15 fragments (one per PM LMO); frozen-space hash `7e82d3bda4a89505…`; arm C at the reference 2264 s
- **stage 0 round trip** E_A(0) − E_C(0) = 0.0001 µE_h (the object reloads; target ≤ 1e-3 µE_h)
- raw energies sealed: `m1_sealed_energies.json`, sha256 `e8e365566885f2ea…` — not printed

| mode | family | ω (cm⁻¹) | q | s_min occ | off-diag occ | s_min vir | off-diag vir | PM fresh | PM transported | match | A−B (µE_h) | A−C (µE_h) | B−C (µE_h) | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 29 | CH-stretch | 3210 | -1.00 | 0.9950 | 4.0e-03 | 0.4613 | 7.0e-01 | 7.008 | 7.008 | 0.988 | — | — | — | 2145 |
| 29 | CH-stretch | 3210 | -0.50 | 0.9976 | 1.9e-03 | 0.6659 | 3.3e-01 | 7.004 | 7.004 | 0.987 | — | — | — | 2292 |
| 29 | CH-stretch | 3210 | +0.00 | 1.0000 | 5.3e-15 | 1.0000 | 3.7e-12 | 7.000 | 7.000 | 1.000 | — | — | — | 2267 |
| 29 | CH-stretch | 3210 | +0.50 | 0.9961 | 1.9e-03 | 0.7010 | 3.0e-01 | 6.996 | 6.996 | 0.964 | — | — | — | 2208 |
| 29 | CH-stretch | 3210 | +1.00 | 0.9921 | 3.7e-03 | 0.5196 | 5.5e-01 | 6.992 | 6.992 | 0.770 | — | — | — | 2258 |
| 5 | CH-oop | 718 | +0.00 | 1.0000 | 5.3e-15 | 1.0000 | 3.7e-12 | 7.000 | 7.000 | 1.000 | — | — | — | 0 |
| 5 | CH-oop | 718 | +0.50 | 0.9960 | 4.8e-03 | 0.5424 | 7.2e-01 | 7.000 | 7.000 | 1.000 | — | — | — | 2364 |
| 5 | CH-oop | 718 | +1.00 | 0.9919 | 9.6e-03 | 0.3759 | 1.7e+00 | 7.000 | 7.000 | 0.963 | — | — | — | 2363 |


No verdict is printed (the τ it would be judged against does not exist yet). Printed by probes/m1_frozen_spaces.py.