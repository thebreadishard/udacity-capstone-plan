# Rung C (equivariant ΔH, C1 from scratch) — out/E7_rungC_chain42_arm0 (2026-11-10 18:01)

recipe: lr 0.0003, epochs 200, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 978 | 0 | (a) | 0.69 | 3.73 | 0.19 | 2.28 | 23.37 | 0.123 | 4944 |
| 978 | 0 | (b) | 1.23 | 3.87 | 0.32 | 3.10 | 22.93 | 0.240 | 4944 |
| 978 | 1 | (a) | 0.60 | 3.73 | 0.16 | 1.98 | 23.37 | 0.110 | 4938 |
| 978 | 1 | (b) | 1.15 | 3.87 | 0.30 | 2.75 | 22.93 | 0.221 | 4938 |
| 978 | 2 | (a) | 0.65 | 3.73 | 0.18 | 2.89 | 23.37 | 0.177 | 5622 |
| 978 | 2 | (b) | 1.14 | 3.87 | 0.30 | 2.72 | 22.93 | 0.219 | 5622 |

wall 15897 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
