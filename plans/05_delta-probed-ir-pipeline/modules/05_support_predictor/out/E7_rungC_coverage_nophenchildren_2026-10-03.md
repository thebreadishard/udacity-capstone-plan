# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_nophenchildren_2026-10-03 (2026-10-03 04:04)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 738 | 0 | (a) | 0.82 | 3.76 | 0.22 | 2.49 | 23.27 | 0.137 | 3271 |
| 738 | 0 | (b) | 1.24 | 3.74 | 0.33 | 3.55 | 23.09 | 0.232 | 3271 |
| 738 | 1 | (a) | 0.85 | 3.76 | 0.23 | 2.64 | 23.27 | 0.137 | 3440 |
| 738 | 1 | (b) | 1.24 | 3.74 | 0.33 | 3.75 | 23.09 | 0.239 | 3440 |
| 738 | 2 | (a) | 0.81 | 3.76 | 0.22 | 2.66 | 23.27 | 0.134 | 3286 |
| 738 | 2 | (b) | 1.20 | 3.74 | 0.32 | 3.60 | 23.09 | 0.227 | 3286 |

wall 10209 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
