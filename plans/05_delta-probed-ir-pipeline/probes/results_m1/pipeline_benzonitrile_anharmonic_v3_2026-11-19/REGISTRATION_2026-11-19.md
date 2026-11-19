# Benzonitrile through pipeline 0.14 with the anharmonic step on format 3 — registered 19 Nov 2026, 20:0x, before launch (TASKS 211 step 2)

Written before `probes/runspecs/benzonitrile_anharm_v3_2026-11-19.json` was launched. Nothing of this run had been seen.

## The molecule and why
TASKS 211 step (2): the four checks again on one substituted molecule outside the table x2* was fitted on. **Benzonitrile**
(`N#Cc1ccccc1`, C7H5N, 13 atoms, C2v):
- outside the table: not among the 37 `training_molecules` of `probes/anharmonic_step/x2star_v3.json` (the table has
  2-naphthonitrile B_a41f4cff9d and oxazole-4-carbonitrile B_052693bd01, not benzonitrile); the run of 17 Nov recorded it as
  `"seen": {"role": "unseen"}`;
- substituted, with a group of a kind the hydrocarbon targets do not have (a linear C≡N; N is in the table's elements);
- small (13 atoms), and in the corpus: the run of 17 Nov (`../pipeline_benzonitrile_anharmonic_second_run`) reused steps 2–3
  with `--reuse-only`, so this run computes only the GFN2-xTB force field and its label (656 s, 1007 MB peak on 17 Nov);
- the one molecule that already has a pipeline record of the step, so the run reads against a known count: the offline replay of
  17 Nov's saved files on format 3 (`../anharmonic_step_2026-11-17/replay_runs.txt`) gives 27 of 33 bands stepped, 6 'unmeasured'.

## No stored force field: the four checks cannot all be read
`first_run_checks.py --reference` needs a same-network reference built from a force field that is independent of the run's (for
benzene: S2's stored field, from S1's pyscf minimum). No such field exists for any substituted molecule outside the table. Every
stored GFN2-xTB quartic force field on disk belongs to the table (S2: 14 in `s2_xtb_2026-10-18/xtb`, S2b: 23 in
`s2b_xtb_2026-11-02/xtb`; together the 37 training molecules) or to the two targets (coronene, tetracene in
`routea_2026-11-02/xtb`: unsubstituted). The styrene force field (`qff_noise_styrene_2026-10-15`) is pyscf B3LYP/6-31G*, not
GFN2-xTB. The only other GFN2-xTB field of benzonitrile is the pipeline's own of 17 Nov, computed by the same code from the same
corpus geometry: a reference from it would test reproducibility, not the scatter between two fields that check 1's line is for,
so it is not used as the checks' reference.

## What is read, and the pass criteria
The four checks' definitions and tolerances stay those of `../anharmonic_step_2026-11-17/first_run_checks.py` (check 1: 0.3 × the
family's bar, 2 cm⁻¹ at most, plus 0.1; check 3: pairs within PAIR_TOL_CM carry equal steps). On this run:
1. **Steps within tolerance**: not read (no independent reference).
2. **No band lost**: read against the replay's count. Pass: 27 of 33 bands stepped, every band without a step 'unmeasured'
   (no 'no-xtb-partner', no other reason). Fewer stepped bands, or a new reason, is a fail to explain.
3. **Degenerate pairs equal**: C2v has no degenerate irreducible representation; read reference-free on the run (any two bands
   within PAIR_TOL_CM carry equal steps). Expected vacuous.
4. **Time and memory recorded**: pass when the record holds the force field's seconds and peak memory; recorded beside 17 Nov's
   656 s / 1007 MB.
Informational, not a pass criterion: the run's Δ_anh per band beside 17 Nov's (that run ran ΔH network v1.3 and format 2, so
harmonic positions differ and bands are paired by position only where they lie within 1 cm⁻¹).
