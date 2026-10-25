# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:46)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 0.28 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.26 | 4.55 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 0.25 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.83 | 0.89 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.54 | 1.14 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.60 | 9.00 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.67 | 4.78 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.63 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 12.71 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.61 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.97 | 2.31 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.45 | 1.70 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.25 | 6.30 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.23 | 22.40 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.658 | 0.724 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.265 | 0.151 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.288 | 0.151 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.08 | 0.58 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.69 | 3.49 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.53 | 0.32 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 1.60 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.38 | 3.42 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.34 | 5.65 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.17 | 3.47 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.624 | 0.878 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.136 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.175 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.06 | 0.41 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.87 | 5.88 |
| A_8448043181 | ΔH residual | 1.00 | 0.56 | 0.26 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.32 | 3.27 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.55 | 4.08 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.32 | 10.04 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.98 | 6.24 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.733 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.96 | 0.78 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.74 | 7.61 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 0.51 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.52 | 5.12 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.63 | 2.51 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.93 | 14.27 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.58 | 7.05 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 0.72 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.82 | 3.29 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 0.33 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 2.98 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.47 | 3.36 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.33 | 3.56 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 3.49 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.682 | 0.826 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.109 | 0.054 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.054 |

213 s.
