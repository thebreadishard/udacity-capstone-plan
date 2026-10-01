# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_hybrid_pf_2026-10-01 (2026-10-01 02:28)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.58 | 3.76 | 0.42 | 4.25 | 23.27 | 0.262 | 275 |
| 175 | 0 | (b) | 1.72 | 3.74 | 0.46 | 4.57 | 23.09 | 0.319 | 275 |
| 175 | 1 | (a) | 1.64 | 3.76 | 0.44 | 4.93 | 23.27 | 0.277 | 128 |
| 175 | 1 | (b) | 1.80 | 3.74 | 0.48 | 5.79 | 23.09 | 0.332 | 128 |
| 175 | 2 | (a) | 1.72 | 3.76 | 0.46 | 4.99 | 23.27 | 0.289 | 266 |
| 175 | 2 | (b) | 1.82 | 3.74 | 0.49 | 5.07 | 23.09 | 0.339 | 266 |

wall 718 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
