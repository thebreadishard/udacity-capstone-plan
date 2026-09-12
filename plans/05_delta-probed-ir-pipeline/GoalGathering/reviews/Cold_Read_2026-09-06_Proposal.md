# Cold read of Project_Proposal_2026-09-06.md — 2026-09-06 (fresh reader, no web, proposal only)

Reader: an academic supervisor in computational chemistry / astrochemistry who has seen no earlier version and no other file. Line numbers refer to the proposal as read. Each finding: quoted text, what is wrong, a concrete fix, and a class (BLOCKING = would mislead or seriously confuse; MINOR = would irritate or slow the reader).

## Findings

1. **Lines 6–7 vs 42 vs §8.** The header lists four items behind the rewrite ("the DFT-only dry run, the frozen-space probe, the feasibility timings, a laboratory-source search"); §1 says "Three things have been measured"; §8 has four bullets (the fourth is the Module-05 corpus timing). The reader spends time reconciling three, four and four. Fix: "Three measurements and one literature search" in the header, and in §8 label the corpus timing as a fourth, smaller measurement. **MINOR.**

2. **Line 11 "Eight external review passes (four cold reads and four adversarial domain reviews, 3–4 September)" and line 409 "Four review rounds — each a cold read by a fresh reader and an adversarial domain review with literature access".** Eight reviews in two calendar days, described as "external" and "adversarial ... with literature access", and nowhere is it said who or what performed them (colleagues, the student under a protocol, an AI system). A supervisor will assume independent human experts and be misled if that is not so; if it is so, the omission is odd. Fix: one sentence in the header and §9 naming the reviewers or the tool, and stating their independence from the author. **BLOCKING.**

3. **Line 24 "'currently unquantified' (Ricca et al. 2026)".** This quotation carries the motivation of the whole project, yet the reference appears only as "Ricca et al. 2026" in the "carried" author-year list (line 609) with no journal or DOI. Fix: give the full reference in §14. **MINOR.**

4. **Lines 30–33 and passim: "Plan 04 ... keeps plan 04's criterion, opponents, laboratory scoreboards, gates and honesty rules".** The word "carried" (from plan 04) appears about twelve times (294, 303, 309, 311, 312, 327, 339, 348, 354, 358, 493, 606) and "plan 01" appears once (505), but the proposal never says what plan 04 was, what its criterion, gates and honesty rules are, or that plans 01–03 existed. A cold reader is repeatedly told something is inherited without being told what it is. Fix: a half-page box after §1, "What plan 04 was and what is carried", listing the carried objects in one line each; and either introduce plans 01–03 in one sentence or delete the plan-01 reference. **MINOR** (but pervasive).

5. **Line 33 "opponents".** First use; the meaning (the baseline predictions the pipeline is scored against) is inferable only from §7 (line 327). Fix: "opponents (the baseline predictions the pipeline must beat)". **MINOR.**

6. **Line 35 "a hashed set of simultaneous multi-atom displacements"; line 162 "consumed in a hashed order fixed before any response exists".** "Hashed" is never explained; a spectroscopist will not know that it means an order fixed by a seeded pseudo-random function. Fix: at line 162, "in an order fixed by a seeded hash function before any energy is computed, so nobody can reorder the patterns after seeing a result". **MINOR.**

7. **Lines 44–45 "smooth to a few nano-hartree where the released local-CC code scatters by ten micro-hartree".** (a) The measured range is 0.002–0.06 µE_h (line 145), i.e. 2–60 nE_h; "a few nano-hartree" describes only the best mode. (b) Only the comparison code's default-threshold figure (7–11 µE_h) is quoted; line 146–147 shows 0.05–2.7 µE_h at tight thresholds, which narrows the contrast to a factor of 1–50 at the low end. Quoting only the flattering pair in the summary reads as selective. Fix: "scatters by 0.002–0.06 µE_h, against 7–11 µE_h (default thresholds) and 0.05–2.7 µE_h (tight) for the same code re-selecting its spaces". **MINOR.**

