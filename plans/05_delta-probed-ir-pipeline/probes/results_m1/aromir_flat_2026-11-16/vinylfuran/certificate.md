# Certificate: C=Cc1ccoc1

C=Cc1ccoc1: the harmonic infrared spectrum of ΔH network v1.3 (3 seeds), B3LYP/6-31G* corrected towards ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians), with the error measured on molecules the network never saw. 33 of 33 bands are licensed: a band is licensed when its family's error is within 3 cm⁻¹ on every hold-out (ring-ip, CH-stretch, CH-oop, other), the molecule lies inside the training sizes, its low-level mode is real, the band is real for the seeds' mean and for every seed, and a band of a C–H family moves carbon-bound hydrogens. 'other' is within the licence line on hold-out (a) at 2.78 cm⁻¹, on 8 molecules: resampling those molecules puts the error between 1.68 and 3.76 cm⁻¹, and 30% of the resamples lie above the line. Not in that error: the same molecule turned, mirrored or listed in another atom order was seen to get positions up to 10.73 cm⁻¹ away, more than the licence line. Coupled cluster: not measured for this network version. The scaled B3LYP positions are a baseline for comparison only.

## Molecule

- C6H6O, 13 atoms; the training set spans 8–30 atoms: inside
- not in the training set or a hold-out: the network has not seen it

## Spectrum, band by band (network v1.3, seeds 0, 1, 2)

| position (cm⁻¹) | height (km/mol) | range over seeds and mean | B3LYP | scaled B3LYP | family | licensed | family's measured error (a) / (b), cm⁻¹ |
|---|---|---|---|---|---|---|---|
| 63.9 | 0.05 | 60.1–67.7 | 20.3 | 19.9 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 216.3 | 0.01 | 215.7–217.4 | 210.1 | 205.7 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 257.4 | 1.79 | 254.9–261.6 | 248.7 | 243.5 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 465.7 | 1.26 | 465.1–466.3 | 461.7 | 452.0 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 585.0 | 8.9 | 583.6–587.1 | 573.5 | 561.5 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 634.5 | 9.51 | 633.3–635.3 | 619.3 | 606.3 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 655.9 | 12.63 | 655.5–656.1 | 649.7 | 636.0 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 733.4 | 1.22 | 732.5–734.3 | 711.5 | 696.6 | CH-oop | yes | 1.64 / 1.88 |
| 754.5 | 13.96 | 749.5–757.2 | 733.0 | 717.6 | CH-oop | yes | 1.64 / 1.88 |
| 817.4 | 38.78 | 817.0–818.1 | 791.7 | 775.1 | CH-oop | yes | 1.64 / 1.88 |
| 879.5 | 4.27 | 877.2–882.1 | 850.1 | 832.3 | CH-oop | yes | 1.64 / 1.88 |
| 897.2 | 22.87 | 896.8–897.5 | 889.6 | 871.0 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 948.1 | 39.42 | 946.3–951.5 | 913.8 | 894.6 | CH-oop | yes | 1.64 / 1.88 |
| 983.8 | 7.19 | 982.9–984.6 | 976.1 | 955.6 | ring-ip | yes | 1.43 / 1.91 |
| 1052.6 | 12.27 | 1050.7–1055.7 | 1033.8 | 1012.1 | CH-oop | yes | 1.64 / 1.88 |
| 1064.4 | 11.88 | 1064.1–1064.5 | 1056.7 | 1034.5 | ring-ip | yes | 1.43 / 1.91 |
| 1093.3 | 20.44 | 1092.3–1094.1 | 1085.5 | 1062.7 | ring-ip | yes | 1.43 / 1.91 |
| 1117.0 | 9.77 | 1115.6–1118.0 | 1113.7 | 1079.2 | ring-ip | yes | 1.43 / 1.91 |
| 1230.0 | 29.25 | 1229.8–1230.3 | 1212.4 | 1174.8 | ring-ip | yes | 1.43 / 1.91 |
| 1261.3 | 9.91 | 1260.8–1261.9 | 1255.7 | 1216.8 | ring-ip | yes | 1.43 / 1.91 |
| 1300.3 | 2.96 | 1300.1–1300.6 | 1291.9 | 1251.8 | ring-ip | yes | 1.43 / 1.91 |
| 1352.1 | 0.93 | 1347.4–1354.5 | 1347.9 | 1306.1 | ring-ip | yes | 1.43 / 1.91 |
| 1424.7 | 5.48 | 1423.1–1427.1 | 1406.6 | 1363.0 | ring-ip | yes | 1.43 / 1.91 |
| 1490.4 | 4.58 | 1489.2–1491.3 | 1483.6 | 1437.7 | ring-ip | yes | 1.43 / 1.91 |
| 1571.5 | 17.35 | 1571.3–1572.0 | 1549.1 | 1501.1 | ring-ip | yes | 1.43 / 1.91 |
| 1661.8 | 3.87 | 1660.6–1662.8 | 1632.5 | 1581.9 | ring-ip | yes | 1.43 / 1.91 |
| 1751.0 | 15.76 | 1750.1–1752.1 | 1715.7 | 1662.5 | ring-ip | yes | 1.43 / 1.91 |
| 3199.7 | 18.53 | 3197.2–3201.6 | 3157.0 | 3030.7 | CH-stretch | yes | 0.95 / 2.19 |
| 3209.8 | 4.39 | 3207.6–3211.6 | 3167.5 | 3040.8 | CH-stretch | yes | 0.95 / 2.19 |
| 3293.2 | 15.21 | 3290.7–3296.3 | 3247.4 | 3117.5 | CH-stretch | yes | 0.95 / 2.19 |
| 3304.7 | 2.01 | 3303.7–3306.5 | 3262.2 | 3131.7 | CH-stretch | yes | 0.95 / 2.19 |
| 3339.7 | 0.91 | 3339.0–3340.2 | 3297.3 | 3165.4 | CH-stretch | yes | 0.95 / 2.19 |
| 3344.6 | 1.18 | 3343.8–3345.4 | 3304.8 | 3172.6 | CH-stretch | yes | 0.95 / 2.19 |

