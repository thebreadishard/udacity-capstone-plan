# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 02:12)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.10 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.59 | 0.58 |
| A_01f3186607 | ΔH residual | 1.00 | 0.68 | 0.06 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.53 | 0.48 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.59 | 0.34 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.27 | 1.01 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.61 | 0.43 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.05 | 0.17 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 9.07 | 1.26 |
| A_3100da3761 | ΔH residual | 1.00 | 0.63 | 0.04 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 6.14 | 0.83 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 5.87 | 0.30 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.97 | 0.67 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 11.09 | 2.02 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.595 | 0.994 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.216 | 0.042 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.432 | 0.042 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.89 | 0.13 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.26 | 0.60 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.80 | 0.12 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.42 | 0.60 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 6.75 | 0.58 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.86 | 0.89 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.13 | 0.39 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.498 | 0.951 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.832 | 0.097 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.834 | 0.109 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 0.12 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.38 | 1.15 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.49 | 0.09 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.44 | 1.17 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 0.40 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.34 | 1.70 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.20 | 0.57 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.662 | 0.974 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.085 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.085 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 0.09 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.41 | 0.47 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.63 | 0.05 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.14 | 0.57 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.30 | 0.52 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.73 | 0.52 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.77 | 0.19 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.639 | 0.999 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.057 | 0.019 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 0.284 | 0.019 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 0.12 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.71 | 0.91 |
| A_8448043181 | ΔH residual | 1.00 | 0.53 | 0.04 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 7.91 | 1.22 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.86 | 0.52 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.55 | 0.52 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.93 | 0.71 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.347 | 0.999 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.001 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.001 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.93 | 0.10 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.65 | 0.45 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.74 | 0.06 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.15 | 0.45 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 7.92 | 0.22 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.83 | 0.71 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.10 | 0.35 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 0.08 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.19 | 0.47 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.69 | 0.08 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.27 | 0.37 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 6.68 | 0.53 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 9.97 | 0.73 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.29 | 0.36 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.690 | 0.999 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.095 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.095 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 0.99 | 0.12 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.46 | 0.51 |
| A_d9139359ab | ΔH residual | 1.00 | 0.70 | 0.07 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.38 | 0.53 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.78 | 0.42 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.80 | 0.72 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.22 | 0.33 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.620 | 0.997 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.138 | 0.092 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.630 | 0.126 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 0.09 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.17 | 0.50 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.08 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.16 | 0.46 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 6.74 | 0.59 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.48 | 0.76 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.43 | 0.20 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.650 | 0.999 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.038 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.018 | 0.038 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.17 | 0.18 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.50 | 0.57 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.46 | 0.05 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.62 | 0.77 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.44 | 0.44 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.58 | 0.52 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.45 | 0.17 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.690 | 0.991 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.109 | 0.013 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.013 |

807 s.