8. **Lines 45, 145 "the released code"; line 368 "the anchor code"; line 156 "the impurity solvers"; line 380 "LNO-CCSD(T)".** The local coupled-cluster program whose scatter is quantified and implicitly criticised is never named (program, version, method) in §3.3; the method name LNO-CCSD(T) first appears in a timing bullet at line 380. Worse, "impurity solvers" is vocabulary from quantum embedding (DMET, etc.), not from LNO/PNO local coupled cluster, so the reader cannot tell what kind of object the "frozen-space object" actually is. Fix: in §3.3, first sentence: "computed with [program, version], LNO-CCSD(T) [or whatever it is], with the local-correlation spaces ..."; replace "impurity solvers" with the actual name of the per-fragment CCSD(T) solver. **BLOCKING.**

9. **Line 62 "Three facts, two of them measured in this project's own history and one from the literature".** The first "fact" is an estimate ("by the source conversation's own estimate", line 66) and the second is a physical argument (line 70–74); neither is a measurement. "The source conversation" is also undefined. Fix: "Three considerations, two from this project's own history and one from the literature"; replace "the source conversation" with the name of the document. **MINOR.**

10. **Lines 84–85 "a cheap probe of the diagonal cubic correction remains, as a reported number that will show how much was given up".** This item never reappears: it is not in the pipeline steps (§5.1), the budget (§8) or the decisions (§10). It also sits in tension with §6 line 303 "**No coupled-cluster anharmonic correction**" and line 313 "No whole-molecule probing" versus §4's "not promised": §6 says "does not do" for things §2/§4 say are "not promised". Fix: either add the cubic probe to §5.1 step 2 and to the budget or delete it; in §6 write "No *promised* coupled-cluster anharmonic correction (a diagonal cubic probe is reported, §2)". **MINOR.**

11. **Line 92 "saturates around a hundred" vs line 266 "The adjectives 'size-independent', 'O(1)' and 'saturates' are forbidden everywhere, including this proposal."** The proposal breaks its own rule 170 lines earlier, even if the use describes the literature. Fix: at line 92, "levels off near a hundred in the authors' data"; or at line 266, "forbidden in any sentence about this project's own cost". **MINOR.**

12. **Line 115–116 "The large off-diagonal elements of the correction couple modes 170–450 cm⁻¹ apart" and Risk 2, lines 483–484 "Measured at benzene: it is not [near-diagonal], and the couplings follow symmetry, not frequency."** In the rehearsal "the correction" is the difference between two DFT functionals standing in for the coupled-cluster correction (line 371). Written this way, §3.2 and Risk 2 read as measured properties of the CC−DFT correction, which has not been computed. Fix: "the surrogate (functional-difference) correction" at 115, 118, 483; in Risk 2: "Measured at benzene on the DFT surrogate: it is not". **BLOCKING.**

13. **Line 116 "the strongest pair at 1186 and 1357 cm⁻¹"; line 371 "The difference between two functionals stood in for the correction"; line 488 "a functional pair that brackets exact exchange".** The two functionals and the basis set of the rehearsal are never named, so the quoted frequencies and the 0.43 cm⁻¹ / 7 cm⁻¹ errors (line 373) have no stated conditions. Fix: name functional pair and basis in §8 bullet 1 and once in §3.2. **MINOR.**

14. **Line 118–119 "the two-mode patterns in the deck".** "Deck" is first used here and never defined (also 125, 222, 459). Fix: "the deck (the ordered list of probe patterns)". **MINOR.**

15. **Line 124 "only for molecules whose point group leaves too many free elements to determine".** No criterion for "too many". Fix: give the rule (e.g. "when the free-element count exceeds the rung's probe cap") or point to the document that holds it. **MINOR.**

16. **Lines 128–129 "the benzene rehearsal needed 388 energies for 435 unknowns" vs line 372 "334 displacement pairs, 2 h 30 min" vs line 374–375 "The measured off-diagonal count, 388 energies for 435 unknowns" vs line 221 "their diagonal costs two energies each" vs line 376 "60 gradients".** If a displacement pair is two energies, 334 pairs is 668 energies; if a pair is one pattern, 334 patterns is fewer than 388. The diagonal block alone should cost 2 × 30 = 60 energies on top of the off-diagonal count. The three numbers cannot be reconciled from the text, and this is the single number on which §3.2's cost expectation "rests" (line 375). Fix: one explicit sentence in §8: "N₁ single-mode patterns + N₂ two-mode patterns, each run as a ± pair, = E energies in total; the off-diagonal count K_off = 388 of these". **BLOCKING.**

