# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 18:52)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.31 | 0.56 | 0.88 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.87 | 42.18 | 11.68 | 6.52 | 9.67 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.22 | 0.87 | 0.46 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.82 | 29.12 | 6.59 | 1.96 | 3.29 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.86 | 76.51 | 8.59 | 3.33 | 1.26 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 42.59 | 20.02 | 12.55 | 18.13 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 25.04 | 11.86 | 6.66 | 10.85 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 12.2, ring-ip 2.0, other 6.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.18 | 0.94 | 0.75 | 0.65 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.13 | 45.31 | 23.31 | 21.60 | 23.37 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.81 | 0.73 | 0.87 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.27 | 29.08 | 3.68 | 2.74 | 2.52 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.40 | 78.96 | 6.65 | 1.72 | 4.80 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.66 | 31.96 | 9.52 | 8.83 | 9.88 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.05 | 41.24 | 38.50 | 41.53 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.140 | 0.474 | 0.541 | 0.518 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.380 | 0.541 | 0.320 | 0.514 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.380 | 0.541 | 0.320 | 0.514 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.8, CH-oop 9.2, ring-ip 2.7, other 41.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 2.25 | 1.04 | 0.78 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 40.54 | 9.56 | 6.67 | 7.86 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.41 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.77 | 28.00 | 7.09 | 2.36 | 5.03 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.06 | 78.00 | 6.83 | 4.63 | 4.02 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.00 | 20.43 | 14.86 | 12.63 | 13.32 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.98 | 22.55 | 8.72 | 4.21 | 7.41 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.641 | 0.193 | 0.676 | 0.746 | 0.704 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.317 | 0.324 | 0.102 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.324 | 0.182 | 0.306 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 12.6, ring-ip 2.1, other 4.1 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.70 | 0.60 | 0.32 | 0.45 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.95 | 43.50 | 8.41 | 7.81 | 8.49 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.22 | 0.68 | 0.36 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.20 | 27.73 | 6.12 | 2.74 | 5.15 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.33 | 81.84 | 3.23 | 7.60 | 7.11 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.91 | 26.62 | 14.57 | 11.15 | 14.64 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 21.58 | 7.71 | 11.30 | 6.77 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.335 | 0.527 | 0.351 | 0.701 | 0.312 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.021 | 0.012 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.733 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.5, CH-oop 11.1, ring-ip 2.7, other 11.5 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.03 | 1.44 | 0.55 | 1.03 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 41.65 | 12.91 | 6.28 | 10.47 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.18 | 0.99 | 0.43 | 0.78 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.47 | 30.61 | 10.05 | 3.55 | 6.05 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.68 | 76.20 | 8.83 | 3.58 | 1.48 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.12 | 46.40 | 22.32 | 12.76 | 20.36 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.26 | 23.75 | 11.31 | 5.00 | 9.99 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.7, CH-oop 16.1, ring-ip 3.5, other 4.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.20 | 2.09 | 1.09 | 0.57 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.85 | 39.69 | 7.72 | 4.16 | 5.78 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.34 | 0.60 | 0.28 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 28.74 | 5.04 | 1.44 | 3.26 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.07 | 77.64 | 7.99 | 6.37 | 2.76 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.08 | 26.70 | 10.83 | 6.96 | 9.29 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.33 | 21.32 | 8.49 | 2.45 | 7.11 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.681 | 0.197 | 0.684 | 0.939 | 0.699 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.194 | 0.203 | 0.111 | 0.174 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.194 | 0.325 | 0.298 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.9, CH-oop 7.2, ring-ip 1.8, other 2.5 |

1036 s.
