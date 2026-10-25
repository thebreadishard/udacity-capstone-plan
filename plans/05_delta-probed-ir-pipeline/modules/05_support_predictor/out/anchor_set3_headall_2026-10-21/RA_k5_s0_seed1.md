# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:23)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.24 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.73 | 4.06 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.27 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.63 | 0.83 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.22 | 1.65 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.32 | 6.59 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 5.41 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.64 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.14 | 13.49 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.72 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 2.70 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.32 | 1.54 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.58 | 4.22 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.94 | 24.09 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.646 | 0.787 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.262 | 0.113 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.113 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.15 | 0.51 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.61 | 3.13 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.28 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.66 | 1.45 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.54 | 1.68 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.78 | 5.40 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.06 | 3.54 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.655 | 0.916 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.103 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.150 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.30 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.84 | 5.04 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.24 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.09 | 2.70 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.89 | 1.83 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.75 | 8.82 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.82 | 5.99 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.345 | 0.727 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.56 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 6.03 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.37 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.28 | 3.63 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.96 | 2.08 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.19 | 11.50 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.29 | 5.71 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.72 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.67 | 3.18 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.34 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.91 | 3.49 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.52 | 2.40 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 2.94 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.38 | 3.26 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.800 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.111 | 0.076 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.278 | 0.076 |

337 s.
