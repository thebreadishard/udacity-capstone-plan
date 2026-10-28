# Rung C (equivariant ΔH, C1 from scratch) — out/anchor_price_2026-10-28/base_c (2026-10-28 14:38)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 3.30 | 3.73 | 0.88 | 40.54 | 23.37 | 1.307 | 1783 |
| 750 | 0 | (b) | 4.64 | 3.87 | 1.20 | 43.91 | 22.95 | 1.377 | 1783 |
| 750 | 1 | (a) | 3.31 | 3.73 | 0.89 | 41.00 | 23.37 | 1.303 | 2514 |
| 750 | 1 | (b) | 3.48 | 3.87 | 0.90 | 42.32 | 22.95 | 1.366 | 2514 |
| 750 | 2 | (a) | 3.44 | 3.73 | 0.92 | 41.48 | 23.37 | 1.367 | 2431 |
| 750 | 2 | (b) | 3.51 | 3.87 | 0.91 | 42.49 | 22.95 | 1.363 | 2431 |

wall 7108 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
