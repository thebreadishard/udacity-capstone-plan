# Certificate — phenanthrene · pipeline 0.4 · 2026-10-30 20:39

phenanthrene: the harmonic infrared spectrum of ΔH-network v1.3 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error measured on molecules the network never saw; licensed for ring-ip, CH-stretch, CH-oop (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule: held out, hold-out (a) (A_541c53d1a5): never trained on; the measured error includes it.

## Molecule

- c1ccc2c(c1)ccc1ccccc12, C14H10, 24 atoms (C, H); the network's training set spans 8–30 atoms: inside
- catalogue: listed as A_541c53d1a5 (phenanthrene, rung 1); its export's B3LYP positions lie within 0.5 cm⁻¹ of this run's (website export catalog.json, molecules/A_541c53d1a5.json)
- the network: held out, hold-out (a) (A_541c53d1a5): never trained on; the measured error includes it
- the ωB97X truth is in the corpus (corpus/molecules/A_541c53d1a5/hessian_wb97x_analytic.npz, 66 bands): the network against it, spectrum overlap 0.996; positions paired by rank, rms 1.17 cm⁻¹ (both independent of the atom order)

## Spectrum, band by band (ΔH-network v1.3, 3 seeds)

| network ω (cm⁻¹) | height (km/mol) | seeds' range | B3LYP ω | baseline ω | family | licensed | measured error (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|
| 111.6 | 0.0 | 110.7–112.4 | 96.2 | 92.0 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 114.3 | 0.53 | 113.8–115.2 | 103.0 | 98.5 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 236.5 | 2.49 | 236.1–236.7 | 232.8 | 222.6 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 255.7 | 0.36 | 255.4–256.1 | 248.8 | 237.9 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 258.9 | 0.0 | 258.3–260.2 | 245.4 | 234.6 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 411.5 | 0.0 | 408.7–414.6 | 401.7 | 384.0 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 415.9 | 0.42 | 415.8–416.0 | 411.8 | 393.7 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 450.1 | 4.52 | 449.2–451.0 | 440.2 | 420.8 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 450.9 | 1.78 | 450.5–451.6 | 446.3 | 426.7 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 510.8 | 0.77 | 510.5–511.3 | 505.7 | 483.4 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 519.5 | 2.72 | 518.6–520.3 | 510.0 | 487.6 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 557.8 | 0.0 | 556.1–559.6 | 549.9 | 525.7 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 561.7 | 0.36 | 560.9–562.1 | 557.8 | 533.3 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 614.4 | 0.0 | 613.4–615.7 | 598.2 | 571.9 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 635.7 | 5.23 | 635.5–636.0 | 631.9 | 604.1 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 732.4 | 0.83 | 732.0–732.4 | 725.1 | 693.2 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 732.6 | 1.85 | 732.5–733.2 | 727.7 | 695.7 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 741.9 | 0.17 | 740.6–743.0 | 726.6 | 694.6 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 761.6 | 62.07 | 761.0–762.4 | 752.9 | 719.8 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 780.4 | 0.0 | 780.4–780.5 | 769.3 | 735.5 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 819.1 | 0.0 | 817.1–820.6 | 806.2 | 770.7 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 845.8 | 46.69 | 844.2–848.0 | 833.1 | 796.4 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 850.1 | 0.09 | 849.8–850.6 | 843.6 | 806.5 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 899.8 | 1.37 | 897.9–899.8 | 890.6 | 851.4 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 900.2 | 0.03 | 900.0–902.6 | 880.1 | 841.4 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 904.1 | 9.36 | 903.6–904.5 | 886.1 | 847.1 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 968.2 | 0.0 | 967.7–968.8 | 936.8 | 895.6 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 982.1 | 2.86 | 981.5–983.1 | 951.6 | 909.7 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1001.4 | 0.0 | 999.8–1002.3 | 970.2 | 927.5 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1015.5 | 0.04 | 1014.9–1016.2 | 985.6 | 942.2 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1016.4 | 0.0 | 1015.1–1017.3 | 986.4 | 943.0 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1025.9 | 0.96 | 1025.7–1026.0 | 1017.6 | 972.8 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1078.9 | 4.71 | 1078.6–1079.2 | 1070.0 | 1022.9 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1081.0 | 0.79 | 1080.8–1081.2 | 1072.7 | 1025.5 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1130.0 | 1.09 | 1129.9–1130.1 | 1121.4 | 1067.6 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1167.8 | 0.29 | 1167.1–1168.7 | 1187.0 | 1130.0 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1179.8 | 1.58 | 1179.7–1179.9 | 1174.4 | 1118.0 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1197.1 | 0.52 | 1197.0–1197.3 | 1199.2 | 1141.6 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1201.8 | 0.18 | 1201.6–1202.1 | 1197.6 | 1140.1 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1229.1 | 1.68 | 1228.9–1229.4 | 1237.9 | 1178.5 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1260.9 | 0.48 | 1260.6–1261.2 | 1252.9 | 1192.8 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1287.6 | 8.71 | 1287.4–1287.9 | 1280.5 | 1219.0 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1317.4 | 0.0 | 1316.7–1318.1 | 1311.4 | 1248.5 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1344.6 | 3.88 | 1344.3–1344.9 | 1335.7 | 1271.6 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1365.4 | 0.0 | 1364.0–1367.5 | 1387.1 | 1320.5 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1393.0 | 1.04 | 1392.1–1393.7 | 1390.8 | 1324.0 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1470.8 | 0.03 | 1470.1–1471.5 | 1461.2 | 1391.1 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1480.2 | 1.52 | 1479.3–1480.7 | 1468.1 | 1397.6 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1503.3 | 2.38 | 1502.8–1503.8 | 1486.3 | 1415.0 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1516.4 | 12.71 | 1515.8–1517.4 | 1507.2 | 1434.9 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1579.7 | 4.78 | 1579.1–1580.5 | 1553.3 | 1478.7 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1608.7 | 1.09 | 1608.5–1608.9 | 1581.3 | 1505.4 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1656.3 | 0.03 | 1655.7–1657.2 | 1623.6 | 1545.7 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1690.9 | 3.99 | 1690.6–1691.5 | 1661.6 | 1581.8 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1711.0 | 0.39 | 1710.5–1711.5 | 1673.2 | 1592.9 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1726.5 | 0.01 | 1724.9–1727.4 | 1678.2 | 1597.6 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 3218.4 | 0.01 | 3218.2–3218.7 | 3174.0 | 3047.0 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3220.6 | 5.96 | 3220.4–3220.8 | 3177.4 | 3050.3 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3221.7 | 3.9 | 3221.5–3221.8 | 3178.2 | 3051.1 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3230.9 | 0.0 | 3230.4–3231.2 | 3187.4 | 3059.9 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3232.4 | 18.42 | 3232.0–3232.7 | 3189.1 | 3061.5 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3238.2 | 40.16 | 3237.8–3238.7 | 3194.3 | 3066.5 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3245.7 | 51.76 | 3245.1–3246.1 | 3201.6 | 3073.5 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3249.0 | 0.52 | 3248.7–3249.2 | 3205.8 | 3077.6 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3255.3 | 22.43 | 3254.7–3255.7 | 3211.3 | 3082.8 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3268.5 | 28.83 | 3267.6–3269.1 | 3223.2 | 3094.3 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |

*Laboratory region and u_band:* modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026). *Positions:* harmonic positions: the anharmonic shift is not in this version (backlog; TASKS 53).

