# Probe M1 — the cheap basis line: DF-RHF and DF-MP2 at the 27 benzene points, cc-pVTZ → larger bases — 2026-09-12 12:13

Reference points: `benzene_cc-pvtz_tight` (same geometries, same DF-RHF reference, frozen core 6). Δω = ½·Δ(2·a2) per mode in cm⁻¹; even-part fit a0 + a2 q² + a4 q⁴. Absolute energies not printed.

| mode | family | part | DZ → TZ (from m1_basis_sensitivity) | TZ → CC-PVQZ | TZ → CC-PV5Z |
|---|---|---|---|---|---|
| 6 | CH-oop 865 | SCF | +44.2 | +1.8 | +3.8 |
| 6 | CH-oop 865 | MP2 correlation | +14.7 | -1.0 | — |
| 12 | CH-ip-bend 1020 | SCF | -22.4 | -2.4 | -2.8 |
| 12 | CH-ip-bend 1020 | MP2 correlation | -11.8 | -2.4 | — |
| 18 | CC-stretch 1357 | SCF | -50.6 | -4.6 | -3.1 |
| 18 | CC-stretch 1357 | MP2 correlation | -16.1 | -8.0 | — |

Reading: if the TZ → QZ step is small next to the DZ → TZ step, the SCF and MP2 parts of a composite anchor are near their limits at TZ and the remaining basis error sits in the CC correlation part beyond MP2; if not, the composite (P18) must carry the SCF/MP2 basis correction explicitly. No verdict; decision 26 input (ii). Printed by probes/m1_basis_scf_mp2_line.py.