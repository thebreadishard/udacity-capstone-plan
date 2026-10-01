# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2b_pretrained_long_175_2026-10-01 (2026-10-01 15:40)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; mean aggregation; hybrid head + SQM α + rung B pair features; pattern d; LS pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.89 | 3.76 | 0.50 | 4.70 | 23.27 | 0.275 | 2239 |
| 175 | 0 | (b) | 1.95 | 3.74 | 0.52 | 5.13 | 23.09 | 0.341 | 2239 |
| 175 | 1 | (a) | 1.75 | 3.76 | 0.46 | 4.19 | 23.27 | 0.249 | 1989 |
| 175 | 1 | (b) | 1.87 | 3.74 | 0.50 | 4.88 | 23.09 | 0.332 | 1989 |
| 175 | 2 | (a) | 1.60 | 3.76 | 0.42 | 4.35 | 23.27 | 0.248 | 1097 |
| 175 | 2 | (b) | 1.61 | 3.74 | 0.43 | 4.90 | 23.09 | 0.294 | 1097 |

wall 5465 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
