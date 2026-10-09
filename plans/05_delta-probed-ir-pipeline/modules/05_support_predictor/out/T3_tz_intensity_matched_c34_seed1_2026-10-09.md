# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-09 13:39)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.34 | 1.42 | 1.04 | 1.14 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 10.00 | 42.18 | 12.55 | 8.12 | 10.63 |
| A_01f3186607 | ΔH residual | 1.00 | 0.75 | 2.22 | 0.89 | 0.55 | 0.75 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.52 | 29.12 | 6.84 | 3.23 | 4.20 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 13.31 | 76.51 | 9.25 | 6.24 | 2.07 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.55 | 42.59 | 21.82 | 16.12 | 20.17 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.61 | 25.04 | 12.62 | 6.46 | 11.40 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.1, CH-oop 15.7, ring-ip 3.3, other 6.2 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.18 | 0.90 | 0.97 | 0.66 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.08 | 45.31 | 21.22 | 19.29 | 20.93 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.69 | 0.77 | 0.79 | 0.81 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.87 | 29.08 | 4.06 | 2.90 | 2.37 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.35 | 78.96 | 7.02 | 3.67 | 3.03 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.39 | 31.96 | 10.47 | 9.60 | 10.20 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.03 | 45.05 | 37.09 | 34.00 | 37.03 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.6, CH-oop 9.9, ring-ip 2.8, other 35.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.04 | 2.25 | 1.03 | 0.95 | 0.93 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.35 | 40.54 | 8.73 | 7.01 | 7.10 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.55 | 2.56 | 0.59 | 0.47 | 0.43 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.17 | 28.00 | 6.36 | 3.76 | 4.55 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 9.48 | 78.00 | 7.03 | 2.50 | 2.83 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 20.43 | 12.65 | 13.30 | 11.69 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.55 | 9.58 | 4.05 | 7.95 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 13.8, ring-ip 2.8, other 3.9 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.99 | 1.70 | 0.60 | 0.16 | 0.46 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.35 | 43.50 | 7.86 | 7.14 | 7.85 |
| A_8448043181 | ΔH residual | 1.00 | 0.57 | 2.22 | 0.69 | 0.34 | 0.61 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.74 | 27.73 | 5.05 | 3.05 | 4.36 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 6.60 | 81.84 | 3.60 | 4.77 | 5.25 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.71 | 26.62 | 13.35 | 9.76 | 13.89 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.74 | 21.58 | 8.67 | 11.82 | 7.44 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.269 | 0.527 | 0.356 | 0.856 | 0.355 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.005 | 0.021 | 0.011 | 0.002 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.002 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 9.6, ring-ip 3.0, other 11.4 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 1.00 | 2.03 | 1.47 | 0.91 | 1.28 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 10.65 | 41.65 | 13.83 | 7.28 | 11.91 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.82 | 2.18 | 1.03 | 0.54 | 0.88 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.25 | 30.61 | 10.56 | 5.75 | 8.25 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 15.01 | 76.20 | 9.40 | 6.03 | 3.72 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 14.03 | 46.40 | 24.24 | 11.51 | 22.38 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.62 | 23.75 | 12.03 | 6.78 | 10.83 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.9, CH-oop 15.2, ring-ip 5.9, other 6.6 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 2.09 | 1.03 | 0.72 | 0.73 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.52 | 39.69 | 7.96 | 3.84 | 5.76 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.52 | 2.34 | 0.62 | 0.27 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.76 | 28.74 | 5.09 | 1.63 | 3.19 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 10.69 | 77.64 | 8.30 | 5.18 | 1.53 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 26.70 | 10.36 | 6.64 | 8.94 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.32 | 9.43 | 2.66 | 7.59 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.1, CH-oop 6.8, ring-ip 1.8, other 2.7 |

444 s.
