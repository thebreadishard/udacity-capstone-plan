# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 06:56)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.43 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.58 | 4.43 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 0.27 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.48 | 1.32 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.48 | 2.02 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.40 | 8.59 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 4.54 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.07 | 0.59 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 14.32 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 0.73 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.41 | 1.58 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 3.23 | 1.48 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.47 | 4.28 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.77 | 25.71 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.645 | 0.794 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.118 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.118 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.10 | 0.65 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.03 | 4.08 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 0.41 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.94 | 2.46 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 8.26 | 2.77 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.82 | 7.25 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.03 | 2.37 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.597 | 0.856 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.163 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.222 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.05 | 0.27 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.15 | 5.15 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.28 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.54 | 2.89 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.38 | 4.01 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.69 | 6.98 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.81 | 7.74 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.292 | 0.782 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.001 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.001 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 0.56 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.99 | 4.48 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 0.33 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.16 | 2.72 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.63 | 5.57 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.51 | 5.84 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.43 | 4.76 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 2.98 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.50 | 0.31 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.71 | 3.38 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 9.37 | 2.28 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.82 | 3.33 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.37 | 2.44 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.676 | 0.810 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.147 | 0.107 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.296 | 0.107 |

222 s.
