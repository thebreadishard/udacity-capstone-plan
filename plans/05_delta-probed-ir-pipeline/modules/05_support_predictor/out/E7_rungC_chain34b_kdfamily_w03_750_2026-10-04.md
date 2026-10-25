# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain34b_kdfamily_w03_750_2026-10-04 (2026-10-04 03:12)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.86 | 3.76 | 0.23 | 2.48 | 23.27 | 0.139 | 4316 |
| 750 | 0 | (b) | 1.24 | 3.74 | 0.33 | 3.52 | 23.09 | 0.236 | 4316 |
| 750 | 1 | (a) | 0.85 | 3.76 | 0.23 | 2.58 | 23.27 | 0.139 | 3297 |
| 750 | 1 | (b) | 1.29 | 3.74 | 0.34 | 3.66 | 23.09 | 0.243 | 3297 |
| 750 | 2 | (a) | 0.82 | 3.76 | 0.22 | 2.62 | 23.27 | 0.135 | 4084 |
| 750 | 2 | (b) | 1.24 | 3.74 | 0.33 | 3.44 | 23.09 | 0.232 | 4084 |

wall 12007 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