17. **Line 131 "naphthalene (D₂h, eight representations) has of order 120 free couplings instead of 1,128".** The free-element count for a given point group and mode assignment is an exact combinatorial number, computable without any calculation; "of order" for it looks unfinished, especially in the sentence that "puts the energy route at naphthalene inside the laptop's budget". Fix: give the exact count. **MINOR.**

18. **Line 142 "(probe M1, 5–6 September ...)"; line 306 and 548 "the dipole probe M1-μ".** The labels are never explained. Fix: "(probe M1 — the first of the plan's numbered measurements; M1-μ is its dipole-derivative companion)". **MINOR.**

19. **Line 143 "along three normal modes — totally symmetric, degenerate, and out-of-plane".** The modes are not identified by symmetry label or frequency, so the bias numbers of lines 149–151 cannot be attached to a band. Fix: give the three labels and DFT frequencies. **MINOR.**

20. **Lines 147–151: three bias ranges ("5–28 cm⁻¹ ... 0.5–2.6 cm⁻¹ ... at default thresholds, and 0.03–0.36 cm⁻¹ at tight thresholds").** The proposal never says which threshold setting the pipeline will run at, so the reader cannot tell which bias goes into the error budget of §5.1 step 4; decision 15 fixes the energy definition but not the thresholds. Fix: state the working threshold, or say explicitly that the threshold-sensitivity line of §7 (line 350) decides it and when. **MINOR** (borders on blocking for the budget).

21. **Line 150 "the local-correlation literature's standard second-order correction for the truncated space".** Only decodable from decision 15 at line 465. Fix: write "[MP2(full) − MP2(local)] (decision 15)" here. **MINOR.**

22. **Line 152 "reproduces the reference energy exactly".** Everywhere else "reference" means canonical CCSD(T); here it seems to mean the equilibrium-geometry energy of the same local method. Fix: "reproduces the equilibrium-geometry energy exactly". **MINOR.**

23. **Lines 153–154 "the basis is larger, the frozen space is a smaller fraction of it, and the cc-pVDZ bias is a lower bound".** A prediction stated as a bound, with no argument or measurement; the scan that would show it is still running. Fix: "and the cc-pVDZ bias is expected to be a lower bound; the cc-pVTZ scan will say". **MINOR** (tone).

24. **Line 157 "without which a first run read a spurious bias of up to 147 cm⁻¹".** Fine to disclose, but the summary (lines 44–45) presents M1 as a clean result; the reader learns only here that the first run was wrong and must infer that every M1 number quoted is post-fix. Fix: add "(all M1 numbers in this proposal are from the corrected run)". **MINOR.**

25. **Lines 166–167 "dominates every response (97.6 % at benzene)".** 97.6 % of what — response magnitude, variance, norm? Fix: state the quantity. **MINOR.**

26. **Line 170 "would have run every rung to its cap".** "Rung" is first used here; the ladder that defines it is §5.2, 65 lines later. "Cap" (a probe cap) is defined only at line 335. Fix: "every rung (step of the size ladder, §5.2) to its probe cap". **MINOR.**

27. **Lines 141, 171, 172, 393: "noise floor" in four senses.** It means (a) the scatter the frozen space imposes (141), (b) "the rung's own noise floor" inside the stopping threshold (171), (c) "the noise requirement for the off-diagonal block" (171–172, a tolerance, not a floor), and (d) "the naphthalene noise-floor measurement" (393). Fix: use "measured noise" for a scatter and "noise requirement" for a tolerance, consistently. **MINOR.**

28. **Line 173 "ten times stricter than the diagonal requirement".** The diagonal requirement is never given. Fix: "(about 20 µE_h)". **MINOR.**

