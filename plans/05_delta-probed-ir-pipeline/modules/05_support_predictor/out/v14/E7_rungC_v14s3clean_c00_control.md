# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s3clean_c00_control (2026-11-17 16:13)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 1082 | 0 | (a) | 0.53 | 3.73 | 0.14 | 1.96 | 23.37 | 0.106 | 6776 |
| 1082 | 0 | (b) | 0.77 | 3.87 | 0.20 | 2.20 | 22.93 | 0.164 | 6776 |
| 1082 | 1 | (a) | 0.52 | 3.73 | 0.14 | 2.01 | 23.37 | 0.111 | 5748 |
| 1082 | 1 | (b) | 0.77 | 3.87 | 0.20 | 2.21 | 22.93 | 0.165 | 5748 |
| 1082 | 2 | (a) | 0.50 | 3.73 | 0.14 | 1.84 | 23.37 | 0.099 | 8568 |
| 1082 | 2 | (b) | 0.79 | 3.87 | 0.20 | 2.15 | 22.93 | 0.164 | 8568 |

wall 21570 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
