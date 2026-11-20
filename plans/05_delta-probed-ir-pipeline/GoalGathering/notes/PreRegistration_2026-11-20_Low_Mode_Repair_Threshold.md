# Is 20 cm⁻¹ the right threshold for the low-mode repair? — registered before the measurement

**Written 20 November 2026, before any molecule of the sample is patched; revised the same day after an independent review of the
first draft, still before any molecule is patched.** TASKS 218. The swap registration of 14 November left this question open on
purpose (`PreRegistration_2026-11-14_Low_Mode_Label_Swap.md`, section 7, last paragraph). Nothing here swaps a label, retrains a
network or changes a constant; section 9 lists what is not decided.

## 1. The question

The training labels are analytic DFT Hessians (B3LYP and ωB97X, 6-31G*). pyscf's CPU Hessian leaves out the derivative of the
quadrature weights, and the low-mode repair corrects that by re-measuring a soft mode's curvature with finite differences of
grid-response gradients. It is applied to modes below 20 cm⁻¹ (`LOW_MODE_CM`, `modules/05_support_predictor/corpus/vibrations.py:29`).

The question: **how wrong is an unrepaired label mode between 20 and 60 cm⁻¹, and is its error ordered by the mode's frequency or by
its force constant?** "Wrong" means that the repair would move it by more than 0.5 cm⁻¹, the bound the repair's own check uses
(`probes/low_mode_patch_check.py:22`).

## 2. What is already known, and how far it goes

**The by-product points (exploratory, biased).** The repair patches both functionals along the same directions, so a molecule selected
for a B3LYP mode below 20 cm⁻¹ was also patched in ωB97X, where that mode often sits higher. `probes/low_mode_threshold_read.py` read
those records on 20 November into `probes/results_m1/low_mode_threshold_2026-11-20/existing/` (RESULT.md, record.json, points.csv):
128 points on 60 molecules, 11 of them flagged and left out. The unflagged ωB97X points between 20 and 100 cm⁻¹:

| label frequency (cm⁻¹) | n | median abs Δ (cm⁻¹) | max abs Δ | > 0.5 | fraction | 1 SE |
|---|---|---|---|---|---|---|
| 20–30 | 1 | 2.81 | 2.81 | 1 | 1.00 | 0.00 |
| 30–40 | 1 | 1.67 | 1.67 | 1 | 1.00 | 0.00 |
| 40–50 | 4 | 2.51 | 4.01 | 3 | 0.75 | 0.22 |
| 50–60 | 35 | 0.70 | 4.43 | 24 | 0.69 | 0.08 |
| 60–80 | 11 | 0.89 | 6.72 | 9 | 0.82 | 0.12 |
| 80–100 | 0 | undefined | undefined | 0 | undefined | undefined |

Spearman of the size of the move against the label frequency is −0.26 and against the logarithm of the force constant −0.29 (n = 52);
frequency and log force constant correlate at +0.56 on these points. In the softest quarter of the force constants (1.68e-4 to
9.59e-4 hartree/bohr²) the median move is 2.76 cm⁻¹; in the other three quarters it is 0.54, 0.71 and 0.89.

This table decides nothing, for three reasons. The points were looked at before the read script existed (TASKS 218 was opened because
of them). Every molecule in it was selected for a label mode below 20 cm⁻¹, so it is not a sample of the molecules the threshold
leaves alone. And it holds no B3LYP mode between 20 and 60 cm⁻¹, which is where the unrepaired population is (section 3).

**One second route.** For B_0f06474656 a full finite-difference Hessian of grid-response gradients exists. Its ωB97X mode reads 55.42
in the label, 58.02 after the patch and 57.98 in the full finite-difference Hessian
(`probes/results_m1/low_mode_patch_2026-11-13/check/check_B_0f06474656.txt:2`). So for that one mode the patch is right to 0.04 cm⁻¹
and the label is off by 2.56. No other point above 20 cm⁻¹ has a second route.

**What a point's change contains besides the label's error.** The first draft said the patch's noise is 0.13 to 0.15 cm⁻¹ and the 0.5
line three to four times that. That is not true for every point of this sample. The 0.13 (patch against full finite difference,
`vibrations.py:15-16`) and the 0.15 (two steps, `vibrations.py:31`) were measured on modes carried by heavy atoms, and the 0.15 with
SCFs converged tighter than the runner's (section 4). Three contributions, per point:

