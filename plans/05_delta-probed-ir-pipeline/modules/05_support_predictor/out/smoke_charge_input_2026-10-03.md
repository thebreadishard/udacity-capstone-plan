# Rung C (equivariant ΔH, C1 from scratch) — out/smoke_charge_input_2026-10-03 (2026-10-03 12:10)

recipe: lr 0.0003, epochs 2, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 30 | 0 | (a) | 2.48 | 3.76 | 0.66 | 6.31 | 23.27 | 0.395 | 6 |
| 30 | 0 | (b) | 2.66 | 3.74 | 0.71 | 6.71 | 23.09 | 0.477 | 6 |

wall 56 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
