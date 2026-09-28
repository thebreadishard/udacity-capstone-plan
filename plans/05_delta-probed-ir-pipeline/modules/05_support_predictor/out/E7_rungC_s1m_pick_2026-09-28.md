# Stage pick — out/E7_rungC_s1m_{label}_2026-09-28

| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |
|---|---|---|---|---|---|---|---|---|
| i | `(registered)` | 175 | 0.3750 | 0.3627, 0.3821, 0.3802 | 0.99 | 11.30 | 0.99 | 10.49 |
| ii **winner** | `--aux-weight 1.0` | 175 | 0.3380 | 0.3157, 0.3421, 0.3561 | 0.93 | 10.81 | 0.94 | 9.91 |
| iii | `--loss internal` | 175 | 0.3484 | 0.3288, 0.3646, 0.3518 | 0.93 | 10.63 | 0.93 | 9.86 |
| iv | `--loss internal --scale class` | 175 | 0.5722 | 0.7663, 0.4052, 0.5450 | 1.00 | 10.97 | 1.00 | 10.51 |

winner: ii → flags `--aux-weight 1.0` (chosen by the inner term alone, as registered)
