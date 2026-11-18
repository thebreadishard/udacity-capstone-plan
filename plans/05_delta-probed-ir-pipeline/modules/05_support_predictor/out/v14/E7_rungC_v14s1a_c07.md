# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c07 (2026-11-18 07:28)

recipe: lr 0.000489 (cosine schedule), epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 300; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.65 | 3.73 | 0.18 | 3.03 | 23.37 | 0.147 | 19921 |
| 913 | 0 | (b) | 0.80 | 3.87 | 0.21 | 2.18 | 22.93 | 0.169 | 19921 |
| 913 | 0 | (sel) | 1.63 | 4.09 | 0.40 | 3.13 | 22.92 | 0.268 | 19921 |

wall 20355 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
