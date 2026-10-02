# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_carried_mixed175_2026-10-01 (2026-10-02 02:38)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 1.06 | 3.76 | 0.28 | 7.02 | 23.27 | 0.228 | 317 |
| 175 | 0 | (b) | 1.36 | 3.74 | 0.36 | 7.82 | 23.09 | 0.303 | 317 |
| 175 | 1 | (a) | 0.97 | 3.76 | 0.26 | 4.75 | 23.27 | 0.185 | 714 |
| 175 | 1 | (b) | 1.38 | 3.74 | 0.37 | 5.96 | 23.09 | 0.282 | 714 |
| 175 | 2 | (a) | 1.07 | 3.76 | 0.28 | 5.47 | 23.27 | 0.211 | 520 |
| 175 | 2 | (b) | 1.37 | 3.74 | 0.37 | 6.32 | 23.09 | 0.285 | 520 |

wall 1655 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
