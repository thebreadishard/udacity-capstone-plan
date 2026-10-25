# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:57)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.29 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.87 | 4.08 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 0.24 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.82 | 0.78 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.86 | 1.02 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 6.65 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 5.50 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.68 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.13 | 14.24 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.78 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.27 | 2.36 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.40 | 1.53 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.66 | 5.20 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 25.39 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.816 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.166 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.166 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.55 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 3.79 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.34 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.77 | 1.72 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.06 | 2.28 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.00 | 6.96 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.98 | 2.98 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.641 | 0.872 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.145 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.153 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 0.41 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.95 | 4.97 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.22 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.20 | 4.10 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.33 | 1.97 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.91 | 8.01 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 4.80 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.335 | 0.672 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.003 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.003 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.62 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 6.42 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.39 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.47 | 3.71 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.68 | 1.61 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.12 | 12.96 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.26 | 5.58 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.20 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.85 | 3.64 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.38 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 3.79 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.07 | 2.95 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.08 | 4.22 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.33 | 3.41 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.681 | 0.780 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.076 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.076 |

298 s.
