# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_carried_kd_750_saved_2026-10-02 (2026-10-02 10:59)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.89 | 3.76 | 0.24 | 2.96 | 23.27 | 0.153 | 2801 |
| 750 | 0 | (b) | 1.29 | 3.74 | 0.35 | 3.47 | 23.09 | 0.241 | 2801 |
| 750 | 1 | (a) | 0.82 | 3.76 | 0.22 | 2.78 | 23.27 | 0.135 | 3212 |
| 750 | 1 | (b) | 1.30 | 3.74 | 0.35 | 3.61 | 23.09 | 0.243 | 3212 |
| 750 | 2 | (a) | 0.78 | 3.76 | 0.21 | 2.45 | 23.27 | 0.126 | 5300 |
| 750 | 2 | (b) | 1.21 | 3.74 | 0.32 | 3.60 | 23.09 | 0.233 | 5300 |

wall 11624 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
