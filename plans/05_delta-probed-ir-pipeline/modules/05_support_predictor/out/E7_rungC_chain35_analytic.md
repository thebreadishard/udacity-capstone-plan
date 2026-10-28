# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35_analytic (2026-10-27 23:59)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 0 | (a) | 0.67 | 3.73 | 0.18 | 2.36 | 23.37 | 0.126 | 3336 |
| 750 | 0 | (b) | 1.26 | 3.87 | 0.33 | 2.91 | 22.95 | 0.246 | 3336 |
| 750 | 1 | (a) | 0.61 | 3.73 | 0.16 | 2.10 | 23.37 | 0.107 | 5072 |
| 750 | 1 | (b) | 1.09 | 3.87 | 0.28 | 3.24 | 22.95 | 0.218 | 5072 |
| 750 | 2 | (a) | 0.63 | 3.73 | 0.17 | 2.16 | 23.37 | 0.117 | 5647 |
| 750 | 2 | (b) | 1.18 | 3.87 | 0.30 | 2.85 | 22.95 | 0.228 | 5647 |

wall 14379 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
