# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-02 14:13)

Model `E7_rungC_carried_kd_750_saved_2026-10-02_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned |
|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.32 | 0.99 | 0.29 | 0.31 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 63.54 | 34.47 | 61.45 | 26.34 | 25.13 |
| A_01f3186607 | ΔH residual | 1.00 | 0.59 | 0.94 | 0.53 | 0.49 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 25.95 | 10.19 | 19.84 | 5.95 | 8.86 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 97.84 | 9.65 | 54.84 | 5.14 | 4.62 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 75.97 | 51.81 | 94.35 | 36.35 | 38.51 |
| A_01f3186607 | ω rms other (cm⁻¹) | 64.89 | 48.52 | 75.08 | 39.54 | 34.71 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.9, CH-oop 35.8, ring-ip 8.9, other 34.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 0.23 | 0.88 | 0.27 | 0.23 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 55.24 | 12.99 | 51.78 | 12.81 | 8.55 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.27 | 0.88 | 0.26 | 0.26 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 25.92 | 7.29 | 30.79 | 6.67 | 4.44 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 97.68 | 7.68 | 56.35 | 4.25 | 2.22 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 52.40 | 10.97 | 71.05 | 22.42 | 16.71 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 50.39 | 26.93 | 60.90 | 14.06 | 2.96 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.5, CH-oop 16.5, ring-ip 4.8, other 2.6 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.12 | 0.92 | 0.17 | 0.09 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 61.65 | 22.27 | 57.65 | 15.57 | 13.50 |
| A_8448043181 | ΔH residual | 1.00 | 0.37 | 0.93 | 0.33 | 0.23 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 24.96 | 6.37 | 22.92 | 6.21 | 4.83 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 99.29 | 10.71 | 58.87 | 8.98 | 3.96 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 72.03 | 33.08 | 91.31 | 17.21 | 23.32 |
| A_8448043181 | ω rms other (cm⁻¹) | 55.94 | 37.68 | 66.40 | 30.02 | 19.00 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.1, CH-oop 24.1, ring-ip 5.0, other 15.5 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 0.18 | 0.99 | 0.22 | 0.26 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 53.63 | 13.86 | 49.29 | 10.88 | 6.87 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.35 | 0.89 | 0.32 | 0.40 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 28.30 | 7.80 | 26.14 | 5.39 | 6.23 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 98.61 | 7.43 | 56.24 | 5.18 | 2.37 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 59.50 | 17.06 | 80.44 | 17.04 | 10.66 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 35.98 | 20.32 | 45.45 | 14.21 | 6.64 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 10.9, ring-ip 9.1, other 6.2 |

193 s.
