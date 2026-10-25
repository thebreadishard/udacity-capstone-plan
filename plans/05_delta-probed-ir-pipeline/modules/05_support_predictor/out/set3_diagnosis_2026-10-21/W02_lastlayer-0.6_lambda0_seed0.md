# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 01:50)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.47 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 6.51 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.45 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 1.78 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 3.63 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 12.51 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 6.66 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.5, CH-oop 11.9, ring-ip 1.8, other 6.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.75 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 23.59 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.05 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 2.72 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 1.40 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 7.55 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 42.34 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.590 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.352 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.352 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.3, CH-oop 7.7, ring-ip 2.7, other 44.8 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 0.61 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 8.00 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.53 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 6.38 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 2.52 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 13.15 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 8.28 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.599 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 0.921 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 0.925 |
| A_45187bb7c8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.8, CH-oop 13.1, ring-ip 6.3, other 8.6 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.83 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 4.37 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.33 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 2.45 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 3.56 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 7.44 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 3.50 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.816 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.155 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.155 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.6, CH-oop 7.6, ring-ip 2.5, other 3.4 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 0.52 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 4.39 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.36 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 2.10 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 2.44 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 7.48 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 5.29 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.835 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.100 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.256 |
| A_7aa232d4e9 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.4, CH-oop 7.9, ring-ip 2.1, other 5.2 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.41 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 6.61 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.39 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 3.06 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 6.18 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 11.28 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 6.26 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.393 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.004 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.1, CH-oop 12.9, ring-ip 3.1, other 10.4 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.58 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 8.04 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.49 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 3.91 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 2.06 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 15.66 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 8.00 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 17.4, ring-ip 3.9, other 7.9 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 0.51 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 3.91 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.40 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 1.95 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 3.32 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 6.29 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 4.53 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.904 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.138 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.138 |
| A_d09f8d1ef8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.4, CH-oop 7.4, ring-ip 1.9, other 4.3 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 1.11 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 9.36 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 0.69 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 8.27 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 2.11 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 13.48 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 10.03 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.846 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.156 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.441 |
| A_d9139359ab | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.3, CH-oop 13.5, ring-ip 7.8, other 9.8 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 0.51 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 2.49 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.33 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 1.76 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 2.48 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 3.30 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 2.80 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.974 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.208 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 0.208 |
| A_ff98e1160d | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 4.7, ring-ip 1.8, other 2.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 4.28 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.28 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 2.45 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 4.52 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 7.19 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 3.80 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.819 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.176 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.534 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.1, CH-oop 7.5, ring-ip 2.5, other 3.8 |

425 s.
