# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 16:59)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 2.37 | 1.30 | 0.50 | 0.87 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.81 | 42.40 | 11.86 | 6.71 | 9.86 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.23 | 0.88 | 0.46 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.80 | 28.95 | 6.66 | 1.93 | 3.35 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.54 | 76.46 | 7.92 | 3.81 | 1.36 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.26 | 43.01 | 19.64 | 12.96 | 17.62 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 26.25 | 13.00 | 6.72 | 11.86 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.7, CH-oop 12.3, ring-ip 1.9, other 6.5 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.14 | 0.92 | 0.67 | 0.62 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 44.91 | 22.40 | 20.73 | 20.22 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.75 | 0.91 | 0.66 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.24 | 28.99 | 3.93 | 2.68 | 2.49 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.18 | 77.94 | 6.98 | 1.54 | 1.85 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.71 | 31.04 | 10.15 | 7.04 | 9.89 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 45.07 | 39.39 | 37.13 | 35.79 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.135 | 0.516 | 0.714 | 0.560 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.405 | 0.536 | 0.334 | 0.492 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.298 | 0.405 | 0.536 | 0.334 | 0.492 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.3, CH-oop 7.3, ring-ip 2.6, other 38.5 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.16 | 2.20 | 1.00 | 0.79 | 0.83 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 40.59 | 9.35 | 4.94 | 7.64 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 2.56 | 0.62 | 0.33 | 0.44 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 28.33 | 7.14 | 2.55 | 5.71 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.78 | 77.60 | 6.33 | 4.17 | 3.30 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.08 | 21.56 | 14.71 | 8.63 | 12.50 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.14 | 7.91 | 3.43 | 6.92 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.646 | 0.184 | 0.671 | 0.781 | 0.744 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.326 | 0.328 | 0.163 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.354 | 0.328 | 0.219 | 0.340 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.2, CH-oop 8.9, ring-ip 2.4, other 3.3 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 1.79 | 0.65 | 0.43 | 0.65 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.97 | 42.93 | 8.07 | 6.34 | 8.05 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.70 | 0.40 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.21 | 26.68 | 7.03 | 3.04 | 6.33 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.08 | 80.99 | 3.37 | 6.44 | 4.36 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.97 | 27.02 | 12.89 | 10.47 | 13.41 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.41 | 7.01 | 5.94 | 6.74 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.340 | 0.601 | 0.350 | 0.374 | 0.386 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.022 | 0.012 | 0.004 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.4, CH-oop 12.6, ring-ip 3.0, other 11.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.07 | 1.47 | 0.60 | 1.09 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.05 | 41.92 | 12.92 | 7.81 | 10.51 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 2.20 | 1.03 | 0.51 | 0.82 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 30.42 | 10.50 | 3.65 | 6.07 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.35 | 76.74 | 7.53 | 2.23 | 2.08 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.07 | 46.64 | 21.66 | 15.34 | 19.94 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.24 | 24.41 | 11.89 | 7.71 | 10.41 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.3, CH-oop 17.6, ring-ip 3.7, other 7.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.16 | 1.11 | 0.87 | 0.75 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.83 | 39.22 | 7.73 | 4.47 | 5.62 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 2.31 | 0.61 | 0.30 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.08 | 27.91 | 4.89 | 3.14 | 3.23 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.77 | 76.57 | 8.38 | 4.59 | 1.41 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.17 | 27.41 | 10.40 | 7.13 | 8.77 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.61 | 8.77 | 3.91 | 7.32 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.174 | 0.706 | 0.781 | 0.716 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.115 | 0.202 | 0.213 | 0.201 | 0.181 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.280 | 0.202 | 0.326 | 0.492 | 0.304 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.0, CH-oop 7.4, ring-ip 3.1, other 3.9 |

888 s.
