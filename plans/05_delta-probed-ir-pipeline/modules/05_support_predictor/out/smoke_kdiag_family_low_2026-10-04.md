# Rung C (equivariant ΔH, C1 from scratch) — out/smoke_kdiag_family_low_2026-10-04 (2026-10-04 08:33) — SMOKE, not a result

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.0, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 5 | 0 | (a) | 2.55 | 3.09 | 0.82 | 13.85 | 24.00 | 0.367 | 119 |
| 5 | 0 | (b) | 2.81 | 3.99 | 0.71 | 8.71 | 23.08 | 0.534 | 119 |

wall 176 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
