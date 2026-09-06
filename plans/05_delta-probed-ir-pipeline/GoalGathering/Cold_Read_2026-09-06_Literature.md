# Cold read 2026-09-06 — literature and PDF record of plan 05

**Reader.** A fresh reader with no earlier version of any file and no conversation history; no web
access; everything below was checked against files on disk only (plan documents, `Papers\_txt\*.txt`,
`Papers\_img\*.png`, and, where a text file did not exist, text extracted locally from the PDF with
`pypdf` into the session scratchpad — Kitzmiller 2024, Lam 2020, Zhang 2024, Mai 2025, Mulas 2018,
Madriaga & Crawford 2025, Williams 2024, Boese 2005, plus the first page of every new PDF).

**Scope.** Brief `Review_Brief_2026-09-06_ColdRead_Literature.md`: is every literature mention in plan
05 correct, consistent across files, and honest about what was read; does the PDF record match the
folder; does anything say PDFs are in the repository; are sealed values printed.

**Files read** (in the brief's order). `Relevant_Scientific_Papers.md` (all 397 lines);
`Project_Proposal_2026-09-06.md` (all 840); `Frozen_Ladder_and_Tolerances.md` (all 734);
`Overarching_Goal.md`, `Frozen_Lines_to_Beat.md`, `Compute_Budget_2026-09-03.md`,
`Distilled_Project_Plan_and_Quality_Checks.md` (every line carrying an author name, item number,
DOI, "recall" or "sealed", with context); the four research notes (same method; §§8–9 of the
2026-09-03 note read in full); `PDF_Request_2026-09-06.md` (all); `probes/README.md`, plan `README.md`,
repository `README.md`, `plans/README.md`, `Papers_Inventory_2026-09-06.md` (literature and layout
lines); `Uitleg/*.md` (literature mentions only); the `Papers\` folder listing, `Papers\README.md`
(local, untracked), `.gitignore`, `git ls-files`, `git rev-list --objects --all`.

**Checks run.** A coverage, B identifiers, C status honesty, D fact spot checks (31, table at the
end, including the two Joblin scans read from the page images), E attribution drift, F the PDF
record, G recall risk, H sealed values. Each is reported in its own section after the findings.

**Counts.** BLOCKING 4 · MAJOR 13 · MINOR 12.

---

## Findings

### BLOCKING

**1. Esposito et al. 2024 is presented as a hybrid CC-harmonic / DFT-anharmonic study "on naphthalene". The paper on disk is not that.**
- `Project_Proposal_2026-09-06.md` line 106–109: "The hybrid quartic-force-field literature (Boese,
  Klopper & Martin 2005; Bégué, Carbonnière & Pouchan 2005; and, on naphthalene, Esposito et al.
  2024) puts the coupled-cluster level in the **harmonic** constants and leaves cubic and quartic
  constants at DFT level."
- Same claim: `Overarching_Goal.md` line 154–155 ("items 14, 27, and the Esposito 2024 naphthalene
  work, item 45"); `Distilled_Project_Plan_and_Quality_Checks.md` line 53 ("Hybrid CC/DFT QFFs (bib
  14, 27, 45) | CC harmonic + DFT anharmonic on small molecules and naphthalene");
  `Relevant_Scientific_Papers.md` line 65, item 45 ("CC used for harmonics only, DFT QFF for
  anharmonics — … the allocation precedent on a PAH"); `Research_Note_2026-09-03_Delta_Probing.md`
  line 230 ("The hybrid-QFF literature (items 14, 27, 45)").
- What is wrong: `Papers\_txt\esposito2024.txt` lines 258–266 — the anharmonic QFF and VPT2 are
  entirely B3LYP/N07D; CCSD(T)-F12b/cc-pVTZ-F12 appears only as a **benzene harmonic-frequency
  comparison in Table S1** ("Table S1 compares the harmonic frequencies of benzene computed using
  the DFT-based B3LYP/N07D and the wave function-based CCSD(T)-F12b/cc-pVTZ-F12 levels of theory …
  mean absolute difference of only 5.45 cm−1"). Line 253–257: "computing the anharmonic frequencies
  of PAHs using correlated wave function methods is inaccessible … as such, DFT methods are the most
  viable option." No coupled-cluster force constant of any kind enters their spectra, and nothing
  coupled-cluster is done on naphthalene. The paper is therefore not a precedent for the harmonic-
  first allocation; the author's own 2026-09-06 reading (bib line 184) already says the MAD is
  benzene-only, but the "allocation precedent" reading of item 45 was left standing in five files.
- Fix: strike Esposito from the hybrid-QFF precedent list everywhere (proposal §2, Goal, Distilled
  row, bib item 45 "Use" column, note §9); keep item 45 for two things only — the benzene MAD 5.45
  cm⁻¹ and the PAHdb-anharmonic protocol. The allocation precedent rests on items 14 and 27 (and item
  27's full text is unread).

**2. The Ladder's expected-effect line quotes a naphthalene number that the author's own reading shows is benzene-only.**
- `Frozen_Ladder_and_Tolerances.md` line 639–641 (§4 item 2, binding): "the literature scale of Δ₂ at
  R1 is ≈ 5 cm⁻¹ mean absolute harmonic difference (item 45, **snippet grade**, verify-on-use)".
- Also `Overarching_Goal.md` line 232 ("~5 cm⁻¹ harmonic difference (item 45, snippet grade") and
  `Uitleg/09_Module_04_Baseline.md` line 72 ("ongeveer 5 cm⁻¹ groot CC−DFT-verschil per familie").
- What is wrong: `esposito2024.txt` line 260–265 — the 5.45 cm⁻¹ (0.59 %) figure is benzene, B3LYP/N07D
  vs CCSD(T)-F12b/cc-pVTZ-F12, harmonic. There is no naphthalene number in the paper. The bib's
  reading (line 184) says exactly this and the proposal's Risk 4 was corrected, but the binding
  document still says "at R1", still says "snippet grade", and carries no dated note.
- Fix: dated note in the Ladder rewriting item 2's line to "benzene, 5.45 cm⁻¹ MAD, B3LYP/N07D vs
  CCSD(T)-F12b/cc-pVTZ-F12 (item 45, read in full 2026-09-06); no literature figure exists at R1 —
  the R1 expected effect is a stated expectation, not a citation"; same correction in the Goal and
  the Uitleg.

**3. The proposal's reference list says the temperature-term source was never opened, while its body says it was read in full.**
- `Project_Proposal_2026-09-06.md` line 800–801: "Joblin, Boissel, Léger, d'Hendecourt & Défourneau
  1995, Astron. Astrophys. 299, 835. (PAH band shifts with temperature; reference known, not yet
  opened.)" — versus line 367–368: "All of these sources were read in full on 6 September 2026 and
  their conditions transcribed" and line 371–373 ("the hot-band slopes of Joblin et al. 1995 replace
  the earlier recalled floor").
- Same pattern: line 790–792, Chu 1999 "(… Crossref record; read by the scoreboard module before any
  uncertainty is printed.)" and line 824–826, Schneider 2024 "(… naphthalene among them, 25 °C,
  0.1 cm⁻¹; Crossref record; read by the scoreboard module.)" — both read in full per the body (line
  367) and the bib (items 56, 57); the Schneider entry also states 25 °C flatly where the body (line
  361) says "25 or 50 °C — the paper states both".
- What is wrong: a supervisor reading the reference list is told the paper the temperature term rests
  on was not opened. One of the two statements is false; the readings section of the bib (lines
  272–327) and the page images show the paper was read.
- Fix: update the three annotations to "read in full 2026-09-06 (ADS scan / nvlpubs / OSTI author
  manuscript)"; Schneider: "25 °C (§2.3) or 50 °C (Fig. 6 caption); 0.112 cm⁻¹".

**4. "Bowman and co-workers, 2024" is cited in the proposal's novelty table with no reference-list entry and no bibliography item.**
- `Project_Proposal_2026-09-06.md` line 150: "Δ-machine learning of potential-energy surfaces (e.g.
  Bowman and co-workers, 2024; transfer learning to CCSD(T), Käser & Meuwly 2021)".
- The only trace is `Relevant_Scientific_Papers.md` line 146, a novelty-search result line: "Δ-ML of
  DFT-based potentials to CCSD(T) (Bowman group, JCTC 20, 8807 (2024); ethanol)" — a search-result
  identifier, no DOI, no author list, no status.
- What is wrong: an unverifiable citation in the document sent to the supervisor, against the
  repository's own rule (bib line 3: "Do not cite from recall in a scored document").
- Fix: either add a verified item (Crossref/arXiv, with the actual author list) or replace the name
  with the verified Käser & Meuwly item alone.

### MAJOR

**5. "Five" jet-cooled 6–15 µm coronene bands — the table on disk has six.**
- `Project_Proposal_2026-09-06.md` line 366–367 ("plus five jet-cooled 6–15 µm bands (Lemmens, Rijs &
  Buma 2021)"); `Frozen_Ladder_and_Tolerances.md` line 59 ("five jet-cooled 6–15 µm bands exist
  (item 62…)") and line 138–139 ("five tabulated 6–15 µm bands"); `Frozen_Lines_to_Beat.md` line 94
  ("coronene, five 6–15 µm bands"); origin `Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md`
  line 51 ("five strongest 6–15 µm bands … 854.6, 1132.1, 1208.1, 1306.4, 1607.1").
- `Papers\_txt\lemmens2021.txt` lines 588–599 (Table A1): 121.1, 381.1, 549.2, **770.1**, 854.6,
  1132.1, 1208.1, 1306.4, 1607.1, 1694, 1774.4, 1902.8. Within 6–15 µm (667–1667 cm⁻¹) there are six
  fundamentals: 770.1 (13.0 µm, rel. int. 0.21), 854.6, 1132.1, 1208.1, 1306.4, 1607.1. The bib's own
  transcription (line 335–337) lists 770.1 and the cross-check table (line 346) uses it as the
  "13.0 µm" row — the scout's count of five was never corrected upstream.
- Fix: "six" in the four places, or list the bands.

**6. Kitzmiller's ±28 cm⁻¹ is pyridine; the proposal makes it "aromatic ring modes".**
- `Project_Proposal_2026-09-06.md` line 133–135: "its own result — that diagonal-only recovery fails
  on aromatic ring modes by up to ±28 cm⁻¹, because DFT and coupled-cluster mode compositions differ
  there — is the strongest evidence for the plan's design choices."
- Bib item 43 (line 63) has the qualifier: "pyridine errors to ±28 cm⁻¹; benzene, pyrrole, furan
  flagged". Kitzmiller text (scratch extract, lines 634–639): "CMA-0A might generally encounter
  difficulties with aromatic ring vibrations … our work has also found some moderate residuals **up to
  5 cm⁻¹** in size for these types of vibrations in benzene, pyrrole, and furan"; line 640: "pyridine
  is an abnormal case".
- What is wrong: the qualifier "pyridine" and the 5 cm⁻¹ figure for the benzene-type rings are
  dropped in the sentence that calls this "the strongest evidence".
- Fix: "fails on pyridine's ring modes by up to ±28 cm⁻¹ and leaves residuals up to 5 cm⁻¹ on
  benzene, pyrrole and furan".

**7. Bibliography statuses were not brought up to date after the 2026-09-06 readings.**
- `Relevant_Scientific_Papers.md` line 65, item 45 status column: "the MAD figure is **snippet grade**
  (full text 403) — verify-on-use" (read in full, line 184); line 47, item 28: "full text not read"
  (read, line 185); line 64, item 44: "full text read by the Round-7 Pass B reviewer" only (author
  read, line 183); line 153: "the 2026 CMA paper is added to the reading list (not yet fetched:
  paywalled)" (held and read, lines 178, 182); line 39, item 20: "**NOT FETCHED** (debt 4…)" and
  line 93, Named debt 4 "Joblin-era T-dependence references (item 20)" (paid, items 52/64); Method
  debts lines 101–106 ("Full texts of items 27, 28, 37 …", "item 44's full text re-read by the
  author") and 132–133 ("Item 45's MAD figure and mode-resolved table (full text) before the
  expected-effect line is written") — all still listed as owed; line 137 "**Status.** Working
  bibliography after the 2026-09-03 search pass".
- Same staleness downstream: `Frozen_Lines_to_Beat.md` line 94 ("author's read owed") and §7 debt 4
  (line 114); `Uitleg/08_Module_03_Scorebord.md` line 34–35 ("hot-band-literatuur (items 52–53, 60)
  … Nog niet gelezen"); `Uitleg/15_Bijproject_en_Reviews.md` line 84.
- Fix: one pass over the item table, both debt lists and the Status line; a dated line in
  Frozen_Lines §7; the two Uitleg sentences.

**8. The Goal's glossary — which "wins on drift" — still defines the temperature term by the recalled values the Ladder retired.**
- `Overarching_Goal.md` line 70–71: "**u_296** the per-molecule 0 → 296 K term (1 / 3 / 5 cm⁻¹ at
  benzene / naphthalene / R2, recalled), **χ_max** = 0.03 cm⁻¹ K⁻¹ (recalled) its unpinned slope".
- `Frozen_Ladder_and_Tolerances.md` line 9–10: "Agrees with Overarching_Goal.md, whose glossary
  defines every symbol used here; the Goal file wins on drift." Ladder line 153–164 (dated note
  2026-09-06): χ_max is exceeded (coronene 6.2 µm −0.038/−0.044, verified on `joblin1995-04.png`),
  the 6–15 µm floor is 0.044, and u_296 is per family from item 52's model.
- What is wrong: by the plan's own precedence rule the stale glossary is the binding definition.
- Fix: dated glossary update in the Goal pointing to the Ladder note and the bib table.

**9. The 2026 CMA paper has no bibliography item, and the bib describes it three different ways.**
- Cited in `Project_Proposal_2026-09-06.md` line 148 and 798–799 (with DOI), `Frozen_Ladder_and_Tolerances.md`
  line 437 ("reading … of the 2026 CMA paper, 2026-09-06"), bib lines 145, 153, 178, 182; `PDF_Request`
  item 9. No numbered item; no status cell; the DOI appears only in the proposal and the request.
- Internal disagreement: line 145 "CCSD(T)/aug-cc-pVTZ targets (abstract via search snippet;
  paywalled)"; line 178 "open at the publisher but bot-blocked"; line 182 "(CMA, intermolecular;
  CC-BY) — read in full". `cma2026.txt` line 74: "This article is licensed under CC-BY 4.0"; line
  19–25: targets are CCSD(T)/aug-cc-pVTZ **or h-aug-cc-pVTZ**, Level B MP2/h-aug-cc-pVTZ.
- Fix: add item 65 (Olive Dornshuld, Lahm, Kitzmiller, Allen & Schaefer III, JPCA 130, 3249 (2026),
  DOI 10.1021/acs.jpca.6c00689, CC-BY, read in full 2026-09-06); re-word lines 145 and 153.

**10. The supervisor is asked for a paper whose open preprint the bibliography already records.**
- `PDF_Request_2026-09-06.md` header line 3 ("Nog van de begeleider nodig: … 10 …") and item 10
  (Wang, Luo, Wang & Liu 2025, O1NumHess); `Relevant_Scientific_Papers.md` line 178: "**Closed, no
  author manuscript found**: … Wang 2025".
- Versus bib line 42, item 23: "arXiv:2508.07544 … **OK (2026-09-03; arXiv abstract + HTML full text;
  Crossref)**".
- Fix: fetch the arXiv PDF into `Papers\`, strike item 10 from the request, correct line 178.

**11. Compute_Budget misreads a CMA-2 percentage as a count of off-diagonals.**
- `Compute_Budget_2026-09-03.md` line 59: "CMA-2: ~33 selected off-diagonals on small molecules
  (bib 43, fetched)".
- Kitzmiller abstract (scratch extract line 26): "a cutoff of ξ = 0.02 provides an average maximum
  absolute error per molecule of only 0.17 cm−1 by incurring merely a **33% increase in average cost**
  over CMA-0A"; Table (line 487) lists 33 as that percentage. Bib item 43 records no "33". Nothing in
  the extract gives 33 as a number of selected elements (the pyrrole-ethanol example uses n = 12 and
  n = 63, line 1004).
- Fix: replace with what the paper says (cost +33 % at ξ = 0.02; per-molecule counts vary) or drop it.

**12. Numbers in the Budget and the Distilled plan that the bibliography's record of the reading does not contain.**
- `Compute_Budget_2026-09-03.md` line 60 and `Research_Note_2026-09-03_Delta_Probing.md` line 225–226:
  O1NumHess "worst covalent case a conjugated polyene, MAD 6–12 cm⁻¹ (bib 23, fetched)". Bib item 23
  (line 42) records "~100–124 gradients; ~2× conventional error" as the numbers taken from the full
  text — not 6–12 cm⁻¹ and not the polyene. The paper is not held (bib line 178 lists it as closed;
  see finding 10).
- `Distilled_Project_Plan_and_Quality_Checks.md` line 50: CMA "molecules to ~17 atoms; diagonal-only
  fails on aromatic ring modes by ±20–28 cm⁻¹". Bib 42–43 record neither figure; in the Kitzmiller
  extract I found 23.1 and 28.2 as table maxima (lines 299, 305) but no "17 atoms".
- Fix: add the numbers to the bib item with their page, or remove them from the Budget/Distilled.

**13. Lam 2020 is quoted with numbers while its status is "record (plan-02)".**
- `Distilled_Project_Plan_and_Quality_Checks.md` line 48: "Lam 2020 (bib 13) | QM harmonic + ML
  anharmonic, 37 small molecules, RMSD 21–23 cm⁻¹". Bib item 13 (line 32): "**record (plan-02)**", no
  volume, no page, no reading; PDF held since 2026-09-06 with no "read" line.
- The numbers are right: Lam PDF abstract (scratch extract lines 15–18) "37 molecules … RMSD of
  21 cm−1 … experimental results with a RMSD of 23 cm−1". So the fix is the status, not the numbers.
- Fix: item 13 → "JCTC 16, 1681 (2020) [from the held PDF's first page: verify]; abstract read from
  `Papers/` 2026-09-06; the 37 / 21 / 23 figures are from the abstract".

**14. "Sealed" raw energies are plaintext JSON files tracked in git and pushed to the public remote.**
- `Project_Proposal_2026-09-06.md` line 525–526: "the raw displaced energies of probe M1 are sealed
  for the same reason, and this proposal quotes only differences"; `Frozen_Ladder_and_Tolerances.md`
  line 389–391: "M1's raw displaced energies are not printed: they go to the same hashed, sealed
  file"; `probes/results_m1/*/REPORT.md` line 5: "raw energies sealed: `m1_sealed_energies.json`,
  sha256 … — not printed".
- `git ls-files` lists sixteen `m1_sealed_energies.json` / `canonical_truth_sealed.json` (+ .sha256)
  files under `probes/results_m1/` (last commit 8e2017e); the remote is
  github.com/thebreadishard/udacity-capstone-plan; `.gitignore` deliberately un-ignores
  `results_*/**/*.json`. The JSON is plain floats keyed `e_scf`, `e_corr_lno_ccsd_t`,
  `e_corr_lno_mp2`, `e_corr_mp2_full` per arm and point (structure inspected; no value copied here).
  The `.sha256` sidecar proves the file was not altered; it does not stop anyone — including the
  pilot-note author — from reading it.
- No Markdown file prints an absolute energy (a search for −2xx.xxxxxx patterns over the plan folder
  returns nothing), so the printing rule holds; the word "sealed" does not.
- Fix: either encrypt the files (or keep them outside the tree, hash in the repo) or re-word every
  "sealed" as "hash-committed, readable — the author has undertaken not to open it before the note".

**15. Proposal author initials: the stated rule is not followed, and three sets could not have come from any file on disk.**
- `Project_Proposal_2026-09-06.md` line 775–776: "author initials are given only where the working
  bibliography records them". The bibliography records initials for none of the twelve entries that
  carry them (Altun, Bégué, Esposito, Fusè, Olive Dornshuld, Kitzmiller, Lahm, Madriaga, Sanders,
  Wang, Williams, Zhang).
- Nine sets match the held PDFs' first pages (checked: Altun, CMA 2026, Kitzmiller, Esposito, Fusè,
  Madriaga, Williams, Zhang). **Bégué, D., Carbonnière, P., Pouchan, C.** (line 781), **Lahm, M. E.,
  Kitzmiller, N. L., Mull, H. F.** (line 804) and **Wang, B., Luo, S., Wang, Z., Liu, W.** (line 830)
  are papers listed as closed and not held (bib line 178) whose Crossref records, per the bib, gave
  "author list verified" without initials — the initials appear only where they could not be fetched
  (brief, check C). (Lahm's co-authors' initials are consistent with the Kitzmiller 2024 PDF, which
  may be the actual source.)
- Fix: drop initials from the three, or record the Crossref author strings in the bib and cite them.

**16. Käser & Meuwly 2021 has four authors on the held PDF.**
- `Relevant_Scientific_Papers.md` line 35, item 16: "Käser & Meuwly, arXiv:2103.05491"; line 163 (PDF
  table): "Kaeser_Meuwly_2021_…"; `Project_Proposal_2026-09-06.md` lines 150, 838: "Käser & Meuwly
  2021"; `Research_Note_2026-09-03_Delta_Probing.md` line 44.
- First page of `Papers\Kaeser_Meuwly_2021_transfer_learning_CCSDT_JCTC17_3687.pdf` (and of the
  byte-identical `04_Kaser2021_TransferLearning_CCSDT.pdf`): "Silvan Käser, Eric Boittier, Meenu
  Upadhyay, and Markus Meuwly". `Papers\README.md` (local) already recorded on 2026-08-23 that this
  file's author list had been wrong in an earlier bibliography.
- Fix: "Käser, Boittier, Upadhyay & Meuwly 2021" in item 16, the file name, and the proposal.

**17. The PNNL naphthalene record's temperature is carried as 25 °C in tables that have no dated note, and the paper's own framing is 50 °C.**
- `Frozen_Lines_to_Beat.md` line 92: "25 °C, 0.1 cm⁻¹, 760 Torr N₂-broadened composite spectra";
  `Frozen_Ladder_and_Tolerances.md` line 57 (R1 row): "(25 °C, 0.1 cm⁻¹, 760 Torr N₂; items 57 and
  59…)"; `Uitleg/08_Module_03_Scorebord.md` line 29; `PDF_Request` item 3.
- `schneider2024.txt` line 213 ("White cell thermostatted at 25 ◦C"), line 716 (Fig. 6 caption,
  "Resultant composite spectra (50 ◦C)") — both recorded in the bib (line 228–232) — **and line 89,
  not recorded**: "quantitative 50 ◦C gas-phase IR spectra for those compounds", i.e. the paper
  introduces its products as 50 °C spectra. Resolution is 0.112 cm⁻¹ (line 113), not 0.1.
- The Ladder's dated note (v) (line 176–179) covers the Ladder; Frozen_Lines, the Uitleg and the
  request carry the 25 °C reading with no note.
- Fix: dated line in Frozen_Lines §5; add line 89 to the bib's reading of item 57 (it tilts the
  default towards 50 °C until the record header says otherwise); "0.112 cm⁻¹".

### MINOR

**18.** `Project_Proposal_2026-09-06.md` line 775: "verified by Crossref, arXiv or full text on 2–5
September 2026 unless marked otherwise" — the CMA 2026 paper, and every "read in full" claim in the
list, date from 6 September. Fix: "2–6 September".

**19.** Reference-list drift: line 788–789 Brumfield "content at abstract grade" vs bib item 63
"snippet grade … band origin not read"; line 834 Zhang "arXiv:2404.03129" only, while bib item 33
gives JCP 161, 014109 (2024); Joblin et al. 1994 (item 64) supplies the "hot spectra" of line 373–374
and the cross-check but has no entry. Fix: align the three.

**20.** `Project_Proposal_2026-09-06.md` line 369–370: "the benzene intensities are certified outside
1325–1900 cm⁻¹ only" — `chu1999.txt` line 437–438 also excludes 3550–3950 (H₂O), and the bib (line
211–212) adds CO 2050–2225 and CO₂ 2295–2385. No scored band is affected; the sentence over-claims.

**21.** `Project_Proposal_2026-09-06.md` line 360–361 "PNNL … at 0.1 cm⁻¹" — 0.112 cm⁻¹ (finding 17).

**22.** `Project_Proposal_2026-09-06.md` line 180–182: naphthalene's 48 modes "from the textbook D₂h
assignment … 9a_g + 3b_1g + 4b_2g + 8b_3g + 4a_u + 8b_1u + 8b_2u + 4b_3u" — no source named (the sum is
48; the deck recomputes it, so the risk is presentational). Fix: "(deck's own analysis; the count is
reproduced by the standard D₂h assignment)".

**23.** `Frozen_Ladder_and_Tolerances.md` line 363–366: "[E_MP2(full) − E_MP2(LNO)] … the LNO
literature's standard correction for the truncated space" — a literature statement with no item.
Fix: cite item 34 (Nagy & Kállay 2019) or the pyscf-forge code (item 48).

**24.** `Project_Proposal_2026-09-06.md` line 312–313: "aug-cc-pVTZ is excluded for benzene-type rings
by a documented linear-dependence artefact" — the document (CMA 2026, `cma2026.txt` line 192–196,
"ω8(b2g) ring puckering … spurious frequency of 495i cm−1") is not named in that sentence.

**25.** `plans/README.md` line 122–125: "Three folders sit at the repository root and are **shared
dumps** … `Papers/` — reference PDFs. Literature is a dump; the current plan's bibliography is the
index." Read cold, this says the repository contains a PDF folder. The root `README.md` (line
121–122, 130–133) is correct ("local only, git-ignored since 2026-09-06"). Fix: same wording in
`plans/README.md`. (Also stale there, line 117: plan 05 "probes owed, none run".)

**26.** `Papers\` housekeeping: `Kaeser_Meuwly_2021_…pdf` is a byte-identical duplicate (799,949 B)
of `04_Kaser2021_…pdf`; `12_Mai2025_MLMD_PAHs.pdf` (MNRAS OA typeset) and
`Mai_2025_MLMD_PAH_MNRAS541_3073.pdf` (arXiv v3) are two versions of one paper; the local
`Papers\README.md` (untracked) still describes 37 files under plan 03's numbering. Not a tracked-file
problem; noted so the "PDFs held locally" table stays the single index.

**27.** Identifiers left incomplete where the held PDF's file name asserts them: item 16 has no
journal (file name says JCTC 17, 3687); item 13 has no volume/page (file name says JCTC 16, 1681).
Neither can be verified from the arXiv manuscripts on disk; either verify the journal record and
write it into the item, or take the numbers out of the file names.

**28.** `Research_Note_2026-09-03_Delta_Probing.md` line 122–123 quotes Bégué 2005 "mean deviations
under 0.8 %" in place; §9 (line 194–196) labels it "from a search snippet". Add the label at line 123
so a reader of §4.4 alone sees it.

**29.** `Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md` line 19–20 and 53: "Chakraborty et al.
2019 Table 2 quotes Joblin χ' values for pyrene bands at 709, 750, 1096, 1435 cm⁻¹". Joblin 1995
Table 1 (`joblin1995-04.png`) has pyrene slopes at 3.3, 8.5 and 12 µm only; whatever Chakraborty
2019 tabulated for those four bands is not Joblin 1995's Table 1. Superseded by the direct
transcription; note it so the "Joblin values" in that row are not re-used. Separately, that note's
Chakraborty 2019 (JPCA 123, 4139; KBr) and bib item 60's Chakraborty arXiv:2102.06582 are two
different papers both cited as "Chakraborty".

**30.** `Relevant_Scientific_Papers.md` line 262–263: "±20 % stated in §3.2.3" for Tables 4–6 of
Joblin 1994. On `joblin1994-09.png` the 20 % is stated for the repeat measurement of the 11.8 µm
coronene band ("found the same value within a 20% uncertainty"), not as the uncertainty of every
entry. Label it "the only stated uncertainty (11.8 µm repeat)".

**31.** `Uitleg/02_Natuurkunde_Trillingen_en_Licht.md` line 101–102 ("laat de literatuur zien dat het
grootste deel van het verschil … in de harmonische term zit") and `Uitleg/13_Module_08_Synthese.md`
line 106 / `Uitleg/16_Checklist_Mapping_Pass_6.md` line 125 ("de bibliografie telt zestig items" /
"60 items"; the table has 64 plus the CMA 2026 paper). Lay text; align the count and, after finding
1, the claim's source (items 14 and 27 only).

---

## Checks, as run

**A. Coverage both ways.** Every reference-list entry in the proposal is cited in its body (26
entries checked one by one). Body citations without an entry: "Bowman and co-workers, 2024"
(finding 4); Joblin 1994 by content (finding 19). Author-year/item mentions outside the bibliography
resolve to an item in every file checked, with two exceptions: the 2026 CMA paper (no item, finding
9) and "Chakraborty 2019" in the R2 note (finding 29). Bibliography items leaned on by plan documents
are all present; none orphaned.

**B. Identifier consistency.** Compared across files for 28 papers (journal, volume, page, year, DOI):
Esposito, CMA 2026, Altun, Kitzmiller, Lahm, Madriaga, Sanders, Wang, Williams, Mai, Mulas, Chu,
Schneider, Sharpe, Pirali, Joblin 1994/1995, Lemmens 2019/2021, Brumfield, Bos, Boese, Bégué, Fusè,
Ricca, Bauschlicher, Mattioda, Zhang. Disagreements: Zhang (journal omitted in the proposal), Käser
author list (finding 16), items 13/16 incomplete vs their file names (finding 27), CMA 2026 basis and
access described three ways (finding 9). DOIs agree everywhere they appear twice; the CMA 2026 and
Esposito DOIs match the PDFs' own text.

**C. Status honesty.** Claims stronger than status: Lam numbers on a "record" item (13); O1NumHess
MAD 6–12 and CMA "~17 atoms / ±20–28" not in the bib's record of the readings (12); the "~33
off-diagonals" (11); initials for three unheld papers (15); the proposal reference list understating
its own readings (3); the Ladder's "snippet grade" for a paper read in full (2); the "allocation
precedent" reading of item 45 that the full text does not support (1). Statuses that are honest and
labelled: items 25, 27, 41, 46, 50, 51, 53, 58, 59, 63 (snippet/abstract/Crossref, with the limit
stated each time); the "recalled" labels in the Ladder (lines 96–98, 259, 266, 288) and the Distilled
row 139.

**D. Fact spot checks.** 31 facts checked against the texts and the two scans; 29 verified, 2 partly
(table below). The Joblin 1995 Table 1 and Table 2 transcription and the Joblin 1994 Table 1, 2, 4,
5 transcriptions in the bib are exact to every entry I compared.

**E. Attribution drift.** Found: Esposito → hybrid on naphthalene (1); 5 cm⁻¹ MAD at R1 (2); pyridine
→ aromatic ring modes (6); five → six coronene bands (5); 25 °C only (17); 0.1 vs 0.112 cm⁻¹ (21);
certified-region list truncated (20); 33 % → 33 elements (11); ±20 % blanket (30). Not drifted: the
0.044 floor, the 10–19 cm⁻¹ cold–hot disagreement, the +6.5 / +17–18 model expectation, the 3.3 %
(k = 2) benzene intensity, the 0.0042 cm⁻¹ RMS, the 0.002–0.06 µE_h scatter — consistent across the
proposal, Ladder, bib and probes README.

**F. The PDF record.** The "PDFs held locally" table (16 rows) plus the four user downloads = 20 new
files; all 20 are in `Papers\` under the names given, and every stated page count matches `pypdf`
(8, 42, 70, 17, 13, 7, 23, 10, 11, 29, 32, 10, 16, 12, 14, 13, 12, 8, 11, 18). The 37 older files of
the Inventory are all present locally (01–37, no 25). `PDF_Request` header vs the bib's line 178:
consistent, except Wang 2025 (10). `Papers_Inventory`: `git rev-list --objects --all | grep -i
'\.pdf$'` returns 0 objects and `git ls-files Papers` is empty, so its "no PDF in any commit" holds
in this clone. Tracked files that say or imply PDFs are in the repository: none in the root README
(rewritten correctly, lines 121–133); `plans/README.md` line 125 still reads that way (25).
`.gitignore` carries `Papers/` with a correct comment.

**G. Recall risk.** Unlabelled literature statements without file, item, DOI or "recalled":
proposal line 150 Bowman (4); proposal line 181 "textbook" D₂h assignment (22); Ladder line 365
"LNO literature's standard correction" (23); proposal line 313 "documented" artefact (24); Uitleg 02
line 101 and 09 line 72 (31, 2); Delta-probing note line 122 in place (28). All other recalled
figures I met are labelled "recalled" (χ_max, u_296, the 250 °C lightpipe default, the Δ₁·p size, the
0.5–2 cm⁻¹ geometry term, the 0.1–1 cm⁻¹ quartic bias, QM9's size range).

**H. Sealed values.** Every "sealed" mention (Ladder 288, 367, 390, 473, 480, 632; proposal 522, 526;
Distilled 88, 174; Budget 200, 221, 230; probes README 40, 59, 97, 141, 158; M1 note 8, 17, 152, 154;
the four `results_m1` REPORT/CANONICAL_COMPARISON files) is surrounded by differences, σ's,
fit-derived biases or hashes only; no absolute energy or diagonal Δ₂ is printed in any Markdown file.
The sealed JSON files themselves are tracked and public (14).

---

## Spot-check table

| # | Fact as stated in the plan (file, line) | Paper | Verified | The paper's line |
|---|---|---|---|---|
| 1 | Benzene coefficients corrected to 296 K and 760.0 Torr (bib 201–203; Ladder 175) | Chu 1999 | yes | `chu1999.txt` 268: "296 K and 1.013 3 105 Pa (760.0 Torr) using the ideal" |
| 2 | Nominal resolution 0.12 cm⁻¹, boxcar (bib 202–203) | Chu 1999 | yes | 42 "spectra at 0.12 cm –1 resolution"; 317 "a boxcar apodization function" |
| 3 | 158 water lines, RMS 0.0042 cm⁻¹ (bib 204–206; Ladder 175) | Chu 1999 | yes | 291–292 "root-mean-square deviation obtained for 158 … lines is 0.0042 cm –1" |
| 4 | Benzene expanded uncertainty 3.3 % (bib 207; item 56) | Chu 1999 | yes | 605 "Benzene 2.6 3 10–4 4.2 3 10–9 2.7 3 10–14 3.3 %" |
| 5 | Not certified in 1325–1900 and 3550–3950 cm⁻¹ (bib 211–212; Ladder 173) | Chu 1999 | yes | 437–438 "not certified in regions of the spectra where H2O [(1325–1900) cm–1 and (3550–3950)" |
| 6 | Nine transmission spectra (bib 200) | Chu 1999 | yes | 41 "was calculated using nine transmittance" |
| 7 | "effort … underway to improve the benzene results" (bib 208–209) | Chu 1999 | yes | 467–468 "An effort is currently underway to improve the benzene results." |
| 8 | 8.05 m White cell, 0.112 cm⁻¹, 256 scans (bib 223–224) | Schneider 2024 | yes | 263 "long-path cell (set to 8.05 m)"; 113 "resolution of 0.112 cm 1, co-adding 256 scans" |
| 9 | 25 °C in §2 and 50 °C in Fig. 6 caption (bib 229–231; Ladder 176–177) | Schneider 2024 | yes (+ line 89, see finding 17) | 213 "White cell thermostatted at 25 ◦C"; 716 "Fig. 6. Resultant composite spectra (50 ◦C)" |
| 10 | ±8 % (2σ) solids; 7 % liquid (bib 236–237) | Schneider 2024 | yes | 755 "± 8 % (2σ)"; 434 "liquid's disseminator value alone (7 %)" |
| 11 | Naphthalene in CS₂ only (bib 225–226) | Schneider 2024 | yes | 385 "naphthalene, which was analyzed only in CS2" |
| 12 | 1 ppm-m at 296 K composites; 748–766 Torr (bib 224, 227) | Schneider 2024 | yes | 298 "(1 ppm-m at 296 K, 1 atm)"; 121 "between 748 and 766 Torr" |
| 13 | FELIX bandwidth 0.5–1 %; T_rot ≈ 2 K (bib 332–333; Ladder 169) | Lemmens 2021 | yes | 137 "bandwidth of FELIX is 0.5%–1% of the IR frequency"; 192 "ballpark figure of 2 K" |
| 14 | Table A1 = 12 bands 121.1–1902.8 incl. 770.1 (bib 335–337) | Lemmens 2021 | yes (so "five" is wrong, finding 5) | 588–599: "121.1 0.004 … 770.1 0.21 … 854.6 1.00 … 1902.8 0.12" |
| 15 | GVPT2 unrealistic CH-oop shifts; drumhead 4 % off (bib 360–363) | Lemmens 2021 | yes | 171 "unrealistic frequency shifts"; 277 "drumhead mode, is 4% off" |
| 16 | FELIX ≈ 1 %; Table A.2 ≈ 30 tetracene bands 548–1970 (bib 338; item 61) | Lemmens 2019 | yes (34 rows) | 141–142 "about 1% of the photon frequency"; 786–826 Table A.2, 548.0 … 1968.6 |
| 17 | Ar matrix 15 ± 3 K, 0.5 cm⁻¹, >1000:1 (bib 367–368; item 4) | Mattioda 2020 | yes | 852 "temperature of 15 K (±3K)"; 168 "resolution of 0.5 cm −1"; 155 "excess of 1000:1" |
| 18 | Sum over 1550–500 cm⁻¹ scaled to computed A-values, "10–20 %", Eq. 8 (bib 374–377) | Mattioda 2020 | yes | 337 "only bands falling between 1550 and 500 cm −1"; 335 "accurate to within 10% –20%"; 332 "Equation (8)" |
| 19 | Apex positions; complexes at strongest peak (bib 370–372) | Mattioda 2020 | yes | 390–392 "its apex … complexes with no discernible individual bands are integrated in" |
| 20 | 15 cm⁻¹ redshift convention, Mackie 2018 (bib 382–383) | Mattioda 2020 | yes | 567–569 "a 15 cm−1 redshift is applied … Mackie et al. (2018)" |
| 21 | Octacene 11.42 / 4.50 / 1.04 kcal/mol; CPS 1.5 factor; error positive (bib 183) | Altun 2021 | yes | 292–294 "11.42, 4.50, and 1.04 kcal/mol … largest acene chain (m = 8)"; 89 Eq. (1); 298–299 "DLPNO error is positive" |
| 22 | "four- to five-fold" (proposal 544) | Altun 2021 | yes | 288–289 "reduces the DLPNO error 4−5 times compared with the default TightPNO" |
| 23 | MAD 5.45 cm⁻¹ / 0.59 %, benzene only, Table S1 (proposal 705–707; bib 184) | Esposito 2024 | yes | 260–265 "Table S1 compares the harmonic frequencies of benzene … 5.45 cm−1, or only 0.59%" |
| 24 | B3LYP/N07D, 200 × 974 grid; D₂h split; <300 cm⁻¹ removed; 20 cm⁻¹ Lorentzian; MAD 5–10 vs experiment (proposal 311, 184; bib 184) | Esposito 2024 | yes | 169–170; 176–177 "performed in the D 2h point group, which splits"; 243; 246–247; 154 "between 5 and 10 cm −1" |
| 25 | 435 frequencies, MAE 0.23 → 0.08 with 3.0 % off-diagonals; 17 complexes (proposal 148; bib 182) | CMA 2026 | yes | 26–29; 20 "performed on 17 prototypical loosely bound" |
| 26 | Symmetry zeroing between irreps; benzene outlier 1155/1331 ∓4; 495i b₂g with aug-cc-pVTZ; basis > correlation (bib 182) | CMA 2026 | yes | 170–176; 666–668 "ω35(a″) 1331.1 −3.7 −4.0 … ω37(a″) 1155.0 4.2 4.6"; 195–196; 624 |
| 27 | κ_E 0.01 / 0.005; <10 added modes; ≤20 active; ≥445 Hessians; DDR gap 100, ǀCǀ ≥ 0.3; Fermi 200 / 1 cm⁻¹ / 0.1 (bib 185) | Fusè 2024 | yes | 1397–1399; 1365; 1515; 1059 "at least 445 times"; 1020–1032 |
| 28 | Joblin 1995 Table 1 (all 20 rows) and Table 2 (7 rows) as transcribed (bib 279–294) | Joblin 1995 | yes, every entry | `joblin1995-04.png`, p. 838, Tables 1–2 |
| 29 | 200 Torr N₂, type-K thermocouple ±0.5 K, one point per 50 K, Bomem DA8, Kirchhoff at 420 K (bib 274–275) | Joblin 1995 | yes | `joblin1995-02.png` §2.1–2.2; `-03.png` Fig. 1–2 |
| 30 | Model Eqs. 3–7; ν_m = 303 (coronene) / 221 (pyrene); low-frequency modes ≪ 700 cm⁻¹; widths ∝ √T; CH anharmonicity ≈ 130 cm⁻¹ (bib 298–305) | Joblin 1995 | yes | `joblin1995-08.png`, p. 842, §4.1–4.2 |
| 31 | Joblin 1994 Table 1 (pyrene), Table 2 (coronene), Tables 4–5 (cross sections); 1 cm⁻¹ (5 for ovalene), 200 Torr, ≈ 50 Torr PAH, purities 99/97/96 %, Ne 4.2 K, contaminant set, "less than 1 %" (bib 245–268) | Joblin 1994 | yes, every entry compared; "±20 %" partly (finding 30) | `joblin1994-04.png` §3.1; `-06.png` Table 1; `-08.png` Table 2, §3.2.2; `-09.png` Tables 4–5 |

Also confirmed from the extracted PDFs: Mulas B97-1, TZ2P pyrene, 6-31G* coronene (item 6);
Madriaga 6.09 µE_h and "large discontinuities and associated errors persist" (item 30); Williams
41,645 molecules, ωB97X/6-31G* (item 47); Zhang Baker set 3–29 atoms (item 33); Mai up to 216 carbon
atoms (item 5); Lam 37 molecules, RMSD 21/23 (finding 13).

## What I could not check, and why

- Wang et al. 2025 (O1NumHess): "~100–124 gradients", "~2×", "conjugated polyene MAD 6–12 cm⁻¹" — no
  PDF or text on disk (the arXiv version exists per item 23 but was not fetched).
- Sanders et al. 2015: "30 % of columns on anthracene, < 3 cm⁻¹, log growth to 15 rings" — read via
  PMC on 2026-09-03; no copy on disk.
- Bégué 2005 "< 0.8 %"; Ruth 2022; Reiher 2003; Pinski & Neese; Lahm 2022 — closed, not held.
- Ricca et al. 2026 "currently unquantified"; Bauschlicher 2018 scale factors — IOP full text read
  2026-09-02, no copy on disk.
- Pirali 2009 (0.005 cm⁻¹, snippet), Sharpe 2004, Brumfield 2012 (T_rot ≈ 25 K, ν68), Maltseva 2016,
  item 50 (SRD 35, 8 cm⁻¹), item 60 (Chakraborty arXiv: −0.025 / −0.014 cm⁻¹ K⁻¹, sub-linear
  low-T behaviour) — not held.
- Kitzmiller 2024 "~17 atoms" and the exact meaning of the 28.2 / 23.1 table maxima — the extracted
  text lacks column headers; the abstract confirms pyridine's four outliers but not the 28 as a
  frequency error.
- Altun 2021 "grows linearly with ring count" — the paper says "grows in absolute value with the
  increasing system size"; the linearity is read from a figure I did not view.
- Fusè 2024 ᾱ_i(j) = |f_iij/(4ω_j)| — formula not recoverable by text search.
- Journal, volume and page of the Käser (JCTC 17, 3687) and Lam (JCTC 16, 1681) PDFs — arXiv
  manuscripts on disk carry no journal metadata.
- Mattioda "Appendix A" as the location of 15 ± 3 K — the extracted text places the "(±3K)" note at
  line 852 in an appendix table caption; consistent, not pinpointed.
- Whether GitHub still serves the pre-rewrite PDF objects (Inventory step 2, "still to do") — no web.

## Verdict

The transcription work of 2026-09-06 is careful and, where I could hold it against the page, exact:
every Joblin table entry, every Chu, Schneider, Mattioda, Lemmens, Altun, Esposito, CMA-2026 and
Fusè number I checked is the paper's number, and the sealed-value rule holds in every Markdown file.
The problems are upstream of the transcription and downstream of it. Upstream, one paper (Esposito
2024) has been carrying a role — the CC-harmonic/DFT-anharmonic precedent "on naphthalene" — that its
text does not support, and that role is written into the proposal's central argument, the Goal, the
Distilled plan and the bibliography; the same paper's benzene MAD is still quoted "at R1" in the
binding Ladder. Downstream, the readings were not propagated: the proposal's reference list tells the
supervisor the temperature-term source was "not yet opened", the bibliography's own status cells and
debt lists still owe readings that were done, the Goal's glossary (which wins on drift) still defines
the retired recalled constants, and a scout's miscount ("five" coronene bands) survived into four
files while the bib's own table shows six. Two honesty gaps are of a different kind: an unverifiable
"Bowman 2024" in the proposal, and "sealed" energies that are plaintext files in a public repository.
None of this requires new reading — every fix above is a wording change against text already on
disk — but findings 1–4 should be made before the proposal goes to the supervisor, and 7–9 and 14
before the bibliography is next cited as the record of what was read.
