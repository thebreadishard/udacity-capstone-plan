# Probe M1 — basis-set sensitivity of the canonical curvature, cc-pVDZ → cc-pVTZ (decision 26, input i)

Truth lines `benzene_cc-pvdz_tight` and `benzene_cc-pvtz_tight` (same 27 geometries, same DF-RHF reference, frozen core); MP2 from the arms' files at the same points. Even-part fit a0 + a2 q² + a4 q⁴ per basis; the table gives Δ(2·a2) = TZ − DZ in cm⁻¹. Absolute curvatures are not printed.

| mode | family | total CCSD(T) | SCF (DF-RHF) | CCSD(T) correlation | of which (T) | MP2 correlation (full space, from the arms' files) | MP2 share of the correlation change | σ(total) DZ / TZ (µE_h) |
|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop 865 | +133.7 | +88.4 | +45.3 | -5.2 | +29.5 | 0.65 | 0.018 / 0.024 |
| 12 | CH-ip-bend 1020 | -66.5 | -44.8 | -21.7 | -0.8 | -23.6 | 1.09 | 0.003 / 0.002 |
| 18 | CC-stretch 1357 | -145.3 | -101.2 | -44.1 | +5.4 | -32.2 | 0.73 | 0.001 / 0.001 |

Reading: the DZ → TZ change is a measured lower bound on the anchor's distance from the basis-set limit per mode (the first step of a convergent series). The SCF and MP2 columns say how much of it a composite anchor could carry at negligible cost (SCF extrapolated in a larger basis; an MP2-level correlation correction, as the composite of §3.3 already does for the LNO truncation). No verdict. Printed by probes/m1_basis_sensitivity.py.