# Pre-registration — the anchor count under the change the anchors measured, with a control read against each base's own start

29 October 2026, 10:4x. Written before any run of this test, after the recipe follow-up's read (ledger 29 Oct 04:4x; TASKS 82; the user,
29 Oct: 'Doe de nieuwe proef met de betere check'). Code: `probes/anchor_count_plan.py` (plan, read); tests `tests/test_anchor_count_plan.py`
(synthetic records, every outcome, the input gate's refusals). No new library call: the fine-tunes are `m05/proxy_transfer_check.py`'s
modes as the follow-up ran them; only the epoch cap changes.

## Why

The follow-up (`PreRegistration_2026-10-28_Anchor_Price_Recipe.md`) gave no reading: its CH-stretch control G failed once under each
recipe. Its registered meaning — the arms differ by more than the distortion — does not hold in their inputs, checked 29 Oct 04:4x:
base (a2)'s trainer command differs from base (c)'s only by the distortion flags, both substitute 862 analytic labels on a pool of 750,
and CH-stretch's factor is −0.79 in both. G compared the two arms' fine-tuned CH-stretch directly, so it also counted what the other
families' distortion does to CH-stretch inside the shared body and head already in the bases. That is a property of the base, not of
the fine-tune, and a control on the fine-tune must subtract it.

Outside that registration, the early-stopped recipes brought arm (c)'s CH-oop at k = 200 under 3 cm⁻¹ (R1 2.73 ± 0.08, R2 2.88 ± 0.18;
R0 3.33 ± 0.03), and at k = 100 they changed nothing beyond twice the combined se. This test reads the anchor count itself — where arm
(c)'s CH-oop curve crosses 3 cm⁻¹ between 100 and 200 — under a control that a leak through the base cannot fail.

## The design

**The input gate** (mechanical, `plan` refuses to write the chain otherwise): base (a2)'s and base (c)'s trainer commands (their chain
files) differ in exactly the distortion flags (`--family-scale` with its value for (a2); `--distortion-file` with its path for (c));
both base logs state the same number of substituted analytic labels; CH-stretch's factor is the same in both (arm (c)'s mean and rest
equal arm (a2)'s family scale).

**Recipe.** R2 (`body1_es`: the whole head, α and the body's last interaction block, fitted on 85 % of the k molecules, stopped by the
loss on the other 15 % with patience 10, the best epoch restored), chosen by the follow-up's registered rule — the lower mean
validation loss of R1 and R2 for arm (c) at k = 200 (R2 0.0538, R1 0.0574; never the read set). The cap rises from 60 to 120 epochs:
one of arm (c)'s three R2 runs at k = 200 kept an epoch within 10 % of 60, which decision 51 answers with a higher cap. R1 (`head_all_es`)
and R0 (`head_all`, 3000 steps) run beside it for arm (c), reported and not judged; R1 under the same cap.

**Arms.** (c) = arm (c)'s base (`out/anchor_price_2026-10-28/base_c_model_n750_seed{0,1,2}.pt`); (a2) = the follow-up's base
(`out/anchor_recipe_2026-10-28/base_a2_model_n750_seed{0,1,2}.pt`), under R2 only. Neither is v1.3's file.

**Draws.** The proxy check's reservoir (200) and read set (343); k = 100, 120, 150, 170 (three draws each, `draw_subsets`) and 200 (the
whole reservoir); seeds 0–2. Chain AC, 30 steps (two arms × five k × three seeds).

## Lines (read by `anchor_count_plan.py read`; mean ± se over seeds × draws; 'above' = higher by more than twice the se)

