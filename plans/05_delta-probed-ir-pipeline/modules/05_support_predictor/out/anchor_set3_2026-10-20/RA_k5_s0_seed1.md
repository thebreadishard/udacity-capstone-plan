# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 20:22)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.34 | 1.31 | 0.52 | 0.87 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 42.18 | 11.55 | 6.58 | 9.53 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.22 | 0.87 | 0.46 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 29.12 | 6.58 | 1.88 | 3.25 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 76.51 | 8.61 | 2.86 | 1.45 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 42.59 | 19.65 | 12.45 | 17.80 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 25.04 | 11.76 | 7.12 | 10.75 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.7, CH-oop 12.1, ring-ip 1.9, other 6.9 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.18 | 0.95 | 0.80 | 0.66 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 45.31 | 24.11 | 22.13 | 24.15 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.82 | 0.72 | 0.89 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 29.08 | 3.70 | 2.87 | 2.56 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 78.96 | 6.69 | 1.71 | 5.03 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 31.96 | 9.45 | 9.21 | 9.88 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 45.05 | 42.72 | 39.41 | 42.96 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.140 | 0.451 | 0.520 | 0.491 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.380 | 0.562 | 0.338 | 0.536 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.380 | 0.562 | 0.338 | 0.536 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.8, CH-oop 9.6, ring-ip 2.8, other 42.2 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.25 | 1.04 | 0.77 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 40.54 | 9.58 | 6.54 | 7.90 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.60 | 0.41 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 28.00 | 7.00 | 2.35 | 5.00 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 78.00 | 6.92 | 4.71 | 4.24 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 20.43 | 15.00 | 12.24 | 13.41 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 22.55 | 8.67 | 4.44 | 7.39 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.193 | 0.674 | 0.748 | 0.701 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.317 | 0.325 | 0.112 | 0.305 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.325 | 0.187 | 0.305 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.8, CH-oop 12.2, ring-ip 2.2, other 4.3 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.70 | 0.61 | 0.32 | 0.46 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 43.50 | 8.49 | 7.78 | 8.55 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.22 | 0.68 | 0.36 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 27.73 | 6.15 | 2.77 | 5.19 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 81.84 | 3.30 | 7.41 | 7.31 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 26.62 | 14.84 | 11.15 | 14.72 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 21.58 | 7.56 | 11.33 | 6.65 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.527 | 0.348 | 0.718 | 0.307 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.021 | 0.011 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.3, CH-oop 11.0, ring-ip 2.8, other 11.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.03 | 1.45 | 0.56 | 1.04 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.65 | 12.78 | 6.48 | 10.34 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.18 | 0.99 | 0.43 | 0.78 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 30.61 | 10.05 | 3.66 | 6.05 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 76.20 | 8.88 | 3.46 | 1.21 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 46.40 | 21.96 | 13.05 | 20.08 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 23.75 | 11.18 | 5.33 | 9.85 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.6, CH-oop 16.2, ring-ip 3.6, other 5.1 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.09 | 1.09 | 0.60 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 39.69 | 7.72 | 4.15 | 5.79 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.34 | 0.60 | 0.28 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 28.74 | 5.04 | 1.49 | 3.26 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 77.64 | 8.02 | 6.37 | 2.95 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 26.70 | 10.99 | 6.81 | 9.42 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 21.32 | 8.34 | 2.59 | 7.00 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.197 | 0.682 | 0.934 | 0.696 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.194 | 0.203 | 0.101 | 0.174 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.194 | 0.325 | 0.295 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.8, CH-oop 7.0, ring-ip 1.8, other 2.6 |

998 s.
