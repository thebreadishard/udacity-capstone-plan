# Certificate — benzene (A_8448043181), rung 5 · validated — 2026-09-28 20:15

benzene: rung 5 (validated). The cheap-level spectrum is served with the laboratory tolerance per family; no predicted correction is shown because no family is licensed; the anchor coverage lists what coupled-cluster evidence exists and where it is wider than the tolerance.

## Ladder

| rung | label | status |
|---|---|---|
| 0 | listed | reached |
| 1 | cheap_level_done | reached |
| 2 | correction_predicted | —: no family licensed |
| 3 | spectrum_predicted | —: no family licensed |
| 4 | anchored | reached |
| 5 | validated | reached |

## Spectrum (cheap rung; harmonic, cm⁻¹)

- **b3lyp**: 30 vibrational modes, 0 imaginary; source website export molecules/A_8448043181.json ← corpus molecules/A_8448043181/ (deck 97ed2d67c66b)
- **wb97x**: 30 vibrational modes, 0 imaginary; source website export molecules/A_8448043181.json ← corpus molecules/A_8448043181/ (deck 97ed2d67c66b)

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

*Ensemble ±:* — : no predicted correction is shown; no family licensed: the registered verdict falls at 1,200 admitted layer-B molecules.

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
| anchor: E8 CCSD(T)/cc-pVDZ Hessian (72 gradients, rented machine, 24 Sep 2026) | CCX53 | — | not priced | probes/results_m1/e8_benzene_ccpvdz/E8_locality_benzene.md; the run's hours are not in a cost record yet — shown as not priced, not as €0 |

## Provenance

- releases: layerA2_2026-09-23, layerA2_2026-09-23b, layerA2_2026-09-24, layerA_2026-09-22; deck 97ed2d67c66b; commit 05a95e2; export built 2026-09-28T18:15:10Z
- evidence: probes/results_m1/e8_benzene_ccpvdz/E8_locality_benzene.md (exists); probes/results_m1/R0_DIAGONAL_READING_2026-09-22.md (exists); probes/results_vpt2/benzene_benchmark_2026-09-22.md (exists)
- licence: 0 families licensed (GoalGathering/notes/PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md)
- family rule: modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026)
