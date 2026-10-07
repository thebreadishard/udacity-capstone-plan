# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 03:31)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.20 | 1.01 | 0.25 | 0.19 | 0.23 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 35.07 | 61.68 | 30.76 | 31.70 | 30.68 |
| A_01f3186607 | ΔH residual | 1.00 | 0.58 | 0.95 | 0.57 | 0.54 | 0.56 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 8.48 | 20.36 | 5.89 | 7.79 | 5.49 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.00 | 54.64 | 5.26 | 7.42 | 3.18 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 53.69 | 94.29 | 45.20 | 49.44 | 45.45 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 49.31 | 75.66 | 44.91 | 44.03 | 44.76 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.7, CH-oop 50.6, ring-ip 8.7, other 39.9 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.91 | 0.27 | 0.26 | 0.25 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 15.28 | 51.74 | 11.57 | 7.73 | 11.35 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.29 | 0.88 | 0.30 | 0.21 | 0.28 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.96 | 30.90 | 7.16 | 4.90 | 6.80 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.79 | 55.65 | 3.69 | 2.43 | 1.91 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 16.08 | 70.86 | 8.17 | 4.82 | 8.37 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 30.35 | 61.66 | 25.15 | 16.99 | 24.92 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 8.6, ring-ip 5.4, other 12.7 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.10 | 0.92 | 0.13 | 0.05 | 0.11 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 24.06 | 57.16 | 20.08 | 16.88 | 19.85 |
| A_8448043181 | ΔH residual | 1.00 | 0.39 | 0.92 | 0.39 | 0.27 | 0.38 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.12 | 22.69 | 6.19 | 3.96 | 5.69 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.26 | 56.93 | 6.95 | 9.85 | 4.14 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 37.61 | 90.65 | 26.57 | 25.55 | 26.94 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 39.39 | 67.21 | 37.60 | 27.72 | 37.26 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 10.1, CH-oop 24.0, ring-ip 4.0, other 25.0 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.27 | 1.02 | 0.32 | 0.23 | 0.30 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 43.91 | 10.78 | 33.91 | 18.69 | 23.33 | 18.51 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.33 | 0.86 | 0.32 | 0.33 | 0.30 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 28.49 | 10.71 | 22.36 | 7.06 | 9.31 | 6.68 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 96.94 | 7.61 | 53.10 | 3.45 | 2.91 | 1.68 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.08 | 17.81 | 46.18 | 37.30 | 42.03 | 37.22 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 17.82 | 7.30 | 25.54 | 18.88 | 27.05 | 18.66 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.1, CH-oop 50.3, ring-ip 9.1, other 24.0 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 1.00 | 0.21 | 0.20 | 0.19 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 15.69 | 49.71 | 12.46 | 10.43 | 12.17 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.37 | 0.90 | 0.35 | 0.29 | 0.34 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.62 | 26.03 | 5.04 | 7.70 | 5.19 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.75 | 56.75 | 5.90 | 4.79 | 2.48 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 22.70 | 80.94 | 11.94 | 15.79 | 12.37 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 21.82 | 46.29 | 20.81 | 12.19 | 20.39 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 15.2, ring-ip 7.7, other 11.2 |

323 s.
