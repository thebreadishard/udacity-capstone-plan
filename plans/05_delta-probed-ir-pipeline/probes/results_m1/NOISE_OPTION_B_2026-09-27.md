# Decision 45, option B — noise floor of the tight cc-pVTZ labels from the anchor's points (results_m1/naphthalene_cc-pvtz_tight_m3), µE_h; printed 2026-09-27 02:04 by probes/m1_noise_option_b.py

## mode 12 (CH-oop, 785.3 cm⁻¹): amplitudes [0.25, 0.5, 0.75, 1.0] (9 points)

| quantity | k | c₄ | even residuals (µE_h) | σ_even (dof) | with q⁶: σ (dof) | g | h | odd residuals (µE_h) | σ_odd (dof) |
|---|---|---|---|---|---|---|---|---|---|
| SCF | +4424.5 | +24.8 | -0.04, -0.05, +0.05, -0.01 | 0.06 (2) | 0.00 (1) | +39.704 | +0.460 | -0.000, -0.000, +0.000, -0.000 | 0.000 (2) |
| LNO-CCSD(T) corr | -808.0 | -8.3 | +0.02, +0.02, -0.02, +0.01 | 0.03 (2) | 0.00 (1) | -37.606 | -0.052 | +0.000, +0.000, -0.001, +0.000 | 0.001 (2) |
| MP2 corr | -1175.3 | +148.1 | -0.32, -0.45, +0.42, -0.10 | 0.50 (2) | 0.03 (1) | -27.455 | +0.046 | -0.003, -0.001, +0.003, -0.001 | 0.003 (2) |
| composite | +3175.5 | +171.9 | -0.36, -0.50, +0.47, -0.12 | 0.55 (2) | 0.03 (1) | +2.250 | +0.512 | -0.003, -0.001, +0.003, -0.001 | 0.003 (2) |

## mode 22 (CH-ip-bend, 1045.1 cm⁻¹): amplitudes [0.5, 1.0] (5 points)

Two amplitudes: (k, c₄) and (g, h) are determined exactly, no residual, no σ (decision 45: the in-plane families keep the coarser spacing).

| quantity | k | c₄ | g | h | max |odd| / even(1) |
|---|---|---|---|---|---|
| SCF | +5019.5 | +12.2 | +1.666 | -0.197 | 5.8e-04 |
| LNO-CCSD(T) corr | -318.4 | -0.6 | -1.919 | -0.003 | 1.2e-02 |
| MP2 corr | -332.4 | -0.2 | -1.051 | -0.004 | 6.3e-03 |
| composite | +4644.6 | +11.7 | -0.250 | -0.198 | 1.9e-04 |

## mode 31 (CC-stretch, 1409.9 cm⁻¹): amplitudes [0.5, 1.0] (5 points)

Two amplitudes: (k, c₄) and (g, h) are determined exactly, no residual, no σ (decision 45: the in-plane families keep the coarser spacing).

| quantity | k | c₄ | g | h | max |odd| / even(1) |
|---|---|---|---|---|---|
| SCF | +5840.9 | +49.7 | +46.445 | -5.362 | 1.4e-02 |
| LNO-CCSD(T) corr | +515.6 | -16.9 | -35.711 | +2.135 | 1.3e-01 |
| MP2 corr | +1078.1 | -36.5 | -53.741 | +4.579 | 9.3e-02 |
| composite | +6250.6 | +34.6 | +10.527 | -3.237 | 2.3e-03 |

**Reading, mode 12, composite:** σ_even 0.55 µE_h (2 dof), σ_odd 0.003 µE_h (2 dof) → per energy ≈ 0.78 / 0.00 µE_h (× √2, approximate); against the response even(1) = +1631 µE_h that is 4.8e-04 / 3.0e-06 relative. The even-part residual still contains the q⁶ truncation of the two-term model (see the q⁶ column); the odd-part σ is the cleaner noise witness.

