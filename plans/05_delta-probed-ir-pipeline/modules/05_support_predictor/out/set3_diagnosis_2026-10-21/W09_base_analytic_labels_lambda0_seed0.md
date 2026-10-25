# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 02:24)

Model `E7_rungC_chain35h2_analytic_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.42 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 5.50 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.35 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 1.88 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 0.94 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 10.78 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 5.69 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 0.9, CH-oop 10.7, ring-ip 1.9, other 5.5 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.57 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 18.80 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.54 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 2.19 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 4.63 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 8.25 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 33.29 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.699 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.292 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.292 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.9, CH-oop 8.3, ring-ip 2.3, other 35.2 |
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 0.81 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 8.49 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 0.65 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 3.29 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 3.10 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 11.31 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 12.29 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.611 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.182 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.186 |
| A_45187bb7c8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 11.3, ring-ip 3.2, other 13.2 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.65 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 4.03 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.29 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 2.32 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 2.14 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 6.81 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 4.29 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.885 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.097 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.178 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.1, CH-oop 7.6, ring-ip 1.4, other 4.2 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 0.48 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 5.08 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 0.37 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 2.01 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 4.37 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 9.11 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 5.57 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.853 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.048 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.292 |
| A_7aa232d4e9 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.3, CH-oop 12.1, ring-ip 2.1, other 5.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.28 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 6.74 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.36 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 2.49 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 2.83 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 11.49 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 9.39 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.651 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.8, CH-oop 11.3, ring-ip 2.5, other 9.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.64 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 7.45 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.54 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 3.01 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 5.38 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 11.74 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 9.00 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.4, CH-oop 13.5, ring-ip 3.0, other 9.0 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 0.51 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 3.69 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 0.35 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 1.83 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 1.30 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 5.60 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 4.96 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.966 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.140 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.295 |
| A_d09f8d1ef8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.2, CH-oop 7.3, ring-ip 1.9, other 4.7 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 1.37 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 13.15 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 1.02 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 16.84 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 4.15 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 12.48 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 11.29 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.621 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.239 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.515 |
| A_d9139359ab | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.1, CH-oop 12.3, ring-ip 16.2, other 12.5 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 0.47 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 2.70 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 0.33 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 1.68 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 1.32 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 4.65 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 2.78 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.974 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.126 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 0.137 |
| A_ff98e1160d | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.4, CH-oop 6.7, ring-ip 1.7, other 2.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.46 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 3.77 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.28 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 2.33 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 2.00 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 6.83 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 3.69 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.872 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.094 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.094 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 6.9, ring-ip 2.3, other 3.7 |

476 s.
