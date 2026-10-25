# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 07:09)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.22 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.65 | 3.65 |
| A_01f3186607 | ΔH residual | 1.00 | 0.69 | 0.21 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.33 | 0.91 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 8.13 | 1.39 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.42 | 6.38 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.65 | 4.51 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 0.50 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.16 | 13.55 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.73 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.93 | 1.87 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.90 | 1.09 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.45 | 4.88 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.21 | 24.22 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.653 | 0.889 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.264 | 0.084 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.305 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.13 | 0.53 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.53 | 3.31 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 0.30 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.69 | 2.64 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 5.39 | 2.01 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.58 | 4.97 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.12 | 3.26 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.663 | 0.888 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.116 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.191 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.13 | 0.17 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.75 | 5.60 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.31 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.04 | 2.87 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 2.76 | 7.37 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.56 | 7.49 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.89 | 5.84 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.349 | 0.713 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.007 | 0.002 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.002 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.94 | 0.58 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 8.99 | 5.70 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.75 | 0.37 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.01 | 3.10 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 8.92 | 2.83 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.46 | 11.72 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.39 | 4.57 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.24 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.52 | 2.66 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 0.30 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.67 | 2.66 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 6.38 | 2.48 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.64 | 2.73 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.41 | 2.72 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.687 | 0.837 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.100 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.276 | 0.677 |

313 s.
