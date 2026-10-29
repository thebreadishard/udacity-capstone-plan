# Analytic Hessian files with a stale `freq_cm` field (TASKS 147)

1724 files: 894 with the software stamp, 830 without; 8 store a `freq_cm` more than 0.01 cm⁻¹ from their own `H_projected`; 0 differ in mode count. Files whose lowest frequency could cross a verdict bound (0, 10 cm⁻¹): 0.

| molecule | file | stamped | largest difference (cm⁻¹) | lowest, stored | lowest, own | bound at risk |
|---|---|---|---|---|---|---|
| A2_13bafae8e0 | hessian_b3lyp_analytic.npz | no | 0.727 | 58.66 | 58.68 | none |
| A2_13bafae8e0 | hessian_wb97x_analytic.npz | no | 0.756 | 79.02 | 79.07 | none |
| A2_22d0e8105c | hessian_b3lyp_analytic.npz | no | 0.726 | 77.52 | 77.56 | none |
| A2_22d0e8105c | hessian_wb97x_analytic.npz | no | 0.754 | 98.65 | 98.71 | none |
| A2_3a2982dd85 | hessian_b3lyp_analytic.npz | no | 0.758 | 83.2 | 83.22 | none |
| A2_3a2982dd85 | hessian_wb97x_analytic.npz | no | 0.771 | 97.12 | 97.16 | none |
| A_8448043181 | hessian_b3lyp_analytic.npz | no | 0.687 | 415.26 | 415.4 | none |
| A_8448043181 | hessian_wb97x_analytic.npz | no | 0.708 | 425.39 | 425.54 | none |