*Positions:* harmonic positions: the anharmonic shift is not included in this version.

## What the measured error does not cover

Each hold-out molecule was read in one orientation and one atom order. For this molecule:

- Another atom order of the same molecule moved a position by up to 10.73 cm⁻¹, the largest seen on 3 molecule(s) in arbitrary orders; that is more than the licence line of 3 cm⁻¹.
- A rigid rotation of the molecule moved a position by up to 0.00 cm⁻¹, the largest seen on 4 molecule(s) without a linear group.
- The molecule's mirror image moved a position by up to 2.60 cm⁻¹, the largest seen on 4 molecule(s) without a linear group.
- Another listing of the same atoms in an xyz file moved a position by up to 3.07 cm⁻¹, the largest seen on 4 molecule(s) without a linear group; that is more than the licence line of 3 cm⁻¹.
- The heights are B3LYP's: the dipole derivatives are not corrected.
- One conformer was computed, the one the optimisation reached from aromir's start geometry; another conformer has another spectrum.
- The start geometry led to a saddle point (a mode at -12 cm⁻¹): the atoms were moved up to 0.3 bohr along that mode and optimised again, so the structure computed is the one that step led to, one of two.

## How well the network is known

The rms error of the corrected band positions of the seeds' mean against ωB97X/6-31G*, in cm⁻¹: what this certificate's positions are. In square brackets the 95 % interval when the hold-out's molecules are resampled. The licence is read on the band error of the seeds' mean, the error of what the release delivers, as recorded to two decimals; chosen on 16 November 2026, after it and the first-order error per seed had both been measured on both hold-outs.

| family | (a), 8 molecules | (b), 39 molecules | within the licence line |
|---|---|---|---|
| ring-ip | 1.43 [1.13–1.70], 199 bands | 1.91 [1.84–2.00], 1164 bands | yes |
| CH-stretch | 0.95 [0.39–1.48], 73 bands | 2.19 [1.80–2.53], 401 bands | yes |
| CH-oop | 1.64 [1.19–1.97], 46 bands | 1.88 [1.56–2.16], 84 bands | yes |
| other | 2.78 [1.68–3.76], 156 bands | 2.77 [2.56–2.97], 1225 bands | yes |

- 'other' is within the licence line on hold-out (a) at 2.78 cm⁻¹, on 8 molecules: resampling those molecules puts the error between 1.68 and 3.76 cm⁻¹, and 30% of the resamples lie above the line.
- (a): eight molecules set aside on 19 September 2026, before any network was trained, and never trained on in any form (two more molecules of that set, 2-naphthoic acid and benzonitrile, are left out of this read because the network had trained on them under another identifier)
- (b): every substituted molecule of two ring scaffolds, set aside on 8 October 2026; the network trained on no molecule of either scaffold
- sources: every error in this record: `aromir evaluate` on the two hold-outs as probes/results_m1/aromir_audit_fixes_2026-11-16/holdouts_for_aromir.py of thebreadishard/udacity-capstone-plan (plan 05) writes them; counterpart for the band errors: probes/results_m1/aromir_product_error_2026-11-16/product_error.json; the hold-outs' molecules, and the first-order errors the training runs recorded themselves (within 0.08 cm⁻¹): E7_rungC_chain35_analytic_eval_frozenb_seed0.json, E7_rungC_chain35_analytic_eval_frozenb_seed1.json, E7_rungC_chain35_analytic_eval_frozenb_seed2.json, E7_rungC_chain35_analytic_a8read_seed0.json, E7_rungC_chain35_analytic_a8read_seed1.json, E7_rungC_chain35_analytic_a8read_seed2.json

For comparison, the first-order error of each seed alone, the number a training run reports: its mean over the seeds, each seed's value in brackets. It is not the error of what is printed above.

| family | (a), 8 molecules | (b), 39 molecules |
|---|---|---|
| ring-ip | 1.77 (1.95, 1.68, 1.70) | 2.12 (2.25, 2.02, 2.11) |
| CH-stretch | 1.19 (0.91, 1.74, 0.91) | 2.50 (1.91, 3.51, 2.08) |
| CH-oop | 2.17 (2.46, 2.05, 1.99) | 2.73 (2.46, 2.93, 2.80) |
| other | 3.62 (4.09, 3.27, 3.51) | 3.89 (3.65, 4.51, 3.51) |

A family is a rule, and its name is the evaluation's:

- ring-ip: between 950 and 1750 cm⁻¹ and in the molecular plane: ring stretches and in-plane bends, and with them every other mode there, such as a C=O stretch or a CH₃ deformation; in a non-planar molecule every mode in that window.
- CH-stretch: above 2800 cm⁻¹ with most of its motion on hydrogens: the C–H stretches, and by the same rule an O–H or N–H stretch.
- CH-oop: between 600 and 1050 cm⁻¹, out of the molecular plane and on hydrogens; a non-planar molecule has none, and its C–H wags fall under other or ring-ip.
- other: every mode the three rules above do not take.
