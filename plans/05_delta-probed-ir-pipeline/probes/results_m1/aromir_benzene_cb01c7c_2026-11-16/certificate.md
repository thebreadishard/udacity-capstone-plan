# Certificate: c1ccccc1

c1ccccc1: the harmonic infrared spectrum of ΔH network v1.3 (3 seeds), B3LYP/6-31G* corrected towards ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians), with the error measured on molecules the network never saw. 30 of 30 bands are licensed: a band is licensed when its family's error is within 3 cm⁻¹ on every hold-out (ring-ip, CH-stretch, CH-oop, other), the molecule lies inside the training sizes, the band is real for the seeds' mean and for every seed, and a band of a C–H family moves carbon-bound hydrogens. 'other' is within the licence line on hold-out (a) at 2.78 cm⁻¹, on 8 molecules: resampling those molecules puts the error between 1.68 and 3.76 cm⁻¹, and 30% of the resamples lie above the line. Not in that error: the same molecule turned, mirrored or listed in another atom order was seen to get positions up to 10.73 cm⁻¹ away, more than the licence line. Coupled cluster: not measured for this network version. The scaled B3LYP positions are a baseline for comparison only.

## Molecule

- C6H6, 12 atoms; the training set spans 8–30 atoms: inside
- in hold-out (a): never trained on; the measured error includes it

## Spectrum, band by band (network v1.3, seeds 0, 1, 2)

| position (cm⁻¹) | height (km/mol) | range over seeds and mean | B3LYP | scaled B3LYP | family | licensed | family's measured error (a) / (b), cm⁻¹ |
|---|---|---|---|---|---|---|---|
| 425.8 | 0.0 | 423.9–427.1 | 415.1 | 406.4 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 425.9 | 0.0 | 424.0–427.2 | 415.1 | 406.3 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 625.1 | 0.0 | 624.9–625.2 | 621.9 | 608.8 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 625.1 | 0.0 | 625.0–625.2 | 621.9 | 608.8 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 701.4 | 77.54 | 700.7–702.4 | 694.6 | 680.0 | CH-oop | yes | 1.64 / 1.88 |
| 733.6 | 0.0 | 733.1–734.2 | 717.8 | 702.7 | other | yes, on thin ground (see above) | 2.78 / 2.77 |
| 882.4 | 0.0 | 881.2–883.3 | 864.7 | 846.6 | CH-oop | yes | 1.64 / 1.88 |
| 883.2 | 0.0 | 881.9–884.5 | 864.7 | 846.6 | CH-oop | yes | 1.64 / 1.88 |
| 998.4 | 0.0 | 997.0–999.9 | 969.3 | 948.9 | CH-oop | yes | 1.64 / 1.88 |
| 998.5 | 0.0 | 997.4–1000.2 | 969.3 | 948.9 | CH-oop | yes | 1.64 / 1.88 |
| 1023.4 | 0.0 | 1022.9–1024.1 | 1019.9 | 998.4 | ring-ip | yes | 1.43 / 1.91 |
| 1033.0 | 0.0 | 1032.9–1033.2 | 1020.5 | 999.1 | ring-ip | yes | 1.43 / 1.91 |
| 1036.3 | 0.0 | 1035.7–1036.9 | 1011.0 | 989.7 | CH-oop | yes | 1.64 / 1.88 |
| 1079.0 | 3.53 | 1078.6–1079.5 | 1069.1 | 1046.7 | ring-ip | yes | 1.43 / 1.91 |
| 1079.0 | 3.53 | 1078.6–1079.5 | 1069.1 | 1046.7 | ring-ip | yes | 1.43 / 1.91 |
| 1174.0 | 0.0 | 1171.5–1176.0 | 1185.7 | 1148.9 | ring-ip | yes | 1.43 / 1.91 |
| 1209.8 | 0.0 | 1209.3–1210.3 | 1207.8 | 1170.4 | ring-ip | yes | 1.43 / 1.91 |
| 1209.8 | 0.0 | 1209.3–1210.3 | 1207.9 | 1170.4 | ring-ip | yes | 1.43 / 1.91 |
| 1324.3 | 0.0 | 1319.4–1329.0 | 1356.7 | 1314.6 | ring-ip | yes | 1.43 / 1.91 |
| 1388.5 | 0.0 | 1385.8–1390.5 | 1387.2 | 1344.2 | ring-ip | yes | 1.43 / 1.91 |
| 1541.1 | 6.22 | 1539.4–1542.8 | 1531.4 | 1484.0 | ring-ip | yes | 1.43 / 1.91 |
| 1541.1 | 6.22 | 1539.4–1542.8 | 1531.4 | 1484.0 | ring-ip | yes | 1.43 / 1.91 |
| 1691.7 | 0.0 | 1691.4–1692.2 | 1656.0 | 1604.7 | ring-ip | yes | 1.43 / 1.91 |
| 1691.8 | 0.0 | 1691.4–1692.3 | 1656.1 | 1604.7 | ring-ip | yes | 1.43 / 1.91 |
| 3216.1 | 0.0 | 3215.7–3216.4 | 3174.5 | 3047.5 | CH-stretch | yes | 0.95 / 2.19 |
| 3226.3 | 0.0 | 3225.8–3226.7 | 3184.1 | 3056.7 | CH-stretch | yes | 0.95 / 2.19 |
| 3226.4 | 0.0 | 3225.8–3226.7 | 3184.1 | 3056.7 | CH-stretch | yes | 0.95 / 2.19 |
| 3242.1 | 52.02 | 3241.5–3242.5 | 3199.9 | 3071.9 | CH-stretch | yes | 0.95 / 2.19 |
| 3242.1 | 52.01 | 3241.5–3242.5 | 3199.9 | 3071.9 | CH-stretch | yes | 0.95 / 2.19 |
| 3252.3 | 0.0 | 3251.8–3252.7 | 3210.5 | 3082.1 | CH-stretch | yes | 0.95 / 2.19 |

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
