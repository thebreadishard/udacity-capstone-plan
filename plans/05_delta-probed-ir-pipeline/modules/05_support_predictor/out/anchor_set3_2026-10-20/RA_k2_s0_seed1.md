# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 17:54)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.31 | 0.75 | 0.89 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.23 | 42.18 | 11.83 | 6.70 | 9.97 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.22 | 0.87 | 0.47 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.33 | 29.12 | 6.67 | 2.18 | 3.39 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.26 | 76.51 | 7.53 | 5.41 | 1.18 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.16 | 42.59 | 20.69 | 13.51 | 18.76 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.56 | 25.04 | 12.08 | 5.15 | 11.15 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.6, CH-oop 13.4, ring-ip 2.2, other 4.9 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.18 | 0.93 | 0.74 | 0.65 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.07 | 45.31 | 21.16 | 21.09 | 21.31 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.78 | 0.86 | 0.84 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.31 | 29.08 | 3.66 | 2.75 | 2.38 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.33 | 78.96 | 5.54 | 1.15 | 4.14 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.95 | 31.96 | 9.68 | 8.71 | 9.90 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.58 | 45.05 | 37.29 | 37.59 | 37.74 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.634 | 0.140 | 0.548 | 0.606 | 0.594 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.259 | 0.380 | 0.489 | 0.265 | 0.461 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.303 | 0.380 | 0.489 | 0.266 | 0.461 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.2, CH-oop 9.1, ring-ip 2.7, other 39.3 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 2.25 | 1.05 | 0.86 | 0.93 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.26 | 40.54 | 9.60 | 8.00 | 8.00 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.64 | 0.47 | 0.45 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.09 | 28.00 | 7.59 | 3.15 | 5.44 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.16 | 78.00 | 5.66 | 5.25 | 3.53 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.68 | 20.43 | 14.92 | 15.16 | 13.47 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.78 | 22.55 | 8.70 | 4.81 | 7.44 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.610 | 0.193 | 0.695 | 0.723 | 0.713 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.317 | 0.324 | 0.119 | 0.309 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.328 | 0.324 | 0.191 | 0.336 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.3, CH-oop 15.3, ring-ip 2.6, other 4.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.70 | 0.61 | 0.24 | 0.49 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.30 | 43.50 | 8.25 | 7.84 | 8.42 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.22 | 0.70 | 0.36 | 0.61 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.49 | 27.73 | 6.23 | 2.60 | 5.14 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.33 | 81.84 | 2.16 | 7.90 | 6.68 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 21.40 | 26.62 | 14.09 | 10.97 | 14.54 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.48 | 21.58 | 7.99 | 11.48 | 7.05 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.527 | 0.373 | 0.700 | 0.322 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.021 | 0.012 | 0.003 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.733 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.8, CH-oop 10.9, ring-ip 2.6, other 11.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.97 | 2.03 | 1.43 | 0.57 | 1.01 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.49 | 41.65 | 13.03 | 7.44 | 10.77 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.18 | 1.00 | 0.42 | 0.79 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.99 | 30.61 | 9.99 | 4.07 | 5.97 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.32 | 76.20 | 7.69 | 7.08 | 2.32 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.89 | 46.40 | 23.00 | 13.34 | 20.92 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.16 | 23.75 | 11.54 | 6.65 | 10.37 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.7, CH-oop 15.6, ring-ip 4.0, other 6.8 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.16 | 2.09 | 1.09 | 0.58 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.33 | 39.69 | 7.56 | 4.05 | 5.77 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.34 | 0.61 | 0.27 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.62 | 28.74 | 5.07 | 1.33 | 3.15 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.23 | 77.64 | 6.77 | 6.28 | 2.37 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.73 | 26.70 | 10.60 | 6.54 | 9.08 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.19 | 21.32 | 8.78 | 2.74 | 7.40 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.677 | 0.197 | 0.681 | 0.937 | 0.716 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.154 | 0.194 | 0.203 | 0.139 | 0.175 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.381 | 0.194 | 0.324 | 0.303 | 0.305 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.9, CH-oop 6.8, ring-ip 1.5, other 2.8 |

775 s.
