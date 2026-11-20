# The anharmonic step on a substituted molecule — registered before either force field is computed

**Written 20 November 2026, before any run of this note is launched.** TASKS 211. Nothing of either run has been seen. The two
run specs are validated and dry-run, not started. Paths are relative to `plans/05_delta-probed-ir-pipeline`.

*Revised the same day, after the independent review of the branch and still before any run: the rule of section 4 has
three outcomes with a line fixed from n, section 5 has the unsubstituted baseline, and section 7 two corrected figures.*

## 1. The question

The pipeline's optional step 6 prints ν = ω + Δ_anh per band, Δ_anh from a GFN2-xTB quartic force field and the model x2* of
`probes/anharmonic_step/x2star_v3.json`. Each stepped band carries its family's error bar: ring-ip 3.37, 'other' 3.84, CH-oop
8.38, CH-stretch 6.21 cm⁻¹ (`GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md`, amendment 1). The bars
are the rms of step − B3LYP GVPT2 label over the target modes of coronene and tetracene, two unsubstituted hydrocarbons, and
that note says so: "Nothing here says the anharmonic step helps a molecule unlike the two targets" (its line 49).

**How large is the step's error against its own label on a substituted molecule that x2* was not fitted on, and does each
family's printed bar cover it?** Nobody has measured that. This note registers the measurement on benzonitrile, and beside it
the one check of the step's first run that could not be read on benzonitrile.

## 2. What is known, and from where

1. **Check 1 is a reproducibility check, not an accuracy check.** `probes/results_m1/anharmonic_step_2026-11-17/first_run_checks.py`
   compares, band by band, the Δ_anh of a run with the Δ_anh of a reference that is the same pipeline result with another
   GFN2-xTB force field of the same molecule (its lines 12-14, 89-108). The tolerance is 0.3 × the family's bar, 2 cm⁻¹ at
   most, plus 0.1 (lines 49-51, 80-86): ring-ip 1.11, 'other' 1.25, CH-oop 2.10, CH-stretch 1.96 cm⁻¹. Its own text names what it bounds: "scatter between two
   GFN2-xTB force fields of the same molecule" (lines 21-22). A pass says two fields of one molecule give the same steps. It
   says nothing about whether those steps are right.
2. **The result note of 19 November words it otherwise.** `probes/results_m1/pipeline_benzonitrile_anharmonic_v3_2026-11-19/RESULT.md`
   ends: "What this does not show: that the step is right for a substituted molecule — that needs an independent field (check
   1)". An independent field cannot show that. A dated note appended to that file corrects the sentence (records append).
3. **The benzonitrile run exists.** Pipeline 0.14, v1.4 release networks, format 3:
   `probes/results_m1/pipeline_benzonitrile_anharmonic_v3_2026-11-19/benzonitrile/pipeline.json`. 27 of 33 bands stepped; 6
   'unmeasured' (167.5, 189.7, 410.9, 422.0, 467.9 and the C≡N stretch at 2386.3 cm⁻¹). Stepped bands per family: ring-ip 12,
   CH-oop 6, CH-stretch 5, 'other' 4 — of which one (582.4 cm⁻¹) is stepped without the bar's claim (`error_not_measured`:
   family 'other' with an out-of-plane share of 0.8 or more, `probes/anharmonic_step.py:60-61`), so **3 'other' bands carry
   the bar**. Benzonitrile is not among the 37 `training_molecules` of the artefact; the record says `"seen": {"role": "unseen"}`.
4. **The stored B3LYP minima of benzonitrile are nearly one geometry.** The run's is corpus B_3100da3761's. Corpus
   A_3100da3761 lies 0.00057 bohr rms from it after rotation, aromir's of 16 November 0.00037
   (`probes/results_m1/anharmonic_step_substituted_2026-11-20/second_minimum/G/start.json`, written by
   `probes/anharmonic_second_field.py start`). The GFN2-xTB field starts with xtb's own optimisation from whichever is given.
5. **Prior information: the substituted molecules inside the training table.** Section 5 and
   `probes/results_m1/anharmonic_step_substituted_2026-11-20/prior/PRIOR.md`.
