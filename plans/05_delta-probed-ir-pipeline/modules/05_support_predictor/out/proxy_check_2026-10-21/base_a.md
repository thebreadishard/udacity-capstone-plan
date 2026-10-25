# Rung C (equivariant ΔH, C1 from scratch) — out/proxy_check_2026-10-21/base_a (2026-10-21 13:54)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 4.95 | 3.73 | 1.33 | 38.98 | 23.37 | 1.397 | 4694 |
| 750 | 0 | (b) | 5.02 | 3.90 | 1.29 | 38.87 | 23.01 | 1.358 | 4694 |
| 750 | 1 | (a) | 4.94 | 3.73 | 1.33 | 38.92 | 23.37 | 1.412 | 3542 |
| 750 | 1 | (b) | 5.00 | 3.90 | 1.28 | 38.32 | 23.01 | 1.359 | 3542 |
| 750 | 2 | (a) | 4.97 | 3.73 | 1.33 | 38.89 | 23.37 | 1.398 | 3974 |
| 750 | 2 | (b) | 5.07 | 3.90 | 1.30 | 38.94 | 23.01 | 1.369 | 3974 |

wall 12514 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
