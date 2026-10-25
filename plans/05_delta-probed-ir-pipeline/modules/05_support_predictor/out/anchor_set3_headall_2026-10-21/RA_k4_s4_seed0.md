# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:25)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.22 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.06 | 3.85 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 0.24 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.91 | 0.82 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.45 | 1.09 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.45 | 6.51 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.69 | 5.02 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 0.70 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.15 | 14.93 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.80 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.32 | 2.12 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.83 | 2.41 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.37 | 4.15 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.98 | 26.77 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.651 | 0.826 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.095 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.277 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 0.54 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.59 | 3.31 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.32 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 1.92 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.60 | 2.69 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.43 | 5.46 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.16 | 2.99 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.637 | 0.869 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.140 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.164 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 0.31 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 5.57 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.28 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.25 | 3.27 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.80 | 4.89 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.45 | 8.91 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.95 | 5.85 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.326 | 0.716 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.000 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.000 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.52 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.40 | 4.66 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 0.31 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.57 | 2.78 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.30 | 2.35 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.54 | 8.81 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.44 | 4.35 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.18 | 0.68 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.75 | 2.32 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 0.28 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.15 | 2.85 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.63 | 0.51 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.49 | 2.32 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.46 | 2.10 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.836 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.116 | 0.141 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.281 | 0.653 |

299 s.
