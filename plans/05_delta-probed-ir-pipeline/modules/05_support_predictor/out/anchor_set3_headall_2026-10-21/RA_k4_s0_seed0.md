# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:03)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.25 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.87 | 3.43 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 0.19 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.82 | 1.00 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.86 | 0.99 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 5.81 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 4.39 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.61 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.13 | 15.31 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.85 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.27 | 1.94 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.40 | 1.29 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.66 | 3.79 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 27.56 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.885 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.113 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.281 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.56 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 3.69 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.35 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.77 | 2.43 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.06 | 1.89 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.00 | 6.39 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.98 | 2.88 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.641 | 0.878 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.149 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.212 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 0.22 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.95 | 4.72 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.28 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.20 | 2.91 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.33 | 4.55 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.91 | 6.80 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 5.61 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.335 | 0.742 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.000 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.000 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.52 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 4.18 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.30 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.47 | 2.49 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.68 | 2.01 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.12 | 7.98 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.26 | 3.87 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.20 | 0.65 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.85 | 2.95 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.31 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.10 | 3.36 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.07 | 1.35 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.08 | 3.05 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.33 | 2.96 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.681 | 0.781 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.065 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.065 |

321 s.
