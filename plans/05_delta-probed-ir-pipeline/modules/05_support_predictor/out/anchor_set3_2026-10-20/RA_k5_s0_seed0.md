# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 17:29)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.37 | 1.30 | 0.46 | 0.87 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 42.40 | 11.87 | 6.57 | 9.74 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.23 | 0.88 | 0.46 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 28.95 | 6.63 | 1.86 | 3.31 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 76.46 | 8.73 | 3.46 | 1.30 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 43.01 | 19.46 | 12.79 | 17.42 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 26.25 | 12.92 | 6.59 | 11.70 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.3, CH-oop 12.1, ring-ip 1.9, other 6.3 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.14 | 0.92 | 0.69 | 0.63 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 44.91 | 24.09 | 22.20 | 21.80 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.78 | 0.96 | 0.68 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 28.99 | 3.95 | 2.74 | 2.56 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 77.94 | 7.82 | 1.38 | 2.10 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 31.04 | 10.24 | 7.31 | 9.90 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 45.07 | 42.46 | 39.80 | 38.73 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.135 | 0.451 | 0.639 | 0.503 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.405 | 0.576 | 0.358 | 0.529 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.405 | 0.576 | 0.358 | 0.529 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.3, CH-oop 7.5, ring-ip 2.6, other 41.8 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.20 | 0.99 | 0.81 | 0.81 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 40.59 | 9.33 | 4.65 | 7.52 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.60 | 0.33 | 0.43 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 28.33 | 6.91 | 2.50 | 5.56 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 77.60 | 7.21 | 4.05 | 3.47 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 21.56 | 14.50 | 7.89 | 12.27 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 22.14 | 7.98 | 3.63 | 6.98 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.184 | 0.657 | 0.800 | 0.746 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.326 | 0.328 | 0.160 | 0.304 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.328 | 0.208 | 0.339 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.1, CH-oop 8.1, ring-ip 2.5, other 3.5 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.79 | 0.64 | 0.47 | 0.64 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 42.93 | 8.14 | 6.53 | 8.09 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.69 | 0.40 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 26.68 | 6.95 | 3.18 | 6.33 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 80.99 | 4.22 | 6.51 | 4.54 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 27.02 | 13.01 | 10.82 | 13.51 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 21.41 | 6.92 | 6.18 | 6.70 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.601 | 0.332 | 0.379 | 0.384 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.012 | 0.005 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.4, CH-oop 12.8, ring-ip 3.2, other 11.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.07 | 1.48 | 0.61 | 1.10 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.92 | 12.93 | 7.90 | 10.41 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.20 | 1.03 | 0.50 | 0.81 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 30.42 | 10.51 | 3.89 | 6.06 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 76.74 | 8.40 | 1.91 | 2.21 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 46.64 | 21.46 | 15.24 | 19.78 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 24.41 | 11.82 | 7.96 | 10.26 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 17.5, ring-ip 3.9, other 8.1 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.16 | 1.11 | 0.85 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 39.22 | 7.89 | 4.32 | 5.62 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.29 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 27.91 | 4.86 | 3.01 | 3.26 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 76.57 | 9.28 | 3.72 | 1.53 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 27.41 | 10.49 | 7.16 | 8.80 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 21.61 | 8.70 | 3.95 | 7.27 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.174 | 0.711 | 0.787 | 0.713 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.202 | 0.213 | 0.158 | 0.179 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.202 | 0.326 | 0.537 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.3, CH-oop 7.5, ring-ip 3.0, other 4.0 |

963 s.
