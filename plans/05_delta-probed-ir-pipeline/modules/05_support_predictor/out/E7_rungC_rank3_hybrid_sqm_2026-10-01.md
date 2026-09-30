# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_rank3_hybrid_sqm_2026-10-01 (2026-10-01 00:17)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.68 | 3.76 | 0.45 | 4.52 | 23.27 | 0.269 | 297 |
| 175 | 0 | (b) | 1.77 | 3.74 | 0.47 | 4.97 | 23.09 | 0.326 | 297 |
| 175 | 1 | (a) | 1.63 | 3.76 | 0.43 | 4.76 | 23.27 | 0.270 | 215 |
| 175 | 1 | (b) | 1.92 | 3.74 | 0.51 | 5.25 | 23.09 | 0.346 | 215 |
| 175 | 2 | (a) | 1.75 | 3.76 | 0.47 | 5.02 | 23.27 | 0.280 | 186 |
| 175 | 2 | (b) | 1.98 | 3.74 | 0.53 | 5.45 | 23.09 | 0.353 | 186 |

wall 747 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
