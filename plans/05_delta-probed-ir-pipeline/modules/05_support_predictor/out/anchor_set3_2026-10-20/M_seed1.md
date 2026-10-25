# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 23:18)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 | head tuned, oop couplings from the low level | head tuned L2 1, oop couplings from the low level | low level + oop model |  head tuned, oop block from the model | head tuned L2 1, oop block from the model |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A_45187bb7c8 | ring-coupling ratio | 1.00 | 0.90 | 1.84 | 1.36 | 0.79 | 0.88 | 0.79 | 0.88 | 1.00 | 0.79 | 0.88 |
| A_45187bb7c8 | ω rms, all modes (cm⁻¹) | 20.75 | 9.52 | 41.56 | 11.87 | 9.09 | 9.78 | 9.03 | 9.73 | 17.01 | 5.87 | 5.65 |
| A_45187bb7c8 | ΔH residual | 1.00 | 0.82 | 2.11 | 0.90 | 0.68 | 0.72 | 0.70 | 0.72 | 0.86 | 0.62 | 0.65 |
| A_45187bb7c8 | ω rms ring-ip (cm⁻¹) | 13.54 | 8.66 | 29.03 | 5.88 | 4.37 | 4.12 | 4.37 | 4.12 | 13.54 | 4.37 | 4.12 |
| A_45187bb7c8 | ω rms CH-stretch (cm⁻¹) | 34.39 | 7.76 | 77.29 | 8.39 | 4.72 | 2.03 | 4.72 | 2.03 | 34.39 | 4.72 | 2.03 |
| A_45187bb7c8 | ω rms CH-oop (cm⁻¹) | 18.55 | 5.93 | 43.71 | 19.41 | 12.72 | 16.63 | 12.51 | 16.43 | 8.54 | 8.54 | 8.54 |
| A_45187bb7c8 | ω rms other (cm⁻¹) | 20.56 | 12.26 | 27.10 | 13.96 | 12.34 | 12.27 | 12.30 | 12.29 | 10.08 | 6.40 | 6.65 |
| A_45187bb7c8 | spectrum overlap (CC APT) | 0.351 | 0.486 | 0.269 | 0.510 | 0.574 | 0.627 | 0.578 | 0.637 | 0.335 | 0.599 | 0.664 |
| A_45187bb7c8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 1.819 | 1.831 | 1.336 | 1.348 | 1.505 | 1.166 | 1.825 | 1.814 | 1.819 | 1.825 | 1.814 |
| A_45187bb7c8 | intensity rel. rms (CC APT) | 1.821 | 1.833 | 1.339 | 1.350 | 1.637 | 1.213 | 1.935 | 1.845 | 1.823 | 1.935 | 1.845 |
| A_45187bb7c8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 12.7, ring-ip 4.4, other 13.5 |
| A_7aa232d4e9 | ring-coupling ratio | 1.00 | 0.99 | 2.28 | 1.37 | 0.50 | 0.78 | 0.50 | 0.78 | 1.00 | 0.50 | 0.78 |
| A_7aa232d4e9 | ω rms, all modes (cm⁻¹) | 18.39 | 7.51 | 39.37 | 8.32 | 4.53 | 6.48 | 4.63 | 6.48 | 17.68 | 5.59 | 5.86 |
| A_7aa232d4e9 | ΔH residual | 1.00 | 0.64 | 2.45 | 0.82 | 0.41 | 0.56 | 0.36 | 0.51 | 0.94 | 0.36 | 0.45 |
| A_7aa232d4e9 | ω rms ring-ip (cm⁻¹) | 14.94 | 7.26 | 29.30 | 5.76 | 2.27 | 3.10 | 2.27 | 3.10 | 14.83 | 2.27 | 3.10 |
| A_7aa232d4e9 | ω rms CH-stretch (cm⁻¹) | 35.84 | 5.51 | 79.56 | 5.19 | 4.61 | 4.65 | 4.61 | 4.65 | 35.84 | 4.61 | 4.65 |
| A_7aa232d4e9 | ω rms CH-oop (cm⁻¹) | 8.77 | 12.94 | 30.38 | 9.90 | 6.45 | 9.04 | 6.83 | 8.98 | 8.77 | 9.26 | 9.26 |
| A_7aa232d4e9 | ω rms other (cm⁻¹) | 13.11 | 4.71 | 23.18 | 11.07 | 5.53 | 8.67 | 5.57 | 8.71 | 9.69 | 6.69 | 6.99 |
| A_7aa232d4e9 | spectrum overlap (CC APT) | 0.627 | 0.633 | 0.313 | 0.692 | 0.812 | 0.709 | 0.811 | 0.711 | 0.601 | 0.863 | 0.876 |
| A_7aa232d4e9 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.060 | 0.058 | 0.097 | 0.260 | 0.035 | 0.067 | 0.040 | 0.071 | 0.060 | 0.040 | 0.071 |
| A_7aa232d4e9 | intensity rel. rms (CC APT) | 0.294 | 1.375 | 0.432 | 0.471 | 0.278 | 0.286 | 0.289 | 0.287 | 0.795 | 0.076 | 0.218 |
| A_7aa232d4e9 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.6, CH-oop 7.9, ring-ip 2.4, other 5.4 |
| A_d09f8d1ef8 | ring-coupling ratio | 1.00 | 0.95 | 2.21 | 1.28 | 0.71 | 0.88 | 0.71 | 0.88 | 1.00 | 0.71 | 0.88 |
| A_d09f8d1ef8 | ω rms, all modes (cm⁻¹) | 18.75 | 7.31 | 39.65 | 7.73 | 4.13 | 5.89 | 4.30 | 5.88 | 17.45 | 4.07 | 4.13 |
| A_d09f8d1ef8 | ΔH residual | 1.00 | 0.70 | 2.38 | 0.81 | 0.43 | 0.61 | 0.46 | 0.57 | 0.92 | 0.45 | 0.50 |
| A_d09f8d1ef8 | ω rms ring-ip (cm⁻¹) | 15.57 | 7.37 | 29.04 | 5.22 | 2.64 | 2.93 | 2.64 | 2.90 | 15.46 | 2.64 | 3.01 |
| A_d09f8d1ef8 | ω rms CH-stretch (cm⁻¹) | 34.22 | 7.15 | 77.75 | 7.13 | 4.29 | 2.39 | 4.29 | 2.39 | 34.22 | 4.29 | 2.39 |
| A_d09f8d1ef8 | ω rms CH-oop (cm⁻¹) | 10.82 | 10.07 | 31.60 | 9.40 | 6.31 | 8.38 | 6.99 | 8.31 | 4.50 | 5.17 | 5.17 |
| A_d09f8d1ef8 | ω rms other (cm⁻¹) | 13.72 | 5.26 | 21.97 | 9.70 | 4.25 | 8.20 | 4.27 | 8.24 | 9.07 | 4.84 | 5.38 |
| A_d09f8d1ef8 | spectrum overlap (CC APT) | 0.476 | 0.679 | 0.216 | 0.752 | 0.897 | 0.903 | 0.896 | 0.903 | 0.484 | 0.881 | 0.950 |
| A_d09f8d1ef8 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.173 | 0.166 | 0.146 | 0.165 | 0.187 | 0.160 | 0.176 | 0.158 | 0.173 | 0.176 | 0.158 |
| A_d09f8d1ef8 | intensity rel. rms (CC APT) | 0.181 | 0.166 | 0.416 | 0.429 | 0.278 | 0.419 | 0.271 | 0.424 | 0.354 | 0.271 | 0.158 |
| A_d09f8d1ef8 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.2, CH-oop 6.9, ring-ip 2.6, other 4.0 |
| A_d9139359ab | ring-coupling ratio | 1.00 | 1.03 | 3.29 | 2.60 | 1.02 | 2.18 | 1.02 | 2.18 | 1.00 | 1.02 | 2.18 |
| A_d9139359ab | ω rms, all modes (cm⁻¹) | 23.67 | 9.64 | 40.62 | 12.29 | 9.86 | 9.82 | 9.82 | 9.76 | 20.95 | 8.71 | 7.58 |
| A_d9139359ab | ΔH residual | 1.00 | 0.72 | 2.42 | 1.57 | 0.71 | 1.29 | 0.72 | 1.29 | 0.93 | 0.70 | 1.26 |
| A_d9139359ab | ω rms ring-ip (cm⁻¹) | 22.36 | 9.80 | 31.76 | 11.12 | 8.81 | 9.01 | 8.81 | 8.98 | 22.23 | 8.81 | 10.04 |
| A_d9139359ab | ω rms CH-stretch (cm⁻¹) | 33.25 | 7.64 | 76.35 | 9.55 | 7.22 | 1.64 | 7.22 | 1.64 | 33.25 | 7.22 | 1.64 |
| A_d9139359ab | ω rms CH-oop (cm⁻¹) | 23.10 | 9.90 | 27.86 | 11.80 | 12.83 | 9.69 | 12.67 | 9.57 | 11.67 | 11.09 | 5.39 |
| A_d9139359ab | ω rms other (cm⁻¹) | 18.08 | 10.31 | 23.90 | 15.29 | 10.28 | 13.32 | 10.28 | 13.24 | 12.71 | 7.43 | 7.11 |
| A_d9139359ab | spectrum overlap (CC APT) | 0.557 | 0.631 | 0.188 | 0.774 | 0.855 | 0.817 | 0.855 | 0.816 | 0.636 | 0.850 | 0.827 |
| A_d9139359ab | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.164 | 0.140 | 0.328 | 0.274 | 0.217 | 0.267 | 0.219 | 0.268 | 0.164 | 0.219 | 0.268 |
| A_d9139359ab | intensity rel. rms (CC APT) | 1.699 | 1.637 | 1.440 | 1.469 | 0.217 | 2.184 | 0.219 | 2.197 | 1.704 | 0.219 | 2.197 |
| A_d9139359ab | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.9, CH-oop 12.6, ring-ip 9.1, other 10.0 |
| A_ff98e1160d | ring-coupling ratio | 1.00 | 0.98 | 2.19 | 1.28 | 0.42 | 0.80 | 0.42 | 0.80 | 1.00 | 0.42 | 0.80 |
| A_ff98e1160d | ω rms, all modes (cm⁻¹) | 18.42 | 7.33 | 39.57 | 8.03 | 3.78 | 5.91 | 3.73 | 5.94 | 17.13 | 4.20 | 4.54 |
| A_ff98e1160d | ΔH residual | 1.00 | 0.67 | 2.46 | 0.80 | 0.35 | 0.57 | 0.36 | 0.52 | 0.93 | 0.35 | 0.46 |
| A_ff98e1160d | ω rms ring-ip (cm⁻¹) | 15.03 | 7.31 | 28.33 | 5.25 | 1.65 | 2.67 | 1.65 | 2.67 | 14.96 | 1.65 | 2.67 |
| A_ff98e1160d | ω rms CH-stretch (cm⁻¹) | 34.15 | 7.24 | 77.66 | 7.44 | 3.16 | 2.61 | 3.16 | 2.61 | 34.15 | 3.16 | 2.61 |
| A_ff98e1160d | ω rms CH-oop (cm⁻¹) | 11.81 | 9.61 | 32.47 | 9.85 | 7.53 | 8.80 | 7.38 | 8.88 | 8.24 | 8.30 | 8.30 |
| A_ff98e1160d | ω rms other (cm⁻¹) | 12.64 | 5.40 | 21.14 | 10.17 | 2.45 | 8.05 | 2.43 | 8.07 | 6.29 | 3.23 | 4.08 |
| A_ff98e1160d | spectrum overlap (CC APT) | 0.670 | 0.641 | 0.288 | 0.723 | 0.957 | 0.817 | 0.960 | 0.819 | 0.627 | 0.875 | 0.874 |
| A_ff98e1160d | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.151 | 0.150 | 0.173 | 0.150 | 0.236 | 0.235 | 0.187 | 0.157 | 0.151 | 0.187 | 0.157 |
| A_ff98e1160d | intensity rel. rms (CC APT) | 3.025 | 3.019 | 0.182 | 2.969 | 0.236 | 2.895 | 0.187 | 3.026 | 3.043 | 0.195 | 0.167 |
| A_ff98e1160d | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.9, CH-oop 8.1, ring-ip 1.7, other 2.4 |

807 s.