29. **Lines 173–174 "the frozen spaces meet it by two orders of magnitude"; Risk 1 line 479 "they are, by two orders of magnitude".** 0.06 µE_h against 2 µE_h is a factor 33 (1.5 orders); only the best mode reaches three orders. Fix: "by a factor of 30–1000 depending on the mode". **MINOR.**

30. **Lines 174–175 "the gradient route of §5.3 becomes load-bearing for the couplings"; Risk 1 line 481 "the gradient route as the labelled fallback".** §5.3 says that route exists only if a side project with a kill criterion succeeds. A fallback that may never exist is not a fallback. Fix: "the gradient route of §5.3, if the side project has delivered it; otherwise the coupling block for that rung is reported at its noise-limited precision and carries no beat claim". **MINOR.**

31. **Lines 182–183 "an in-house ML-calibrated harmonic baseline, and ... DFT-teacher machine-learning molecular dynamics"; line 54 "named, version-frozen state-of-the-art predictions"; line 327 "named, versioned lines".** Only PAHdb is ever named. The ML-MD opponent has no name, version or reference; the in-house baseline is called four different things ("ML-calibrated harmonic baseline" 182, "ML-corrected scaling baseline" 309, "calibrated-harmonic baseline" 355, "calibrated harmonics" 491). The supervisor is asked (§13.1) to critique §7, the evaluation contract, without knowing what is being beaten. Fix: a three-row table in §7 — opponent, version/date, reference — and one name for the in-house baseline throughout. **BLOCKING.**

32. **Lines 194–202: "is **not promised**" (whole-molecule R6) then "The largest species remains a promised object in the fragment-probed form"; vs lines 403–405 "Cluster node-hours ... get no number until access ... The C₃₈₄H₄₈-class DFT Hessian is itself a cluster object"; vs R6's licence part 3 "where the cluster allows" (line 244).** A "promised object" that needs a cluster the plan says it has no access to reads as a contradiction unless the reader remembers decision 1's "or the measured reason it could not be produced" (line 440). Fix at line 201: "remains a promised deliverable: a fragment-probed spectrum, or the measured reason none could be produced (decision 1)". **MINOR.**

33. **Line 208 "at a declared DFT level".** The DFT functional, basis set and grid are never declared anywhere in the proposal (B3LYP appears only for the Module-05 corpus, line 388). The DFT level fixes every harmonic frequency, every anharmonic constant, the normal-mode basis in which the correction is recovered, and the meaning of the correction itself. Fix: state functional/basis/dispersion/grid in §5.1 step 1. **BLOCKING.**

34. **Line 225 "the resonance-explicit routes plan 04 froze — second-order vibrational perturbation theory with explicit resonance treatment".** The VPT2 implementation (program, resonance scheme) is not named. Fix: name it. **MINOR.**

35. **Line 232 "the long-range share of the family's correction".** Undefined; presumably the fraction of the correction that comes from couplings beyond some distance. Fix: define in one clause, or point to the locality test of §5.1 step 2. **MINOR.**

36. **Table lines 237–244.** (a) The R2 cell holds a forty-word parenthetical about sources; the table is unreadable at a glance. (b) "Type: accuracy" for R2 whose C–C families are pre-declared undecidable (line 255–256). (c) R4–R5 "the R4 fragment checks promised conditional on cluster access" — "promised conditional" cancels itself. Fix: move source notes into the paragraph below; write "accuracy (C–H families; C–C families expected undecidable, see text)" for R2; "conditional on cluster access" without "promised". **MINOR.**

37. **Line 240 (R1: "the anchor licence") vs line 382 ("The anchor's bias line — 61 canonical energies along benzene's 30 modes") vs line 348 ("The anchor gate has three formulas").** The ladder places the anchor licence at naphthalene; §8 places its bias line at benzene (the only place the canonical reference fits). So the licence spans R0 and R1. Fix in the table: R0 "... anchor bias line (canonical reference)"; R1 "anchor noise line; anchor licence closes". **MINOR.**

38. **Line 248 "smaller than its beat margin"; line 351 "the smallest beat margin".** Never defined. Fix: at 248, "beat margin (the pre-registered minimum per-band improvement over the best opponent that counts as a win)". **MINOR.**

