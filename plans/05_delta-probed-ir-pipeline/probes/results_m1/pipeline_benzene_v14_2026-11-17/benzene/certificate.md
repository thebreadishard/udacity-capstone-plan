# Certificate — benzene · pipeline 0.12 · 2026-11-18 20:58

<!-- delivery 1 -->

benzene: the infrared spectrum of ΔH-network v1.4 (3 seeds) — B3LYP/6-31G* corrected toward ωB97X/6-31G*. The spectrum is made by the release networks of version 1.4, trained on the 1132 labelled entries of their training pool, hold-outs (a) and (b) included: each of the 3 networks is fitted on a random 85 % of the molecules and stopped on the other 15 %, a different 15 % per seed, so not every molecule is fitted by every network (with 3 networks about 0.15³ ≈ 0.3 % by none). Its error bars were measured on the measurement networks of the same version — the same recipe trained without the hold-out molecules — on molecules those networks never saw; the release networks themselves have seen the molecules of hold-outs (a) and (b), so they have no held-out error of their own. The error stated is the measurement networks' error of the corrected band positions of the seed-mean correction; the harmonic positions ω are licensed for ring-ip, CH-stretch, CH-oop, other (decision 65), each band marked; at the coupled-cluster level not measured for this network version: the coupled-cluster reads (T3) were made on an earlier network (chain 34). The scaled B3LYP spectrum is shown as the baseline only. This molecule and the ΔH network: in the release networks' training data: the error bars are not an out-of-sample error for this molecule; expect it to be smaller.

**Positions.** Positions are harmonic (ω): the anharmonic step was not applied — the step exists and was not run: it is off unless the run names a time budget, and `--anharmonic-minutes 120` switches it on.

## Molecule

- c1ccccc1, C6H6, 12 atoms (C, H); the network's training set spans 8–40 atoms: inside
- catalogue: listed as A_8448043181 (benzene, rung 5; website export catalog.json, molecules/A_8448043181.json); the export's B3LYP positions (psi4 1.11 (conda env qc, Windows), modules/05_support_predictor/corpus/molecules/A_8448043181/hessian_b3lyp.npz) lie within 22.8 cm⁻¹ of this run's; the corpus's analytic B3LYP Hessian (corpus/molecules/A_8448043181/hessian_b3lyp_analytic.npz), the route step 3 computes, within 0.0 cm⁻¹
- the ΔH network: in the release networks' training data: the error bars are not an out-of-sample error for this molecule; expect it to be smaller
- the ωB97X truth is in the corpus (corpus/molecules/A_8448043181/hessian_wb97x_analytic.npz, 30 bands): the network against it, spectrum overlap 0.963; positions paired by rank, rms 1.13 cm⁻¹ (both independent of the atom order)
- delivery 1 — only: harmonic, the anharmonic step is switched off: 2026-11-18 20:58:43, 2.2 s after the start

## Spectrum, band by band (ΔH-network v1.4, 3 seeds)

