# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain36_hinge_750_2026-10-07 (2026-10-07 07:32)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.70 | 3.73 | 0.19 | 2.45 | 23.37 | 0.128 | 2311 |
| 750 | 0 | (b) | 1.22 | 3.74 | 0.33 | 3.50 | 23.09 | 0.228 | 2311 |
| 750 | 1 | (a) | 0.71 | 3.73 | 0.19 | 2.39 | 23.37 | 0.131 | 4132 |
| 750 | 1 | (b) | 1.21 | 3.74 | 0.32 | 3.58 | 23.09 | 0.232 | 4132 |
| 750 | 2 | (a) | 0.74 | 3.73 | 0.20 | 2.74 | 23.37 | 0.139 | 3072 |
| 750 | 2 | (b) | 1.28 | 3.74 | 0.34 | 3.79 | 23.09 | 0.246 | 3072 |

wall 9782 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
