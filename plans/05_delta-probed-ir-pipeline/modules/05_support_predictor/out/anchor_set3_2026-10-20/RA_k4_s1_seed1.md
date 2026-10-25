# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 19:09)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.33 | 0.50 | 0.93 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.65 | 42.18 | 11.80 | 6.25 | 9.66 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 2.22 | 0.88 | 0.44 | 0.71 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.33 | 29.12 | 6.70 | 1.84 | 3.52 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.13 | 76.51 | 9.40 | 1.40 | 1.27 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.42 | 42.59 | 19.95 | 12.43 | 18.13 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.65 | 25.04 | 11.92 | 6.36 | 10.75 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.4, CH-oop 11.9, ring-ip 1.9, other 6.1 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.18 | 0.94 | 0.98 | 0.66 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 45.31 | 24.24 | 22.44 | 24.13 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.82 | 0.72 | 0.88 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.93 | 29.08 | 3.88 | 3.40 | 2.44 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.90 | 78.96 | 7.46 | 2.41 | 4.48 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.45 | 31.96 | 9.64 | 9.27 | 9.95 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.21 | 45.05 | 42.86 | 39.92 | 42.95 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.653 | 0.140 | 0.438 | 0.533 | 0.486 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.264 | 0.380 | 0.563 | 0.323 | 0.535 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.380 | 0.563 | 0.323 | 0.535 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.4, CH-oop 9.7, ring-ip 3.3, other 43.2 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 2.25 | 1.03 | 0.85 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.53 | 40.54 | 9.30 | 5.90 | 7.54 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.58 | 0.40 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.69 | 28.00 | 6.33 | 2.83 | 4.47 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.39 | 78.00 | 7.61 | 3.86 | 3.77 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.58 | 20.43 | 14.43 | 10.86 | 12.86 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.12 | 22.55 | 8.92 | 3.92 | 7.60 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.663 | 0.193 | 0.667 | 0.783 | 0.712 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.317 | 0.323 | 0.115 | 0.304 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.323 | 0.190 | 0.304 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.9, CH-oop 10.9, ring-ip 2.7, other 3.8 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 1.70 | 0.60 | 0.24 | 0.44 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.75 | 43.50 | 8.33 | 7.53 | 8.31 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.22 | 0.67 | 0.35 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.04 | 27.73 | 5.55 | 2.99 | 4.78 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.76 | 81.84 | 4.02 | 5.29 | 6.68 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.56 | 26.62 | 14.62 | 11.29 | 14.59 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.89 | 21.58 | 7.78 | 11.43 | 6.80 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.349 | 0.527 | 0.337 | 0.808 | 0.321 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.021 | 0.011 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.2, CH-oop 11.1, ring-ip 3.0, other 11.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 2.03 | 1.47 | 0.72 | 1.19 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 41.65 | 13.11 | 6.53 | 10.78 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.75 | 2.18 | 1.01 | 0.51 | 0.82 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.01 | 30.61 | 10.45 | 4.70 | 7.35 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.92 | 76.20 | 9.72 | 4.35 | 1.35 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.46 | 46.40 | 22.29 | 12.50 | 20.48 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.39 | 23.75 | 11.31 | 4.90 | 9.90 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.4, CH-oop 15.7, ring-ip 4.8, other 4.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.24 | 2.09 | 1.06 | 0.63 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.52 | 39.69 | 7.86 | 4.21 | 5.72 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.34 | 0.60 | 0.27 | 0.47 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.67 | 28.74 | 5.12 | 1.17 | 3.23 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.38 | 77.64 | 8.70 | 6.60 | 2.46 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.64 | 26.70 | 10.79 | 7.00 | 9.26 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.41 | 21.32 | 8.50 | 2.56 | 7.06 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.687 | 0.197 | 0.691 | 0.943 | 0.700 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.194 | 0.202 | 0.051 | 0.172 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.276 | 0.194 | 0.326 | 0.266 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.6, CH-oop 7.3, ring-ip 1.5, other 2.6 |

890 s.
