# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_coverage_control620_2026-10-02 (2026-10-02 17:26)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 620 | 0 | (a) | 0.84 | 3.76 | 0.22 | 3.00 | 23.27 | 0.140 | 3597 |
| 620 | 0 | (b) | 1.21 | 3.74 | 0.32 | 3.81 | 23.09 | 0.234 | 3597 |
| 620 | 1 | (a) | 0.86 | 3.76 | 0.23 | 3.25 | 23.27 | 0.149 | 5179 |
| 620 | 1 | (b) | 1.35 | 3.74 | 0.36 | 3.84 | 23.09 | 0.262 | 5179 |
| 620 | 2 | (a) | 0.89 | 3.76 | 0.24 | 3.05 | 23.27 | 0.150 | 6066 |
| 620 | 2 | (b) | 1.35 | 3.74 | 0.36 | 4.17 | 23.09 | 0.265 | 6066 |

wall 15125 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
