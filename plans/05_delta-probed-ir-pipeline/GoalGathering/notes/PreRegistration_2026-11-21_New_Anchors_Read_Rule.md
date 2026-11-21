# Pre-registration — the read rule of the new CC anchors: how many small anchors reach 3 cm⁻¹ per family

Registered 21 November 2026, before any new anchor is finished (TASKS 291). The mechanical parts are `probes/new_anchor_read.py`, tested on
synthetic curves with the regime's edge cases (`tests/test_new_anchor_read.py`, 18 cases) before this note was committed. The frozen id
lists are `GoalGathering/notes/new_anchors_2026-11-21/test_ids.txt` and `train_ids.txt`.

## Why

On 21 November 2026 the user rented five CPX62 servers and asked for new anchors, with a principle: train on the smallest molecules that
are proven to reach the goal, and keep it affordable. The plan behind them is count_n167 (TASKS 82). Its count of 167 was read on the DFT
proxy, with the networks of late October, on randomly drawn molecules; the plan prices the cheapest molecules instead, which were never
measured. Real CC labels can now answer the question itself: does the network, fine-tuned on k small CC anchors, predict CC-level band
positions of molecules it did not train on within 3 cm⁻¹ per family, and from which k?

## The design

**Labels.** Every anchor on the composite tier: CCSD(T)/cc-pVDZ FD Hessian plus the MP2 basis step [MP2/cc-pVTZ − MP2/cc-pVDZ]
(`probes/dfmp2_anchors.sh`, density-fitted MP2, adopted 20 Oct 2026), at the molecule's B3LYP/6-31G* geometry, carried in the anchor
registry (`m05/anchor_registry.py`) with its checks passed (VALID; the energy route as the second route). An anchor without its MP2 step,
or with a check that failed, is not read. Tiers are not mixed (the registry refuses).

**Test anchors, fixed now.** The 11 anchors carried before 21 Nov (benzene … anthracene) and every new anchor whose id's sha1 is divisible
by 5 (`new_anchor_read.is_test`): 49 molecules, 38 of them new. Nothing about size, cost or a result chooses them. A test anchor is never
trained on, at any milestone.

**Training anchors.** The plan's other 122 molecules. At milestone k the training set is the k cheapest training anchors finished at
read time, by `anchor_plan.anchor_hours` — the user's principle, smallest first.

**Milestones.** k = 20, 40, 60, … and all training anchors finished (`new_anchor_read.milestones`). Each read uses every test anchor finished
at that time; the test set grows as the waves finish, and each read names how many of the 49 it holds.

**Network and fine-tune.** The carried measurement networks at read time (v1.4 today, three seeds; decision 66: measurement networks
measure), read from `modules/MODELS.md`, never from memory. The fine-tune is R2 (`body1_es`: the whole head, α and the body's last
interaction block; 85 % of the k training anchors fitted, stopped on the other 15 % with patience 10, best epoch restored, cap 120
epochs), the recipe the anchor count of 29 Oct chose for the CC step. It must be added to `m05/rungC_cc_transfer.py` as a fit mode, with a
test, before the first read; until it is, there is no read (no fallback to another mode).

**Quantity.** Per family (ring-ip, CH-stretch, CH-oop, other; the rule of `m05/learning_curve_layerA.py`), the rms over the test anchors'
bands of the corrected band position against the composite CC position: the seeds' mean ΔH added to the B3LYP Hessian and diagonalised,
each band paired to its CC band by mode overlap and counted in the family of its B3LYP partner — the quantity decision 65's licence reads.
Reported with its 95 % interval from a bootstrap over molecules.

**Beside it, read and not judged.** The zero rule (B3LYP alone), the proxy model without a fine-tune, and the per-class α scaling fitted
on the same k (the transfer without a network). The size read-out: the test anchors in the largest quarter by atoms, separately, with
their count. No anchor has more than 24 atoms (anthracene), so this read-out says nothing about larger molecules; their accuracy rests on
the proxy's size test (7.9 cm⁻¹ on four molecules of 36–60 atoms).

## The rule (`new_anchor_read.decide`, on each family's seed-mean error per milestone)

- **NO READING** — a family missing, the families read at different milestones, fewer than two milestones, or a value not finite.
- **REACHED at k** — every family ≤ 3.0 cm⁻¹ at k and at the next milestone.
- **NO LEARNING** — a family's last value is not below the proxy model as it is.
- **FLAT** — every family above 3.0 cm⁻¹ gained less than 0.1 cm⁻¹ over its last two milestone steps.
- **FALLING** — otherwise: a family above the line is still falling.

## What each outcome means

- **REACHED at k:** the anchors needed are the k cheapest training anchors. New waves stop; the anchors already running finish (their
  cost is spent) and join the release model's training data; they are not a reason to read again. The price of the goal is the CC and MP2
  cost of those k, from the servers' logs.
- **FALLING:** the waves continue in the plan's order; the next read at the next milestone.
- **FLAT:** more anchors of this kind do not buy the remaining families; the waves stop after the running molecules, and the lever is the
  network's input for those vibrations (TASKS on the 'other' family), not more CC.
- **NO LEARNING:** the fine-tune does not transfer; the waves pause and the recipe is examined before more money is spent.
- **NO READING:** fixed and read again; no decision is taken on it.

## Predictions (written before any new anchor exists)

Ring-ip and CH-stretch reach the line by k = 40. CH-oop reaches it later than on the proxy's count, or not by 122, because the cheapest
molecules carry fewer ring contexts than the random draws. 'Other' is the family that decides between REACHED and FLAT.

## Order and cost

Wave 1 (32 molecules, 6 of them test anchors) runs since 21 Nov 20:56; the DFT step for the other 128 since 21:20, then their waves. The
MP2 step for each finished anchor follows on the servers or the laptop. The first read is possible at 20 training anchors with their MP2
steps; by the anchor plan's hour rule that is several days into wave 1 and the waves after it. Every read is a script over the records
(no judgement), its output kept beside this note.
