# The four claims, as of 18 November 2026

TASKS 140. The meeting of Wednesday 25 November is a conversation, not a resource request (decision 63). The user speaks with the
supervisor, she speaks with me through the chat, and the funding of further expensive calculations is discussed on the day (the user,
9 November: no written note). This page is what the chat reads from. Every number names the file it comes from. A claim without a number
and a counterpart counts as not made.

**Do not send her to the README's opening summary:** it is dated 12 September and describes the plan before the network existed. If she
asks for the binding text, point her to decisions 63 (the capstone's end point), 65 (the licence) and 66 (release networks) in
`README.md`'s 'Decisions'.

## Read this first: what the errors are measured against, and two rules changed after data

- **Every error on this page is against ωB97X/6-31G\*, a DFT level used as a stand-in (the proxy).** The network corrects B3LYP/6-31G\*
  toward ωB97X/6-31G\*. No coupled-cluster licence and no laboratory licence exists (decision 65: "It holds at the level the network is
  measured at, the DFT proxy").
- **The licence quantity changed on 16 November** (decision 65 amended): from the first-order frequency error of each seed's correction
  to the error of the band positions the pipeline prints, from the seeds' mean correction.
- **The promotion rule changed on 17 November** (decision 57 amended): from "no read-out worse at the reported precision" to a combined
  score that must improve beyond a Student-t line.
- **Both changes came after data and both favour v1.4.** On the old rules v1.4 is not promoted (worse on (a8) CH-oop by 0.05, inside two
  standard errors; `modules/05_support_predictor/out/v14/read_clean_rule-of-26oct.md`), and 'other' on hold-out (b) reads 3.68, above
  the line of 3 (`modules/05_support_predictor/out/v14/read_clean.md`).
- **The new rule would have refused v1.3** (combined score 0.820 against 0.915, line 0.103:
  `probes/results_m1/promotion_rule_test_2026-11-17/rule_test.txt`).
- **The new rule's power was estimated at v1.4's own observed effect**: on simulated arms it promotes 72.8 % of improvements that size
  (the old rule 12.0 %), with 1.5 % false promotions. For an improvement the size of v1.3's it promotes 40.7 % (same file).

## Words used on this page

| term | meaning |
|---|---|
| hold-out (a) | ten small parent molecules (benzene, phenanthrene, fluorene, …) held out on 19 September |
| (a8) | the eight of those ten never trained on under any name; the other two (2-naphthoic acid, benzonitrile) had a twin in training |
| hold-out (b) | every substituted molecule of two scaffold cores (fluoranthene, fluorene), frozen on 8 October; read on 40 molecules |
| twin | the same molecule under another id or in another charge state, e.g. benzene's radical cation beside benzene |
| carried / promoted | the carried version is the network the pipeline uses; a new version is promoted to carried by a registered rule (decision 57) |
| measurement / release networks | measurement networks train without the hold-outs and give every error bar; release networks train on all labelled molecules and are what ships (decision 66) |
| combined score | each read-out divided by its line (3 cm⁻¹ per family, 0.25 for the coupling ratio), averaged over hold-outs and read-outs, per seed; lower is better |
| families | CH-stretch (C–H stretches), CH-oop (C–H out-of-plane bends, the strong 11–15 µm bands), ring-ip (ring and in-plane modes), 'other' (the remaining, mostly low skeletal modes) |
| proxy task | a rehearsal in which ωB97X labels stand in for coupled-cluster anchors, so anchor counts can be measured without paying for CC |
| q_T | the size test's ratio: the network's coupling error (relative to no correction) on four 36–60-atom molecules, over the same on hold-out (a); ≤ 1.3 carries, ≥ 1.8 is steep |
| arm 0 / arm D | the size test's two trainings: arm 0 without molecules of the target size, arm D with one molecule per target size (34–54 atoms) |
| aromir | the public Python package that carries the pipeline and the release networks (GitHub) |

## Where v1.4 stands on 18 November

| claim | number | counterpart | molecules | file | read on |
|---|---|---|---|---|---|
| v1.4 promoted | combined score 0.690 | v1.3's 0.844; line −0.100 | (a8) 8, (b) 40 | `modules/05_support_predictor/out/v14/read_clean.md` | v1.4 measurement networks |
| licence, ring-ip | 1.17 / 1.22 cm⁻¹ on (a) / (b) | 3 | 8 / 40 | `probes/results_m1/pipeline_benzene_v14_2026-11-17/benzene/certificate.md` | v1.4 measurement networks |
| licence, CH-stretch | 0.80 / 1.67 | 3 | 8 / 40 | same | same |
| licence, CH-oop | 1.86 / 1.26 | 3 | 5 of 8 / 40 | same | same |
| licence, 'other' | 2.38 / 2.10 | 3 | 8 / 40 | same | same |
| old licence quantity, 'other' on (b) | 3.68 | 3 | 40 | `modules/05_support_predictor/out/v14/read_clean.md` | same |
| release checks | 5 of 5 passed | the design note's checks | 1,132 trained | `modules/05_support_predictor/out/v14/E7_rungC_v14s3clean_c00_control_release_release_checks.md` | v1.4 release networks |
| benzene, v1.4 | 2.35 cm⁻¹ (mean of 3 seeds) | v1.3's 1.66 | 1 | `probes/results_m1/v14_data_read_2026-11-17/clean_benzene.txt` | v1.4 measurement networks |

Notes to the table:

- **The licence rests on few molecules in two cells.** CH-oop on (a) rests on 5 molecules (the other three have no such band); its 95 %
  bootstrap interval over molecules is 0.93–3.2 cm⁻¹ and crosses the line. 'other' on (a) rests on 8 molecules; its interval is
  1.45–3.19 and crosses it too (certificate).
- **The measurement networks trained on 1,075 molecules** (914 fitted, 161 for early stopping;
  `E7_rungC_v14s3clean_c00_control_eval_clean_seed0.json`, `"n_train_ids": 1075`, and the training log). The `n1082` in their file
  names is the size requested, which is larger than the pool.
- **What ships is trained on all data (decision 66).** The pipeline and aromir use v1.4's release networks, trained on all 1,132
  labelled molecules, with error bars and licence from the measurement networks. aromir is on GitHub at `42a8956`, CI green. The
  weights go to Hugging Face only after aromir's acceptance tests (TASKS 269).
- **Benzene's demo certificate is in-sample.** Its rms of 1.13 cm⁻¹ against ωB97X comes from release networks that trained on benzene
  (two of the three fitted it), so it is not an out-of-sample error (certificate; release checks §5).

**The hold-out lesson.** Benzene's radical cation had been trained beside the held-out neutral benzene, because the twin rule matched
charge. On one network it raised benzene's error from 1.47 to 5.37 cm⁻¹ (`probes/results_m1/v14_data_read_2026-11-17/probe_nop3c.txt`,
seed 0). The rule now drops a hold-out molecule's twin in every charge state, and the readers refuse a model that trained one. The clean
arm removed seven pool molecules, one of them benzene's cation. It brought benzene to 2.35 on the mean of three seeds (2.63, 1.98,
2.44; `clean_benzene.txt`). That is still worse than v1.3's 1.66, so the cation is part of the cause, not all of it.

