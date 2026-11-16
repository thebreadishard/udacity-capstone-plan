# Certificate: Oc1ccccc1

Oc1ccccc1: the harmonic infrared spectrum of ΔH network v1.3 (3 seeds), B3LYP/6-31G* corrected towards ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians), with the error measured on molecules the network never saw. 32 of 33 bands are licensed: a band is licensed when its family's error is within 3 cm⁻¹ on every hold-out (ring-ip, CH-stretch, CH-oop, other), the molecule lies inside the training sizes, the band is real for the seeds' mean and for every seed, and a band of a C–H family moves carbon-bound hydrogens. 'other' is within the licence line on hold-out (a) at 2.78 cm⁻¹, on 8 molecules: resampling those molecules puts the error between 1.68 and 3.76 cm⁻¹, and 30% of the resamples lie above the line. Not in that error: the same molecule turned, mirrored or listed in another atom order was seen to get positions up to 10.73 cm⁻¹ away, more than the licence line. Coupled cluster: not measured for this network version. The scaled B3LYP positions are a baseline for comparison only.

## Molecule

- C6H6O, 13 atoms; the training set spans 8–30 atoms: inside
- in the network's training set: the hold-out error is not this molecule's measure

## Spectrum, band by band (network v1.3, seeds 0, 1, 2)

| position (cm⁻¹) | height (km/mol) | range over seeds and mean | B3LYP | scaled B3LYP | family | licensed | family's measured error (a) / (b), cm⁻¹ |
|---|---|---|---|---|---|---|---|
| 246.6 | 0.0 | 246.5–246.9 | 233.8 | 228.9 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 418.2 | 0.0 | 417.3–418.6 | 406.9 | 398.4 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 429.6 | 0.0 | 426.6–432.6 | 359.6 | 352.0 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 435.7 | 0.0 | 433.4–439.3 | 422.6 | 413.7 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 529.8 | 0.0 | 528.9–530.8 | 518.2 | 507.3 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 539.0 | 0.0 | 538.8–539.4 | 535.4 | 524.2 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 636.5 | 0.0 | 636.2–636.6 | 632.9 | 619.6 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 713.4 | 0.0 | 712.9–714.0 | 700.0 | 685.3 | CH-oop | yes | 1.64 / 1.88 |
| 779.3 | 0.0 | 778.6–780.5 | 762.5 | 746.5 | CH-oop | yes | 1.64 / 1.88 |
| 840.5 | 0.0 | 839.8–841.3 | 833.1 | 815.6 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 844.5 | 0.0 | 844.1–845.0 | 824.4 | 807.1 | CH-oop | yes | 1.64 / 1.88 |
| 910.2 | 0.0 | 909.3–911.0 | 885.1 | 866.5 | CH-oop | yes | 1.64 / 1.88 |
| 984.0 | 0.0 | 982.9–985.5 | 951.9 | 931.9 | CH-oop | yes | 1.64 / 1.88 |
| 1009.3 | 0.0 | 1007.2–1010.4 | 980.0 | 959.5 | CH-oop | yes | 1.64 / 1.88 |
| 1021.6 | 0.0 | 1021.2–1021.8 | 1014.9 | 993.6 | ring-ip | yes | 1.43 / 1.91 |
| 1062.1 | 0.0 | 1062.1–1062.3 | 1052.5 | 1030.4 | ring-ip | yes | 1.43 / 1.91 |
| 1112.8 | 0.0 | 1112.3–1113.2 | 1103.8 | 1080.6 | ring-ip | yes | 1.43 / 1.91 |
| 1180.1 | 0.0 | 1179.9–1180.3 | 1188.3 | 1151.5 | ring-ip | yes | 1.43 / 1.91 |
| 1203.3 | 0.0 | 1202.2–1204.1 | 1202.0 | 1164.7 | ring-ip | yes | 1.43 / 1.91 |
| 1230.7 | 0.0 | 1230.0–1231.5 | 1212.9 | 1175.3 | ring-ip | yes | 1.43 / 1.91 |
| 1318.4 | 0.0 | 1317.9–1319.1 | 1304.9 | 1264.5 | ring-ip | yes | 1.43 / 1.91 |
| 1344.5 | 0.0 | 1344.2–1344.9 | 1367.4 | 1325.0 | ring-ip | yes | 1.43 / 1.91 |
| 1389.5 | 0.0 | 1389.0–1390.3 | 1385.8 | 1342.9 | ring-ip | yes | 1.43 / 1.91 |
| 1534.2 | 0.0 | 1534.1–1534.4 | 1520.8 | 1473.7 | ring-ip | yes | 1.43 / 1.91 |
| 1564.8 | 0.0 | 1564.1–1565.4 | 1550.6 | 1502.5 | ring-ip | yes | 1.43 / 1.91 |
| 1692.6 | 0.0 | 1691.9–1693.4 | 1657.2 | 1605.8 | ring-ip | yes | 1.43 / 1.91 |
| 1704.8 | 0.0 | 1704.3–1705.6 | 1670.0 | 1618.2 | ring-ip | yes | 1.43 / 1.91 |
| 3208.2 | 0.0 | 3207.5–3208.8 | 3163.9 | 3037.3 | CH-stretch | yes | 0.95 / 2.19 |
| 3228.1 | 0.0 | 3227.8–3228.5 | 3185.8 | 3058.3 | CH-stretch | yes | 0.95 / 2.19 |
| 3236.5 | 0.0 | 3236.4–3236.6 | 3194.0 | 3066.2 | CH-stretch | yes | 0.95 / 2.19 |
| 3252.2 | 0.0 | 3251.5–3253.4 | 3209.7 | 3081.3 | CH-stretch | yes | 0.95 / 2.19 |
| 3260.4 | 0.0 | 3259.4–3261.4 | 3217.4 | 3088.7 | CH-stretch | yes | 0.95 / 2.19 |
| 3789.3 | 0.0 | 3788.4–3789.9 | 3749.8 | 3599.8 | CH-stretch | no: 100% of its hydrogen motion is on N–H, O–H or S–H, which the rule counts as CH-stretch | 0.95 / 2.19 |

*Positions:* harmonic positions: the anharmonic shift is not included in this version.

## What the measured error does not cover

Each hold-out molecule was read in one orientation and one atom order. For this molecule:

- Another atom order of the same molecule moved a position by up to 10.73 cm⁻¹, the largest seen on 3 molecule(s) in arbitrary orders; that is more than the licence line of 3 cm⁻¹.
- A rigid rotation of the molecule moved a position by up to 0.00 cm⁻¹, the largest seen on 4 molecule(s) without a linear group.
- The molecule's mirror image moved a position by up to 2.60 cm⁻¹, the largest seen on 4 molecule(s) without a linear group.
- Another listing of the same atoms in an xyz file moved a position by up to 3.07 cm⁻¹, the largest seen on 4 molecule(s) without a linear group; that is more than the licence line of 3 cm⁻¹.
- The heights are B3LYP's: the dipole derivatives are not corrected.
- One conformer was computed, the one the optimisation reached from aromir's start geometry; another conformer has another spectrum.

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
