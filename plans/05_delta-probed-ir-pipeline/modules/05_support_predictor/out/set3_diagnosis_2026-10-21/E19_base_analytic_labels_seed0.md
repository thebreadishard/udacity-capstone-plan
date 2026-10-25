# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 02:38)

Model `E7_rungC_chain35h2_analytic_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | head tuned, L2 1 |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.76 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 9.54 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.65 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 2.94 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 1.97 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 18.02 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 10.64 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.54 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 20.39 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.64 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 2.25 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 2.72 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 8.58 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 36.30 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.571 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.475 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.475 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 0.81 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 9.74 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.72 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 3.38 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 1.99 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 16.40 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 12.61 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.611 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.279 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.282 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.73 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 7.31 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.35 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 4.58 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 2.76 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 12.83 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 6.42 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.737 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.269 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.307 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 0.74 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 5.76 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.51 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 2.94 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 3.10 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 9.73 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 6.91 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.761 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.054 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.287 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.53 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 7.39 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.57 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 5.56 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 6.13 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 11.81 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 5.91 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.354 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.96 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 10.00 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.72 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 5.93 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 2.63 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 19.22 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 9.53 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 0.80 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 5.66 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.57 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 2.46 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 2.04 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 8.61 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 7.78 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.925 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.202 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.423 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 2.95 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 11.17 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 1.75 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 10.53 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 2.93 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 10.81 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 14.87 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.767 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.280 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.571 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 0.73 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 5.39 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.52 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 2.49 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 1.26 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 8.16 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 7.36 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.826 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.172 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 3.105 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.62 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 4.90 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.43 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 2.61 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 2.08 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 7.60 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 6.41 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.785 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.147 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.286 |

478 s.
