# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35h2_analytic (2026-10-17 07:30)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.75 | 3.73 | 0.20 | 2.56 | 23.37 | 0.130 | 4414 |
| 750 | 0 | (b) | 1.47 | 3.90 | 0.38 | 3.60 | 23.01 | 0.283 | 4414 |
| 750 | 1 | (a) | 0.63 | 3.73 | 0.17 | 2.20 | 23.37 | 0.109 | 5054 |
| 750 | 1 | (b) | 1.26 | 3.90 | 0.32 | 3.42 | 23.01 | 0.243 | 5054 |
| 750 | 2 | (a) | 0.63 | 3.73 | 0.17 | 2.12 | 23.37 | 0.113 | 4679 |
| 750 | 2 | (b) | 1.22 | 3.90 | 0.31 | 3.35 | 23.01 | 0.237 | 4679 |

wall 14539 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
