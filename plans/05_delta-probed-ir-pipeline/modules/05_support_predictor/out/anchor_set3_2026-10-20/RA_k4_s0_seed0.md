# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 16:17)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.30 | 0.52 | 0.88 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.87 | 42.40 | 11.99 | 6.69 | 9.93 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.23 | 0.88 | 0.46 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.82 | 28.95 | 6.64 | 2.04 | 3.36 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.86 | 76.46 | 8.66 | 4.03 | 1.58 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 43.01 | 19.79 | 12.84 | 17.80 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 26.25 | 13.03 | 6.69 | 11.87 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.9, CH-oop 12.2, ring-ip 2.1, other 6.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.14 | 0.91 | 0.64 | 0.62 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.13 | 44.91 | 23.26 | 21.45 | 21.20 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.76 | 0.93 | 0.67 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.27 | 28.99 | 3.93 | 2.71 | 2.58 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.40 | 77.94 | 7.71 | 1.24 | 1.78 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.66 | 31.04 | 10.19 | 7.15 | 10.03 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.07 | 40.92 | 38.45 | 37.60 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.135 | 0.477 | 0.677 | 0.518 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.405 | 0.555 | 0.345 | 0.513 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.405 | 0.555 | 0.345 | 0.513 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.1, CH-oop 7.4, ring-ip 2.6, other 40.2 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.20 | 0.99 | 0.80 | 0.81 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 40.59 | 9.30 | 4.83 | 7.44 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.33 | 0.43 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.77 | 28.33 | 7.02 | 2.56 | 5.51 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.06 | 77.60 | 7.06 | 4.07 | 3.20 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.00 | 21.56 | 14.35 | 8.39 | 12.12 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.98 | 22.14 | 8.02 | 3.39 | 7.05 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.641 | 0.184 | 0.661 | 0.784 | 0.750 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.326 | 0.328 | 0.157 | 0.305 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.328 | 0.213 | 0.340 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.1, CH-oop 8.7, ring-ip 2.4, other 3.3 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.79 | 0.64 | 0.45 | 0.62 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.95 | 42.93 | 8.06 | 6.52 | 7.94 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.70 | 0.40 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.20 | 26.68 | 6.92 | 3.16 | 6.19 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.33 | 80.99 | 4.09 | 6.81 | 4.20 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.91 | 27.02 | 12.75 | 10.61 | 13.26 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 21.41 | 7.07 | 6.19 | 6.84 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.335 | 0.601 | 0.336 | 0.373 | 0.391 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.012 | 0.005 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.7, CH-oop 12.6, ring-ip 3.2, other 11.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.07 | 1.48 | 0.59 | 1.10 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 41.92 | 13.04 | 7.94 | 10.57 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.20 | 1.03 | 0.50 | 0.82 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.47 | 30.42 | 10.51 | 3.79 | 6.04 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.68 | 76.74 | 8.29 | 2.77 | 2.11 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.12 | 46.64 | 21.82 | 15.30 | 20.13 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.26 | 24.41 | 11.92 | 7.98 | 10.43 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.8, CH-oop 17.6, ring-ip 3.8, other 7.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.20 | 2.16 | 1.11 | 0.86 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.85 | 39.22 | 7.89 | 4.31 | 5.61 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.29 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 27.91 | 4.87 | 3.23 | 3.23 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.07 | 76.57 | 9.21 | 3.28 | 1.28 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.08 | 27.41 | 10.32 | 7.17 | 8.65 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.33 | 21.61 | 8.85 | 3.91 | 7.39 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.681 | 0.174 | 0.713 | 0.775 | 0.718 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.202 | 0.213 | 0.151 | 0.179 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.202 | 0.326 | 0.545 | 0.304 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.0, CH-oop 7.5, ring-ip 3.2, other 3.9 |

808 s.
