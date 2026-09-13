# T-1 transfer test — source benzene, target naphthalene (2026-09-13 11:33)

Rule: mode-resolved: each target mode takes delta_nu/nu of the source mode nearest in relative position within the same family (rank position in the family's frequency span); losing condition: RMS error > 2.5 cm⁻¹ for CH-stretch, CC-stretch (Module 03 U_BAND.md: QUANT-IR benzene gas-phase u_band 2.55 cm-1 (R0 floor form)). Stand-in: {'low': 'b3lyp', 'high': 'bhhlyp'}.

## Source (benzene): per-family relative correction and the within-molecule floor of the rule

| family | modes | median δν/ν | median δν (cm⁻¹) | δν range (cm⁻¹) | floor: RMS of the rule inside the source (cm⁻¹) |
|---|---|---|---|---|---|
| CC-stretch | 6 | +0.0291 | +46.2 | -35.6 … +64.9 | 32.62 |
| CH-ip-bend | 7 | +0.0305 | +31.6 | +12.1 … +43.6 | 8.14 |
| CH-oop | 9 | +0.0903 | +78.1 | +36.3 … +84.4 | 12.62 |
| CH-stretch | 6 | +0.0079 | +25.1 | +24.7 … +25.4 | 0.17 |
| ring-ip | 2 | +0.0371 | +23.1 | +23.0 … +23.1 | 0.04 |

## Transfer to naphthalene: **NOT_RUN** — `results_dryrun/naphthalene/stageA.json` does not exist yet (machine queue item 5).