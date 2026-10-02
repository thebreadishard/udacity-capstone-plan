# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever4_w0.3_175_2026-10-01 (2026-10-02 05:14)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 0.3, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern d; LS pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.42 | 3.76 | 0.38 | 3.83 | 23.27 | 0.217 | 1211 |
| 175 | 0 | (b) | 1.64 | 3.74 | 0.44 | 4.60 | 23.09 | 0.293 | 1211 |
| 175 | 1 | (a) | 1.41 | 3.76 | 0.38 | 4.08 | 23.27 | 0.218 | 1273 |
| 175 | 1 | (b) | 1.67 | 3.74 | 0.45 | 4.74 | 23.09 | 0.296 | 1273 |
| 175 | 2 | (a) | 1.52 | 3.76 | 0.40 | 4.49 | 23.27 | 0.231 | 1610 |
| 175 | 2 | (b) | 1.77 | 3.74 | 0.47 | 5.34 | 23.09 | 0.319 | 1610 |

wall 4202 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
