# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever1_overfit_benzene_2026-10-01 (2026-10-01 07:12)

recipe: lr 0.0003, epochs 5000, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.0, patience 0; pool layers A,A2; sum aggregation; overfit-one A_8448043181 (diagnostic 2); hybrid head + SQM α + rung B pair features; pattern d

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0 | (a) | 0.05 | 3.30 | 0.02 | 0.21 | 25.01 | 0.007 | 79 |
| 1 | 0 | (b) | 0.05 | 3.30 | 0.02 | 0.21 | 25.01 | 0.007 | 79 |

wall 103 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
