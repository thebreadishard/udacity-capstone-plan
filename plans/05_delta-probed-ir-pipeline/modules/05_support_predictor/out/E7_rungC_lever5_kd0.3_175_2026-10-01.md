# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_lever5_kd0.3_175_2026-10-01 (2026-10-02 05:11)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 175 | 0 | (a) | 0.85 | 3.76 | 0.23 | 2.88 | 23.27 | 0.162 | 653 |
| 175 | 0 | (b) | 1.23 | 3.74 | 0.33 | 3.58 | 23.09 | 0.238 | 653 |
| 175 | 1 | (a) | 0.86 | 3.76 | 0.23 | 2.60 | 23.27 | 0.148 | 1089 |
| 175 | 1 | (b) | 1.37 | 3.74 | 0.37 | 3.60 | 23.09 | 0.254 | 1089 |
| 175 | 2 | (a) | 0.83 | 3.76 | 0.22 | 2.80 | 23.27 | 0.149 | 1522 |
| 175 | 2 | (b) | 1.22 | 3.74 | 0.33 | 3.60 | 23.09 | 0.234 | 1522 |

wall 3387 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
