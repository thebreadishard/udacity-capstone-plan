# Certificate — benzene (A_8448043181), rung 5 · validated — 2026-11-20 09:17

benzene: rung 5 (validated). The cheap-level spectrum is served with the laboratory tolerance per family; no predicted correction is shown in this record — the pipeline serves it for the licensed families (ring-ip, CH-stretch, CH-oop, other; decision 65), a band only where its own position moved by no more than the licence line in the presentations tried (this molecule turned, mirrored or listed in another atom order); the anchor coverage lists what coupled-cluster evidence exists and where it is wider than the tolerance. Licence caveat: CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it).

**Positions.** Positions are harmonic (ω): a catalogue record carries no anharmonic step; the pipeline (m08/pipeline.py) prints the anharmonic estimate ν = ω + Δ_anh for a molecule it computes, and claims no licence for it.

## Ladder

| rung | label | status |
|---|---|---|
| 0 | listed | reached |
| 1 | cheap_level_done | reached |
| 2 | correction_predicted | — not in this record: the pipeline (m08/pipeline.py) serves it for the licensed families (decision 65) |
| 3 | spectrum_predicted | — not in this record: the pipeline (m08/pipeline.py) serves it for the licensed families (decision 65); heights only where an APT exists |
| 4 | anchored | reached |
| 5 | validated | reached |

## Spectrum (cheap rung; harmonic, cm⁻¹)

- **b3lyp**: 30 vibrational modes, 0 imaginary; source website export molecules/A_8448043181.json ← corpus molecules/A_8448043181/ (deck 97ed2d67c66b)
- **wb97x**: 30 vibrational modes, 0 imaginary; source website export molecules/A_8448043181.json ← corpus molecules/A_8448043181/ (deck 97ed2d67c66b)

## Spectral shape (cheap rung; harmonic positions and heights)

7 infrared-active bands of 30 modes (the others have height zero and are not drawn); Lorentzian FWHM 10 cm⁻¹. APT modules/05_support_predictor/corpus/molecules/A_8448043181/dipole_b3lyp_cphf.npz; Hessian modules/05_support_predictor/corpus/molecules/A_8448043181/hessian_b3lyp.npz; largest difference to the listed positions 0.05 cm⁻¹.

| band (cm⁻¹) | height (km/mol) | family |
|---|---|---|
| 694.6 | 77.57 | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 1068.8 | 3.26 | ring / CH-ip (9-10.5 um) |
| 1069.1 | 3.25 | ring / CH-ip (9-10.5 um) |
| 1530.8 | 6.52 | CC-stretch (6.2 um) |
| 1531.1 | 6.54 | CC-stretch (6.2 um) |
| 3183.2 | 0.15 | CH-stretch |
| 3199.4 | 51.88 | CH-stretch |
| 3199.5 | 51.71 | CH-stretch |

