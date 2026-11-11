# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain42_armD (2026-11-10 22:27)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,D; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 983 | 0 | (a) | 0.57 | 3.73 | 0.15 | 1.96 | 23.37 | 0.109 | 5750 |
| 983 | 0 | (b) | 1.05 | 3.87 | 0.27 | 2.66 | 22.93 | 0.208 | 5750 |
| 983 | 1 | (a) | 0.57 | 3.73 | 0.15 | 1.94 | 23.37 | 0.107 | 5366 |
| 983 | 1 | (b) | 1.03 | 3.87 | 0.27 | 2.62 | 22.93 | 0.205 | 5366 |
| 983 | 2 | (a) | 0.62 | 3.73 | 0.17 | 2.11 | 23.37 | 0.109 | 6804 |
| 983 | 2 | (b) | 1.17 | 3.87 | 0.30 | 2.98 | 22.93 | 0.233 | 6804 |

wall 18377 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
