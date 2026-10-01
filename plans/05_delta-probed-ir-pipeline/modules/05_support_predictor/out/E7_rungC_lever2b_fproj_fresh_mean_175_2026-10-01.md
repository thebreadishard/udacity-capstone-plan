# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2b_fproj_fresh_mean_175_2026-10-01 (2026-10-01 22:37)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; mean aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.04 | 3.76 | 0.28 | 4.63 | 23.27 | 0.191 | 1070 |
| 175 | 0 | (b) | 1.41 | 3.74 | 0.38 | 6.00 | 23.09 | 0.274 | 1070 |
| 175 | 1 | (a) | 1.27 | 3.76 | 0.34 | 6.93 | 23.27 | 0.274 | 529 |
| 175 | 1 | (b) | 1.54 | 3.74 | 0.41 | 6.65 | 23.09 | 0.308 | 529 |
| 175 | 2 | (a) | 1.03 | 3.76 | 0.27 | 9.37 | 23.27 | 0.330 | 949 |
| 175 | 2 | (b) | 1.41 | 3.74 | 0.38 | 5.37 | 23.09 | 0.274 | 949 |

wall 2710 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
