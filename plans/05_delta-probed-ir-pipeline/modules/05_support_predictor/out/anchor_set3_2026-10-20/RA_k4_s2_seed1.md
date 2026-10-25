# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 19:25)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.31 | 0.57 | 0.87 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.86 | 42.18 | 11.65 | 6.69 | 9.63 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.22 | 0.87 | 0.46 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.78 | 29.12 | 6.59 | 1.95 | 3.26 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.83 | 76.51 | 8.55 | 3.33 | 1.28 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 42.59 | 19.95 | 12.85 | 18.04 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 25.04 | 11.85 | 6.92 | 10.82 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 12.5, ring-ip 2.0, other 6.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.18 | 0.94 | 0.85 | 0.65 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.31 | 23.46 | 22.37 | 23.51 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.81 | 0.81 | 0.88 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 29.08 | 3.70 | 3.00 | 2.53 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.38 | 78.96 | 6.61 | 1.67 | 4.82 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 31.96 | 9.52 | 9.41 | 9.89 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.86 | 45.05 | 41.52 | 39.83 | 41.79 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.644 | 0.140 | 0.469 | 0.535 | 0.513 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.380 | 0.545 | 0.316 | 0.517 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.297 | 0.380 | 0.545 | 0.316 | 0.517 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 9.8, ring-ip 2.9, other 42.4 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 2.25 | 1.04 | 0.78 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.74 | 40.54 | 9.57 | 6.79 | 7.88 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.61 | 0.42 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.73 | 28.00 | 7.11 | 2.35 | 5.05 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.04 | 78.00 | 6.79 | 4.70 | 4.08 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.94 | 20.43 | 14.90 | 12.78 | 13.32 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.01 | 22.55 | 8.71 | 4.69 | 7.43 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.643 | 0.193 | 0.677 | 0.748 | 0.704 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.317 | 0.324 | 0.129 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.328 | 0.324 | 0.197 | 0.306 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.8, CH-oop 12.7, ring-ip 2.2, other 4.5 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.12 | 1.70 | 0.60 | 0.29 | 0.46 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.92 | 43.50 | 8.43 | 7.66 | 8.51 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.22 | 0.68 | 0.35 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.15 | 27.73 | 6.15 | 2.59 | 5.18 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.31 | 81.84 | 3.20 | 6.70 | 7.13 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.86 | 26.62 | 14.61 | 11.19 | 14.66 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.76 | 21.58 | 7.68 | 11.44 | 6.77 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.336 | 0.527 | 0.352 | 0.753 | 0.312 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.021 | 0.011 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.6, CH-oop 11.0, ring-ip 2.6, other 11.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.03 | 1.44 | 0.57 | 1.03 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 41.65 | 12.88 | 6.48 | 10.44 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.18 | 0.99 | 0.43 | 0.78 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 30.61 | 10.06 | 3.73 | 6.00 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.65 | 76.20 | 8.78 | 3.68 | 1.42 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.16 | 46.40 | 22.26 | 13.12 | 20.31 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.28 | 23.75 | 11.29 | 5.15 | 9.97 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.8, CH-oop 16.3, ring-ip 3.7, other 4.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.19 | 2.09 | 1.09 | 0.59 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.81 | 39.69 | 7.70 | 4.21 | 5.79 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.34 | 0.60 | 0.28 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.06 | 28.74 | 5.05 | 1.39 | 3.25 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.05 | 77.64 | 7.89 | 6.84 | 2.81 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.03 | 26.70 | 10.86 | 6.54 | 9.31 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.35 | 21.32 | 8.46 | 2.79 | 7.11 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.197 | 0.682 | 0.927 | 0.699 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.194 | 0.203 | 0.122 | 0.175 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.194 | 0.325 | 0.300 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.2, CH-oop 6.8, ring-ip 1.6, other 2.8 |

901 s.
