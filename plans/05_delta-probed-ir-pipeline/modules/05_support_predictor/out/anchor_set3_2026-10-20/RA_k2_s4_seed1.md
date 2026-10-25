# T3 — leave-one-anchor-out transfer to CCSD(T)/cc-pVDZ (2026-10-20 18:41)

Model `E7_rungC_chain34_kdfamily_750_2026-10-05_model_n750_seed1.pt` ({'pattern': 'f', 'aux_mode': 'both', 'aux_target': 'projected', 'n': 750, 'seed': 1}); fine-tune 300 epochs at lr 0.001, aux weight 1; low levels {'A_8448043181': 'hessian_b3lyp_analytic.npz', 'A_01f3186607': 'hessian_b3lyp_analytic.npz', 'A_6e858b26e5': 'hessian_b3lyp_analytic.npz', 'B_8b12a55d3a': 'hessian_b3lyp_analytic.npz', 'A_3100da3761': 'hessian_b3lyp_analytic.npz', 'A_a1e6ec1862': 'hessian_b3lyp_analytic.npz', 'A_d09f8d1ef8': 'hessian_b3lyp_analytic.npz', 'A_d9139359ab': 'hessian_b3lyp_analytic.npz'}.

| held-out anchor | read-out | zero rule | α scaling (training anchors) | network as is | network, α tuned | network, head tuned | head tuned, L2 1 |
|---|---|---|---|---|---|---|---|
| A_01f3186607 | ring-coupling ratio | 1.00 | 0.96 | 2.34 | 1.35 | 0.61 | 0.92 |
| A_01f3186607 | ω rms, all modes (cm⁻¹) | 21.12 | 9.50 | 42.18 | 11.97 | 7.05 | 10.07 |
| A_01f3186607 | ΔH residual | 1.00 | 0.73 | 2.22 | 0.87 | 0.51 | 0.72 |
| A_01f3186607 | ω rms ring-ip (cm⁻¹) | 16.40 | 7.50 | 29.12 | 6.65 | 2.10 | 3.44 |
| A_01f3186607 | ω rms CH-stretch (cm⁻¹) | 33.25 | 11.09 | 76.51 | 8.14 | 5.28 | 1.24 |
| A_01f3186607 | ω rms CH-oop (cm⁻¹) | 21.15 | 11.36 | 42.59 | 20.86 | 13.32 | 19.05 |
| A_01f3186607 | ω rms other (cm⁻¹) | 17.20 | 9.63 | 25.04 | 12.18 | 6.88 | 11.13 |
| A_01f3186607 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.5, CH-oop 12.8, ring-ip 2.1, other 6.7 |
| A_3100da3761 | ring-coupling ratio | 1.00 | 1.08 | 2.18 | 0.93 | 0.80 | 0.65 |
| A_3100da3761 | ω rms, all modes (cm⁻¹) | 22.78 | 10.11 | 45.31 | 21.53 | 18.20 | 21.50 |
| A_3100da3761 | ΔH residual | 1.00 | 0.65 | 1.69 | 0.78 | 0.61 | 0.83 |
| A_3100da3761 | ω rms ring-ip (cm⁻¹) | 15.42 | 5.42 | 29.08 | 3.64 | 2.67 | 2.39 |
| A_3100da3761 | ω rms CH-stretch (cm⁻¹) | 35.41 | 2.91 | 78.96 | 6.09 | 1.47 | 4.04 |
| A_3100da3761 | ω rms CH-oop (cm⁻¹) | 13.96 | 11.56 | 31.96 | 9.82 | 8.55 | 9.94 |
| A_3100da3761 | ω rms other (cm⁻¹) | 26.13 | 14.75 | 45.05 | 37.91 | 32.24 | 38.10 |
| A_3100da3761 | spectrum overlap (CC APT) | 0.479 | 0.643 | 0.140 | 0.528 | 0.620 | 0.583 |
| A_3100da3761 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.258 | 0.261 | 0.380 | 0.496 | 0.239 | 0.465 |
| A_3100da3761 | intensity rel. rms (CC APT) | 0.258 | 2.295 | 0.380 | 0.496 | 0.240 | 0.465 |
| A_3100da3761 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 1.5, CH-oop 8.8, ring-ip 2.6, other 33.2 |
| A_6e858b26e5 | ring-coupling ratio | 1.00 | 1.12 | 2.25 | 1.04 | 0.87 | 0.90 |
| A_6e858b26e5 | ω rms, all modes (cm⁻¹) | 19.09 | 11.07 | 40.54 | 9.31 | 7.46 | 7.65 |
| A_6e858b26e5 | ΔH residual | 1.00 | 0.52 | 2.56 | 0.62 | 0.46 | 0.44 |
| A_6e858b26e5 | ω rms ring-ip (cm⁻¹) | 14.88 | 8.00 | 28.00 | 7.29 | 3.46 | 5.10 |
| A_6e858b26e5 | ω rms CH-stretch (cm⁻¹) | 35.58 | 7.90 | 78.00 | 6.32 | 4.77 | 3.39 |
| A_6e858b26e5 | ω rms CH-oop (cm⁻¹) | 5.40 | 18.99 | 20.43 | 14.01 | 13.85 | 12.79 |
| A_6e858b26e5 | ω rms other (cm⁻¹) | 13.02 | 3.97 | 22.55 | 9.03 | 4.86 | 7.55 |
| A_6e858b26e5 | spectrum overlap (CC APT) | 0.626 | 0.602 | 0.193 | 0.693 | 0.731 | 0.720 |
| A_6e858b26e5 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.262 | 0.277 | 0.317 | 0.324 | 0.056 | 0.306 |
| A_6e858b26e5 | intensity rel. rms (CC APT) | 0.300 | 0.311 | 0.328 | 0.324 | 0.161 | 0.306 |
| A_6e858b26e5 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.7, CH-oop 14.2, ring-ip 2.5, other 4.7 |
| A_8448043181 | ring-coupling ratio | 1.00 | 1.07 | 1.70 | 0.61 | 0.23 | 0.47 |
| A_8448043181 | ω rms, all modes (cm⁻¹) | 21.43 | 11.19 | 43.50 | 8.19 | 7.37 | 8.31 |
| A_8448043181 | ΔH residual | 1.00 | 0.55 | 2.22 | 0.69 | 0.35 | 0.61 |
| A_8448043181 | ω rms ring-ip (cm⁻¹) | 14.14 | 8.61 | 27.73 | 6.04 | 2.74 | 5.00 |
| A_8448043181 | ω rms CH-stretch (cm⁻¹) | 38.65 | 5.03 | 81.84 | 2.76 | 7.09 | 6.32 |
| A_8448043181 | ω rms CH-oop (cm⁻¹) | 14.86 | 20.83 | 26.62 | 13.94 | 9.83 | 14.50 |
| A_8448043181 | ω rms other (cm⁻¹) | 13.31 | 2.72 | 21.58 | 8.11 | 11.40 | 7.01 |
| A_8448043181 | spectrum overlap (CC APT) | 0.257 | 0.298 | 0.527 | 0.365 | 0.728 | 0.330 |
| A_8448043181 | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.003 | 0.006 | 0.021 | 0.012 | 0.004 | 0.007 |
| A_8448043181 | intensity rel. rms (CC APT) | 0.734 | 0.734 | 0.734 | 0.734 | 0.004 | 0.734 |
| A_8448043181 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 7.0, CH-oop 9.7, ring-ip 2.7, other 11.2 |
| A_a1e6ec1862 | ring-coupling ratio | 1.00 | 0.98 | 2.03 | 1.44 | 0.55 | 1.04 |
| A_a1e6ec1862 | ω rms, all modes (cm⁻¹) | 21.49 | 9.87 | 41.65 | 13.16 | 6.38 | 10.90 |
| A_a1e6ec1862 | ΔH residual | 1.00 | 0.80 | 2.18 | 1.00 | 0.44 | 0.79 |
| A_a1e6ec1862 | ω rms ring-ip (cm⁻¹) | 16.72 | 8.17 | 30.61 | 9.89 | 3.69 | 6.10 |
| A_a1e6ec1862 | ω rms CH-stretch (cm⁻¹) | 32.88 | 12.21 | 76.20 | 8.34 | 4.66 | 2.64 |
| A_a1e6ec1862 | ω rms CH-oop (cm⁻¹) | 26.43 | 13.40 | 46.40 | 23.23 | 11.67 | 21.22 |
| A_a1e6ec1862 | ω rms other (cm⁻¹) | 16.46 | 8.38 | 23.75 | 11.64 | 5.95 | 10.40 |
| A_a1e6ec1862 | per-family diag rms, head tuned | — | — | — | — | CH-stretch 4.5, CH-oop 14.6, ring-ip 3.6, other 5.9 |
| B_8b12a55d3a | ring-coupling ratio | 1.00 | 1.14 | 2.09 | 1.09 | 0.75 | 0.77 |
| B_8b12a55d3a | ω rms, all modes (cm⁻¹) | 18.96 | 9.26 | 39.69 | 7.67 | 4.13 | 5.73 |
| B_8b12a55d3a | ΔH residual | 1.00 | 0.49 | 2.34 | 0.61 | 0.27 | 0.48 |
| B_8b12a55d3a | ω rms ring-ip (cm⁻¹) | 16.20 | 5.75 | 28.74 | 4.97 | 1.61 | 3.19 |
| B_8b12a55d3a | ω rms CH-stretch (cm⁻¹) | 34.71 | 8.99 | 77.64 | 7.44 | 6.24 | 2.16 |
| B_8b12a55d3a | ω rms CH-oop (cm⁻¹) | 8.29 | 18.01 | 26.70 | 10.54 | 6.92 | 9.06 |
| B_8b12a55d3a | ω rms other (cm⁻¹) | 12.60 | 4.34 | 21.32 | 8.91 | 2.40 | 7.33 |
| B_8b12a55d3a | spectrum overlap (CC APT) | 0.390 | 0.672 | 0.197 | 0.690 | 0.923 | 0.715 |
| B_8b12a55d3a | intensity rel. rms, modes matched by eigenvector (CC APT) | 0.104 | 0.173 | 0.194 | 0.202 | 0.119 | 0.173 |
| B_8b12a55d3a | intensity rel. rms (CC APT) | 0.288 | 0.309 | 0.194 | 0.325 | 0.274 | 0.303 |
| B_8b12a55d3a | per-family diag rms, head tuned | — | — | — | — | CH-stretch 6.5, CH-oop 7.0, ring-ip 2.0, other 2.4 |

670 s.
