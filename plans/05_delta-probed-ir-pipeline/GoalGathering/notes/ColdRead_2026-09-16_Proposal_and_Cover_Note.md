# Cold read, 16 September 2026 — plan 05 proposal, cover note draft, Ladder §1–3

*A fresh reader (a separate model instance with no knowledge of the project's conversations) read the three files in full as the supervisor would — an insider, busy, sceptical, reading once — and reported at most 25 stumbles, ranked. Nothing was edited. The report is kept verbatim below; the disposition (what becomes a dated note before 26 September, what waits, what is disputed) is added by the student underneath, dated, after the user has read it. Files: P = `Project_Proposal_2026-09-06.md`; C = `notes/Cover_Note_Draft_2026-09-12.md`; L = `Frozen_Ladder_and_Tolerances_2026-09-14.md`.*

## The reader's report (verbatim)

1. **(b) The body and the 14-September revision disagree on what is promised.** P:605 opens §6 in bold with "No transferable, train-once spectrum model", P:642 repeats "Plan 05 builds no transferable model", and P:659–664 (decision 32) says the network "is not in the promised set and not in §1" — while P:95 (§1), P:387 (§3.5 "Pipeline A is the product: a network…") and P:657 make the network the reach deliverable; the title and P:20–25 still describe a per-molecule pipeline. Fix: decide which sentence governs, then rewrite §1, §6 and the title as one voice and move the superseded paragraphs to the history rather than leaving them in bold in the body.

2. **(f) Esposito et al. 2024 is twice attributed to the supervisor's own group.** P:38–39 ("the supervisor's own group built, with Mackie and later Esposito…") and P:46 ("from the supervisor's own group (Esposito et al. 2024, Table S1)") credit the NASA Ames paper to the reader's group; P:725 later gets it right (co-author on Mackie 2015/2016 and Maltseva 2016 only). Fix: attribute Esposito 2024 to Ames in §1 and keep the supervisor's co-authorship to the 2015/2016 papers.

3. **(a)(e) The central ask — cluster sponsorship — is one 90-word sentence with unsourced numbers.** P:1131–1134 bundles the request, "330,000–500,000 SBU" (unit never defined, derivation not shown, no statement whether it fits a "Small Compute application"), "a suitable machine in the supervisor's network", and "serving as or nominating the named expert" into a single sentence. Fix: split item 5 into three numbered asks and give the SBU figure a one-line derivation from the 38 h energy and the deck size.

4. **(b) Decisions 35, 36 and 37 are cited throughout but do not exist in §10.** P:873 says "§10, items 8–34", §10 ends at item 34 (P:984–990), yet decision 36 (which rewrites the promise) is cited at P:95, 387, 657, 1099, 1101, 1132, decision 35 at P:1084 and L:24, decision 37 at P:387 and L:79. Fix: add items 35–37 to §10 with their dates and update the count at P:873 and the "(all closed)" heading at P:882.

5. **(b) The Cost research question and the size sentence are orphaned by the thin decks.** P:399–401 (Cost question), P:488–489 (R2 "first off-diagonal-count ratio", R3 "size sentence decided here"), P:553–556 and P:1020–1025 all need K_off at pyrene and coronene, but P:95, 387 and 1099 now say full decks above naphthalene are out of reach and R2–R3 get diagonal-only decks. Fix: either restate the Cost question as R0→R1 only or say explicitly in §4 and §5.3 that the size sentence is now conditional on probe M3.

6. **(b) The cover note contradicts itself and the proposal it summarises.** C:17–23 says the network is "bewust niet beloofd" and "Dat netwerk zelf beloof ik in dit plan niet"; the replaced paragraph C:32 calls it "het netwerk waar dit alles naartoe werkt … getraind op wat betaalbaar gemeten is"; and C:37–39 describes item 3 in the 6-September wording ("spectra … die mijn zoektocht … heeft gemist") though P:1116 revised it on 13 September into a request for a measurement. Fix: rewrite C:17–23 and C:36–41 against the 14-September state of §1, §3.5 and §13.

7. **(b) The calendar is circular on its own hinge.** P:1069 dates the R1 probe batch 4 Dec 2026 and says it runs on Snellius or the desktop; P:1070 dates the cluster request 11 Dec 2026, "sized by the R1 timings"; P:1076 gives the defence as 21 May 2027 while P:1101 says "end of March 2027". Fix: move the R1 row after the request (or label it "R1 on the desktop only") and give one defence date per scenario.

8. **(c)(b) Two different objects are both called M3.** P:585 defines M3 as the side-project gradient milestone (benzene then naphthalene at cc-pVTZ); P:95, 387, 1099 and 1132 use "probe M3" for the cc-pVDZ-deck-with-transferred-increment test, despite P:572–573 already warning that M1 and M2–M5 are unrelated. Fix: rename the basis probe (e.g. "probe B1") everywhere.

9. **(c) Tokens used before or without definition.** P13 (P:255, 261), P18 (P:344), P24/P25/P26 (P:201, 984, 1087–1088), T-1/T-2 (P:95, 387), Q6–Q8 (only in L), τ₇ and η₈ (P:669), "line D" (P:203, absent from the §7 table), SBU (P:1132); in L: "B2 laptop", "B3 classification" (L:24, 27, 59). Fix: add one line each to the §1 terms paragraph (P:116–135) or drop the internal proposal numbers from the supervisor's copy.

10. **(d)(f) The reader cannot tell what degree this is or what supervising it entails.** P:3 says "Master's capstone", P:1064 "the Udacity rubric form", P:663 "the degree's rubrics … version 1.5.1", C:10 "Udacity capstone", with nine modules and administrative deadlines but no institution, credit weight or role named. Fix: one sentence in the header stating the programme, the institution and what the supervisor is being asked to be.

11. **(b)(d) What "fits the laptop" means changes between sections.** P:814–815: the 1,801-energy canonical Hessian (≈378 h) "does not" fit; P:1082 and 1099: the 448-energy R0 pilot (≈567 h) does; P:838 sets 168 h per batch as the cluster line; P:261 still says the R1 deck is "thirty weekly batches", arithmetic from the superseded 5,450 h. Fix: define "fits" once (memory, wall-clock or the 168-h rule) and recompute P:261 at 38 h.

12. **(d) The R0 pilot is priced on the no-prior deck.** P:243 says the symmetry-prior rerun reached threshold at 210 off-diagonal energies (K ≈ 270), yet P:1082 and C:32 price the pilot at 448 energies. Fix: state which deck the pilot runs and why, or reprice it.

13. **(b) The naphthalene noise measurement has three sizes.** P:743–746 and 1065: 72 energies, "not deliverable on the laptop"; L:24 and L:78 (decision 35): one mode, nine points; P:1084: "10 naphthalene tight energies", 4.8 laptop-days. Fix: pick one, cite decision 35 in §7 item 7, and delete the stale sentence at P:1065.

14. **(e) The sections the supervisor is asked to read critically are the least readable.** P:27–53 is two sentences of ≈200 words each; the §3.1 novelty table (P:197–204) has cells of 8–12 lines with dated insertions inside them. Fix: break P:44–53 into three sentences and move the dated additions out of the table cells into a short paragraph below it.

15. **(e) §3.3's bullet list has collapsed into one block.** P:288–358 carries " - *Smoothness.*", " - *Bias.*", " - *Reload.*" inline, interleaved with bookkeeping asides ("the result file's '×0.7' compares with…", P:332–334) that the reader does not need. Fix: restore the list breaks and move the cost-factor bookkeeping to a footnote.

16. **(e) Two sentences in §3.2 are broken.** P:241–243 ("11 of the 57 lie within blocks grouped as degenerate, ten true pairs and that one and the rerun…") and P:252 ("The arithmetic, at benzene's measured per-energy time … Two numbers, with different roles.") are fragments left by a dated insertion. Fix: re-read P:236–264 as prose and repair the two sentences.

17. **(d)(f) The 5.45 cm⁻¹ "upper bound" does not survive the basis line.** P:46–47 and 475–476 call the Esposito MAD an upper bound on what the anchor can buy, but P:348–349 reports basis terms of +2.8/−5.2/−11.1 cm⁻¹ on single modes, "of the size of the whole gap". Fix: say plainly that a MAD over families and a per-mode basis correction are different quantities and drop the "upper bound" reading or qualify it per family.

18. **(b)(f) Charge state appears once and is otherwise absent.** P:387 promises pipeline A "licensed per family and charge state", but P:20 restricts the plan to neutrals and L:47 says all rungs are neutral; for an AIB reader the cations are the point. Fix: either delete "and charge state" or add the sentence that says where a cation label would come from.

19. **(a)(f) The claim about the PAHdb paper is unsourced.** P:19 and P:1269 assert that Ricca et al. 2026 "leaves unquantified" its systematic uncertainties, with no section or quote, about a paper by the reader's close collaborators. Fix: quote or cite the passage, or soften to "does not report".

20. **(a) Unread papers are stated as mechanism in §1.** P:36–37 states Mata & Werner 2006's content as fact; P:202 and P:1256 say the full text is unread ("as described by Pinski & Neese"); Russ & Crawford 2004 and Subotnik & Head-Gordon 2005 (P:1270, 1280) are likewise unread but cited for the discontinuity mechanism. Fix: mark the reading status at P:36 or move the sentence to §3.1 where it is already marked.

21. **(f) Item 3 asks the reader's instruments for what the document says they cannot do.** P:1118–1119 says free-electron-laser jet-cooled lists carry ≥5–17 cm⁻¹ bandwidth; P:1121–1123 then asks for cold pyrene band centres to ≤1 cm⁻¹ from "an instrument in the supervisor's network". Fix: name the instrument class that could reach 1 cm⁻¹ (cavity/QCL as Brumfield 2012) so the ask reads as informed.

22. **(b) The document's own status line is wrong.** P:4 says "revised through 12 September"; P:95, 201, 203, 387, 657, 1099, 1116, 1132 carry 13/14-September revisions; P:1062 says it was sent 14 September 08:00; L:51 keeps a superseded table "as written" under a footnote that "governs". Fix: update P:4 to the real last date and, in L, mark the superseded rows in the table itself.

23. **(c)(b) The threshold-sensitivity line uses another program's vocabulary and a stale pair of settings.** L:78 writes "TightPNO−NormalPNO" and "CPS extrapolation" (ORCA/DLPNO terms) for an LNO code; P:770–771 defines the line as tight vs default, but P:331 moved the anchor to xtight without saying which two settings now define the line. Fix: name the two LNO threshold pairs the line compares and replace the PNO terms.

24. **(b) §1 misreports its own measurement.** P:73–74 gives the re-selecting program "0.05–2.7 µE_h at tight" settings; P:290 gives arm C 0.9–2.7 and arm B 0.05–1.2. Fix: quote arm C only in §1, or name both arms.

25. **(a)(b) Q9's arithmetic and inputs.** P:621 says "eight molecules, five sizes" (it is six sizes: C₆, C₁₀, C₁₄, C₁₆, C₁₈, C₂₄) and "no new coupled-cluster energy", but anthracene exists only as "a dated bonus" probe at P:834–836. Fix: correct the count and state that Q9 is conditional on the anthracene probe running.

Smaller items not ranked: "the table the student was asked for on 13 September" (P:1078) reads as if the supervisor asked; the Dutch "schatting" in the English table (P:1078, 1080); decision 20's "naphthalene factor owed" (P:939) is stale after P:335; whole-molecule R6 cost is 5,160 energies at P:407 and ≥2,580 at L:29; the blanket exclusion of aug-cc-pVTZ for aromatic rings on one reported artefact (P:434–435) will strike an insider as over-read.

**The ask.** The document asks the supervisor for a critical reading of §2–§3 and §7, a view on the fragment route, Module 05 and the gradient side project, either a laboratory source or a cold resolved pyrene measurement, sponsorship of a Snellius Small Compute request (with a named expert later), and — implicitly at item 16 — agreement to sign the scope. The asks are findable (§13 and C:36–41 both point at items 1, 3, 5), but the decisive one, item 5, is a single unparsed sentence whose SBU figures have no derivation, and the cover note's summary of item 3 describes the superseded wording. The single biggest risk of a "no" is that the reader cannot tell what they are being asked to sponsor: the body promises a per-molecule measured pipeline and disclaims a network in bold, the 14-September insertions make the network the product, the request is sized on a 474-energy deck that decision 37 has already decided to shrink — and the misattribution of Esposito et al. 2024 to the reader's own group on the first page spends credibility before any of that is reached.

## Disposition (student, 16 September 2026, after the user read the report on the train: "Akkoord op al je adviezen" — decision 42)

- **Items 1, 5, 7, 8, 9, 11–16, 22–25 and the smaller items:** resolved in the **consolidated reading copy** for 26 September (one voice for §1/§6/title; the Cost question restated as conditional on the DZ probe; the calendar re-ordered; the DZ probe renamed so that "M3" means one thing; the terms paragraph extended; the broken sentences repaired; the status line and the noise-measurement size made single). The dated original of 6 September stays unchanged apart from the notes below.
- **Item 2 (Esposito 2024):** corrected at once by dated note at both places in §1 (16 September).
- **Item 3 (the ask):** §13 item 5 split into three numbered asks with the SBU derivation on the decision-37 deck — in the reading copy.
- **Item 4 (decisions 35–37 missing from §10):** added in the reading copy with their dates; the count and the heading corrected there.
- **Item 6 (cover note):** rewritten against the 14–16 September state before 26 September (with P27's sentence and the cation rung).
- **Item 10 (what degree, what role):** one sentence in the header of the reading copy; the wording is the user's to confirm.
- **Item 17 (the 5.45 cm⁻¹ "upper bound"):** qualified per family in the reading copy, as the reader suggests.
- **Item 18 (charge state):** the cations enter explicitly as rung R1⁺ with the (T) port as its condition (P27 §5–6, decision 41).
- **Items 19–21:** the Ricca 2026 sentence softened to what was checked; the reading status of Mata & Werner 2006 marked at §1; the instrument class named in item 3 of §13 — all in the reading copy.
- **Disputed:** none. The reader's ranking is accepted as the order of work.

