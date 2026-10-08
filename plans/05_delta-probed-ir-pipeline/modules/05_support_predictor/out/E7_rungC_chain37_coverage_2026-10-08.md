# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain37_coverage_2026-10-08 (2026-10-08 06:26)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 912 | 0 | (a) | 0.70 | 3.73 | 0.19 | 2.15 | 23.37 | 0.118 | 3176 |
| 912 | 0 | (b) | 1.37 | 3.91 | 0.35 | 3.29 | 23.03 | 0.262 | 3176 |
| 912 | 1 | (a) | 0.66 | 3.73 | 0.18 | 2.44 | 23.37 | 0.126 | 3415 |
| 912 | 1 | (b) | 1.28 | 3.91 | 0.33 | 3.40 | 23.03 | 0.248 | 3415 |
| 912 | 2 | (a) | 0.67 | 3.73 | 0.18 | 2.50 | 23.37 | 0.131 | 3574 |
| 912 | 2 | (b) | 1.31 | 3.91 | 0.34 | 3.40 | 23.03 | 0.254 | 3574 |

wall 10399 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
