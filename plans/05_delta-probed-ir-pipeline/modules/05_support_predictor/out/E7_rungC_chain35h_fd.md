# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35h_fd (2026-10-17 04:18)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 4.58 | 5.90 | 0.78 | 8.31 | 24.31 | 0.364 | 2513 |
| 750 | 0 | (b) | 1.33 | 3.91 | 0.34 | 3.34 | 23.03 | 0.259 | 2513 |
| 750 | 1 | (a) | 4.57 | 5.90 | 0.78 | 8.05 | 24.31 | 0.371 | 2919 |
| 750 | 1 | (b) | 1.32 | 3.91 | 0.34 | 3.31 | 23.03 | 0.251 | 2919 |
| 750 | 2 | (a) | 4.58 | 5.90 | 0.78 | 8.20 | 24.31 | 0.370 | 3876 |
| 750 | 2 | (b) | 1.43 | 3.91 | 0.37 | 3.36 | 23.03 | 0.266 | 3876 |

wall 9723 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
