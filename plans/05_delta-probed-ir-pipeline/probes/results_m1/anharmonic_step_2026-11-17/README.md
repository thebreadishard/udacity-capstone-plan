# The anharmonic step with the set-wise match — record of 17 Nov 2026 (TASKS 255)

- `acceptance.md`, `acceptance.json` — `probes/anharmonic_step_accept.py` on format 3 of the artefact (`probes/anharmonic_step/x2star_v3.json`).
- `table_diff.py`, `.txt`, `.json` — every stored mode under the one-to-one and the set-wise match; format 2's table against format 3's.
- `replay_runs.py`, `.txt`, `.json` — the two real runs (benzene, benzonitrile) through the step's functions again, from their saved files.
- `first_run_checks.py` — the second version of a real run's four checks. Its tolerance on a step (0.3 × the family's bar, 2 cm⁻¹ at
  most, plus 0.1 for the record's rounding) was set on 17 Nov 2026 after the first run's 1.7 cm⁻¹ on a C–H stretch pair, knowing that
  number. The 1.7 is scatter between two GFN2-xTB force fields of the same molecule, an error the family's bar does not contain; it was
  measured once, on benzene.
- Certificates print the registered bars (3.37 / 3.84 / 8.38 / 6.21). Format 3's own bars are in its header (`bars.own_cm`) and in
  `acceptance.md`, and are not printed until a dated amendment of the registration.