- *Gradient noise.* The patch measures a mode's curvature as λ = d·(g₊ − g₋)/(2q), with d = v/√m the mode's Cartesian displacement
  and q the mass-weighted length of the step. Noise σ on every gradient component becomes σ·√2·|d|/(2q) in λ and that divided by 2ω in
  the frequency (`low_mode_threshold_read.noise_sensitivity_cm`, pinned on a two-atom mode and against the repair's own `column` in
  `tests/test_low_mode_threshold_read.py`). A mode in which light atoms carry the motion has a short step q for the same largest
  displacement of 0.01 bohr, so it is several times more sensitive. Per 1e-7 hartree/bohr of gradient noise the 21 registered points
  give (SAMPLE.md, column "noise"):

  | point (label cm⁻¹) | cm⁻¹ per 1e-7 hartree/bohr |
  |---|---|
  | B_0c6c144a7f (23.7) | 1.09 |
  | B_55cca3aaf2 (23.8) | 1.04 |
  | B_4ff67f9ea2 (33.0) | 0.73 |
  | B_3dcbd985e3, second mode (30.3) | 0.71 |
  | B_863cdaad7a (53.8) | 0.28 |
  | the other 16 | 0.06 to 0.24 |

  The gradient noise itself is known from one molecule: on B_0f06474656 (15 atoms) the patch's g₊ − g₋ differs from the full
  finite-difference column by 1.9e-8 hartree/bohr rms in both functionals, which is σ ≈ 1.4e-8 per gradient if the two are
  independent (the `columns` of `low_mode_patch_2026-11-13/check/B_0f06474656/hessian_<tag>_analytic_grfpatch.npz` against `H_fd` of
  `probes/results_m1/hessian_grf_B_0f06474656_2026-11-12/fd_hessian_<tag>.npz`). At σ between 1e-8 and 2e-8 one standard deviation is
  0.07 to 0.22 cm⁻¹ on the four points above 0.5, 0.03 to 0.06 on B_863cdaad7a and 0.01 to 0.05 on the 16 quiet ones. For molecules
  of 23 to 25 atoms σ has not been measured.
- *Step and other systematic error.* On the same molecule the patched curvature along the direction stands 4.08 (B3LYP) and 4.10
  (ωB97X) cm⁻² above the full finite difference's (same two files). If that offset is the same size elsewhere, which one molecule
  cannot show, it is 0.10 cm⁻¹ at 20 cm⁻¹, 0.05 at 40 and 0.03 at 60.
- *The pyscf version.* Below 0.01 cm⁻¹ on soft modes (section 4).

Added up at σ = 2e-8, a heavy-frame point at 20 cm⁻¹ carries about 0.15 cm⁻¹ that is not label error, so the 0.5 line is three times
that or more. The four light-atom points, all between 20 and 35 cm⁻¹, carry 0.21 to 0.30 (noise plus the offset at their frequency),
so the line is only 1.7 to 2.4 times that. That is thin, and it is why those points are step-checked from the start (section 5).

## 3. The sample

`probes/low_mode_threshold_sample.py`, seed 218, wrote `probes/results_m1/low_mode_threshold_2026-11-20/sample/` (SAMPLE.md,
sample.json, ids_sample.txt, ids_step02.txt). The population is the corpus molecules that carry no repair in either label, banded by
their lowest B3LYP mode:

| lowest B3LYP mode (cm⁻¹) | unrepaired molecules | with ≤ 25 atoms | eligible | drawn |
|---|---|---|---|---|
| 20–30 | 54 | 41 | 41 | 5 |
| 30–40 | 66 | 42 | 41 | 5 |
| 40–50 | 79 | 54 | 54 | 5 |
| 50–60 | 191 | 146 | 146 | 5 |

- **At most 25 atoms**, because the run shares the laptop with the training search: a gradient of a 21–25-atom molecule takes a median
  202 s (B3LYP) and 264 s (ωB97X) at 8 threads (SAMPLE.md, last paragraph), and the 26–30-atom molecules of the repair of
  13 November took about twice that (the `seconds` of their `dir_*.json` files in `low_mode_patch_2026-11-13/corpus`: medians 438 and
  491 s over 14 points each). The cost of this choice: the sample says nothing about the 107 larger molecules of the population
  (390 − 283), and the size of the move may depend on size.
- **Eligible** means no mode of either label below 20 cm⁻¹, imaginary ones included. One molecule with at most 25 atoms falls out by
  this (band 30–40). Such a molecule is a repair candidate already or never trains.
- **The draw.** Per band the sorted ids are shuffled once with `numpy.random.default_rng(218)` and the first five taken. A larger draw
  with the same seed contains the smaller one (`tests/test_low_mode_threshold_sample.py`, first test).
- **Five per band, not in proportion.** The bands hold 41 to 146 eligible molecules; equal numbers give each band the same weight, so
  the pooled fraction is not the population's fraction: it over-weights the soft end, where the question is. The read prints the
  fraction per band and a second fraction weighted by the bands' eligible molecules (41/41/54/146) beside it; the rule reads the
  unweighted one, and its outcome is worded for this population and no other (section 7).

The 20 molecules hold 21 B3LYP modes between 20 and 60 cm⁻¹ (SAMPLE.md, the per-molecule table) and 3 ωB97X modes.

## 4. The settings

The measurement is the repair's own runner, `probes/low_mode_patch_run.py`, called through `probes/low_mode_patch.sh` with
`--below 60`: every label mode below 60 cm⁻¹ in either functional is re-measured in both. 6-31G* with Cartesian d functions
(`corpus/analytic_hessians.py:227`), the labels' unpruned (99,590) grid (`probes/butterfly_scan.py:50`), a largest atomic displacement
of 0.01 bohr (`vibrations.py:31`), pyscf 2.15.0. Two settings differ from the labels':

- A displaced point converges to 1e-9 in the energy and 1e-7 in the orbital gradient where a label converges to 1e-11
  (`analytic_hessians.py:95-96, 237`). This is part of the gradient noise of section 2.