6. **The label route.** x2* is trained against B3LYP/6-31G* GVPT2 labels at grid 75,302, each at its own pyscf minimum, ±0.10
   along every mode ("the G route": `probes/s2_batch.sh` → `probes/s1_anharmonic_level.sh`, then `probes/gvpt2_labels.py`),
   computed on servers in the env `qc05` with pyscf 2.14.0 (`probes/bootstrap_s1_cpx62.sh:5`). The laptop's `qc05` holds
   pyscf 2.14.0 too (the dry run of 20 November prints it).

## 3. Part A — check 1 on benzonitrile (formal, cheap)

**What is computed.** A second GFN2-xTB quartic force field of benzonitrile with its GVPT2 label, by
`probes/xtb_field_for_step.sh` — the script the pipeline's step 6 runs — under `probes/wsl_capped.sh 1536`, started from corpus
A_3100da3761's minimum (the stored minimum farthest from the run's, item 4) instead of the run's own. Run spec
`probes/runspecs/benzonitrile_xtb_second_field_2026-11-20.json`. No library call is new: every call is one
`probes/runspecs/s2_xtb.json` and the pipeline runs of 17 and 19 November already make. The spec's dry run leaves two small files in the out folder
(section 7); the real run writes them again.

**The reference.** `probes/anharmonic_second_field.py reference` builds it as the benzene reference of 19 November was built: a
copy of the run's steps 1-5 files, the pipeline's own step 6 on them, the force field being the stored second one with its
modes rotated onto the run's frame. Run and reference differ in the force field only. On benzene's inputs the tool gives the
19 November reference band for band (`tests/test_anharmonic_second_field.py`, the last test).

**The read.** The unchanged `first_run_checks.py`, with its tolerances as they are:

    python probes/results_m1/anharmonic_step_2026-11-17/first_run_checks.py <run> --reference <reference>/benzonitrile --out <a file outside the run folder>

- **Check 1 passes** when no band lies beyond its tolerance (`bands_beyond` empty); the record names the band closest to its
  line. **It fails** otherwise, and the failing bands are named.
- Check 2 is read as on 19 November: 27 of 33 stepped, every band without a step 'unmeasured'.
- **Check 3 will print FAIL and that is not a finding.** The script passes check 3 only when it finds at least one degenerate
  pair (its line 121), and C2v benzonitrile has none. On 19 November it was registered and read as not applicable; it is
  again. The script's last line will therefore say "NOT PASSED: the default stays 0" whatever check 1 gives. The read of part
  A is check 1's own line.
- Check 4 is the run's and was passed on 19 November (1830.9 s, 1003 MB).

**What a pass means, in plain words.** Two GFN2-xTB fields of benzonitrile, from two starting geometries 0.0006 bohr apart that
xtb re-optimises, give the same steps within the line. I expect a pass, close to zero: the two same-geometry runs of 17 and 19
November agree to 0.1 cm⁻¹ on all 27 steps. **A pass does not show that the step is right for a substituted molecule**, and
is not counted as evidence for it. It closes the formal condition of TASKS 211's row — check 1 read on a substituted
molecule before its step (3) — and nothing more. A fail would be a real finding — a step that moves by more than the line when the start moves by 0.0006
bohr — and would stop the default on its own.

## 4. Part B — the step against its label (the question of section 1)

**What is computed.** The G route on benzonitrile: `probes/g_label_for_step.sh` runs `probes/s1_anharmonic_level.sh <corpus
B_3100da3761 geometry> <out> 4 G:6-31g*:75,302` and then `probes/gvpt2_labels.py --setting G`, in WSL env `qc05` under
`probes/wsl_capped.sh 4096`. 13 atoms, 33 modes, 67 Hessians. Run spec `probes/runspecs/benzonitrile_g_label_2026-11-20.json`.
The two scripts are called as `probes/s2_batch.sh` called the first for every training molecule and as
`probes/xtb_field_for_step.sh` calls the second; no library call is new. One setting is: `PYSCF_MAX_MEMORY` at half the cap,
the environment variable `pyscf/__config__.py` reads for `MAX_MEMORY` (line 12 in the installed 2.14.0). It sizes pyscf's
blocks and changes no number; `probes/low_mode_patch.sh` sets the same half through `--max-memory`.