39. **Line 252, 498, 540 "an exhaustive search".** No literature search can be shown exhaustive, and §13.3 itself asks whether it missed something. Fix: "a systematic search of [databases and journals named] on 5 September". **MINOR** (tone).

40. **Lines 255–258 "the student has decided to sign off the scoreboard module with that expected result"; lines 300–301 "The student ruled more generally that a rule inherited from an earlier plan carries no authority of its own".** Two decisions that are not in the numbered list of §10 (1–19), although §10 is headed as the list of decisions "all closed". Fix: number them (20, 21) or mark them "unnumbered, in the ladder document". **MINOR.**

41. **Line 260 heading "Why the cost is reported and never described".** "Described" here means "characterised with adjectives"; on first reading the heading is opaque. Fix: "Why the cost is reported in numbers and never in adjectives". **MINOR.**

42. **Line 262 "probe count, mode, prior"; line 372 "Energy mode"; line 376 "gradient mode"; line 462 "Mode E is budgeted".** "Mode" here means the energy/gradient operating route, and collides with "normal mode" used throughout; "Mode E" is never expanded. Fix: say "route" (energy route / gradient route) everywhere, and in decision 13 write "The energy route". **MINOR.**

43. **Lines 272–273 and 385 "a canonical CCSD(T) gradient ... costs about fifty energies and 13.9 GB already at cc-pVDZ".** The cc-pVDZ energy time is never given (only 755 s at cc-pVTZ, line 380), so "fifty energies" has no visible denominator. Fix: add the cc-pVDZ energy time (about 28 s if the ratio is right) in §8. **MINOR.**

44. **Line 287 "four milestones with printed pass conditions, its own budget line, a twelve-week checkpoint and a kill criterion"; line 536–537 asks the supervisor for "a view ... on the side project of §5.3, which is where the plan's ambition and its main time risk both sit".** None of the four milestones, the pass conditions, the hours, or the kill criterion is stated. The supervisor is asked to judge a project whose only visible content is two hopeful arguments (lines 276–281). Fix: a five-line list in §5.3 — M1–M4 with pass condition and week, the hours budget, the kill rule. **BLOCKING.**

45. **Line 294 "the measured failure of motif transfer is the reason"; line 311 "the published cascade model is inherited post-processing".** Neither is explained or cited. Fix: one clause each with the reference ("motif transfer — plan 04's attempt to reuse a correction learned on one ring motif on another — failed by X"; "the emission cascade model of Mulas et al. 2018"). **MINOR.**

46. **Line 295 "The Module-05 deep-learning component"; §12; Module 01 absent.** "Module-05" is used 60 lines before §12 explains the module numbering, and Module 01 is never mentioned. Fix: "(Module 05 of the programme, §12)" at first use; list Module 01 in §12 or say it maps to nothing. **MINOR.**

47. **Lines 329–334 "seven inputs in hand ... Four of the seven exist today" vs lines 391–393 "Still owed before the pilot note: the naphthalene DFT rehearsal ..., the scoreboard re-read ..., the run/no-run gradient check, and the naphthalene noise-floor measurement".** §8 lists four items owed, which leaves three of seven existing, not four — unless the naphthalene DFT rehearsal is not among the seven, in which case the seven-list should say "benzene rehearsal". The four that exist are also not named. Uncertain which is intended. Fix: bullet the seven inputs with "exists (date)" / "owed". **MINOR.**

48. **Line 332 and 392 "a run/no-run gradient check at equilibrium".** It is never said what is being checked to run (the PySCFAD local gradient? the canonical one?) or what "run" means (completes within memory?). Fix: one clause. **MINOR.**

49. **Lines 344–345 "must beat the zero correction against the reference by a frozen factor".** The factor is neither given nor said to live in the pilot note. Fix: "by a factor frozen in the pilot note". **MINOR.**

50. **Lines 350–351 "makes complete-PNO-space extrapolation mandatory at double cost".** Jargon (CPS); Altun et al. 2021 (line 559) is listed with "CPS extrapolation" in its note but is never cited in the body. Fix: "complete-PNO-space (CPS) extrapolation (Altun et al. 2021)". **MINOR.**

