# Substituted training molecules: the step's scaffold-left-out error beside the printed bars

Registration: `GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md`, section 5 (descriptive; no run). Source: `probes/results_m1/anharmonic_design_questions_2026-11-16/modes.json`, `per_molecule`, `rms_inputs_on_B`: x2* fitted without the molecule's scaffold, against the molecule's B3LYP GVPT2 label; rms in cm⁻¹ with the number of modes. Bold: above the bar with at least 4 modes.

| molecule | id | CH-oop | other | ring-ip | CH-stretch | all |
|---|---|---|---|---|---|---|
| naphthalene+CN | B_a41f4cff9d | 1.85 (5) | 1.68 (8) | 2.20 (16) | 3.40 (7) | 2.35 (36) |
| oxazole+CN | B_052693bd01 | 3.36 (2) | 1.73 (5) | **6.80 (8)** | 4.98 (2) | 5.18 (17) |
| phenylacetylene | A_a848c04a21 | 4.92 (6) | 3.47 (2) | **3.48 (12)** | **11.85 (5)** | 6.38 (25) |
| benzene+NH2+ethynyl | B_410ac0fb2f | — | **7.41 (7)** | **5.18 (11)** | 4.80 (4) | 5.92 (22) |
| isoquinoline+CH3 | B_079e66d017 | — | 3.31 (10) | 2.91 (24) | **12.35 (9)** | 6.26 (43) |
| azulene+NH2 | B_78f8233b4c | — | **6.15 (10)** | **4.51 (15)** | **17.98 (7)** | 9.59 (32) |
| azulene+ethynyl | B_0603418c5b | **9.04 (9)** | 1.92 (4) | **3.58 (18)** | **9.24 (7)** | 6.44 (38) |
| printed bar | | 8.38 | 3.84 | 3.37 | 6.21 | |

## Beside the unsubstituted molecules of the same read

Molecules with at least 4 modes in the family: how many lie above the printed bar, how many beyond the 95% line for their number of modes, the median of their rms, and the rms pooled over every mode of the group. Unsubstituted: 31 molecules, the bare ring systems of the training table and coronene (a target, fitted on all training molecules).

| family | bar | substituted: above / beyond / of | median | pooled | unsubstituted: above / beyond / of | median | pooled |
|---|---|---|---|---|---|---|---|
| CH-oop | 8.38 | 1 / 0 / 3 | 4.92 | 6.47 | 3 / 1 / 28 | 3.96 | 5.79 |
| other | 3.84 | 2 / 2 / 6 | 2.62 | 4.54 | 4 / 3 / 30 | 1.53 | 3.12 |
| ring-ip | 3.37 | 5 / 3 / 7 | 3.58 | 3.95 | 6 / 1 / 31 | 2.76 | 2.96 |
| CH-stretch | 6.21 | 4 / 4 / 6 | 10.55 | 11.22 | 22 / 7 / 31 | 7.27 | 8.52 |

The substituted molecules were in the fit of every scaffold but their own, and the bars were measured on two other molecules: the table says which outcome to expect of an unseen substituted molecule, it is not that measurement.