**The read.** `probes/anharmonic_step_label_read.py read --run <the 19 November result> --g-dir <out>/g/benzonitrile/G --label
<out>/gvpt2_g/benzonitrile.json --out <folder>`:

1. The label's geometry is rotated onto the run's (Kabsch). The label is refused when its atoms or their order differ, when
   the distance left exceeds 0.05 bohr, when it has another number of modes than the run has bands, when it predates the
   VPT2-domain check, or when it names symmetry pairs (benzonitrile has none; the bars count a pair once and this read does
   not collapse pairs).
2. Each of the run's 33 bands (the modes of H_B3LYP + ΔH, as step 6 formed them) is matched to the label's modes by
   `s2_xtb_read.match_sets` — the match the step and its training table use, same lines (0.5 one-to-one, 0.8 for a
   near-degenerate set). The band takes its partner's label shift Δ_label = ν_GVPT2 − ω.
3. Per band: error = Δ_step − Δ_label, with Δ_step the printed step of the record (rounded to 0.1 cm⁻¹, so each error carries
   up to 0.05 of rounding).
4. Per family: n and the rms of the errors over the bands **printed with a step and the family's bar** whose label mode is
   inside VPT2's domain. The rms is computed by `s3_read.family_read`, the function that computed the bars. On the stored
   rows of coronene and tetracene the read's function returns their registered numbers: ring-ip 4.25 / 2.35, 'other' 5.69 /
   1.09, CH-oop 11.91 / 4.55, CH-stretch 6.94 / 5.68, and pooled the four bars 3.37, 3.84, 8.38, 6.21
   (`tests/test_anharmonic_step_label_read.py`; the CH-stretch pair is `route_rule_ch.md`'s. Amendment 1 of the printed-position
   note also quotes 6.92 / 5.67, the format-3 refit of 17 November, whose rows are not stored).
5. Listed and outside the rms: a band without a step, with what the label says for it (that is what printing it harmonic
   costs); a band stepped without the bar's claim (582.4 cm⁻¹); a band whose label mode is outside VPT2's domain; a band no
   label mode matches. A second column gives n and rms over every stepped band the label covers, for information.
6. A band whose printed family differs from its label mode's family is listed in RESULT.md. It is read against the printed
   family's bar, since that is the bar the certificate prints on it.

**What differs from how the bars were measured, said once.** The bars were read in the label's own modes, with the model's
inputs attached to them. This read is in the pipeline's bands — the corrected modes, with the step carried to them as step 6
carries it — because that is what a user is given. A band's family is the one the pipeline printed. So this number contains
the carrying from B3LYP modes to bands, which the bars do not; that is the quantity whose bar is printed on the certificate.

**The registered rule.** Per family with at least **4** bands in the rms, three outcomes. The line is fixed now, from n alone:

- **within the bar**: rms ≤ the printed bar (the rms rounded to 0.01 cm⁻¹, as the bars are);
- **consistent with the bar at this n**: bar < rms ≤ the one-sided 95 % line for that n;
- **beyond the bar**: rms above that line — evidence that the bar understates the step's error on this molecule;
- with fewer than 4 bands the rms is reported and no statement is made.

**The line.** If a family's bar is exactly right and its n errors are independent and Gaussian with the bar as their standard
deviation, then n·rms²/bar² is chi-square distributed with n degrees of freedom, and the rms stays under bar × √(χ²₀.₉₅(n)/n)
in 95 runs of 100. `anharmonic_step_label_read.line_factor` computes that from the n the read finds
(`scipy.stats.chi2.ppf`; pinned in the tests on the tabulated quantiles). For the expected counts:

| family | n expected | bar | factor | line (cm⁻¹) |
|---|---|---|---|---|
| ring-ip | 12 | 3.37 | 1.32 | 4.46 |
| CH-oop | 6 | 8.38 | 1.45 | 12.14 |
| CH-stretch | 5 | 6.21 | 1.49 | 9.24 |
| other | 3 (4 would give 1.54, 5.91) | 3.84 | — | no statement |

