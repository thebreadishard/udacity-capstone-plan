# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain40_fivering15 (2026-10-16 18:33)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 943 | 0 | (a) | 0.71 | 3.73 | 0.19 | 2.10 | 23.37 | 0.117 | 7648 |
| 943 | 0 | (b) | 1.34 | 3.91 | 0.34 | 3.61 | 23.03 | 0.255 | 7648 |
| 943 | 1 | (a) | 0.60 | 3.73 | 0.16 | 2.07 | 23.37 | 0.108 | 5863 |
| 943 | 1 | (b) | 1.21 | 3.91 | 0.31 | 3.30 | 23.03 | 0.234 | 5863 |
| 943 | 2 | (a) | 0.81 | 3.73 | 0.22 | 2.51 | 23.37 | 0.133 | 5940 |
| 943 | 2 | (b) | 1.50 | 3.91 | 0.38 | 3.70 | 23.03 | 0.287 | 5940 |

wall 19940 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
