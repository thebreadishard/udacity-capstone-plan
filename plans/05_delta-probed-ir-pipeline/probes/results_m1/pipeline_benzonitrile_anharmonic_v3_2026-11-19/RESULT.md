# Benzonitrile on the anharmonic step's format 3 — result (19 Nov 2026, TASKS 211 step 2)

Run spec `benzonitrile_anharm_v3_2026-11-19`, launched 20:06:31, exit 0; pipeline 0.14, v1.4 release networks, artefact
`x2star_v3.json` (sha16 0bc87e653fb05d6d). Registered before launch in `REGISTRATION_2026-11-19.md`, which says check 1 would
not be read.

| check | result | numbers |
|---|---|---|
| 1. steps within tolerance of an independent field | not read | no stored GFN2-xTB quartic field exists for any substituted molecule outside x2*'s table |
| 2. no band lost | pass, against the registered replay count | 27 of 33 stepped; the 6 without a step are 'unmeasured' (the five lowest, 167.5–467.9 cm⁻¹, and the C≡N stretch at 2386.3); no 'no-xtb-partner' |
| 3. degenerate pairs equal | not applicable | no degenerate pair (C2v) |
| 4. time and memory recorded | pass | 1830.9 s, 1003 MB peak (the search ran beside it; 655.9 s on 17 Nov) |

Against the run of 17 Nov (information, not a check: the same code on the same geometry): all 27 steps agree to 0.1 cm⁻¹.

What this does not show: that the step is right for a substituted molecule — that needs an independent field (check 1). The
substituent's own band (C≡N) is printed harmonic. At 1831 s beside the search the force field alone exceeds the demo's half hour.

## Note of 20 November 2026, 12:5x — what check 1 is (appended; the text above stands as written)

The last paragraph says that showing "the step is right for a substituted molecule … needs an independent field (check 1)". That
is not what check 1 measures. By its definition (`../anharmonic_step_2026-11-17/first_run_checks.py`, lines 12-14 and 21-22) check
1 compares the steps from two GFN2-xTB force fields of one molecule at one level of theory: it bounds the scatter between two
fields, and a pass says the steps are reproducible, not that they are right. Whether they are right for a substituted molecule
is the step's error against its B3LYP GVPT2 label, which has not been measured on any substituted molecule outside x2*'s table.
Both are registered in `GoalGathering/notes/PreRegistration_2026-11-20_Anharmonic_Step_Substituted_Molecule.md`: check 1 on a
second field of benzonitrile (part A, with this caveat), and the error against the label (part B).
