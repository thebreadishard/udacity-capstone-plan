# Decision 20 read-in — arm A, cc-pVTZ, tight vs xtight LNO thresholds, against the sealed canonical truth line — 2026-09-12 11:53

Runs `benzene_cc-pvtz_tight` (27 arm points) and `benzene_cc-pvtz_xtight` (27 arm points); same 27 geometries, same DF-RHF reference, frozen core. Δω = a2 of the even part of E_A − E_canonical (the factor-2 erratum of 2026-09-10 applied: frequency bias = a2, curvature bias = 2·a2). Absolute energies not read.

| mode | family | energy | σ tight (µE_h) | σ xtight | Δω tight (cm⁻¹) | Δω xtight | change | a4 tight → xtight (µE_h) |
|---|---|---|---|---|---|---|---|---|
| 6 | CH-oop 865 | bare | 0.010 | 0.003 | +16.29 | +2.08 | -14.21 | -2.53 → -0.27 |
| 6 | CH-oop 865 | composite | 0.007 | 0.004 | +0.47 | +0.11 | -0.35 | -0.04 → +0.02 |
| 12 | CH-ip-bend 1020 | bare | 0.002 | 0.003 | +1.78 | +0.23 | -1.55 | +0.01 → +0.03 |
| 12 | CH-ip-bend 1020 | composite | 0.002 | 0.003 | +0.03 | -0.01 | -0.04 | +0.02 → +0.03 |
| 18 | CC-stretch 1357 | bare | 0.021 | 0.044 | +5.26 | +0.76 | -4.50 | +0.01 → +0.06 |
| 18 | CC-stretch 1357 | composite | 0.021 | 0.044 | +0.79 | +0.23 | -0.56 | +0.10 → +0.06 |

Wall time per arm-A point: tight median 6441 s, xtight median 4576 s (×0.7); xtight points 27.

Composite arm A, largest |Δω| over the three modes: tight 0.79 cm⁻¹ → xtight 0.23 cm⁻¹. Reading for decision 20: if the xtight bias is materially smaller, the residual at tight was LNO truncation; if it is unchanged, the residual sits elsewhere (basis, frozen core, the composite's MP2 term) and tighter thresholds buy nothing at their price. No verdict here; the proposal §3.3 and the M1 note record the numbers.

Printed by probes/m1_xtight_readin.py from the M1 chain's comparison files.