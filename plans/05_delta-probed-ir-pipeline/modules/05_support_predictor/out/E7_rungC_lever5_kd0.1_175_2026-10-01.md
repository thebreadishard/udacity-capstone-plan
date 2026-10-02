# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever5_kd0.1_175_2026-10-01 (2026-10-02 04:17)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.84 | 3.76 | 0.22 | 2.67 | 23.27 | 0.140 | 1074 |
| 175 | 0 | (b) | 1.33 | 3.74 | 0.36 | 3.91 | 23.09 | 0.250 | 1074 |
| 175 | 1 | (a) | 0.86 | 3.76 | 0.23 | 2.94 | 23.27 | 0.145 | 973 |
| 175 | 1 | (b) | 1.24 | 3.74 | 0.33 | 3.80 | 23.09 | 0.233 | 973 |
| 175 | 2 | (a) | 0.90 | 3.76 | 0.24 | 2.72 | 23.27 | 0.148 | 1088 |
| 175 | 2 | (b) | 1.43 | 3.74 | 0.38 | 4.34 | 23.09 | 0.268 | 1088 |

wall 3255 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
