# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever2c_wide_175_2026-10-01 (2026-10-01 23:58)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.35 | 3.76 | 0.36 | 3.91 | 23.27 | 0.205 | 1456 |
| 175 | 0 | (b) | 1.54 | 3.74 | 0.41 | 5.00 | 23.09 | 0.277 | 1456 |
| 175 | 1 | (a) | 1.28 | 3.76 | 0.34 | 3.63 | 23.27 | 0.198 | 1662 |
| 175 | 1 | (b) | 1.48 | 3.74 | 0.40 | 4.26 | 23.09 | 0.265 | 1662 |
| 175 | 2 | (a) | 1.29 | 3.76 | 0.34 | 3.59 | 23.27 | 0.201 | 1826 |
| 175 | 2 | (b) | 1.47 | 3.74 | 0.39 | 4.36 | 23.09 | 0.271 | 1826 |

wall 5054 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
