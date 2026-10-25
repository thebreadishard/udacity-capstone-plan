# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:13)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.97 | 0.24 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.81 | 4.34 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.29 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.80 | 1.56 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.54 | 0.66 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.26 | 6.78 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.62 | 5.91 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.10 | 0.61 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 14.44 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.78 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.24 | 2.28 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.18 | 1.92 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.71 | 5.33 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.85 | 25.74 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.642 | 0.760 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.153 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.298 | 0.153 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.16 | 0.59 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.78 | 3.74 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.50 | 0.29 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.78 | 2.63 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.78 | 2.78 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.08 | 5.88 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 3.45 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.646 | 0.912 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.062 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.157 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.14 | 0.36 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.97 | 5.40 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.26 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.21 | 3.50 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.08 | 2.78 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.97 | 8.83 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 6.34 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.340 | 0.757 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.63 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.05 | 6.22 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.76 | 0.40 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.44 | 3.90 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 9.35 | 1.70 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.07 | 11.99 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.24 | 5.73 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.70 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.83 | 3.21 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.47 | 0.32 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.08 | 2.89 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.77 | 2.72 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.17 | 3.40 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 3.79 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.680 | 0.830 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.115 | 0.066 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.280 | 0.066 |

303 s.
