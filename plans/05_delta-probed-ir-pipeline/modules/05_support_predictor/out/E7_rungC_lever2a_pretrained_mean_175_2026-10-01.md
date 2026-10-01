# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2a_pretrained_mean_175_2026-10-01 (2026-10-01 10:05)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; mean aggregation; hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.38 | 3.76 | 0.37 | 4.35 | 23.27 | 0.228 | 1949 |
| 175 | 0 | (b) | 1.69 | 3.74 | 0.45 | 7.06 | 23.09 | 0.308 | 1949 |
| 175 | 1 | (a) | 1.79 | 3.76 | 0.48 | 6.45 | 23.27 | 0.310 | 620 |
| 175 | 1 | (b) | 1.90 | 3.74 | 0.51 | 7.01 | 23.09 | 0.359 | 620 |
| 175 | 2 | (a) | 1.45 | 3.76 | 0.38 | 5.07 | 23.27 | 0.259 | 1427 |
| 175 | 2 | (b) | 1.63 | 3.74 | 0.44 | 5.07 | 23.09 | 0.298 | 1427 |

wall 4229 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
