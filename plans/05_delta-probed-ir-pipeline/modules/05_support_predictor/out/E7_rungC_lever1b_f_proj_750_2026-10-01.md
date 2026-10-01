# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever1b_f_proj_750_2026-10-01 (2026-10-01 19:41)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.94 | 3.76 | 0.25 | 3.61 | 23.27 | 0.161 | 3833 |
| 750 | 0 | (b) | 1.32 | 3.74 | 0.35 | 3.95 | 23.09 | 0.248 | 3833 |
| 750 | 1 | (a) | 1.00 | 3.76 | 0.27 | 4.08 | 23.27 | 0.161 | 3960 |
| 750 | 1 | (b) | 1.44 | 3.74 | 0.39 | 5.03 | 23.09 | 0.275 | 3960 |
| 750 | 2 | (a) | 1.03 | 3.76 | 0.28 | 3.82 | 23.27 | 0.177 | 3850 |
| 750 | 2 | (b) | 1.43 | 3.74 | 0.38 | 4.21 | 23.09 | 0.271 | 3850 |

wall 11910 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
