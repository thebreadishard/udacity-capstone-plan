# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:08)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.22 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.86 | 4.56 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 0.29 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.78 | 0.76 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.83 | 1.46 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.29 | 8.07 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 5.66 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 0.68 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 13.69 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.70 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.23 | 2.63 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.38 | 2.01 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 5.19 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.86 | 24.33 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.644 | 0.785 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.156 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.297 | 0.156 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 0.58 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.74 | 3.27 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.32 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.73 | 1.88 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.04 | 2.11 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.94 | 5.40 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.01 | 3.52 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.643 | 0.914 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.095 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.160 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.12 | 0.34 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.92 | 5.07 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.24 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.15 | 3.08 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.31 | 3.34 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.86 | 8.62 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.76 | 5.18 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.336 | 0.705 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.61 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.13 | 6.31 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.39 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 3.19 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.65 | 1.92 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.16 | 12.82 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.28 | 5.64 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.19 | 0.78 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.81 | 3.15 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.38 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.06 | 4.15 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.05 | 1.45 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.03 | 2.80 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.35 | 2.25 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.683 | 0.769 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.112 | 0.066 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.279 | 0.066 |

298 s.