51. **Line 377 "5–10 minutes per geometry for all three arms"; line 376 "two threshold settings, 27 geometries each".** The three arms of the frozen-space probe are never listed, and "two threshold settings" suggests two runs, not three. Fix: name the arms once in §3.3 ("arm A: frozen spaces; arm B: re-selected, default thresholds; arm C: re-selected, tight thresholds" — or whatever they are). **MINOR.**

52. **Lines 383–384 "the full canonical reference Hessian by energies, 1,801 energies or about 378 hours".** The count is not derived (presumably 1 + 2·30 + 4·435). Fix: show the sum in parentheses. **MINOR.**

53. **Line 386 "exceeded the memory the laptop can give at cc-pVTZ".** The machine has 31 GB and the subsystem 22 GB (line 368–369); the number the gradient needed is not given. Fix: "did not complete within the 22 GB ceiling (estimated need: X GB)". **MINOR.**

54. **Line 393 "the naphthalene noise-floor measurement (72 energies)".** Naphthalene has 48 modes; the origin of 72 is not stated (modes × displacements?). Fix: state the design, as was done for benzene at line 143. **MINOR.**

55. **Lines 396–397 "because anthracene is the first acene where DFT's delocalisation error is visible".** A literature claim with no citation. Fix: cite (Altun et al. 2021 seems intended) or hedge. **MINOR.**

56. **Line 399 "plan 04's first factory batch".** Undefined. Fix: "plan 04's first batch of surface-learning points". **MINOR.**

57. **Line 422 "seventeen of eighteen held, then twelve of twelve".** The one closure that did not hold is not identified or said to be fixed. Fix: "(the one that did not, X, was re-closed in round four)". **MINOR.**

58. **Lines 423–428: seven design changes, of which "a first-order geometry term on every scored band" and "the shared reference energy's offset identified from a second displacement amplitude" appear nowhere else** — not in §5.1, not in the error budget of §7. Fix: add both to §5.1/§7, or drop them from the list of load-bearing changes. **MINOR.**

