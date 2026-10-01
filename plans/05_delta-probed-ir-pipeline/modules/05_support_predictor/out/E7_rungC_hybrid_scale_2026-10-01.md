# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_hybrid_scale_2026-10-01 (2026-10-01 00:50)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.84 | 3.76 | 0.49 | 5.36 | 23.27 | 0.293 | 181 |
| 175 | 0 | (b) | 1.95 | 3.74 | 0.52 | 5.70 | 23.09 | 0.357 | 181 |
| 175 | 1 | (a) | 1.83 | 3.76 | 0.49 | 6.42 | 23.27 | 0.306 | 220 |
| 175 | 1 | (b) | 2.00 | 3.74 | 0.53 | 5.99 | 23.09 | 0.355 | 220 |
| 175 | 2 | (a) | 2.09 | 3.76 | 0.55 | 6.03 | 23.27 | 0.354 | 159 |
| 175 | 2 | (b) | 2.22 | 3.74 | 0.59 | 6.57 | 23.09 | 0.414 | 159 |
| 449 | 0 | (a) | 1.83 | 3.76 | 0.49 | 4.90 | 23.27 | 0.290 | 481 |
| 449 | 0 | (b) | 2.02 | 3.74 | 0.54 | 5.43 | 23.09 | 0.369 | 481 |
| 449 | 1 | (a) | 1.65 | 3.76 | 0.44 | 6.07 | 23.27 | 0.298 | 730 |
| 449 | 1 | (b) | 1.96 | 3.74 | 0.52 | 6.85 | 23.09 | 0.363 | 730 |
| 449 | 2 | (a) | 1.77 | 3.76 | 0.47 | 6.15 | 23.27 | 0.300 | 408 |
| 449 | 2 | (b) | 1.98 | 3.74 | 0.53 | 5.69 | 23.09 | 0.358 | 408 |
| 750 | 0 | (a) | 1.76 | 3.76 | 0.47 | 5.79 | 23.27 | 0.301 | 692 |
| 750 | 0 | (b) | 1.92 | 3.74 | 0.51 | 5.55 | 23.09 | 0.358 | 692 |
| 750 | 1 | (a) | 1.74 | 3.76 | 0.46 | 5.13 | 23.27 | 0.285 | 1120 |
| 750 | 1 | (b) | 1.86 | 3.74 | 0.50 | 5.13 | 23.09 | 0.337 | 1120 |
| 750 | 2 | (a) | 1.67 | 3.76 | 0.44 | 5.11 | 23.27 | 0.282 | 1040 |
| 750 | 2 | (b) | 1.81 | 3.74 | 0.49 | 5.20 | 23.09 | 0.334 | 1040 |

wall 5131 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
