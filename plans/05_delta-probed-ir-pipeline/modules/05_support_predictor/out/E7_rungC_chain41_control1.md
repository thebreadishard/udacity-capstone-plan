# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain41_control1 (2026-10-17 21:54)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 986 | 0 | (a) | 0.64 | 3.73 | 0.17 | 2.12 | 23.37 | 0.114 | 9619 |
| 986 | 0 | (b) | 1.14 | 3.90 | 0.29 | 3.10 | 23.01 | 0.222 | 9619 |
| 986 | 1 | (a) | 0.60 | 3.73 | 0.16 | 2.30 | 23.37 | 0.115 | 6395 |
| 986 | 1 | (b) | 1.10 | 3.90 | 0.28 | 3.09 | 23.01 | 0.219 | 6395 |
| 986 | 2 | (a) | 0.58 | 3.73 | 0.15 | 1.97 | 23.37 | 0.106 | 7598 |
| 986 | 2 | (b) | 1.08 | 3.90 | 0.28 | 3.14 | 23.01 | 0.221 | 7598 |

wall 24068 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
