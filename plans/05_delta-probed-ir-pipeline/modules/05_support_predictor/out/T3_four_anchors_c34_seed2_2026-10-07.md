# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-07 05:22)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.32 | 0.99 | 0.39 | 0.32 | 0.44 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 34.47 | 61.33 | 25.24 | 19.21 | 25.18 |
| A_01f3186607 | ΔH residual | 1.00 | 0.59 | 0.95 | 0.53 | 0.44 | 0.53 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 10.19 | 20.26 | 7.10 | 8.38 | 7.60 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.65 | 54.07 | 4.27 | 2.26 | 2.99 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 51.81 | 94.05 | 33.91 | 28.05 | 34.09 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 48.52 | 75.13 | 38.10 | 26.87 | 37.82 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.2, CH-oop 26.2, ring-ip 9.2, other 26.8 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.89 | 0.26 | 0.26 | 0.24 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 12.99 | 51.72 | 13.23 | 8.36 | 13.04 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.27 | 0.89 | 0.26 | 0.22 | 0.24 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.29 | 30.79 | 6.25 | 4.97 | 5.72 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.68 | 54.07 | 1.29 | 3.48 | 1.40 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 10.97 | 71.97 | 23.88 | 15.44 | 23.84 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 26.93 | 61.56 | 14.38 | 5.02 | 13.94 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.7, CH-oop 15.2, ring-ip 5.9, other 4.5 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.12 | 0.91 | 0.12 | 0.17 | 0.09 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 22.27 | 57.73 | 16.25 | 14.80 | 15.68 |
| A_8448043181 | ΔH residual | 1.00 | 0.37 | 0.93 | 0.34 | 0.23 | 0.33 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.37 | 22.92 | 6.42 | 9.99 | 5.61 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.71 | 55.61 | 5.71 | 1.53 | 2.44 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 33.08 | 92.06 | 18.51 | 25.71 | 18.67 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 37.68 | 68.92 | 32.06 | 16.11 | 31.11 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.6, CH-oop 25.2, ring-ip 9.5, other 14.4 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 0.98 | 0.21 | 0.16 | 0.18 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 13.86 | 49.52 | 11.26 | 6.75 | 10.86 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.35 | 0.90 | 0.32 | 0.28 | 0.30 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.80 | 26.21 | 5.21 | 3.95 | 5.47 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.43 | 55.48 | 4.09 | 3.69 | 1.40 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 17.06 | 81.06 | 18.59 | 13.57 | 18.20 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 20.32 | 46.19 | 14.42 | 4.91 | 13.76 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.8, CH-oop 15.6, ring-ip 4.7, other 5.2 |

168 s.
