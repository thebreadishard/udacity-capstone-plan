# Stage pick — out/E7_rungC_s2_{label}_2026-09-27

| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |
|---|---|---|---|---|---|---|---|---|
| lr3e-4_e60 | `--aux-weight 1.0 --lr 3e-4 --epochs 60` | 175 | 0.3502 | 0.3269, 0.3602, 0.3634 | 0.94 | 10.65 | 0.95 | 10.03 |
| lr3e-4_e200 | `--aux-weight 1.0 --lr 3e-4 --epochs 200 --patience 20` | 175 | 0.2682 | 0.2479, 0.2612, 0.2954 | 0.81 | 10.07 | 0.83 | 8.70 |
| lr1e-3_e60 | `--aux-weight 1.0 --lr 1e-3 --epochs 60` | 175 | 0.3120 | 0.3056, 0.3056, 0.3248 | 0.88 | 10.27 | 0.88 | 9.46 |
| lr1e-3_e200 **winner** | `--aux-weight 1.0 --lr 1e-3 --epochs 200 --patience 20` | 175 | 0.2634 | 0.2485, 0.2561, 0.2857 | 0.81 | 9.42 | 0.84 | 8.45 |
| lr3e-3_e60 | `--aux-weight 1.0 --lr 3e-3 --epochs 60` | 175 | nan | 0.6074, nan, 0.3933 | nan | nan | nan | nan |
| lr3e-3_e200 | `--aux-weight 1.0 --lr 3e-3 --epochs 200 --patience 20` | 175 | 0.3201 | 0.3097, 0.3613, 0.2892 | 0.92 | 10.89 | 0.93 | 10.27 |

winner: lr1e-3_e200 → flags `--aux-weight 1.0 --lr 1e-3 --epochs 200 --patience 20` (chosen by the inner term alone, as registered)
