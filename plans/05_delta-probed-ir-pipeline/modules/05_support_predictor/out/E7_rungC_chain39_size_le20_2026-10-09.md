# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain39_size_le20_2026-10-09 (2026-10-09 05:48)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 370 | 0 | (a) | 1.41 | 3.73 | 0.38 | 4.04 | 23.37 | 0.242 | 722 |
| 370 | 0 | (b) | 1.70 | 3.91 | 0.44 | 3.95 | 23.03 | 0.314 | 722 |
| 370 | 0 | (s) | 2.82 | 3.94 | 0.72 | 5.18 | 23.17 | 0.492 | 722 |
| 370 | 1 | (a) | 1.39 | 3.73 | 0.37 | 4.10 | 23.37 | 0.234 | 838 |
| 370 | 1 | (b) | 1.69 | 3.91 | 0.43 | 4.08 | 23.03 | 0.312 | 838 |
| 370 | 1 | (s) | 2.59 | 3.94 | 0.66 | 5.30 | 23.17 | 0.449 | 838 |
| 370 | 2 | (a) | 1.43 | 3.73 | 0.38 | 4.76 | 23.37 | 0.242 | 773 |
| 370 | 2 | (b) | 1.71 | 3.91 | 0.44 | 5.86 | 23.03 | 0.338 | 773 |
| 370 | 2 | (s) | 2.74 | 3.94 | 0.70 | 6.30 | 23.17 | 0.490 | 773 |

wall 2447 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
