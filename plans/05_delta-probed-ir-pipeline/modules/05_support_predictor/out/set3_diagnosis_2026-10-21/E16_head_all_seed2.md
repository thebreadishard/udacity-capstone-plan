# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 04:00)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.24 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 4.30 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.23 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 1.40 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 1.56 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 7.56 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 5.18 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.47 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 14.64 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.79 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 1.53 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 1.91 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 3.89 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 26.33 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.884 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.101 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.101 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 0.78 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 8.85 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.60 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 3.69 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 1.83 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 14.95 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 11.19 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.629 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.283 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.317 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.50 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 2.98 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.37 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 2.31 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 1.62 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 4.52 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 3.16 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.886 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.162 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.162 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 0.42 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 2.42 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.19 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 1.52 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 2.30 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 3.72 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 2.67 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.961 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.042 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.042 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.44 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 5.46 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.27 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 3.65 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 3.62 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 8.34 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 6.72 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.760 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.003 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.003 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.63 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 5.03 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.36 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 2.97 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 1.32 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 10.09 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 4.40 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 0.34 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 2.73 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.23 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 1.28 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 1.59 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 4.79 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 3.15 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.987 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.115 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.352 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 0.94 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 6.64 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 0.56 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 5.30 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 4.51 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 9.21 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 7.25 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.871 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.180 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 2.204 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 0.29 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 2.72 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.23 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 0.72 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 0.95 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 6.13 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 1.15 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.990 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.052 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 0.052 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.67 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 2.46 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.26 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 2.43 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 2.81 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 3.01 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 1.78 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.858 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.044 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.044 |

735 s.
