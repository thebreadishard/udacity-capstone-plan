# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 18:06)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.32 | 0.63 | 0.95 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.90 | 42.18 | 11.97 | 6.44 | 9.94 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.22 | 0.88 | 0.45 | 0.72 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.62 | 29.12 | 6.77 | 2.40 | 3.68 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.31 | 76.51 | 8.68 | 1.78 | 1.19 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.33 | 42.59 | 20.57 | 13.17 | 18.68 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.60 | 25.04 | 12.14 | 5.84 | 10.99 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.8, CH-oop 12.8, ring-ip 2.4, other 5.6 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.18 | 0.91 | 0.97 | 0.65 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.31 | 22.05 | 20.69 | 21.97 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.78 | 0.77 | 0.84 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.83 | 29.08 | 3.92 | 3.62 | 2.31 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.74 | 78.96 | 6.67 | 2.10 | 4.03 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 31.96 | 9.78 | 9.09 | 9.91 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.07 | 45.05 | 38.81 | 36.68 | 38.98 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.648 | 0.140 | 0.510 | 0.602 | 0.565 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.263 | 0.380 | 0.508 | 0.250 | 0.476 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.380 | 0.508 | 0.250 | 0.477 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.1, CH-oop 9.5, ring-ip 3.5, other 38.8 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.11 | 2.25 | 1.04 | 0.88 | 0.92 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.89 | 40.54 | 9.20 | 7.01 | 7.59 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.59 | 0.44 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.91 | 28.00 | 6.48 | 3.22 | 4.65 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.27 | 78.00 | 6.71 | 4.95 | 3.41 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.11 | 20.43 | 14.36 | 12.95 | 12.93 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.95 | 22.55 | 8.96 | 4.30 | 7.66 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.639 | 0.193 | 0.684 | 0.749 | 0.719 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.317 | 0.323 | 0.134 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.328 | 0.323 | 0.202 | 0.306 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.1, CH-oop 13.1, ring-ip 2.9, other 4.2 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.70 | 0.61 | 0.22 | 0.47 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.98 | 43.50 | 8.13 | 7.64 | 8.24 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.22 | 0.68 | 0.35 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.24 | 27.73 | 5.45 | 3.10 | 4.68 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.52 | 81.84 | 3.19 | 5.57 | 6.38 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.92 | 26.62 | 14.20 | 11.23 | 14.49 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.58 | 8.06 | 11.68 | 7.07 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.331 | 0.527 | 0.356 | 0.830 | 0.329 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.021 | 0.012 | 0.003 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.003 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.5, CH-oop 11.0, ring-ip 3.1, other 11.3 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.03 | 1.46 | 0.70 | 1.20 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.26 | 41.65 | 13.29 | 6.90 | 11.10 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 2.18 | 1.02 | 0.49 | 0.84 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.30 | 30.61 | 10.57 | 4.79 | 7.61 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.31 | 76.20 | 8.89 | 6.07 | 1.95 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.35 | 46.40 | 22.92 | 13.03 | 20.99 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.35 | 23.75 | 11.55 | 4.87 | 10.22 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.1, CH-oop 15.4, ring-ip 4.9, other 4.6 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.09 | 1.04 | 0.63 | 0.73 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.86 | 39.69 | 7.74 | 3.89 | 5.72 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.34 | 0.61 | 0.25 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.97 | 28.74 | 5.13 | 1.24 | 3.14 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.32 | 77.64 | 7.84 | 5.23 | 2.20 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.13 | 26.70 | 10.54 | 6.81 | 9.08 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.30 | 21.32 | 8.78 | 2.92 | 7.30 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.686 | 0.197 | 0.690 | 0.931 | 0.714 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.194 | 0.201 | 0.054 | 0.173 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.194 | 0.326 | 0.267 | 0.304 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.2, CH-oop 7.1, ring-ip 1.4, other 2.9 |

684 s.
