# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain39_control_2026-10-09 (2026-10-09 06:29)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 370 | 0 | (a) | 0.98 | 3.73 | 0.26 | 3.18 | 23.37 | 0.165 | 1100 |
| 370 | 0 | (b) | 1.67 | 3.91 | 0.43 | 4.24 | 23.03 | 0.307 | 1100 |
| 370 | 0 | (s) | 1.39 | 3.94 | 0.35 | 3.81 | 23.17 | 0.269 | 1100 |
| 370 | 1 | (a) | 0.78 | 3.73 | 0.21 | 2.90 | 23.37 | 0.146 | 1012 |
| 370 | 1 | (b) | 1.42 | 3.91 | 0.36 | 3.54 | 23.03 | 0.263 | 1012 |
| 370 | 1 | (s) | 1.29 | 3.94 | 0.33 | 3.65 | 23.17 | 0.245 | 1012 |
| 370 | 2 | (a) | 0.84 | 3.73 | 0.22 | 3.01 | 23.37 | 0.151 | 979 |
| 370 | 2 | (b) | 1.39 | 3.91 | 0.36 | 3.68 | 23.03 | 0.264 | 979 |
| 370 | 2 | (s) | 1.47 | 3.94 | 0.37 | 3.60 | 23.17 | 0.269 | 979 |

wall 3232 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
