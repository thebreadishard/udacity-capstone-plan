# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 15:34)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.37 | 1.32 | 0.55 | 0.95 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.90 | 42.40 | 12.27 | 6.87 | 10.26 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 2.23 | 0.90 | 0.46 | 0.74 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.62 | 28.95 | 6.85 | 2.23 | 3.85 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.31 | 76.46 | 8.64 | 5.63 | 1.32 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.33 | 43.01 | 20.29 | 12.63 | 18.44 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.60 | 26.25 | 13.34 | 6.78 | 12.09 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.6, CH-oop 12.0, ring-ip 2.2, other 6.5 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 2.14 | 0.87 | 0.66 | 0.58 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 44.91 | 21.86 | 20.04 | 19.92 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 1.64 | 0.73 | 0.92 | 0.65 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.83 | 28.99 | 4.10 | 2.93 | 2.48 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.74 | 77.94 | 7.62 | 1.17 | 2.27 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 31.04 | 10.25 | 6.86 | 10.30 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.07 | 45.07 | 38.27 | 35.86 | 35.15 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.648 | 0.135 | 0.519 | 0.817 | 0.577 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.263 | 0.405 | 0.520 | 0.298 | 0.478 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.405 | 0.520 | 0.297 | 0.478 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.1, CH-oop 7.2, ring-ip 2.8, other 37.0 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.11 | 2.20 | 0.99 | 0.80 | 0.82 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.89 | 40.59 | 8.88 | 4.90 | 7.20 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.59 | 0.35 | 0.41 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.91 | 28.33 | 6.28 | 2.71 | 4.80 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.27 | 77.60 | 6.81 | 2.99 | 3.51 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.11 | 21.56 | 13.84 | 8.92 | 11.97 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.95 | 22.14 | 8.28 | 3.13 | 7.13 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.639 | 0.184 | 0.670 | 0.778 | 0.746 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.326 | 0.326 | 0.176 | 0.304 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.354 | 0.326 | 0.231 | 0.339 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.0, CH-oop 9.4, ring-ip 2.3, other 3.0 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 1.79 | 0.65 | 0.45 | 0.61 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.98 | 42.93 | 7.77 | 6.17 | 7.72 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.18 | 0.69 | 0.40 | 0.62 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.24 | 26.68 | 6.27 | 2.88 | 5.50 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.52 | 80.99 | 3.93 | 7.47 | 4.87 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.92 | 27.02 | 12.46 | 9.64 | 12.98 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 21.41 | 7.44 | 5.33 | 6.97 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.331 | 0.601 | 0.344 | 0.341 | 0.382 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.022 | 0.012 | 0.004 | 0.009 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.4, CH-oop 12.2, ring-ip 2.9, other 10.8 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 2.07 | 1.50 | 0.78 | 1.26 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.26 | 41.92 | 13.40 | 8.05 | 11.19 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 2.20 | 1.05 | 0.57 | 0.88 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.30 | 30.42 | 10.98 | 4.40 | 7.67 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.31 | 76.74 | 8.23 | 5.67 | 2.17 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.35 | 46.64 | 22.42 | 15.42 | 20.88 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.35 | 24.41 | 12.17 | 7.10 | 10.54 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.5, CH-oop 18.4, ring-ip 4.7, other 7.7 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 2.16 | 1.06 | 0.80 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.86 | 39.22 | 7.87 | 4.38 | 5.60 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 2.31 | 0.62 | 0.30 | 0.49 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.97 | 27.91 | 4.92 | 3.36 | 3.10 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.32 | 76.57 | 8.93 | 5.08 | 1.63 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.13 | 27.41 | 10.02 | 6.25 | 8.53 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.30 | 21.61 | 9.12 | 3.81 | 7.49 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.686 | 0.174 | 0.720 | 0.761 | 0.729 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.202 | 0.212 | 0.219 | 0.177 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.202 | 0.326 | 0.247 | 0.304 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.4, CH-oop 6.5, ring-ip 3.3, other 3.8 |

652 s.
