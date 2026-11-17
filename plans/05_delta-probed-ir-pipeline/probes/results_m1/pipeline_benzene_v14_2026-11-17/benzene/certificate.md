# Certificate — benzene · pipeline 0.11 · 2026-11-17 23:37

<!-- delivery 1 -->

benzene: the infrared spectrum of ΔH-network v1.4 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G* — with the error of the corrected band positions of the seed-mean correction measured on molecules the network never saw; the harmonic positions ω are licensed for ring-ip, CH-stretch, CH-oop, other (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026. The scaled B3LYP spectrum is shown as the baseline only. This molecule and the ΔH network: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it. Licence caveat: CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it).

**Positions.** Positions are harmonic (ω): the anharmonic step was not applied — the step exists and was not run: it is off unless the run names a time budget, and `--anharmonic-minutes 120` switches it on (TASKS 211).

## Molecule

- c1ccccc1, C6H6, 12 atoms (C, H); the network's training set spans 8–40 atoms: inside
- catalogue: listed as A_8448043181 (benzene, rung 5); its export's B3LYP positions lie within 22.8 cm⁻¹ of this run's (website export catalog.json, molecules/A_8448043181.json)
- the ΔH network: held out, hold-out (a) (A_8448043181): never trained on; the measured error includes it
- the ωB97X truth is in the corpus (corpus/molecules/A_8448043181/hessian_wb97x_analytic.npz, 30 bands): the network against it, spectrum overlap 0.994; positions paired by rank, rms 2.02 cm⁻¹ (both independent of the atom order)
- delivery 1 — only: harmonic, the anharmonic step is switched off: 2026-11-17 23:37:13, 2.3 s after the start

## Spectrum, band by band (ΔH-network v1.4, 3 seeds)

| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | ± of Δ_anh, against its VPT2 label (measured, not licensed) | height (km/mol) | seeds' range of ω | B3LYP ω | baseline ω | family | ω licensed | error of the corrected band positions of the seed-mean correction of ω on (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 425.3 | harmonic ω | 425.3 | — | — | 0.0 | 424.2–426.0 | 415.4 | 397.1 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 425.4 | harmonic ω | 425.4 | — | — | 0.0 | 424.3–426.1 | 415.4 | 397.1 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 625.5 | harmonic ω | 625.5 | — | — | 0.0 | 625.1–626.0 | 621.9 | 594.5 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 625.5 | harmonic ω | 625.5 | — | — | 0.0 | 625.1–626.0 | 621.9 | 594.5 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 701.1 | harmonic ω | 701.1 | — | — | 77.57 | 699.0–702.2 | 694.9 | 664.3 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 733.5 | harmonic ω | 733.5 | — | — | 0.0 | 732.6–734.1 | 717.9 | 686.3 | other | yes | 2.38 / 2.1 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 888.3 | harmonic ω | 888.3 | — | — | 0.0 | 886.5–889.2 | 864.9 | 826.8 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 891.0 | harmonic ω | 891.0 | — | — | 0.0 | 889.6–892.0 | 864.8 | 826.7 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 997.6 | harmonic ω | 997.6 | — | — | 0.0 | 995.3–999.0 | 969.4 | 926.7 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 998.1 | harmonic ω | 998.1 | — | — | 0.0 | 996.1–999.6 | 969.3 | 926.7 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1024.6 | harmonic ω | 1024.6 | — | — | 0.0 | 1024.1–1024.8 | 1019.8 | 974.9 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1031.9 | harmonic ω | 1031.9 | — | — | 0.0 | 1030.4–1032.8 | 1020.0 | 975.1 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1038.9 | harmonic ω | 1038.9 | — | — | 0.0 | 1033.7–1043.5 | 1011.0 | 966.5 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.5 | harmonic ω | 1078.5 | — | — | 3.53 | 1078.3–1078.9 | 1068.8 | 1021.8 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.6 | harmonic ω | 1078.6 | — | — | 3.53 | 1078.3–1078.9 | 1068.8 | 1021.8 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1175.5 | harmonic ω | 1175.5 | — | — | 0.0 | 1174.0–1177.1 | 1185.5 | 1128.6 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1210.1 | harmonic ω | 1210.1 | — | — | 0.0 | 1208.7–1211.5 | 1207.7 | 1149.7 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1210.1 | harmonic ω | 1210.1 | — | — | 0.0 | 1208.8–1211.6 | 1207.7 | 1149.7 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1324.1 | harmonic ω | 1324.1 | — | — | 0.0 | 1321.9–1326.9 | 1355.6 | 1290.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1388.5 | harmonic ω | 1388.5 | — | — | 0.0 | 1387.2–1389.7 | 1387.1 | 1320.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1541.3 | harmonic ω | 1541.3 | — | — | 6.23 | 1540.1–1542.0 | 1531.0 | 1457.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch (6.2 um) | 21.14 |
| 1541.4 | harmonic ω | 1541.4 | — | — | 6.23 | 1540.1–1542.0 | 1531.1 | 1457.6 | ring-ip | yes | 1.17 / 1.22 | CC-stretch (6.2 um) | 21.14 |
| 1688.9 | harmonic ω | 1688.9 | — | — | 0.0 | 1687.2–1690.4 | 1655.3 | 1575.8 | ring-ip | yes | 1.17 / 1.22 | overtone / combination region | 15.27 |
| 1689.0 | harmonic ω | 1689.0 | — | — | 0.0 | 1687.2–1690.4 | 1655.3 | 1575.8 | ring-ip | yes | 1.17 / 1.22 | overtone / combination region | 15.27 |
| 3216.6 | harmonic ω | 3216.6 | — | — | 0.0 | 3216.2–3217.2 | 3174.0 | 3047.0 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3226.4 | harmonic ω | 3226.4 | — | — | 0.0 | 3226.0–3227.1 | 3183.6 | 3056.3 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3226.4 | harmonic ω | 3226.4 | — | — | 0.0 | 3226.0–3227.1 | 3183.7 | 3056.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3242.3 | harmonic ω | 3242.3 | — | — | 51.99 | 3241.8–3243.2 | 3199.4 | 3071.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3242.3 | harmonic ω | 3242.3 | — | — | 51.97 | 3241.8–3243.2 | 3199.4 | 3071.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3252.4 | harmonic ω | 3252.4 | — | — | 0.0 | 3251.3–3253.1 | 3210.1 | 3081.7 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |

