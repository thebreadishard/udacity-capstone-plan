# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_hybrid_zerohlow_2026-10-01 (2026-10-01 02:15)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term pattern, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; H_low input zeroed (diagnostic 1); hybrid head + SQM α

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.63 | 3.76 | 0.43 | 4.65 | 23.27 | 0.273 | 290 |
| 175 | 0 | (b) | 1.79 | 3.74 | 0.48 | 4.74 | 23.09 | 0.321 | 290 |

wall 339 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