**Why not "rms ≤ bar" alone.** An rms of a handful of errors lies above its own true value nearly half the time. With
independent Gaussian errors of exactly the bar's size, the rms exceeds the bar with probability 0.45, 0.42 and 0.42 at n = 12,
6 and 5, and at least one of three families does in 0.81 of runs (1 − 0.55 × 0.58 × 0.58). A two-way rule would have said
"exceeds" four times in five with every bar right. The stored read agrees: 22 of the 31 unsubstituted molecules of section 5
lie above the CH-stretch bar. Being above the bar is therefore not evidence about substitution, and is not read as such.

**The chance rates of the rule as registered, said plainly.** With a 5 % line in each of three families, about 14 % of runs
(1 − 0.95³) show one "beyond" when every bar is right. The errors of one molecule's bands are not independent — neighbouring
modes share the force field's errors — so the effective number of errors is below n and the true line is wider than the one
used: the rule is approximate and, if anything, too eager to say "beyond". And one molecule cannot establish a bar, in either
direction: "within" on benzonitrile does not show the bars hold for substituted molecules, and "beyond" does not give the new
bar.

**The floor of 4 bands.** It was chosen knowing the counts (12 / 6 / 5 / 3), and the read that made the bars uses 6
(`s3_read.MIN_MODES`). At 6, CH-stretch — the family the prior of section 5 points at — would get no statement from this
molecule. 4 is kept, and the smaller n is paid for by the wider line (1.54 × at n = 4 against 1.32 × at 12), not by a looser
reading. From the run's record the counts will be ring-ip 12, CH-oop 6, CH-stretch 5 and 'other' 3, unless the label marks a
mode or a band finds no partner. **So 'other' is expected to get no statement from this molecule.** Its fourth stepped band
is the one the certificate prints without the bar's claim, and a bar is not tested on a band it is not printed for.

**What follows.**

- **No family beyond its bar:** TASKS 211's step (3), the default of 120 minutes, may go to a reviewed change. The
  certificate's wording does not change. The numbers are recorded as one substituted data point beside the bars. 'other'
  stays as unmeasured on substituted molecules as it is today, and the record says so.
- **Any family beyond its bar:** the default does not change by this run. The certificate's sentence about what the bars
  rest on gains the measured number for a substituted molecule. The question "do the bars need a substituted target" goes
  to the author with that number: a new target is label compute, and that is the author's decision.
- **No family reaches 4 bands** (only if the label loses bands): no statement, the default does not change.

**What this is not.** One molecule, 3 to 12 bands a family: one data point on substituted molecules, not a new bar and not an
interval. **No bar is changed by this registration or by its read.** A bar changes only by a dated amendment of
`PreRegistration_2026-11-14_Printed_Band_Position.md` (its section 5). The label is B3LYP/6-31G* GVPT2: the read measures the
step against what it was trained to reproduce, not against experiment.

**If the G field is NOISY.** `dpir.qff` refuses a force field whose two finite-difference routes for the quartic constants
disagree by more than 10 cm⁻¹; the runner marks it `NOISY`, which is how S2 set five molecules aside (`probes/s2_read.py:134-135`).
The run then ends with `=== (GLB) NOISY`, writes no label, and the read script records "not read" with that reason (exit 3).
Part B is then not read. Nothing is concluded from the noisy field's numbers, and the default does not change.

## 5. Descriptive, from records on disk: the seven substituted training molecules

No run. `probes/anharmonic_step_label_read.py prior` reads
`probes/results_m1/anharmonic_design_questions_2026-11-16/modes.json` (`per_molecule`, `rms_inputs_on_B`): x2* fitted with the
molecule's scaffold left out, against the molecule's own B3LYP GVPT2 label; rms in cm⁻¹ (modes). Bold: above the printed bar
with at least 4 modes.

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

