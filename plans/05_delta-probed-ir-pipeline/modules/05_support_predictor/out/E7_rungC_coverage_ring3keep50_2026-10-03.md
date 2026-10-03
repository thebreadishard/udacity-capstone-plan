# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_ring3keep50_2026-10-03 (2026-10-03 01:10)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 689 | 0 | (a) | 0.87 | 3.76 | 0.23 | 2.43 | 23.27 | 0.135 | 3204 |
| 689 | 0 | (b) | 1.30 | 3.74 | 0.35 | 3.85 | 23.09 | 0.245 | 3204 |
| 689 | 1 | (a) | 0.85 | 3.76 | 0.22 | 2.44 | 23.27 | 0.130 | 3050 |
| 689 | 1 | (b) | 1.29 | 3.74 | 0.35 | 3.94 | 23.09 | 0.236 | 3050 |
| 689 | 2 | (a) | 0.81 | 3.76 | 0.22 | 2.62 | 23.27 | 0.134 | 3438 |
| 689 | 2 | (b) | 1.26 | 3.74 | 0.34 | 3.71 | 23.09 | 0.250 | 3438 |

wall 9886 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
