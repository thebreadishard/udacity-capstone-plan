# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 21:40)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.24 | 0.55 | 0.73 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.87 | 42.29 | 11.47 | 5.69 | 9.36 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.21 | 0.86 | 0.39 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.82 | 28.43 | 6.39 | 1.72 | 3.30 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.86 | 77.02 | 7.62 | 5.98 | 1.18 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 43.03 | 19.44 | 9.88 | 17.68 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 25.37 | 12.23 | 5.57 | 10.33 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.8, CH-oop 9.6, ring-ip 1.7, other 5.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.17 | 0.98 | 0.66 | 0.59 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.13 | 45.03 | 23.22 | 21.46 | 21.38 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.78 | 0.86 | 0.72 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.27 | 28.39 | 3.75 | 2.79 | 2.57 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.40 | 78.77 | 6.38 | 1.78 | 3.47 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.66 | 30.53 | 9.34 | 7.58 | 8.95 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.41 | 41.11 | 38.40 | 38.03 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.148 | 0.573 | 0.599 | 0.606 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.368 | 0.520 | 0.434 | 0.475 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.368 | 0.520 | 0.434 | 0.475 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.9, CH-oop 8.2, ring-ip 2.8, other 40.8 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.27 | 0.96 | 0.62 | 0.75 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 41.06 | 8.92 | 4.88 | 7.23 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.29 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.77 | 27.44 | 7.15 | 2.40 | 4.90 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.06 | 79.15 | 4.99 | 5.40 | 1.63 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.00 | 22.78 | 13.55 | 7.93 | 12.21 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.98 | 22.59 | 8.75 | 3.52 | 7.32 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.641 | 0.207 | 0.672 | 0.781 | 0.739 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.344 | 0.343 | 0.122 | 0.318 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.343 | 0.122 | 0.318 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.4, CH-oop 8.0, ring-ip 2.4, other 3.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.80 | 0.56 | 0.19 | 0.51 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.95 | 43.42 | 7.25 | 8.19 | 8.02 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.71 | 0.44 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.20 | 25.95 | 6.63 | 3.40 | 6.23 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.33 | 82.30 | 2.51 | 10.95 | 7.52 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.91 | 28.29 | 10.49 | 11.15 | 12.22 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 21.75 | 7.84 | 8.92 | 6.16 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.335 | 0.556 | 0.355 | 0.438 | 0.320 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.001 | 0.005 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.8, CH-oop 13.7, ring-ip 3.3, other 10.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.04 | 1.41 | 0.74 | 0.93 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 41.91 | 12.67 | 8.47 | 10.15 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.19 | 1.01 | 0.58 | 0.73 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.47 | 30.05 | 9.97 | 3.63 | 5.68 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.68 | 76.88 | 7.62 | 4.86 | 1.52 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.12 | 46.46 | 20.76 | 15.77 | 19.26 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.26 | 24.82 | 12.27 | 8.77 | 10.20 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.1, CH-oop 16.3, ring-ip 3.6, other 8.6 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.20 | 2.19 | 1.16 | 0.56 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.85 | 39.49 | 7.84 | 3.27 | 5.58 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.22 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 27.32 | 4.65 | 1.64 | 2.80 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.07 | 77.83 | 7.50 | 1.43 | 2.15 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.08 | 27.62 | 11.74 | 6.93 | 9.45 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.33 | 21.61 | 8.75 | 2.19 | 6.80 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.681 | 0.186 | 0.722 | 0.850 | 0.747 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.199 | 0.210 | 0.043 | 0.156 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.199 | 0.326 | 0.279 | 0.298 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.4, CH-oop 7.1, ring-ip 1.9, other 2.2 |

833 s.
