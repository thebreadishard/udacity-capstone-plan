# Target noise floor — finite-difference ΔH read as a prediction of the analytic ΔH (2026-10-01 07:53)

27 two-route molecules; K formula vs stored K: max relative deviation 4.46e-04.

| group | n | ring-coupling rms | zero rms | **ratio = noise share** | corrected ω rms | zero ω | ΔH residual ratio |
|---|---|---|---|---|---|---|---|
| clean | 7 | 7.65 | 3.92 | **1.95** | 10.90 | 25.45 | 0.411 |
| suspect | 20 | 1.98 | 3.81 | **0.52** | 10.88 | 23.16 | 0.287 |
| all | 27 | 3.14 | 3.82 | **0.82** | 10.89 | 23.58 | 0.332 |

Per molecule (ring-coupling ratio; 'imag' = an imaginary mode in the corpus deck, excluded from the training pool):

| id | name | atoms | imag | ratio | ΔH residual ratio |
|---|---|---|---|---|---|
| A2_0420908ebe |  | 26 | yes | 0.14 | 0.073 |
| A2_13bafae8e0 |  | 23 | no | 0.09 | 0.062 |
| A2_13eea56ee5 |  | 27 | yes | 0.13 | 0.042 |
| A2_197913eb9c |  | 26 | yes | 0.15 | 0.070 |
| A2_1c29b66c9d |  | 26 | yes | 0.11 | 0.039 |
| A2_20747fd501 |  | 30 | yes | 0.07 | 0.036 |
| A2_20e59f3897 |  | 26 | yes | 0.11 | 0.073 |
| A2_220d2c107b |  | 26 | yes | 0.13 | 0.070 |
| A2_22d0e8105c |  | 23 | no | 0.11 | 0.056 |
| A2_28eed45ad3 |  | 26 | yes | 0.16 | 0.077 |
| A2_2a0b78bd2b |  | 25 | yes | 0.14 | 0.107 |
| A2_2b693cf6e7 |  | 29 | yes | 0.12 | 0.076 |
| A2_2c22216564 |  | 25 | yes | 0.12 | 0.037 |
| A2_3020175511 |  | 18 | yes | 0.07 | 0.026 |
| A2_330b4d6d8d |  | 26 | yes | 0.08 | 0.039 |
| A2_356c370f21 |  | 25 | yes | 0.13 | 0.077 |
| A2_3802542cb6 |  | 24 | yes | 0.09 | 0.051 |
| A2_3a2982dd85 |  | 23 | yes | 0.12 | 0.025 |
| A2_3c2cf09504 |  | 24 | yes | 0.10 | 0.046 |
| A_014f8519af |  | 24 | yes | 3.00 | 1.196 |
| A_01f3186607 |  | 18 | no | 0.07 | 0.024 |
| A_3100da3761 |  | 13 | no | 0.07 | 0.033 |
| A_6e858b26e5 |  | 11 | no | 0.50 | 0.157 |
| A_78896cfe24 |  | 27 | yes | 0.11 | 0.051 |
| A_8448043181 |  | 12 | no | 7.98 | 1.059 |
| A_b90527ca2d |  | 21 | yes | 0.13 | 0.022 |
| B_8b12a55d3a |  | 12 | no | 0.10 | 0.021 |

Read-out keys of the group tables: ['block_median_rule_rms', 'block_rms', 'corrected_freq_rms', 'corrected_freq_rms_zero_rule', 'coupling_ratio', 'coupling_rms', 'coupling_zero_rms', 'dH_residual_ratio', 'duschinsky_overlap_median', 'duschinsky_overlap_p10']

25 s.