59. **Lines 430–431 "The review loop was **closed on 4 September** ... The plan's text has been frozen since; it changes only by dated notes"** vs §3.2 (prior changed from banded to symmetry, decision 11), §3.4 (stopping rule and threshold changed, decisions 8, 9, 12), decisions 14–15 (the object's definition), all dated 5–6 September. The document says "frozen" and then shows the stopping rule, the prior and the probed quantity all changing after data were seen. The dated-note mechanism makes this technically consistent, but a supervisor reading once will see a contradiction and, worse, a stopping rule tuned after a result — which is exactly what §7 line 334–335 promises cannot happen. Fix: "frozen except by dated notes; §3.2 and §3.4 record the notes of 5–6 September, all made on DFT-only rehearsal data before any coupled-cluster correction exists, and none of them touches a tolerance or margin". **BLOCKING.**

60. **Line 451, decision 7 "an unsubmitted draft on QM9 is renamed so the Module-05 corpus carries no reuse exposure".** Cryptic on a matter (re-use of coursework) where a supervisor needs plain language; as written it sounds like something is being hidden by renaming. Fix: "No earlier coursework overlaps with this project. An unsubmitted draft that used the QM9 set has been renamed so that the Module-05 corpus cannot be mistaken for re-used work". **MINOR** (would irritate).

61. **Line 468, decision 17 "Module 07's agent runs on LangGraph ... with the Anthropic API"; lines 518–519 "the campaign officer that enforces the budget rules".** A large-language-model agent appears in a coupled-cluster spectroscopy plan with no explanation of its function until §12, and even there only "enforces the budget rules ... every refusal logged". The reader will ask whether it touches any scientific number. Fix: one sentence at first mention: what it reads, what it writes, and that it never produces or edits a scientific value. **MINOR.**

62. **Lines 492–493 "one naphthalene study puts near 5 cm⁻¹ (carried at snippet grade until the full text is read)".** The study is not named; "snippet grade" is jargon. Fix: name it and write "(from the abstract only; full text not yet read)". **MINOR.**

63. **Lines 421, 430 "closed in spec", "a seam check of the last patch (19 seams, all mechanical)".** Internal jargon; meaningless to a cold reader. Fix: "closed in the specification"; "a consistency check of the last revision (19 cross-references, all mechanical)". **MINOR.**

64. **Tone: "honest"/"honesty" at lines 56–57, 127, 193, 300, 521, 526, 532, 551 (nine uses).** Repeated self-attestation reads as protesting too much; the rules themselves are persuasive, the adjective is not. Fix: delete all but line 532. **MINOR.**

65. **Repetition.** The 5 September source search is told three times (lines 252–258, 496–499, 538–544); the frozen-space result three times (§3.3, §8 bullet 2, Risk 1); the intensity policy three times (§1 lines 49–51, §7 lines 317–325, §13.4). Fix: state each once in full and cross-reference. **MINOR.**

66. **Lines 559, 606–610: references listed but never cited.** Altun et al. 2021 is never cited in the body; of the fifteen "carried" author-year entries only Ricca 2026 and Boese 2005 are cited, and none has a journal or DOI. Fix: cite or drop; give full references for those cited. **MINOR.**

67. **Line 240 "PNNL quantitative vapour-phase record, 25 °C, 0.1 cm⁻¹" vs lines 588–592.** The conditions match Schneider et al. 2024 (JQSRT), while Sharpe et al. 2004 is listed as "the PNNL gas-phase quantitative IR database". Which one is the naphthalene intensity source? Fix: cite explicitly at 240. **MINOR.**

68. **Lines 239, 250, 586: "NIST Quantitative IR series" / "NIST Quantitative series" / "NIST Quantitative Infrared Database".** One source, three names. Fix: one name. **MINOR.**

69. **Lines 39–40 "a pre-registered measurement with a stated losing condition".** The losing condition for the size question is never stated in this document. Fix: one line ("losing = the off-diagonal count grows at least as fast as the free-element count from naphthalene to coronene"). **MINOR.**

70. **Line 30 "reviewed in the previous round" vs §9 "Four review rounds".** "Round" means a supervision round at line 30 and an internal review round in §9. Fix: "in the previous supervision meeting". **MINOR.**

71. **Line 243 "expert-judgment datum".** First use; explained only in §13.5 (lines 549–551). Fix: "(a named expert's pre-registered judgment, §13.5)". **MINOR.**

72. **Lines 4–15, header paragraph.** A dense provenance paragraph (dates, companion documents, review passes, script provenance) precedes the summary; a supervisor reading once will skim it and miss the useful sentence at lines 13–15. Fix: move to a short "Provenance" note after §1 or into a footnote; keep the sentence on script-printed numbers. **MINOR.**

73. **Line 183 "DFT-teacher machine-learning molecular dynamics"; line 388 "Module-05 corpus"; line 445 "Hessian QM9 set".** Small: the ML-MD opponent should carry its reference (none of the carried list is obviously it), and "Hessian QM9" should cite Williams et al. 2024 at line 445. **MINOR.**

## Overall impression

What will be done is clear at the level of ideas: a DFT harmonic/anharmonic treatment per PAH, with the harmonic force constants corrected by a probed local-CC minus DFT difference recovered in the DFT normal-mode basis under a symmetry prior, scored against laboratory bands and frozen baselines up a size ladder from benzene to a C₃₈₄ flake. What is promised is stated carefully and repeatedly (positions everywhere decidable, intensities on two molecules, a fragment-probed spectrum or a documented refusal at the top). What has been measured is a DFT-only rehearsal, a 27-point smoothness scan of the frozen-space energy at benzene/cc-pVDZ, and a handful of timings; the proposal's own language sometimes lets the rehearsal read as a measurement of the real correction, and the one cost number everything leans on (388 / 334 / 435) does not add up in the text. What is asked of me is explicit and reasonable, but two of the five requests (the side project, the evaluation contract) cannot be answered from this document because the milestones, kill criterion, DFT level and opponent names are not in it. The document would read as a strong, unusually disciplined proposal once the eight blocking items are fixed; as it stands a careful reader is left checking arithmetic and guessing at inherited vocabulary.

