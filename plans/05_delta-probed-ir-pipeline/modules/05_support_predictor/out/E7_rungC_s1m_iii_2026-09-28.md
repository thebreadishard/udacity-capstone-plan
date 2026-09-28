# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_s1m_iii_2026-09-28 (2026-09-28 08:02)

recipe: lr 0.001, epochs 60, loss internal, aux weight 0.1, output scale rms, inner validation 0.15, patience 0; pool layers A,A2; mean aggregation

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 3.53 | 3.76 | 0.94 | 11.14 | 23.29 | 0.687 | 108 |
| 175 | 0 | (b) | 3.51 | 3.74 | 0.94 | 10.24 | 23.09 | 0.702 | 108 |
| 175 | 1 | (a) | 3.40 | 3.76 | 0.90 | 10.61 | 23.29 | 0.661 | 106 |
| 175 | 1 | (b) | 3.42 | 3.74 | 0.92 | 9.85 | 23.09 | 0.681 | 106 |
| 175 | 2 | (a) | 3.54 | 3.76 | 0.94 | 10.15 | 23.29 | 0.691 | 106 |
| 175 | 2 | (b) | 3.53 | 3.74 | 0.95 | 9.49 | 23.09 | 0.705 | 106 |

wall 336 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
