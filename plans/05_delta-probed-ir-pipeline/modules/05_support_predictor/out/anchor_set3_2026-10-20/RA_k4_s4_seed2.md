# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 22:36)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.26 | 0.48 | 0.74 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.06 | 42.29 | 11.55 | 6.45 | 9.38 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.21 | 0.86 | 0.42 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.91 | 28.43 | 6.36 | 1.20 | 3.27 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.45 | 77.02 | 7.99 | 6.74 | 0.95 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.45 | 43.03 | 19.52 | 11.40 | 17.84 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.69 | 25.37 | 12.29 | 6.35 | 10.28 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.5, CH-oop 11.0, ring-ip 1.2, other 6.1 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.17 | 0.98 | 0.91 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.15 | 45.03 | 23.91 | 20.68 | 21.93 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.79 | 0.85 | 0.73 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.32 | 28.39 | 3.73 | 3.47 | 2.59 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.83 | 78.77 | 6.71 | 1.79 | 3.12 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.37 | 30.53 | 9.40 | 7.94 | 9.06 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.98 | 45.41 | 42.36 | 36.85 | 39.05 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.651 | 0.148 | 0.537 | 0.611 | 0.579 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.368 | 0.536 | 0.436 | 0.487 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.368 | 0.536 | 0.436 | 0.487 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.1, CH-oop 8.5, ring-ip 3.4, other 39.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 2.27 | 0.96 | 0.57 | 0.74 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.59 | 41.06 | 8.75 | 4.95 | 6.96 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.29 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 27.44 | 6.99 | 2.23 | 4.85 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.60 | 79.15 | 5.43 | 2.59 | 1.02 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.43 | 22.78 | 12.98 | 9.38 | 11.50 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.16 | 22.59 | 8.97 | 3.15 | 7.54 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.637 | 0.207 | 0.668 | 0.802 | 0.748 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.344 | 0.343 | 0.098 | 0.317 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.343 | 0.098 | 0.317 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 9.3, ring-ip 2.2, other 3.1 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.80 | 0.55 | 0.21 | 0.51 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 43.42 | 7.22 | 7.59 | 7.81 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.71 | 0.46 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.25 | 25.95 | 6.51 | 3.78 | 6.21 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.80 | 82.30 | 2.92 | 7.35 | 6.79 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.45 | 28.29 | 10.40 | 11.07 | 11.99 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.95 | 21.75 | 7.91 | 9.84 | 6.19 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.326 | 0.556 | 0.348 | 0.550 | 0.334 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.001 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.3, CH-oop 13.9, ring-ip 3.7, other 11.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.04 | 1.42 | 0.72 | 0.94 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.40 | 41.91 | 12.75 | 9.03 | 10.22 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 2.19 | 1.01 | 0.60 | 0.74 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.57 | 30.05 | 9.94 | 3.52 | 5.73 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.30 | 76.88 | 8.02 | 4.64 | 1.34 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.54 | 46.46 | 20.90 | 16.93 | 19.47 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.44 | 24.82 | 12.34 | 9.54 | 10.23 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.5, CH-oop 17.4, ring-ip 3.5, other 9.5 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 2.19 | 1.16 | 0.53 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.75 | 39.49 | 7.88 | 3.26 | 5.50 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.61 | 0.21 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.15 | 27.32 | 4.59 | 1.66 | 2.73 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.63 | 77.83 | 7.85 | 1.71 | 1.69 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.49 | 27.62 | 11.65 | 6.79 | 9.28 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 21.61 | 8.83 | 2.25 | 6.84 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.186 | 0.727 | 0.893 | 0.761 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.116 | 0.199 | 0.210 | 0.035 | 0.155 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.281 | 0.199 | 0.326 | 0.282 | 0.298 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 7.0, ring-ip 1.8, other 2.3 |

766 s.
