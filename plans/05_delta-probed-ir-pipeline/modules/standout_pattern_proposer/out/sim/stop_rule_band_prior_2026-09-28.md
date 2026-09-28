# Stop-rule read-out — all_p2s1_merged.json (solver prior w 200 cm⁻¹) against band_p2s1A_merged.json; 2026-09-28 21:51 — reading (i): as registered, band prior, P2 = stage-1 recipe

τ_stop 0.3, B_max = 2 × whole band deck, false stop = frob_off > 0.4 at the stop; seeds [0, 1, 2]; W1/W2 judged on P12.

## all: 97 molecules, median M 60, median whole band deck 1560 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 27 / 97 (28 %) | 1750 | 1.12 | 1.72 | 24 (89 %) | 98 |
| P12 | 51 / 97 (53 %) | 1650 | 1.06 | 1.36 | 15 (29 %) | 110 |
| P3_oracle | 73 / 97 (75 %) | 876 | 0.56 | 0.71 | 2 (3 %) | 110 |

## eval_parents: 41 molecules, median M 57, median whole band deck 1360 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 11 / 41 (27 %) | 1750 | 1.29 | 1.79 | 10 (91 %) | 70 |
| P12 | 26 / 41 (63 %) | 1564 | 1.15 | 1.35 | 5 (19 %) | 98 |
| P3_oracle | 35 / 41 (85 %) | 660 | 0.49 | 0.63 | 2 (6 %) | 98 |

## eval: 56 molecules, median M 64, median whole band deck 1686 energies

| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |
|---|---|---|---|---|---|---|
| P0 | 16 / 56 (29 %) | 1768 | 1.05 | 1.57 | 14 (88 %) | 115 |
| P12 | 25 / 56 (45 %) | 1898 | 1.13 | 1.40 | 10 (40 %) | 146 |
| P3_oracle | 38 / 56 (68 %) | 1227 | 0.73 | 0.90 | 0 (0 %) | 134 |

**W1** (P12: stopped on ≥ 90 % and ratio of medians ≤ 1.5): FAIL (53 %, 1.06×). **W2** (false stops ≤ 5 %): FAIL (29 %).
