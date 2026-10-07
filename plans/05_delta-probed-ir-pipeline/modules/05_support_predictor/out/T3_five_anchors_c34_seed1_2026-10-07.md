# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 03:36)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.20 | 1.00 | 0.25 | 0.25 | 0.22 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 35.07 | 61.28 | 30.31 | 30.21 | 30.07 |
| A_01f3186607 | ΔH residual | 1.00 | 0.58 | 0.94 | 0.56 | 0.50 | 0.55 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 8.48 | 20.71 | 5.82 | 5.43 | 5.35 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.00 | 54.60 | 5.35 | 9.81 | 2.77 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 53.69 | 94.10 | 45.03 | 49.34 | 44.97 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 49.31 | 74.57 | 43.94 | 40.56 | 43.61 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.1, CH-oop 51.1, ring-ip 5.2, other 37.9 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.90 | 0.28 | 0.29 | 0.26 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 15.28 | 51.29 | 11.85 | 6.19 | 11.57 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.29 | 0.86 | 0.29 | 0.27 | 0.28 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.96 | 30.84 | 7.45 | 5.18 | 6.96 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.79 | 55.28 | 3.81 | 5.14 | 2.62 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 16.08 | 69.59 | 7.61 | 8.81 | 7.57 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 30.35 | 61.79 | 26.01 | 5.39 | 25.75 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.4, CH-oop 10.3, ring-ip 5.9, other 4.9 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.10 | 0.95 | 0.14 | 0.07 | 0.11 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 24.06 | 56.81 | 19.43 | 14.19 | 19.02 |
| A_8448043181 | ΔH residual | 1.00 | 0.39 | 0.92 | 0.38 | 0.20 | 0.36 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.12 | 24.46 | 5.45 | 5.54 | 4.83 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.26 | 56.08 | 6.27 | 5.97 | 2.92 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 37.61 | 89.28 | 24.81 | 25.02 | 25.09 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 39.39 | 66.86 | 37.45 | 18.31 | 36.68 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.2, CH-oop 27.1, ring-ip 5.4, other 12.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.27 | 1.02 | 0.31 | 0.25 | 0.29 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 43.91 | 10.78 | 33.93 | 18.68 | 23.59 | 18.64 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.33 | 0.85 | 0.31 | 0.36 | 0.29 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 28.49 | 10.71 | 22.90 | 7.06 | 6.98 | 6.64 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 96.94 | 7.61 | 53.65 | 4.27 | 5.88 | 2.76 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.08 | 17.81 | 45.87 | 36.81 | 39.79 | 37.13 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 17.82 | 7.30 | 24.83 | 19.20 | 29.69 | 19.07 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.4, CH-oop 44.5, ring-ip 6.5, other 27.4 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 1.01 | 0.21 | 0.26 | 0.18 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 15.69 | 49.31 | 12.34 | 7.04 | 12.05 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.37 | 0.89 | 0.34 | 0.36 | 0.34 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.62 | 26.61 | 5.19 | 4.09 | 5.34 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.75 | 55.67 | 4.78 | 4.49 | 0.89 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 22.70 | 80.09 | 11.72 | 12.98 | 12.41 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 21.82 | 45.93 | 20.74 | 6.55 | 20.13 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.8, CH-oop 13.4, ring-ip 8.3, other 6.1 |

269 s.
