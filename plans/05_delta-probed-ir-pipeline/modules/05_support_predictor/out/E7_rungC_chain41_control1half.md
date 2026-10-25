# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain41_control1half (2026-10-19 04:55)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 978 | 0 | (a) | 0.66 | 3.73 | 0.18 | 2.13 | 23.37 | 0.124 | 3326 |
| 978 | 0 | (b) | 1.18 | 3.90 | 0.30 | 3.00 | 23.01 | 0.234 | 3326 |
| 978 | 1 | (a) | 0.61 | 3.73 | 0.16 | 2.17 | 23.37 | 0.118 | 5533 |
| 978 | 1 | (b) | 1.08 | 3.90 | 0.28 | 2.97 | 23.01 | 0.219 | 5533 |
| 978 | 2 | (a) | 0.66 | 3.73 | 0.18 | 2.28 | 23.37 | 0.120 | 6021 |
| 978 | 2 | (b) | 1.11 | 3.90 | 0.29 | 3.02 | 23.01 | 0.220 | 6021 |

wall 15317 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
