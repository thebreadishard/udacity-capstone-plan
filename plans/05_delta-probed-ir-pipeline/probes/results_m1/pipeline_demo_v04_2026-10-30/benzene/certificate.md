# Certificate — benzene · pipeline 0.4 · 2026-10-30 18:19

benzene: the harmonic infrared spectrum of ΔH-network v1.3 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error measured on molecules the network never saw; licensed for ring-ip, CH-stretch, CH-oop (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it.

## Molecule

- c1ccccc1, C6H6, 12 atoms (C, H); the network's training set spans 8–30 atoms: inside
- catalogue: listed as A_8448043181 (benzene, rung 5); its export's B3LYP positions lie within 22.8 cm⁻¹ of this run's (website export catalog.json, molecules/A_8448043181.json)
- the network: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it
- the ωB97X truth is in the corpus (corpus/molecules/A_8448043181/hessian_wb97x_analytic.npz, 30 bands): the network against it, spectrum overlap 0.985; positions paired by rank, rms 1.27 cm⁻¹ (both independent of the atom order)

## Spectrum, band by band (ΔH-network v1.3, 3 seeds)

| network ω (cm⁻¹) | height (km/mol) | seeds' range | B3LYP ω | baseline ω | family | licensed | measured error (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|
| 426.2 | 0.0 | 424.3–427.4 | 415.4 | 397.1 | other | no | 3.35 / 3.89 | low / skeletal | 16.05 |
| 426.2 | 0.0 | 424.3–427.5 | 415.4 | 397.1 | other | no | 3.35 / 3.89 | low / skeletal | 16.05 |
| 625.1 | 0.0 | 624.9–625.2 | 621.9 | 594.5 | other | no | 3.35 / 3.89 | low / skeletal | 16.05 |
| 625.1 | 0.0 | 624.9–625.2 | 621.9 | 594.5 | other | no | 3.35 / 3.89 | low / skeletal | 16.05 |
| 701.7 | 77.57 | 701.0–702.6 | 694.9 | 664.3 | CH-oop | yes | 1.99 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 733.7 | 0.0 | 733.2–734.3 | 717.9 | 686.3 | other | no | 3.35 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 882.5 | 0.0 | 881.4–883.4 | 864.9 | 826.8 | CH-oop | yes | 1.99 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 883.4 | 0.0 | 882.0–884.7 | 864.8 | 826.7 | CH-oop | yes | 1.99 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 998.4 | 0.0 | 997.1–1000.0 | 969.3 | 926.7 | CH-oop | yes | 1.99 / 2.7 | ring / CH-ip (9-10.5 um) | 12.7 |
| 998.6 | 0.0 | 997.5–1000.2 | 969.4 | 926.7 | CH-oop | yes | 1.99 / 2.7 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1023.3 | 0.0 | 1022.8–1024.0 | 1019.8 | 974.9 | ring-ip | yes | 1.66 / 2.12 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1032.4 | 0.0 | 1032.3–1032.6 | 1020.0 | 975.1 | ring-ip | yes | 1.66 / 2.12 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1036.4 | 0.0 | 1035.7–1036.9 | 1011.0 | 966.5 | CH-oop | yes | 1.99 / 2.7 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.7 | 3.53 | 1078.3–1079.2 | 1068.8 | 1021.8 | ring-ip | yes | 1.66 / 2.12 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.7 | 3.53 | 1078.3–1079.2 | 1068.8 | 1021.8 | ring-ip | yes | 1.66 / 2.12 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1173.7 | 0.0 | 1171.2–1175.7 | 1185.5 | 1128.6 | ring-ip | yes | 1.66 / 2.12 | CH-ip-bend (8.6 um) | 32.24 |
| 1209.7 | 0.0 | 1209.1–1210.1 | 1207.7 | 1149.7 | ring-ip | yes | 1.66 / 2.12 | CH-ip-bend (8.6 um) | 32.24 |
| 1209.7 | 0.0 | 1209.2–1210.1 | 1207.7 | 1149.7 | ring-ip | yes | 1.66 / 2.12 | CH-ip-bend (8.6 um) | 32.24 |
| 1323.3 | 0.0 | 1318.4–1327.9 | 1355.6 | 1290.5 | ring-ip | yes | 1.66 / 2.12 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1388.5 | 0.0 | 1385.7–1390.5 | 1387.1 | 1320.5 | ring-ip | yes | 1.66 / 2.12 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1540.7 | 6.22 | 1539.0–1542.4 | 1531.0 | 1457.5 | ring-ip | yes | 1.66 / 2.12 | CC-stretch (6.2 um) | 21.14 |
| 1540.7 | 6.22 | 1539.0–1542.4 | 1531.1 | 1457.6 | ring-ip | yes | 1.66 / 2.12 | CC-stretch (6.2 um) | 21.14 |
| 1691.0 | 0.0 | 1690.6–1691.5 | 1655.3 | 1575.8 | ring-ip | yes | 1.66 / 2.12 | overtone / combination region | 15.27 |
| 1691.0 | 0.0 | 1690.7–1691.5 | 1655.3 | 1575.8 | ring-ip | yes | 1.66 / 2.12 | overtone / combination region | 15.27 |
| 3215.7 | 0.0 | 3215.3–3216.0 | 3174.0 | 3047.0 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |
| 3225.9 | 0.0 | 3225.4–3226.3 | 3183.6 | 3056.3 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |
| 3225.9 | 0.0 | 3225.4–3226.3 | 3183.7 | 3056.4 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |
| 3241.6 | 51.99 | 3241.0–3242.0 | 3199.4 | 3071.4 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |
| 3241.6 | 51.97 | 3241.0–3242.1 | 3199.4 | 3071.4 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |
| 3251.8 | 0.0 | 3251.3–3252.2 | 3210.1 | 3081.7 | CH-stretch | yes | 1.15 / 2.5 | above 3200 | 15.59 |

*Laboratory region and u_band:* modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026). *Positions:* harmonic positions: the anharmonic shift is not in this version (backlog; TASKS 53).

