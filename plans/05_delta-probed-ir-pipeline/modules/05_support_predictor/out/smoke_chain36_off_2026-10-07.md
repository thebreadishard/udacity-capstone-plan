# Rung C (equivariant ΔH, C1 from scratch) — out/smoke_chain36_off_2026-10-07 (2026-10-07 07:25) — SMOKE, not a result

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.0, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | (a) | 1.96 | 3.04 | 0.64 | 8.31 | 23.80 | 0.313 | 74 |
| 5 | 0 | (b) | 2.41 | 3.99 | 0.61 | 6.11 | 23.08 | 0.457 | 74 |

wall 113 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
