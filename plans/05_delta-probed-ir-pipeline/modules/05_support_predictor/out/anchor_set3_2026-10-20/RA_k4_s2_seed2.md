# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 22:08)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.24 | 0.55 | 0.73 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.86 | 42.29 | 11.46 | 6.01 | 9.36 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.21 | 0.86 | 0.39 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.78 | 28.43 | 6.39 | 1.61 | 3.29 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.83 | 77.02 | 7.59 | 6.39 | 1.25 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 43.03 | 19.39 | 10.39 | 17.66 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 25.37 | 12.24 | 5.97 | 10.35 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.2, CH-oop 10.2, ring-ip 1.7, other 5.8 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.17 | 0.98 | 0.66 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.03 | 23.37 | 21.73 | 21.61 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.78 | 0.87 | 0.73 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 28.39 | 3.78 | 2.74 | 2.59 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.38 | 78.77 | 6.34 | 2.05 | 3.56 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 30.53 | 9.36 | 8.17 | 8.99 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.86 | 45.41 | 41.38 | 38.82 | 38.45 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.644 | 0.148 | 0.566 | 0.565 | 0.594 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.368 | 0.523 | 0.448 | 0.479 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.297 | 0.368 | 0.523 | 0.448 | 0.479 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 8.8, ring-ip 2.7, other 41.3 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 2.27 | 0.96 | 0.61 | 0.75 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.74 | 41.06 | 8.92 | 4.98 | 7.24 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.29 | 0.41 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.73 | 27.44 | 7.17 | 2.43 | 4.96 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.04 | 79.15 | 4.95 | 5.26 | 1.79 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.94 | 22.78 | 13.56 | 8.29 | 12.15 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.01 | 22.59 | 8.76 | 3.44 | 7.36 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.643 | 0.207 | 0.672 | 0.786 | 0.738 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.344 | 0.343 | 0.120 | 0.318 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.371 | 0.343 | 0.120 | 0.318 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.3, CH-oop 8.4, ring-ip 2.4, other 3.3 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.12 | 1.80 | 0.55 | 0.20 | 0.51 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.92 | 43.42 | 7.25 | 8.27 | 8.08 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.71 | 0.45 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.15 | 25.95 | 6.63 | 3.72 | 6.28 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.31 | 82.30 | 2.48 | 11.20 | 7.64 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.86 | 28.29 | 10.51 | 10.99 | 12.26 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.76 | 21.75 | 7.83 | 8.90 | 6.17 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.336 | 0.556 | 0.355 | 0.433 | 0.317 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.011 | 0.000 | 0.005 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 11.1, CH-oop 13.8, ring-ip 3.6, other 10.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.04 | 1.41 | 0.73 | 0.93 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 41.91 | 12.66 | 8.61 | 10.15 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.19 | 1.01 | 0.58 | 0.73 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 30.05 | 9.99 | 3.50 | 5.67 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.65 | 76.88 | 7.58 | 4.85 | 1.60 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.16 | 46.46 | 20.73 | 16.02 | 19.26 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.28 | 24.82 | 12.26 | 9.03 | 10.21 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.2, CH-oop 16.6, ring-ip 3.5, other 8.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.19 | 2.19 | 1.16 | 0.61 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.81 | 39.49 | 7.82 | 3.53 | 5.59 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.23 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.06 | 27.32 | 4.65 | 1.81 | 2.82 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.05 | 77.83 | 7.40 | 2.01 | 2.31 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.03 | 27.62 | 11.75 | 7.42 | 9.42 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.35 | 21.61 | 8.74 | 2.20 | 6.82 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.186 | 0.718 | 0.818 | 0.745 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.199 | 0.210 | 0.054 | 0.156 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.199 | 0.326 | 0.275 | 0.298 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 7.6, ring-ip 2.1, other 2.2 |

769 s.
