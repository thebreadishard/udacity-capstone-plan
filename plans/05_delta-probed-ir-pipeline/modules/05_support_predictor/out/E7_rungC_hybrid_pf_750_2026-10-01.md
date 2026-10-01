# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_hybrid_pf_750_2026-10-01 (2026-10-01 02:41)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 1.55 | 3.76 | 0.41 | 4.45 | 23.27 | 0.257 | 949 |
| 750 | 0 | (b) | 1.64 | 3.74 | 0.44 | 4.50 | 23.09 | 0.306 | 949 |
| 750 | 1 | (a) | 1.59 | 3.76 | 0.42 | 4.36 | 23.27 | 0.270 | 723 |
| 750 | 1 | (b) | 1.76 | 3.74 | 0.47 | 4.71 | 23.09 | 0.322 | 723 |
| 750 | 2 | (a) | 1.56 | 3.76 | 0.42 | 4.65 | 23.27 | 0.255 | 1720 |
| 750 | 2 | (b) | 1.69 | 3.74 | 0.45 | 4.74 | 23.09 | 0.310 | 1720 |

wall 3488 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
