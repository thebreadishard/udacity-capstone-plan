# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35h_analytic (2026-10-17 00:22)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.68 | 3.73 | 0.18 | 2.36 | 23.37 | 0.123 | 3674 |
| 750 | 0 | (b) | 1.29 | 3.91 | 0.33 | 3.34 | 23.03 | 0.250 | 3674 |
| 750 | 1 | (a) | 0.67 | 3.73 | 0.18 | 2.67 | 23.37 | 0.129 | 3527 |
| 750 | 1 | (b) | 1.27 | 3.91 | 0.32 | 3.32 | 23.03 | 0.241 | 3527 |
| 750 | 2 | (a) | 0.74 | 3.73 | 0.20 | 2.59 | 23.37 | 0.136 | 6592 |
| 750 | 2 | (b) | 1.50 | 3.91 | 0.38 | 3.45 | 23.03 | 0.282 | 6592 |

wall 14207 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
