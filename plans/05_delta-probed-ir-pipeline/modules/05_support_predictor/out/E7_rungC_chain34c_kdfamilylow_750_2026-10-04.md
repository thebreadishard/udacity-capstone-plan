# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain34c_kdfamilylow_750_2026-10-04 (2026-10-04 08:41)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.80 | 3.76 | 0.21 | 2.67 | 23.27 | 0.140 | 3257 |
| 750 | 0 | (b) | 1.13 | 3.74 | 0.30 | 3.72 | 23.09 | 0.218 | 3257 |
| 750 | 1 | (a) | 0.80 | 3.76 | 0.21 | 2.46 | 23.27 | 0.126 | 5398 |
| 750 | 1 | (b) | 1.28 | 3.74 | 0.34 | 3.55 | 23.09 | 0.237 | 5398 |
| 750 | 2 | (a) | 0.83 | 3.76 | 0.22 | 2.89 | 23.27 | 0.134 | 4058 |
| 750 | 2 | (b) | 1.22 | 3.74 | 0.33 | 3.64 | 23.09 | 0.233 | 4058 |

wall 13080 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