| best estimate (cm⁻¹) | printed | harmonic ω, network | Δ_anh | ± of Δ_anh, against its VPT2 label (measured, not licensed) | height (km/mol) | seeds' range of ω | B3LYP ω | baseline ω | family | ω licensed | error of the corrected band positions of the seed-mean correction of ω on (a) / (b), cm⁻¹ | laboratory region | u_band (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 425.9 | harmonic ω | 425.9 | — | — | 0.0 | 424.9–427.3 | 415.4 | 397.1 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 426.0 | harmonic ω | 426.0 | — | — | 0.0 | 425.2–427.4 | 415.4 | 397.1 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 625.7 | harmonic ω | 625.7 | — | — | 0.0 | 625.6–625.8 | 621.9 | 594.5 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 625.8 | harmonic ω | 625.8 | — | — | 0.0 | 625.6–625.9 | 621.9 | 594.5 | other | yes | 2.38 / 2.1 | low / skeletal | 16.05 |
| 702.5 | harmonic ω | 702.5 | — | — | 77.57 | 700.5–703.8 | 694.9 | 664.3 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 735.4 | harmonic ω | 735.4 | — | — | 0.0 | 734.0–736.4 | 717.9 | 686.3 | other | yes | 2.38 / 2.1 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 884.7 | harmonic ω | 884.7 | — | — | 0.0 | 883.5–885.8 | 864.8 | 826.7 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 885.7 | harmonic ω | 885.7 | — | — | 0.0 | 884.8–887.2 | 864.9 | 826.8 | CH-oop | yes | 1.86 / 1.26 | CH-oop (10.5-15 um; benzene nu11 at 673 included) | 5.22 |
| 1000.1 | harmonic ω | 1000.1 | — | — | 0.0 | 999.1–1001.1 | 969.3 | 926.7 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1000.2 | harmonic ω | 1000.2 | — | — | 0.0 | 999.3–1001.9 | 969.4 | 926.7 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1024.8 | harmonic ω | 1024.8 | — | — | 0.0 | 1024.3–1025.6 | 1019.8 | 974.9 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1033.0 | harmonic ω | 1033.0 | — | — | 0.0 | 1032.2–1033.8 | 1020.0 | 975.1 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1037.0 | harmonic ω | 1037.0 | — | — | 0.0 | 1035.5–1038.3 | 1011.0 | 966.5 | CH-oop | yes | 1.86 / 1.26 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.8 | harmonic ω | 1078.8 | — | — | 3.51 | 1078.0–1079.4 | 1068.8 | 1021.8 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1078.9 | harmonic ω | 1078.9 | — | — | 3.51 | 1078.0–1079.5 | 1068.8 | 1021.8 | ring-ip | yes | 1.17 / 1.22 | ring / CH-ip (9-10.5 um) | 12.7 |
| 1175.8 | harmonic ω | 1175.8 | — | — | 0.0 | 1174.4–1176.7 | 1185.5 | 1128.6 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1210.8 | harmonic ω | 1210.8 | — | — | 0.0 | 1210.0–1211.4 | 1207.7 | 1149.7 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1210.8 | harmonic ω | 1210.8 | — | — | 0.0 | 1210.0–1211.4 | 1207.7 | 1149.7 | ring-ip | yes | 1.17 / 1.22 | CH-ip-bend (8.6 um) | 32.24 |
| 1323.9 | harmonic ω | 1323.9 | — | — | 0.0 | 1321.8–1326.1 | 1355.6 | 1290.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1390.3 | harmonic ω | 1390.3 | — | — | 0.0 | 1389.6–1391.3 | 1387.1 | 1320.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch/CH-ip (7.7 um) | 14.61 |
| 1541.5 | harmonic ω | 1541.5 | — | — | 6.24 | 1540.5–1542.5 | 1531.0 | 1457.5 | ring-ip | yes | 1.17 / 1.22 | CC-stretch (6.2 um) | 21.14 |
| 1541.5 | harmonic ω | 1541.5 | — | — | 6.24 | 1540.5–1542.5 | 1531.1 | 1457.6 | ring-ip | yes | 1.17 / 1.22 | CC-stretch (6.2 um) | 21.14 |
| 1689.0 | harmonic ω | 1689.0 | — | — | 0.0 | 1687.9–1689.8 | 1655.3 | 1575.8 | ring-ip | yes | 1.17 / 1.22 | overtone / combination region | 15.27 |
| 1689.0 | harmonic ω | 1689.0 | — | — | 0.0 | 1688.0–1689.8 | 1655.3 | 1575.8 | ring-ip | yes | 1.17 / 1.22 | overtone / combination region | 15.27 |
| 3215.1 | harmonic ω | 3215.1 | — | — | 0.0 | 3214.9–3215.4 | 3174.0 | 3047.0 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3225.2 | harmonic ω | 3225.2 | — | — | 0.0 | 3224.8–3225.5 | 3183.6 | 3056.3 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3225.2 | harmonic ω | 3225.2 | — | — | 0.0 | 3224.8–3225.5 | 3183.7 | 3056.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3240.8 | harmonic ω | 3240.8 | — | — | 51.99 | 3240.0–3241.4 | 3199.4 | 3071.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3240.8 | harmonic ω | 3240.8 | — | — | 51.97 | 3240.0–3241.4 | 3199.4 | 3071.4 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |
| 3251.2 | harmonic ω | 3251.2 | — | — | 0.0 | 3250.6–3251.6 | 3210.1 | 3081.7 | CH-stretch | yes | 0.8 / 1.67 | above 3200 | 15.59 |

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

