# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_carried_kd_750_2026-10-01 (2026-10-02 06:11)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.85 | 3.76 | 0.23 | 2.88 | 23.27 | 0.149 | 4434 |
| 750 | 0 | (b) | 1.29 | 3.74 | 0.35 | 3.56 | 23.09 | 0.247 | 4434 |
| 750 | 1 | (a) | 0.81 | 3.76 | 0.21 | 2.98 | 23.27 | 0.133 | 6000 |
| 750 | 1 | (b) | 1.27 | 3.74 | 0.34 | 3.72 | 23.09 | 0.243 | 6000 |
| 750 | 2 | (a) | 0.82 | 3.76 | 0.22 | 2.59 | 23.27 | 0.136 | 4232 |
| 750 | 2 | (b) | 1.18 | 3.74 | 0.32 | 3.55 | 23.09 | 0.232 | 4232 |

wall 14956 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