Above the bar, of the molecules with enough modes: CH-oop 1 of 3, 'other' 2 of 6, ring-ip 5 of 7, CH-stretch 4 of 6. Six of
the seven are above a bar in at least one family.

**The same read's unsubstituted molecules, as the baseline.** `modes.json` holds 38 molecules: the artefact's 37 training
molecules and coronene, a target, which that read fitted on all training molecules (tetracene is in its `skipped`: no corpus
row). Without the seven above that leaves 31: 30 bare ring systems with their scaffold left out, and coronene. Molecules with
at least 4 modes in the family; "beyond" is the 95 % line of section 4 at the molecule's own n; pooled is the rms over every
mode of the group (`prior/PRIOR.md`, `prior.json` `groups`):

| family | bar | substituted: above / beyond / of | median rms | pooled | unsubstituted: above / beyond / of | median rms | pooled |
|---|---|---|---|---|---|---|---|
| CH-oop | 8.38 | 1 / 0 / 3 | 4.92 | 6.47 | 3 / 1 / 28 | 3.96 | 5.79 |
| other | 3.84 | 2 / 2 / 6 | 2.62 | 4.54 | 4 / 3 / 30 | 1.53 | 3.12 |
| ring-ip | 3.37 | 5 / 3 / 7 | 3.58 | 3.95 | 6 / 1 / 31 | 2.76 | 2.96 |
| CH-stretch | 6.21 | 4 / 4 / 6 | 10.55 | 11.22 | 22 / 7 / 31 | 7.27 | 8.52 |

How to read it.

- **Against the bar, only ring-ip shows a contrast**: 5 of 7 substituted molecules above it, 6 of 31 unsubstituted.
- **CH-stretch sits above its printed bar for unsubstituted molecules too**: 22 of 31, median 7.27, pooled 8.52 against 6.21.
  The bar was measured on two molecules and the scaffold-left-out read of the training table is larger. So a CH-stretch rms
  above the bar on benzonitrile would say something about the bar, not about the substituent.
- Against the line the substituted molecules stand out more (ring-ip 3 of 7 against 1 of 31, CH-stretch 4 of 6 against 7 of
  31, 'other' 2 of 6 against 3 of 30), but the six CH-stretch and 'other' cases come from five molecules with an NH₂, CH₃ or
  ≡C–H group, which benzonitrile does not have. With seven molecules this is a pointer, not a finding.
- These are not the registered measurement: the rows are in the label's modes, with the one-to-one match of 16 November
  (before format 3), and four of the seven carry an NH₂ or ≡C–H group, whose large-amplitude modes that read leaves out.

**The expectation, written down so that the read cannot be bent toward it afterwards.** Ring-ip above its bar (3.37) and
probably under its line (4.46): the substituted median is 3.58, and the closest relative in the table, naphthalene+CN, is at
2.20. CH-stretch above its bar is the base rate (22 of 31), so I expect it and would read nothing into it unless it passes
9.24. I expect no family beyond.

## 6. What is not decided here

