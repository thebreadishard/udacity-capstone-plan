# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 21:54)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.28 | 0.51 | 0.83 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.65 | 42.29 | 11.63 | 6.07 | 9.55 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.21 | 0.87 | 0.39 | 0.68 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.33 | 28.43 | 6.55 | 1.43 | 3.68 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.13 | 77.02 | 8.59 | 6.40 | 0.92 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.42 | 43.03 | 19.39 | 10.94 | 17.81 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.65 | 25.37 | 12.32 | 5.66 | 10.67 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.3, CH-oop 10.6, ring-ip 1.4, other 5.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.17 | 0.94 | 0.68 | 0.58 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 45.03 | 24.21 | 22.26 | 22.80 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.79 | 0.86 | 0.75 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.93 | 28.39 | 4.01 | 3.01 | 2.64 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.90 | 78.77 | 7.35 | 2.05 | 3.37 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.45 | 30.53 | 9.48 | 7.13 | 9.03 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.21 | 45.41 | 42.82 | 39.89 | 40.66 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.653 | 0.148 | 0.524 | 0.639 | 0.557 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.264 | 0.368 | 0.542 | 0.428 | 0.513 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.368 | 0.543 | 0.428 | 0.513 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 7.9, ring-ip 3.0, other 43.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 2.27 | 0.95 | 0.59 | 0.76 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.53 | 41.06 | 8.52 | 4.15 | 6.99 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.57 | 0.28 | 0.39 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.69 | 27.44 | 5.98 | 2.21 | 4.16 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.39 | 79.15 | 5.92 | 3.54 | 1.79 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.58 | 22.78 | 13.13 | 6.75 | 11.88 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.12 | 22.59 | 8.97 | 4.18 | 7.89 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.663 | 0.207 | 0.659 | 0.841 | 0.734 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.344 | 0.342 | 0.117 | 0.326 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.342 | 0.117 | 0.326 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.5, CH-oop 6.9, ring-ip 2.2, other 4.1 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.80 | 0.56 | 0.23 | 0.48 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.75 | 43.42 | 7.08 | 8.08 | 7.92 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.18 | 0.70 | 0.45 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.04 | 25.95 | 5.82 | 3.33 | 5.49 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.76 | 82.30 | 3.45 | 10.20 | 7.47 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.56 | 28.29 | 10.64 | 11.37 | 12.52 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.89 | 21.75 | 7.92 | 9.08 | 6.59 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.349 | 0.556 | 0.338 | 0.437 | 0.321 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.010 | 0.002 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.1, CH-oop 13.8, ring-ip 3.3, other 11.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.04 | 1.45 | 0.74 | 1.13 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.91 | 12.93 | 9.55 | 10.78 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.75 | 2.19 | 1.03 | 0.60 | 0.82 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.01 | 30.05 | 10.48 | 4.07 | 7.53 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.92 | 76.88 | 8.72 | 4.48 | 1.15 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.46 | 46.46 | 20.77 | 18.53 | 19.50 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.39 | 24.82 | 12.31 | 9.51 | 10.64 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 18.6, ring-ip 4.0, other 9.4 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.24 | 2.19 | 1.09 | 0.55 | 0.73 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.52 | 39.49 | 8.00 | 3.33 | 5.72 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.61 | 0.21 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.67 | 27.32 | 4.83 | 1.46 | 2.93 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.38 | 77.83 | 8.36 | 2.67 | 2.29 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.64 | 27.62 | 11.65 | 6.78 | 9.43 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.41 | 21.61 | 8.77 | 2.30 | 7.14 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.687 | 0.186 | 0.733 | 0.875 | 0.737 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.199 | 0.208 | 0.044 | 0.170 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.276 | 0.199 | 0.328 | 0.284 | 0.307 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.6, CH-oop 7.0, ring-ip 1.8, other 2.3 |

838 s.
