# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever3b_fproj_kw0.3_175_2026-10-01 (2026-10-01 19:07)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.90 | 3.76 | 0.24 | 5.28 | 23.27 | 0.197 | 790 |
| 175 | 0 | (b) | 1.27 | 3.74 | 0.34 | 5.98 | 23.09 | 0.269 | 790 |
| 175 | 1 | (a) | 0.97 | 3.76 | 0.26 | 4.66 | 23.27 | 0.193 | 764 |
| 175 | 1 | (b) | 1.49 | 3.74 | 0.40 | 5.45 | 23.09 | 0.288 | 764 |
| 175 | 2 | (a) | 0.85 | 3.76 | 0.22 | 5.07 | 23.27 | 0.166 | 989 |
| 175 | 2 | (b) | 1.37 | 3.74 | 0.37 | 5.44 | 23.09 | 0.273 | 989 |

wall 2676 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
