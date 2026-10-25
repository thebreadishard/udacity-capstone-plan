# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 15:22)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.30 | 0.78 | 0.91 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.23 | 42.40 | 12.11 | 7.39 | 10.30 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 2.23 | 0.89 | 0.50 | 0.73 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.33 | 28.95 | 6.72 | 2.75 | 3.52 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.26 | 76.46 | 7.42 | 5.89 | 2.02 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.16 | 43.01 | 20.40 | 14.21 | 18.50 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.56 | 26.25 | 13.26 | 6.52 | 12.24 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.8, CH-oop 13.6, ring-ip 2.8, other 6.2 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 2.14 | 0.90 | 0.59 | 0.60 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.07 | 44.91 | 20.92 | 19.17 | 19.06 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.73 | 0.88 | 0.63 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.31 | 28.99 | 3.93 | 2.77 | 2.56 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.33 | 77.94 | 6.41 | 0.82 | 1.36 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.95 | 31.04 | 10.12 | 6.93 | 10.21 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.58 | 45.07 | 36.65 | 34.27 | 33.58 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.634 | 0.135 | 0.560 | 0.807 | 0.587 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.259 | 0.405 | 0.502 | 0.301 | 0.465 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.303 | 0.405 | 0.502 | 0.301 | 0.465 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 0.8, CH-oop 7.3, ring-ip 2.6, other 35.3 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 2.20 | 1.00 | 0.87 | 0.85 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.26 | 40.59 | 9.32 | 5.97 | 7.56 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 2.56 | 0.64 | 0.35 | 0.45 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.09 | 28.33 | 7.52 | 3.20 | 5.75 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.16 | 77.60 | 5.66 | 3.50 | 2.93 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.68 | 21.56 | 14.44 | 11.20 | 12.29 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.78 | 22.14 | 7.99 | 2.51 | 7.01 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.610 | 0.184 | 0.684 | 0.742 | 0.749 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.326 | 0.328 | 0.160 | 0.307 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.354 | 0.328 | 0.219 | 0.341 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.5, CH-oop 11.7, ring-ip 2.5, other 2.4 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.79 | 0.66 | 0.42 | 0.64 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.30 | 42.93 | 7.91 | 6.34 | 7.79 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 2.18 | 0.71 | 0.40 | 0.63 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.49 | 26.68 | 7.06 | 3.07 | 6.12 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.33 | 80.99 | 2.79 | 7.13 | 3.77 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 21.40 | 27.02 | 12.33 | 10.19 | 12.91 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.48 | 21.41 | 7.35 | 5.54 | 7.05 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.601 | 0.365 | 0.353 | 0.398 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.012 | 0.005 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.0, CH-oop 12.5, ring-ip 3.1, other 10.7 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.97 | 2.07 | 1.46 | 0.61 | 1.08 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.49 | 41.92 | 13.15 | 8.07 | 10.88 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 2.20 | 1.03 | 0.54 | 0.83 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.99 | 30.42 | 10.49 | 3.75 | 6.06 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.32 | 76.74 | 6.97 | 6.54 | 2.03 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.89 | 46.64 | 22.46 | 15.16 | 20.76 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.16 | 24.41 | 12.13 | 7.48 | 10.83 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.4, CH-oop 17.5, ring-ip 3.8, other 7.4 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.16 | 2.16 | 1.11 | 0.86 | 0.74 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.33 | 39.22 | 7.68 | 4.29 | 5.64 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.62 | 0.29 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.62 | 27.91 | 4.94 | 3.34 | 3.23 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.23 | 76.57 | 7.83 | 3.29 | 1.06 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.73 | 27.41 | 10.09 | 7.10 | 8.47 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.19 | 21.61 | 9.11 | 3.73 | 7.61 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.677 | 0.174 | 0.706 | 0.774 | 0.723 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.154 | 0.202 | 0.213 | 0.221 | 0.181 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.381 | 0.202 | 0.326 | 0.476 | 0.305 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.0, CH-oop 7.4, ring-ip 3.3, other 3.8 |

688 s.
