# Benzene through pipeline 0.14 with the anharmonic step on format 3 — 19 Nov 2026 (TASKS 255, 211)

Run spec `probes/runspecs/benzene_anharm_v3_2026-11-19.json`, launched 19:29:47 through `tools/runspec.py`, exit 0. ΔH networks:
v1.4's release networks. Artefact: `probes/anharmonic_step/x2star_v3.json`. The GFN2-xTB force field and its label took 998.8 s
in the systemd scope `m08-anharmonic-benzene-adbc4c365b.scope`, with a peak of 982 MB (page cache included). 28 of 30 bands stepped.

## Why the default reference refused
Against its default reference (`../anharmonic_step_2026-11-16/stored_field_demo/benzene`), `first_run_checks.py` refused because
the harmonic positions were up to 2.30 cm-1 apart. That reference was built on the pipeline result of 3 Nov, which ran ΔH network
v1.3 (its record: `"version": "1.3"`), with artefact format 2. This run used v1.4's release networks, so the corrected harmonic
positions are not the same. The force field is not the cause (`compare_references.py`).

## The reference rebuilt
`../anharmonic_reference_v14release_v3_2026-11-19/build_reference.py` runs `stored_field_demo.py` unchanged except for one thing:
its base is a copy of this run's own steps 1–5 files. The rebuilt reference has v1.4 release, format 3, S2's stored force field
rotated onto this geometry (0.030 bohr rms), and 28 of 30 bands stepped. Run and reference now differ only in the force field. Their
harmonic positions agree to 0.00 cm-1. The checks' tolerances are unchanged.

## The four checks
`python ../anharmonic_step_2026-11-17/first_run_checks.py benzene --reference ../anharmonic_reference_v14release_v3_2026-11-19/benzene`
gives exit 0, recorded in `first_run_checks_2026-11-19.json`:

1. Steps within tolerance: **pass**. The band closest to its line is the CH-stretch pair at 3240.8, which differs by 1.7 cm-1
   against a tolerance of 1.96 (0.87 of it). No band is beyond its tolerance.
2. No band lost: **pass**. 28 of 30 bands stepped in the run, 28 of 30 in the reference.
3. Degenerate pairs equal: **pass**. All 5 pairs are equal. The pair at 1689.0 (1691 on v1.3) is stepped in both run and
   reference, with Δ −38.6. The first run of 17 Nov lost this pair to 'no-xtb-partner'.
4. Time and memory recorded: **pass**. 998.8 s, 982 MB.

## Caveats
- Check 1's tolerance (0.3 × the family's bar, 2 cm-1 at most, plus 0.1) was set on 17 Nov, after the first run and knowing its
  1.7 cm-1. This run is the first test of that line. It gives the same 1.7 cm-1 on the same CH-stretch pair at 0.87 of the line,
  which is close to it.
- The reference was rebuilt after the run, on the run's own steps 1–5. The rule it follows (same base, stored field) is the
  original demo's, not something chosen on this run's numbers.
- This is one molecule, a symmetric hydrocarbon.
