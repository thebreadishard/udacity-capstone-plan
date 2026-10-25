# Rung C (equivariant ΔH, C1 from scratch) — out/proxy_check_2026-10-21/base_b (2026-10-21 09:31)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 607 | 0 | (a) | 1.09 | 3.73 | 0.29 | 3.11 | 23.37 | 0.196 | 2576 |
| 607 | 0 | (b) | 1.49 | 3.90 | 0.38 | 3.51 | 23.01 | 0.286 | 2576 |
| 607 | 1 | (a) | 1.17 | 3.73 | 0.32 | 5.36 | 23.37 | 0.260 | 4167 |
| 607 | 1 | (b) | 1.37 | 3.90 | 0.35 | 3.45 | 23.01 | 0.270 | 4167 |
| 607 | 2 | (a) | 1.07 | 3.73 | 0.29 | 2.91 | 23.37 | 0.180 | 3979 |
| 607 | 2 | (b) | 1.42 | 3.90 | 0.36 | 3.68 | 23.01 | 0.277 | 3979 |

wall 10973 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
