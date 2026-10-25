# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:43)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.46 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.58 | 4.50 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 0.29 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.48 | 2.01 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.48 | 0.88 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.40 | 8.43 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 4.83 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.07 | 0.38 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 14.13 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 0.73 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.41 | 1.89 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 3.23 | 1.10 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.47 | 4.36 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.77 | 25.35 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.645 | 0.908 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.081 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.318 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.10 | 0.53 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.03 | 3.61 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.94 | 1.56 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 8.26 | 1.45 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.82 | 6.95 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.03 | 2.40 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.597 | 0.869 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.197 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.224 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.05 | 0.38 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.15 | 6.19 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.36 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.54 | 2.50 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.38 | 4.28 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.69 | 7.64 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.81 | 11.03 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.292 | 0.825 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.003 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.003 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 0.74 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.99 | 5.28 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 0.41 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.16 | 3.22 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.63 | 3.62 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.51 | 10.57 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.43 | 3.94 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 0.59 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 2.52 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.50 | 0.26 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.71 | 2.84 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 9.37 | 2.30 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.82 | 2.60 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.37 | 2.07 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.676 | 0.831 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.147 | 0.052 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.296 | 0.052 |

221 s.
