# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-09 13:32)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (3 anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.37 | 1.42 | 0.81 | 1.12 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 10.00 | 42.40 | 12.84 | 7.81 | 11.08 |
| A_01f3186607 | ΔH residual | 1.00 | 0.75 | 2.23 | 0.91 | 0.55 | 0.78 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.52 | 28.95 | 6.90 | 2.88 | 4.41 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 13.31 | 76.46 | 9.17 | 4.90 | 2.58 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.55 | 43.01 | 21.51 | 14.91 | 20.07 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.61 | 26.25 | 13.84 | 7.61 | 12.72 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.8, CH-oop 14.4, ring-ip 2.9, other 7.4 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.14 | 0.86 | 0.75 | 0.57 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.08 | 44.91 | 20.93 | 18.58 | 19.39 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.72 | 0.89 | 0.64 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.87 | 28.99 | 4.22 | 2.83 | 2.44 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.35 | 77.94 | 7.89 | 1.84 | 1.14 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.39 | 31.04 | 10.52 | 6.66 | 10.41 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.03 | 45.07 | 36.43 | 33.18 | 34.18 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 7.1, ring-ip 2.7, other 34.3 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.04 | 2.20 | 0.98 | 0.84 | 0.84 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.35 | 40.59 | 8.38 | 5.59 | 6.60 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.55 | 2.56 | 0.59 | 0.36 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.17 | 28.33 | 6.15 | 3.51 | 4.38 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 9.48 | 77.60 | 7.07 | 3.32 | 2.61 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 21.56 | 12.08 | 10.12 | 10.61 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 22.14 | 8.91 | 2.55 | 7.71 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.3, CH-oop 10.9, ring-ip 2.6, other 2.5 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.99 | 1.79 | 0.64 | 0.43 | 0.58 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.35 | 42.93 | 7.56 | 5.77 | 7.33 |
| A_8448043181 | ΔH residual | 1.00 | 0.57 | 2.18 | 0.70 | 0.40 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.74 | 26.68 | 5.94 | 2.83 | 5.07 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 6.60 | 80.99 | 4.30 | 6.62 | 3.61 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.71 | 27.02 | 11.68 | 8.98 | 12.39 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.74 | 21.41 | 8.08 | 5.45 | 7.44 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.269 | 0.601 | 0.345 | 0.365 | 0.406 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.005 | 0.022 | 0.012 | 0.005 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.5, CH-oop 11.7, ring-ip 2.8, other 11.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 1.00 | 2.07 | 1.50 | 0.77 | 1.34 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 10.65 | 41.92 | 13.91 | 8.99 | 12.00 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.82 | 2.20 | 1.06 | 0.62 | 0.93 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.25 | 30.42 | 10.94 | 4.00 | 8.25 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 15.01 | 76.74 | 8.68 | 9.29 | 1.80 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 14.03 | 46.64 | 23.73 | 17.03 | 22.51 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.62 | 24.41 | 12.65 | 7.36 | 11.23 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 9.1, CH-oop 20.1, ring-ip 4.3, other 7.2 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 2.16 | 1.04 | 0.73 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.52 | 39.22 | 8.10 | 4.36 | 5.74 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.52 | 2.31 | 0.63 | 0.30 | 0.50 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.76 | 27.91 | 4.88 | 3.97 | 3.07 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 10.69 | 76.57 | 9.40 | 2.68 | 1.02 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 27.41 | 9.82 | 7.12 | 8.39 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 21.61 | 9.75 | 3.40 | 8.05 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.6, CH-oop 7.3, ring-ip 3.9, other 3.4 |

451 s.
