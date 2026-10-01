# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_hybrid_best_750_2026-10-01 (2026-10-01 05:02)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 1.64 | 3.76 | 0.44 | 4.15 | 23.27 | 0.254 | 1625 |
| 750 | 0 | (b) | 1.77 | 3.74 | 0.47 | 5.18 | 23.09 | 0.316 | 1625 |
| 750 | 1 | (a) | 1.60 | 3.76 | 0.42 | 4.41 | 23.27 | 0.263 | 1029 |
| 750 | 1 | (b) | 1.74 | 3.74 | 0.47 | 4.63 | 23.09 | 0.311 | 1029 |
| 750 | 2 | (a) | 1.62 | 3.76 | 0.43 | 4.32 | 23.27 | 0.257 | 1345 |
| 750 | 2 | (b) | 1.84 | 3.74 | 0.49 | 4.60 | 23.09 | 0.325 | 1345 |

wall 4096 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
