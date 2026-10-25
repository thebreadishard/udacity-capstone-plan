# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 19:53)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.34 | 1.31 | 0.54 | 0.86 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.81 | 42.18 | 11.56 | 6.60 | 9.64 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.22 | 0.87 | 0.46 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.80 | 29.12 | 6.61 | 1.84 | 3.29 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.54 | 76.51 | 7.93 | 3.47 | 1.25 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.26 | 42.59 | 19.86 | 12.58 | 18.01 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 25.04 | 11.85 | 6.91 | 10.87 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 12.2, ring-ip 1.9, other 6.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.18 | 0.94 | 0.77 | 0.66 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.31 | 22.47 | 20.52 | 22.59 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.80 | 0.68 | 0.86 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.24 | 29.08 | 3.67 | 2.88 | 2.45 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.18 | 78.96 | 6.00 | 1.67 | 4.78 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.71 | 31.96 | 9.41 | 8.99 | 9.80 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.05 | 39.74 | 36.46 | 40.09 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.140 | 0.512 | 0.556 | 0.551 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.380 | 0.522 | 0.290 | 0.495 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.298 | 0.380 | 0.522 | 0.290 | 0.495 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 9.4, ring-ip 2.8, other 38.5 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.16 | 2.25 | 1.05 | 0.81 | 0.90 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 40.54 | 9.62 | 7.26 | 8.02 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.43 | 0.43 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 28.00 | 7.21 | 2.70 | 5.22 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.78 | 78.00 | 6.21 | 5.82 | 4.02 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.08 | 20.43 | 15.19 | 13.40 | 13.62 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.55 | 8.62 | 4.73 | 7.36 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.646 | 0.193 | 0.685 | 0.726 | 0.703 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.317 | 0.324 | 0.116 | 0.308 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.324 | 0.190 | 0.340 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.9, CH-oop 13.5, ring-ip 2.3, other 4.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.70 | 0.61 | 0.26 | 0.48 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.97 | 43.50 | 8.42 | 7.89 | 8.52 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.22 | 0.68 | 0.36 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.21 | 27.73 | 6.19 | 2.80 | 5.19 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.08 | 81.84 | 2.62 | 8.36 | 7.17 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.97 | 26.62 | 14.69 | 10.86 | 14.68 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.58 | 7.66 | 11.29 | 6.73 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.340 | 0.527 | 0.362 | 0.688 | 0.311 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.021 | 0.012 | 0.005 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.731 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 8.3, CH-oop 10.8, ring-ip 2.8, other 11.4 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.03 | 1.44 | 0.54 | 1.02 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.05 | 41.65 | 12.78 | 6.60 | 10.44 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.18 | 0.99 | 0.43 | 0.78 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 30.61 | 10.02 | 3.87 | 6.03 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.35 | 76.20 | 8.15 | 4.42 | 1.48 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.07 | 46.40 | 22.18 | 13.31 | 20.25 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.24 | 23.75 | 11.27 | 5.01 | 9.99 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.5, CH-oop 15.8, ring-ip 3.8, other 4.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.09 | 1.10 | 0.63 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.83 | 39.69 | 7.59 | 3.89 | 5.77 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.34 | 0.60 | 0.28 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.08 | 28.74 | 5.04 | 1.51 | 3.18 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.77 | 77.64 | 7.25 | 5.41 | 2.80 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.17 | 26.70 | 10.89 | 6.66 | 9.34 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.32 | 8.42 | 2.71 | 7.09 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.197 | 0.680 | 0.929 | 0.705 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.115 | 0.194 | 0.203 | 0.092 | 0.175 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.280 | 0.194 | 0.324 | 0.291 | 0.304 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.8, CH-oop 6.9, ring-ip 1.8, other 2.7 |

874 s.
