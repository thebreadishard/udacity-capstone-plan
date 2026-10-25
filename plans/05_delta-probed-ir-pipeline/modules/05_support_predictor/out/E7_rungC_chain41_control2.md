# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain41_control2 (2026-10-18 04:37)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 983 | 0 | (a) | 0.58 | 3.73 | 0.16 | 1.98 | 23.37 | 0.107 | 7680 |
| 983 | 0 | (b) | 1.16 | 3.90 | 0.30 | 3.29 | 23.01 | 0.232 | 7680 |
| 983 | 1 | (a) | 0.64 | 3.73 | 0.17 | 2.21 | 23.37 | 0.115 | 6530 |
| 983 | 1 | (b) | 1.11 | 3.90 | 0.28 | 3.15 | 23.01 | 0.219 | 6530 |
| 983 | 2 | (a) | 0.61 | 3.73 | 0.16 | 1.99 | 23.37 | 0.110 | 6794 |
| 983 | 2 | (b) | 1.17 | 3.90 | 0.30 | 3.02 | 23.01 | 0.225 | 6794 |

wall 21542 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
