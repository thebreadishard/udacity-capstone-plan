# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 06:59)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.26 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.50 | 3.57 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 0.20 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.50 | 1.39 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.09 | 1.55 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.36 | 5.00 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 5.05 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.08 | 0.67 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 14.38 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 0.69 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.42 | 1.92 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.91 | 2.45 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.56 | 5.75 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.75 | 25.60 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.643 | 0.730 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.169 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.169 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.12 | 0.51 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.07 | 4.29 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 0.38 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.00 | 2.12 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.90 | 2.97 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 7.89 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.97 | 2.53 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.602 | 0.858 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.140 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.206 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.07 | 0.22 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.19 | 4.87 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.28 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.61 | 2.80 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.03 | 1.77 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.83 | 7.50 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 7.11 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.298 | 0.810 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.000 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.000 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 0.55 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.87 | 4.99 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 0.36 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.17 | 2.84 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.21 | 2.45 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.40 | 9.41 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.38 | 4.78 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.14 | 0.62 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 2.28 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 0.26 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.75 | 2.97 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.99 | 0.68 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.01 | 2.35 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.34 | 1.61 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.672 | 0.857 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.173 | 0.119 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.309 | 0.119 |

226 s.
