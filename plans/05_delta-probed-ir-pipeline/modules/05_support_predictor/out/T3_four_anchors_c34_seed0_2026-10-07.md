# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 05:17)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.32 | 1.01 | 0.32 | 0.32 | 0.23 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 34.47 | 61.68 | 25.77 | 24.07 | 25.49 |
| A_01f3186607 | ΔH residual | 1.00 | 0.59 | 0.95 | 0.53 | 0.50 | 0.52 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 10.19 | 20.36 | 6.35 | 9.95 | 6.15 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.65 | 54.64 | 5.79 | 8.05 | 4.39 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 51.81 | 94.29 | 35.21 | 34.64 | 34.92 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 48.52 | 75.66 | 38.69 | 33.71 | 38.35 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 8.3, CH-oop 30.7, ring-ip 9.7, other 33.5 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.91 | 0.27 | 0.24 | 0.25 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 12.99 | 51.74 | 13.78 | 10.40 | 13.64 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.27 | 0.88 | 0.26 | 0.22 | 0.25 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.29 | 30.90 | 6.70 | 5.17 | 6.28 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.68 | 55.65 | 3.58 | 2.07 | 2.13 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 10.97 | 70.86 | 25.06 | 20.42 | 25.27 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 26.93 | 61.66 | 13.72 | 4.35 | 13.21 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 19.3, ring-ip 6.0, other 3.7 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.12 | 0.92 | 0.14 | 0.05 | 0.11 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 22.27 | 57.16 | 15.89 | 13.18 | 15.53 |
| A_8448043181 | ΔH residual | 1.00 | 0.37 | 0.92 | 0.34 | 0.22 | 0.32 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.37 | 22.69 | 6.06 | 3.97 | 5.52 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.71 | 56.93 | 7.58 | 6.65 | 5.02 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 33.08 | 90.65 | 19.07 | 21.52 | 19.40 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 37.68 | 67.21 | 30.23 | 19.83 | 29.75 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.8, CH-oop 20.6, ring-ip 3.9, other 17.8 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 1.00 | 0.21 | 0.19 | 0.19 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 13.86 | 49.71 | 11.33 | 7.45 | 11.00 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.35 | 0.90 | 0.32 | 0.26 | 0.30 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.80 | 26.03 | 5.36 | 7.24 | 5.62 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.43 | 56.75 | 6.34 | 2.45 | 3.27 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 17.06 | 80.94 | 17.97 | 13.19 | 18.10 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 20.32 | 46.29 | 14.53 | 4.13 | 13.96 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.6, CH-oop 15.2, ring-ip 7.2, other 4.8 |

165 s.
