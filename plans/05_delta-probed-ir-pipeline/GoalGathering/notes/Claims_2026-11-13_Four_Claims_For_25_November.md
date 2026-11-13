# The four claims, as they read on 13 November 2026

TASKS 140. The meeting of Wednesday 25 November is a conversation, not a resource request (decision 63): the user speaks with the
supervisor, she speaks with me through the chat, and the funding of further expensive calculations is discussed on the day (the user,
9 November: no written note). This page is what the chat reads from. Every number here names the file it comes from; a claim without a
number and a counterpart counts as not made.

## The line

Pretrained on ωB97X, adjusted with few coupled-cluster anchors. "100–200 anchors for the final goal" (the user's wording, 21 October),
with its three notes, which are part of the claim and not a caveat added afterwards:

1. The number is the rehearsal's, on the proxy task, not coupled cluster's.
2. It is molecules and prices, not a count: which molecules, at what level, for what money.
3. The anchors must span ring fusion.

## (1) The correction is learned, and it carries to larger molecules — **open**

This is the central claim and the one still open. What stands and what does not:

- **Carries within corpus size:** chain 41 on analytic labels carries, q5 = 1.06 (read 9 November, ledger).
- **Does not yet carry to 34–60 atoms:** chain 42's registered line 1 gives q_T = 0.767 / 0.174 = **4.40**, read 11 November
  (`modules/05_support_predictor/out/read_chain42.md`). The registration's own reading of a steep q_T is that the mandate's spectra
  need the target sizes in the corpus, or another route.
- Beside that number: set T's corrected ω rms is **7.90** cm⁻¹ (arm 0) and **7.79** (arm D) — `corrected_freq_rms` 7.9036 and
  7.7852 in `modules/05_support_predictor/out/read_chain42.json` — against the zero rule's **22.829**
  (`read_chain42_beside.json`). The learned correction removes about two thirds of the error at 36–60 atoms, and does not reach 3.
- **The 4.40 may move.** Arm D trained on five of the six registered training molecules, because D_ac28161d06 left the pool at load
  with a negative analytic mode. Its low mode was repaired on 13 November (−7.48 → +7.05 cm⁻¹,
  `probes/results_m1/low_mode_patch_2026-11-13/corpus/D_ac28161d06/report.json`), so arm D can be re-run with six. Whether it is
  re-run waits on one decision of the user's (do the repaired Hessians become the corpus's labels, TASKS 201).
- **What is still owed before 25 November:** v1.4 after the CCX53 labels merge (TASKS 129, search from Monday 16 November, ending
  ≈ 19 November), and the floor re-read on the ≥ 34-atom molecules.

**How it will be presented:** as *what large molecules need*, not as *it carries*. The honest statement on the day is that the learned
correction cuts the error at 36–60 atoms from 22.8 to about 7.9 cm⁻¹, that the penalty with size is steep, and that we have measured
what closing the rest would take.

## (2) A few examples move a pretrained network — **stands**

- The proxy check (read 22 October, ledger): the whole head goes from **6.55 to 2.82 cm⁻¹** in CH-oop as k rises from 5 to 200
  anchors, while a single λ stays stuck at 8–10 at every k. It is the whole head that moves, not a scaling.
- Repeated on set three with the whole head (R-B, 3 of 3; read 21 October, ledger).
- Re-read on v1.4 only if v1.4 becomes the carried model.

## (3) The anchor count per accuracy, with prices — **stands**

`modules/05_support_predictor/out/anchor_count_2026-10-29/anchor_count_read.md` (proxy task, arm (c), body1_es):

| family | anchors to 3 cm⁻¹ |
|---|---|
| ring-ip | 100 |
| CH-stretch | 100 |
| CH-oop | **167** (153–177) |
| 'other' | not reached by 200 |

Priced at ≈ €729–3,026 (`modules/05_support_predictor/out/anchor_plan/count_n167.md`), and made as November decides (TASKS 82). CH-oop needing two thirds more anchors than the other families is
consistent with claims (4) and with the spectral shape below: the same family is the hardest in three independent measurements.

## (4) The eleven coupled-cluster anchors as the bridge — **stands**

