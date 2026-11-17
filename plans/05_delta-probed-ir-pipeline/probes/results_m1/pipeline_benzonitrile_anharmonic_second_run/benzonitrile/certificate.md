# Certificate — benzonitrile · pipeline 0.11 · 2026-11-17 09:00

<!-- delivery 2 -->

benzonitrile: the infrared spectrum of ΔH-network v1.3 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error of the corrected band positions of the seed-mean correction measured on molecules the network never saw; the harmonic positions ω are licensed for ring-ip, CH-stretch, CH-oop, other (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule and the ΔH network: in the network's training set (B_3100da3761) and also in hold-out (a) as A_3100da3761: that hold-out was not clean for it, and the hold-out error is not this molecule's measure. Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it).

**Positions.** Each band is printed at its best estimate — the anharmonic position ν = ω + Δ_anh for 27 of 33 bands (Δ_anh from the model x2* on the molecule's GFN2-xTB force field; for 1 of them the step's error is not measured for that kind of mode, and no bar is printed), the harmonic position ω for the other 6, each with its reason; ω stands beside every ν; the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the anharmonic position ν; no licence is claimed for ν.

**What the bar is, and what ν's error is.** The bar beside a step is the step's error alone — the rms of Δ_anh against its B3LYP VPT2 label — and not the error of ν: ν carries ω's error too, the harmonic position's error against the DFT proxy (ωB97X), which is what the licence is about; neither of the two is an error against experiment.

**What the bars rest on.** The bars rest on 2 target molecules, coronene and tetracene, both hydrocarbons — target modes: CH-oop 22, other 23, ring-ip 56, CH-stretch 20; the step's rms per molecule, coronene / tetracene, in cm⁻¹: CH-oop 11.91 / 4.55; other 5.69 / 1.09; ring-ip 4.25 / 2.35; CH-stretch 6.94 / 5.68; coronene carries the larger error in every family. They are the best numbers there are and they are thin: nothing here says the step helps a molecule unlike the targets, and a bar is a family's rms, not a prediction interval for one band.

## Molecule

- N#Cc1ccccc1, C7H5N, 13 atoms (C, H, N); the network's training set spans 8–30 atoms: inside
- catalogue: listed as A_3100da3761 (benzonitrile, rung 4); its export's B3LYP positions lie within 1.9 cm⁻¹ of this run's (website export catalog.json, molecules/A_3100da3761.json)
- the ΔH network: in the network's training set (B_3100da3761) and also in hold-out (a) as A_3100da3761: that hold-out was not clean for it, and the hold-out error is not this molecule's measure
- the anharmonic model x2* has not seen this molecule: it is neither in its training table (37 molecules) nor a target
- the ωB97X truth is in the corpus (corpus/molecules/A_3100da3761/hessian_wb97x_analytic.npz, 33 bands): the network against it, spectrum overlap 0.987; positions paired by rank, rms 1.19 cm⁻¹ (both independent of the atom order)
- delivery 1 — first: harmonic, the anharmonic step is running: 2026-11-17 08:49:40, 6.7 s after the start; final by 2026-11-17 10:52, and if no later delivery stands here by then, this one is final
- delivery 2 — second: with the anharmonic positions: 2026-11-17 09:00:38, 664.5 s after the start

## Spectrum, band by band (ΔH-network v1.3, 3 seeds)

| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | ± of Δ_anh, against its VPT2 label (measured, not licensed) | height (km/mol) | seeds' range of ω | B3LYP ω | baseline ω | family | ω licensed | error of the corrected band positions of the seed-mean correction of ω on (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 167.8 | harmonic ω | 167.8 | — | — | 1.84 | 167.3–168.2 | 147.1 | 140.6 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 188.3 | harmonic ω | 188.3 | — | — | 4.43 | 187.7–188.8 | 164.6 | 157.4 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 411.0 | harmonic ω | 411.0 | — | — | 0.93 | 410.5–411.3 | 392.1 | 374.8 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 422.3 | harmonic ω | 422.3 | — | — | 0.0 | 421.0–423.2 | 411.0 | 392.9 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 468.8 | harmonic ω | 468.8 | — | — | 0.0 | 468.5–469.1 | 465.4 | 444.9 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 571.8 | anharmonic ν | 576.8 | -5.0 | 3.84 | 0.24 | 576.2–577.1 | 558.8 | 534.2 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 572.2 | anharmonic ν | 580.5 | -8.3 | not measured | 14.65 | 579.2–581.5 | 569.9 | 544.8 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 636.9 | anharmonic ν | 643.3 | -6.4 | 3.84 | 0.15 | 643.2–643.4 | 638.3 | 610.2 | other | yes | 2.78 / 2.77 | low / skeletal | 16.12 |
| 705.5 | anharmonic ν | 716.2 | -10.7 | 8.38 | 25.75 | 715.5–716.9 | 704.1 | 673.1 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 773.0 | anharmonic ν | 781.6 | -8.6 | 3.84 | 2.2 | 781.4–781.9 | 774.5 | 740.4 | other | yes | 2.78 / 2.77 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 778.8 | anharmonic ν | 791.3 | -12.5 | 8.38 | 31.59 | 790.7–791.6 | 777.5 | 743.3 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 871.6 | anharmonic ν | 880.4 | -8.8 | 8.38 | 0.0 | 880.0–880.6 | 861.4 | 823.5 | CH-oop | yes | 1.64 / 1.88 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 955.6 | anharmonic ν | 965.9 | -10.3 | 8.38 | 2.36 | 964.8–967.8 | 941.7 | 900.3 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 15.87 |
| 995.8 | anharmonic ν | 1007.7 | -11.9 | 8.38 | 0.0 | 1006.8–1009.5 | 976.3 | 933.3 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1010.8 | anharmonic ν | 1025.7 | -14.9 | 3.37 | 0.54 | 1025.4–1025.8 | 1017.9 | 973.1 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1022.1 | anharmonic ν | 1035.8 | -13.7 | 8.38 | 0.03 | 1034.6–1036.9 | 1007.8 | 963.5 | CH-oop | yes | 1.64 / 1.88 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1047.4 | anharmonic ν | 1064.5 | -17.1 | 3.37 | 2.53 | 1064.4–1064.6 | 1055.8 | 1009.3 | ring-ip | yes | 1.43 / 1.91 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1104.2 | anharmonic ν | 1120.2 | -16.0 | 3.37 | 2.91 | 1119.6–1120.9 | 1112.9 | 1059.5 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 8.64 |
| 1177.1 | anharmonic ν | 1189.8 | -12.7 | 3.37 | 0.36 | 1189.2–1190.4 | 1197.4 | 1139.9 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 8.64 |
| 1197.7 | anharmonic ν | 1213.8 | -16.1 | 3.37 | 0.9 | 1213.5–1214.2 | 1211.5 | 1153.3 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 8.64 |
| 1226.0 | anharmonic ν | 1246.3 | -20.3 | 3.37 | 0.53 | 1246.1–1246.5 | 1226.9 | 1168.0 | ring-ip | yes | 1.43 / 1.91 | CH-ip-bend (8.6 um) | 8.64 |
| 1281.5 | anharmonic ν | 1307.2 | -25.7 | 3.37 | 1.7 | 1305.4–1308.3 | 1338.6 | 1274.3 | ring-ip | yes | 1.43 / 1.91 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1338.2 | anharmonic ν | 1363.3 | -25.1 | 3.37 | 0.46 | 1362.8–1363.9 | 1367.7 | 1302.1 | ring-ip | yes | 1.43 / 1.91 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1475.2 | anharmonic ν | 1503.9 | -28.7 | 3.37 | 6.35 | 1503.2–1504.4 | 1491.8 | 1420.2 | ring-ip | yes | 1.43 / 1.91 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1522.7 | anharmonic ν | 1553.7 | -31.0 | 3.37 | 8.18 | 1553.0–1554.9 | 1540.5 | 1466.6 | ring-ip | yes | 1.43 / 1.91 | CC-stretch (6.2 um) | 16.09 |
| 1628.1 | anharmonic ν | 1666.4 | -38.3 | 3.37 | 0.79 | 1666.2–1666.6 | 1633.3 | 1554.9 | ring-ip | yes | 1.43 / 1.91 | CC-stretch (6.2 um) | 16.09 |
| 1659.5 | anharmonic ν | 1697.9 | -38.4 | 3.37 | 0.88 | 1697.5–1698.3 | 1660.0 | 1580.3 | ring-ip | yes | 1.43 / 1.91 | overtone / combination region | 15.98 |
| 2387.8 | harmonic ω | 2387.8 | — | — | 26.74 | 2386.3–2389.6 | 2349.3 | 2236.5 | other | yes | 2.78 / 2.77 | overtone / combination region | 15.98 |
| 3087.8 | anharmonic ν | 3234.1 | -146.3 | 6.21 | 0.17 | 3233.3–3235.0 | 3191.5 | 3063.8 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 11.38 |
| 3110.9 | anharmonic ν | 3245.4 | -134.5 | 6.21 | 5.47 | 3244.9–3245.9 | 3202.8 | 3074.7 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 11.38 |
| 3117.6 | anharmonic ν | 3252.8 | -135.2 | 6.21 | 15.34 | 3252.1–3253.6 | 3210.1 | 3081.7 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 11.38 |
| 3141.1 | anharmonic ν | 3262.8 | -121.7 | 6.21 | 13.08 | 3262.6–3263.2 | 3220.0 | 3091.2 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 11.38 |
| 3126.9 | anharmonic ν | 3265.4 | -138.5 | 6.21 | 3.03 | 3265.0–3265.9 | 3222.9 | 3094.0 | CH-stretch | yes | 0.95 / 2.19 | CH-stretch | 11.38 |

