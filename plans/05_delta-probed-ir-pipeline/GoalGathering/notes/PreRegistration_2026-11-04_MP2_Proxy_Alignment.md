# Pre-registration, 4 November 2026, 23:1x — MP2 against ωB97X as the stepping stone, on the eleven anchors (TASKS 11 (c))

The user, 4 Nov 2026: 'Pak (c) maar op.' Written before any shift of this check was computed. What was seen beforehand: the anchors' file
inventory (every composite names complete MP2/cc-pVDZ and MP2/cc-pVTZ rows; benzene's test-1 rows are complete) and, from a structure check that
printed no shift, the modes per family (CH-oop 79 over the eleven anchors, 'other' 131, ring-ip 183, CH-stretch 75).

## Why

The network learns the correction from B3LYP to CCSD(T) in two steps. It first pretrains on a cheap 'stepping stone' that thousands of molecules
can afford, ωB97X − B3LYP, and the few CC anchors then tune it. The anchors are the expensive part: the count of 29 Oct (TASKS 82, the ledger of 29 Oct 18:1x)
put 167 of them on the way to 3 cm⁻¹. They have the most to correct where the stone points the wrong way. For CH-oop the CC correction is a mean shift of the opposite
sign to ωB97X's (TASKS 89, 22–23 Oct), and 'other' is still unlicensed under decision 65. A stone that follows CC more closely would leave the
anchors less to do. MP2 is the registered candidate (`Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md`, registration 2). It was parked on
6 Oct for its price, not for its quality, and re-opening was tied to 'other' not moving with the analytic labels, which it did not.

This check is the free first step: it trains nothing and computes nothing new.

## What is compared

Per anchor, in the low level's mode basis (analytic B3LYP/6-31G*, mass-weighted, translations and rotations projected), the first-order shift
K_kk = (Vᵀ ΔH_mw V)_kk / 2ω_k of each mode k under four corrections ΔH = H − H_B3LYP:

- **CC**, the truth: the carried TZ anchor of the anchor registry (nine composites CC/DZ + [MP2/TZ − MP2/DZ], benzene's full CC/TZ anchor);
- **ωB97X/6-31G***, the current stone (the corpus's analytic Hessian);
- **MP2/cc-pVDZ**, the main candidate (frozen core, the rows the composites were built from: pyscf conventional MP2 for the 7 Oct anchors,
  DF-MP2 psi4 for set three's);
- **MP2/cc-pVTZ**, reported beside it.

MP2/cc-pVDZ is the main candidate for two reasons. An affordable stone for the pool would be MP2 in a double-zeta basis (6-31G*, the pool's
basis; the 6 Oct price). And for the nine composites, CC − MP2/TZ equals CC/DZ − MP2/DZ exactly: MP2/TZ shares the composite's basis step by
construction, so its agreement with the truth is partly built in. Benzene's full CC/TZ anchor is the one clean TZ comparison.

Shifts by `probes/set3_decompose.py`'s `shifts`, families by the corpus rule (`probes/e8_cc_locality.py`), MP2 Hessians assembled by the code
the composites were built with (`cc_composite_full_check.mp2_rows_frame`, split out of `build` tonight; three stored composites rebuilt from it
are equal to the bit).

## The read (`probes/mp2_proxy_alignment.py`, tested first on synthetic records: `tests/test_mp2_proxy_alignment.py`, 7)

Per family, pooled over the anchors that have modes of it, per candidate: the correlation of the CC shifts with the candidate's, the least-squares
slope of CC on the candidate, the rms of the CC shifts, the rms of CC − candidate, and **the rms of CC − s·candidate with s fitted on the other
ten anchors** (leave one anchor out; one factor per family, as the anchors tune the head). A family with fewer than 3 anchors or 10 modes is not
read.

**Line, per family, on that last rms:** MP2/cc-pVDZ over ωB97X ≤ 0.8 → *MP2 follows CC better*; ≥ 1.25 → *MP2 follows CC worse*; between →
*no clear difference*. The family that decides is **CH-oop**, then **'other'**. Ring-ip and CH-stretch are read the same way. MP2/cc-pVTZ is
reported and not judged.

**What each outcome means for the plan.**
- *Better in CH-oop or 'other':* the parked step 1 of the stepping-stone registration is re-proposed to the user, priced. That step is MP2/6-31G*
  labels on the 46 parents (≈ 110 h of one 8-thread lane, ≈ €30 on the labels CCX53 at the 6 Oct price) and a network pretrained on them, read
  by T3 against the ωB97X-trained one. For planar molecules the out-of-plane block can be computed alone (the repair-oop route), which is cheaper.
- *No clear difference or worse in both:* nothing changes. The stone stays ωB97X, and the lever for CH-oop and 'other' lies elsewhere (the
  input design, TASKS 23).
- Either way this check does not license anything and does not touch a carried model.

**What it does not show.** First-order shifts in B3LYP's modes, not frequencies after diagonalisation; a check on eleven anchors of 12–24
atoms; MP2 at cc-pVDZ, not at 6-31G* (the pool's basis, which no anchor has). MP2's known over-softening of some arene out-of-plane modes in
larger bases is part of what the CH-oop read sees, and the cc-pVTZ column beside it shows whether the basis makes it worse.

## Predictions (before any number)

- CH-oop: MP2/cc-pVDZ follows CC better than ωB97X: **one in three** (5 Oct: 'CH-oop does not', for MP2's out-of-plane weakness).
- 'other': better: **one in two**.
- ring-ip and CH-stretch: better: **two in three** each (5 Oct: 'improve by ≥ 30 %').

## Outcome (4 November 2026, 23:2x; `probes/results_m1/mp2_proxy_alignment_2026-11-04/`)

Scaled rms (CC − s·candidate, s fitted on the other ten anchors), ωB97X / MP2/cc-pVDZ / MP2/cc-pVTZ, cm⁻¹: CH-oop 13.73 / 10.17 / 13.61 (79 modes, CC rms 17.78); 'other' 13.10 / 11.11 / 14.73 (131, 17.56); ring-ip 16.01 / 15.07 / 16.94 (183, 16.02); CH-stretch 2.52 / 2.27 / 2.16 (75, 34.38). MP2/cc-pVDZ over ωB97X: CH-oop **0.74 → better**; 'other' 0.85, ring-ip 0.94, CH-stretch 0.90 → no clear difference. **By the registered line, MP2/cc-pVDZ follows CC better than ωB97X in CH-oop and makes no clear difference in the other three families.** Predictions: CH-oop better, one in three, happened; 'other' better (one in two), ring-ip and CH-stretch better (two in three each) did not. The 5 Oct expectation, MP2 helping in-plane and not out of plane, came out the other way round.

Read beside it, not a verdict (`probes/mp2_proxy_per_anchor.py`, `per_anchor.txt`): in CH-oop ωB97X shifts every anchor's modes up by +18 to +24 cm⁻¹ on average, where CC moves them down by up to −22 (fused rings) or leaves them near zero (benzene, pyridine, fluorobenzene). MP2/cc-pVDZ moves them down by −37 to −84, the right sign and the same rise with ring fusion, at three to five times the size (own slopes +0.01 to +0.29): MP2's known over-softening of arene out-of-plane modes in this basis. The leave-one-out residual of MP2/cc-pVDZ is below ωB97X's on all eleven anchors in CH-oop. The margin to the line is small (0.74 against 0.8). MP2/cc-pVTZ correlates best (+0.97) but changes sign between the small and the fused anchors, so one factor through zero does not fit it; it shares the composite's basis step and is not judged. In ring-ip and CH-stretch the CC correction is close to one constant shift per family (mean ≈ rms), which no candidate's factor reproduces in ring-ip.

**What follows, as registered:** step 1 of the stepping-stone registration is re-proposed to the user. One check comes first because it is free: whether the CH-oop advantage holds at 6-31G*, the basis an affordable stone would use, since this read saw MP2 only at cc-pVDZ and the advantage rests on a basis artefact's direction (TASKS 183). Nothing is licensed and no carried model is touched.

## Amendment 1 (4 November 2026, 23:4x — after the outcome above, before any MP2/6-31G* shift; the user: 'Akkoord met 183')

The CH-oop advantage was seen at cc-pVDZ only, and it rests on the direction of MP2's out-of-plane over-softening in that basis. An affordable
stone would be MP2 at the pool's basis, 6-31G*, which no anchor has. This amendment adds that candidate; the read above stays as it is.

**The candidate.** MP2/6-31G* − B3LYP/6-31G*: pyscf conventional MP2, Cartesian d functions (the corpus's 6-31G*), frozen core by the element
rule, central differences of analytic gradients with the anchors' step 0.005 bohr, the corpus frame — the route and settings of the 5 Oct
step 0 (`cc_composite_full_check.py compute`). Benzene's and naphthalene's step-0 row files are reused (sha256-equal copies; their diagonal
row elements were printed on 5 Oct, no shift was ever computed from them); the nine others are computed by `probes/mp2_631gs_anchors.sh`
(run spec `mp2_631gs_anchors`, laptop WSL, smoked on water tonight). `compute` now writes pyscf's own log beside each row file; the rows
themselves are unchanged (`tests/test_cc_composite_pyscf_regression.py`, 3 passed against the changed scripts).

**The read.** `probes/mp2_proxy_alignment.py --mp2-631gs <rows dir>`: the same records, statistics and line, with MP2/6-31G* in the place of
MP2/cc-pVDZ — scaled rms over ωB97X's ≤ 0.8 *better*, ≥ 1.25 *worse*, between *no clear difference*; CH-oop decides, then 'other'. Without
the option the read reproduces the outcome above exactly (checked tonight).

**What each outcome means.** *Better in CH-oop:* step 1 of the stepping-stone registration is proposed to the user with its price (TASKS 183
(2)). *No clear difference or worse in CH-oop:* the cc-pVDZ advantage belongs to that basis; MP2 is parked again as a stone, and the lever
for CH-oop lies elsewhere.

**Prediction (before any number).** MP2/6-31G* also follows CC better than ωB97X in CH-oop: one in two.

## Outcome of amendment 1 (5 November 2026, 05:2x)

The nine row files came from run spec `mp2_631gs_anchors` (launched 4 Nov 23:46, `=== (M631) all done: 9 of 9` at 05:14:26, no failure);
benzene's and naphthalene's are the 5 Oct copies. Read: `probes/results_m1/mp2_proxy_alignment_631gs_2026-11-05/mp2_proxy_alignment.md` and `.json`; per anchor: `per_anchor.txt` there. The
first real read stopped at its first record (a parameter of `anchor_record` shadowed the row reader; the synthetic tests never passed
through that path): the reader was renamed, a test now runs `anchor_record` with the option on, and the read was run again unchanged
otherwise. The ωB97X, MP2/cc-pVDZ and MP2/cc-pVTZ rows of the new read equal the outcome above.

| family | scaled rms, ωB97X / MP2/6-31G* (cm⁻¹) | ratio | corr, MP2/6-31G* | verdict |
|---|---|---|---|---|
| CH-oop | 13.73 / 8.14 | 0.59 | +0.88 | better |
| other | 13.10 / 12.44 | 0.95 | +0.69 | no clear difference |
| ring-ip | 16.01 / 10.81 | 0.68 | −0.43 | better |
| CH-stretch | 2.52 / 1.91 | 0.76 | −0.44 | better |

**By the line: better in CH-oop**, which decides; 'other' shows no clear difference. The prediction (one in two) came out on the better side.
Per anchor, MP2/6-31G*'s leave-one-out residual in CH-oop is below ωB97X's on all eleven (2.2 to 13.5 against 7.9 to 19.6 cm⁻¹), and below
MP2/cc-pVDZ's on ten (azulene 11.3 against 10.6).

**What it does not say.** The stone carries the right sign at about six times CC's size (pooled slope +0.16; unscaled rms of CC − candidate
83.7 against CC's own 17.8 cm⁻¹): it is usable only through a fitted scale, as the stepping-stone design intends, never raw. In ring-ip and
CH-stretch the 'better' comes through a negative slope (MP2/6-31G* shifts against CC's direction), so those two families do not count as
support for the stone; the registration lets CH-oop decide and those do not enter. Eleven anchors, one basis pair, shifts to first order.

**What follows, as registered:** step 1 of the stepping-stone registration is proposed to the user with its price (TASKS 183 (2)).
