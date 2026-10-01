# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever1b_f_ls_750_2026-10-01 (2026-10-01 15:14)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f; LS pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 1.11 | 3.76 | 0.30 | 4.26 | 23.27 | 0.197 | 4037 |
| 750 | 0 | (b) | 1.33 | 3.74 | 0.36 | 4.44 | 23.09 | 0.260 | 4037 |
| 750 | 1 | (a) | 1.31 | 3.76 | 0.35 | 3.58 | 23.27 | 0.210 | 5152 |
| 750 | 1 | (b) | 1.71 | 3.74 | 0.46 | 4.88 | 23.09 | 0.316 | 5152 |
| 750 | 2 | (a) | 1.65 | 3.76 | 0.44 | 3.89 | 23.27 | 0.245 | 6518 |
| 750 | 2 | (b) | 1.69 | 3.74 | 0.45 | 4.67 | 23.09 | 0.313 | 6518 |

wall 16012 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
