# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c09 (2026-11-18 14:43)

recipe: lr 0.000394 (cosine schedule), epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 300; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f; ls pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.63 | 3.73 | 0.17 | 2.40 | 23.37 | 0.134 | 14583 |
| 913 | 0 | (b) | 0.80 | 3.87 | 0.21 | 2.24 | 22.93 | 0.173 | 14583 |
| 913 | 0 | (sel) | 1.68 | 4.09 | 0.41 | 3.11 | 22.92 | 0.276 | 14583 |

wall 15008 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
