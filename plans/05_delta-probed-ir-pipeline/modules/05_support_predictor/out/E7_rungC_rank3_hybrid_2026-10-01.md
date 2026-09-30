# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_rank3_hybrid_2026-10-01 (2026-10-01 00:02)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.77 | 3.76 | 0.47 | 4.29 | 23.27 | 0.267 | 357 |
| 175 | 0 | (b) | 1.99 | 3.74 | 0.53 | 4.93 | 23.09 | 0.353 | 357 |
| 175 | 1 | (a) | 1.81 | 3.76 | 0.48 | 6.28 | 23.27 | 0.318 | 188 |
| 175 | 1 | (b) | 2.03 | 3.74 | 0.54 | 6.21 | 23.09 | 0.376 | 188 |
| 175 | 2 | (a) | 1.73 | 3.76 | 0.46 | 5.04 | 23.27 | 0.296 | 319 |
| 175 | 2 | (b) | 2.00 | 3.74 | 0.53 | 5.47 | 23.09 | 0.363 | 319 |

wall 912 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
