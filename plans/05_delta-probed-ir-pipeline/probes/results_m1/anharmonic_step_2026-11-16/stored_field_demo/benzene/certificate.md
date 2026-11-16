# Certificate — benzene · pipeline 0.11 (step 6 added to a 0.9 result from a stored force field) · 2026-11-16 20:32

benzene: the infrared spectrum of ΔH-network v1.3 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error of the corrected band positions of the seed-mean correction measured on molecules the network never saw; the harmonic positions ω are licensed for ring-ip, CH-stretch, CH-oop, other (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule and the ΔH network: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it. Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it).

**Positions.** Each band is printed at its best estimate — the anharmonic position ν = ω + Δ_anh for 28 of 30 bands (Δ_anh from the model x2* on the molecule's GFN2-xTB force field; for 1 of them the step's error is not measured for that kind of mode, and no bar is printed), the harmonic position ω for the other 2, each with its reason; ω stands beside every ν; the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the anharmonic position ν; no licence is claimed for ν.

**What the bar is, and what ν's error is.** The bar beside a step is the step's error alone — the rms of Δ_anh against its B3LYP VPT2 label — and not the error of ν: ν carries ω's error too, the harmonic position's error against the DFT proxy (ωB97X), which is what the licence is about; neither of the two is an error against experiment.

**What the bars rest on.** The bars rest on 2 target molecules, coronene and tetracene, both hydrocarbons — target modes: CH-oop 22, other 23, ring-ip 56, CH-stretch 20; the step's rms per molecule, coronene / tetracene, in cm⁻¹: CH-oop 11.91 / 4.55; other 5.69 / 1.09; ring-ip 4.25 / 2.35; CH-stretch 6.94 / 5.68; coronene carries the larger error in every family. They are the best numbers there are and they are thin: nothing here says the step helps a molecule unlike the targets, and a bar is a family's rms, not a prediction interval for one band.

## Molecule

- c1ccccc1, C6H6, 12 atoms (C, H); the network's training set spans 8–30 atoms: inside
- catalogue: listed as A_8448043181 (benzene, rung 5); its export's B3LYP positions lie within 22.8 cm⁻¹ of this run's (website export catalog.json, molecules/A_8448043181.json)
- the ΔH network: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it
- the anharmonic model x2* has this molecule in its training table (A_8448043181, one of 37): for this molecule the step's bar is not an out-of-sample error
- the ωB97X truth is in the corpus (corpus/molecules/A_8448043181/hessian_wb97x_analytic.npz, 30 bands): the network against it, spectrum overlap 0.985; positions paired by rank, rms 1.27 cm⁻¹ (both independent of the atom order)

## Spectrum, band by band (ΔH-network v1.3, 3 seeds)

| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | ± of Δ_anh, against its VPT2 label (measured, not licensed) | height (km/mol) | seeds' range of ω | B3LYP ω | baseline ω | family | ω licensed | error of the corrected band positions of the seed-mean correction of ω on (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 426.2 | harmonic ω | 426.2 | — | — | 0.0 | 424.3–427.4 | 415.4 | 397.1 | other | yes | 2.78 / 2.77 | low / skeletal | 16.05 |
| 426.2 | harmonic ω | 426.2 | — | — | 0.0 | 424.3–427.5 | 415.4 | 397.1 | other | yes | 2.78 / 2.77 | low / skeletal | 16.05 |
| 618.8 | anharmonic ν | 625.1 | -6.3 | 3.84 | 0.0 | 624.9–625.2 | 621.9 | 594.5 | other | yes | 2.78 / 2.77 | low / skeletal | 16.05 |
| 618.8 | anharmonic ν | 625.1 | -6.3 | 3.84 | 0.0 | 624.9–625.2 | 621.9 | 594.5 | other | yes | 2.78 / 2.77 | low / skeletal | 16.05 |
| 692.4 | anharmonic ν | 701.7 | -9.3 | 8.38 | 77.57 | 701.0–702.6 | 694.9 | 664.3 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 722.4 | anharmonic ν | 733.7 | -11.3 | not measured | 0.0 | 733.2–734.3 | 717.9 | 686.3 | other | yes | 2.78 / 2.77 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 874.2 | anharmonic ν | 882.5 | -8.3 | 8.38 | 0.0 | 881.4–883.4 | 864.9 | 826.8 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 875.1 | anharmonic ν | 883.4 | -8.3 | 8.38 | 0.0 | 882.0–884.7 | 864.8 | 826.7 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 986.8 | anharmonic ν | 998.4 | -11.6 | 8.38 | 0.0 | 997.1–1000.0 | 969.3 | 926.7 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 12.7 |
| 987.0 | anharmonic ν | 998.6 | -11.6 | 8.38 | 0.0 | 997.5–1000.2 | 969.4 | 926.7 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1009.4 | anharmonic ν | 1023.3 | -13.9 | 3.37 | 0.0 | 1022.8–1024.0 | 1019.8 | 974.9 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1016.7 | anharmonic ν | 1032.4 | -15.7 | 3.37 | 0.0 | 1032.3–1032.6 | 1020.0 | 975.1 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1021.2 | anharmonic ν | 1036.4 | -15.2 | 8.38 | 0.0 | 1035.7–1036.9 | 1011.0 | 966.5 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1062.8 | anharmonic ν | 1078.7 | -15.9 | 3.37 | 3.53 | 1078.3–1079.2 | 1068.8 | 1021.8 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1062.8 | anharmonic ν | 1078.7 | -15.9 | 3.37 | 3.53 | 1078.3–1079.2 | 1068.8 | 1021.8 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1161.7 | anharmonic ν | 1173.7 | -12.0 | 3.37 | 0.0 | 1171.2–1175.7 | 1185.5 | 1128.6 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 32.24 |
| 1195.5 | anharmonic ν | 1209.7 | -14.2 | 3.37 | 0.0 | 1209.1–1210.1 | 1207.7 | 1149.7 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 32.24 |
| 1195.5 | anharmonic ν | 1209.7 | -14.2 | 3.37 | 0.0 | 1209.2–1210.1 | 1207.7 | 1149.7 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 32.24 |
| 1297.8 | anharmonic ν | 1323.3 | -25.5 | 3.37 | 0.0 | 1318.4–1327.9 | 1355.6 | 1290.5 | ring-ip | yes | 1.43 / 1.91 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1364.9 | anharmonic ν | 1388.5 | -23.6 | 3.37 | 0.0 | 1385.7–1390.5 | 1387.1 | 1320.5 | ring-ip | yes | 1.43 / 1.91 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1511.0 | anharmonic ν | 1540.7 | -29.7 | 3.37 | 6.22 | 1539.0–1542.4 | 1531.0 | 1457.5 | ring-ip | yes | 1.43 / 1.91 | CC-stretch (6.2 um) | 21.14 |
| 1511.0 | anharmonic ν | 1540.7 | -29.7 | 3.37 | 6.22 | 1539.0–1542.4 | 1531.1 | 1457.6 | ring-ip | yes | 1.43 / 1.91 | CC-stretch (6.2 um) | 21.14 |
| 1652.4 | anharmonic ν | 1691.0 | -38.6 | 3.37 | 0.0 | 1690.6–1691.5 | 1655.3 | 1575.8 | ring-ip | yes | 1.43 / 1.91 | overtone / combination region | 15.27 |
| 1652.4 | anharmonic ν | 1691.0 | -38.6 | 3.37 | 0.0 | 1690.7–1691.5 | 1655.3 | 1575.8 | ring-ip | yes | 1.43 / 1.91 | overtone / combination region | 15.27 |
| 3069.5 | anharmonic ν | 3215.7 | -146.2 | 6.21 | 0.0 | 3215.3–3216.0 | 3174.0 | 3047.0 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |
| 3089.0 | anharmonic ν | 3225.9 | -136.9 | 6.21 | 0.0 | 3225.4–3226.3 | 3183.6 | 3056.3 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |
| 3089.0 | anharmonic ν | 3225.9 | -136.9 | 6.21 | 0.0 | 3225.4–3226.3 | 3183.7 | 3056.4 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |
| 3109.0 | anharmonic ν | 3241.6 | -132.6 | 6.21 | 51.99 | 3241.0–3242.0 | 3199.4 | 3071.4 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |
| 3109.0 | anharmonic ν | 3241.6 | -132.6 | 6.21 | 51.97 | 3241.0–3242.1 | 3199.4 | 3071.4 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |
| 3115.1 | anharmonic ν | 3251.8 | -136.7 | 6.21 | 0.0 | 3251.3–3252.2 | 3210.1 | 3081.7 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 8.34 |

*Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it).*

Which position each band is printed at (the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the anharmonic position ν):

- harmonic position, no anharmonic step: no model was measured for this family in this range — 2 band(s): 426.2, 426.2 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.84 cm⁻¹ (rms of Δ_anh against its VPT2 label, family other); no licence is claimed for ν — 2 band(s): 618.8, 618.8 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 8.38 cm⁻¹ (rms of Δ_anh against its VPT2 label, family CH-oop); no licence is claimed for ν — 6 band(s): 692.4, 874.2, 875.1, 986.8, 987.0, 1021.2 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh, printed without an error bar: the step's error is not measured for this kind of mode (family 'other' with an out-of-plane share of 0.8 or more); no licence is claimed for ν — 1 band(s): 722.4 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.37 cm⁻¹ (rms of Δ_anh against its VPT2 label, family ring-ip); no licence is claimed for ν — 13 band(s): 1009.4, 1016.7, 1062.8, 1062.8, 1161.7, 1195.5, 1195.5, 1297.8, 1364.9, 1511.0, 1511.0, 1652.4, 1652.4 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 6.21 cm⁻¹ (rms of Δ_anh against its VPT2 label, family CH-stretch); no licence is claimed for ν — 6 band(s): 3069.5, 3089.0, 3089.0, 3109.0, 3109.0, 3115.1 cm⁻¹

*Laboratory region and u_band:* modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026), read at the printed position.

## How well the network is known (its product-error record and its evaluation records)

Against ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians); two quantities, each under its name.

