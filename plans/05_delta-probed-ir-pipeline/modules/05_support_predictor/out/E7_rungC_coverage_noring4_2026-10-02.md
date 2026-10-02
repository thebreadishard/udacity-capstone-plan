# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_noring4_2026-10-02 (2026-10-02 21:58)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 743 | 0 | (a) | 0.80 | 3.76 | 0.21 | 2.92 | 23.27 | 0.142 | 2694 |
| 743 | 0 | (b) | 1.29 | 3.74 | 0.35 | 3.72 | 23.09 | 0.243 | 2694 |
| 743 | 1 | (a) | 0.84 | 3.76 | 0.22 | 2.41 | 23.27 | 0.136 | 3821 |
| 743 | 1 | (b) | 1.34 | 3.74 | 0.36 | 3.57 | 23.09 | 0.248 | 3821 |
| 743 | 2 | (a) | 0.85 | 3.76 | 0.23 | 2.59 | 23.27 | 0.133 | 4199 |
| 743 | 2 | (b) | 1.34 | 3.74 | 0.36 | 3.84 | 23.09 | 0.253 | 4199 |

wall 10958 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