**How well the shape is known** — the carried ΔH-network v1.4 against ωB97X/6-31G* (the DFT proxy: the network's ΔH is trained on ωB97X − B3LYP Hessians); the corrected spectrum is the pipeline's (`m08/pipeline.py`), not this record's:

| hold-out | molecules with an APT | spectrum overlap, uncorrected → corrected | height error, uncorrected → corrected |
|---|---|---|---|
| (a) | 8 | 0.277 → 0.977 | 0.227 → 0.109 |
| (b) | 31 | 0.366 → 0.975 | 0.511 → 0.216 |

*Overlap:* cosine similarity of the two Lorentzian-broadened spectra (FWHM 10 cm⁻¹, 500–3500 cm⁻¹); 1 = identical shape. *Height error:* intensity-weighted rms of the relative height error per band, bands paired by the shape of the motion (eigenvector overlap); 0 = identical heights. *Coupled cluster:* not measured for this network version: the coupled-cluster reads (T3) were made on an earlier network (chain 34). *Open:* the APT itself is computed at the cheap level; its CC-minus-B3LYP difference (≈ 20 % on benzene) is not corrected by any rung yet. *Sources:* E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed1.json; E7_rungC_v14s3clean_c00_control_eval_clean_seed2.json; E7_rungC_v14s3clean_c00_control_a8read_seed0.json; E7_rungC_v14s3clean_c00_control_a8read_seed1.json; E7_rungC_v14s3clean_c00_control_a8read_seed2.json; E7_rungC_v14s3clean_c00_control_product_error.json.

## Per-band error budget

| family | modes | ω range | laboratory tolerance u_band (cm⁻¹) | ensemble ± | source |
|---|---|---|---|---|---|
| CC-stretch (6.2 um) | 3 | 1530.8–1647.5 | 21.14 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx |
| CC-stretch/CH-ip (7.7 um) | 2 | 1355.6–1388.1 | 14.61 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx, C71432_quantir_res0.125_boxcar.jdx |
| CH-ip-bend (8.6 um) | 3 | 1185.5–1206.2 | 32.24 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx |
| CH-oop (10.5-15 um; benzene nu11 at 673 included) | 4 | 694.6–864.8 | 5.22 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx, C71432_quantir_res0.125_boxcar.jdx |
| CH-stretch | 5 | 3174.1–3199.6 | 8.34 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx, C71432_quantir_res0.125_boxcar.jdx |
| above 3200 | 1 | 3210.4–3210.4 | 15.59 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx |
| low / skeletal | 4 | 414.9–644.7 | 16.05 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx |
| overtone / combination region | 1 | 1652.8–1652.8 | 15.27 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx |
| ring / CH-ip (9-10.5 um) | 7 | 968.9–1069.1 | 12.7 | — | module 03 u_band_by_record_family.csv, benzene, record(s) C71432_0.jdx, C71432_1.jdx, C71432_quantir_res0.125_boxcar.jdx |

*Ensemble ±:* — : this record is the cheap level; the pipeline serves the correction with its measured error (licence, decision 65: licensed at the DFT proxy: ring-ip (1.17 / 1.22), CH-stretch (0.8 / 1.67), CH-oop (1.86 / 1.26), other (2.38 / 2.1); not licensed: none — error of the corrected band positions of the seed-mean correction on hold-outs (a) / (b) in cm⁻¹ against 3 (decision 65 as amended on 16 Nov 2026); CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it); the first-order diagonal error of each seed's correction, averaged over the seeds, which the licence read until then: ring-ip (1.55 / 1.64), CH-stretch (1.15 / 2.02), CH-oop (2.22 / 1.72), other (2.91 / 3.68); no coupled-cluster licence).

## The anchor in force

**CCSD(T)/cc-pVTZ** (full, basis tier TZ), registered 2026-10-06, `probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz` (sha16 `4f264c390ec9ffc5`).

Checks that passed: pair ≤ 1.9e-6; energy route gradient 4.8e-6, H_kk 4.7e-4; lambda kernel 7.3e-17.

Source: `modules/05_support_predictor/out/ANCHORS_STATUS.json`, the project's anchor registry.

## Anchor coverage (coupled-cluster evidence)

| family | modes read | RMS vs CCSD(T) | u_band | reading | evidence |
|---|---|---|---|---|---|
| CC-stretch (6.2 um) | 4 | 8.65 | 21.14 | composite vs CCSD(T): RMS 8.7 cm⁻¹ against the laboratory tolerance 21.1 — within | probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md |
| CH-ip-bend (8.6 um) | 3 | 3.93 | 32.24 | composite vs CCSD(T): RMS 3.9 cm⁻¹ against the laboratory tolerance 32.2 — within | probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md |
| CH-oop (10.5-15 um; benzene nu11 at 673 included) | 6 | 23.56 | 5.22 | composite vs CCSD(T): RMS 23.6 cm⁻¹ against the laboratory tolerance 5.2 — wider: not decidable at this rung, shown as such | probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md |
| CH-stretch | 3 | 52.34 | 8.34 | composite vs CCSD(T): RMS 52.3 cm⁻¹ against the laboratory tolerance 8.3 — wider: not decidable at this rung, shown as such | probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md |
| ring / CH-ip (9-10.5 um) | 3 | 12.44 | 12.7 | composite vs CCSD(T): RMS 12.4 cm⁻¹ against the laboratory tolerance 12.7 — within | probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md |

## Laboratory record (rung 5): 92 bands in 3 record(s) — module 03 notebook/bands_lab.csv

## Cost record

| step | machine | hours | € ex VAT | source |
|---|---|---|---|---|
| cheap rung (deck v1, both functionals) | Asus18 | 0.289 | 0.00 | corpus ledger machine column 'Asus18' |
| anchor in force: CCSD(T)/cc-pVTZ (full, registered 2026-10-06) | — | — | not priced | modules/05_support_predictor/out/ANCHORS_STATUS.json → probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz; the registry carries no hours for this run — shown as not priced, not as €0 |

## Provenance

- releases: layerA2_2026-09-23, layerA2_2026-09-23b, layerA2_2026-09-24, layerA_2026-09-22; deck 97ed2d67c66b; commit c53b15c4; export built 2026-11-20T08:08:50Z
- evidence: probes/results_m1/e8_benzene_ccpvtz_oop_2026-10-03/hessian_ccsd_t.npz (exists); probes/results_m1/e8_benzene_ccpvdz_tlambda/E8_locality_benzene.md (exists); probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md (exists); probes/results_vpt2/benzene_benchmark_2026-09-22.md (exists)
- licence: 4 families licensed, read on the error of the corrected band positions of the seed-mean correction (README.md, decision 65 as amended on 16 Nov 2026); CH-oop on hold-out (a) rests on 5 of the hold-out's 8 molecules (the others have no such band): the 95 % interval of a bootstrap over molecules is 0.93–3.2 cm⁻¹ and crosses the line (96 % of the resamples lie under it); other on hold-out (a) rests on 8 molecules: the 95 % interval of a bootstrap over molecules is 1.45–3.19 cm⁻¹ and crosses the line (93 % of the resamples lie under it)
- family rule: modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026)
