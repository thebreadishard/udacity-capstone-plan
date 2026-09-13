# Naphthalene — family labels by DFT mode vector (B3LYP/6-31G*, unscaled; 2026-09-13)

Source: plan 02 git 57a7910, probes/results_dft_locality/naphthalene.npz (B3LYP/6-31G*, psi4); families by plan 05 dryrun_dft_delta_recovery.assign_families (frequency window + out-of-plane share + hydrogen share), via plan 06 X13; IR activity by D2h irrep (B1u, B2u, B3u). 48 modes, 0 imaginary, 20 IR-active.

| family (mode vector) | modes | IR-active | ν range (cm⁻¹, unscaled) | irreps |
|---|---|---|---|---|
| CC-stretch | 9 | 4 | 1410–1688 | Ag, B1g, B2u, B3u |
| CH-ip-bend | 9 | 5 | 1045–1297 | Ag, B1g, B2u, B3u |
| CH-oop | 15 | 4 | 176–994 | Au, B1u, B2g, B3g |
| CH-stretch | 8 | 4 | 3174–3208 | Ag, B1g, B2u, B3u |
| ring-ip | 7 | 3 | 364–949 | Ag, B1g, B2u, B3u |

Window rule versus mode vector: the Module-03 frequency-window label differs in wording for every mode (different label sets); modes where the *physics* differs (an out-of-plane mode inside an in-plane window, or the reverse) are listed in the CSV by comparing the two columns. Modes with imaginary frequency: 0.

| mode | ν (cm⁻¹) | irrep | IR | family (mode vector) | window label |
|---|---|---|---|---|---|
| 0 | 175.6 | B1u | yes | CH-oop | low / skeletal |
| 1 | 189.6 | Au | — | CH-oop | low / skeletal |
| 2 | 363.7 | B2u | yes | ring-ip | low / skeletal |
| 3 | 396.6 | B2g | — | CH-oop | low / skeletal |
| 4 | 482.0 | B3g | — | CH-oop | low / skeletal |
| 5 | 491.5 | B1u | yes | CH-oop | low / skeletal |
| 6 | 517.4 | B1g | — | ring-ip | low / skeletal |
| 7 | 520.4 | Ag | — | ring-ip | low / skeletal |
| 8 | 633.4 | Au | — | CH-oop | low / skeletal |
| 9 | 635.5 | B3u | yes | ring-ip | low / skeletal |
| 10 | 734.5 | B2g | — | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 11 | 775.5 | Ag | — | ring-ip | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 12 | 785.3 | B3g | — | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 13 | 803.9 | B1u | yes | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 14 | 808.2 | B2u | yes | ring-ip | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 15 | 852.4 | Au | — | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 16 | 900.1 | B3g | — | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 17 | 946.9 | B2g | — | CH-oop | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 18 | 949.4 | B1g | — | ring-ip | CH-oop (10.5-15 um; benzene nu11 at 673 included) |
| 19 | 963.2 | B1u | yes | CH-oop | ring / CH-ip (9-10.5 um) |
| 20 | 985.1 | Au | — | CH-oop | ring / CH-ip (9-10.5 um) |
| 21 | 993.8 | B3g | — | CH-oop | ring / CH-ip (9-10.5 um) |
| 22 | 1045.3 | B3u | yes | CH-ip-bend | ring / CH-ip (9-10.5 um) |
| 23 | 1055.7 | Ag | — | CH-ip-bend | ring / CH-ip (9-10.5 um) |
| 24 | 1157.1 | B2u | yes | CH-ip-bend | CH-ip-bend (8.6 um) |
| 25 | 1181.3 | B1g | — | CH-ip-bend | CH-ip-bend (8.6 um) |
| 26 | 1184.3 | B3u | yes | CH-ip-bend | CH-ip-bend (8.6 um) |
| 27 | 1194.0 | Ag | — | CH-ip-bend | CH-ip-bend (8.6 um) |
| 28 | 1244.0 | B3u | yes | CH-ip-bend | CH-ip-bend (8.6 um) |
| 29 | 1278.0 | B1g | — | CH-ip-bend | CC-stretch/CH-ip (7.7 um) |
| 30 | 1297.4 | B2u | yes | CH-ip-bend | CC-stretch/CH-ip (7.7 um) |
| 31 | 1409.9 | B3u | yes | CC-stretch | CC-stretch/CH-ip (7.7 um) |
| 32 | 1416.6 | Ag | — | CC-stretch | CC-stretch/CH-ip (7.7 um) |
| 33 | 1431.2 | B2u | yes | CC-stretch | CC-stretch/CH-ip (7.7 um) |
| 34 | 1505.7 | B1g | — | CC-stretch | CC-stretch (6.2 um) |
| 35 | 1509.8 | Ag | — | CC-stretch | CC-stretch (6.2 um) |
| 36 | 1567.6 | B3u | yes | CC-stretch | CC-stretch (6.2 um) |
| 37 | 1630.1 | Ag | — | CC-stretch | CC-stretch (6.2 um) |
| 38 | 1658.8 | B2u | yes | CC-stretch | overtone / combination region |
| 39 | 1688.4 | B1g | — | CC-stretch | overtone / combination region |
| 40 | 3174.3 | B1g | — | CH-stretch | CH-stretch |
| 41 | 3176.4 | B2u | yes | CH-stretch | CH-stretch |
| 42 | 3177.8 | B3u | yes | CH-stretch | CH-stretch |
| 43 | 3181.5 | Ag | — | CH-stretch | CH-stretch |
| 44 | 3193.3 | B2u | yes | CH-stretch | CH-stretch |
| 45 | 3194.4 | B1g | — | CH-stretch | CH-stretch |
| 46 | 3206.7 | Ag | — | CH-stretch | above 3200 |
| 47 | 3208.0 | B3u | yes | CH-stretch | above 3200 |

Use in the scoreboard: assign an observed naphthalene band to the nearest IR-active mode of the same family after scaling (the scaling and the assignment rule are the pilot note's, not this table's); the C–H out-of-plane sub-families by hydrogen adjacency (Q9, decision 27) need the mode vectors themselves (in plan 02's npz), not this table.

Constants: {"source": "plan 02 git 57a7910, probes/results_dft_locality/naphthalene.npz (B3LYP/6-31G*, psi4)", "ir_active_irreps_D2h": ["B1u", "B2u", "B3u"], "family_rule": "plan 05 dryrun_dft_delta_recovery.assign_families (frequency window + out-of-plane share + hydrogen share), via plan 06 X13", "window_rule": "Module 03 build_lab_tables.FAMILY_RULE applied to the unscaled harmonic frequency"}