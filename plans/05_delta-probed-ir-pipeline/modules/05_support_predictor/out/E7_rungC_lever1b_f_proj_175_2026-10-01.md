# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever1b_f_proj_175_2026-10-01 (2026-10-01 17:11)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.10 | 3.76 | 0.29 | 4.43 | 23.27 | 0.180 | 1157 |
| 175 | 0 | (b) | 1.56 | 3.74 | 0.42 | 6.29 | 23.09 | 0.292 | 1157 |
| 175 | 1 | (a) | 1.07 | 3.76 | 0.28 | 4.73 | 23.27 | 0.187 | 1056 |
| 175 | 1 | (b) | 1.63 | 3.74 | 0.44 | 5.30 | 23.09 | 0.302 | 1056 |
| 175 | 2 | (a) | 1.01 | 3.76 | 0.27 | 4.76 | 23.27 | 0.198 | 1042 |
| 175 | 2 | (b) | 1.45 | 3.74 | 0.39 | 5.91 | 23.09 | 0.290 | 1042 |

wall 3387 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
