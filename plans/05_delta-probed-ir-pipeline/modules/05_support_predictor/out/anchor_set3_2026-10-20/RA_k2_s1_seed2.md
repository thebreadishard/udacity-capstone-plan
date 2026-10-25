# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 20:58)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.35 | 1.27 | 0.53 | 0.86 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.90 | 42.29 | 11.77 | 5.90 | 9.82 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.21 | 0.88 | 0.38 | 0.70 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.62 | 28.43 | 6.63 | 1.71 | 3.88 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.31 | 77.02 | 7.70 | 5.99 | 1.08 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.33 | 43.03 | 19.92 | 10.38 | 18.27 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.60 | 25.37 | 12.55 | 5.79 | 10.94 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.8, CH-oop 10.2, ring-ip 1.7, other 5.6 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.17 | 0.91 | 0.60 | 0.57 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 45.03 | 21.66 | 18.14 | 20.28 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.66 | 0.75 | 0.78 | 0.71 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.83 | 28.39 | 3.97 | 2.56 | 2.55 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.74 | 78.77 | 6.35 | 1.67 | 2.93 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 30.53 | 9.41 | 6.92 | 9.10 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.07 | 45.41 | 38.16 | 32.37 | 35.99 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.648 | 0.148 | 0.624 | 0.849 | 0.661 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.263 | 0.368 | 0.479 | 0.286 | 0.450 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.368 | 0.480 | 0.286 | 0.450 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.7, CH-oop 7.6, ring-ip 2.5, other 33.5 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.11 | 2.27 | 0.95 | 0.62 | 0.79 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.89 | 41.06 | 8.39 | 5.12 | 7.07 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.58 | 0.31 | 0.40 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.91 | 27.44 | 6.09 | 2.44 | 4.28 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.27 | 79.15 | 4.83 | 7.06 | 2.18 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.11 | 22.78 | 12.97 | 7.27 | 11.97 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.95 | 22.59 | 9.05 | 4.15 | 7.82 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.639 | 0.207 | 0.679 | 0.767 | 0.725 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.344 | 0.341 | 0.145 | 0.324 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.371 | 0.341 | 0.145 | 0.343 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.1, CH-oop 7.4, ring-ip 2.4, other 4.0 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.80 | 0.57 | 0.22 | 0.49 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.98 | 43.42 | 6.89 | 8.93 | 7.82 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.18 | 0.71 | 0.47 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.24 | 25.95 | 5.63 | 3.66 | 5.35 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.52 | 82.30 | 2.49 | 13.23 | 7.54 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.92 | 28.29 | 10.32 | 10.96 | 12.21 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.75 | 8.21 | 9.47 | 6.74 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.331 | 0.556 | 0.359 | 0.427 | 0.320 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.011 | 0.001 | 0.006 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 13.1, CH-oop 13.7, ring-ip 3.6, other 12.1 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.04 | 1.44 | 0.71 | 1.15 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.26 | 41.91 | 13.10 | 8.91 | 11.07 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 2.19 | 1.03 | 0.57 | 0.84 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.30 | 30.05 | 10.60 | 3.43 | 7.80 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.31 | 76.88 | 7.70 | 5.63 | 1.02 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.35 | 46.46 | 21.37 | 16.67 | 19.93 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.35 | 24.82 | 12.55 | 9.21 | 10.97 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.7, CH-oop 17.0, ring-ip 3.4, other 9.0 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.19 | 1.08 | 0.62 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.86 | 39.49 | 7.83 | 3.57 | 5.74 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.61 | 0.23 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.97 | 27.32 | 4.80 | 1.80 | 2.93 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.32 | 77.83 | 7.33 | 2.05 | 2.20 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.13 | 27.62 | 11.34 | 7.56 | 9.39 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.30 | 21.61 | 9.02 | 2.18 | 7.26 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.686 | 0.186 | 0.728 | 0.801 | 0.741 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.199 | 0.207 | 0.052 | 0.171 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.199 | 0.328 | 0.275 | 0.307 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 2.0, CH-oop 7.8, ring-ip 2.1, other 2.2 |

663 s.
