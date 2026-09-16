# Cold read, 16 September 2026 — plan 06 annex, decision rule, README, cost ladder §3/§5

*A fresh reader (a separate model instance with no knowledge of the project's conversations) read the four files as the supervisor would and reported at most twenty stumbles, ranked. Nothing was edited. The report is kept verbatim below; the disposition (what is fixed by a dated note before 26 September, what is deferred, what is disputed) is added by the student underneath, dated. Files: A = `Annex_Draft_2026-09-13_Plan06_for_the_Supervisor.md`, D = `Decision_Rule_2026-09-13_When_Plan06_Closes_or_Transfers.md`, R = `README.md`, C = `Cost_Ladder_2026-09-12_Network_Data.md`.*

## The reader's report (verbatim)

1. **A:14 vs D:14, R:31.** The annex's "one unmeasured number" item says the g measurement "runs after the current naphthalene timing", while the decision rule and README record that M2a ran on 14 September, gave g = 2.84/3.20 only at RHF/MP2, and that the anchor-level cells are "unmeasurable on the laptop" — and the annex's own 14 September update (A:24–28) never mentions it. Fix: replace item 4 with the measured outcome and its consequence (the closing arm of the rule is now the live one).

2. **A:9, A:11–13; R:70.** "All measured on the benzene stand-in tensor" is never defined, and the README shows the naphthalene stand-in is a BHHLYP − B3LYP difference, so the reader cannot tell whether items 1–3 describe a coupled-cluster correction or a DFT–DFT surrogate. Fix: one clause stating exactly what the benzene stand-in tensor is (method pair, basis, provenance) and whether any claim rests on a real local-CC deck.

3. **A:11 vs A:26; C:37, C:73.** Item 1 says the correction "is not local" and "follows the π system", item 5 says the pair correlation is "nearest-neighbour", σ-short-ranged and gap-independent; the ladder's network bullet still says "the range grows as the gap closes with size" and §5 says that bullet "stands" though X7 undercuts it. Fix: one sentence reconciling the two objects (curvature of Δ₂ in real space vs MP2 pair-energy decay) and a dated correction to C:37.

4. **A:28 (last sentence) vs C:71; D:14.** The annex says the 15 October criterion "is read with that division of labour in mind", but the ladder says that re-reading is "for the user, not decided here", and the decision rule says the closing arm is live and the remedy is "not scheduled" — the supervisor is not told the cost branch is on course to close. Fix: state plainly which rule text is in force and what the expected 15 October verdict is.

5. **A:11, A:13 vs A:28, C:54.** Sparsity and low rank are rejected at 0.5 cm⁻¹, yet lever G is accepted with a 2.5 cm⁻¹ win / 5 cm⁻¹ lose condition on increments of +7.9/−6.0 cm⁻¹; an insider will ask which tolerance the project actually needs. Fix: name the project's band-position error budget once and say why the two tests use different bars.

6. **A:12; R:58; C:26; D:14.** "Recovers Δ₂ exactly (to 10⁻¹⁶) … 9 products at naphthalene" reads as a measured recovery, but X14 was a pattern count on a DFT irrep table (no naphthalene Δ₂ existed on 13 September); and "18 gradients" is offered without saying the production engine has no gradient and the AD route did not fit in memory. Fix: mark the naphthalene number as a count, not a recovery, and add the gradient's availability status in the same sentence.

7. **A:14 (g ≤ 6 / ≤ 20 / > 20), A:22 and D:14, D:24 (20 / 26 / > 26), C:26 (g < 34–40), C:27 (g < 4.4).** Four different g thresholds appear with no reconciliation. Fix: one sentence giving the single operative threshold (26.3 from X14) and labelling the others as superseded or as belonging to lever D.

8. **A:18.** "Finds the colouring literature never entering chemistry" is a universal negative drawn from an abstract-level chase of 873 citing works, and the novelty claim that follows is scoped so narrowly it cannot fail. Fix: "not found in the 873 works chased" plus the search's stated limits.

9. **D:1, D:14, D:15–19.** A rule titled "before the numbers" has its g row's *expected* cell overwritten with the result (the original expectation is gone), while rows 15–19 are left stale though X6, X7 and T1d are reported done in A:26–27. Fix: keep the original cell and add outcomes in a separate dated column or a §2b, updated for every row.

10. **A:28 ("two to four desktop-weeks instead of a desktop-year", "removes ≈ 38 %"); C:15, C:55, C:57, C:67.** Both figures are unmarked estimates: the desktop factor is a never-timed core-count rule, the 0.62 is "arithmetic … not yet a run", and the 15 September remeasurement (69 min, 3.8 h) shifted the rows. Fix: carry the ladder's **m**/*e* marks into the annex and quote the 15 September numbers.

11. **A:28 vs C:55.** H's admissibility (odd part ≤ 0.55 µE_h) was measured at TZ tight, but at DZ *normal* it is −103 µE_h, larger than the curvature bias; G moves the deck to DZ, so "if both are licensed" silently assumes an unmeasured DZ-tight odd part. Fix: name the DZ-tight odd-part measurement as a prerequisite of stacking G and H.

12. **A:7, A:11 ("nine PAHs") vs C:29 ("eight PAH Hessians").** The X15 sample size differs between files. Fix: check the X15 note and align both.

13. **A:12, A:27.** Machine-checking Curtis–Powell–Reid and Coleman–Moré in Lean is presented as an achievement; a spectroscopy supervisor reads it as effort on 1974–84 results with no stated payoff for spectra. Fix: one sentence on what the certificates protect (or move the Lean material out of the annex).

14. **A:26 (X7).** "Under the pre-stated 2" keeps T3 alive while the data show the opposite trend (λ rises 12 % where the claim predicts 77 %), so the threshold looks chosen too loosely to fail. Fix: say the threshold was lenient and state what observation would close T3 by 1 December.

15. **A:26 (X6).** "CAS(6,6) carries 9 % of the MP2 correlation curvature (−48 % on the C–H out-of-plane mode)" compares a static-correlation share to an MP2 curvature, and a negative share is undefined for the reader. Fix: define the share in one clause and say what a negative value means.

16. **A:1, A:3, A:7, A:30.** The document to be handed over still carries "the user decides whether it accompanies the proposal", internal codes (K, R1, Δ₂, P25, M2a, decision 34, X8) without gloss, "two transfers" of which one is pending, and a citation list that lives in an unattached Orientation. Fix: strip the meta-status, gloss each code at first use, and append the verified reference list.

17. **R:8, R:13, R:25–31.** "The target: solving the Schrödinger equation" and "the answer is known to be no (QMA-hardness)" overstate both ambition and complexity theory; the "where it stands" paragraph says X6/X7 are "next" and g "is measured nowhere", then reports g = 2.84 in the same paragraph. Fix: reword the target as the annex does and rewrite the status paragraph as of 16 September.

18. **R:70 (X18), absent from A.** The per-family transfer result (C–H stretch 0.27 cm⁻¹ RMS benzene→naphthalene, C–C stretch fails, lead D loses as a whole-correction route) is the most spectroscopy-relevant finding in the folder and is missing from the annex. Fix: add it as item 8 with its stand-in caveat.

19. **C:35 vs C:24; C:36; C:35 last sentence.** §3 still quotes lever A as 2.1–4.7 after 3.34 was measured; "step 4 (measure g …)" points at the wrong §4 item; "a training set at pyrene size … does not" is ambiguous. Fix: update the factor, fix the cross-reference, and finish the sentence.

20. **R:9 (2,087 s) vs C:11 (36 min); C:54 (2,087 s).** 2,087 s is 34.8 min, not 36. Fix: one figure, with the file that prints it.

**Closing.** The annex asks nothing of the supervisor — no question, no decision, no request to read anything beyond it — so its function (information, reassurance that scope is unchanged, or an invitation to comment) is left to be guessed. A busy reader can tell within one page that four things were "established" but not what the side project has found overall, because the operative conclusions (no cheap route from plan 06 itself, g unmeasurable at the anchor level, the real levers lie in plan 05, cost branch heading for closure) sit on page two in a dated update that contradicts page one. The sentence that most risks trust is A:18, "A citation chase over 873 works … finds the colouring literature never entering chemistry", a universal negative that an insider will test against their own memory and that the search method cannot support.

## Disposition (student, 16 September 2026 — decision 42 of plan 05: "Akkoord op al je adviezen")

- **Closing point and items 1, 4, 16, 18:** the annex gets an **opening paragraph** with the four outcomes in plain words (no cheap route from plan 06's own mathematics; g measured at 2.84/3.20 where measurable and the anchor-level cells unmeasurable on the laptop; the real levers are plan 05's G and H; the cost branch heads for its 15 October closing unless P25 is licensed) and **one question to the supervisor** (whether the side project continues as a tests-only line); X18 added as item 8; the meta-status stripped; codes glossed at first use; the verified reference list appended.
- **Items 2, 3, 5, 6, 7, 10, 11, 15:** one clarifying sentence each in the annex (what the stand-in tensor is; curvature locality vs pair-energy decay; the single operative g threshold 26.3 and the others labelled; the error budget the tests are read against; X14 as a count; the m/e marks carried in and the 15 September numbers quoted; the DZ-tight odd part named as a prerequisite of stacking G and H — now measured on 15 September at DZ tight, ≤ 2.4 µE_h on the b-modes with the factory modes and ≤ 0.001 after projection, to be cited; the X6 share defined).
- **Item 8 ("never entering chemistry"):** softened to "not found in the 873 works chased" with the search's limits, in the annex and the README.
- **Item 9 (the decision rule's overwritten expectation):** a §2b "outcomes" block added to the rule with the original expectation restored from git history; rows 15–19 updated.
- **Items 12, 19, 20 (numbers):** X15's sample size aligned after checking the X15 note; lever A's factor, the cross-reference and the unfinished sentence fixed in the cost ladder; 2,087 s = 34.8 min everywhere.
- **Items 13, 14, 17:** one sentence on what the Lean certificates protect (or the material moved out of the annex); the X7 threshold called lenient with the observation that would close T3 by 1 December; the README's target and status paragraph rewritten as of 16 September.
- **Disputed:** none.

