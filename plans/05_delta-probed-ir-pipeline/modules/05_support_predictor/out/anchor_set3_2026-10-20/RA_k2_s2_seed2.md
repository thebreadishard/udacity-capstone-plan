# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 21:09)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 2.35 | 1.30 | 0.49 | 0.89 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.26 | 42.29 | 12.03 | 6.46 | 9.94 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.21 | 0.88 | 0.42 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.83 | 28.43 | 6.59 | 1.58 | 3.89 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.54 | 77.02 | 9.05 | 7.66 | 1.60 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.60 | 43.03 | 20.23 | 11.54 | 18.71 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.67 | 25.37 | 12.62 | 5.50 | 10.85 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.5, CH-oop 11.1, ring-ip 1.6, other 5.3 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 2.17 | 0.92 | 0.85 | 0.58 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 45.03 | 23.05 | 18.93 | 21.62 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.76 | 0.80 | 0.72 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.97 | 28.39 | 3.94 | 3.33 | 2.68 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.45 | 78.77 | 7.64 | 2.36 | 2.48 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.25 | 30.53 | 9.49 | 6.76 | 9.41 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.23 | 45.41 | 40.63 | 33.74 | 38.44 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.658 | 0.148 | 0.554 | 0.785 | 0.595 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.265 | 0.368 | 0.509 | 0.373 | 0.479 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.288 | 0.368 | 0.510 | 0.373 | 0.479 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.7, CH-oop 7.5, ring-ip 3.3, other 35.6 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.08 | 2.27 | 0.94 | 0.57 | 0.76 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.69 | 41.06 | 8.20 | 4.42 | 6.58 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.53 | 2.56 | 0.57 | 0.29 | 0.39 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 27.44 | 5.84 | 2.21 | 4.00 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.38 | 79.15 | 6.29 | 4.09 | 0.75 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.34 | 22.78 | 11.93 | 7.39 | 10.85 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.17 | 22.59 | 9.41 | 3.80 | 8.17 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.624 | 0.207 | 0.661 | 0.788 | 0.746 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.344 | 0.341 | 0.106 | 0.324 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.371 | 0.341 | 0.106 | 0.324 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.0, CH-oop 7.4, ring-ip 2.2, other 3.7 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.06 | 1.80 | 0.55 | 0.23 | 0.46 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.87 | 43.42 | 6.92 | 7.98 | 7.45 |
| A_8448043181 | ΔH residual | 1.00 | 0.56 | 2.18 | 0.71 | 0.47 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.32 | 25.95 | 5.47 | 4.27 | 5.19 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.55 | 82.30 | 3.89 | 7.85 | 6.34 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.32 | 28.29 | 10.09 | 11.21 | 11.85 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.98 | 21.75 | 8.35 | 10.48 | 6.82 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.556 | 0.334 | 0.574 | 0.346 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.010 | 0.001 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.8, CH-oop 13.5, ring-ip 4.2, other 12.5 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.96 | 2.04 | 1.46 | 0.73 | 1.18 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.74 | 41.91 | 13.34 | 9.51 | 11.21 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.19 | 1.04 | 0.63 | 0.85 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.52 | 30.05 | 10.53 | 3.62 | 7.87 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.63 | 76.88 | 9.14 | 3.99 | 1.41 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.93 | 46.46 | 21.71 | 17.75 | 20.35 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.58 | 24.82 | 12.67 | 10.31 | 10.98 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.3, CH-oop 18.3, ring-ip 3.6, other 10.3 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 2.19 | 1.07 | 0.59 | 0.71 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.82 | 39.49 | 8.10 | 3.06 | 5.68 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 2.31 | 0.62 | 0.22 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 27.32 | 4.79 | 1.56 | 2.92 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.47 | 77.83 | 8.80 | 1.78 | 1.49 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.33 | 27.62 | 11.21 | 6.27 | 9.18 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 21.61 | 9.20 | 2.21 | 7.35 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.682 | 0.186 | 0.742 | 0.893 | 0.761 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.109 | 0.199 | 0.207 | 0.035 | 0.168 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.199 | 0.329 | 0.285 | 0.307 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.8, CH-oop 6.5, ring-ip 1.8, other 2.2 |

618 s.
