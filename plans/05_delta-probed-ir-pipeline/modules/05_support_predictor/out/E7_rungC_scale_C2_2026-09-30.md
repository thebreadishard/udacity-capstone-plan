# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_scale_C2_2026-09-30 (2026-09-30 22:45)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term all, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 449 | 0 | (a) | 3.13 | 3.76 | 0.83 | 9.28 | 23.27 | 0.619 | 386 |
| 449 | 0 | (b) | 3.23 | 3.74 | 0.86 | 8.87 | 23.09 | 0.632 | 386 |
| 449 | 1 | (a) | 3.05 | 3.76 | 0.81 | 9.11 | 23.27 | 0.608 | 546 |
| 449 | 1 | (b) | 3.17 | 3.74 | 0.85 | 8.30 | 23.09 | 0.609 | 546 |
| 449 | 2 | (a) | 3.02 | 3.76 | 0.80 | 9.03 | 23.27 | 0.603 | 514 |
| 449 | 2 | (b) | 3.13 | 3.74 | 0.84 | 8.31 | 23.09 | 0.599 | 514 |
| 750 | 0 | (a) | 3.11 | 3.76 | 0.83 | 9.08 | 23.27 | 0.608 | 690 |
| 750 | 0 | (b) | 3.16 | 3.74 | 0.84 | 8.37 | 23.09 | 0.606 | 690 |
| 750 | 1 | (a) | 3.03 | 3.76 | 0.81 | 9.14 | 23.27 | 0.597 | 685 |
| 750 | 1 | (b) | 3.07 | 3.74 | 0.82 | 8.31 | 23.09 | 0.588 | 685 |
| 750 | 2 | (a) | 2.98 | 3.76 | 0.79 | 8.99 | 23.27 | 0.590 | 787 |
| 750 | 2 | (b) | 3.10 | 3.74 | 0.83 | 8.27 | 23.09 | 0.591 | 787 |

wall 3642 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
