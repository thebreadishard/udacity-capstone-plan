# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 01:58)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | head tuned, L2 1 |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 1.06 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 9.68 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.68 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 5.07 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 5.97 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 15.65 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 11.30 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 1.01 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 26.46 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.99 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 4.33 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 4.79 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 12.02 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 46.79 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.383 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.552 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.552 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 1.16 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 10.17 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.84 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 5.84 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 4.87 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 11.19 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 14.71 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.537 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.836 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.838 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 1.01 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 6.54 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.37 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 2.33 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 3.89 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 12.10 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 5.83 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.840 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.256 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.256 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 1.19 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 6.32 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.66 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 5.28 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 3.02 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 7.18 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 8.03 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.805 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.093 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.293 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.70 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 7.69 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.48 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 3.54 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 2.04 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 15.17 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 6.41 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.441 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.004 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 1.21 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 11.34 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.80 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 7.27 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 8.07 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 19.16 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 11.48 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 1.08 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 6.02 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.68 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 5.01 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 4.95 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 5.69 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 7.74 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.861 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.236 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.439 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 2.40 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 16.38 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 1.49 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 19.19 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 7.07 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 18.36 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 14.74 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.836 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.259 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.642 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 1.13 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 6.20 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.65 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 4.78 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 5.27 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 7.16 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 7.72 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.885 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.153 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 0.164 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.80 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 5.84 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.39 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 2.64 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 3.68 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 10.61 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 6.21 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.792 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.085 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.706 |

438 s.
