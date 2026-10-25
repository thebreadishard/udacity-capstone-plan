# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:54)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.29 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.50 | 3.58 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 0.23 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.50 | 1.08 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.09 | 1.30 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.36 | 6.57 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 4.11 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.08 | 0.53 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 16.01 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 0.86 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.42 | 2.10 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.91 | 0.93 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.56 | 7.03 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.75 | 28.48 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.643 | 0.683 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.154 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.154 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.12 | 0.63 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.07 | 4.46 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 0.33 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.00 | 3.73 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.90 | 3.84 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 6.56 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.97 | 3.05 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.602 | 0.875 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.079 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.170 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.07 | 0.41 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.19 | 5.67 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.27 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.61 | 3.60 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.03 | 3.47 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.83 | 9.93 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 5.15 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.298 | 0.713 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.003 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.003 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 0.72 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.87 | 5.41 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 0.39 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.17 | 3.81 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.21 | 1.39 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.40 | 10.40 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.38 | 4.67 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.14 | 0.89 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 3.90 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 0.39 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.75 | 3.63 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.99 | 5.07 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.01 | 2.53 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.34 | 4.15 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.672 | 0.806 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.173 | 0.075 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.309 | 0.075 |

222 s.