*Read-outs:* rms over the family's B3LYP modes of the first-order diagonal error of a seed's ΔH against the higher level, per seed, and the seeds' mean (cm⁻¹); families by module 05's rule (m05/learning_curve_layerA.molecule_features).
*Hold-outs:* hold-out (a) on its eight molecules never trained on in any version (the set fixed on 30 Oct 2026): eight layer-A molecules held out on 19 Sep 2026; this version's training left out the twins of the hold-out molecules, so the other two, 2-naphthoic acid and benzonitrile, are clean too, and the eight are kept for comparability with v1.3; hold-out (b): every substituted molecule of two scaffold cores, frozen on 8 Oct 2026 — scaffolds the measurement networks never saw. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on an earlier network (chain 34).
*Sources:* E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed1.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed2.json; E7_rungC_v14s3clean_c00_control_a8read_seed0.json; E7_rungC_v14s3clean_c00_control_a8read_seed1.json; E7_rungC_v14s3clean_c00_control_a8read_seed2.json; E7_rungC_v14s3clean_c00_control_product_error.json.

*Licence:* licensed at the DFT proxy: ring-ip (1.17 / 1.22), CH-stretch (0.8 / 1.67), CH-oop (1.86 / 1.26), other (2.38 / 2.1); not licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 (decision 65 as amended on 16 Nov 2026); CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it); the first-order diagonal error of each seed's correction, averaged over the seeds, which the licence read until then: ring-ip (1.55 / 1.64), CH-stretch (1.15 / 2.02), CH-oop (2.22 / 1.72), other (2.91 / 3.68); no coupled-cluster licence (README.md, decision 65 as amended on 16 Nov 2026).

## Cost

- Asus18 (laptop): 1.6 s, € 0.00 ex VAT (corpus ledger machine column 'Asus18'); steps reuse 0.5 s, correction_and_spectra 1.1 s

## Provenance

- result C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\probes\results_m1\pipeline_benzene_v14_2026-11-17\benzene; run at commit 6ee43785 (uncommitted changes: yes); certificate at 6ee43785
- steps 2–3 taken from the corpus folder C:\Users\thebr\Documents\CapstonePlan\plans\05_delta-probed-ir-pipeline\modules\05_support_predictor\corpus\molecules\A_8448043181
- deck 9e27bf8e934893f3; low level null; host Asus18
- models: E7_rungC_v14s3clean_c00_control_release_model_n1132_seed0.pt (carried, sha16 6f52c9d8570fbcf5); E7_rungC_v14s3clean_c00_control_release_model_n1132_seed1.pt (carried, sha16 1e820b8755078b90); E7_rungC_v14s3clean_c00_control_release_model_n1132_seed2.pt (carried, sha16 bc4de0b6458e44f2)
- the models above are release networks, trained on the 1132 labelled entries of their training pool: each of the 3 networks is fitted on a random 85 % of the molecules and stopped on the other 15 %, a different 15 % per seed, so not every molecule is fitted by every network (with 3 networks about 0.15³ ≈ 0.3 % by none); the error bars are those of the measurement networks: E7_rungC_v14s3clean_c00_control_model_n1082_seed0.pt (sha16 89574ed1b69c4e10); E7_rungC_v14s3clean_c00_control_model_n1082_seed1.pt (sha16 03dbbf9f29b59186); E7_rungC_v14s3clean_c00_control_model_n1082_seed2.pt (sha16 8dd85f3f1ba5bbeb)
