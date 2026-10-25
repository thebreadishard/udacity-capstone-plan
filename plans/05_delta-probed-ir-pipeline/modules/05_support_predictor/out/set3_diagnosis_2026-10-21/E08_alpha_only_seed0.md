# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 01:17)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, α tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 1.30 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 11.87 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.88 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 6.63 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 8.73 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 19.46 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 12.92 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.92 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 24.09 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.78 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 3.95 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 7.82 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 10.24 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 42.46 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.451 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.576 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.576 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 1.39 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 11.93 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.93 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 5.98 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 8.88 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 18.93 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 14.21 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.499 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.261 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.265 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.99 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 9.33 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.60 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 6.91 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 7.21 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 14.50 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 7.98 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.657 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.328 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 1.38 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 8.74 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.85 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 6.49 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 5.97 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 9.92 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 11.39 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.675 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.261 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.473 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.64 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 8.14 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.69 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 6.95 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 4.22 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 13.01 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 6.92 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.332 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.012 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 1.48 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 12.93 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 1.03 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 10.51 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 8.40 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 21.46 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 11.82 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 1.31 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 8.07 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.84 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 5.46 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 7.26 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 9.38 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 10.42 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.736 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.128 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.369 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 2.89 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 12.32 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 1.72 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 11.19 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 9.23 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 12.49 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 15.06 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.808 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.299 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.451 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 1.30 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 8.41 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.83 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 5.61 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 7.66 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 9.90 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 10.87 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.710 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.375 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 2.642 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 1.11 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 7.89 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.61 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 4.86 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 9.28 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 10.49 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 8.70 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.711 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.213 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.326 |

562 s.
