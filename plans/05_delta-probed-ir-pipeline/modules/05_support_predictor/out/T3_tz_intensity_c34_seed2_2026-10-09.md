# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-09 13:22)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.35 | 1.36 | 0.72 | 1.07 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 10.00 | 42.29 | 12.29 | 6.72 | 10.52 |
| A_01f3186607 | ΔH residual | 1.00 | 0.75 | 2.21 | 0.89 | 0.47 | 0.74 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.52 | 28.43 | 6.71 | 4.04 | 4.38 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 13.31 | 77.02 | 8.12 | 7.93 | 2.75 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.55 | 43.03 | 21.03 | 11.57 | 19.63 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.61 | 25.37 | 13.01 | 4.64 | 11.40 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.6, CH-oop 11.3, ring-ip 4.2, other 4.5 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.17 | 0.89 | 0.75 | 0.57 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.08 | 45.03 | 20.47 | 14.33 | 19.18 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.73 | 0.72 | 0.69 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.87 | 28.39 | 3.99 | 3.58 | 2.58 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.35 | 78.77 | 6.46 | 2.12 | 1.50 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.39 | 30.53 | 9.58 | 6.73 | 9.39 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.03 | 45.41 | 35.89 | 25.16 | 33.93 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 7.4, ring-ip 3.5, other 25.4 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.04 | 2.27 | 0.94 | 0.68 | 0.80 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.35 | 41.06 | 7.90 | 4.58 | 6.51 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.55 | 2.56 | 0.59 | 0.31 | 0.41 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.17 | 27.44 | 5.92 | 2.77 | 4.11 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 9.48 | 79.15 | 5.02 | 2.52 | 1.05 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 22.78 | 11.28 | 8.04 | 10.54 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.59 | 9.69 | 3.73 | 8.22 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.4, CH-oop 8.1, ring-ip 2.7, other 3.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.99 | 1.80 | 0.56 | 0.31 | 0.48 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.35 | 43.42 | 6.70 | 8.86 | 7.21 |
| A_8448043181 | ΔH residual | 1.00 | 0.57 | 2.18 | 0.72 | 0.49 | 0.64 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.74 | 25.95 | 5.15 | 4.87 | 4.91 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 6.60 | 82.30 | 2.82 | 11.19 | 6.00 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.71 | 28.29 | 9.71 | 11.03 | 11.39 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.74 | 21.75 | 8.79 | 10.63 | 7.07 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.269 | 0.556 | 0.361 | 0.554 | 0.354 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 11.1, CH-oop 13.5, ring-ip 4.7, other 12.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 1.00 | 2.04 | 1.45 | 0.85 | 1.24 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 10.65 | 41.91 | 13.61 | 8.41 | 11.83 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.82 | 2.19 | 1.04 | 0.62 | 0.89 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.25 | 30.05 | 10.62 | 3.73 | 8.49 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 15.01 | 76.88 | 8.02 | 5.74 | 2.14 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 14.03 | 46.46 | 22.62 | 15.56 | 21.19 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.62 | 24.82 | 13.07 | 8.48 | 11.62 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.7, CH-oop 16.4, ring-ip 3.7, other 8.3 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 2.19 | 1.05 | 0.65 | 0.72 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.52 | 39.49 | 7.96 | 3.42 | 5.76 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.52 | 2.31 | 0.63 | 0.23 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.76 | 27.32 | 4.74 | 1.78 | 2.95 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 10.69 | 77.83 | 7.65 | 2.41 | 1.25 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 27.62 | 10.93 | 6.96 | 9.20 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.61 | 9.61 | 2.28 | 7.59 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.4, CH-oop 7.2, ring-ip 2.1, other 2.3 |

322 s.
