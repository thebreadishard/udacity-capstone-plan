# The anharmonic step, stage 1 — acceptance (2026-11-17 09:44, TASKS 211)

Artefact `probes/anharmonic_step/x2star_v3.json` (written at commit 46c7ba6d); every molecule through `anharmonic_step.mode_steps` alone; this record by `probes/anharmonic_step_accept.py` at commit 46c7ba6d (uncommitted changes: yes).

**PASSED**

## 1. The route-A targets against the artefact's bars (cm⁻¹)

Pass: the step's rms within 0.01 of the artefact's own bar, within 0.05 of the registered bar, on the registered rows. The registered bar was read with one xtb mode per mode; the artefact's table is matched set-wise (TASKS 255).

| family | rows | registered rows | rms of step − label | the artefact's bar | registered bar | registered match reproduced | from the registered | changed by the set-wise match | harmonic position | per molecule | |
|---|---|---|---|---|---|---|---|---|---|---|---|
| CH-oop | 22 | 22 | 8.3809 | 8.3809 | 8.38 | 8.3809 | +0.0009 | +0 rows | 12.48 | coronene 11.91, tetracene 4.55 | pass |
| other | 23 | 23 | 3.8387 | 3.8387 | 3.84 | 3.8387 | -0.0013 | +0 rows | 8.20 | coronene 5.69, tetracene 1.09 | pass |
| ring-ip | 56 | 56 | 3.3694 | 3.3694 | 3.37 | 3.3694 | -0.0006 | +0 rows | 26.23 | coronene 4.25, tetracene 2.35 | pass |
| CH-stretch | 20 | 20 | 6.1994 | 6.1994 | 6.21 | 6.2143 | -0.0106 | +1 rows | 134.24 | coronene 6.92, tetracene 5.67 | pass |

## 2. The modes only the B3LYP label marks

| mode | ω (cm⁻¹) | family | o | step (cm⁻¹) | bar | error not measured | the label's shift | |
|---|---|---|---|---|---|---|---|---|
| coronene mode 24 | 642.9 | other | 1.00 | -9.1 | None | yes | +66.2 | pass |
| coronene mode 36 | 807.1 | other | 1.00 | -11.6 | None | yes | +179.1 | pass |

## 3. The label-free rule over 39 molecules, 2244 modes

- modes a B3LYP label marks: 6; of those without a step under the rule: 4 (expected 4 of 6)
- modes no label marks that lose their step to an xtb partner's mark: 0 (expected 0)
- the marked modes the rule misses all carry the 'error not measured' flag: yes
- all modes by route: {'unmeasured': 384, 'step': 1749, 'no-xtb-partner': 71, 'large-amplitude': 40}; stepped modes with the flag: 120

| molecule | mode | ω | family | o | under the rule |
|---|---|---|---|---|---|
| B_0603418c5b | 11 | 564.5 | other | 1.00 | large-amplitude |
| B_410ac0fb2f | 8 | 518.1 | other | 1.00 | large-amplitude |
| B_410ac0fb2f | 11 | 593.7 | other | 0.84 | large-amplitude |
| B_78f8233b4c | 10 | 509.4 | other | 0.83 | large-amplitude |
| coronene | 24 | 642.9 | other | 1.00 | step, error not measured |
| coronene | 36 | 807.1 | other | 1.00 | step, error not measured |
- **pass**

## 4. Stated, not checked

- **The printed bars.** A certificate prints the registered bars (printed_cm), read with the one-to-one match. This table is matched set-wise and its own bars (own_cm) are not printed until a dated amendment of the registration (GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md) names them. Printed: {'CH-oop': 8.38, 'other': 3.84, 'ring-ip': 3.37, 'CH-stretch': 6.21}; this table's own: {'CH-oop': 8.3809, 'other': 3.8387, 'ring-ip': 3.3694, 'CH-stretch': 6.1994}.
- **A degenerate pair in another basis.** The match gives the pair one shift in every basis when its two GFN2-xTB labels are one number; where they differ the carried shift lies between them. Over 44 symmetry pairs of 2 molecules the two labels differ by 0.025 cm⁻¹ at most (coronene at 1007.0 cm⁻¹).

