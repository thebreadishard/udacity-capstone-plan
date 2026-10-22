# Design and pre-registration — the few-anchor transfer checked on hundreds of molecules (21 Oct 2026; the user's item 2)

*Written 06:5x as a desk design; rewritten 07:3x after the user's question why a third level would be needed ('Waarom denk je dat er een
derde niveau nodig is?') and their choice ('doe (a) en (b) vóór de kationrun'). Registered before any fine-tune of this check runs.*

## The question

Set three's diagnosis (`Diagnosis_2026-10-21_Set_Three_Read.md`, exploratory) found that fine-tuning the whole head on a few CC anchors
halves the held-out error, where the last layer alone could not even fit the anchors. That rests on eleven anchors, and the protocol was
chosen on them. The general question: **does a base model that learned one correction move to another from k labelled molecules, which
part of the network has to move, and how many molecules does it take?** Read on hundreds of held-out molecules, it gives the T3 transfer a
test the CC anchors cannot give before July 2027 (decision 63), and the curve along k says how many CC anchors a target would need.

## No third level is needed

The first version of this note said a second correction had to be computed (xTB or a third DFT). That was too quick: what the question
needs is a base that learned something *other* than the target. The target can stay the corpus's own ωB97X − B3LYP correction, of which
601 molecules have analytic labels. Two such bases are built from the data we have:

- **Arm (a), a different correction.** The base trains on the corpus label with each mode family's diagonal block (low level's mode
  basis) multiplied by the CC correction's measured relation to the proxy: per family the median, over set three's anchors, of the slope
  of the CC correction's first-order shifts on the proxy's (`out/set3_diagnosis_2026-10-21/decompose.json`: ring-ip −0.34, CH-stretch
  −0.79, CH-oop −0.43, other −1.16; the median correlations are +0.46, −0.28, −0.38, −0.31). It is then fine-tuned on k molecules with the
  true label. As in the CC case, the base has seen the molecules' inputs (with its own label); the distortion keeps the measured slopes
  but not their scatter, so within a family the two corrections are exactly anti-aligned — harder than the CC case on ring-ip, comparable
  out of plane. Switch: `rungC_train.py --family-scale` (tests: `tests/test_rungC_family_scale.py`).
- **Arm (b), a new domain.** The base trains without layer A2 (the substituted fused-ring children) and is fine-tuned on k A2 molecules
  with the same correction it learned. This is transfer to molecules it never saw, without a change of correction.

Both bases use chain 34's recipe (read from its record) on chain 34's own pool — the base the CC transfer used; arm (b) drops the A2
molecules from it. Three seeds each.

## The check

`m05/proxy_transfer_check.py`, one run per arm, base seed and k; planned by `probes/proxy_check_plan.py`. Per draw of k molecules from the
arm's reservoir, four models are read on every molecule of the arm's read set: **head_l2** (last layer + α with the pull λ = 1, set three's
registered protocol), **head** (the same at λ = 0), **head_all** (every head layer + α), **scratch** (the base's own recipe trained on the
k molecules alone, true label — what the base is worth against no base). The zero rule and the base as it is are read beside them. A
fine-tune takes 3000 optimiser steps whatever k (epochs = ⌈3000 / k⌉; at k = 10 that is set three's 300 epochs).

| | arm (a) | arm (b) |
|---|---|---|
| reservoir (hash order) | the first 200 eligible molecules | the first 40 eligible A2 molecules |
| read set | the other eligible molecules | the other eligible A2 molecules |
| k | 5, 10, 20, 50, 100, 200 | 5, 10, 20, 40 |
| draws per k | 3 (1 at the full reservoir) | 3 (1 at the full reservoir) |

Eligible = admitted molecules of layers A, A2, B with analytic labels for both functionals. Read-outs per read molecule: corrected-ω rms
per family; matched intensity error where its B3LYP APT exists (both truth and prediction with that APT, so it measures mode shapes).

**The split** (`probes/proxy_check_plan.py split`, 21 Oct 09:26; `out/proxy_check_2026-10-21/manifest.json` and the id files there):
543 eligible molecules, 67 of them A2. Arm (a): reservoir 200, read set 343; its base's pool is chain 34's 750 exactly (none missing,
none extra; 222 molecules of today's pool excluded). Arm (b): reservoir 40, read set **27** — fewer than planned (the A2 molecules with
analytic labels), so arm (b)'s reads carry wider errors; its base's pool is 607 (chain 34's without its 143 A2 molecules). Family scales
of arm (a): ring-ip −0.34, CH-stretch −0.79, CH-oop −0.43, other −1.16.

## Lines (read by `probes/proxy_check_plan.py read`; standard errors over seeds × draws; 'below' = lower by more than twice the combined standard error)

- **L1, the protocol.** Per arm: at k = 5, 10 and 20, is head_all below head_l2 on CH-oop? **Holds** for the arm when it is at two of the
  three.
- **L2, the base's worth.** Per arm and k: is head_all below scratch on CH-oop? The read names the largest k at which it is.
- Reported, no line: 'other' and the matched intensity by the same comparisons; every column along k; head (λ 0) beside them.

## Predictions

- **(a)** L1 holds: a last layer pulled to the base cannot reverse a family block's sign (the diagnosis' in-sample result). L2: the base
  helps at least up to k = 50 — its body's features are right even where its correction is not.
- **(b)** L1 is uncertain, and I predict it does **not** hold: the correction is the one the base learned, so the last layer may suffice.
  L2: the base helps at every k.
- If (a)'s L1 fails, the diagnosis' protocol result was specific to the eleven anchors and the registered λ = 1 protocol stands.

## Order and cost

The laptop alone, after set three's whole-head repeat (ends about 09:30). One chain: base (b), base (a), the registry entries (status
`candidate`, never a production model), then the fine-tunes, arm (b) first. Base time: chain 34's three seeds took 3.3 h at 750 molecules.
The fine-tunes are timed on their first run before any end time is stated. Peak memory: the trainer's 7.7 GB (chain 41, n = 978) bounds
the bases; nothing runs beside them. The cation restart (P3-2) follows the chain. No paid compute (decision 63, spending pause).

