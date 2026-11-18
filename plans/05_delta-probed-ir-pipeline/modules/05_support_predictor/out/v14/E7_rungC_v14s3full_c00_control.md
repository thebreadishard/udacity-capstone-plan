# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s3full_c00_control (2026-11-16 21:59)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 1082 | 0 | (a) | 0.49 | 3.73 | 0.13 | 2.00 | 23.37 | 0.112 | 7976 |
| 1082 | 0 | (b) | 0.81 | 3.87 | 0.21 | 2.27 | 22.93 | 0.166 | 7976 |
| 1082 | 1 | (a) | 0.55 | 3.73 | 0.15 | 1.87 | 23.37 | 0.108 | 6663 |
| 1082 | 1 | (b) | 0.78 | 3.87 | 0.20 | 2.13 | 22.93 | 0.164 | 6663 |
| 1082 | 2 | (a) | 0.50 | 3.73 | 0.13 | 1.81 | 23.37 | 0.105 | 8007 |
| 1082 | 2 | (b) | 0.79 | 3.87 | 0.21 | 2.27 | 22.93 | 0.168 | 8007 |

wall 23061 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
