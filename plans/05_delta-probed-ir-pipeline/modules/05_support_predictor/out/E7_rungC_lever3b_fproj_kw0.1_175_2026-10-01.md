# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever3b_fproj_kw0.1_175_2026-10-01 (2026-10-01 18:12)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.88 | 3.76 | 0.24 | 4.50 | 23.27 | 0.180 | 1142 |
| 175 | 0 | (b) | 1.28 | 3.74 | 0.34 | 5.50 | 23.09 | 0.256 | 1142 |
| 175 | 1 | (a) | 1.04 | 3.76 | 0.28 | 5.61 | 23.27 | 0.206 | 731 |
| 175 | 1 | (b) | 1.51 | 3.74 | 0.41 | 7.11 | 23.09 | 0.314 | 731 |
| 175 | 2 | (a) | 0.91 | 3.76 | 0.24 | 5.14 | 23.27 | 0.179 | 1319 |
| 175 | 2 | (b) | 1.39 | 3.74 | 0.37 | 6.30 | 23.09 | 0.268 | 1319 |

wall 3326 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
