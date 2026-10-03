# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_ring3keep25_2026-10-03 (2026-10-03 01:10)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 658 | 0 | (a) | 0.86 | 3.76 | 0.23 | 2.82 | 23.27 | 0.148 | 3260 |
| 658 | 0 | (b) | 1.25 | 3.74 | 0.33 | 3.45 | 23.09 | 0.244 | 3260 |
| 658 | 1 | (a) | 1.00 | 3.76 | 0.27 | 3.92 | 23.27 | 0.196 | 2857 |
| 658 | 1 | (b) | 1.41 | 3.74 | 0.38 | 3.76 | 23.09 | 0.269 | 2857 |
| 658 | 2 | (a) | 0.95 | 3.76 | 0.25 | 3.16 | 23.27 | 0.174 | 2887 |
| 658 | 2 | (b) | 1.28 | 3.74 | 0.34 | 3.76 | 23.09 | 0.250 | 2887 |

wall 9189 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
