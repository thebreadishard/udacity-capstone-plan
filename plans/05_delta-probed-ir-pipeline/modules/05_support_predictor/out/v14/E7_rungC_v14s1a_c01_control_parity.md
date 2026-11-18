# Rung C (equivariant ΔH, C1 from scratch) — out/v14/E7_rungC_v14s1a_c01_control_parity (2026-11-16 00:13)

recipe: lr 0.0003, epochs 300, loss registered, aux weight 1.0, internal term both, output scale rms, inner validation 0.15, patience 20; pool layers A,A2,B,P3,P3c; sum aggregation; hybrid head + SQM α; pattern f

| n | seed | hold-out | ring couplings | zero | ratio | corrected ω | zero ω | ΔH residual ratio | s |
|---|---|---|---|---|---|---|---|---|---|
| 913 | 0 | (a) | 0.82 | 3.73 | 0.22 | 3.10 | 23.37 | 0.167 | 5335 |
| 913 | 0 | (b) | 0.91 | 3.87 | 0.24 | 2.65 | 22.93 | 0.191 | 5335 |
| 913 | 0 | (sel) | 1.73 | 4.09 | 0.42 | 3.77 | 22.92 | 0.291 | 5335 |

wall 5804 s; read-out keys: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'diag_rms', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']
