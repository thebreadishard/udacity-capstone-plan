# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 22:21)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.35 | 1.24 | 0.52 | 0.72 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.81 | 42.29 | 11.35 | 5.69 | 9.29 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.21 | 0.86 | 0.39 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.80 | 28.43 | 6.41 | 1.52 | 3.24 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.54 | 77.02 | 6.86 | 5.42 | 1.23 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.26 | 43.03 | 19.28 | 9.81 | 17.48 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 25.37 | 12.22 | 6.01 | 10.33 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.2, CH-oop 9.5, ring-ip 1.6, other 5.8 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.17 | 0.98 | 0.61 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.03 | 22.31 | 19.86 | 20.40 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.76 | 0.83 | 0.71 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.24 | 28.39 | 3.75 | 2.64 | 2.48 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.18 | 78.77 | 5.62 | 1.37 | 3.42 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.71 | 30.53 | 9.33 | 7.47 | 8.74 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.41 | 39.48 | 35.47 | 36.25 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.148 | 0.619 | 0.691 | 0.654 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.368 | 0.499 | 0.366 | 0.453 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.298 | 0.368 | 0.499 | 0.367 | 0.453 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.4, CH-oop 8.1, ring-ip 2.6, other 37.1 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.16 | 2.27 | 0.97 | 0.63 | 0.77 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 41.06 | 9.01 | 5.76 | 7.41 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.62 | 0.31 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 27.44 | 7.33 | 2.32 | 5.12 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.78 | 79.15 | 4.24 | 8.61 | 1.90 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.08 | 22.78 | 13.90 | 8.28 | 12.54 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.59 | 8.64 | 3.55 | 7.19 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.646 | 0.207 | 0.683 | 0.723 | 0.733 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.344 | 0.343 | 0.142 | 0.320 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.343 | 0.142 | 0.326 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 8.7, CH-oop 8.4, ring-ip 2.3, other 3.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.80 | 0.58 | 0.20 | 0.54 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.97 | 43.42 | 7.29 | 8.53 | 8.10 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.72 | 0.45 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.21 | 25.95 | 6.78 | 3.09 | 6.38 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.08 | 82.30 | 1.81 | 12.30 | 7.59 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.97 | 28.29 | 10.61 | 11.17 | 12.30 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.75 | 7.79 | 8.97 | 6.08 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.340 | 0.556 | 0.367 | 0.418 | 0.317 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.002 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 12.2, CH-oop 14.1, ring-ip 3.0, other 11.3 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.04 | 1.40 | 0.72 | 0.92 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.05 | 41.91 | 12.54 | 8.66 | 10.07 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.19 | 1.00 | 0.58 | 0.73 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 30.05 | 9.94 | 3.41 | 5.63 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.35 | 76.88 | 6.83 | 4.97 | 1.44 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.07 | 46.46 | 20.62 | 15.98 | 19.08 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.24 | 24.82 | 12.23 | 9.21 | 10.17 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.4, CH-oop 16.5, ring-ip 3.4, other 9.0 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.19 | 1.18 | 0.57 | 0.79 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.83 | 39.49 | 7.71 | 3.37 | 5.58 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.22 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.08 | 27.32 | 4.65 | 1.53 | 2.79 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.77 | 77.83 | 6.66 | 1.28 | 2.25 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.17 | 27.62 | 11.82 | 7.29 | 9.53 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.61 | 8.68 | 2.19 | 6.71 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.186 | 0.717 | 0.842 | 0.746 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.115 | 0.199 | 0.210 | 0.047 | 0.157 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.280 | 0.199 | 0.326 | 0.280 | 0.298 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.3, CH-oop 7.5, ring-ip 1.8, other 2.2 |

850 s.
