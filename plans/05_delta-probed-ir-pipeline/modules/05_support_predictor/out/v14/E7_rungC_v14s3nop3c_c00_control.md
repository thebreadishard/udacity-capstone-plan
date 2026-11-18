# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s3nop3c_c00_control (2026-11-17 09:07)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3; sum aggregation; hybrid head + SQM α + rung B pair features; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 1032 | 0 | (a) | 0.45 | 3.73 | 0.12 | 1.55 | 23.37 | 0.088 | 8227 |
| 1032 | 0 | (b) | 0.72 | 3.87 | 0.19 | 2.05 | 22.93 | 0.155 | 8227 |

wall 8638 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
