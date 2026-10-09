# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain38_control_2026-10-09 (2026-10-09 10:28)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 853 | 0 | (a) | 0.72 | 3.73 | 0.19 | 2.46 | 23.37 | 0.124 | 2503 |
| 853 | 0 | (b) | 1.27 | 3.91 | 0.33 | 3.41 | 23.03 | 0.247 | 2503 |
| 853 | 1 | (a) | 0.68 | 3.73 | 0.18 | 2.35 | 23.37 | 0.126 | 2606 |
| 853 | 1 | (b) | 1.28 | 3.91 | 0.33 | 3.16 | 23.03 | 0.243 | 2606 |
| 853 | 2 | (a) | 0.68 | 3.73 | 0.18 | 2.62 | 23.37 | 0.129 | 4133 |
| 853 | 2 | (b) | 1.31 | 3.91 | 0.34 | 3.30 | 23.03 | 0.254 | 4133 |

wall 9495 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
