# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 16:31)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.33 | 0.46 | 0.93 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.65 | 42.40 | 12.14 | 6.38 | 9.91 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.23 | 0.90 | 0.44 | 0.72 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.33 | 28.95 | 6.78 | 1.97 | 3.64 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.13 | 76.46 | 9.51 | 3.55 | 1.13 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.42 | 43.01 | 19.74 | 12.33 | 17.81 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.65 | 26.25 | 13.10 | 6.35 | 11.74 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.4, CH-oop 11.7, ring-ip 2.0, other 6.1 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.14 | 0.90 | 0.69 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 44.91 | 24.24 | 22.70 | 22.11 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.77 | 0.99 | 0.69 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.93 | 28.99 | 4.07 | 3.01 | 2.49 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.90 | 77.94 | 8.57 | 1.14 | 2.65 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.45 | 31.04 | 10.32 | 7.50 | 10.14 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.21 | 45.07 | 42.65 | 40.68 | 39.26 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.653 | 0.135 | 0.437 | 0.633 | 0.500 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.264 | 0.405 | 0.577 | 0.369 | 0.531 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.405 | 0.577 | 0.369 | 0.531 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.0, CH-oop 7.7, ring-ip 2.9, other 42.9 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 2.20 | 0.98 | 0.76 | 0.80 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.53 | 40.59 | 9.02 | 4.41 | 7.17 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.58 | 0.32 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.69 | 28.33 | 6.15 | 2.64 | 4.74 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.39 | 77.60 | 7.90 | 3.42 | 3.78 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.58 | 21.56 | 13.90 | 7.40 | 11.86 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.12 | 22.14 | 8.24 | 3.69 | 7.13 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.663 | 0.184 | 0.651 | 0.810 | 0.746 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.326 | 0.327 | 0.166 | 0.303 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.327 | 0.222 | 0.338 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.4, CH-oop 7.8, ring-ip 2.5, other 3.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.79 | 0.63 | 0.47 | 0.60 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.75 | 42.93 | 7.98 | 6.45 | 7.88 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.18 | 0.69 | 0.40 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.04 | 26.68 | 6.34 | 2.98 | 5.64 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.76 | 80.99 | 4.93 | 7.99 | 5.15 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.56 | 27.02 | 12.82 | 9.81 | 13.30 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.89 | 21.41 | 7.15 | 5.86 | 6.78 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.349 | 0.601 | 0.320 | 0.340 | 0.376 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.004 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.9, CH-oop 12.1, ring-ip 3.0, other 11.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.07 | 1.50 | 0.77 | 1.24 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.92 | 13.25 | 8.09 | 10.83 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.75 | 2.20 | 1.04 | 0.55 | 0.86 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.01 | 30.42 | 10.85 | 4.79 | 7.30 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.92 | 76.74 | 9.22 | 2.96 | 2.47 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.46 | 46.64 | 21.82 | 15.54 | 20.26 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.39 | 24.41 | 11.96 | 7.58 | 10.21 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 18.6, ring-ip 5.0, other 7.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.24 | 2.16 | 1.07 | 0.82 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.52 | 39.22 | 8.04 | 4.30 | 5.59 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.61 | 0.30 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.67 | 27.91 | 4.90 | 3.12 | 3.12 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.38 | 76.57 | 9.94 | 4.78 | 1.86 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.64 | 27.41 | 10.26 | 6.26 | 8.68 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.41 | 21.61 | 8.87 | 3.98 | 7.30 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.687 | 0.174 | 0.723 | 0.777 | 0.721 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.202 | 0.212 | 0.326 | 0.176 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.276 | 0.202 | 0.326 | 0.375 | 0.302 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.2, CH-oop 6.6, ring-ip 3.1, other 4.0 |

833 s.
