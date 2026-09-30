# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_diag_zerohlow_2026-09-30 (2026-09-30 23:47)

recipe: lr 0.001, epochs 200, loss registered, aux weight 1.0, internal term all, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; H_low input zeroed (diagnostic 1)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 3.06 | 3.76 | 0.82 | 9.01 | 23.27 | 0.609 | 279 |
| 175 | 0 | (b) | 3.18 | 3.74 | 0.85 | 8.37 | 23.09 | 0.605 | 279 |

wall 301 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
