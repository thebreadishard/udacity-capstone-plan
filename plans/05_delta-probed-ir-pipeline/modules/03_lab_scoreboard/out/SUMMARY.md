# Module 03 - laboratory band dataset and matrix-gas pairs - 2026-09-12 18:19

Built by `build_lab_tables.py` under PRE_REGISTRATION.md (2026-09-11). These are laboratory measurements from the public PAHdb experimental library and the NIST Chemistry WebBook. Not synthetic, not AI-generated, not the Module 02 dataset.

**Dataset `notebook/bands_lab.csv`: 4,218 rows x 31 columns** - matrix bands 3,896 (84 species), gas peaks 318 (8 records, 6 species), R0 scoreboard rows 4.

| gas record | species | source | state | stated resolution | grid | points | noise sigma (absorbance) | peaks | role |
|---|---|---|---|---|---|---|---|---|---|
| C91203_0.jdx | naphthalene | MSDC-IR | gas | - (8.0 by series description) | 4 | 880 | 8.49e-04 | 58 | primary |
| C120127_0.jdx | anthracene | MSDC-IR | gas | - (8.0 by series description) | 4 | 880 | 4.89e-04 | 44 | primary |
| C129000_0.jdx | pyrene | MSDC-IR | gas | - (8.0 by series description) | 4 | 825 | 1.09e-05 | 29 | primary |
| C218019_0.jdx | chrysene | MSDC-IR | gas | - (8.0 by series description) | 4 | 825 | 1.25e-05 | 28 | primary |
| C217594_0.jdx | triphenylene | MSDC-IR | gas | - (8.0 by series description) | 4 | 825 | 9.93e-06 | 32 | gas only |
| C71432_0.jdx | benzene | MSDC-IR | gas | - (8.0 by series description) | 4 | 880 | 1.14e-03 | 39 | gas only |
| C91203_1.jdx | naphthalene | COBLENTZ | VAPOR (1.0 MICROLITER AT 245 C) | 4 CM^-^1 | 1.19 | 2762 | 4.34e-04 | 39 | secondary |
| C71432_1.jdx | benzene | COBLENTZ | GAS (70 mmHg, N2 ADDED, TOTAL PRESSURE 6 | 2 | 1 | 3343 | 4.04e-04 | 49 | gas only |

**Pairs `notebook/pairs_matrix_gas.csv`: 74** (primary 63, secondary 11).

| species / record | gas peaks | pairs | gas unmatched | matrix bands | matrix unmatched |
|---|---|---|---|---|---|
| naphthalene / C91203_0.jdx (primary) | 58 | 13 | 45 | 19 | 6 |
| anthracene / C120127_0.jdx (primary) | 44 | 20 | 24 | 29 | 9 |
| pyrene / C129000_0.jdx (primary) | 29 | 13 | 16 | 22 | 9 |
| chrysene / C218019_0.jdx (primary) | 28 | 17 | 11 | 23 | 6 |
| naphthalene / C91203_1.jdx (secondary) | 39 | 11 | 28 | 19 | 8 |

u_band per record and family: `out/U_BAND.md` (75 rows); pairs carry u_T_gas_cm, u_band_gas_cm and decidable_at_2/5/10.

Primary pairs per family (descriptive; the test itself runs in the notebook):

```
                                                   count  median  mean   std
family                                                                      
CC-stretch (6.2 um)                                    7    4.64  4.87  2.66
CC-stretch/CH-ip (7.7 um)                             10    3.49  3.86  2.72
CH-ip-bend (8.6 um)                                    7    3.30  5.02  5.67
CH-oop (10.5-15 um; benzene nu11 at 673 included)     11    3.64  3.29  1.60
CH-stretch                                             4   -0.78  0.27  3.11
low / skeletal                                         5    1.57  0.92  3.26
overtone / combination region                         12    5.92  6.69  3.97
ring / CH-ip (9-10.5 um)                               7    3.58  4.60  2.64
```

Constants:

```
{
 "noise_window_cm": [
  2400.0,
  2500.0
 ],
 "noise_rule": "1.4826 * MAD of the linearly detrended noise window",
 "peak_prominence_sigma": 5.0,
 "peak_min_snr": 10.0,
 "position_rule": "parabolic apex through the maximum and its two neighbours",
 "u_c_rule": "u_c = FWHM / (2 * S/N)",
 "match_window_cm": 20.0,
 "match_choice": "largest matrix intensity inside the window; one-to-one, closer gas peak keeps a contested band",
 "msdc_ir_resolution_cm": 8.0,
 "matrix_resolution_cm_hudgins1998": 0.9,
 "matrix_temperature_K_hudgins1998": 10.0,
 "family_rule_source": "Module 02 build_opponent_atlas.py FAMILY_RULE (copied verbatim)",
 "u_band_rule": "u_band = sqrt(u_res^2 + u_c^2 + u_T^2); hot source: u_T = chi_F * (T_source - 296 K) + u_296 (Ladder floor form, no correction applied); delta_T = chi_F * (T_source - 296 K) is printed beside it as the hot-band correction the pilot note may apply (+-30 % form)",
 "chi_F_rule": "per (molecule, family): the molecule's own measured slope from item 52 Table 1 (largest |chi'| of the P/H/D fits); else pyrene's slope for that family as a labelled stand-in (Ladder dated note 2026-09-06 (ii)); else the floor 0.044 cm-1/K (largest measured 6-15 um slope)",
 "chi_floor_cm_per_K": 0.044,
 "u_296_rule": "u_296 = chi_F * (hc nu_m / k_B) * nbar(nu_m, 296 K); nu_m = mean of the PAHdb theoretical v4.00 B3LYP/4-31G unscaled harmonic frequencies below 700 cm-1 for the species' uid (benzene: probe 2a's DFT bath, 553.8 cm-1, the library has no benzene)",
 "bath_mode_cutoff_cm": 700.0,
 "T_source_rule": "245 C where the record states it (Coblentz naphthalene vapour). GC-IRD records: the SRD 35 users' guide (item 50, read in full 2026-09-12) documents NO temperature - for the EPA/Sadtler spectra it says the original header information was not located and 'analytical conditions are not given'; for the NIST spectra only the instrument (HP GC-MS-IR, IRD 5965) and 8 cm-1. So T_source = 523.15 K is the Ladder's hot-default ASSUMPTION, labelled per record origin, not a documented or recalled instrument value. A record with neither a stated temperature nor series documentation (Dow benzene cell) is treated the same way (Ladder rule)",
 "T_gcird_default_K": 523.15,
 "T_ref_K": 296.0,
 "candidate_margins_cm": [
  2.0,
  5.0,
  10.0
 ]
}
```

Inputs (sha256):

- `plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas/out/experimental_3.10/bands.csv.gz` - `b325a04aed9dc4d1...`
- `plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas/out/experimental_3.10/species.csv` - `53aa20318ae2d92f...`
- `plans/05_delta-probed-ir-pipeline/modules/02_opponent_atlas/out/theoretical_4.00/bands.csv.gz` - `f9997629812a3e26...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C91203_0.jdx` - `e3cdfa7709578efa...`
- `plans/02_coupled-cluster-anharmonic-ir/probes/nist_cache/C120127_0.jdx` - `5ef5e17f19bbaa40...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C129000_0.jdx` - `66f830281a8343a6...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C218019_0.jdx` - `22f14d60e2ec674f...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C217594_0.jdx` - `00afbc5610db8041...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C71432_0.jdx` - `167a29781624908d...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C91203_1.jdx` - `c3d303a075457288...`
- `plans/04_cc-anchored-ir-pipeline/probes/nist_cache/C71432_1.jdx` - `392cd7684f8d9352...`
- `plans/05_delta-probed-ir-pipeline/probes/results_m03/benzene/SCOREBOARD_benzene_quantir_0p125.json` - `bad6dfdf70753c47...`