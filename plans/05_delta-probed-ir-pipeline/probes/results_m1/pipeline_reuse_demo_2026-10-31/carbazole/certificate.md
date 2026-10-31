# Certificate — carbazole · pipeline 0.6 · 2026-10-31 13:56

carbazole: the harmonic infrared spectrum of ΔH-network v1.3 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error measured on molecules the network never saw; licensed for ring-ip, CH-stretch, CH-oop (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule: in the catalogue (A_8152ea74fd) but not among the molecules the network trained on.

## Molecule

- c1ccc2c(c1)[nH]c1ccccc12, C12H9N, 22 atoms (C, H, N); the network's training set spans 8–30 atoms: inside
- catalogue: listed as A_8152ea74fd (carbazole, rung 1); its export's B3LYP positions lie within 1.1 cm⁻¹ of this run's (website export catalog.json, molecules/A_8152ea74fd.json)
- the network: in the catalogue (A_8152ea74fd) but not among the molecules the network trained on
- the ωB97X truth is in the corpus (corpus/molecules/A_8152ea74fd/hessian_wb97x_analytic.npz, 60 bands): the network against it, spectrum overlap 0.998; positions paired by rank, rms 0.93 cm⁻¹ (both independent of the atom order)

## Spectrum, band by band (ΔH-network v1.3, 3 seeds)

| network ω (cm⁻¹) | height (km/mol) | seeds' range | B3LYP ω | baseline ω | family | licensed | measured error (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|
| 118.0 | 4.17 | 117.2–119.0 | 104.1 | 99.5 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 162.9 | 0.0 | 161.4–164.3 | 152.3 | 145.6 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 224.9 | 0.27 | 224.5–225.2 | 219.3 | 209.7 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 297.0 | 21.76 | 294.3–300.8 | 280.3 | 268.0 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 308.9 | 0.01 | 308.3–309.7 | 297.5 | 284.4 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 363.1 | 76.19 | 359.6–368.6 | 348.8 | 333.5 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 438.1 | 1.11 | 437.9–438.1 | 435.0 | 415.9 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 445.4 | 7.29 | 444.3–446.4 | 433.9 | 414.8 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 461.5 | 0.01 | 458.8–463.7 | 455.3 | 435.3 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 518.6 | 4.06 | 517.9–519.3 | 513.9 | 491.3 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 567.5 | 0.12 | 567.5–567.5 | 563.3 | 538.5 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 592.1 | 11.05 | 591.6–592.5 | 576.5 | 551.1 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 601.0 | 0.0 | 600.2–602.4 | 585.2 | 559.5 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 635.1 | 6.14 | 634.9–635.2 | 631.6 | 603.8 | other | no | 3.62 / 3.89 | low / skeletal | 16.12 |
| 675.0 | 0.58 | 674.9–675.1 | 669.3 | 639.9 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 755.9 | 61.34 | 755.3–756.5 | 741.5 | 708.9 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 766.5 | 0.01 | 765.9–767.0 | 759.4 | 726.0 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 769.0 | 0.02 | 768.0–770.6 | 754.7 | 721.5 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 783.1 | 44.92 | 782.4–784.3 | 763.2 | 729.6 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 804.6 | 0.01 | 803.0–805.7 | 791.0 | 756.2 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 873.3 | 2.32 | 872.9–873.5 | 865.7 | 827.6 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 878.7 | 0.45 | 877.5–880.4 | 856.6 | 818.9 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 884.4 | 0.0 | 883.7–885.0 | 862.3 | 824.4 | CH-oop | yes | 2.17 / 2.7 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 896.3 | 0.28 | 896.3–896.4 | 889.2 | 850.1 | other | no | 3.62 / 3.89 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9.61 |
| 957.6 | 1.41 | 956.9–958.2 | 924.7 | 884.0 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 958.9 | 0.01 | 958.1–960.2 | 925.0 | 884.3 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 997.6 | 0.0 | 997.1–998.3 | 964.9 | 922.4 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 998.7 | 0.01 | 997.4–999.7 | 966.8 | 924.3 | CH-oop | yes | 2.17 / 2.7 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1027.5 | 4.1 | 1027.4–1027.6 | 1019.6 | 974.7 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1056.5 | 0.25 | 1056.4–1056.7 | 1046.2 | 1000.2 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1060.0 | 4.29 | 1059.6–1060.5 | 1051.0 | 1004.8 | ring-ip | yes | 1.77 / 2.12 | ring / CH-ip (9-10.5 um) | 15.87 |
| 1144.3 | 3.51 | 1143.9–1144.8 | 1136.3 | 1081.8 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1156.7 | 6.74 | 1156.2–1157.2 | 1149.8 | 1094.6 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1178.7 | 5.73 | 1178.4–1179.1 | 1184.2 | 1127.4 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1188.5 | 2.11 | 1188.0–1189.0 | 1191.4 | 1134.2 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1246.1 | 5.52 | 1245.3–1246.6 | 1241.2 | 1181.6 | ring-ip | yes | 1.77 / 2.12 | CH-ip-bend (8.6 um) | 8.64 |
| 1256.1 | 3.02 | 1255.5–1256.6 | 1246.2 | 1186.4 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1277.4 | 75.15 | 1276.4–1278.1 | 1270.2 | 1209.2 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1331.1 | 0.06 | 1330.6–1331.3 | 1321.3 | 1257.9 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1349.2 | 5.48 | 1348.6–1349.9 | 1349.3 | 1284.5 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1354.9 | 39.44 | 1354.0–1356.4 | 1370.6 | 1304.8 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1369.3 | 10.07 | 1368.9–1369.6 | 1387.1 | 1320.5 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1448.1 | 25.28 | 1447.8–1448.3 | 1442.5 | 1373.3 | ring-ip | yes | 1.77 / 2.12 | CC-stretch/CH-ip (7.7 um) | 15.87 |
| 1510.4 | 31.66 | 1509.3–1511.4 | 1493.8 | 1422.1 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1522.6 | 30.3 | 1521.8–1523.6 | 1511.5 | 1438.9 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1553.8 | 0.29 | 1553.2–1554.8 | 1533.4 | 1459.8 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1565.2 | 46.06 | 1565.0–1565.5 | 1544.8 | 1470.6 | ring-ip | yes | 1.77 / 2.12 | CC-stretch (6.2 um) | 16.09 |
| 1663.6 | 0.19 | 1663.4–1663.8 | 1631.0 | 1552.7 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1668.6 | 1.94 | 1668.1–1669.0 | 1636.3 | 1557.8 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1703.2 | 42.54 | 1703.1–1703.4 | 1666.7 | 1586.7 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 1727.3 | 3.3 | 1726.3–1728.4 | 1681.5 | 1600.8 | ring-ip | yes | 1.77 / 2.12 | overtone / combination region | 15.98 |
| 3224.0 | 0.1 | 3223.8–3224.4 | 3180.9 | 3053.7 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3224.6 | 3.16 | 3224.4–3225.0 | 3181.5 | 3054.2 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3230.3 | 4.14 | 3230.1–3230.6 | 3186.9 | 3059.4 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3231.8 | 1.6 | 3231.5–3232.3 | 3188.6 | 3061.1 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3240.6 | 5.2 | 3240.5–3240.8 | 3197.4 | 3069.5 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3241.4 | 59.6 | 3241.2–3241.8 | 3198.1 | 3070.2 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3252.0 | 58.75 | 3251.6–3252.4 | 3209.2 | 3080.8 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3252.8 | 5.04 | 3252.4–3253.2 | 3210.0 | 3081.6 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |
| 3713.3 | 48.16 | 3712.3–3714.9 | 3664.8 | 3518.2 | CH-stretch | yes | 1.19 / 2.5 | above 3200 | 16.05 |

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

- Asus18 (laptop): 3.4 s = 0.001 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps reuse 0.6 s, correction_and_spectra 2.8 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_reuse_demo_2026-10-31\carbazole; run at commit 69166291 (uncommitted changes: yes); certificate at 69166291
- deck 9e27bf8e934893f3; low level {"pyscf": "2.14.0", "pyscf_git": null, "numpy": "2.5.3", "python": "3.12.14", "sha256": {"analytic_hessians.py": "501d97b474b3", "apt.py": "3a29ebeb0242"}}; host Asus18
- models: E7_rungC_chain35_analytic_model_n750_seed0.pt (carried, sha16 f930db4af9268a00); E7_rungC_chain35_analytic_model_n750_seed1.pt (carried, sha16 87734859e866d6f7); E7_rungC_chain35_analytic_model_n750_seed2.pt (carried, sha16 023b8c142ad5fa52)
