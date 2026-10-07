# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 03:40)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.20 | 0.99 | 0.24 | 0.15 | 0.21 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 35.07 | 61.33 | 30.11 | 28.92 | 29.99 |
| A_01f3186607 | ΔH residual | 1.00 | 0.58 | 0.95 | 0.56 | 0.49 | 0.55 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 8.48 | 20.26 | 5.79 | 6.16 | 5.49 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.00 | 54.07 | 3.95 | 7.63 | 2.20 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 53.69 | 94.05 | 43.84 | 44.78 | 43.98 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 49.31 | 75.13 | 44.25 | 40.49 | 44.00 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.8, CH-oop 45.2, ring-ip 6.6, other 37.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.89 | 0.26 | 0.28 | 0.24 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 15.28 | 51.72 | 11.60 | 8.95 | 11.51 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.29 | 0.89 | 0.30 | 0.20 | 0.28 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.96 | 30.79 | 6.78 | 5.64 | 6.35 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.79 | 54.07 | 1.50 | 2.46 | 1.51 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 16.08 | 71.97 | 9.13 | 9.41 | 9.42 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 30.35 | 61.56 | 25.35 | 17.44 | 25.25 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 13.6, ring-ip 6.4, other 13.2 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.10 | 0.91 | 0.11 | 0.17 | 0.08 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 24.06 | 57.73 | 20.80 | 19.11 | 20.53 |
| A_8448043181 | ΔH residual | 1.00 | 0.39 | 0.93 | 0.40 | 0.28 | 0.38 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.12 | 22.92 | 6.49 | 10.08 | 5.75 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.26 | 55.61 | 5.21 | 1.99 | 1.79 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 37.61 | 92.06 | 27.31 | 33.70 | 27.91 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 39.39 | 68.92 | 39.48 | 23.67 | 38.78 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 33.2, ring-ip 9.6, other 20.4 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.27 | 1.01 | 0.31 | 0.20 | 0.28 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 43.91 | 10.78 | 33.91 | 18.79 | 23.57 | 18.81 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.33 | 0.86 | 0.32 | 0.31 | 0.29 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 28.49 | 10.71 | 22.34 | 6.97 | 7.59 | 6.70 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 96.94 | 7.61 | 52.96 | 2.68 | 3.21 | 1.76 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.08 | 17.81 | 45.80 | 37.36 | 42.60 | 37.74 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 17.82 | 7.30 | 26.03 | 19.19 | 27.82 | 19.08 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.5, CH-oop 51.1, ring-ip 7.6, other 23.1 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 0.98 | 0.21 | 0.17 | 0.18 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 15.69 | 49.52 | 12.18 | 10.06 | 12.05 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.37 | 0.90 | 0.35 | 0.29 | 0.34 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.62 | 26.21 | 4.88 | 5.12 | 5.01 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.75 | 55.48 | 3.89 | 2.57 | 1.06 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 22.70 | 81.06 | 11.43 | 19.90 | 12.18 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 21.82 | 46.19 | 20.73 | 9.40 | 20.33 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.7, CH-oop 19.9, ring-ip 5.7, other 8.5 |

272 s.
