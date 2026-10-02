# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_carried_wide_175_2026-10-01 (2026-10-02 01:42)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.86 | 3.76 | 0.23 | 4.19 | 23.27 | 0.158 | 1051 |
| 175 | 0 | (b) | 1.36 | 3.74 | 0.36 | 4.78 | 23.09 | 0.252 | 1051 |
| 175 | 1 | (a) | 0.80 | 3.76 | 0.21 | 6.06 | 23.27 | 0.196 | 811 |
| 175 | 1 | (b) | 1.27 | 3.74 | 0.34 | 6.85 | 23.09 | 0.277 | 811 |
| 175 | 2 | (a) | 0.85 | 3.76 | 0.23 | 4.51 | 23.27 | 0.173 | 1332 |
| 175 | 2 | (b) | 1.26 | 3.74 | 0.34 | 5.03 | 23.09 | 0.252 | 1332 |

wall 3315 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
