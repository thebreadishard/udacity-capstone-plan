# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 15:44)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.37 | 1.35 | 0.51 | 0.98 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.26 | 42.40 | 12.56 | 6.68 | 10.39 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.23 | 0.90 | 0.47 | 0.74 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.83 | 28.95 | 6.80 | 2.10 | 3.83 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.54 | 76.46 | 10.02 | 4.36 | 1.72 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.60 | 43.01 | 20.64 | 12.38 | 18.86 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.67 | 26.25 | 13.45 | 6.99 | 12.08 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.3, CH-oop 11.8, ring-ip 2.2, other 6.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.14 | 0.89 | 0.83 | 0.59 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 44.91 | 23.26 | 20.69 | 21.41 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.75 | 0.95 | 0.68 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.97 | 28.99 | 4.07 | 3.19 | 2.46 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.45 | 77.94 | 8.95 | 1.91 | 1.78 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.25 | 31.04 | 10.40 | 7.31 | 10.44 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.23 | 45.07 | 40.74 | 36.98 | 37.92 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.658 | 0.135 | 0.456 | 0.737 | 0.512 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.265 | 0.405 | 0.549 | 0.335 | 0.510 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.288 | 0.405 | 0.549 | 0.335 | 0.510 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 7.6, ring-ip 3.1, other 38.6 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.08 | 2.20 | 0.98 | 0.75 | 0.80 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.69 | 40.59 | 8.70 | 4.78 | 6.70 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.53 | 2.56 | 0.58 | 0.34 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 28.33 | 6.04 | 3.09 | 4.37 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.38 | 77.60 | 8.31 | 3.67 | 2.94 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.34 | 21.56 | 12.64 | 8.18 | 10.89 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.17 | 22.14 | 8.69 | 2.89 | 7.53 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.624 | 0.184 | 0.657 | 0.764 | 0.767 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.326 | 0.327 | 0.148 | 0.302 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.327 | 0.201 | 0.337 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.7, CH-oop 9.0, ring-ip 2.4, other 2.8 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.06 | 1.79 | 0.62 | 0.42 | 0.58 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.87 | 42.93 | 7.81 | 5.84 | 7.56 |
| A_8448043181 | ΔH residual | 1.00 | 0.56 | 2.18 | 0.69 | 0.39 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.32 | 26.68 | 6.08 | 2.87 | 5.33 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.55 | 80.99 | 5.40 | 6.66 | 4.27 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.32 | 27.02 | 12.15 | 9.03 | 12.78 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.98 | 21.41 | 7.62 | 5.68 | 7.13 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.601 | 0.317 | 0.368 | 0.394 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.011 | 0.004 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.6, CH-oop 11.6, ring-ip 2.9, other 11.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.96 | 2.07 | 1.51 | 0.81 | 1.28 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.74 | 41.92 | 13.66 | 8.44 | 11.33 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.20 | 1.05 | 0.56 | 0.89 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.52 | 30.42 | 10.87 | 4.05 | 7.59 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.63 | 76.74 | 9.72 | 5.26 | 2.09 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.93 | 46.64 | 22.82 | 16.59 | 21.36 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.58 | 24.41 | 12.30 | 7.62 | 10.61 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.4, CH-oop 19.9, ring-ip 4.3, other 7.3 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 2.16 | 1.06 | 0.79 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.82 | 39.22 | 8.21 | 4.44 | 5.60 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 2.31 | 0.62 | 0.31 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 27.91 | 4.86 | 4.14 | 3.07 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.47 | 76.57 | 10.47 | 2.92 | 1.06 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.33 | 27.41 | 9.93 | 6.80 | 8.38 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 21.61 | 9.33 | 3.76 | 7.68 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.682 | 0.174 | 0.735 | 0.677 | 0.741 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.109 | 0.202 | 0.211 | 0.115 | 0.176 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.202 | 0.326 | 0.165 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.7, CH-oop 7.0, ring-ip 4.1, other 3.8 |

592 s.
