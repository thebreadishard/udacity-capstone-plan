# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35h2_fd (2026-10-17 11:32)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 4.58 | 5.90 | 0.78 | 8.00 | 24.31 | 0.360 | 4967 |
| 750 | 0 | (b) | 1.39 | 3.91 | 0.36 | 3.68 | 23.03 | 0.269 | 4967 |
| 750 | 1 | (a) | 4.57 | 5.90 | 0.78 | 7.98 | 24.31 | 0.364 | 4975 |
| 750 | 1 | (b) | 1.31 | 3.91 | 0.34 | 3.33 | 23.03 | 0.247 | 4975 |
| 750 | 2 | (a) | 4.60 | 5.90 | 0.78 | 7.51 | 24.31 | 0.370 | 6795 |
| 750 | 2 | (b) | 1.48 | 3.91 | 0.38 | 3.59 | 23.03 | 0.276 | 6795 |

wall 17103 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
