# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 16:06)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.34 | 0.64 | 0.94 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.50 | 42.40 | 12.26 | 6.84 | 10.38 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 2.23 | 0.89 | 0.50 | 0.73 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.50 | 28.95 | 6.68 | 2.24 | 3.54 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.09 | 76.46 | 8.11 | 3.48 | 2.19 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.36 | 43.01 | 20.59 | 12.82 | 18.74 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 26.25 | 13.36 | 7.28 | 12.25 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.4, CH-oop 12.2, ring-ip 2.3, other 7.0 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.08 | 2.14 | 0.90 | 0.74 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 44.91 | 21.43 | 19.29 | 19.61 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 1.64 | 0.73 | 0.89 | 0.64 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.42 | 28.99 | 3.88 | 2.68 | 2.44 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.91 | 77.94 | 7.03 | 1.27 | 1.02 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.56 | 31.04 | 10.21 | 6.57 | 10.26 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.75 | 45.07 | 37.56 | 34.54 | 34.61 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.643 | 0.135 | 0.534 | 0.789 | 0.562 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.405 | 0.511 | 0.302 | 0.476 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.405 | 0.511 | 0.302 | 0.476 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.2, CH-oop 6.9, ring-ip 2.5, other 35.7 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.12 | 2.20 | 0.99 | 0.76 | 0.84 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.07 | 40.59 | 9.03 | 5.30 | 7.19 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.63 | 0.34 | 0.44 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.00 | 28.33 | 7.24 | 2.80 | 5.39 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.90 | 77.60 | 6.42 | 4.43 | 2.60 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 21.56 | 13.48 | 9.45 | 11.53 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.97 | 22.14 | 8.34 | 2.70 | 7.33 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.602 | 0.184 | 0.680 | 0.752 | 0.762 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.326 | 0.328 | 0.131 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.328 | 0.197 | 0.341 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.4, CH-oop 9.9, ring-ip 2.3, other 2.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.07 | 1.79 | 0.65 | 0.34 | 0.62 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.19 | 42.93 | 7.86 | 5.94 | 7.71 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.18 | 0.71 | 0.39 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.61 | 26.68 | 6.87 | 2.87 | 6.00 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.03 | 80.99 | 3.50 | 6.24 | 3.32 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.83 | 27.02 | 12.16 | 9.36 | 12.87 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 21.41 | 7.48 | 6.21 | 7.13 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.298 | 0.601 | 0.353 | 0.392 | 0.404 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.012 | 0.004 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.2, CH-oop 11.6, ring-ip 2.9, other 11.2 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 2.07 | 1.47 | 0.63 | 1.10 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.87 | 41.92 | 13.27 | 7.98 | 10.99 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 2.20 | 1.03 | 0.52 | 0.83 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.17 | 30.42 | 10.38 | 3.08 | 6.08 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.21 | 76.74 | 7.69 | 6.20 | 1.95 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.40 | 46.64 | 22.70 | 15.78 | 21.05 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.38 | 24.41 | 12.24 | 7.07 | 10.90 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.2, CH-oop 18.1, ring-ip 3.1, other 6.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.14 | 2.16 | 1.10 | 0.87 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 39.22 | 7.82 | 4.25 | 5.65 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 2.31 | 0.62 | 0.29 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.75 | 27.91 | 4.83 | 3.52 | 3.14 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.99 | 76.57 | 8.57 | 2.02 | 0.97 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.01 | 27.41 | 10.02 | 7.37 | 8.41 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.34 | 21.61 | 9.25 | 3.56 | 7.75 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.672 | 0.174 | 0.717 | 0.739 | 0.734 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.173 | 0.202 | 0.213 | 0.190 | 0.182 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.309 | 0.202 | 0.326 | 0.502 | 0.305 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.1, CH-oop 7.6, ring-ip 3.5, other 3.6 |

654 s.
