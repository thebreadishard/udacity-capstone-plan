# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c02_control_target (2026-11-16 02:32)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f; ls pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.78 | 3.73 | 0.21 | 3.87 | 23.37 | 0.177 | 7758 |
| 913 | 0 | (b) | 0.85 | 3.87 | 0.22 | 2.45 | 22.93 | 0.185 | 7758 |
| 913 | 0 | (sel) | 1.69 | 4.09 | 0.41 | 3.90 | 22.92 | 0.288 | 7758 |

wall 10752 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
