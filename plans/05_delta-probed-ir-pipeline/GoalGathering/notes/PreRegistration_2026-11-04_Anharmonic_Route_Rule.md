# Pre-registration: which anharmonic shift the pipeline carries, per family (TASKS 178, steps 1 and 2; 4 Nov 2026)

**Status: REGISTERED 4 Nov 2026, 17:3x**, before S2b's read and before S3's read. S2b is still computing on `s2b1`–`s2b3`; no S2b label
has been read. Route A's tetracene was fetched at 17:1x. Of it, only the file list and the absence of a NOISY flag have been looked at:
no frequency, shift or report table was opened. Coronene is still computing. The read script `probes/anharmonic_route_rule.py` passed
its synthetic tests first (`tests/test_anharmonic_route_rule.py`, 11 cases). The user agreed the order on 4 Nov ('Akkoord met alles').

## Why

The pipeline reports harmonic band positions (`m08/pipeline.py`, HARMONIC_NOTE). TASKS 178's design is ν = ω(ΔH network) + Δ_anh(level
G), with the anharmonic shift as a model of its own, beside the ΔH network. Three candidate models exist per family:
- S2b's learned model;
- the family mean (c);
- none.

S2b and S3 decide between them. If the rule is written after their numbers, it follows the numbers, so it is fixed now.

## Inputs

- **S2b's read** (`probes/s2b_read.py`), main scope 'no-large-amplitude'. Per family it gives the verdict model, `best_curve_model`:
  the lowest leave-one-scaffold-out rms at 'all' among (c), (b), x1 and x2*.
- **S3's read** (`probes/s3_read.py`). Per family, pooled over tetracene and coronene, it gives:
  - every model's rms on the targets' window modes (550–2000 cm⁻¹), with a degenerate pair counted once;
  - the number of target modes.

TASKS 178 says the model must beat (c) "on the hold-outs and on route A's tetracene". For Δ_anh, the hold-outs are these two reads:
- S2b's leave-one-scaffold-out at 'all', which chooses the model;
- S3's targets, which check that model at 30–60 atoms.

No other hold-out has anharmonic labels at G. The ΔH hold-outs (a) and (b) carry none.

## Rule (`probes/anharmonic_route_rule.py`)

Per family:

1. **S3's line 1 holds for S2b's verdict model** (target rms ≤ 3.0 cm⁻¹ and below (c)'s on the same modes; `s3_read.transfer_holds`,
   the one implementation): the route is the verdict model. Its error bar is its target rms.
2. **Otherwise, if (c)'s target rms is ≤ 3.0 cm⁻¹**: the route is (c), the family mean over the training molecules. Its error bar is
   (c)'s target rms. This case includes S2b choosing (c) itself, and a verdict model that gives no prediction.
3. **Otherwise**, no anharmonic step. The family's bands keep their harmonic positions with the pipeline's HARMONIC_NOTE.
4. **A family S3 cannot judge** (fewer than 6 target modes, or no S2b verdict) gets no step, whatever its small-molecule numbers.

**Licence (TASKS 178, step 2).** A family's anharmonic step is licensed exactly when rule 1 or rule 2 chooses a route. The certificate
gives each band its family's error bar. The line, 3.0 cm⁻¹, is the same as line 2 of S2, S2b and S3 and as decision 65's licence for ΔH.

## Outside the rule, stated now

These classes get no anharmonic step from this rule:
- **Bands outside 550–2000 cm⁻¹.** S2, S2b and S3 read no mode there. Among them are the 3 µm C–H stretches, whose polyads the design note
  puts out of scope (`Design_2026-10-13_Spectral_Shape_Anharmonic_Step.md`, §4). They stay harmonic, with the note.
- **Large-amplitude classes outside S2b's main scope** (methyl and other rotors, linear X–H bends, the NH₂ wag; TASKS 156 and 176). Step
  3 of TASKS 178 marks them per band.
- **Combination bands, overtones and hot bands** (TASKS 179).

If coronene does not finish, S3 reads tetracene alone, and this rule reads whatever S3 reads. Rule 4's six modes still apply.

A different rule after the numbers would be a new, dated registration with its reason. It does not replace this one for the reads it was
written for.

## Predictions (before any number)

| prediction | odds |
|---|---|
| at least one family gets a learned route (rule 1) | one in four, S3's own odds for its line 1 |
| at least one family gets no step (rule 3 or 4) | two in three |
