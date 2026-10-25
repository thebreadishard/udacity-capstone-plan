# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 06:48)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed0.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 0}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_45187bb7c8': 'hessian_b3lyp_analytic.npz', 'A_ff98e1160d': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 0.31 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 8.90 | 4.36 |
| A_01f3186607 | ΔH residual | 1.00 | 0.70 | 0.24 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 6.62 | 1.05 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 9.31 | 2.23 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.33 | 7.53 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.60 | 5.35 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.12 | 0.52 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.12 | 15.23 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.82 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.83 | 1.67 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 1.74 | 0.87 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.63 | 5.52 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.07 | 27.26 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.648 | 0.775 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.263 | 0.150 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.296 | 0.150 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.11 | 0.58 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 10.89 | 3.73 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 0.32 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.91 | 2.60 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 6.27 | 2.42 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 19.11 | 6.29 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.95 | 2.66 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.639 | 0.873 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.128 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.198 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.10 | 0.23 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 10.98 | 4.96 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 0.27 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.24 | 3.27 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 3.52 | 3.04 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.92 | 7.65 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.70 | 6.19 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.331 | 0.712 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.000 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.000 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.95 | 0.64 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.26 | 5.69 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.77 | 0.37 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 7.30 | 4.10 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 10.31 | 3.55 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.35 | 10.78 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.35 | 4.50 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.21 | 0.83 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 8.86 | 2.88 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.48 | 0.32 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 4.97 | 3.42 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 7.32 | 1.25 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.13 | 2.79 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.30 | 2.80 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.686 | 0.825 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.108 | 0.060 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.277 | 0.060 |

246 s.
