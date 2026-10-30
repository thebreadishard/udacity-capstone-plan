# benzene against the corpus folder A_8448043181

- optimised geometry: largest coordinate difference 2.21e-07 bohr
- analytic B3LYP frequencies: largest difference 0.0003 cm⁻¹
- network spectrum (E7_rungC_chain35_analytic_model_n750_seed0.pt, E7_rungC_chain35_analytic_model_n750_seed1.pt, E7_rungC_chain35_analytic_model_n750_seed2.pt): 30 bands, positions within 0.0 cm⁻¹, heights within 0.07 km/mol
- scaled B3LYP baseline: positions within 0.0 cm⁻¹, heights within 0.07 km/mol

## Against the ωB97X truth (A_8448043181/hessian_wb97x_analytic.npz)

Position error, rms over the modes (cm⁻¹), each B3LYP mode paired by its shape with its truth mode:

| family | modes | network | B3LYP |
|---|---|---|---|
| CH-oop | 6 | 1.97 | 23.99 |
| CH-stretch | 6 | 0.92 | 42.92 |
| other | 5 | 0.47 | 10.03 |
| ring-ip | 13 | 1.2 | 17.45 |
| all | 30 | 1.27 | 25.14 |

Spectrum overlap with the truth (1 = the same shape): network 0.9848, B3LYP 0.3238. Height error (0 = the same heights): network 0.001, B3LYP 0.018.

The network's own evaluation of this molecule (hold-out (a), seed means): corrected-frequency rms 1.6565 cm⁻¹, overlap 0.9823, height error 0.0012.

The scaled-B3LYP baseline is not read against this truth: PAHdb's factors aim at measured band positions, the anharmonic shift folded in, while the truth here is harmonic ωB97X; the baseline is compared where a laboratory record exists.
