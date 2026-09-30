# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_scale_C1_2026-09-30 (2026-09-30 21:42)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 449 | 0 | (a) | 3.15 | 3.76 | 0.84 | 9.42 | 23.27 | 0.616 | 539 |
| 449 | 0 | (b) | 3.24 | 3.74 | 0.87 | 8.64 | 23.09 | 0.621 | 539 |
| 449 | 1 | (a) | 3.12 | 3.76 | 0.83 | 9.81 | 23.27 | 0.608 | 509 |
| 449 | 1 | (b) | 3.13 | 3.74 | 0.84 | 8.77 | 23.09 | 0.601 | 509 |
| 449 | 2 | (a) | 3.13 | 3.76 | 0.83 | 9.65 | 23.27 | 0.612 | 507 |
| 449 | 2 | (b) | 3.19 | 3.74 | 0.85 | 8.66 | 23.09 | 0.599 | 507 |
| 750 | 0 | (a) | 3.12 | 3.76 | 0.83 | 9.02 | 23.27 | 0.608 | 654 |
| 750 | 0 | (b) | 3.13 | 3.74 | 0.84 | 8.20 | 23.09 | 0.601 | 654 |
| 750 | 1 | (a) | 3.10 | 3.76 | 0.83 | 9.64 | 23.27 | 0.601 | 583 |
| 750 | 1 | (b) | 3.15 | 3.74 | 0.84 | 8.81 | 23.09 | 0.592 | 583 |
| 750 | 2 | (a) | 3.06 | 3.76 | 0.81 | 9.22 | 23.27 | 0.596 | 1005 |
| 750 | 2 | (b) | 3.12 | 3.74 | 0.83 | 8.53 | 23.09 | 0.597 | 1005 |

wall 3824 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
