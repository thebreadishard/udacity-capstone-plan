# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 02:12)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.28 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 29.87 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 1.41 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 26.05 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 49.45 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 25.37 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 20.54 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.28 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 32.06 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.26 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 26.08 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 52.29 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 17.94 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 31.88 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.240 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.245 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.245 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 2.03 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 29.14 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 1.44 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 21.95 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 51.19 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 20.73 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 25.82 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.411 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 2.134 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 2.136 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 1.94 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 29.26 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 1.59 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 25.40 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 52.49 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 8.58 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 16.98 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.415 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.206 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.253 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 2.37 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 27.43 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 1.61 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 24.81 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 52.32 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 13.04 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 16.85 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.402 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.107 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.298 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 2.11 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 31.44 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 1.44 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 24.82 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 55.39 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 15.46 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 18.97 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.526 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.004 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.10 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 30.47 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 1.46 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 27.15 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 48.65 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 31.35 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 21.43 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 2.14 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 28.04 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 1.53 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 25.70 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 50.19 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 15.70 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 17.85 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.360 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.253 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.254 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 3.34 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 36.08 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 2.27 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 39.54 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 49.33 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 30.44 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 22.39 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.432 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.295 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.816 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 2.26 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 27.52 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 1.57 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 24.64 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 50.38 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 16.82 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 16.09 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.469 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.201 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 3.043 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.39 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 28.86 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 1.54 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 27.04 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 51.98 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 9.82 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 16.67 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.358 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.061 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.751 |

4 s.
