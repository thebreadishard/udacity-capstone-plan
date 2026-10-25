# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 18:29)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_7aa232d4e9': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.33 | 0.77 | 0.93 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.58 | 42.18 | 12.08 | 7.32 | 10.04 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 2.22 | 0.88 | 0.52 | 0.72 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.48 | 29.12 | 6.60 | 2.24 | 3.40 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.48 | 76.51 | 8.93 | 5.40 | 1.18 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.40 | 42.59 | 20.94 | 13.93 | 19.08 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.64 | 25.04 | 12.17 | 7.04 | 11.05 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.5, CH-oop 13.4, ring-ip 2.3, other 6.9 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.07 | 2.18 | 0.93 | 0.84 | 0.64 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 45.31 | 22.59 | 21.23 | 22.49 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 1.69 | 0.79 | 0.85 | 0.86 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.41 | 29.08 | 3.67 | 2.49 | 2.48 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 3.23 | 78.96 | 6.88 | 1.80 | 4.09 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.47 | 31.96 | 9.94 | 9.23 | 10.03 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.77 | 45.05 | 39.80 | 37.78 | 39.91 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.645 | 0.140 | 0.483 | 0.578 | 0.542 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.380 | 0.519 | 0.269 | 0.486 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.380 | 0.519 | 0.269 | 0.486 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.8, CH-oop 9.6, ring-ip 2.4, other 39.3 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.10 | 2.25 | 1.03 | 0.80 | 0.87 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.03 | 40.54 | 9.27 | 6.69 | 7.47 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.61 | 0.43 | 0.42 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 7.94 | 28.00 | 7.15 | 2.66 | 4.91 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 8.26 | 78.00 | 7.07 | 3.12 | 3.48 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.82 | 20.43 | 13.68 | 12.87 | 12.42 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 4.03 | 22.55 | 9.14 | 4.50 | 7.62 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.597 | 0.193 | 0.683 | 0.775 | 0.721 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.276 | 0.317 | 0.324 | 0.073 | 0.304 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.310 | 0.328 | 0.324 | 0.168 | 0.304 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 3.1, CH-oop 13.0, ring-ip 2.2, other 4.3 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.05 | 1.70 | 0.59 | 0.28 | 0.45 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.15 | 43.50 | 8.21 | 7.10 | 8.29 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.22 | 0.69 | 0.33 | 0.60 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.54 | 27.73 | 5.98 | 2.60 | 4.98 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.38 | 81.84 | 3.51 | 5.72 | 6.27 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.69 | 26.62 | 13.87 | 10.06 | 14.46 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.81 | 21.58 | 8.13 | 11.13 | 7.04 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.292 | 0.527 | 0.351 | 0.789 | 0.332 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.021 | 0.011 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 5.7, CH-oop 9.9, ring-ip 2.6, other 10.7 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 2.03 | 1.45 | 0.61 | 1.04 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.99 | 41.65 | 13.28 | 6.45 | 10.89 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 2.18 | 1.00 | 0.44 | 0.79 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.16 | 30.61 | 9.97 | 3.57 | 6.08 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.63 | 76.20 | 9.15 | 4.47 | 2.58 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.51 | 46.40 | 23.31 | 11.96 | 21.26 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.43 | 23.75 | 11.65 | 6.05 | 10.35 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.4, CH-oop 15.4, ring-ip 3.5, other 6.0 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.13 | 2.09 | 1.09 | 0.63 | 0.76 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 39.69 | 7.82 | 4.37 | 5.75 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.50 | 2.34 | 0.61 | 0.27 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.71 | 28.74 | 4.97 | 1.33 | 3.26 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 9.37 | 77.64 | 8.26 | 7.61 | 2.17 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 17.82 | 26.70 | 10.54 | 6.53 | 9.06 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.37 | 21.32 | 8.95 | 2.47 | 7.34 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.676 | 0.197 | 0.693 | 0.927 | 0.709 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.147 | 0.194 | 0.202 | 0.133 | 0.173 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.296 | 0.194 | 0.325 | 0.282 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.9, CH-oop 6.6, ring-ip 1.6, other 2.5 |

721 s.
