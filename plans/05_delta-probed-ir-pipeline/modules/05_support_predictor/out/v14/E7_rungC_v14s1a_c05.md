# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c05 (2026-11-16 10:39)

recipe: lr 0.000105, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α; pattern f; ls pattern target (λ_rel 0.001)

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 1.01 | 3.73 | 0.27 | 3.46 | 23.37 | 0.186 | 15701 |
| 913 | 0 | (b) | 0.95 | 3.87 | 0.25 | 2.69 | 22.93 | 0.202 | 15701 |
| 913 | 0 | (sel) | 1.86 | 4.09 | 0.46 | 3.80 | 22.92 | 0.316 | 15701 |

wall 16147 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