- The labels were made with pyscf 2.14.0. On B_0f06474656 the 2.15.0 analytic Hessian (`H_analytic_215` in the `fd_hessian_<tag>.npz`
  files named in section 2) differs from the label by at most 0.24 cm⁻¹, and that is one B3LYP mode at 1187.9 cm⁻¹; on the lowest mode
  the difference is 0.013 cm⁻¹ (B3LYP, 9.5 cm⁻¹) and 0.001 (ωB97X, 55.4 cm⁻¹). The likely source is the older version's Krylov CPHF
  solver, which can stop early (pyscf issue #2702); the ledger entry of 12 November 19:5x read these same numbers as too small to
  matter. Either way it is a second cause of label error beside the missing grid-weight derivative, small on the soft modes of this
  one molecule, and the finite difference of 2.15.0 gradients corrects both. A change read here is therefore "label against patch",
  not "the grid-weight error".

**The upstream call.** The gradient is `mf.nuc_grad_method().set(grid_response=True).kernel()`
(`probes/hessian_grid_response_fd.py:92-93`). pyscf's own `hessian/test/test_rks.py`, function `finite_diff`, makes the same call to
build its reference Hessian; `probes/hessian_grid_response_fd.py:4-5` cites it.

**Where it writes.** Into `probes/results_m1/low_mode_threshold_2026-11-20/patch_below60/<id>/`. The runner reads `geometry.json` and
the two label files (`probes/low_mode_patch.py`, `read_label`) and writes only under its out folder: the gradient points, the patched
Hessian, the report, its settings and pyscf's log (`probes/low_mode_patch_run.py`: `gradient_at`, `write_patch`, `patch_molecule`,
`claim_out_folder`, `main`). No label file is touched. Since this revision the out folder records the threshold, step and grid its
points were made with (`run_settings.json`), and the runner refuses to write into a folder made with others or into one that holds
results without that record, because it keeps every point file it finds (`low_mode_patch.settings_conflict`,
`tests/test_low_mode_patch.py`; the refusal was exercised in WSL on both cases, before any SCF). Run spec:
`probes/runspecs/low_mode_threshold_sample_2026-11-20.json`; 84 gradients and 40 reference SCFs, 6 to 12 hours at 4 threads by an
estimate whose 4-thread factor is assumed, not measured.

## 5. The two-route check

**From the start.** Seven molecules are patched a second time with a step of 0.02 bohr into `patch_step02_below60/`
(`probes/runspecs/low_mode_threshold_step02_2026-11-20.json`; 32 gradients, 2 to 4 hours by the same estimate). The list is a rule in
the sample script, not a choice: the smallest sampled molecule of each band (B_0c6c144a7f, B_1726105aae, B_0af11315e3, B_1428bc8164),
and every molecule with a registered point whose noise exceeds 0.5 cm⁻¹ per 1e-7 hartree/bohr (B_0c6c144a7f again, B_55cca3aaf2,
B_4ff67f9ea2, B_3dcbd985e3). A doubled step halves the gradient-noise term, so a point that is mostly noise shows it here.

**Before the rule is read.** Every registered point that moved by more than 0.25 and less than 1.0 cm⁻¹ and has no step check is
repeated at step 0.02 in a second, small run into the same folder. Until it has its check the read states no outcome and names the
points that are waiting.

**What a failed check does.** A point whose patched frequency differs by more than 0.15 cm⁻¹ between the two steps is flagged and
left out of every statistic. If two or more registered points fail, the finite difference is not under control at these frequencies:
the outcome is 3 (undecided) and the step check is extended to all 20 molecules before any statement. A check point whose own mode has
no single counterpart after the patch checks nothing and is set aside; its point counts as unchecked.

This checks the finite difference, not the method. The method's only independent check above 20 cm⁻¹ stays the one mode of section 2.

## 6. What is read

`probes/low_mode_threshold_read.py` derives one point per re-measured label mode and functional: the mode's frequency in the label, the
frequency of the patched mode it overlaps most, the signed change, the share of the mode inside the patched space (coverage), the
Cartesian force constant along the mode in the label (hartree/bohr²), and the noise per 1e-7 hartree/bohr of section 2. A point with
coverage or overlap below 0.9 is listed, flagged, and left out. Per functional the read prints, by frequency band (20–30, 30–40,
40–50, 50–60, 60–80, 80–100 cm⁻¹) and by quartile of the force constant: the number of points, the median and largest absolute
change, the fraction above 0.5 cm⁻¹ with its binomial standard error, and the median noise; Spearman's correlation of the absolute
change with the frequency and with the logarithm of the force constant, and of those two with each other; and every registered point
on a line of its own.

**An ωB97X point is a weaker measurement.** The directions at `--below 60` come almost entirely from B3LYP modes. An unflagged ωB97X
point is therefore the ωB97X Hessian corrected along the B3LYP direction only: the part of the ωB97X mode outside that direction keeps
the label's value, so the change understates the label's error by roughly (1 − coverage), up to a tenth for a point that passes.

The script ran on synthetic records before this registration was committed (`tests/test_low_mode_threshold_read.py`, 43 tests): a
direction that is an exact mode gives back a constructed change of 2.5 cm⁻¹ to 1e-6; a mixed direction is flagged and counted nowhere;
a mode that turns imaginary is a signed move and is counted; two rotated directions give one point per mode; two near-degenerate modes
that the patch couples are both flagged; an empty band is a row with n = 0; moves that are all zero give an undefined correlation,
printed as such; each outcome of section 7 is reached from constructed points, the boundaries included; two failed step checks give
outcome 3; and a move near the line without a step check holds the outcome back.

## 7. The decision rule

