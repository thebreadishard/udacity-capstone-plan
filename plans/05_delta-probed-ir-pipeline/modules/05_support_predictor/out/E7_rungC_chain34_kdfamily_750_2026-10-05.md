# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain34_kdfamily_750_2026-10-05 (2026-10-03 23:12)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.80 | 3.76 | 0.21 | 2.38 | 23.27 | 0.130 | 3896 |
| 750 | 0 | (b) | 1.24 | 3.74 | 0.33 | 3.46 | 23.09 | 0.233 | 3896 |
| 750 | 1 | (a) | 0.81 | 3.76 | 0.22 | 2.52 | 23.27 | 0.132 | 3898 |
| 750 | 1 | (b) | 1.22 | 3.74 | 0.33 | 3.58 | 23.09 | 0.232 | 3898 |
| 750 | 2 | (a) | 0.84 | 3.76 | 0.22 | 2.55 | 23.27 | 0.134 | 3844 |
| 750 | 2 | (b) | 1.24 | 3.74 | 0.33 | 3.51 | 23.09 | 0.234 | 3844 |

wall 11995 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
