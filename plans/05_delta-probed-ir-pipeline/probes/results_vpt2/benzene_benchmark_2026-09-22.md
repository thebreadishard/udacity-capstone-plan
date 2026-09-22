# Benzene: our modes against Goodman 1991 / Miani 2000 — qff_benzene_pyscf_analytic_d010_2026-09-21.npz

Mapping by class (e pairs, a1g by |φ_iii|, other non-degenerate) and rank against Miani's B3LYP/TZ2P ω; see the script docstring. Δν = ν − ω is the anharmonic shift; ours from the two-route QFF, Miani's from their B3LYP/TZ2P force field (Table VII, ε = 0). ω_exp are experiment-derived harmonics: Goodman's Table II estimate (corrections applied to nine modes only) and Miani's Table II 'this work'.

| ours | ω 6-31G* | ν ours | Δν ours | Wilson | sym | ω TZ2P | ν Miani | Δν Miani | ω_exp Goodman | ω_exp Miani | ν exp | ν ours − ν exp | note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0/1 | 414.5 | 407.5 | -7.0 | ν16 | e2u | 412 | 403 | -9 | 398 | 406 | 398* | +9.5 |  |
| 2/3 | 621.6 | 616.2 | -5.4 | ν6 | e2g | 624 | 615† | -9 | 607.8 | 611 | 608.13 | +8.1 |  |
| 4 | 695.1 | 685.0 | -10.0 | ν11 | a2u | 686 | 677 | -9 | 674.0 | 687 | 673.97465 | +11.1 |  |
| 5 | 718.0 | 708.3 | -9.8 | ν4 | b2g | 723 | 708 | -15 | 707 | 709 | 707* | +1.3 |  |
| 6/7 | 865.2 | 850.6 | -14.5 | ν10 | e1g | 864 | 846 | -18 | 847.1 | 865 | 847.1 | +3.5 |  |
| 8/9 | 969.8 | 965.6 | -4.2 | ν17 | e2u | 992 | 972 | -20 | 967 | 985 | 967* | -1.4 |  |
| 10 | 1011.5 | 994.3 | -17.2 | ν5 | b2g | 1017 | 997 | -20 | 990 | 1009 | 990* | +4.3 | near-crossing: rank-assigned |
| 11 | 1019.2 | 1007.4 | -11.8 | ν12 | b1u | 1031 | 1015 | -16 | 1010 | 1020 | 1010* | -2.6 | near-crossing: rank-assigned |
| 12 | 1021.7 | 1004.4 | -17.4 | ν1 | a1g | 1012 | 995 | -17 | 994.4 | 1003 | 993.071 | +11.3 |  |
| 13/14 | 1069.7 | 1052.5 | -17.2 | ν18 | e1u | 1060 | 1038 | -22 | 1038.3 | 1056 | 1038.267 | +14.3 |  |
| 15 | 1185.7 | 1174.8 | -10.9 | ν15 | b2u | 1178 | 1163 | -15 | 1149.7 | 1163 | 1149.7 | +25.1 |  |
| 16/17 | 1207.9 | 1192.9 | -15.0 | ν9 | e2g | 1201 | 1181 | -20 | 1177.8 | 1194 | 1177.776 | +15.1 |  |
| 18 | 1358.5 | 1324.0 | -34.5 | ν14 | b2u | 1333 | 1305 | -28 | 1309.4 | 1326 | 1309.4 | +14.6 |  |
| 19 | 1388.1 | 1367.1 | -21.0 | ν3 | a2g | 1392 | 1351† | -41 | 1367 | 1380 | 1350* | +17.1 |  |
| 20/21 | 1532.3 | 1501.7 | -30.6 | ν19 | e1u | 1519 | 1484 | -35 | 1494 | 1509 | 1483.9854 | +17.7 |  |
| 22/23 | 1657.3 | 1617.7 | -39.6 | ν8 | e2g | 1635 | 1613† | -22 | 1607 | 1637 | 1600.976 | +16.7 |  |
| 24 | 3176.2 | 3035.4 | -140.8 | ν13 | b1u | 3159 | 2988† | -171 | 3174 | 3173 | 3057* | -21.6 |  |
| 25/26 | 3185.9 | 3045.0 | -140.8 | ν7 | e2g | 3168 | 3028 | -140 | 3174 | 3183 | 3056.7 | -11.7 |  |
| 27/28 | 3201.8 | 3062.9 | -139.0 | ν20 | e1u | 3183 | 3023† | -160 | 3181.1 | 3200 | 3064.3674 | -1.5 |  |
| 29 | 3212.6 | 3070.6 | -141.9 | ν2 | a1g | 3192 | 3051† | -141 | 3191 | 3210 | 3073.942 | -3.3 |  |

\* estimated from infrared combinations (Goodman Table I, in parentheses there). † Miani's value with Fermi resonances within 100 cm⁻¹ treated (Table VII, ε = 100); the others are their ε = 0 values, the only ones the paper lists for those modes.

- anharmonic shifts, ours vs Miani over the 20 modes: median |difference| 4.3 cm⁻¹, max 30.2; without the four C–H stretches: median 4.3, max 20.0
- fundamentals against experiment, ours (B3LYP/6-31G*): MAE 10.6 cm⁻¹ (without C–H stretches 10.9); Miani's B3LYP/TZ2P: MAE 11.6 (without C–H stretches 4.4)