- **G′ — the control against each base's start:** per run, d = its fine-tuned CH-stretch minus its own base's as it is (the record's
  'none' read, the same seed's base). G′ fails at a k when arm (c)'s d is above arm (a2)'s by twice the combined se (arm (c)'s fine-tune
  improves CH-stretch less, or harms it more, than arm (a2)'s). G′ holds when it fails at no more than one of the five
  k (if the arms truly agree, a one-sided 2-se test at five k fails one by chance in about one in nine).
- **Cap:** binds when more than a third of arm (c)'s R2 runs at a k keep an epoch ≥ 108 (within 10 % of 120).
- **N — the count:** the smallest k at which arm (c)'s R2 CH-oop curve (k = 100 … 200) reaches 3.0 cm⁻¹, interpolated in log k
  (`anchor_price_plan.crossing`); reported with the crossings of the mean ± se curves as its range, and per family.

**Outcome:** **no reading** (G′ fails at two or more k); else **undecided: the cap binds** (the cap binds at any k); else **count N**
(the curve crosses by 200; '≤ 100' when it is already at the line at 100) or **above 200** (no crossing).

## Predictions

- G′ holds: the CH-stretch gap between the arms is in the bases, and the fine-tune adds none.
- The cap does not bind at 120.
- Count N between 140 and 190 under R2 (the follow-up's R2 points, 3.49 at 100 and 2.88 at 200, cross in log k near 175; its R1
  points near 150); R1 crosses earlier than R2 on the read set.
- R0's curve does not cross by 200.

## What each outcome means for claim 3

- count N → the anchor plan is priced on N anchors with every ring context (arm (c)'s C1: a cell cover does not beat random draws),
  fine-tuned by R2 with the 120-epoch cap; R2 replaces 'head_all, 3000 steps' as the fine-tune of the CC step.
- above 200 → arm (c)'s 'more than 200' stands under the best recipe found; the anchor plan prices more than 200 or narrows the claim.
- undecided: the cap binds → the cap is raised again before anything is priced.
- no reading → the fine-tune itself treats the arms differently; that is found before any price is read.
- Limits stated now: one reservoir of 200 and one read set; the draws at 150–200 overlap strongly, so their se understates the spread
  of a fresh anchor set; k = 100 and 200 repeat the follow-up's draws and seeds (only the cap changed), so the new information is the
  three interior k and the control; the proxy carries only the change measured on nine anchors.

## Order and cost

Laptop only; nothing runs beside it. By the follow-up's step times (corpus load ≈ 3 min per step; R1 + R2 ≈ 3.7 min per draw at
k = 100, R0 ≈ 1.2 min) and per-epoch time growing with k: ≈ 7 h. Memory: the follow-up's bound, 7.7 GB. Read the day it ends.

## Amendment 1 — 29 October 2026, 10:4x, before any run: G′ replaced by a repeat control

**Why.** The reader's smoke on the recipe follow-up's records (format only, k = 100 and 200; `scratchpad/smoke_count_read.py`) showed
that G′ cannot measure what it was written for. Each base as it is sits about 78 cm⁻¹ from the true CH-stretch correction (the
follow-up's 'base as is' rows: arm (c) 77.44, 78.40, 77.71; arm (a2) 77.95, 78.18, 77.92), because CH-stretch's factor −0.79 leaves a
fifth of its correction. A change from the base is therefore a change of about −75 cm⁻¹ in both arms, and the bases agree there to
0.2 cm⁻¹ — so the follow-up's CH-stretch gap after fine-tuning (+0.36 to +0.65 at k = 100) is not in the bases. It arises in the
fine-tune: arm (c)'s fine-tune must also undo the other families' larger, context-dependent distortion with the same shared parameters.
That is the measured change's own cost, not a difference between the arms' inputs, and no read of the fine-tuned models can tell the
two apart. The registration's reasoning in 'Why' (the gap 'already in the bases') is wrong on this evidence.

**What replaces it.** The count reads arm (c) alone; arm (a2) is its reference, not its control. The arms' inputs are checked by the
input gate (passed at 10:40: 862 analytic labels in both, CH-stretch factor −0.79 in both, the commands equal but for the distortion
flags and the prefix). A difference in the pipeline itself is caught by:

- **R — the repeat control:** at k = 100 each arm's R2 read repeats the follow-up's R2 read (the same draws, seeds and bases; the cap
  60 → 120 touches no run there: every follow-up R2 run at k = 100 stopped by its patience, after at most 57 epochs): no family's mean differs from the
  follow-up's by more than twice the combined se, in either arm.

**Outcome** (replacing the original's): **no reading** (R fails); else **undecided: the cap binds**; else **count N** or **above 200**,
as registered. Reported beside the count, not judged: arm (a2)'s crossing per family (what the measured change costs in anchors
against one factor per family), the CH-stretch gap between the arms at every k, and both bases as they are.

**Predictions** (G′'s removed, the rest unchanged): R holds; arm (a2)'s CH-oop crossing below arm (c)'s.
