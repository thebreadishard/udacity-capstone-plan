# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:31)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.45 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.23 | 3.61 |
| A_01f3186607 | ΔH residual | 1.00 | 0.71 | 0.21 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.33 | 1.84 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 10.26 | 0.70 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.16 | 6.01 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.56 | 4.39 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 0.39 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.07 | 15.08 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.82 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.31 | 1.37 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.33 | 1.65 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.95 | 3.79 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.58 | 27.18 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.634 | 0.888 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.259 | 0.084 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.303 | 0.084 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.14 | 0.63 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.26 | 4.52 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.51 | 0.44 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.09 | 2.15 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.16 | 5.44 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.68 | 7.22 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.78 | 2.93 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.610 | 0.788 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.185 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.239 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 0.31 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.30 | 5.81 |
| A_8448043181 | ΔH residual | 1.00 | 0.54 | 0.32 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.49 | 1.83 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 4.33 | 4.37 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 21.40 | 8.94 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.48 | 8.66 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.311 | 0.694 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.001 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.001 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.97 | 0.83 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.49 | 4.37 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.78 | 0.34 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.99 | 3.89 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 11.32 | 2.65 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 12.89 | 7.41 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.16 | 3.55 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.16 | 0.68 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.33 | 2.53 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 0.26 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.62 | 2.53 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.23 | 2.82 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.73 | 2.49 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.19 | 2.35 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.677 | 0.866 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.154 | 0.047 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.381 | 0.047 |

242 s.
