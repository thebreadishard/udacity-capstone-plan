# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain38_ablation_fivering_2026-10-09 (2026-10-09 07:25)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 853 | 0 | (a) | 0.93 | 3.73 | 0.25 | 2.45 | 23.37 | 0.151 | 4550 |
| 853 | 0 | (b) | 1.79 | 3.91 | 0.46 | 4.00 | 23.03 | 0.335 | 4550 |
| 853 | 1 | (a) | 0.85 | 3.73 | 0.23 | 2.66 | 23.37 | 0.140 | 3764 |
| 853 | 1 | (b) | 1.59 | 3.91 | 0.41 | 3.75 | 23.03 | 0.294 | 3764 |
| 853 | 2 | (a) | 0.80 | 3.73 | 0.21 | 2.44 | 23.37 | 0.146 | 2394 |
| 853 | 2 | (b) | 1.66 | 3.91 | 0.42 | 3.73 | 23.03 | 0.313 | 2394 |

wall 10961 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
