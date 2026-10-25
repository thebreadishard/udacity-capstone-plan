# Rung C (equivariant ΔH, C1 from scratch) — out/smoke_kdiag_family_2026-10-03 (2026-10-03 11:20)

recipe: lr 0.0003, epochs 2, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 30 | 0 | (a) | 2.42 | 3.76 | 0.64 | 6.44 | 23.27 | 0.385 | 12 |
| 30 | 0 | (b) | 2.54 | 3.74 | 0.68 | 6.45 | 23.09 | 0.459 | 12 |

wall 106 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
