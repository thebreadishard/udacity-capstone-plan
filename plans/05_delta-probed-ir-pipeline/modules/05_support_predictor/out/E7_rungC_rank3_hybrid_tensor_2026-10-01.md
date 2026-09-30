# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_rank3_hybrid_tensor_2026-10-01 (2026-10-01 00:29)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; rank-2 tensor input; hybrid head

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.66 | 3.76 | 0.44 | 4.42 | 23.27 | 0.262 | 361 |
| 175 | 0 | (b) | 1.88 | 3.74 | 0.50 | 5.12 | 23.09 | 0.339 | 361 |
| 175 | 1 | (a) | 1.74 | 3.76 | 0.46 | 5.22 | 23.27 | 0.290 | 252 |
| 175 | 1 | (b) | 2.02 | 3.74 | 0.54 | 5.74 | 23.09 | 0.368 | 252 |
| 175 | 2 | (a) | 1.85 | 3.76 | 0.49 | 5.22 | 23.27 | 0.299 | 213 |
| 175 | 2 | (b) | 2.05 | 3.74 | 0.55 | 5.49 | 23.09 | 0.363 | 213 |

wall 876 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
