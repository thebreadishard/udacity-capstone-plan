# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2a_fresh_mean_175_2026-10-01 (2026-10-01 09:17)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; mean aggregation; hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.65 | 3.76 | 0.44 | 6.04 | 23.27 | 0.287 | 429 |
| 175 | 0 | (b) | 1.75 | 3.74 | 0.47 | 6.12 | 23.09 | 0.331 | 429 |
| 175 | 1 | (a) | 1.66 | 3.76 | 0.44 | 5.91 | 23.27 | 0.284 | 524 |
| 175 | 1 | (b) | 1.82 | 3.74 | 0.49 | 6.98 | 23.09 | 0.358 | 524 |
| 175 | 2 | (a) | 1.43 | 3.76 | 0.38 | 4.84 | 23.27 | 0.245 | 1648 |
| 175 | 2 | (b) | 1.58 | 3.74 | 0.42 | 5.11 | 23.09 | 0.293 | 1648 |

wall 2695 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
