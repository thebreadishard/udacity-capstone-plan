# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 05:20)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.32 | 1.00 | 0.25 | 0.39 | 0.23 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 34.47 | 61.28 | 25.09 | 22.62 | 24.70 |
| A_01f3186607 | ΔH residual | 1.00 | 0.59 | 0.94 | 0.52 | 0.46 | 0.51 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 10.19 | 20.71 | 6.11 | 8.29 | 6.26 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.65 | 54.60 | 5.92 | 7.44 | 4.36 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 51.81 | 94.10 | 34.58 | 33.80 | 34.07 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 48.52 | 74.57 | 37.52 | 31.33 | 36.97 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.7, CH-oop 32.3, ring-ip 7.8, other 29.9 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.90 | 0.28 | 0.28 | 0.27 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 12.99 | 51.29 | 14.01 | 9.58 | 13.69 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.27 | 0.86 | 0.26 | 0.31 | 0.25 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.29 | 30.84 | 6.93 | 5.18 | 6.41 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.68 | 55.28 | 3.79 | 2.08 | 3.04 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 10.97 | 69.59 | 25.14 | 18.35 | 24.93 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 26.93 | 61.79 | 14.64 | 5.40 | 14.08 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 17.4, ring-ip 6.2, other 4.9 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.12 | 0.95 | 0.15 | 0.10 | 0.12 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 22.27 | 56.81 | 15.58 | 10.94 | 14.95 |
| A_8448043181 | ΔH residual | 1.00 | 0.37 | 0.92 | 0.33 | 0.18 | 0.31 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.37 | 24.46 | 5.61 | 6.30 | 4.99 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.71 | 56.08 | 6.96 | 1.99 | 4.30 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 33.08 | 89.28 | 18.69 | 18.13 | 18.53 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 37.68 | 66.86 | 29.97 | 14.69 | 29.03 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.1, CH-oop 20.4, ring-ip 6.0, other 9.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 1.01 | 0.21 | 0.20 | 0.18 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 13.86 | 49.31 | 11.13 | 6.48 | 10.59 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.35 | 0.89 | 0.31 | 0.33 | 0.30 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.80 | 26.61 | 5.52 | 4.02 | 5.82 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.43 | 55.67 | 5.25 | 3.86 | 1.68 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 17.06 | 80.09 | 17.74 | 11.30 | 17.20 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 20.32 | 45.93 | 14.32 | 6.65 | 13.52 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.5, CH-oop 13.2, ring-ip 6.6, other 7.7 |

171 s.
