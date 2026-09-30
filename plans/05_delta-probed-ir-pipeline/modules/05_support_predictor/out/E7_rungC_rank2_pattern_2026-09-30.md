# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_rank2_pattern_2026-09-30 (2026-09-30 23:52)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 3.74 | 3.76 | 0.99 | 14.06 | 23.27 | 0.764 | 122 |
| 175 | 0 | (b) | 3.70 | 3.74 | 0.99 | 13.58 | 23.09 | 0.767 | 122 |
| 175 | 1 | (a) | 3.86 | 3.76 | 1.03 | 11.64 | 23.27 | 0.755 | 137 |
| 175 | 1 | (b) | 3.82 | 3.74 | 1.02 | 11.12 | 23.09 | 0.753 | 137 |
| 175 | 2 | (a) | 3.89 | 3.76 | 1.03 | 10.96 | 23.27 | 0.754 | 167 |
| 175 | 2 | (b) | 3.85 | 3.74 | 1.03 | 10.34 | 23.09 | 0.752 | 167 |

wall 464 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
