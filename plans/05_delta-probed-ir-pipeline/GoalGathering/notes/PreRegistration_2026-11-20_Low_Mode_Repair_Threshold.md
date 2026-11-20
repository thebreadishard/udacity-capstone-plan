# Is 20 cm⁻¹ the right threshold for the low-mode repair? — registered before the measurement

**Written 20 November 2026, before any molecule of the sample is patched.** TASKS 218. The swap registration of 14 November left this
question open on purpose (`PreRegistration_2026-11-14_Low_Mode_Label_Swap.md`, section 7, last paragraph). Nothing here swaps a label,
retrains a network or changes a constant; section 9 lists what is not decided.

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

Spearman of the size of the move against the label frequency is −0.26 and against the logarithm of the force constant −0.29 (n = 52).
In the softest quarter of the force constants (1.68e-4 to 9.59e-4 hartree/bohr²) the median move is 2.76 cm⁻¹; in the other three
quarters it is 0.54, 0.71 and 0.89.

This table decides nothing, for three reasons. The points were looked at before the read script existed (TASKS 218 was opened because
of them). Every molecule in it was selected for a label mode below 20 cm⁻¹, so it is not a sample of the molecules the threshold
leaves alone. And it holds no B3LYP mode between 20 and 60 cm⁻¹, which is where the unrepaired population is (section 3).

**One second route.** For B_0f06474656 a full finite-difference Hessian of grid-response gradients exists. Its ωB97X mode reads 55.42
in the label, 58.02 after the patch and 57.98 in the full finite-difference Hessian
(`probes/results_m1/low_mode_patch_2026-11-13/check/check_B_0f06474656.txt:2`). So for that one mode the patch is right to 0.04 cm⁻¹
and the label is off by 2.56. No other point above 20 cm⁻¹ has a second route.

**The patch's own noise.** Patch against full finite difference on B_0f06474656: 0.13 cm⁻¹ (`vibrations.py:15-16`). Steps of 0.01 and
0.02 bohr: within 0.15 cm⁻¹ (`vibrations.py:31`). The 0.5 cm⁻¹ line is three to four times that.

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
  491 s over 14 points each). The cost of this choice: the sample says nothing about
  the 107 larger molecules of the population (390 − 283), and the size of the move may depend on size.
- **Eligible** means no mode of either label below 20 cm⁻¹, imaginary ones included. One molecule with at most 25 atoms falls out by
  this (band 30–40). Such a molecule is a repair candidate already or never trains.
- **The draw.** Per band the sorted ids are shuffled once with `numpy.random.default_rng(218)` and the first five taken. A larger draw
  with the same seed contains the smaller one (`tests/test_low_mode_threshold_sample.py`, first test).
- **Five per band, not in proportion.** The bands hold 41 to 146 eligible molecules; equal numbers give each band the same weight in
  the table, and the fraction over all four bands is therefore not the population's fraction. It over-weights the soft end, where the
  question is.

The 20 molecules hold 21 B3LYP modes between 20 and 60 cm⁻¹ (SAMPLE.md, the per-molecule table) and 3 ωB97X modes.

## 4. The settings

The measurement is the repair's own runner, `probes/low_mode_patch_run.py`, called through `probes/low_mode_patch.sh` with
`--below 60`: every label mode below 60 cm⁻¹ in either functional is re-measured in both. 6-31G* with Cartesian d functions
(`corpus/analytic_hessians.py:227`), the labels' unpruned (99,590) grid (`probes/butterfly_scan.py:50`), a largest atomic displacement
of 0.01 bohr (`vibrations.py:31`), pyscf 2.15.0. Two settings differ from the labels': a displaced point converges to 1e-9 in the
energy and 1e-7 in the orbital gradient where a label converges to 1e-11 (`analytic_hessians.py:95-96, 237`), and the labels were made
with pyscf 2.14.0, whose analytic Hessians differed from 2.15.0's by at most 0.24 cm⁻¹ on the two molecules compared (obstacle ledger,
entry of 12 November 19:5x).

**The upstream call.** The gradient is `mf.nuc_grad_method().set(grid_response=True).kernel()`
(`probes/hessian_grid_response_fd.py:92-93`). pyscf's own `hessian/test/test_rks.py`, function `finite_diff`, makes the same call to
build its reference Hessian; `probes/hessian_grid_response_fd.py:4-5` cites it.

**Where it writes.** Into `probes/results_m1/low_mode_threshold_2026-11-20/patch_below60/<id>/`. The runner reads `geometry.json` and
the two label files (`probes/low_mode_patch.py:42-49`) and writes only under its out folder: the gradient points, the patched Hessian,
the report and pyscf's log (`probes/low_mode_patch_run.py:103, 111-112, 130, 145, 172-173`). No label file is touched. Run spec:
`probes/runspecs/low_mode_threshold_sample_2026-11-20.json`; 84 gradients and 40 reference SCFs, 6 to 12 hours at 4 threads by an
estimate whose 4-thread factor is assumed, not measured.

