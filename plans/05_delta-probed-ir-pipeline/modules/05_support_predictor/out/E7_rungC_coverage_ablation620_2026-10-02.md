# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_ablation620_2026-10-02 (2026-10-02 17:26)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 620 | 0 | (a) | 1.45 | 3.76 | 0.39 | 4.72 | 23.27 | 0.252 | 6337 |
| 620 | 0 | (b) | 1.73 | 3.74 | 0.46 | 4.32 | 23.09 | 0.334 | 6337 |
| 620 | 1 | (a) | 1.33 | 3.76 | 0.35 | 4.42 | 23.27 | 0.239 | 4917 |
| 620 | 1 | (b) | 1.39 | 3.74 | 0.37 | 4.16 | 23.09 | 0.273 | 4917 |
| 620 | 2 | (a) | 1.43 | 3.76 | 0.38 | 5.19 | 23.27 | 0.270 | 4271 |
| 620 | 2 | (b) | 1.48 | 3.74 | 0.40 | 4.81 | 23.09 | 0.301 | 4271 |

wall 15784 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