## How well the network is known (its own evaluation records)

Against ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians), seed means (each seed's value in brackets); targets: 3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py).

| read-out | (a), 10 molecules | (b), 39 molecules | target |
|---|---|---|---|
| ring-ip | 1.66 (1.82, 1.59, 1.59) | 2.12 (2.25, 2.02, 2.11) | 3.0 |
| CH-stretch | 1.15 (0.87, 1.62, 0.97) | 2.5 (1.91, 3.51, 2.08) | 3.0 |
| CH-oop | 1.99 (2.22, 1.9, 1.86) | 2.7 (2.44, 2.95, 2.72) | 3.0 |
| other | 3.35 (3.79, 3.02, 3.24) | 3.89 (3.65, 4.51, 3.52) | 3.0 |
| coupling_ratio | 0.172 (0.18, 0.164, 0.17) | 0.263 (0.282, 0.243, 0.265) | 0.25 |

| spectral shape | (a), 10 with an APT | (b), 31 with an APT |
|---|---|---|
| overlap, uncorrected → corrected | 0.27 → 0.982 | 0.366 → 0.967 |
| height error, uncorrected → corrected | 0.296 → 0.087 | 0.511 → 0.236 |

*Hold-outs:* hold-out (a): layer-A molecules held out on 19 Sep 2026 (benzene, phenanthrene, fluoranthene, benzonitrile, benzophenone, …), never trained; hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026.
*Sources:* E7_rungC_chain35_analytic_eval_frozenb_seed0.json; E7_rungC_chain35_analytic_eval_frozenb_seed1.json; E7_rungC_chain35_analytic_eval_frozenb_seed2.json.

*Licence:* licensed at the DFT proxy: ring-ip (1.66 / 2.12), CH-stretch (1.15 / 2.5), CH-oop (1.99 / 2.7); not licensed: other (3.35 / 3.89) — seed-mean error on hold-outs (a) / (b) in cm⁻¹ against 3; no coupled-cluster licence (README.md, decision 65).

## Cost

- Asus18 (laptop): 355.8 s = 0.099 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps optimise 17.6 s, low_level 337.3 s, correction_and_spectra 0.9 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_demo_v04_2026-10-30\benzene; run at commit 8be44b32 (uncommitted changes: no); certificate at c8015316
- deck 9e27bf8e934893f3; low level {"pyscf": "2.14.0", "pyscf_git": null, "numpy": "2.5.2", "python": "3.12.14", "sha256": {"analytic_hessians.py": "37404740a7f9", "apt.py": "35bb49dfb46f"}}; host Asus18
- models: E7_rungC_chain35_analytic_model_n750_seed0.pt (carried, sha16 f930db4af9268a00); E7_rungC_chain35_analytic_model_n750_seed1.pt (carried, sha16 87734859e866d6f7); E7_rungC_chain35_analytic_model_n750_seed2.pt (carried, sha16 023b8c142ad5fa52)
