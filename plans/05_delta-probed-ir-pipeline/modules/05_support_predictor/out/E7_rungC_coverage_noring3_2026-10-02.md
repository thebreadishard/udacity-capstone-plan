# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_noring3_2026-10-02 (2026-10-02 21:57)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 627 | 0 | (a) | 1.38 | 3.76 | 0.37 | 3.70 | 23.27 | 0.232 | 3607 |
| 627 | 0 | (b) | 1.56 | 3.74 | 0.42 | 3.76 | 23.09 | 0.291 | 3607 |
| 627 | 1 | (a) | 1.29 | 3.76 | 0.34 | 4.22 | 23.27 | 0.237 | 3111 |
| 627 | 1 | (b) | 1.50 | 3.74 | 0.40 | 4.06 | 23.09 | 0.294 | 3111 |
| 627 | 2 | (a) | 1.50 | 3.76 | 0.40 | 4.69 | 23.27 | 0.271 | 2809 |
| 627 | 2 | (b) | 1.63 | 3.74 | 0.44 | 3.90 | 23.09 | 0.315 | 2809 |

wall 9733 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
