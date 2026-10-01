# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_carried_449_2026-10-01 (2026-10-02 00:09)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 449 | 0 | (a) | 0.81 | 3.76 | 0.21 | 4.94 | 23.27 | 0.172 | 1403 |
| 449 | 0 | (b) | 1.19 | 3.74 | 0.32 | 5.74 | 23.09 | 0.254 | 1403 |
| 449 | 1 | (a) | 0.90 | 3.76 | 0.24 | 4.97 | 23.27 | 0.192 | 2112 |
| 449 | 1 | (b) | 1.35 | 3.74 | 0.36 | 5.55 | 23.09 | 0.279 | 2112 |
| 449 | 2 | (a) | 0.95 | 3.76 | 0.25 | 3.84 | 23.27 | 0.172 | 1906 |
| 449 | 2 | (b) | 1.35 | 3.74 | 0.36 | 4.23 | 23.09 | 0.264 | 1906 |

wall 5609 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
