# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s3more_c00_control (2026-11-17 04:40)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 1082 | 3 | (a) | 0.56 | 3.73 | 0.15 | 2.53 | 23.37 | 0.133 | 7009 |
| 1082 | 3 | (b) | 0.83 | 3.87 | 0.21 | 2.27 | 22.93 | 0.178 | 7009 |
| 1082 | 4 | (a) | 0.58 | 3.73 | 0.15 | 2.17 | 23.37 | 0.135 | 7147 |
| 1082 | 4 | (b) | 0.86 | 3.87 | 0.22 | 2.20 | 22.93 | 0.178 | 7147 |

wall 14561 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