## How well the network is known (its own evaluation records)

Against ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians), seed means (each seed's value in brackets); targets: 3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py).

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

*Hold-outs:* hold-out (a) without its two trained twins (2-naphthoic acid and benzonitrile were trained on as layer-B molecules; TASKS 157): eight layer-A molecules held out on 19 Sep 2026, never trained on under any id; hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026.
*Sources:* E7_rungC_chain35_analytic_eval_frozenb_seed0.json; E7_rungC_chain35_analytic_eval_frozenb_seed1.json; E7_rungC_chain35_analytic_eval_frozenb_seed2.json; E7_rungC_chain35_analytic_a8read_seed0.json; E7_rungC_chain35_analytic_a8read_seed1.json; E7_rungC_chain35_analytic_a8read_seed2.json.

*Licence:* licensed at the DFT proxy: ring-ip (1.77 / 2.12), CH-stretch (1.19 / 2.5), CH-oop (2.17 / 2.7); not licensed: other (3.62 / 3.89) — seed-mean error on hold-outs (a) / (b) in cm⁻¹ against 3; no coupled-cluster licence (README.md, decision 65).

## Cost

- Asus18 (laptop): 4706.0 s = 1.307 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps optimise 80.1 s, low_level 4624.1 s, correction_and_spectra 1.8 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_demo_v04_2026-10-30\phenanthrene; run at commit 87145510 (uncommitted changes: no); certificate at ea24fc20
- deck 9e27bf8e934893f3; low level {"pyscf": "2.14.0", "pyscf_git": null, "numpy": "2.5.2", "python": "3.12.14", "sha256": {"analytic_hessians.py": "37404740a7f9", "apt.py": "35bb49dfb46f"}}; host Asus18
- models: E7_rungC_chain35_analytic_model_n750_seed0.pt (carried, sha16 f930db4af9268a00); E7_rungC_chain35_analytic_model_n750_seed1.pt (carried, sha16 87734859e866d6f7); E7_rungC_chain35_analytic_model_n750_seed2.pt (carried, sha16 023b8c142ad5fa52)
