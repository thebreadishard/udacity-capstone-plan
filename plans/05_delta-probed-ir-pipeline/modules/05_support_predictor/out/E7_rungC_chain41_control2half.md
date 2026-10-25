# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain41_control2half (2026-10-19 09:13)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 977 | 0 | (a) | 0.64 | 3.73 | 0.17 | 2.13 | 23.37 | 0.114 | 13479 |
| 977 | 0 | (b) | 1.22 | 3.90 | 0.31 | 3.21 | 23.01 | 0.242 | 13479 |
| 977 | 1 | (a) | 0.63 | 3.73 | 0.17 | 1.92 | 23.37 | 0.108 | 11411 |
| 977 | 1 | (b) | 1.23 | 3.90 | 0.31 | 3.11 | 23.01 | 0.233 | 11411 |
| 977 | 2 | (a) | 0.60 | 3.73 | 0.16 | 1.91 | 23.37 | 0.109 | 8265 |
| 977 | 2 | (b) | 1.20 | 3.90 | 0.31 | 3.18 | 23.01 | 0.238 | 8265 |

wall 33705 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
