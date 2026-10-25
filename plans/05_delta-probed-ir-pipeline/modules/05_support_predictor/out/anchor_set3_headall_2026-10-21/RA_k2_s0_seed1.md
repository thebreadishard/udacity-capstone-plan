# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:38)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.51 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.23 | 4.04 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 0.29 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.33 | 2.35 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.26 | 2.39 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.16 | 6.43 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.56 | 4.69 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 0.59 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.07 | 15.74 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.86 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.31 | 2.43 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.33 | 1.83 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.95 | 6.26 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.58 | 28.03 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.634 | 0.725 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.259 | 0.163 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.303 | 0.163 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 0.88 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.26 | 6.11 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 0.47 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.09 | 6.33 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.16 | 4.85 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.68 | 7.83 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.78 | 3.30 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.610 | 0.735 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.147 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.210 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 0.41 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.30 | 5.92 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.28 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.49 | 3.39 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.33 | 3.29 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 21.40 | 9.39 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.48 | 7.85 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.719 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.003 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.003 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.97 | 0.73 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.49 | 5.03 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 0.37 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.99 | 4.23 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.32 | 3.36 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.89 | 9.44 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.16 | 3.30 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.16 | 0.88 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.33 | 3.38 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 0.38 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.62 | 3.65 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.23 | 3.17 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.73 | 3.57 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.19 | 2.93 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.677 | 0.796 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.154 | 0.070 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.381 | 0.070 |

247 s.
