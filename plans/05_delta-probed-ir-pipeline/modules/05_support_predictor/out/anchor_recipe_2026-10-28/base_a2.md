# Rung C (equivariant ΔH, C1 from scratch) — out/anchor_recipe_2026-10-28/base_a2 (2026-10-28 22:48)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 4.99 | 3.73 | 1.34 | 38.86 | 23.37 | 1.396 | 2923 |
| 750 | 0 | (b) | 5.07 | 3.87 | 1.31 | 38.42 | 22.95 | 1.363 | 2923 |
| 750 | 1 | (a) | 5.00 | 3.73 | 1.34 | 38.94 | 23.37 | 1.397 | 3432 |
| 750 | 1 | (b) | 5.01 | 3.87 | 1.29 | 38.96 | 22.95 | 1.367 | 3432 |
| 750 | 2 | (a) | 4.94 | 3.73 | 1.33 | 39.09 | 23.37 | 1.388 | 5300 |
| 750 | 2 | (b) | 4.96 | 3.87 | 1.28 | 39.20 | 22.95 | 1.350 | 5300 |

wall 11956 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
