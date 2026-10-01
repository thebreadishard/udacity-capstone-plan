# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2b_fproj_pretrained_long_175_2026-10-01 (2026-10-01 23:22)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; mean aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.94 | 3.76 | 0.25 | 4.19 | 23.27 | 0.181 | 1092 |
| 175 | 0 | (b) | 1.28 | 3.74 | 0.34 | 4.91 | 23.09 | 0.249 | 1092 |
| 175 | 1 | (a) | 1.01 | 3.76 | 0.27 | 4.82 | 23.27 | 0.198 | 726 |
| 175 | 1 | (b) | 1.49 | 3.74 | 0.40 | 5.35 | 23.09 | 0.281 | 726 |
| 175 | 2 | (a) | 1.02 | 3.76 | 0.27 | 5.13 | 23.27 | 0.227 | 813 |
| 175 | 2 | (b) | 1.47 | 3.74 | 0.39 | 5.82 | 23.09 | 0.283 | 813 |

wall 2753 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
