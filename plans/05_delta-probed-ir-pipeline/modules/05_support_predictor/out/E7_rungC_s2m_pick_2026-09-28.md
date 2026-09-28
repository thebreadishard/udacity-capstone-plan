# Stage pick — out/E7_rungC_s2m_{label}_2026-09-28

| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |
|---|---|---|---|---|---|---|---|---|
| lr3e-4_e60 | `--aux-weight 1.0 --lr 3e-4 --epochs 60` | 175 | 0.3794 | 0.3495, 0.3835, 0.4052 | 0.98 | 10.99 | 0.98 | 10.24 |
| lr3e-4_e200 | `--aux-weight 1.0 --lr 3e-4 --epochs 200 --patience 20` | 175 | 0.3077 | 0.2718, 0.2946, 0.3567 | 0.90 | 10.03 | 0.91 | 9.29 |
| lr1e-3_e60 | `--aux-weight 1.0 --lr 1e-3 --epochs 60` | 175 | 0.3472 | 0.3423, 0.3561, 0.3431 | 0.92 | 10.77 | 0.93 | 9.98 |
| lr1e-3_e200 **winner** | `--aux-weight 1.0 --lr 1e-3 --epochs 200 --patience 20` | 175 | 0.2676 | 0.2547, 0.2619, 0.2862 | 0.84 | 9.89 | 0.87 | 9.12 |
| lr3e-3_e60 | `--aux-weight 1.0 --lr 3e-3 --epochs 60` | 175 | 0.3542 | 0.3310, 0.3385, 0.3929 | 0.96 | 10.94 | 0.96 | 10.29 |

winner: lr1e-3_e200 → flags `--aux-weight 1.0 --lr 1e-3 --epochs 200 --patience 20` (chosen by the inner term alone, as registered)
