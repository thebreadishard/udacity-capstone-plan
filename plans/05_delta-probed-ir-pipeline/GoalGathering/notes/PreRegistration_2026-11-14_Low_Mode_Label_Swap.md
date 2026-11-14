# The repaired low modes become the corpus's labels — registered before the swap

**Written 14 November 2026, before any label file is touched.** The decision is the user's, this morning: *"Als de gerepareerde
lage-modus-Hessianen kwalitatief beter zijn dan wat we hadden, moeten ze labels van het corpus worden"*, under the rule that the
pipeline carries every quality-raising lesson (CLAUDE.md, *Improvements reach the end product*). TASKS 201.

## 1. What is being swapped, and what is not

For each of the 58 corpus folders the repair selected (`probes/results_m1/low_mode_patch_2026-11-13/ids_below20.txt`), both analytic
label files `hessian_b3lyp_analytic.npz` and `hessian_wb97x_analytic.npz` get the patched `H_raw`, `H_projected` and `freq_cm` from
`probes/low_mode_patch_run.py`. Every other entry of the label file — `energy`, `grid`, `charge`, `spin`, `reference` — is carried over
unchanged, because the patch changes a Hessian, not the SCF it came from. The provenance of both the original and the patch is written
into the new file.

Untouched: the 874 folders the repair did not select, the geometries, the dipoles and APTs, and the finite-difference deck. In
particular the **34 molecules whose lowest mode lies below −20 cm⁻¹ keep their imaginary mode**: there the negative frequency is a
geometry that is no minimum of that functional, not quadrature noise, and this swap makes no claim about them (TASKS 215).

## 2. Why the patched Hessian is the better label

- The error being removed is known and measured: pyscf's CPU DFT Hessian carries no grid-weight derivatives, which moves modes below
  ≈ 20 cm⁻¹ by up to 6 cm⁻¹ and modes above it by under 0.5 cm⁻¹ (TASKS 201 step 2, ledger 12 November).
- The repair's own second route passed: on B_0f06474656 the patched Hessians give 15.82 / 58.02 cm⁻¹ against the full finite-difference
  reference's 15.69 / 57.98, with every other mode within 0.43 cm⁻¹ (ledger 12 November).
- The modes below 20 cm⁻¹ hold ≈ 82 % of the estimated label noise of family 'other' (rms 1.99 → 0.84 without them).

## 3. The acceptance criteria, registered before the numbers are read

A molecule is swapped only if all four hold; one that fails any of them is reported and left alone, and the run says so.

1. **Nothing moves above the threshold.** Every vibrational mode above 20 cm⁻¹ moves by at most **2.0 cm⁻¹**. The measurement on
   B_0f06474656 gave ≤ 0.43; 2.0 is the refusal line, chosen before reading the 58, and the largest change seen is recorded.
2. **Nothing turns imaginary.** No mode that was real becomes negative.
3. **The two files describe the same calculation.** Same `grid`, same number of frequencies, same Hessian shape.
4. **The patch used the registered settings.** `below_cm` = 20.0 and the step the repair recorded.

## 4. What is expected, so that a surprise is visible

The eight molecules whose lowest mode lies between −20 and 0 cm⁻¹ lose their imaginary mode and return to the training set, as
D_ac28161d06 already did (−7.48 → +7.05 cm⁻¹); so do any of the four selected molecules below −20 whose other label was the one in the
window. Up to twelve molecules therefore return. 'other''s estimated label noise rms falls from 1.99 toward 0.84 cm⁻¹. No family's
target rms is expected to change by more than the label noise itself.

## 5. What the swap costs in comparability

v1.4 will train on labels that differ from the ones chain 41 and chain 42 trained on, and on a slightly larger set. Any comparison that
crosses the swap names it; the carried-model record gets the swap's date and record file, so a later reader can tell which labels a
checkpoint saw.

## 6. How it is verified, and how it is undone

`probes/low_mode_swap.py` writes a record per molecule — the lowest mode before and after, the largest change above the threshold, and
the sha256 of the file before and after — and moves every original to `modules/05_support_predictor/corpus/superseded_2026-11-14/`,
from which the swap can be reversed file by file. Afterwards `probes/low_mode_coverage.py` is re-read: the band table must show the
0-to-20 band empty of selected molecules that still carry an imaginary mode, and the count of molecules with an imaginary lowest mode
must fall by the number the record claims.

## 7. Amendment, 08:3x on 14 November, after the dry run and before any label moved

The dry run (`probes/low_mode_swap.py --dry-run`, record `probes/results_m1/low_mode_swap_2026-11-14/swap_dry_run.json`) refused seven
files. Reading them showed that **criterion 1 measured the wrong thing**, so it is replaced here, with the reason, before any file is
swapped. The new form is stricter about what it was meant to catch and silent about what it was never meant to catch.

**What the dry run showed.** In every refused file exactly one mode moved — the molecule's own lowest, at 62.61, 55.42 or 51.03 cm⁻¹ —
and every other mode moved by at most 0.37 cm⁻¹. That one mode is the mode the repair exists to correct: the merged direction set gives
a functional the low direction of *either* label, so a molecule whose B3LYP mode is below 20 cm⁻¹ is patched along the same direction
in ωB97X, where that mode sits higher. Criterion 1 bounded every mode above 20 cm⁻¹, which includes exactly those, so it refused the
repair for being a repair.

**The counter-evidence.** For B_0f06474656 the registered second route of 12 November is a full finite-difference grid-response
Hessian: **57.98 cm⁻¹** for that ωB97X mode. The analytic label says 55.42 and the patch says 58.02. The patch is right by the only
independent reference we have, and criterion 1 as written refused it.

**Criterion 1 is replaced by 1a and 1b.** With *k* the number of directions the repair patched in that file:

1a. **Collateral damage is bounded.** All but the *k* largest mode changes stay within **0.5 cm⁻¹** — the bound the 12 November
    measurement actually supports for modes the patch does not target.
1b. **Only the patched modes move.** At most *k* modes change by more than that bound. A file where more modes move is refused:
    the patch has disturbed something it did not target, or a mode has crossed a neighbour, and either way it needs reading first.

The *k* patched modes themselves carry no bound. A bound on them would be a bound on the size of the error we are correcting, which is
the quantity we do not know in advance; their changes are listed one by one in the record instead.

**Criterion 2 is narrowed in the same way.** A *patched* mode that turns imaginary is accepted and flagged, not refused: if the better
Hessian says the mode is imaginary, the honest consequence is that the molecule leaves the training set, which is the trainer's own
rule (`m05/rungC_train.py`, molecules with an imaginary mode dropped). Refusing the patch there would mean keeping a label we believe
is wrong because we dislike what it costs. A mode that turns imaginary and was *not* patched still refuses the file.

**One molecule is known to leave by this.** B_84485091e3's B3LYP lowest mode goes 4.685 → −3.527 cm⁻¹, so it drops out of training
where it is in today. Expected count, written before the run: up to twelve molecules return, one leaves.

**What this amendment does not do.** It does not move the 20 cm⁻¹ selection threshold, and it makes no statement about molecules the
repair never selected. The dry run raised a question about that threshold — a 62 cm⁻¹ mode moving 6.72 cm⁻¹ means the error is set by
how soft a mode is, not by its frequency alone — and that question is TASKS 218, to be measured on its own, not settled here.