The licence reads the error of the corrected band positions of the seed-mean correction (rms over the family's bands of the corrected band position's error against the higher level (cm⁻¹): the seeds' mean ΔH added to the B3LYP Hessian and diagonalised, each corrected band paired to its higher-level band by mode overlap and counted in the family of its B3LYP partner — what the pipeline prints; with the 95 % interval of a bootstrap over whole molecules).

| family | (a), 8 molecules | (b), 39 molecules | line |
|---|---|---|---|
| ring-ip | 1.43 (95 % interval over molecules 1.13–1.7; 199 bands) | 1.91 (95 % interval over molecules 1.84–2.0; 1164 bands) | 3 |
| CH-stretch | 0.95 (95 % interval over molecules 0.39–1.48; 73 bands) | 2.19 (95 % interval over molecules 1.8–2.53; 401 bands) | 3 |
| CH-oop | 1.64 (95 % interval over molecules 1.19–1.97; 46 bands) | 1.88 (95 % interval over molecules 1.56–2.16; 84 bands) | 3 |
| other | 2.78 (95 % interval over molecules 1.68–3.76; 156 bands) | 2.77 (95 % interval over molecules 2.56–2.97; 1225 bands) | 3 |

Beside it the evaluation records' read-outs — the first-order diagonal error of each seed's correction, averaged over the seeds (each seed's value in brackets), which the licence read until 16 Nov 2026 — and the coupling ratio; targets: 3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py).

| read-out | (a), 8 molecules | (b), 39 molecules | target |
|---|---|---|---|
| ring-ip | 1.77 (1.95, 1.68, 1.7) | 2.12 (2.25, 2.02, 2.11) | 3.0 |
| CH-stretch | 1.19 (0.91, 1.74, 0.91) | 2.5 (1.91, 3.51, 2.08) | 3.0 |
| CH-oop | 2.17 (2.47, 2.06, 1.99) | 2.7 (2.44, 2.95, 2.72) | 3.0 |
| other | 3.62 (4.09, 3.27, 3.51) | 3.89 (3.65, 4.51, 3.52) | 3.0 |
| coupling_ratio | 0.184 (0.193, 0.176, 0.183) | 0.263 (0.282, 0.243, 0.265) | 0.25 |

| spectral shape | (a), 8 with an APT | (b), 31 with an APT |
|---|---|---|
| overlap, uncorrected → corrected | 0.277 → 0.979 | 0.366 → 0.967 |
| height error, uncorrected → corrected | 0.227 → 0.097 | 0.511 → 0.236 |

*Read-outs:* the read-outs: rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the higher level, per seed, and the seeds' mean (cm⁻¹); families by module 05's rule (m05/learning_curve_layerA.molecule_features).
*Hold-outs:* hold-out (a) without its two trained twins (2-naphthoic acid and benzonitrile were trained on as layer-B molecules; TASKS 157): eight layer-A molecules held out on 19 Sep 2026, never trained on under any id; hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026.
*Sources:* E7_rungC_chain35_analytic_eval_frozenb_seed0.json; E7_rungC_chain35_analytic_eval_frozenb_seed1.json; E7_rungC_chain35_analytic_eval_frozenb_seed2.json; E7_rungC_chain35_analytic_a8read_seed0.json; E7_rungC_chain35_analytic_a8read_seed1.json; E7_rungC_chain35_analytic_a8read_seed2.json; E7_rungC_chain35_analytic_product_error.json.

*Licence:* licensed at the DFT proxy: ring-ip (1.43 / 1.91), CH-stretch (0.95 / 2.19), CH-oop (1.64 / 1.88), other (2.78 / 2.77); not licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 (decision 65 as amended on 16 Nov 2026); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it); the first-order diagonal error of each seed's correction, averaged over the seeds, which the licence read until then: ring-ip (1.77 / 2.12), CH-stretch (1.19 / 2.5), CH-oop (2.17 / 2.7), other (3.62 / 3.89); no coupled-cluster licence (README.md, decision 65 as amended on 16 Nov 2026).

## Cost

- Asus18 (laptop): 324.0 s = 0.09 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps optimise 15.1 s, low_level 308.2 s, correction_and_spectra 0.7 s, anharmonic 0.0 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan-wt-anharmonic\plans\05_delta-probed-ir-pipeline\probes\results_m1\anharmonic_step_2026-11-16\stored_field_demo\benzene; run at commit 292b3f9a (uncommitted changes: yes); certificate at 49c51624
- deck 9e27bf8e934893f3; low level {"pyscf": "2.14.0", "pyscf_git": null, "numpy": "2.5.2", "python": "3.12.14", "sha256": {"analytic_hessians.py": "0ea113dae1df", "apt.py": "b22c29d0575f"}}; host Asus18
- models: E7_rungC_chain35_analytic_model_n750_seed0.pt (carried, sha16 f930db4af9268a00); E7_rungC_chain35_analytic_model_n750_seed1.pt (carried, sha16 87734859e866d6f7); E7_rungC_chain35_analytic_model_n750_seed2.pt (carried, sha16 023b8c142ad5fa52)