## 5. The two-route check

The smallest sampled molecule of each band — B_0c6c144a7f, B_1726105aae, B_0af11315e3, B_1428bc8164 — is patched a second time with a
step of 0.02 bohr into `patch_step02_below60/` (`probes/runspecs/low_mode_threshold_step02_2026-11-20.json`). A point whose patched
frequency differs by more than 0.15 cm⁻¹ between the two steps is flagged and left out of every statistic; the read states how many
points were checked and how many were flagged. The other 16 molecules have no step check.

This checks the finite difference, not the method. The method's only independent check above 20 cm⁻¹ stays the one mode of section 2.

## 6. What is read

`probes/low_mode_threshold_read.py` derives one point per re-measured label mode and functional: the mode's frequency in the label, the
frequency of the patched mode it overlaps most, the signed change, the share of the mode inside the patched space (coverage), and the
Cartesian force constant along the mode in the label (hartree/bohr²). A point with coverage or overlap below 0.9 is listed, flagged,
and left out. Per functional the read prints, by frequency band (20–30, 30–40, 40–50, 50–60, 60–80, 80–100 cm⁻¹) and by quartile of
the force constant: the number of points, the median and largest absolute change, and the fraction above 0.5 cm⁻¹ with its binomial
standard error; and Spearman's correlation of the absolute change with the frequency and with the logarithm of the force constant.

The script ran on synthetic records before this registration was committed (`tests/test_low_mode_threshold_read.py`, 28 tests): a
direction that is an exact mode gives back a constructed change of 2.5 cm⁻¹ to 1e-6; a mixed direction is flagged and counted nowhere;
a mode that turns imaginary is a signed move and is counted; two rotated directions give one point per mode; an empty band is a row
with n = 0; moves that are all zero give an undefined correlation, printed as such; and each outcome of section 7 is reached from
constructed points, the boundaries included.

## 7. The decision rule

Registered population: the **B3LYP** points of the **sample of section 3**, label frequency **20 to 60 cm⁻¹**, coverage and overlap at
least 0.9, not flagged by the step check. With n such points, p the fraction that moved by more than 0.5 cm⁻¹ and SE = √(p(1 − p)/n):

1. **p ≤ 0.20 and p + SE ≤ 0.30.** The B3LYP labels above 20 cm⁻¹ are sound at the 0.5 cm⁻¹ line and the threshold stays. The ωB97X
   moves of section 2 are then a property of that functional's label and get a task line of their own.
2. **p ≥ 0.50 and p − SE ≥ 0.40.** The 20 cm⁻¹ threshold leaves a majority of the soft-mode labels wrong by more than 0.5 cm⁻¹ and the
   trigger must change: to a higher frequency or to the force constant, whichever has the larger absolute Spearman correlation with
   the size of the move on these points. That correlation must exceed 0.4 in absolute value for the quantity to be called a trigger;
   if neither does, the read says that no trigger is named. The size of the re-patch — molecules and hours — is then put to the author
   as a compute decision before anything is patched.
3. **Anything else.** Undecided at this sample size. The next step is the extension: five more molecules per band from the same
   shuffle (`--per-band 10`), not a verdict.

Fewer than 16 points left in the registered population is outcome 3 whatever p is: the binomial standard error is zero at p = 0 and at
p = 1 for any n, so without a floor three unmoved points would read as outcome 1.

**The power of this sample, stated before the run.** 21 points are expected. At p = 0.5 one standard error is 0.11. With 21 points
outcome 1 needs at most 4 moved, outcome 2 at least 11, and 5 to 10 moved is undecided. A true fraction near 0.35 will most likely come
out undecided, and that is a correct reading of 21 points.

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
- Nothing about molecules above 25 atoms, about cations, or about molecules with an imaginary mode (TASKS 215).
- Nothing about whether the patched frequency is the true one beyond the one mode with a second route. Outcome 2 says that label and
  patch disagree by more than 0.5 cm⁻¹ on a majority of soft modes; that the patch is the better of the two rests on B_0f06474656 and
  on the step check.

## 10. If the author chooses `--below 100` instead

The sample then has 36 directions, 144 gradients, 9.6 to 19.1 hours by the same estimate (SAMPLE.md). The registered population and the
rule do not change; the 60–80 and 80–100 bands get B3LYP points, which the table shows and the rule does not read. In both run specs
`--below 60` becomes `--below 100` and `patch_below60` / `patch_step02_below60` become `patch_below100` / `patch_step02_below100` in
the command and in `heartbeat_glob`, with the estimate's hours.
