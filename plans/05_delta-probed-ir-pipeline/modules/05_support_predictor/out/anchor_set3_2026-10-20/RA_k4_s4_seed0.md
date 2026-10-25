# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 17:14)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.32 | 0.47 | 0.90 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.06 | 42.40 | 12.09 | 6.53 | 9.94 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.23 | 0.89 | 0.47 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.91 | 28.95 | 6.61 | 1.96 | 3.34 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.45 | 76.46 | 9.12 | 3.16 | 1.55 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.45 | 43.01 | 19.89 | 12.41 | 17.90 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.69 | 26.25 | 13.09 | 6.90 | 11.84 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.0, CH-oop 11.9, ring-ip 2.0, other 6.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.14 | 0.92 | 0.90 | 0.62 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.15 | 44.91 | 23.93 | 21.24 | 21.70 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.77 | 0.97 | 0.68 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.32 | 28.99 | 3.90 | 3.11 | 2.52 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.83 | 77.94 | 8.14 | 1.62 | 1.65 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.37 | 31.04 | 10.28 | 6.99 | 10.14 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.98 | 45.07 | 42.13 | 38.03 | 38.52 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.651 | 0.135 | 0.448 | 0.705 | 0.499 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.405 | 0.570 | 0.333 | 0.524 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.405 | 0.570 | 0.333 | 0.524 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.6, CH-oop 7.2, ring-ip 3.0, other 39.7 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 2.20 | 0.99 | 0.77 | 0.80 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.59 | 40.59 | 9.12 | 4.66 | 7.22 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.60 | 0.34 | 0.43 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 28.33 | 6.83 | 2.65 | 5.33 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.60 | 77.60 | 7.62 | 4.16 | 3.02 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.43 | 21.56 | 13.69 | 7.94 | 11.64 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.16 | 22.14 | 8.26 | 3.01 | 7.23 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.637 | 0.184 | 0.658 | 0.779 | 0.759 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.326 | 0.328 | 0.134 | 0.304 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.328 | 0.197 | 0.339 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.2, CH-oop 8.3, ring-ip 2.4, other 2.9 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.79 | 0.63 | 0.39 | 0.62 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 42.93 | 8.05 | 5.92 | 7.94 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.69 | 0.39 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.25 | 26.68 | 6.81 | 2.95 | 6.19 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.80 | 80.99 | 4.62 | 5.29 | 4.11 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.45 | 27.02 | 12.63 | 9.76 | 13.27 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.95 | 21.41 | 7.15 | 6.33 | 6.88 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.326 | 0.601 | 0.327 | 0.415 | 0.392 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.012 | 0.005 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.2, CH-oop 11.9, ring-ip 2.9, other 11.2 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.07 | 1.48 | 0.65 | 1.11 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.40 | 41.92 | 13.14 | 8.06 | 10.62 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 2.20 | 1.03 | 0.50 | 0.82 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.57 | 30.42 | 10.46 | 3.67 | 6.06 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.30 | 76.74 | 8.81 | 2.80 | 2.04 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.54 | 46.64 | 21.97 | 15.73 | 20.31 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.44 | 24.41 | 11.99 | 8.01 | 10.44 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.9, CH-oop 17.8, ring-ip 3.7, other 7.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 2.16 | 1.10 | 0.88 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.75 | 39.22 | 7.98 | 4.28 | 5.60 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.61 | 0.29 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.15 | 27.91 | 4.80 | 3.68 | 3.18 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.63 | 76.57 | 9.68 | 2.01 | 1.11 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.49 | 27.41 | 10.25 | 7.09 | 8.55 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 21.61 | 8.93 | 3.79 | 7.48 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.174 | 0.719 | 0.720 | 0.724 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.116 | 0.202 | 0.213 | 0.149 | 0.180 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.281 | 0.202 | 0.327 | 0.548 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 7.4, ring-ip 3.6, other 3.8 |

873 s.