Registered population: the **B3LYP** points of the **sample of section 3**, label frequency **20 to 60 cm⁻¹**, coverage and overlap at
least 0.9, not flagged by the step check. With n such points, p the fraction that moved by more than 0.5 cm⁻¹ and SE = √(p(1 − p)/n):

1. **p ≤ 0.20 and p + SE ≤ 0.30.** For molecules whose lowest B3LYP mode lies in 20–60 cm⁻¹, with at most 25 atoms, each band weighted
   equally: the B3LYP labels of their modes in this window are sound at the 0.5 cm⁻¹ line. The threshold stays. The ωB97X moves of
   section 2 are then a property of that functional's label and get a task line of their own.
2. **p ≥ 0.50 and p − SE ≥ 0.40.** For the same population: a majority of those labels stand more than 0.5 cm⁻¹ from the patched
   value, and the 20 cm⁻¹ threshold leaves them so. The outcome says that label and patch disagree; it does not say that the
   quadrature grid is the cause (section 4). The size of a re-patch — which molecules, how many hours — is then put to the author as a
   compute decision before anything is patched.
3. **Anything else.** Undecided at this sample size. The next step is the extension: five more molecules per band from the same
   shuffle (`--per-band 10`), not a verdict.

Four conditions stand before the rule:

- Fewer than 16 points left in the registered population is outcome 3 whatever p is: the binomial standard error is zero at p = 0 and
  at p = 1 for any n, so without a floor three unmoved points would read as outcome 1.
- Two or more registered points failing the step check is outcome 3 (section 5).
- A registered point near the line without a step check: no outcome is stated yet (section 5).
- The outcome is also printed with the flagged points counted as moved and as unmoved, beside the registered one. The registered p
  stays the one on unflagged points; where the two bounds give different outcomes, the registered outcome is reported together with
  that fact and not without it.

**What orders the moves is described, not decided.** The first draft let outcome 2 name a trigger, frequency or force constant,
by the larger correlation. On the 21 registered points the label frequency and the logarithm of the force constant correlate at 0.79
(Spearman, computed from the labels by the reviewer; the read prints the value on its own points). They are nearly one ordering, and
in the reviewer's simulation the sub-rule named the true trigger in 37 % of draws and named one in 11 % of draws that had none. So the
read prints both correlations with their signs and n, says that this sample cannot separate them, and names no trigger. Telling them
apart needs points chosen for it — soft modes at high frequency and stiff ones at low — which this sample was not drawn for.

**The power of this sample, stated before the run.** 21 points are expected. At p = 0.5 one standard error is 0.11. With 21 points
outcome 1 needs at most 4 moved, outcome 2 at least 11, and 5 to 10 moved is undecided. The rule's error rates at n = 21
(`low_mode_threshold_read.outcome_probabilities`, pinned in the tests): a true fraction of 0.30 reads as outcome 1 in 20 % of draws; a
true fraction of 0.40 reads as outcome 2 in 17 %; a true fraction of 0.35 comes out undecided in 83 %. These rates are accepted
because neither outcome moves a label by itself: outcome 1 leaves things as they are and can be revisited by the extension, and
outcome 2 only opens a compute decision that is taken separately, with the re-patch's own registration.

## 8. The secondary read (descriptive)

The read prints the root mean square of the signed changes of the unflagged points between 20 and 100 cm⁻¹, per functional. It is set
beside the network's error on family 'other' — 2.38 and 2.10 cm⁻¹ on the two test sets for v1.4
(`modules/08_industry_synthesis/out/scenario_results_submitted.json`, `licence.errors.other`) — because noise in the soft-mode labels
bounds how well the network can be measured there. This is a description and carries no decision. Two limits: the read does not
compute a mode's family (the rule lives in the trainer's code, which is not imported while the search runs), so "soft modes" stands in
for "'other' modes" on the strength of the count of 12 November, which found every label mode below 50 cm⁻¹ in 'other'; and at
`--below 60` few points lie above 60 cm⁻¹.

## 9. What this registration does not decide

- No label file is swapped. A swap needs its own registration, and `probes/low_mode_swap.py` refuses a patch made at another threshold.
- No retrain. A changed threshold changes labels, and changed labels ride with the one retrain of TASKS 287 after the search.
- `LOW_MODE_CM` stays 20 until then.
- No trigger is chosen between frequency and force constant.
- Nothing about molecules above 25 atoms, about cations, or about molecules with an imaginary mode (TASKS 215).
- Nothing about whether the patched frequency is the true one beyond the one mode with a second route. Outcome 2 says that label and
  patch disagree by more than 0.5 cm⁻¹ on a majority of soft modes of the sampled population; that the patch is the better of the two
  rests on B_0f06474656 and on the step check.

## 10. If the author chooses `--below 100` instead

The sample then has 36 directions, 144 gradients, 9.6 to 19.1 hours by the same estimate, and the step check 13 directions, 52
gradients, 3.1 to 6.2 hours (SAMPLE.md). The registered population and the rule do not change; the 60–80 and 80–100 bands get B3LYP
points, which the table shows and the rule does not read. In both run specs `--below 60` becomes `--below 100` and `patch_below60` /
`patch_step02_below60` become `patch_below100` / `patch_step02_below100` in the command and in `heartbeat_glob`, with the estimate's
hours. Both runs must use the same threshold: the read refuses a step check made at another.

## Amendment 1 (20 November 2026, 12:3x UTC, before any molecule of the sample is patched) — the place of the sample run

