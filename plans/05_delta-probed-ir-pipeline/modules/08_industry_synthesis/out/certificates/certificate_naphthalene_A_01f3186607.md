# Certificate — naphthalene (A_01f3186607), rung 4 · anchored — 2026-11-15 02:48

naphthalene: rung 4 (anchored). The cheap-level spectrum is served with the laboratory tolerance per family; no predicted correction is shown in this record — the pipeline serves it for the licensed families (ring-ip, CH-stretch, CH-oop; decision 65); the anchor coverage lists what coupled-cluster evidence exists and where it is wider than the tolerance.

## Ladder

| rung | label | status |
|---|---|---|
| 0 | listed | reached |
| 1 | cheap_level_done | reached |
| 2 | correction_predicted | — not in this record: the pipeline (m08/pipeline.py) serves it for the licensed families (decision 65) |
| 3 | spectrum_predicted | — not in this record: the pipeline (m08/pipeline.py) serves it for the licensed families (decision 65); heights only where an APT exists |
| 4 | anchored | reached |
| 5 | validated | — not reached |

## Spectrum (cheap rung; harmonic, cm⁻¹)

- **b3lyp**: 48 vibrational modes, 0 imaginary; source website export molecules/A_01f3186607.json ← corpus molecules/A_01f3186607/ (deck 97ed2d67c66b)
- **wb97x**: 48 vibrational modes, 0 imaginary; source website export molecules/A_01f3186607.json ← corpus molecules/A_01f3186607/ (deck 97ed2d67c66b)

## Spectral shape (cheap rung; positions and heights)

Positions only: no dipole derivatives (APT) computed for this molecule — heights are not shown rather than guessed.

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

*Ensemble ±:* — : this record is the cheap level; the pipeline serves the correction with its measured error (licence, decision 65: licensed at the DFT proxy: ring-ip (1.77 / 2.12), CH-stretch (1.19 / 2.5), CH-oop (2.17 / 2.7); not licensed: other (3.62 / 3.89) — seed-mean error on hold-outs (a) / (b) in cm⁻¹ against 3; no coupled-cluster licence).

## The anchor in force

**CCSD(T)/cc-pVDZ + [MP2/cc-pVTZ − MP2/cc-pVDZ]** (composite, basis tier TZ), registered 2026-10-07, `modules/05_support_predictor/out/composite_full_naphthalene_2026-10-07.npz` (sha16 `3d37769ea7dcd41c`).

Checks that passed: MP2 row symmetry spread 2.9e-05 / 4.0e-05; basis step rms 6.3e-03; softest 167, 180 cm⁻¹.

Source: `modules/05_support_predictor/out/ANCHORS_STATUS.json`, the project's anchor registry.

## Anchor coverage (coupled-cluster evidence)

| family | modes read | RMS vs CCSD(T) | u_band | reading | evidence |
|---|---|---|---|---|---|
| ring / CH-ip (9-10.5 um) | 1 | — | 15.87 | a family reading exists (curvature at DZ and TZ); no per-mode deviation table | probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md |

## Cost record

| step | machine | hours | € ex VAT | source |
|---|---|---|---|---|
| cheap rung (deck v1, both functionals) | Asus18 | 0.95 | 0.00 | corpus ledger machine column 'Asus18' |
| anchor family readings (M3, two families, laptop) | laptop | 66.83 | 0.00 | probes/results_m1/M3_TZ_MODE12_READING_2026-09-20.md (12.2 h per TZ energy); REPRODUCE.md row on the neutral price (4,201 s) |

## Provenance

- releases: layerA2_2026-09-23, layerA2_2026-09-23b, layerA2_2026-09-24, layerA_2026-09-22; deck 97ed2d67c66b; commit 04241d7f; export built 2026-11-02T10:01:23Z
- evidence: modules/05_support_predictor/out/composite_full_naphthalene_2026-10-07.npz (exists); probes/results_m1/e8_naphthalene_ccpvdz_tlambda_2026-10-02/E8_locality_naphthalene.md (exists); probes/results_m1/M3_TZ_MODE22_READING_2026-09-23.md (exists)
- licence: 3 families licensed (README.md, decision 65)
- family rule: modules/03_lab_scoreboard/build_lab_tables.py FAMILY_RULE (12 Sep 2026)
