# Module 04 - paired theory<->lab band table - 2026-09-12 08:19

Built by `build_training_table.py` under RECIPE.md (2026-09-12). The training table is a derived dataset matching public computed bands (PAHdb theoretical v4.00, as served) to public laboratory bands (PAHdb experimental v3.10, argon matrix); it is not AI-generated. Pre-release: the Zenodo release of reading 1 is still the student's action.

**Species joined: 83** (experimental entries without a theoretical record, dropped: ['548']). **Pairs: 2,477** of 3,873 laboratory bands (1,396 unmatched, 36.0%); columns: 28.

Target y = nu_lab - nu_scaled: mean +0.55, median +0.68, SD 9.24, MAE of the zero model 6.49 cm-1; pairs with more than one candidate: 2117.

Per family (target):

```
                                                   count  mean  median    std
family                                                                       
CC-stretch (6.2 um)                                  300  0.24    0.78  10.13
CC-stretch/CH-ip (7.7 um)                            655  1.40    1.55  10.00
CH-ip-bend (8.6 um)                                  367  0.88    1.78   8.71
CH-oop (10.5-15 um; benzene nu11 at 673 included)    617  0.91    0.74   8.91
CH-stretch                                           118 -1.90   -1.38   8.86
low / skeletal                                       233 -0.17   -0.48   5.66
ring / CH-ip (9-10.5 um)                             187 -1.32   -1.04  10.40
```

Ladder molecules:

```
                  count  mean  median
uid species_name                     
18  coronene          9  5.04    3.30
265 anthracene       17  0.98   -1.06
282 tetracene        20  4.81    2.59
291 chrysene         20  2.85    3.13
330 naphthalene      12  0.31   -2.52
334 pyrene           17 -0.78    2.79
```

Constants:

```
{
 "match_window_cm": 30.0,
 "min_computed_intensity_km_mol": 1.0,
 "match_order": "lab bands in descending laboratory intensity; nearest free candidate; one-to-one; no second choice",
 "target": "y = nu_lab - nu_scaled (cm-1), library as served (decision 30)",
 "scale_regions_cm": [
  [
   0,
   1111
  ],
  [
   1111,
   2500
  ],
  [
   2500,
   1000000000.0
  ]
 ],
 "intensity_floor_km_mol": 0.001,
 "ladder_uids": {
  "330": "R1 naphthalene",
  "265": "anthracene (locality probe)",
  "334": "R2 pyrene",
  "282": "R2 tetracene",
  "291": "R2 chrysene",
  "18": "R3 coronene"
 },
 "family_rule_source": "Module 02 build_opponent_atlas.py FAMILY_RULE (the label stored in the band table)"
}
```

Inputs (sha256):

- `theoretical_4.00/bands.csv.gz` - `f9997629812a3e26...`
- `theoretical_4.00/species.csv` - `b9fbefb77ca932f9...`
- `experimental_3.10/bands.csv.gz` - `b325a04aed9dc4d1...`
- `experimental_3.10/species.csv` - `53aa20318ae2d92f...`