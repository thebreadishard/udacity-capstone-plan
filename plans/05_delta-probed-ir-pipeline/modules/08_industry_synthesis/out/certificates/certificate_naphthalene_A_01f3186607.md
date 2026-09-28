# Certificate — naphthalene (A_01f3186607), rung 4 · anchored — 2026-09-28 20:15

naphthalene: rung 4 (anchored). The cheap-level spectrum is served with the laboratory tolerance per family; no predicted correction is shown because no family is licensed; the anchor coverage lists what coupled-cluster evidence exists and where it is wider than the tolerance.

## Ladder

| rung | label | status |
|---|---|---|
| 0 | listed | reached |
| 1 | cheap_level_done | reached |
| 2 | correction_predicted | —: no family licensed |
| 3 | spectrum_predicted | —: no family licensed |
| 4 | anchored | reached |
| 5 | validated | — not reached |

## Spectrum (cheap rung; harmonic, cm⁻¹)

- **b3lyp**: 48 vibrational modes, 0 imaginary; source website export molecules/A_01f3186607.json ← corpus molecules/A_01f3186607/ (deck 97ed2d67c66b)
- **wb97x**: 48 vibrational modes, 0 imaginary; source website export molecules/A_01f3186607.json ← corpus molecules/A_01f3186607/ (deck 97ed2d67c66b)

## Per-band error budget

| family | modes | ω range | laboratory tolerance u_band (cm⁻¹) | ensemble ± | source |
|---|---|---|---|---|---|
| CC-stretch (6.2 um) | 4 | 1505.6–1630.4 | 15.88 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| CC-stretch/CH-ip (7.7 um) | 5 | 1277.7–1431.1 | 15.87 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| CH-ip-bend (8.6 um) | 5 | 1157.2–1243.9 | 8.59 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| CH-oop (10.5-15 um; benzene nu11 at 673 included) | 9 | 734.4–949.4 | 9.61 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| CH-stretch | 6 | 3174.7–3194.7 | 10.24 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| above 3200 | 2 | 3206.8–3208.1 | 15.87 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| low / skeletal | 10 | 175.6–635.5 | 15.87 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| overtone / combination region | 2 | 1658.8–1688.1 | 15.91 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |
| ring / CH-ip (9-10.5 um) | 5 | 963.1–1055.8 | 15.87 | — | module 03 u_band_by_record_family.csv, naphthalene, record(s) C91203_0.jdx |

*Ensemble ±:* — : no predicted correction is shown; no family licensed: the registered verdict falls at 1,200 admitted layer-B molecules.

## Anchor coverage (coupled-cluster evidence)

| family | modes read | RMS vs CCSD(T) | u_band | reading | evidence |
|---|---|---|---|---|---|
| CH-oop (10.5-15 um; benzene nu11 at 673 included) | 1 | — | 9.61 | a family reading exists (curvature at DZ and TZ); no per-mode deviation table | probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md |
| ring / CH-ip (9-10.5 um) | 1 | — | 15.87 | a family reading exists (curvature at DZ and TZ); no per-mode deviation table | probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md |

## Cost record

| step | machine | hours | € ex VAT | source |
|---|---|---|---|---|
| cheap rung (deck v1, both functionals) | Asus18 | 0.95 | 0.00 | corpus ledger machine column 'Asus18' |
| anchor family readings (M3, two families, laptop) | laptop | 66.83 | 0.00 | probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md (12.2 h per TZ energy); REPRODUCE.md row on the neutral price (4,201 s) |

## Provenance

- releases: layerA2_2026-09-23, layerA2_2026-09-23b, layerA2_2026-09-24, layerA_2026-09-22; deck 97ed2d67c66b; commit 05a95e2; export built 2026-09-28T18:15:10Z
- evidence: probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md (exists); probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md (exists)
- licence: 0 families licensed (GoalGathering/notes/PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md)
- family rule: modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026)
