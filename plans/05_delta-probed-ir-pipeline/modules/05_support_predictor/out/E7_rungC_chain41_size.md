# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain41_size (2026-10-17 17:10)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 972 | 0 | (a) | 0.66 | 3.73 | 0.18 | 2.28 | 23.37 | 0.120 | 3778 |
| 972 | 0 | (b) | 1.16 | 3.90 | 0.30 | 3.31 | 23.01 | 0.233 | 3778 |
| 972 | 1 | (a) | 0.69 | 3.73 | 0.18 | 2.42 | 23.37 | 0.125 | 7011 |
| 972 | 1 | (b) | 1.30 | 3.90 | 0.33 | 3.42 | 23.01 | 0.252 | 7011 |
| 972 | 2 | (a) | 0.67 | 3.73 | 0.18 | 2.35 | 23.37 | 0.119 | 5796 |
| 972 | 2 | (b) | 1.30 | 3.90 | 0.33 | 3.24 | 23.01 | 0.249 | 5796 |

wall 17049 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
