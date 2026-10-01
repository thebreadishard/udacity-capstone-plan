# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever3_kring_175_2026-10-01 (2026-10-01 12:20)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term kring, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.20 | 3.76 | 0.32 | 7.27 | 23.27 | 1.029 | 1195 |
| 175 | 0 | (b) | 1.61 | 3.74 | 0.43 | 7.12 | 23.09 | 0.864 | 1195 |
| 175 | 1 | (a) | 1.10 | 3.76 | 0.29 | 6.50 | 23.27 | 0.420 | 909 |
| 175 | 1 | (b) | 1.56 | 3.74 | 0.42 | 6.94 | 23.09 | 0.406 | 909 |
| 175 | 2 | (a) | 1.02 | 3.76 | 0.27 | 8.15 | 23.27 | 0.365 | 703 |
| 175 | 2 | (b) | 1.46 | 3.74 | 0.39 | 9.15 | 23.09 | 0.381 | 703 |

wall 2897 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
