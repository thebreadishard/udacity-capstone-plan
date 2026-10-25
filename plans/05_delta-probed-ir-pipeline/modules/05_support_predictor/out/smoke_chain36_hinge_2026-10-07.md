# Rung C (equivariant ΔH, C1 from scratch) — out/smoke_chain36_hinge_2026-10-07 (2026-10-07 07:23) — SMOKE, not a result

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.0, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | (a) | 1.92 | 3.04 | 0.63 | 8.08 | 23.80 | 0.326 | 75 |
| 5 | 0 | (b) | 2.53 | 3.99 | 0.63 | 6.24 | 23.08 | 0.473 | 75 |

wall 114 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
