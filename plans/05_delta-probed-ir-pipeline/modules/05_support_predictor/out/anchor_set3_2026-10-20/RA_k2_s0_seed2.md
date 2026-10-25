# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 20:46)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.25 | 0.63 | 0.75 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.23 | 42.29 | 11.60 | 5.58 | 9.57 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.21 | 0.86 | 0.40 | 0.66 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.33 | 28.43 | 6.53 | 2.61 | 3.38 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.26 | 77.02 | 6.30 | 5.69 | 1.09 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.16 | 43.03 | 20.02 | 9.40 | 18.15 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.56 | 25.37 | 12.45 | 5.38 | 10.51 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.5, CH-oop 9.3, ring-ip 2.7, other 5.2 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.17 | 0.97 | 0.55 | 0.59 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.07 | 45.03 | 20.70 | 17.40 | 19.02 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.74 | 0.79 | 0.69 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.31 | 28.39 | 3.68 | 2.33 | 2.42 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.33 | 78.77 | 4.99 | 1.41 | 3.07 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.95 | 30.53 | 9.26 | 6.92 | 9.08 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.58 | 45.41 | 36.53 | 31.03 | 33.64 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.634 | 0.148 | 0.665 | 0.818 | 0.696 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.259 | 0.368 | 0.462 | 0.313 | 0.418 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.303 | 0.368 | 0.462 | 0.313 | 0.418 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.4, CH-oop 7.6, ring-ip 2.3, other 31.7 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 2.27 | 0.97 | 0.73 | 0.79 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.26 | 41.06 | 9.03 | 6.50 | 7.37 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.65 | 0.35 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.09 | 27.44 | 7.81 | 2.99 | 5.14 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.16 | 79.15 | 3.56 | 10.16 | 2.11 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.68 | 22.78 | 13.52 | 8.89 | 12.41 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.78 | 22.59 | 8.77 | 3.30 | 7.10 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.610 | 0.207 | 0.694 | 0.698 | 0.730 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.344 | 0.343 | 0.169 | 0.315 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.371 | 0.343 | 0.169 | 0.315 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.3, CH-oop 9.0, ring-ip 3.0, other 3.2 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.80 | 0.59 | 0.23 | 0.53 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.30 | 43.42 | 7.19 | 9.51 | 7.93 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.73 | 0.46 | 0.64 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.49 | 25.95 | 6.81 | 3.62 | 6.20 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.33 | 82.30 | 1.32 | 15.21 | 7.60 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 21.40 | 28.29 | 10.08 | 11.06 | 11.85 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.48 | 21.75 | 8.11 | 9.16 | 6.23 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.556 | 0.378 | 0.414 | 0.319 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.011 | 0.000 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 15.1, CH-oop 14.0, ring-ip 3.5, other 10.7 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.97 | 2.04 | 1.39 | 0.74 | 0.91 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.49 | 41.91 | 12.78 | 7.73 | 10.28 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.19 | 1.01 | 0.56 | 0.73 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.99 | 30.05 | 9.92 | 3.04 | 5.51 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.32 | 76.88 | 6.21 | 6.94 | 1.17 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.89 | 46.46 | 21.40 | 13.03 | 19.64 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.16 | 24.82 | 12.53 | 8.37 | 10.39 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 8.2, CH-oop 14.3, ring-ip 3.0, other 8.1 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.16 | 2.19 | 1.18 | 0.66 | 0.78 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.33 | 39.49 | 7.64 | 3.68 | 5.57 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.63 | 0.26 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.62 | 27.32 | 4.69 | 2.05 | 2.79 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.23 | 77.83 | 6.06 | 1.97 | 2.10 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.73 | 27.62 | 11.43 | 7.75 | 9.38 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.19 | 21.61 | 9.01 | 2.13 | 6.84 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.677 | 0.186 | 0.713 | 0.762 | 0.749 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.154 | 0.199 | 0.210 | 0.054 | 0.154 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.381 | 0.199 | 0.326 | 0.269 | 0.296 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 7.9, ring-ip 2.3, other 2.1 |

664 s.
