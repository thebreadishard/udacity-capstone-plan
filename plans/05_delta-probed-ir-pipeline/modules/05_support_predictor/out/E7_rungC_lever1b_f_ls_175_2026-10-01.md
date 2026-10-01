# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever1b_f_ls_175_2026-10-01 (2026-10-01 14:11)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f; LS pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.30 | 3.76 | 0.34 | 4.64 | 23.27 | 0.228 | 851 |
| 175 | 0 | (b) | 1.53 | 3.74 | 0.41 | 7.38 | 23.09 | 0.318 | 851 |
| 175 | 1 | (a) | 1.21 | 3.76 | 0.32 | 4.20 | 23.27 | 0.210 | 914 |
| 175 | 1 | (b) | 1.50 | 3.74 | 0.40 | 5.13 | 23.09 | 0.282 | 914 |
| 175 | 2 | (a) | 1.21 | 3.76 | 0.32 | 4.96 | 23.27 | 0.221 | 1535 |
| 175 | 2 | (b) | 1.50 | 3.74 | 0.40 | 5.66 | 23.09 | 0.287 | 1535 |

wall 3409 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
