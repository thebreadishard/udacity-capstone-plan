# Probe M1 — frozen spaces — benzene_quick cc-pvdz, LNO thresholds [1e-05, 1e-06], arms A, 2026-09-15 13:54, Asus18 (WSL), 8 threads

- reference: 15 fragments (one per PM LMO); frozen-space hash `e678b5a3f2a15a11…`; arm C at the reference 83 s
- **stage 0 round trip** E_A(0) − E_C(0) = 0.0000 µE_h (the object reloads; target ≤ 1e-3 µE_h)
- raw energies sealed: `m1_sealed_energies.json`, sha256 `9e9e68a27b6dd264…` — not printed

| mode | family | ω (cm⁻¹) | q | s_min occ | off-diag occ | s_min vir | off-diag vir | PM fresh | PM transported | match | A−B (µE_h) | A−C (µE_h) | B−C (µE_h) | s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 18 | CC-stretch | 1357 | -1.00 | 0.9922 | 3.6e-03 | 0.8915 | 1.3e-01 | 7.084 | 6.926 | 0.771 | — | — | — | 89 |
| 18 | CC-stretch | 1357 | +0.00 | 1.0000 | 6.3e-15 | 1.0000 | 1.1e-12 | 7.000 | 7.000 | 1.000 | — | — | — | 83 |
| 18 | CC-stretch | 1357 | +1.00 | 0.9922 | 3.6e-03 | 0.8934 | 1.3e-01 | 7.084 | 7.070 | 0.988 | — | — | — | 87 |
| 20 | CC-stretch | 1531 | -1.00 | 0.9898 | 1.1e-02 | 0.8390 | 1.0e-01 | 6.999 | 6.999 | 0.769 | — | — | — | 83 |
| 20 | CC-stretch | 1531 | +0.00 | 1.0000 | 6.3e-15 | 1.0000 | 1.1e-12 | 7.000 | 7.000 | 1.000 | — | — | — | 0 |
| 20 | CC-stretch | 1531 | +1.00 | 0.9898 | 1.1e-02 | 0.8374 | 1.0e-01 | 6.999 | 6.999 | 0.836 | — | — | — | 83 |


No verdict is printed (the τ it would be judged against does not exist yet). Printed by probes/m1_frozen_spaces.py.