# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-21 08:28)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed2.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 2}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network, whole head tuned |
|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.95 | 0.67 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 10.00 | 4.43 |
| A_01f3186607 | ΔH residual | 1.00 | 0.75 | 0.33 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.52 | 2.80 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 13.31 | 0.79 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.55 | 8.85 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.61 | 3.46 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.09 | 0.37 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.08 | 15.47 |
| A_3100da3761 | ΔH residual | 1.00 | 0.66 | 0.84 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 4.87 | 1.35 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.35 | 1.31 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.39 | 4.83 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 15.03 | 27.80 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.653 | 0.847 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.263 | 0.128 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.292 | 0.332 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.04 | 0.73 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.35 | 4.67 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.55 | 0.49 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.17 | 2.90 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 9.48 | 1.12 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 8.73 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.96 | 2.48 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.574 | 0.842 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.275 | 0.225 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.269 |
| A_8448043181 | ring-coupling ratio | 1.00 | 0.99 | 0.19 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.35 | 6.06 |
| A_8448043181 | ΔH residual | 1.00 | 0.57 | 0.35 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.74 | 2.48 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 6.60 | 4.91 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.71 | 7.73 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.74 | 10.19 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.269 | 0.702 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.005 | 0.001 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.001 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 1.00 | 0.85 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 10.65 | 5.65 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.82 | 0.42 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.25 | 3.98 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 15.01 | 4.82 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 14.03 | 10.43 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.62 | 4.32 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 0.67 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.52 | 2.49 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.52 | 0.29 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.76 | 3.17 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 10.69 | 2.31 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.88 | 1.59 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.32 | 1.81 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.676 | 0.819 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.113 | 0.067 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.280 | 0.067 |

154 s.
