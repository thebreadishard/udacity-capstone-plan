# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c06 (2026-11-16 15:09)

recipe: lr 0.00093, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α; pattern f; ls pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.83 | 3.73 | 0.22 | 2.87 | 23.37 | 0.172 | 7892 |
| 913 | 0 | (b) | 0.86 | 3.87 | 0.22 | 2.37 | 22.93 | 0.185 | 7892 |
| 913 | 0 | (sel) | 1.74 | 4.09 | 0.43 | 3.50 | 22.92 | 0.290 | 7892 |

wall 8423 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