The author rented a Hetzner CCX53 (32 dedicated cores, 122 GB, Ubuntu 24.04; `night20` in `tools/hosts.tsv`) for the night of
20 November. The sample of section 3 runs there instead of on the laptop. Nothing else in this registration changes: the sample,
the settings of section 4, the two-route check, the read and the rule stand as written.

- **Same code, same commit.** The server's code is `git archive` of commit fb3cd34b (`/root/dpir`, stamped in `/root/dpir/COMMIT`).
  The runner and everything it imports are unchanged between fb3cd34b and the trunk at this amendment (63929079; `git diff --stat`
  over the run spec's sources is empty).
- **Same pyscf.** Env `qc215` on the server is built as `tools/build_env_beside.py` built the laptop's: a venv on the server's `qc05`
  interpreter with the laptop `qc215`'s 21 pins installed `--no-deps` (pyscf 2.15.0, numpy 2.5.2, scipy 1.18.1); `pip check` passes
  and its `pip freeze` equals the pin list. The interpreter differs in its patch release and compiler (CPython 3.12.16, GCC, from
  conda-forge; the laptop's is 3.12.14, Clang, from uv). Both freezes are kept in `probes/results_m1/night20_2026-11-20/env/`.
- **Same arguments.** `--below 60`, the default step of 0.01 bohr, `--max-memory 2048`. Threads differ: 8 per process where the
  laptop spec has 4.
- **Four lanes.** Four processes of 8 threads over four disjoint id lists that together are `ids_sample.txt`
  (`probes/results_m1/night20_2026-11-20/job218/ids_lane{0,1,2,3}.txt`; 4, 5, 5 and 6 molecules; 90, 90, 90 and 93 minutes by
  SAMPLE.md's minutes per molecule). Each lane writes into an out folder of its own (`/root/night20_218/out_lane<k>`), because the
  runner appends pyscf's log to one `pyscf.log` per out folder and four processes would write that file together; every other file
  is per molecule. Each folder carries its own `run_settings.json`. The fetch puts the molecule folders and the settings record
  into `probes/results_m1/low_mode_threshold_2026-11-20/patch_below60/`, where the read expects them, and the four logs beside the
  env records. Launched through `tools/runspec.py` (specs `probes/runspecs/night20_218_lane<k>.json`), which calls
  `tools/remote_launch.sh`.
- **The gate, passed before this amendment.** (a) The runner's own water test on the server in `qc215`
  (`tests/test_low_mode_patch_run.py`): 3 passed in 20.8 s. (b) One molecule of the repair of 13 November recomputed on the server
  with that run's arguments (`--below 20`, step 0.01, 8 threads, `--max-memory 2048`) from the label files that run read
  (`corpus/superseded_2026-11-14/B_1e0fa2d7f0/`, 13 atoms; the corpus's own files are the swapped ones since 14 November), against
  the laptop's records in `probes/results_m1/low_mode_patch_2026-11-13/corpus/B_1e0fa2d7f0/`, over the four gradient points of both
  functionals: the energies differ by at most 3.2e-12 hartree (bound 1e-8), the gradients by at most 1.9e-8 hartree/bohr in any
  component (bound 1e-6), the patched frequencies by at most 0.0016 cm⁻¹ over all 33 modes of either functional (bound 0.05;
  B3LYP's lowest −11.9545 on the laptop and −11.9535 on the server, ωB97X's 48.6212 and 48.6229), and the directions by 4e-15.
  The gradient difference is the size of the gradient noise section 2 measured on B_0f06474656 (σ ≈ 1.4e-8 per gradient), so the
  place adds no noise beyond what the registration already counts. The server's records are in `/root/night20_gate/out`.
- **The inputs.** Per sampled molecule `geometry.json` and the two label files, the files `read_label` opens and no others, copied
  from the corpus; 60 files, sha256 equal on both sides. None of the 20 has a superseded label. The runner's dry run on the server
  over the full list prints 20 molecules, 21 directions below 60.0 cm⁻¹, 84 gradient points, as SAMPLE.md has it.
- **The step-0.02 check stays on the laptop** (`low_mode_threshold_step02_2026-11-20`, running since before this amendment, into
  `patch_step02_below60/`). The two routes of section 5 are therefore also two machines; the gate above is what makes a difference
  between them a difference of the step.
- **The laptop spec `probes/runspecs/low_mode_threshold_sample_2026-11-20.json` is not launched.** Its estimate of 6 to 12 hours
  was for 4 threads beside the training search; four lanes of 8 threads on the server are expected to end within about two hours.

## Amendment 2 (20 November 2026, 14:3x UTC) — the read's outcome, and the step check extended to all 20 on night20

**The registered read ran** (`probes/results_m1/low_mode_threshold_2026-11-20/read/RESULT.md`, with record.json and points.csv),
on the sample's records from night20 (amendment 1; fetched and checked by sha256, 145 files) and the laptop's seven step-0.02
molecules. **Outcome 3, undecided**: all 8 checked registered points — the B3LYP modes of B_0af11315e3, B_0c6c144a7f,
B_1428bc8164, B_1726105aae, B_3dcbd985e3 (two modes), B_4ff67f9ea2 and B_55cca3aaf2 — differ by more than 0.15 cm⁻¹ between
step 0.01 and step 0.02. Two or more failed checks are outcome 3 by sections 5 and 7, "and the step check is extended to all
20 molecules before any statement".

**That extension runs now, on night20.** The 13 sampled molecules not in `ids_step02.txt`
(`probes/results_m1/night20_2026-11-20/job218b/ids_step02_extension.txt`, derived by script as `ids_sample.txt` minus those
seven) are patched with the same runner call as the sample and `--step 0.02`: `--below 60`, `--max-memory 2048`, 8 threads per
process, pyscf 2.15.0 (env `qc215`), the code of commit fb3cd34b in `/root/dpir` that the sample ran from, the inputs the sample
read. 13 directions, 52 gradients and 26 reference SCFs, in two processes over two disjoint lists (119 and 121
minutes by SAMPLE.md), each into a fresh out folder of its own (`/root/night20_218b/out_lane<k>`; the runner refuses a folder
made at another step). Run specs `probes/runspecs/night20_218b_lane<k>.json`. The fetch puts the molecule folders into
`probes/results_m1/low_mode_threshold_2026-11-20/patch_step02_below60_extension/`.

**The laptop's seven step-0.02 molecules stand as measured** (`patch_step02_below60/`). For the 13 new ones both steps are
night20's; for those seven the two steps are two machines, which the gate of amendment 1 covers (gradients within 1.9e-8
hartree/bohr). Nothing else in the registration changes.

## Amendment 3 (20 November 2026, 14:3x UTC; revised 14:4x UTC before it joined the trunk) — the measurement becomes the value extrapolated to step zero, once the q² law is tested

**When this is written, and what had been seen.** After the registered read gave outcome 3 (amendment 2), and after the two steps of
the seven checked molecules were set side by side (`probes/low_mode_step_analysis.py`, into
`probes/results_m1/low_mode_threshold_2026-11-20/step_analysis/`: STEP_ANALYSIS.md, step_points.csv, record.json). Before the
step-0.02 data of the other 13 molecules were read: their folder, `patch_step02_below60_extension/`, did not exist in the
checkout when this was written and was not opened. Everything below comes from the seven molecules of `patch_step02_below60/`.
The extrapolated values of six of those seven were also seen (`step_analysis/extrapolated_7/`, a demonstration of the new read
that states no outcome); point 6 says what that costs.

This amendment was revised once, the same day, before it joined the trunk and with that folder still absent and unopened: the
rotated directions of B_3dcbd985e3 became a flag on its points where the first text made the read wait for a new measurement
(points 2 and 3), and the test of the q² law was added (point 7). The first text is commit a7a5d87b on the branch.

**1. What the two steps showed.** As registered, a point whose two steps differ by more than 0.15 cm⁻¹ is flagged and left out.
On the seven molecules that removes all 8 registered points, so after the extension the rule would have nothing to read. The
difference is not noise:

- *One sign.* The seven molecules give 16 points (re-measured mode × functional); one has no single counterpart after the patch
  and is set aside. On all 15 others the step-0.02 frequency lies above the step-0.01 one, by 0.120 to 0.573 cm⁻¹ (the 8
  registered B3LYP points: 0.226 to 0.573). Noise without a preferred sign gives one sign on 15 points with probability 6e-5.
- *One size, as a curvature.* Expressed as curvature, the difference is +16.0 to +31.2 cm⁻² (mean 23.9, standard deviation
  5.2), whatever the mode's frequency (23 to 112 cm⁻¹) and whoever carries the motion.
- *The same in two separate calculations.* Along the six directions that were measured along the same vector at both steps, the
  measured curvature uᵀC rises by 20.1 to 30.8 cm⁻² from step 0.01 to step 0.02, and the B3LYP and ωB97X values of one direction
  stand 0.8 to 3.2 cm⁻² apart. The two functionals are separate SCFs with independent gradient noise.
- *Against the noise estimate of section 2.* The two-step difference of a frequency carries √(1 + ¼) = 1.118 times the small
  step's noise. At σ = 2e-8 hartree/bohr a point's difference is 1.6 to 18.8 of those standard deviations (median 2.7; 8 of the
  15 points, the ones with the most noise, below 3), at σ = 1e-8 it is 3.2 to 37.6 (none below 3). So a single light-atom point does not
  show the bias by itself at the upper σ; the sign, the common size and the agreement of the functionals do.

This is what a central difference does. Its error is even in the step q: the measured column is C(q) = C₀ + a·q² + b·q⁴ + …,
where a comes from the quartic term of the potential along the direction. Doubling the step multiplies a·q² by four, so the two
steps differ by three times the small step's own bias: the step-0.01 curvature stands 5.3 to 10.4 cm⁻² too high on these
molecules. Section 2 already had this offset on one molecule (the step-0.01 patch of B_0f06474656 stands 4.08 and 4.10 cm⁻²
above the full finite difference, same sign, same in both functionals) and could not say whether it was general. The registered
0.15 cm⁻¹ agreement of the two steps was taken from one heavy-frame molecule at higher frequency (`vibrations.py:31`); a fixed
curvature bias weighs 1/(2ω) in the frequency, so it does not hold for modes of 20 to 60 cm⁻¹.

What two steps cannot show: that the error grows as q² and not otherwise. That is the central difference's error law for a
smooth potential, not a measurement of ours; a third step on one molecule would test it.

**2. The measurement becomes the step-extrapolated value.** Per direction the columns of the two steps are combined as

    C₀ = (4·C(0.01) − C(0.02)) / 3

(Richardson extrapolation in q²: exact for a quartic term; a sextic term b·q⁴ leaves −4·b·q⁴ at the small step's q). The patched
Hessian and its frequencies are computed from C₀ with the unchanged arithmetic of `vibrations.py` (`patched_hessian`), from the
label and the `directions` and `columns` the runner stored. Each point reports three numbers: the extrapolated change (the
measurement, which the rule reads), the step-0.01 change (what the registered read called the change), and
|ω(0.01) − ω(extrapolated)|, the size of the step bias that was removed. A point's overlap is the smallest of its three matches
(at step zero and at each step), so a mode without a single counterpart at either step is flagged as before.

Two checks stand before the combination, both in `probes/low_mode_threshold_read.py` (option `--second-step`):

- The stored columns of each step, put through `patched_hessian` from the label, must give the patched frequencies the runner
  stored, to 1e-6 cm⁻¹; otherwise the read stops. On the seven molecules, both steps, both functionals, the largest difference
  is 5.9e-11 cm⁻¹.
- Both steps must hold the same `directions`, to 1e-12 in every element. Columns measured along rotated directions carry another
  step error and do not combine. **B_3dcbd985e3 fails this**: its two directions span the same space at both steps but are
  rotated in it (largest element difference 0.73; the step-0.01 run was night20's, the step-0.02 run the laptop's, and the two
  directions come from a singular-value decomposition; the two projectors agree to 3e-14). It has two registered points (23.7
  and 30.3 cm⁻¹). They get no extrapolated value. **They are left out, flagged "directions differ"**, and listed with the
  frequencies of both steps; the read does not wait for a new measurement of that molecule. Like any flagged point they count
  in the outcome printed with the flagged points as moved and as unmoved, and they do not count towards the "two or more not
  quadratic" clause. Any molecule among the extension's 13 whose two steps turn out to hold rotated directions of one space is
  treated the same way (both their steps are night20's, so none is expected); this was decided before their data were read. A
  second step that measured another space is no second step of this measurement, and the read stops on it.

**3. What replaces the 0.15 cm⁻¹ flag.** A point is flagged "not quadratic in the step" and left out of every statistic when
|ω(0.02) − ω(0.01)| exceeds 1.0 cm⁻¹. The limit is set now, from the seven molecules, above their largest difference
(0.573 cm⁻¹, B_0c6c144a7f, B3LYP, 23.7 cm⁻¹): a difference of that size is a removed bias of about 0.19 cm⁻¹, and beyond 1.0
(a bias beyond a third of a wavenumber, two thirds of the line) a two-point extrapolation is not trusted. A molecule without a
second step at all is a missing measurement, not a flag: it is listed, and **the read states no outcome while any molecule of
its sources has no second step**. The rule is then read on the registered points that have both steps along the same directions
and carry no flag, and only when at least 16 of them are left (the floor of section 7); with the two points of B_3dcbd985e3
out, at most 19 of the 21 are.

**4. The noise of the extrapolated value.** A column's gradient noise goes as σ/q, so the step-0.02 column carries half the noise
of the step-0.01 one. With the weights 4/3 and −1/3 and independent noise at the two steps the extrapolated column carries
√((4/3)² + (1/3 · 1/2)²) = √65/6 = 1.344 times the step-0.01 column's noise. The per-point noise column is multiplied by that
factor, and the 0.5 cm⁻¹ line is held against it as before. The extrapolation removes a bias and pays for it in noise: for the
noisiest registered points (1.04 and 1.09 cm⁻¹ per 1e-7 hartree/bohr at step 0.01, 1.39 and 1.46 extrapolated) one standard
deviation at σ = 2e-8 is now 0.28 to 0.29 cm⁻¹, so the line is 1.7 times that. That is thinner than section 2 had it.

**5. Unchanged.** The population (the sample of section 3, B3LYP, label frequency 20 to 60 cm⁻¹, coverage and overlap at least
0.9); the 0.5 cm⁻¹ line; the three outcomes and their thresholds (p ≤ 0.20 with p + 1 SE ≤ 0.30; p ≥ 0.50 with p − 1 SE ≥ 0.40;
anything else undecided); the floor of 16 points; the outcome printed with the flagged points counted as moved and as unmoved;
the descriptive lines (bands, quartiles, correlations, the weighted fraction, the root mean square of section 8); and that no
label is swapped and `LOW_MODE_CM` does not change by this registration. The clause "two or more registered points failing the
step check is outcome 3" now means two or more registered points flagged "not quadratic". The rule that a registered point
which moved by 0.25 to 1.0 cm⁻¹ without a step check must be repeated is moot once every molecule has both steps, and the
extrapolated read does not apply it: a molecule without a second step holds the outcome back by point 3 instead.

The registered, un-extrapolated read stays reproducible: `--step-check` runs it as it ran, and
`tests/test_low_mode_threshold_read.py` pins that it writes the three files of `read/` to the byte. The extrapolated read ran
on synthetic records before this amendment was committed (same test file): a quartic term is removed to 1e-8 cm⁻¹ where each
single step is off by the constructed amount; a sextic term leaves the stated −4·b·q⁴; the noise factor follows from the
repair's own `column` by propagation; the flag holds at 1.0 exactly and trips just beyond; a molecule without its second step
gets no point and holds the outcome back; one with rotated directions gets flagged points that count nowhere, and 19 clean
points beside them are read while 15 are not; a second step that is not twice the first, that patched below another threshold
or that measured another space is refused; each outcome is reached from constructed extrapolated points; and without a q²-test
record that holds, no outcome is stated (point 7).

**6. What this amendment costs.** The definition of the measurement changed after part of the data was seen: the two-step
differences of seven molecules, and the extrapolated values of six of them (12 points, 6 registered; the bias removed is 0.04
to 0.19 cm⁻¹, and one registered point, B_4ff67f9ea2, goes from −0.43 at step 0.01 to −0.53 extrapolated, across the line).
The limit of 1.0 cm⁻¹ was chosen with those seven molecules' differences in view. The rule's line, thresholds and floor did not
change, and the step-0.02 data of the other 13 molecules had not been read. The registered read stays on record as outcome 3
(`read/`), and a reader who distrusts the extrapolation has the step-0.01 change of every point beside the extrapolated one.
Leaving out the two points of B_3dcbd985e3 was decided knowing their step-0.01 changes (+0.08 and −0.35 cm⁻¹, both inside the
line) and their two-step differences (+0.44 and +0.27); the reason they are out, a rotation of the directions between two
machines, does not depend on those values, and the outcome is printed with them counted both ways.

**7. The q² law is tested on a third step before the extrapolated read is believed.** Registered here, before the run; the run
is made on night20 after this amendment has joined the trunk. Points 1 and 2 rest on the step error growing as q², which two
steps cannot show. B_1726105aae and B_1428bc8164 — of the seven checked molecules the two with one direction and the least
noise (0.14 and 0.07 cm⁻¹ per 1e-7 hartree/bohr at step 0.01) — are patched a third time at a step of 0.04 bohr, with the same
runner call otherwise (`--below 60`; the runner takes steps up to 0.05 bohr, `probes/low_mode_patch_run.py:66`). The third
step must hold the directions of the other two to 1e-12, as in point 2; otherwise the test is not read.

- *The prediction.* With c = uᵀC the measured curvature along the direction and an error a·q², c(0.04) − c(0.01) = 15·a·q² and
  c(0.02) − c(0.01) = 3·a·q², so their ratio R = [c(0.04) − c(0.01)] / [c(0.02) − c(0.01)] is (16 − 1)/(4 − 1) = 5.0. An error
  linear in the step gives 3, one that grows as q⁴ gives 17, and noise gives no particular value. The denominators are known:
  29.1 (B3LYP) and 30.0 (ωB97X) cm⁻² for B_1726105aae, 29.9 and 30.8 for B_1428bc8164. The predicted numerators are five
  times those: 146, 150, 149 and 154 cm⁻².
- *The rule.* R is read per molecule and functional: four values. The law is taken to hold when all four lie in 4.0 to 6.0.
- *Where the interval comes from.* The curvature's noise goes as 1/q, so c(0.02) carries half and c(0.04) a quarter of the
  noise n of c(0.01), and to first order R carries (n/D)·√((R − 1)² + (R/2)² + (1/4)²), with D the denominator
  (`low_mode_step_analysis.q2_ratio_noise`, checked against numerical derivatives in the tests). At σ = 2e-8 hartree/bohr and
  R = 5 that is 0.30 for B_1726105aae (n = 1.88 cm⁻²) and 0.22 for B_1428bc8164 (n = 1.41); at σ = 1e-8 half of it. The
  interval is therefore 3.3 (B_1726105aae) to 4.6 (B_1428bc8164) standard deviations wide on either side at the upper σ, and
  6.6 to 9.2 at the lower: noise alone leaves it about once in a thousand per value at worst. It is not loose either. With a
  q⁴ term of x times the q² term at step 0.01, R = (15 + 255x)/(3 + 15x): R = 6.0 is x = +1.8 %, R = 4.0 is x = −1.5 %. What
  a two-point extrapolation then leaves is 4x of the bias it removed, about 7 % of at most 10.4 cm⁻², which is under
  0.02 cm⁻¹ at 23 cm⁻¹. So 4.0 to 6.0 is kept as proposed; the propagation gave no reason to move it.
- *If the law holds*, the extrapolated value is the measurement, as points 2 to 5 say.
- *If any R lies outside*, a two-point extrapolation is not trusted: the extrapolated read states no outcome, the registered
  read's outcome 3 stands, and the four R values are reported.
- *How the read enforces it.* `probes/low_mode_step_analysis.py --third <the step-0.04 folder>` writes Q2_TEST.md and
  q2_test.json with the four values and the verdict. The extrapolated read states an outcome only when that record is named
  with `--q2-test` and says the law holds; without a record, or with one that fails, it prints its tables and states none.
  There is no default record.
- *Described, without a rule.* The same script prints the zero-step curvature of c₀ + a·q² + b·q⁴ fitted through the three
  steps beside the two-point value of point 2, for these two molecules.
- *What the test does not cover.* It is made on two heavy-frame molecules (34 and 50 cm⁻¹ in B3LYP) and taken to speak for
  the light-atom modes, where the noise would swallow it; the 1.0 cm⁻¹ flag of point 3 stays the guard per point.

The test's read ran on synthetic records before this amendment was committed: an error a·q² gives R = 5 and "holds"; a q⁴
term beside it gives the computed R = 8.16 and "fails", and the three-point fit then recovers the true curvature where the
two-point value is off by the stated −4·b·q⁴; differences made as noise would leave them give R = 0.4 and "fails"; R just
inside and just outside 6.0; a third step along rotated directions, or not twice the second, is refused.