- CH-oop **6.25 cm⁻¹** on the original anchors in the whole-head fit mode.
- On the three low-symmetry anchors the whole head's matched intensities beat the uncorrected B3LYP shapes: 0.136 / 0.063 / 0.086
  against 0.262 / 0.104 / 0.258 (R-B; both read 21 October, ledger).
- **Not claimed:** T3's ≤ 3 cm⁻¹.
- How true the anchors themselves are in CH-oop, stated with the claim: pyridine's composite lies within **6.62 cm⁻¹** of CC/TZ, and
  benzene's TZ **5.40** from QZ (10 November). The bridge is not more accurate than its own level.

## Beside the four

- **The network beats every scale factor** on the proxy task — including, as the baseline it is, the PAHdb scale factor.
- **The spectral shape** (TASKS 53), where the anharmonic shift is a model of its own beside the ΔH network. S3's second registered read
  of 13 November, with the two modes VPT2 cannot state excluded and reported apart
  (`probes/results_m1/labels_domain_2026-11-13/s3_read_exclude/s3_read.md`): CH-oop **8.38**, ring-ip **3.37**, 'other' **3.84** cm⁻¹
  against a registered line of 3.0. The registered route rule therefore licenses **no anharmonic step in any family**
  (`probes/results_m1/labels_domain_2026-11-13/route_rule/route_rule.md`).
  Two things belong beside that verdict on the day:
  - **One target carries every failure.** On tetracene alone the model gives ring-ip 2.35 and 'other' 1.09, under the line; coronene
    gives 4.25, 5.69 and CH-oop 11.91. Coronene is a compact pericondensed PAH, and the corpus holds nothing of the kind: of 3,129
    modes over 57 force fields, 8 reach a strain of 0.08 and **not one** of those would be covered by a block of the mode and its
    largest partner (`probes/results_m1/coverage_screen_2026-11-13/coverage_screen.md`, TASKS 210).
  - **Leaving the step out costs more than the model it refuses:** the rms of the true shift over the same modes is ring-ip **26.23**,
    CH-oop **12.48**, 'other' **8.20** cm⁻¹. Whether the pipeline prints the shift unlicensed is an open decision of the user's
    (TASKS 211).
- **VPT2 has a domain, and we now mark it.** For an out-of-plane mode of a highly symmetric planar molecule, symmetry removes the cubic
  terms that normally cancel the quartic one, so second-order perturbation theory cannot state the fundamental: coronene's mode 36
  gets +179 cm⁻¹, 22 % of ω. The threshold is set from the distribution, not chosen: over 2,028 labelled modes the strain's median
  is 0.018 and its 99th percentile 0.052, the C–H stretches (where a −170 cm⁻¹ correction is sound VPT2) sit at 0.054–0.056, and
  nothing else reaches 0.09 before four modes at 0.166, 0.193, 0.222 and 0.388. The line of 0.10 marks 8 modes in 5 of those 36
  force fields (`GoalGathering/notes/Design_2026-11-13_VPT2_Domain_Marks.md`). Two of coronene's are solved non-perturbatively with
  a two-mode block
  (mode 24 at 681.45 and mode 36 at 969.41 cm⁻¹); the three corpus cases are not coverable and stay marked.

## What is not proved, and will be said so

- That the correction carries to large molecules at ≤ 3 cm⁻¹. It does not, yet; claim (1) is open.
- That the anharmonic step can be licensed in any family. It cannot, by the registered line.
- T3's ≤ 3 cm⁻¹ (claim 4).
- Anything about modes like coronene's 24 and 36: the corpus contains nothing of the kind, and a corpus that does is the open question
  of TASKS 200 and 210.

## Questions for her

- CFOUR (`Supervisor_Brief_CFOUR_2026-10-05.md`) and access to Snellius.
- The pyrene laboratory truth.
- The 2015 CCSD(T)/cc-pVTZ naphthalene reference.
- An open-shell reference for the cations.
- Closed-access papers: the paste-ready block `PDF_Request_2026-10-25_Supervisor.md` (22 papers).

## Schedule

One rerun fits before the last reads of 16–18 November. Every read lands here with its number, so that the chat can answer her on the
day.