*Licence caveat: CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it).*

*Laboratory region and u_band:* modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026), read at the printed position.

## How well the network is known (its product-error record and its evaluation records)

Against ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians); two quantities, each under its name.

The licence reads the error of the corrected band positions of the seed-mean correction (rms over the family's bands of the corrected band position's error against the higher level (cm⁻¹): the seeds' mean ΔH added to the B3LYP Hessian and diagonalised, each corrected band paired to its higher-level band by mode overlap and counted in the family of its B3LYP partner — what the pipeline prints; with the 95 % interval of a bootstrap over whole molecules).

| family | (a), 8 molecules | (b), 40 molecules | line |
|---|---|---|---|
| ring-ip | 1.17 (95 % interval over molecules 0.9–1.41; 199 bands) | 1.22 (95 % interval over molecules 1.09–1.34; 1194 bands) | 3 |
| CH-stretch | 0.8 (95 % interval over molecules 0.44–1.2; 73 bands) | 1.67 (95 % interval over molecules 1.37–1.95; 410 bands) | 3 |
| CH-oop | 1.86 (95 % interval over molecules 0.93–3.2; 46 bands) | 1.26 (95 % interval over molecules 0.98–1.59; 84 bands) | 3 |
| other | 2.38 (95 % interval over molecules 1.45–3.19; 156 bands) | 2.1 (95 % interval over molecules 1.88–2.34; 1258 bands) | 3 |

Beside it the evaluation records' read-outs — the first-order diagonal error of each seed's correction, averaged over the seeds (each seed's value in brackets), which the licence read until 16 Nov 2026 — and the coupling ratio; targets: 3 cm⁻¹ per family — decision 53's line for ring-ip, CH-oop and 'other', every family's under decision 65 (the licence) — and the coupling ratio ≤ 0.25 of chain 35's T1 line (probes/chain35_read.py).

| read-out | (a), 8 molecules | (b), 40 molecules | target |
|---|---|---|---|
| ring-ip | 1.55 (1.77, 1.52, 1.37) | 1.64 (1.53, 1.49, 1.89) | 3.0 |
| CH-stretch | 1.15 (1.34, 1.19, 0.92) | 2.02 (2.32, 2.2, 1.55) | 3.0 |
| CH-oop | 2.22 (2.22, 2.1, 2.35) | 1.72 (1.8, 1.96, 1.41) | 3.0 |
| other | 2.91 (2.79, 3.1, 2.84) | 3.68 (3.2, 4.15, 3.7) | 3.0 |
| coupling_ratio | 0.147 (0.15, 0.147, 0.143) | 0.17 (0.168, 0.164, 0.177) | 0.25 |

| spectral shape | (a), 8 with an APT | (b), 31 with an APT |
|---|---|---|
| overlap, uncorrected → corrected | 0.277 → 0.977 | 0.366 → 0.975 |
| height error, uncorrected → corrected | 0.227 → 0.109 | 0.511 → 0.216 |

*Read-outs:* the read-outs: rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the higher level, per seed, and the seeds' mean (cm⁻¹); families by module 05's rule (m05/learning_curve_layerA.molecule_features).
*Hold-outs:* hold-out (a) without its two trained twins (2-naphthoic acid and benzonitrile were trained on as layer-B molecules; TASKS 157): eight layer-A molecules held out on 19 Sep 2026, never trained on under any id; hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the network never saw. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on chain 34, and tests on the 9–11 existing anchors wait for the anchor decision of November 2026.
*Sources:* E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed1.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed2.json; E7_rungC_v14s3clean_c00_control_a8read_seed0.json; E7_rungC_v14s3clean_c00_control_a8read_seed1.json; E7_rungC_v14s3clean_c00_control_a8read_seed2.json; E7_rungC_v14s3clean_c00_control_product_error.json.

*Licence:* licensed at the DFT proxy: ring-ip (1.17 / 1.22), CH-stretch (0.8 / 1.67), CH-oop (1.86 / 1.26), other (2.38 / 2.1); not licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 (decision 65 as amended on 16 Nov 2026); CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it); the first-order diagonal error of each seed's correction, averaged over the seeds, which the licence read until then: ring-ip (1.55 / 1.64), CH-stretch (1.15 / 2.02), CH-oop (2.22 / 1.72), other (2.91 / 3.68); no coupled-cluster licence (README.md, decision 65 as amended on 16 Nov 2026).

## Cost

- Asus18 (laptop): 1.7 s = 0.0 h, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps reuse 0.6 s, correction_and_spectra 1.1 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_benzene_v14_2026-11-17\benzene; run at commit 6697fa40 (uncommitted changes: yes); certificate at 6697fa40
- deck 9e27bf8e934893f3; low level null; host Asus18
- models: E7_rungC_v14s3clean_c00_control_model_n1082_seed0.pt (carried, sha16 89574ed1b69c4e10); E7_rungC_v14s3clean_c00_control_model_n1082_seed1.pt (carried, sha16 03dbbf9f29b59186); E7_rungC_v14s3clean_c00_control_model_n1082_seed2.pt (carried, sha16 8dd85f3f1ba5bbeb)
