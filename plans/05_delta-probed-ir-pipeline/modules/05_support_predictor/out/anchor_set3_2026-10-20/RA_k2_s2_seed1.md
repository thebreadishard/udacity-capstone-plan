# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 18:18)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.34 | 1.34 | 0.52 | 0.98 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.26 | 42.18 | 12.24 | 7.27 | 10.06 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.22 | 0.89 | 0.48 | 0.73 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.83 | 29.12 | 6.71 | 1.87 | 3.71 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.54 | 76.51 | 9.91 | 3.40 | 1.20 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.60 | 42.59 | 20.90 | 14.91 | 19.12 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.67 | 25.04 | 12.24 | 6.58 | 10.94 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.3, CH-oop 14.1, ring-ip 1.9, other 6.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.18 | 0.93 | 1.04 | 0.66 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 45.31 | 23.28 | 19.99 | 22.97 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.80 | 0.65 | 0.85 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.97 | 29.08 | 3.92 | 3.49 | 2.37 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.45 | 78.96 | 7.85 | 4.03 | 3.86 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.25 | 31.96 | 10.04 | 9.67 | 10.06 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.23 | 45.05 | 40.97 | 35.22 | 40.82 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.658 | 0.140 | 0.455 | 0.570 | 0.520 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.265 | 0.380 | 0.534 | 0.288 | 0.500 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.288 | 0.380 | 0.534 | 0.288 | 0.500 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.0, CH-oop 10.0, ring-ip 3.4, other 36.9 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.08 | 2.25 | 1.02 | 0.89 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.69 | 40.54 | 8.99 | 5.78 | 7.14 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.53 | 2.56 | 0.58 | 0.42 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 28.00 | 6.21 | 2.85 | 4.34 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.38 | 78.00 | 8.01 | 3.18 | 3.24 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.34 | 20.43 | 13.22 | 10.84 | 11.95 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.17 | 22.55 | 9.36 | 3.47 | 7.78 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.624 | 0.193 | 0.672 | 0.777 | 0.728 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.317 | 0.323 | 0.083 | 0.301 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.323 | 0.173 | 0.301 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.2, CH-oop 11.0, ring-ip 2.3, other 3.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.06 | 1.70 | 0.60 | 0.22 | 0.43 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.87 | 43.50 | 8.14 | 6.85 | 8.08 |
| A_8448043181 | ΔH residual | 1.00 | 0.56 | 2.22 | 0.68 | 0.33 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.32 | 27.73 | 5.30 | 2.90 | 4.59 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.55 | 81.84 | 4.48 | 3.71 | 5.89 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.32 | 26.62 | 13.92 | 9.96 | 14.30 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.98 | 21.58 | 8.22 | 11.15 | 7.05 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.527 | 0.333 | 0.875 | 0.340 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.021 | 0.011 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.7, CH-oop 9.8, ring-ip 2.9, other 10.7 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.96 | 2.03 | 1.48 | 0.78 | 1.23 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.74 | 41.65 | 13.54 | 6.67 | 11.26 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.18 | 1.02 | 0.52 | 0.85 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.52 | 30.61 | 10.47 | 4.50 | 7.68 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.63 | 76.20 | 10.22 | 2.48 | 2.33 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.93 | 46.40 | 23.30 | 11.83 | 21.42 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.58 | 23.75 | 11.68 | 6.71 | 10.24 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.6, CH-oop 15.3, ring-ip 4.6, other 6.5 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 2.09 | 1.05 | 0.68 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.82 | 39.69 | 8.01 | 4.27 | 5.70 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 2.34 | 0.61 | 0.27 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 28.74 | 5.08 | 1.51 | 3.24 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.47 | 77.64 | 9.20 | 6.55 | 1.91 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.33 | 26.70 | 10.47 | 7.15 | 9.04 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 21.32 | 8.97 | 2.50 | 7.25 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.682 | 0.197 | 0.702 | 0.933 | 0.709 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.109 | 0.194 | 0.201 | 0.060 | 0.170 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.194 | 0.327 | 0.252 | 0.302 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.5, CH-oop 7.3, ring-ip 1.8, other 2.5 |

648 s.
