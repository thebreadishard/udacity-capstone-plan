# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain35s2_analytic (2026-11-03 16:38)

recipe: lr 0.0003, epochs 500, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 750 | 2 | (a) | 0.66 | 3.73 | 0.18 | 2.03 | 23.37 | 0.119 | 3592 |
| 750 | 2 | (b) | 1.24 | 3.87 | 0.32 | 2.77 | 22.95 | 0.239 | 3592 |

wall 3886 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
