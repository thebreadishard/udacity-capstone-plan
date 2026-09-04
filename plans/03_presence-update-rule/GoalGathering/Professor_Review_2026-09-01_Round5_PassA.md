# Professor review — 2026-09-01, Round 5, Pass A (cold read)

**Scope.** Internal consistency only, per [Review_Brief_2026-09-01_Round5_PassA.md](Review_Brief_2026-09-01_Round5_PassA.md).
No TDDFT, Maxwell or stencil physics is judged here; that is Pass B. Numbering is **Round 5, Pass A,
issues 1–15**, independent of plan 01's 1–15 and of the R3/R4 lists.

**Method note.** Three claims below were checked by executing the repository's own probes rather than
by reading them: `len(grid_spec.CHANNEL_ORDER)`, a 200-step run of `p0_fixed_point.py` on a synthetic
state, and the Courant ratio of `linear_stencil.py`. Commands and outputs are quoted in the findings.

---

Verdict: **Proceed to Pass B, but not as written.** The governance is real and the bibliography pass is
genuinely honest; however four frozen objects say something different from what they are (the channel
count, the P0 baseline, the workspace contents, and the Module 03/05 dataset eligibility), and two of
those change the premise of Pass B attack 5. Pass B must be handed findings 2–4 with this file.

**Disposition, 2026-09-01 (same day).** All fifteen findings were addressed; the per-finding Status lines
below say how. Two were closed by *measurement* rather than by editing prose (3 and 4). Five were closed
by correcting a frozen constant or a citation (2, 7, 8, 9, 12). Two are closed *in spec only* and remain
open as work (5, 6): Module 03 and Module 05 Task A now have no pinned dataset at all, which is the honest
state, and pinning them is a blocking precondition of those modules. The eight loopholes are closed in
[Distilled §4](Distilled_Project_Plan_and_Quality_Checks.md) and the Round-5 block of
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md). Nothing here became a result.

---

## Blocking findings

### 1. Plan 02 is still in the workspace, and it contains results

**Where:** [README.md](../../../README.md) ("Current plan", "Repository layout"), [plans/README.md](../../README.md)
(opening), [README.md](../README.md) (status), [Inheritance_of_Reviews.md](Inheritance_of_Reviews.md)
R4A-2, and both Round-5 briefs.

**What:** Five documents state the same thing —

> "Folders for plans 01 (voxel field PES) and 02 (coupled-cluster anharmonic IR) were **removed from the
> tree on 2026-09-01**. They remain in git history. They are not in this workspace."

and the Pass A brief instructs the reviewer: "Do not look for `plans/01_*` or `plans/02_*`: those folders
are gone." The folder `plans/02_coupled-cluster-anharmonic-ir/probes/` is in this workspace. It holds
`benzene_d6h.log`, `benzene_sym_good.log`, `symmetry_benzene.{json,log}`, `timer.dat`, `results_dft_locality/`,
and `batch_results/` with seven executed frequency results (`02_freq_phenanthrene.npz` … `07_freq_coronene.npz`)
plus eleven psi4 run logs. `git ls-files plans/02_coupled-cluster-anharmonic-ir plans/01_voxel-field-pes`
returns **0** lines and `git status --short` is clean, so the statement is true *about git* and false
*about the workspace*: the files are ignored, not deleted. The root README's layout diagram omits the
folder entirely.

This also collides with two absolute statements. Root README: "It contains no implementation and no
results." Pass A brief: "**Nothing has been executed.** There are no results." Seven `.npz` frequency
results and a `run.log` are results, produced by execution, sitting two directories from the plan under
review.

**Why it matters:** the one instruction the cold reader is given about the tree is wrong, and it is wrong
in the direction that hides prior results from a reviewer who was told none exist. A reader who greps the
workspace — as I did — finds plan 02 immediately and now distrusts every other status banner. Worse, the
sentence is repeated in five files, so it is *load-bearing* for the "draft, nothing executed" frame.