**The search for a better recipe runs** (`probes/v14_search.py`, stage 1 on 18 November). Two of ten finished one-seed candidates lead
the carried recipe on the selection set. One seed is not a verdict; the registered read decides, against v1.4.

## The line

Pretrained on ωB97X, adjusted with few coupled-cluster anchors. "100–200 anchors for the final goal" (the user's wording, 21 October),
with its notes, which are part of the claim and not a caveat added afterwards:

1. The number is the rehearsal's, on the proxy task, not coupled cluster's.
2. It is molecules and prices, not a count: which molecules, at what level, for what money.
3. The anchors must span ring fusion.
4. 100–200 anchors reach 3 cm⁻¹ in three of the four families. 'other' is not reached at 200 (claim 3).

## (1) The correction is learned, and it carries to larger molecules — **open**

This is the central claim, and it is still open. All of it was read before v1.4.

| read | number | counterpart | file |
|---|---|---|---|
| chain 41: five fused rings (32–40 atoms) from a corpus of at most four | q5 = 1.06 (carries, line ≤ 1.3) | — | `modules/05_support_predictor/out/read_chain41_analytic.md` |
| chain 41: corrected ω error on those molecules | 3.77 cm⁻¹ | 3.17 with five-ring molecules in training; 22.71 uncorrected | same |
| chain 42: four molecules of 36–60 atoms | q_T = 0.767 / 0.174 = **4.40** (steep, line ≥ 1.8) | — | `modules/05_support_predictor/out/read_chain42.md` |
| chain 42: corrected ω error on those four, arm 0 / arm D | **7.90** / **7.79** cm⁻¹ | 22.83 uncorrected | `read_chain42.json`, `read_chain42_beside.json` |

- The learned correction removes about two thirds of the error at 36–60 atoms. It does not reach 3.
- The registration reads a steep q_T as: the mandate's spectra need the target sizes in the corpus, or another route.
- **q_T = 4.40 stands.** It is arm 0's number. Arm D trained on five of its six molecules, because D_ac28161d06 left the pool with a
  negative mode. That mode was repaired on 13 November (−7.48 → +7.05 cm⁻¹,
  `probes/results_m1/low_mode_patch_2026-11-13/corpus/D_ac28161d06/report.json`). Re-running arm D with six can move g
  (0.92, arm D against arm 0), not q_T.
- **Still owed:** the floor re-read on the 36–60-atom molecules with v1.4.

**How it will be presented:** as *what large molecules need*, not as *it carries*. The learned correction cuts the error at 36–60 atoms
from 22.8 to about 7.9 cm⁻¹. The penalty with size is steep. We have measured what closing the rest would take.

## (2) A few examples move a pretrained network — **stands on the proxy, for known families**

Read on 21–22 October with the proxy check's own base networks, before v1.3; not re-read on v1.4.

- Arm (a), a different correction on known families: re-fitting the whole output head takes CH-oop from **6.55 to 2.82 cm⁻¹** as the
  anchors rise from 5 to 200. Re-fitting only the last layer stays at 8–10 cm⁻¹ at every count. So the whole head moves, not a scaling
  (`modules/05_support_predictor/out/proxy_check_2026-10-21/proxy_check_read.md`).
- **Arm (b), a new domain: the registered line does not hold.** The base network already reads 2.66 cm⁻¹ CH-oop there before any anchor,
  and the whole head beats the last layer at only one of three anchor counts (same file).

## (3) The anchor count per accuracy, with prices — **stands on the proxy**

Read on 29 October with the count's own base networks, not a carried version (proxy task, arm (c), body1_es); not re-read on v1.4
(`modules/05_support_predictor/out/anchor_count_2026-10-29/anchor_count_read.md`):

| family | anchors to 3 cm⁻¹ |
|---|---|
| ring-ip | ≤ 100 (already 2.35 at 100, the smallest count measured) |
| CH-stretch | ≤ 100 (2.77 at 100) |
| CH-oop | **167** (153–177) |
| 'other' | not reached by 200 (3.59 at 200) |

- Of the three families that reach the line, CH-oop needs the most anchors.
- 167 anchors cost ≈ €729 for the cheapest selection and ≈ €3,026 drawn as the count drew them
  (`modules/05_support_predictor/out/anchor_plan/count_n167.md`).
- The price leaves out the MP2 basis step. The €729 selection uses smaller molecules than the count measured.
- Whether to make them is a funding question for 25 November (TASKS 82). Paid computation stopped on 15 November (decision 63).

## (4) The eleven coupled-cluster anchors as the bridge — **direction confirmed**

The registry holds eleven carried anchors (`modules/05_support_predictor/out/ANCHORS_STATUS.json`). Read on 21 October on chain 34 (v1.1);
not re-read since (`modules/05_support_predictor/out/anchor_set3_headall_2026-10-21/read_set3.md`):

- **CH-oop on the original six anchors: 7.24 → 6.25 cm⁻¹** with all anchors in the whole-head fit (−13.8 %, predicted ≈ −16 %). The
  registered reading is "between".
- **Intensities on the three low-symmetry anchors:** the whole head's matched intensities beat the uncorrected B3LYP shapes on 3 of 3 —
  pyridine 0.136 against 0.262, fluorobenzene 0.063 against 0.104, benzonitrile 0.086 against 0.258.
- **This confirms the direction, not the protocol:** the protocol was chosen on the same anchors (ledger, 21 October).
- **The anchors' own accuracy in CH-oop is of the same size as 6.25.** Pyridine's composite lies 6.62 cm⁻¹ from CC/TZ
  (`probes/results_m1/anchor_oop_checks_2026-11-05/read_pyridine/anchor_oop_pyridine.md`). Benzene's CC/TZ moves 5.40 with a QZ basis
  step (`probes/results_m1/anchor_oop_checks_2026-11-05/read_benzene_qz/anchor_oop_benzene_qz.md`). The bridge is not more accurate than
  its own level.
- **Not claimed:** T3's ≤ 3 cm⁻¹.

## Beside the four

**The network beats every fitted scale factor on the proxy task.** Read on 25 October on chain 34 (v1.1), not re-read on v1.4
(`modules/05_support_predictor/out/scale_factor_baseline_2026-10-25.md`; the frequency shift B3LYP → ωB97X, cm⁻¹):

| family | network, (a) / (b) | three factors on the PAHdb regions, (a) / (b) |
|---|---|---|
| CH-stretch | 1.25 / 2.57 | 2.02 / 3.86 |
| CH-oop | 2.36 / 3.81 | 9.21 / 9.96 |
| ring-ip | 1.82 / 2.62 | 15.47 / 14.19 |
| 'other' | 3.35 / 6.03 | 8.58 / 14.63 |

One factor per family does better than the three regions in CH-oop (6.61 / 6.93) and still loses to the network everywhere.

**The anharmonic shift** (TASKS 53) is a model of its own beside the network. Its truth is GVPT2 at B3LYP/6-31G\*. S3's registered read
of 13 November, on coronene and tetracene, with the two modes VPT2 cannot state excluded
(`probes/results_m1/labels_domain_2026-11-13/s3_read_exclude/s3_read.md`, `route_rule/route_rule.md`, `route_rule/route_rule_ch.md`):

| family | model's error | line | coronene | tetracene | error of keeping the harmonic position |
|---|---|---|---|---|---|
| CH-oop | 8.38 | 3.0 | 11.91 | 4.55 | 12.48 |
| ring-ip | 3.37 | 3.0 | 4.25 | 2.35 | 26.23 |
| 'other' | 3.84 | 3.0 | 5.69 | 1.09 | 8.20 |
| CH-stretch | 6.21 | 3.0 | 6.94 | 5.68 | 134.24 |

- The registered route rule licenses **no anharmonic step in any family**.
- **Coronene carries most of the failures, not all.** Tetracene passes in ring-ip and 'other' but fails in CH-oop (4.55) and CH-stretch
  (5.68).
- Coronene is a compact pericondensed PAH, and the corpus holds nothing like it. Over 3,129 modes in 57 force fields (B3LYP and GFN2-xTB),
  8 reach a strain of 0.08, and **not one** of them would be covered by a block of the mode and its largest partner
  (`probes/results_m1/coverage_screen_2026-11-13/coverage_screen.md`, TASKS 210).
- **Decided 14 November (TASKS 211):** the pipeline prints the modelled shift as its best estimate with the measured bar above and
  claims no licence, because keeping the harmonic position costs more in every family
  (`GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md`).
- **The current default is harmonic.** The step exists but is off unless the run is given `--anharmonic-minutes`, so the 18 November
  benzene certificate prints harmonic positions (certificate).

**VPT2 has a domain, and we now mark it.**

- For an out-of-plane mode of a highly symmetric planar molecule, symmetry removes the cubic terms that normally cancel the quartic one.
  Second-order perturbation theory then cannot state the fundamental. Coronene's mode 36 gets +179 cm⁻¹, 22 % of ω.
- The threshold comes from the distribution. Over 2,028 labelled modes in 36 force fields the strain's median is 0.018 and its 99th
  percentile 0.052. The C–H stretches, where a −170 cm⁻¹ correction is sound VPT2, sit at 0.054–0.056. Above them the next modes are at
  0.166, 0.193, 0.222 and 0.388 (`GoalGathering/notes/Design_2026-11-13_VPT2_Domain_Marks.md`).
- The line of 0.10 marks 8 modes in 5 of those 36 force fields (same note). This is a different population from the coverage screen's
  (3,129 modes in 57 force fields, B3LYP and GFN2-xTB), whose 8 modes at 0.08 are another set.
- Coronene's two marked modes are solved without perturbation theory, by a two-mode block: mode 24 at 681.45 and mode 36 at
  969.41 cm⁻¹ (`probes/results_m1/solved_modes_2026-11-13/coronene/solved_modes_pair.md`). The corpus cases cannot be covered this way and
  stay marked.

## What is not proved, and will be said so

- Any accuracy against coupled cluster or experiment. Every licence is against ωB97X.
- That the correction carries to large molecules at ≤ 3 cm⁻¹. It does not, yet; claim (1) is open.
- That the anharmonic step can be licensed in any family. It cannot, by the registered line; it is printed with its bar instead.
- T3's ≤ 3 cm⁻¹ (claim 4).
- Anything about modes like coronene's 24 and 36. The corpus contains nothing like them; a corpus that does is the open question of
  TASKS 200 and 210.
- That the low label modes are clean. pyscf's CPU DFT Hessian has no grid-weight derivatives, so label modes below ≈ 25 cm⁻¹ carry grid
  noise, which reaches into 'other' (TASKS 201). The repaired Hessians became the labels on 14 November
  (`probes/results_m1/low_mode_swap_2026-11-14/swap.json`). Which reads already use them is not on this page.

## Questions for her

- CFOUR (`Supervisor_Brief_CFOUR_2026-10-05.md`) and access to Snellius.
- The pyrene laboratory truth.
- The 2015 CCSD(T)/cc-pVTZ naphthalene reference.
- An open-shell reference for the cations.
- Closed-access papers: the paste-ready block `PDF_Request_2026-10-25_Supervisor.md` (22 papers).
- Funding for anchors. No file states a request; the figure comes from the anchor price table in claim (3): ≈ €729–3,026 for 167
  anchors, without the MP2 step.

## Schedule

No expensive calculation before 25 November (the user, 18 November). Every read lands here with its number, so that the chat can answer
her on the day.
