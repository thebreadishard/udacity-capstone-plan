# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever3b_fproj_kw0.3_750_2026-10-01 (2026-10-01 19:57)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.80 | 3.76 | 0.21 | 3.74 | 23.27 | 0.139 | 3132 |
| 750 | 0 | (b) | 1.19 | 3.74 | 0.32 | 4.36 | 23.09 | 0.240 | 3132 |
| 750 | 1 | (a) | 0.81 | 3.76 | 0.22 | 2.94 | 23.27 | 0.125 | 2946 |
| 750 | 1 | (b) | 1.25 | 3.74 | 0.33 | 4.47 | 23.09 | 0.239 | 2946 |
| 750 | 2 | (a) | 0.83 | 3.76 | 0.22 | 3.80 | 23.27 | 0.148 | 3340 |
| 750 | 2 | (b) | 1.29 | 3.74 | 0.35 | 4.40 | 23.09 | 0.256 | 3340 |

wall 9690 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