**Status:** closed 2026-09-01, by the *first* branch, after the disposition below was written. The
leftovers were deleted rather than described: `plans/02_coupled-cluster-anharmonic-ir/` no longer exists.
Before deleting, the ten raw `.npz` frequency arrays (361 KB, ~10 h of psi4, never committed because
`.gitignore` excluded them) were force-added in `800f3aa`, so “they remain in git history” is now true of
**everything** the sentence covers — which is what made the sentence safe to restore. The ~66 MB of psi4
logs and scratch were not preserved: reproducible noise, not results.

---

### 2. The frozen state has eleven channels, and four files call it twelve

**Where:** [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §5.1
("Twelve channels, same order everywhere"); [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §3
("State channels | 12: …"); [probes/cube_io.py](../probes/cube_io.py) (`"""Full 12-channel npz, or fail closed."""`);
[Review_Brief_2026-09-01_Round5_PassB.md](Review_Brief_2026-09-01_Round5_PassB.md) attack 1
("not a 12-channel neighbourhood").

**What:** every one of those sentences is immediately followed by the same enumeration,
\((\rho_+,\rho_-,j_x,j_y,j_z,E_x,E_y,E_z,B_x,B_y,B_z)\), which is \(2+3+3+3 = 11\). Measured:

```
> python -c "import grid_spec as g; print(len(g.CHANNEL_ORDER))"
11
```

**Why it matters:** this is not cosmetic. `CHANNEL_ORDER` is hashed into Q0 by
[probes/grid_hash.py](../probes/grid_hash.py). Whichever way the contradiction is resolved — the prose is
wrong, or a twelfth channel is missing from the frozen list — the resolution changes the Q0 digest. If it
is discovered after Q0 is hashed in Module 05 it becomes a Distilled §4 deviation on the *definition of the
state*, which is the least deviable object in the plan. It also means the single most-repeated technical
sentence in the plan set was never checked against the code that implements it, which is the exact failure
mode the brief's calibration warning names.

**Status:** closed 2026-09-01. Eleven everywhere: Distilled §5.1/§5.2, Compute Budget §3, `cube_io.py`,
the Pass B brief, `probes/README.md`. `grid_spec.N_CHANNELS` now exists so the count has one source. Fixed
before Q0 was hashed, so no §4 deviation was needed.

---

### 3. Q3 / P0 on the linear stencil cannot fail

**Where:** [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
§7.3 rung 4 and §8 claim-ladder rung 2; [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §7 rung 4;
[probes/p0_fixed_point.py](../probes/p0_fixed_point.py); [probes/linear_stencil.py](../probes/linear_stencil.py).

**What:** the plan treats "linear stencil P0 printed" as claim-ladder rung 2 and pre-registers the escalation
"P0 fails on the linear stencil → fix the teacher/grid, do not train." That branch is unreachable by
construction. `linear_stencil.step` updates \(\rho_-\) by \(-\Delta t\,\nabla\!\cdot\!\mathbf{j}\) using
`np.roll` central differences — a periodic permutation — so the grid sum of the divergence is exactly zero,
and \(\mathbf{j}\) is never updated ("j held (no constitutive update)"). Electron count is therefore conserved
to round-off for any input whatsoever. Measured, on a state of pure Gaussian noise:

```
> python p0_fixed_point.py _tmp_state.npz
steps 200
p0_rel 4.0921389191909416e-15
gate_h2 1.0000000000000000e-03
p0_pass_h2 1
```

Random numbers pass the H₂ fixed-point gate with twelve orders of magnitude of margin.

**Why it matters:** three governance objects rest on a measurement that carries no information — the rung-2
claim, escalation rung 4, and the Module 07 agent's `run_p0_probe` tool, whose declared safeguard is "if P0
fails, the agent may not emit a P2 claim." An agent wired to a gate that cannot fail is a demo of governance,
not governance. It also weakens P0 on the *learned* rule, since the plan offers no evidence that P0 is a
discriminating test in the first place.

**Status:** closed 2026-09-01, by measurement. `linear_stencil.py` is now non-periodic by default
(`grid_spec.PERIODIC_BOX = False`), matching the frozen finite box, so charge can leave through the rim.
The same noise state that used to pass now fails: `p0_rel 7.44e-1`, `p0_pass_h2 0`. Escalation rung 4 can
fire, and it no longer authorises an unnoted grid edit.

---

### 4. The frozen \(\Delta t\) and spacing put the frozen linear baseline 59× past its stability limit

**Where:** [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) "Time and grid (frozen)";
[Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §3;
[probes/linear_stencil.py](../probes/linear_stencil.py); [probes/grid_spec.py](../probes/grid_spec.py).

**What:** the freeze is \(h = 0.20\,a_0\), \(\Delta t = 0.05\) au, and the baseline is an explicit
central-difference Maxwell update with \(c = 137.036\) au. The Courant ratio is

\[
\frac{c\,\Delta t}{h} = \frac{137.036 \times 0.05}{0.20} = 34.26 ,
\]

against a 3-D explicit-stencil limit of \(1/\sqrt{3} \approx 0.577\). Measured over the P2 horizon:

```
courant c*dt/h = 34.25899979425   stability limit (3D) = 0.5773502691896258
step   5  max|E| = 6.5e+08
step  10  max|E| = 2.4e+17
step  20  max|E| = 7.7e+34
step  50  max|E| = 4.2e+87
step 200  max|E| = nan            sum rho*vol = 11.2863416263341 (unchanged)
```

The same 200 steps that define P2 take the field channels to NaN — and P0 still prints pass, because of
finding 3. Separately, §5.2 freezes padding as "periodic only if the teacher box is periodic; otherwise
zero / absorb to match the teacher rim", while the frozen box is "molecule + \(\ge 6\,a_0\) vacuum +
absorbing rim". The baseline is unconditionally periodic. Frozen spec and frozen implementation disagree
about boundaries.

**Why it matters:** P4 is the thesis comparison and P3's only pass condition is "beat the frozen linear
stencil." A baseline that diverges to NaN inside the scored horizon makes every P3/P4 "win" uninformative,
which is precisely the straw-man branch Pass B attack 5 was written to test — so Pass B must be told this
is now *measured*, not hypothetical. It also raises a question for Pass B that Pass A cannot answer: whether
\(\Delta t = 0.05\) au on a \(0.20\,a_0\) grid is a defensible *teacher* setting once Maxwell fields are
dynamical.

**Status:** closed 2026-09-01, by measurement. Maxwell is now leapfrogged (B uses the updated E) and
sub-cycled to \(\lceil 34.26/(0.5/\sqrt{3})\rceil = 119\) sub-steps per teacher step. Re-measured over the
same 200 steps: \(\max|E|\) = 6.9 / 63.6 / 254.7 at steps 5 / 50 / 200, all finite — growth driven by the
held constant current, not by instability. The teacher \(\Delta t\) and spacing are untouched; the
sub-cycling is a property of the baseline. Boundaries now match §5.2. **The teacher-side question is left
for Pass B on purpose.**

---

### 5. Module 03's frozen dataset is not from an accepted source, and the rubric matrix does not record the constraint

**Where:** [Capstone_Mapping.md](Capstone_Mapping.md) §1 row 03 and §3 "Module 03";
[Rubrics/03_Conduct_a_Statistical_Analysis_Using_Python.md](../../../Rubrics/03_Conduct_a_Statistical_Analysis_Using_Python.md)
Task 1.

**What:** the mapping's own rubric matrix records the accepted-sources trap for Module 04 only —
"**Kaggle / UCI / Data.gov / open-gov only.** … Accepted-sources list has no 'own data' carve-out" — while
Module 03's row says merely "Own dataset; must differ from 02". Rubric 1.5.1 for Module 03 carries the same
closed list:

> Accepted Sources: Kaggle Datasets · UCI Machine Learning Repository · Data.gov · FiveThirtyEight Data ·
> Open government data portals

The frozen Module 03 dataset is a flatten of **HZDR RODARE record 3995**, and the pre-declared fallback is
**QM7-X**. Neither is Kaggle, UCI, Data.gov, FiveThirtyEight, nor an open-government portal. Module 02's
rubric, by contrast, genuinely has no such list ("use your own dataset as long as it meets the project
requirements"), so the mapping's M02 choice is safe — the omission is specific to 03.

**Why it matters:** Module 03 is a graded submission with a frozen dataset intent, a pre-registered
hypothesis, and a declared fallback, all built on a source class the rubric may reject. Plan 01 issue 5 is
carried in [Inheritance_of_Reviews.md](Inheritance_of_Reviews.md) as "Rubric landmines … **Carried**", so
this is a carried finding that the carry did not actually catch.

**Status:** closed **in spec only**; the underlying work is now openly unfinished. The §1 matrix records
Module 03's closed list; RODARE and QM7-X are withdrawn as the graded CSV (RODARE keeps its role as
scientific context and prior art); the hypothesis is pre-registered in *form* and its variables are named
in the same dated note that pins an accepted-portal table. Module 03 now has **no** pinned dataset, which
is the honest state, and pinning one is blocking.

---

### 6. Module 05's pre-declared fallback depends on the thing that is marked FAIL

**Where:** [Capstone_Mapping.md](Capstone_Mapping.md) §3 Module 05 and §5.5;
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) item 10.

**What:** Module 05 is split into Task A (rubric shield, public voxel corpus) and Task B (the thesis stencil).
The pre-declared hard fallback is: "If a mentor treats self-run TDDFT cubes as 'synthetic,' Module 05 **ships
on Task A alone**." But the same section, dated the same day, says: "**2026-09-01:** item 10 is still unpinned
as a cube dump … **Do not write the Task A source sentence.**" The bibliography agrees: item 10 is
"**FAIL as a voxel dump**", and no substitute is permitted ("Do not substitute DeepDFT, Cuevas-Zuviría,
Rackers, or Shah/Cangi 1-D densities").

So Task A currently has no dataset, and the fallback for Task B failing is Task A. Module 06 is wired to the
same missing DOI ("Same DOI as 05 A + new split hash"), so a single unpinned identifier blocks two graded
modules and the plan's only rubric shield for the thesis.

**Why it matters:** the fallback is what makes the Task A/Task B split a risk control rather than a slogan.
As written, both branches terminate on the same missing object, and §5.5 forbids improvising ("Do not
improvise a third dataset"). This is the single most likely place the *rubric* side of the plan stops.

**Status:** closed **in spec only**. The fallback is now a three-rung ladder whose branches are
independent: A1 voxel DOI pinned; A2 a different public volumetric/image corpus pinned as a *new numbered
bibliography entry* (Module 05's rubric has no closed source list, unlike 03 and 04); A3 stop and report
the stop. Pinning A1 or A2 is a blocking precondition of Module 05, not a task inside it, and Module 06
inherits whichever branch fires. No identifier was invented to close this.

---

### 7. "Plan 01 spent ~560 h" is asserted as a measurement of a plan that was never executed

**Where:** [Overarching_Goal.md](Overarching_Goal.md) "Hours" table; [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md)
§5; [plans/README.md](../../README.md) "Why the earlier plans were dropped".

**What:** the 80 h grid+teacher cap is justified in two files by the sentence "Plan 01 spent ~560 h here.
That is forbidden," and in a third by "Roughly two thirds of plan 01's fixed 840-hour baseline was spent
making a voxel grid behave." The arithmetic is self-consistent (\(\tfrac{2}{3}\times 840 = 560\)), but
[plans/README.md](../../README.md) states two paragraphs earlier: "Neither 01, 02, nor 03 has been executed."
An unexecuted plan cannot have spent hours. At best this is a *planned allocation* in a deleted document;
past-tense "spent" makes it read as a retrospective measurement.

**Why it matters:** it is the only stated justification for the hardest cap in the plan, and the cap in turn
drives escalation rung 3 ("Human grid+teacher I/O exceeds 80 h → stop"). A cap derived from a number no one
measured is exactly the class of claim [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) was
written to eliminate ("No wall-clock in this file is a result"). The document polices Octopus timings and
then exempts its own justification.

**Status:** closed 2026-09-01. "Spent" → **"budgeted"** in all three files. The 80 h cap is unchanged; it is
now honestly described as a reaction to a plan-01 *allocation*, not to a measured overrun.

---

### 8. P3 is defined twice, and P0-on-water is a gate in one file and a report in another

**Where:** [Overarching_Goal.md](Overarching_Goal.md) "Promised Module 08 exit" items 4-P3/P4;
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) contradiction table and tolerance table;
[Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §7.2.

**What:** two mismatches in the gate definitions, in files that explicitly claim to agree
("Agrees with `Overarching_Goal.md`. If they drift, the Goal file wins").

*P3.* The Goal defines it purely as a measurement — "the H₂-trained rule, **untrained on water**, scored on
H₂O teacher windows (zero-shot)" — with no comparison and no criterion. The freeze and Distilled define its
pass condition as a comparison: "no numerical gate; beat linear baseline or say inconclusive." Since the Goal
wins on drift, the promised deliverable's P3 currently has *no* criterion at all, and the criterion that
exists is the P4 comparison under a second name.

*P0 on H₂O.* [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) puts \(< 5\times10^{-3}\) in
a column headed "Gate (H₂O transfer)". Distilled §7.2 writes the same number as "\(< 5\times 10^{-3}\)
**(report)**". [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §4 omits the water column
entirely. Gate, report, or absent — three files, three answers.

**Why it matters:** P3 is the transfer claim, the thing the plan exists to test. A gate whose status is
ambiguous is a gate that will be read as "report" if the number is bad and "gate" if it is good, without
anyone having to edit a file.

**Status:** closed 2026-09-01. P3 is now one test with two parts, both always reported: the zero-shot error
(the Goal's definition) *and* the comparison against the frozen linear stencil (its pass language), with
neither droppable because the other looked better. Water P0 is **report only** in all three files, and the
column heading that called it a gate is gone.

---

### 9. The freeze cites Octopus in the form its own bibliography forbids

**Where:** [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md), end of the contradiction pass:
"Teacher code for every promised rung: **Octopus** (Andrade et al. 2020 family)."
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) item 1.

**What:** the bibliography's 2026-09-01 verify pass records, in bold, "**Do not cite as Andrade et al.**" —
the 2020 JCP paper's first author is Tancogne-Dejean; Andrade is a coauthor; the "Andrade et al." title the
working bibliography carried belongs to a *different* 2015 PCCP paper. It repeats the correction in the notes
("Item 1 first author is Tancogne-Dejean (2020 JCP), not Andrade"). The frozen ladder — the document whose
whole function is to be quoted downstream — still says "Andrade et al. 2020 family", with no DOI. The Pass A
brief itself flags this string under question 5.

**Why it matters:** "never cite from recall" is one of the five conventions the root README advertises as the
most portable thing in the repository, and the freeze file breaks it against a correction recorded the same
day in the same folder. Every downstream document that quotes the freeze inherits the wrong attribution.

**Status:** closed 2026-09-01. The freeze now reads "Tancogne-Dejean et al., *J. Chem. Phys.* **152**,
124119 (2020), DOI 10.1063/1.5142502; bibliography item 1", with the trap named in the same sentence.

---

## Non-blocking findings

All six addressed 2026-09-01, in the files named under each.

### 10. "Laptop idle ~168 h/week" is a calendar week, not idle time — and the same 168 h is also a one-off cap

**Where:** [Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) §1 and §2.

\(7 \times 24 = 168\). §1 tabulates "**Wall-clock compute** | laptop idle ~168 h/week", i.e. the machine is
asserted to be 100 % idle, on the same laptop where the 840 h of human attention is spent. §2 then reuses the
same 168 h as a *total* cap for the promised teacher set ("One unattended week for the whole promised set").
One number is doing duty as a weekly throughput rate and as an absolute budget; if the promised set needs two
weeks of nights, the two readings disagree about whether that is a stop.

### 11. Root README's "no implementation and no results" is false about its own tree

**Where:** [README.md](../../../README.md), opening block vs "Repository layout".

The banner says the repository "contains no implementation and no results"; nine paragraphs later the layout
lists `probes/ scripts`, `scraper/ tooling, and the raw scrapes it produced`, and `requirements.txt`. Eight
executable probe scripts are implementation. Combined with finding 1, the safest wording is "no results *for
plan 03*".

### 12. The nuclear refinement rule is coarser than the outer spacing on every promised rung

**Where:** [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) "Time and grid";
[probes/grid_spec.py](../probes/grid_spec.py) `REFINEMENT_RULE`.

The rule is "\(h(r)\sim a_0/Z\) near nuclei, \(h\) capped outside", with outer spacing \(0.20\,a_0\). For
hydrogen \(Z=1\), so \(a_0/Z = 1.0\,a_0\) — five times *coarser* than the grid it is supposed to refine. The
promised ladder is H, H₂, H₂O; on rungs 0 and 1 the refinement rule is inoperative or inverted, and only
oxygen (\(0.125\,a_0\)) refines. Whether the intended rule was \(h \sim 0.20\,a_0/Z\) or something else is a
Pass B question, but as written the sentence does not describe a refinement.

### 13. Two incompatible "item N" numbering systems

**Where:** [Papers/README.md](../../../Papers/README.md) header vs
[Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md).

`Papers/README.md` states the PDFs are "numbered to match the bibliographies in
`plans/*/GoalGathering/Relevant_Scientific_Papers.md`". Plan 03 renumbered from scratch: its item 10 is the
missing voxel dump (FAIL), while `Papers/10_Meng2023_PAH_Charges_OUP.pdf` is a PAH-charges paper. Its item 4
is the FNO paper, stored as `Papers/16_…`. Since plan 03 is the only plan in the tree, the shared folder's
stated invariant is now false, and "item 10" means two different things depending on which file the reader is
in. Also: `Papers/README.md` claims "**36 PDFs**"; the folder holds 37 (`37_the_hydrogen_molecular_ion_revisited.pdf`
is present, is not in the table, and breaks the `NN_FirstAuthorYear_Topic.pdf` convention).

### 14. Small status drifts in the probe/gate tables

- [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §7.1 lists **Q6**
  in a table headed "Scripts under `probes/`", with the pass condition "one training step is one conv over the
  volume". [probes/README.md](../probes/README.md) states plainly that Q6 "is not a file yet". A row in a
  script table for a script that does not exist is the R4A-1 class.
- The **H-atom** rung is "Analytic 1-e / exact grid TDSE" (a rung with no Octopus in it), yet
  `teacher_cost.py` requires an `"H"` wall-clock entry and refuses to run without it, and §2 counts the H-atom
  window inside the *Octopus* 168 h cap.
- [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md) has no date in its filename, is stamped
  "Frozen date. 2026-08-29", and contains a table of edits made to it on 2026-09-01. Plan 02's convention
  (per its own supersession note) was a new dated file. A freeze whose amendment mechanism is "add a row to
  the freeze" is weaker than the plan thinks.
- 840 h is never divided by an hours-per-week figure anywhere in the plan. "~10 h/week" appears **only** in the
  two reviewer briefs, which are not plan documents. Issue 15 / R3-6 are correctly marked open, but a reader
  cannot even sanity-check 840 h without a number the plan does not contain.

### 15. Two files sit in the folder that the reading order neither includes nor excludes

**Where:** [Why_03_Supersedes_02.md](Why_03_Supersedes_02.md); [PATCH_plans_README.md](../PATCH_plans_README.md).

The Pass A reading list has nine entries and an explicit ignore list. `Why_03_Supersedes_02.md` is on neither,
although [plans/README.md](../../README.md) calls it "the argument of record" and
[Compute_Budget_2026-09-01.md](Compute_Budget_2026-09-01.md) declares that it *supersedes a sentence inside it*
— i.e. a file the reviewer is not told to read is being actively patched by a file the reviewer is told to
read. `PATCH_plans_README.md` is on the ignore list but is still in the tree and still contains the only
surviving three-column comparison table, including the phrase "Complete as a plan" (about plan 02).
The PATCH file is correctly banner-ed; it is the *combination* of "ignore this" and "this is the only place
the table lives" that is unreadable without the author.

---

## Loopholes (question 4)

Named sentences that would let a determined author pass a gate without earning it. All eight closed
2026-09-01 in [Distilled §4](Distilled_Project_Plan_and_Quality_Checks.md), §6.2, and the Round-5 block of
[Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md): a deviation note must now be committed
*before* the affected quantity is measured; loosening any P0–P4 number after the pilot, promoting the
5×5×5 axis to the thesis, and editing the frozen baseline after Q0 are named as deviations; the 8 h pilot
is confined to the train/validation slice; "silently" is gone; and a differing file hash is explicitly *not*
sufficient to make two datasets distinct.

1. **Every gate is loosenable by a note the author writes.** "The 8 h pilot may only **tighten**, never
   loosen, without a §4 note." Nothing in [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
   §4 requires a counter-signature, a mentor, or a date *before* the number is known — "A deviation is allowed
   only in writing, dated, with the probe that forced it." The author owns the probe, the writing and the date.
   This is the single widest hole in the plan; every other loophole here is a special case of it.
2. **The effect size is set after seeing the learner.** "Pre-register 'small / medium' after the 8 h pilot,
   not after the test." The pilot's data provenance is never constrained, so the pilot may be run on the P4
   comparison itself; §6.2 forbids stopping on H₂ *test* windows but says nothing about the pilot.
3. **"Silently" is doing a lot of work.** "A later probe may force a §4 deviation; it may not **silently**
   reopen the OR." A loud reopen is permitted by the same sentence.
4. **Escalation rung 4 authorises what rungs 2–3 forbid.** "P0 fails on the linear stencil already → fix the
   **teacher/grid**, do not train," with no §4 note required — against "Do not coarsen \(0.20\,a_0\)" (rung 2),
   "Do not redesign the grid" (rung 3) and §4's "Changing the grid after Q0 is hashed". Given finding 3, this
   rung cannot fire today; if P0 is repaired so that it can, the loophole opens.
5. **A hash is not a dataset.** "02 and 04 may both be 'QM9' **only** if file hashes and prediction targets
   differ." The rubric bar is "Not the same dataset used in Projects 1 or 2". Re-exporting one CSV changes the
   hash while leaving the dataset identical; the plan's test would be passed by a `to_csv` call.
6. **The headline comparison has no pre-registered threshold.** P3: "no numerical gate … beat linear baseline
   or say inconclusive"; P4: "**declared** \(\Delta\) in relative \(L^2\)" — declared where, and when, is never
   fixed. Combined with loophole 2, the plan's flagship result has no number frozen in advance at all.
7. **Drift is reported, never bounded.** "Energy drift is reported. It is not a hidden extra gate." Any drift,
   of any magnitude, is compatible with a pass.
8. **Kernel promotion is not listed as a deviation.** \(5\times5\times5\) is "the single Module 05 comparison
   axis". §4's forbidden-without-a-note list does not mention promoting the comparison axis to the thesis, so
   a \(3\times3\times3\) failure can be relabelled as a \(5\times5\times5\) success without a §4 note.

---

## What passed

Named explicitly, because these are the parts a Round 6 should not re-litigate.

- **The inheritance tally audits exactly.** I recomputed all thirty fates from the named rows: superseded
  {2, 10, 11, 14, R3-2, R4B-1, R4B-3, R4B-4} = 8; re-scoped {1, 7, 12, R3-1, R3-4} = 5; carried {3, 4, 5, 8, 9,
  13, 15, R3-3, R3-5, R3-6, R4A-1, R4A-2, R4A-3, R4B-2, R4B-5, R4B-6} = 16; addressed in spec {6} = 1;
  \(8+5+16+1=30\). The inline tally in [README.md](../README.md) lists the *same issue numbers*, not just the
  same counts. R4A-3 (summary sentence vs named rows) is genuinely closed — this is the one Round-4 Pass A
  finding I actively tried to break and could not.
- **The bibliography verify pass is the opposite of the failure mode the brief warns about.** Item 10 is
  marked FAIL with the three near-misses named and rejected; items 7, 8 and 15 are marked NOT FETCHED with an
  explicit ban on citing them; item 1 corrects the plan's own authorship error; item 14 corrects an issue
  number (19(1) → 19(5)). Three claimed PDF locations spot-checked and present: `Papers/01_Ramakrishnan2014_QM9.pdf`,
  `Papers/16_Li2020_FourierNeuralOperator.pdf`, `Papers/19_Mordvintsev2020_GrowingNCA.pdf`.
- **The probes really do refuse to invent numbers.** `die_not_run` prints `NOT_RUN` and exits 2;
  `teacher_cost.py` will not run without a log and will not fabricate a species; `p0_fixed_point.py` refuses
  any `--rule` other than `linear` ("not hashed"). The 168 h cap is not typed into any Python file as a result.
- **Arithmetic I could check, checked out.** \(80+160+320+200+80 = 840\). \(200 \times 0.05\) au \(= 10\) au
  \(= 0.242\) fs, matching the stated "\(\approx 0.24\) fs". \(\tfrac{2}{3} \times 840 = 560\) (the number is
  consistent even though its provenance is not — finding 7).
- **The 2026-09-01 contradiction pass did close what it claims to close.** No surviving instance of "hash the
  grid in Module 02"; no surviving instance of Poisson-as-teacher outside an explicit prohibition; no
  surviving "0.15–0.25 \(a_0\)"; no instance of "complete as a plan" applied to plan 03 anywhere in the tree —
  the only survivals describe plan 02, correctly, in historic tables.
- **Rubric row/column counts are right.** Module 02 "≥200 rows, ≥5 cols" and Module 03 "≥500 rows, ≥6 cols"
  match Rubrics 1.5.1 verbatim, and the "Project 1 = module 02" offset is stated rather than silently applied.
  Module 04's accepted-sources trap is recorded accurately (the Module 03 one is not — finding 5).
- **The forbidden-quotes list and the non-claims section are consistent** across
  [Overarching_Goal.md](Overarching_Goal.md) §"Forbidden quotes" and
  [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md) §9, and the
  Horizon folder does not smuggle any of them back into Module 08.

---

## Hand-off to Pass B

Pass B should be given this file, and told specifically:

- Attack 5 ("the linear stencil is either too weak or too strong") is no longer hypothetical. Finding 4
  measures it: at the frozen \(\Delta t\) and \(h\) the baseline is 59× past its stability limit and reaches
  NaN inside the P2 horizon, while finding 3 shows the P0 that was supposed to catch that cannot.
- Attack 1 should be told the state is **eleven** channels, not twelve (finding 2), before it argues about
  what a \(3\times3\times3\) neighbourhood can represent.
- Finding 12 (\(a_0/Z\) coarser than the outer spacing on H and H₂) is stated as arithmetic, not as physics.
  Pass B should decide what the rule was meant to say.
- Findings 5 and 6 are rubric-side, not domain-side; Pass B attack 4 can take them as given rather than
  re-deriving them.

**Do not write Pass B in this file.**
