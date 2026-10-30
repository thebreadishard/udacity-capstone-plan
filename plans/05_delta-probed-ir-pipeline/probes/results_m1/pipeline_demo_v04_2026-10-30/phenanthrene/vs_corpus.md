# phenanthrene against the corpus folder A_541c53d1a5

- optimised geometry: largest coordinate difference 1.07e-04 bohr
- analytic B3LYP frequencies: largest difference 0.0089 cm⁻¹
- network spectrum (E7_rungC_chain35_analytic_model_n750_seed0.pt, E7_rungC_chain35_analytic_model_n750_seed1.pt, E7_rungC_chain35_analytic_model_n750_seed2.pt): 66 bands, positions within 1.2 cm⁻¹, heights within 0.33 km/mol
- scaled B3LYP baseline: positions within 0.1 cm⁻¹, heights within 0.02 km/mol

## Against the ωB97X truth (A_541c53d1a5/hessian_wb97x_analytic.npz)

Position error, rms over the modes (cm⁻¹), each B3LYP mode paired by its shape with its truth mode:

| family | modes | network | B3LYP |
|---|---|---|---|
| CH-oop | 11 | 1.39 | 24.33 |
| CH-stretch | 10 | 0.29 | 43.88 |
| other | 20 | 1.32 | 9.5 |
| ring-ip | 25 | 1.14 | 18.81 |
| all | 66 | 1.16 | 23.49 |

Spectrum overlap with the truth (1 = the same shape): network 0.9959, B3LYP 0.2871. Height error (0 = the same heights): network 0.077, B3LYP 0.177.

The network's own evaluation of this molecule (hold-out (a), seed means): corrected-frequency rms 1.3807 cm⁻¹, overlap 0.9936, height error 0.0865.

The scaled-B3LYP baseline is not read against this truth: PAHdb's factors aim at measured band positions, the anharmonic shift folded in, while the truth here is harmonic ωB97X; the baseline is compared where a laboratory record exists.
