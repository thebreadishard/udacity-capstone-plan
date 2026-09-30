# Stop-rule read-out — all_p2s1_w0_merged.json (solver prior w 0 cm⁻¹) against band_p2s1A_merged.json; 2026-09-30 06:59 — reading (ii): band-free solver prior (w-cm 0), P12 and oracle; laptop 29 Sep 21:57 → 22:58

τ_stop 0.3, B_max = 2 × whole band deck, false stop = frob_off > 0.4 at the stop; seeds [0, 1, 2]; W1/W2 judged on P12.

## all: 97 molecules, median M 60, median whole band deck 1560 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 24 / 97 (25 %) | 1859 | 1.19 | 1.57 | 23 (96 %) | 115 |
| P12 | 39 / 97 (40 %) | 1794 | 1.15 | 1.24 | 11 (28 %) | 110 |
| P3_oracle | 53 / 97 (55 %) | 840 | 0.54 | 0.65 | 1 (2 %) | 110 |

## eval_parents: 41 molecules, median M 57, median whole band deck 1360 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 12 / 41 (29 %) | 1859 | 1.37 | 1.65 | 11 (92 %) | 104 |
| P12 | 25 / 41 (61 %) | 1752 | 1.29 | 1.34 | 5 (20 %) | 98 |
| P3_oracle | 29 / 41 (71 %) | 730 | 0.54 | 0.55 | 1 (3 %) | 98 |

## eval: 56 molecules, median M 64, median whole band deck 1686 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 12 / 56 (21 %) | 1913 | 1.13 | 1.53 | 12 (100 %) | 122 |
| P12 | 14 / 56 (25 %) | 1887 | 1.12 | 1.05 | 6 (43 %) | 122 |
| P3_oracle | 24 / 56 (43 %) | 1109 | 0.66 | 0.70 | 0 (0 %) | 122 |

**W1** (P12: stopped on ≥ 90 % and ratio of medians ≤ 1.5): FAIL (40 %, 1.15×). **W2** (false stops ≤ 5 %): FAIL (28 %).
