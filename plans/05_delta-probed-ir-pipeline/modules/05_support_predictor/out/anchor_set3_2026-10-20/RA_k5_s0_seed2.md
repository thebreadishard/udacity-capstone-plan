# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 22:48)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.35 | 1.24 | 0.52 | 0.72 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 42.29 | 11.36 | 5.90 | 9.25 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.21 | 0.85 | 0.39 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 28.43 | 6.37 | 1.44 | 3.24 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 77.02 | 7.68 | 6.04 | 1.31 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 43.03 | 19.12 | 10.33 | 17.40 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 25.37 | 12.15 | 5.90 | 10.28 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.8, CH-oop 10.0, ring-ip 1.5, other 5.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.17 | 0.98 | 0.68 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 45.03 | 24.13 | 22.67 | 22.24 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.80 | 0.89 | 0.74 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 28.39 | 3.82 | 2.96 | 2.60 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 78.77 | 6.47 | 1.81 | 3.62 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 30.53 | 9.41 | 8.06 | 8.85 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 45.41 | 42.77 | 40.56 | 39.63 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.148 | 0.538 | 0.542 | 0.573 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.368 | 0.544 | 0.470 | 0.497 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.368 | 0.544 | 0.470 | 0.497 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.9, CH-oop 8.7, ring-ip 2.9, other 43.5 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.27 | 0.97 | 0.61 | 0.75 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 41.06 | 8.94 | 4.88 | 7.27 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.60 | 0.29 | 0.41 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 27.44 | 7.04 | 2.37 | 4.95 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 79.15 | 5.10 | 5.32 | 1.72 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 22.78 | 13.72 | 8.02 | 12.27 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 22.59 | 8.70 | 3.53 | 7.35 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.207 | 0.669 | 0.782 | 0.738 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.344 | 0.343 | 0.117 | 0.319 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.343 | 0.117 | 0.319 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.3, CH-oop 8.1, ring-ip 2.4, other 3.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.80 | 0.56 | 0.20 | 0.52 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 43.42 | 7.31 | 7.99 | 8.13 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.71 | 0.44 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 25.95 | 6.67 | 3.36 | 6.35 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 82.30 | 2.59 | 10.30 | 7.59 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 28.29 | 10.72 | 11.18 | 12.43 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 21.75 | 7.71 | 8.72 | 6.09 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.556 | 0.352 | 0.430 | 0.317 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.001 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.2, CH-oop 13.9, ring-ip 3.3, other 11.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.04 | 1.41 | 0.75 | 0.93 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.91 | 12.56 | 8.92 | 10.07 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.19 | 1.01 | 0.59 | 0.73 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 30.05 | 9.98 | 3.74 | 5.72 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 76.88 | 7.71 | 4.67 | 1.67 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 46.46 | 20.43 | 16.92 | 19.03 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 24.82 | 12.15 | 9.13 | 10.12 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.6, CH-oop 17.2, ring-ip 3.7, other 9.0 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.19 | 1.16 | 0.55 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 39.49 | 7.85 | 3.34 | 5.59 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.21 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 27.32 | 4.65 | 1.58 | 2.81 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 77.83 | 7.55 | 1.70 | 2.29 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 27.62 | 11.92 | 7.04 | 9.51 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 21.61 | 8.61 | 2.28 | 6.75 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.186 | 0.721 | 0.863 | 0.744 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.199 | 0.210 | 0.043 | 0.157 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.199 | 0.326 | 0.280 | 0.299 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 7.3, ring-ip 1.8, other 2.3 |

960 s.