*Licence caveat: other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.68–3.76 cm⁻¹ and crosses the line (70 % of the resamples lie under it).*

Which position each band is printed at (the licence (decision 65) is on the harmonic position ω against the DFT proxy (ωB97X); it says nothing about the anharmonic position ν):

- harmonic position, no anharmonic step: no model was measured for this family in this range — 6 band(s): 167.8, 188.3, 411.0, 422.3, 468.8, 2387.8 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.84 cm⁻¹ (rms of Δ_anh against its VPT2 label, family other); no licence is claimed for ν — 3 band(s): 571.8, 636.9, 773.0 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh, printed without an error bar: the step's error is not measured for this kind of mode (family 'other' with an out-of-plane share of 0.8 or more); no licence is claimed for ν — 1 band(s): 572.2 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 8.38 cm⁻¹ (rms of Δ_anh against its VPT2 label, family CH-oop); no licence is claimed for ν — 6 band(s): 705.5, 778.8, 871.6, 955.6, 995.8, 1022.1 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 3.37 cm⁻¹ (rms of Δ_anh against its VPT2 label, family ring-ip); no licence is claimed for ν — 12 band(s): 1010.8, 1047.4, 1104.2, 1177.1, 1197.7, 1226.0, 1281.5, 1338.2, 1475.2, 1522.7, 1628.1, 1659.5 cm⁻¹
- anharmonic estimate ν = ω + Δ_anh; the step's error is ± 6.21 cm⁻¹ (rms of Δ_anh against its VPT2 label, family CH-stretch); no licence is claimed for ν — 5 band(s): 3087.8, 3110.9, 3117.6, 3141.1, 3126.9 cm⁻¹

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

- Asus18 (laptop): 657.2 s = 0.183 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps reuse 0.3 s, correction_and_spectra 0.8 s, anharmonic 656.1 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_benzonitrile_anharmonic_second_run\benzonitrile; run at commit 42f0f40f (uncommitted changes: no); certificate at 42f0f40f
- deck 9e27bf8e934893f3; low level {"pyscf": "2.14.0", "pyscf_git": null, "numpy": "2.5.3", "python": "3.12.14", "sha256": {"analytic_hessians.py": "0ea113dae1df", "apt.py": "b22c29d0575f"}}; host Asus18
- models: E7_rungC_chain35_analytic_model_n750_seed0.pt (carried, sha16 f930db4af9268a00); E7_rungC_chain35_analytic_model_n750_seed1.pt (carried, sha16 87734859e866d6f7); E7_rungC_chain35_analytic_model_n750_seed2.pt (carried, sha16 023b8c142ad5fa52)