## Amendment (21 Oct 2026, 14:0x, before any fine-tune ran) — molecules without an intensity read-out

At 13:44 the chain stopped in base (a)'s own hold-out read, after seed 0 was trained and saved: for one hold-out molecule the distorted
base's prediction moved a soft mode across the vibrational threshold (60 modes in the truth, 59 in the prediction), and the intensity
read-out raised. With the 'other' block scaled by −1.16 this was to be expected, and it would equally have stopped the check's read of the
base as it is. From now on such a molecule has no intensity read-out for that prediction: the reason is recorded per molecule and counted
per column ('no intensity' in the read's table), the intensity is the mean over the molecules that have one, and every other error still
stops (commit 6938cf33, `tests/test_mode_crossing.py`). The lines read CH-oop and are untouched; intensity stays reported, no line. Base
(a) is trained again from seed 0 (the step does not resume within its seeds).

## Outcome

### 22 Oct 2026, 02:1x — the read

`python probes/proxy_check_plan.py read modules/05_support_predictor/out/proxy_check_2026-10-21` → `proxy_check_read.{json,md}` there
(records git-ignored, mirrored to capstone-data). Chain PX 21 Oct 09:27 – 22 Oct 02:11, 33 steps (one stop and relaunch, 13:44, recorded
above). Means ± standard error over seeds × draws; CH-oop and 'other' in cm⁻¹, intensity the matched relative rms.

**Arm (a), a different correction — L1 holds, as predicted** (the whole head below λ 1 at k = 5, 10 and 20). **L2: the base helps up to
k = 100.** The base as it is reads 31.50 on CH-oop (the zero rule 21.90): it learned the distorted correction. Along k, CH-oop:

| k | λ 1 (head_l2) | λ 0 (head) | whole head | scratch |
|---|---|---|---|---|
| 5 | 9.05 ± 0.31 | 5.90 ± 0.18 | 6.55 ± 0.19 | 7.33 ± 0.31 |
| 10 | 8.44 ± 0.31 | 5.22 ± 0.08 | 5.08 ± 0.16 | 6.27 ± 0.13 |
| 20 | 8.09 ± 0.25 | 5.37 ± 0.07 | 4.04 ± 0.14 | 5.38 ± 0.17 |
| 50 | 9.45 ± 0.28 | 4.71 ± 0.05 | 3.81 ± 0.14 | 4.76 ± 0.16 |
| 100 | 9.18 ± 0.29 | 4.85 ± 0.10 | 3.17 ± 0.08 | 3.41 ± 0.08 |
| 200 | 9.90 ± 0.56 | 4.80 ± 0.17 | 2.82 ± 0.04 | 2.79 ± 0.09 |

'other' and the intensity follow the same order (whole head at k = 200: 'other' 3.32, intensity 0.20; λ 1: 12.86, 0.54). Read beside
the lines, not a line: λ 1 does not learn at all along k (8–10 throughout) — the pull toward the base holds the network on the wrong
correction; the last layer free (λ 0) learns quickly but levels off near 4.8; the whole head keeps falling and is the only column that
does at k ≥ 50. At k = 5 the free last layer is ahead of the whole head (5.90 against 6.55). The 'no intensity' column counts molecules
whose prediction moved a mode across the threshold: most under λ 1 (≈ 12 per read), 4 per read for the others.

**Arm (b), a new domain — L1 does not hold, as predicted** (the whole head below λ 1 only at k = 20). **L2: the base helps up to k = 20.**
The base as it is reads 2.66 ± 0.24 on CH-oop of the 27 A2 molecules it never saw (zero rule 22.76): the correction it learned carries to
the new family, and fine-tuning adds little (whole head 2.72 → 2.24 from k = 5 to 40; λ 1 2.73 → 2.66). Scratch needs k = 40 to come
near (2.85 ± 0.35). 27 read molecules: the errors are wider than arm (a)'s.

**What it says.** Where the correction changes (a), how the network is fine-tuned decides the outcome, and the registered protocol of set
three (λ = 1) is the one that cannot follow: it stays where the base put it. The whole head follows and keeps improving with more molecules.
The pretrained base saves most at few molecules — the whole head at k = 20 (4.04) is below scratch at k = 50 (4.76) — and the saving
shrinks with k: at k = 100 the two differ by 0.24 (3.17 against 3.41), at k = 200 they are level (2.82 against 2.79). *(Corrected 02:2x:
the first wording claimed 'about half the molecules' at k = 50 too, where the whole head's 3.81 is above scratch's 3.41 at k = 100.)* Where only the molecules change (b), the base already carries and the protocol hardly matters. This is the
independent support set three's repeat could not give: hundreds of molecules, a protocol chosen before the read. Within its limits: one
distortion (the median slopes, exact anti-alignment per family), one held-out family for (b), proxy-level labels.
