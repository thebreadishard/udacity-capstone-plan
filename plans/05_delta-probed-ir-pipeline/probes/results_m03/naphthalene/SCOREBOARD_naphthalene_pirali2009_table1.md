# Scoreboard — naphthalene — Pirali, Vervloet, Mulas, Malloci & Joblin, Phys. Chem. Chem. Phys. 11, 3443-3454 (2009), DOI 10.1039/b814037e (pirali2009_table1) — probe 2a, 2026-09-11 07:58

Source class: **gas, room temperature, resolved fundamental (decision 21)**, 300 K; transcription `pirali2009_table1.json`, sha256 `28a6a0c1d7a76cef…`. u_band = √(res² + reading² + head-to-origin²) with res = 0.005 cm⁻¹ (the paper's resolution), reading = half the last printed digit, head-to-origin = 0.5 cm⁻¹ (decision 21's labelled upper bound), u_T = 0 (the fundamental is resolved from its hot bands). No intensities in this source.

| mode | irrep | band type | position (cm⁻¹, as printed) | family | reading | **u_band** | Cané calc. | decidable at 2 / 5 / 10 | flag |
|---|---|---|---|---|---|---|---|---|---|
| nu20 | b1u | a/b-type, in-plane | **1392.5** | CC-stretch/CH-ip | 0.05 | **0.503** | 1388.4 | yes / yes / yes |  |
| nu21 | b1u | a/b-type, in-plane | **1268.0** | CC-stretch/CH-ip | 0.05 | **0.503** | 1265.2 | yes / yes / yes |  |
| nu22 | b1u | a/b-type, in-plane | **1130** | CH-ip-bend | 0.5 | **0.707** | 1130.5 | yes / yes / yes |  |
| nu24 | b1u | a/b-type, in-plane | **358.7** | low / skeletal | 0.05 | **0.503** | 358.7 | yes / yes / yes |  |
| nu29 | b2u | a/b-type, in-plane | **3057** | CH-stretch | 0.5 | **0.707** | 3048.1 | yes / yes / yes |  |
| nu30 | b2u | a/b-type, in-plane | **3042** | CH-stretch | 0.5 | **0.707** | 2989.9 | yes / yes / yes |  |
| nu31 | b2u | a/b-type, in-plane | **1514.3** | CC-stretch | 0.05 | **0.503** | 1504.3 | yes / yes / yes |  |
| nu32 | b2u | a/b-type, in-plane | **1361.1** | CC-stretch/CH-ip | 0.05 | **0.503** | 1357.9 | yes / yes / yes |  |
| nu33 | b2u | a/b-type, in-plane | **1210.2** | CH-ip-bend | 0.05 | **0.503** | 1209.8 | yes / yes / yes |  |
| nu34 | b2u | a/b-type, in-plane | **1135.5** | CH-ip-bend | 0.05 | **0.503** | 1144.2 | yes / yes / yes |  |
| nu35 | b2u | a/b-type, in-plane | **1011.89** | ring / CH-ip | 0.005 | **0.5** | 1012.1 | yes / yes / yes |  |
| nu36 | b2u | a/b-type, in-plane | **619.5** | low / skeletal | 0.05 | **0.503** | 623.7 | yes / yes / yes |  |
| nu45 | b3u | c-type, out-of-plane | **959.04** | CH-oop / out-of-plane (b3u) | 0.005 | **0.5** | 958.9 | yes / yes / yes | running text: 959.5 |
| nu46 | b3u | c-type, out-of-plane | **782.33** | CH-oop / out-of-plane (b3u) | 0.005 | **0.5** | 783.4 | yes / yes / yes |  |
| nu47 | b3u | c-type, out-of-plane | **473.33** | CH-oop / out-of-plane (b3u) | 0.005 | **0.5** | 473.2 | yes / yes / yes |  |
| nu48 | b3u | c-type, out-of-plane | **166.4** | CH-oop / out-of-plane (b3u) | 0.05 | **0.503** | 166.4 | yes / yes / yes |  |

Notes from the transcription: Values are printed by the paper to differing precision (two decimals, one decimal, or integer); the transcription keeps the paper's digits and the script takes half the last printed digit as the reading precision. The running text gives nu45 'observed in the high-resolution spectra at 959.5 cm-1' while Table 1 gives 959.04; the table value is used and the discrepancy is flagged in the row. b1u and b2u are in-plane (a-/b-type bands, read at lower signal-to-noise per the paper); b3u are out-of-plane c-type bands with sharp Q branches in which the fundamental is resolved from its hot-band sequences. The 'Calculations' column (Cane et al.'s B97-1/TZ2P anharmonic set as re-solved by the authors) is transcribed for reference only and is not a scoreboard value.

Matching to the pipeline's DFT modes (irrep, family by mode vector) waits for the naphthalene dry-run mode table; the family column is the frequency-range rule plus the paper's symmetry. Printed by `probes/m03_band_uncertainty.py --table`.
