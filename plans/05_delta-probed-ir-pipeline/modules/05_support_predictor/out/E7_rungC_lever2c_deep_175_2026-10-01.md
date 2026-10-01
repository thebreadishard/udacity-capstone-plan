# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2c_deep_175_2026-10-01 (2026-10-01 22:58)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.38 | 3.76 | 0.37 | 3.94 | 23.27 | 0.218 | 1351 |
| 175 | 0 | (b) | 1.56 | 3.74 | 0.42 | 4.60 | 23.09 | 0.281 | 1351 |
| 175 | 1 | (a) | 1.65 | 3.76 | 0.44 | 6.19 | 23.27 | 0.269 | 574 |
| 175 | 1 | (b) | 1.77 | 3.74 | 0.47 | 6.42 | 23.09 | 0.321 | 574 |
| 175 | 2 | (a) | 1.34 | 3.76 | 0.36 | 3.67 | 23.27 | 0.214 | 1555 |
| 175 | 2 | (b) | 1.50 | 3.74 | 0.40 | 4.91 | 23.09 | 0.270 | 1555 |

wall 3588 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