- Whether the default becomes 120 minutes. This note only says which outcome lets that go to review.
- Whether the bars get a substituted target, and which. That is label compute and the author's decision.
- The time question of TASKS 211 (the force field beside a training run exceeds the demo's half hour). Not touched.
- Anything about `m08/` or `m05/`. No code of either changes for this measurement; the default stays 0.

## 7. Cost, order and where it runs

Through `tools/runspec.py launch`. The laptop budget is 13 GB (`tools/runspec.py:74`); the training search holds 7.7
(`probes/runspecs/v14_stage1.json`) and the DFT measurement of TASKS 218 4.0 until it ends.

| run | threads | cap | estimate | basis |
|---|---|---|---|---|
| part A, second xtb field | 2 × 2 | 1536 MB | 0.2–0.5 h (the spec states 0.6) | the same field: 656 s alone (17 Nov), 1,831 s beside the search (19 Nov); peak 1,007 / 1,003 MB |
| part B, G label | 4 | 4096 MB | 3.4–14.5 h (the spec states 14.5) | 67 Hessians at 180–260 s on a server, times 1–3 on the laptop; see below |

- **Part B's seconds per Hessian.** Phenylacetylene (14 atoms) measured 225–260 s over its 72 displaced Hessians, median 240,
  at 5 server threads (`s2_anharmonic_2026-10-18/s2/A_a848c04a21.log`). S2's fit, exp(−4.92)·n^3.89
  (`PreRegistration_2026-10-19_S2b_Learning_Curve.md:37`), gives 157 s at 13 atoms; phenylacetylene's median scaled by the
  fit's exponent gives 180 s. The range is 180–260 s, so 3.4–4.8 h on a server. The laptop at 4 threads beside the search is
  **assumed** 1–3 times that, not measured (the GFN2-xTB field of this molecule took 2.8 times longer beside the search).
- **Part B's memory.** The cap is a bound, not a measured peak of this setting. The nearest laptop peak: the whole product
  pipeline on benzonitrile, max RSS 2,440,324 kB over 1,435 s (`probes/results_m1/aromir_e2e_benzonitrile.log:5`) — the
  same molecule and basis, another program path. The corpus job peaked at 1.71 and 1.9 GB (psi4;
  `corpus/molecules/{B,A}_3100da3761/result.json`). A kill at the cap prints `KILLED`, and the run resumes (it skips the
  minimum and every Hessian that exists).
- The first displaced Hessian prices part B: past 1800 s the runner stops (`MAX_FIRST`, the value of `probes/s2_batch.sh`).
- **Part B may run on a rented server instead of the laptop.** The author offered one for a night. The registered run is the
  call, not the place: `probes/s1_anharmonic_level.sh <corpus B_3100da3761 geometry> <out> <threads> G:6-31g*:75,302` in an
  env `qc05` with pyscf 2.14.0 (the servers' labels recipe, `tools/bootstrap_qc05_env.sh`), then `probes/gvpt2_labels.py
  --setting G` with the polyad fork. Either place is this registration's run. The record states where it ran, the threads
  and the wall time; no server spec is written here.
- Order on the laptop: part A first (it fits beside the search once TASKS 218's run has ended: 7.7 + 1.5 = 9.2 GB), then
  part B (7.7 + 4.0 = 11.7 GB). Not both at once (13.2 GB), and neither while TASKS 218's run holds its 4.0 GB.
- Both specs were started in dry-run form the way the run door starts them (`bash -c "cd <workdir> && <command> --dry-run"`
  from the plan folder with a Windows-form PWD) on 20 November: exit 0, tools found (xtb 6.7.1; pyscf 2.14.0; pyvpt2's
  fermi_solver). The wrapper finds its plan folder physically (`probes/plan_paths.sh`), so the `/mntC:/…` path that stopped
  `probes/low_mode_patch.sh`'s dry run this morning cannot occur (`tests/test_anharmonic_substituted_wrapper.py`).
- **Part A's dry run leaves two files** in its out folder, `second_field/ids.tsv` and `selection.json`:
  `probes/xtb_field_for_step.sh` writes them before its dry-run branch (its lines 24-27). That is the pipeline's script and
  is not changed here. The real run writes both again, each through a temp file, with the same content, and skips nothing
  for their being there (the runner skips a molecule only where `X/qff_report.npz` exists), so the leftovers do not confuse it.

## 8. The read script on synthetic records, before this note is committed

`tests/test_anharmonic_step_label_read.py`, 20 November: the line by n on the tabulated chi-square quantiles; every outcome
(within, consistent, beyond, no statement) and both boundaries of every family at its expected count (at the bar, one
hundredth above it, at the line, one hundredth above the line); a family with fewer than 4 bands; a band without a step; a
band stepped without the bar's claim; a band printed in another family than its label mode's; a label mode outside VPT2's
domain; a label at another geometry, in another atom order, with another number of modes, with symmetry pairs, without the
domain check (each refused); a NOISY field (not read, exit 3); a record never written twice; and the bars' arithmetic on
coronene's and tetracene's stored rows. On the real path, without a label: the run of 19 November read against its own B3LYP
modes gives 33 bands with a partner, no family mismatch, and the counts 12 / 6 / 5 / 3.
