# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever3b_both_175_2026-10-01 (2026-10-01 14:30)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern d; LS pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.05 | 3.76 | 0.28 | 5.77 | 23.27 | 0.382 | 1119 |
| 175 | 0 | (b) | 1.46 | 3.74 | 0.39 | 6.56 | 23.09 | 0.393 | 1119 |
| 175 | 1 | (a) | 1.11 | 3.76 | 0.29 | 6.30 | 23.27 | 0.502 | 1638 |
| 175 | 1 | (b) | 1.58 | 3.74 | 0.42 | 6.25 | 23.09 | 0.423 | 1638 |
| 175 | 2 | (a) | 1.05 | 3.76 | 0.28 | 7.47 | 23.27 | 0.335 | 1192 |
| 175 | 2 | (b) | 1.53 | 3.74 | 0.41 | 8.80 | 23.09 | 0.383 | 1192 |

wall 4068 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
