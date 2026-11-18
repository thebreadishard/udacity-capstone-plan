# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c03_control_schedule (2026-11-16 04:48)

recipe: lr 0.0003 (cosine schedule), epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 300; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.74 | 3.73 | 0.20 | 3.51 | 23.37 | 0.177 | 10179 |
| 913 | 0 | (b) | 0.83 | 3.87 | 0.22 | 2.40 | 22.93 | 0.184 | 10179 |
| 913 | 0 | (sel) | 1.68 | 4.09 | 0.41 | 3.58 | 22.92 | 0.290 | 10179 |

wall 10587 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
