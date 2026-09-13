# T-1 transfer test — source benzene, target benzene (2026-09-13 11:21)

Rule: relative: delta_nu/nu per family (median); losing condition: RMS error > 2.5 cm⁻¹ for CH-stretch, CC-stretch (Module 03 U_BAND.md: QUANT-IR benzene gas-phase u_band 2.55 cm-1 (R0 floor form)). Stand-in: {'low': 'b3lyp', 'high': 'bhhlyp'}.

## Source (benzene): per-family relative correction and the within-molecule floor of the rule

| family | modes | median δν/ν | median δν (cm⁻¹) | δν range (cm⁻¹) | floor: RMS of the rule inside the source (cm⁻¹) |
|---|---|---|---|---|---|
| CC-stretch | 6 | +0.0291 | +46.2 | -35.6 … +64.9 | 32.62 |
| CH-ip-bend | 7 | +0.0305 | +31.6 | +12.1 … +43.6 | 8.14 |
| CH-oop | 9 | +0.0903 | +78.1 | +36.3 … +84.4 | 12.62 |
| CH-stretch | 6 | +0.0079 | +25.1 | +24.7 … +25.4 | 0.17 |
| ring-ip | 2 | +0.0371 | +23.1 | +23.0 … +23.1 | 0.04 |

## Transfer to benzene

| family | target modes | in source | RMS error, relative rule (cm⁻¹) | max | RMS zero rule | RMS absolute rule | judged | passes 2.5 |
|---|---|---|---|---|---|---|---|---|
| CC-stretch | 6 | yes | **32.62** | 75.12 | 48.46 | 34.42 | yes | NO |
| CH-ip-bend | 7 | yes | **8.14** | 19.08 | 34.69 | 10.17 | — | NO |
| CH-oop | 9 | yes | **12.62** | 28.52 | 70.35 | 22.52 | — | NO |
| CH-stretch | 6 | yes | **0.17** | 0.26 | 25.11 | 0.24 | yes | yes |
| ring-ip | 2 | yes | **0.04** | 0.04 | 23.07 | 0.04 | — | yes |

**Verdict (judged families only): LOSE.** The zero rule is the floor a useful rule must beat; the absolute rule is the secondary comparison.

Self-test: source = target — the transfer errors equal the within-molecule floors by construction (the rule applied to itself).