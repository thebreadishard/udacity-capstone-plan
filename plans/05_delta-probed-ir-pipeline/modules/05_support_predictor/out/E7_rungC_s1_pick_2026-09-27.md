# Stage pick — out/E7_rungC_s1_{label}_2026-09-27

| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |
|---|---|---|---|---|---|---|---|---|
| i | `(registered)` | 175 | 0.3873 | 0.3404, 0.4770, 0.3446 | 0.96 | 11.16 | 0.96 | 10.44 |
| ii **winner** | `--aux-weight 1.0` | 175 | 0.3025 | 0.2925, 0.3175, 0.2975 | 0.88 | 10.01 | 0.89 | 9.21 |
| iii | `--loss internal` | 175 | 0.3285 | 0.2925, 0.3223, 0.3706 | 0.89 | 10.44 | 0.90 | 9.60 |
| iv | `--loss internal --scale class` | 175 | 0.5113 | 0.4092, 0.4253, 0.6994 | 0.99 | 10.79 | 0.98 | 10.52 |

winner: ii → flags `--aux-weight 1.0` (chosen by the inner term alone, as registered)
