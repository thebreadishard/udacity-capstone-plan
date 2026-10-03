# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_nophenanthridinechildren_2026-10-03 (2026-10-03 04:03)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 716 | 0 | (a) | 0.92 | 3.76 | 0.25 | 2.73 | 23.27 | 0.147 | 3107 |
| 716 | 0 | (b) | 1.28 | 3.74 | 0.34 | 3.48 | 23.09 | 0.239 | 3107 |
| 716 | 1 | (a) | 0.94 | 3.76 | 0.25 | 2.72 | 23.27 | 0.152 | 3933 |
| 716 | 1 | (b) | 1.31 | 3.74 | 0.35 | 3.97 | 23.09 | 0.244 | 3933 |
| 716 | 2 | (a) | 0.88 | 3.76 | 0.23 | 2.78 | 23.27 | 0.145 | 3880 |
| 716 | 2 | (b) | 1.26 | 3.74 | 0.34 | 3.68 | 23.09 | 0.244 | 3880 |

wall 11124 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
