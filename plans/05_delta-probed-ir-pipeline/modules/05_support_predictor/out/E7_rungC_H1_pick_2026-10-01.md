# Stage pick — out/E7_rungC_H1_{label}_2026-10-01

| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |
|---|---|---|---|---|---|---|---|---|
| lr3e-4_w128 | `--lr 3e-4 --hybrid-hidden 128` | 175 | 0.1102 | 0.0555, 0.1992, 0.0758 | 0.46 | 5.06 | 0.51 | 6.08 |
| lr3e-4_w256 **winner** | `--lr 3e-4 --hybrid-hidden 256` | 175 | 0.0991 | 0.0530, 0.1658, 0.0783 | 0.43 | 4.44 | 0.49 | 5.13 |
| lr1e-3_w128 | `--lr 1e-3 --hybrid-hidden 128` | 175 | 0.1023 | 0.0607, 0.1642, 0.0819 | 0.45 | 5.18 | 0.50 | 5.62 |
| lr1e-3_w256 | `--lr 1e-3 --hybrid-hidden 256` | 175 | 0.1021 | 0.0565, 0.1642, 0.0855 | 0.46 | 5.27 | 0.50 | 5.91 |
| lr3e-3_w256 | `--lr 3e-3 --hybrid-hidden 256` | 175 | 0.1252 | 0.0632, 0.2128, 0.0997 | 0.44 | 6.52 | 0.48 | 6.04 |

winner: lr3e-4_w256 → flags `--lr 3e-4 --hybrid-hidden 256` (chosen by the inner term alone, as registered)
