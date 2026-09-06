# Brief — cold read with a literature focus, 2026-09-06

**Reader.** A fresh reader with no earlier version of any file and no conversation history: an
academic in computational chemistry / astrochemistry who is also a careful librarian. No web
access. Everything you need is on disk.

**Repository.** `C:\Users\thebr\Documents\CapstonePlan`, plan folder
`plans\05_delta-probed-ir-pipeline\`. The literature copies are in `Papers\` at the repository
root (git-ignored; extracted texts in `Papers\_txt\`, page images of two scans in `Papers\_img\`).

**Question.** Is every mention of the literature in plan 05 correct, consistent across files, and
honest about what was actually read? "Honest" means: a fact attributed to a paper was taken from
that paper's text on disk, not from memory; a paper described as read was read; a number or
condition quoted from a paper is the paper's number; identifiers agree across files; the record
of which PDFs are held matches the folder; and nothing says or implies that PDFs are in the
repository.

**Files to read (in this order).**

1. `GoalGathering/Relevant_Scientific_Papers.md` — the bibliography (item table with per-item
   verify status; "PDFs held locally"; "Novelty search 2026-09-06"; "Readings of 2026-09-06"
   in two sections).
2. `GoalGathering/Project_Proposal_2026-09-06.md` — the supervisor proposal, including its
   reference list at the end.
3. `GoalGathering/Frozen_Ladder_and_Tolerances.md` — the binding plan text; dated notes cite items.
4. `GoalGathering/Overarching_Goal.md`, `GoalGathering/Frozen_Lines_to_Beat.md`,
   `GoalGathering/Compute_Budget_2026-09-03.md`,
   `GoalGathering/Distilled_Project_Plan_and_Quality_Checks.md`.
5. `GoalGathering/Research_Note_2026-09-05_Probe_M1.md`,
   `GoalGathering/Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md`,
   `GoalGathering/Research_Note_2026-09-05_DryRun_Benzene.md`,
   `GoalGathering/Research_Note_2026-09-03_Delta_Probing.md` (§§8–9 win over §§1–7).
6. `GoalGathering/PDF_Request_2026-09-06.md` — the list sent to the supervisor.
7. `probes/README.md`, `README.md` (plan), the repository `README.md`, `plans/README.md`,
   `Papers_Inventory_2026-09-06.md` (repository root).
8. `Uitleg/*.md` — Dutch lay explanation; check only its literature mentions.
9. The folder `Papers\` itself (list it) and, for spot checks, the texts in `Papers\_txt\`.

**Checks to run (report each as done, with what you found).**

- **A. Coverage both ways.** Every author-year or item-number mention outside the bibliography
  resolves to one bibliography item; every proposal reference-list entry is cited in the
  proposal text and exists in the bibliography; every bibliography item that a plan document
  leans on is present. List orphans in both directions.
- **B. Identifier consistency.** For every paper that appears in more than one file, compare
  journal, volume, page/article number, year and DOI across files. Report every disagreement.
- **C. Status honesty.** For every item whose status says "read", "read in full", "opened",
  "snippet", "not read", "not opened", check that the claims made about that paper elsewhere are
  no stronger than the status allows. A number quoted from a paper marked "not read" is a
  finding. A detail that could only come from the full text of a paper marked "snippet" is a
  finding. Author initials, page numbers or section numbers that appear only where they could
  not have been fetched are findings.
- **D. Fact spot checks against the texts on disk.** Take at least fifteen specific facts that
  the plan attributes to papers whose text is in `Papers\_txt\` (for example: measurement
  temperature, resolution, an uncertainty figure, a band position, a slope, a MAD, a threshold
  value, a count) and verify each against the text file. Quote the paper's line. For the two
  Joblin scans, use the page images in `Papers\_img\` if you can read images; otherwise say so.
- **E. Attribution drift.** A fact attributed to paper X in one file and to paper Y in another;
  a number that changed between files (e.g. a MAD, a temperature, a bandwidth, a number of
  bands); a qualifier that was dropped ("benzene only", "linear fit", "at 770 K", "2σ").
- **F. The PDF record.** Compare the "PDFs held locally" table with the actual `Papers\` listing
  (file names, page counts if stated), with `PDF_Request_2026-09-06.md` (what is asked of the
  supervisor must not be something already held, and what is held must not still be asked), and
  with `Papers_Inventory_2026-09-06.md`. Report every mismatch. Confirm that no tracked file
  says PDFs are in the repository (the layout paragraph of the repository README was rewritten
  today; check it).
- **G. Recall risk.** Flag any literature statement anywhere in the plan that is presented as
  fact without a file, item number, DOI or "recalled" label — the repository's rule is "never
  cite from recall" and recalled statements must be labelled.
- **H. Sealed values.** The plan keeps some benzene numbers sealed. Confirm no document prints
  them (search for "sealed" and check the surrounding text).

**Format.** Write the report to
`GoalGathering/Cold_Read_2026-09-06_Literature.md`. Header: reader, scope, files read, checks
run. Then numbered findings, each with: file and line, quoted text, what is wrong, a concrete
fix, and a class — BLOCKING (a false or unverifiable literature claim in a binding document or
the proposal), MAJOR (inconsistency across files or a status weaker than the claim), MINOR
(wording, formatting, redundancy). Finish with a table of the spot checks (fact, file, paper,
verified yes/no, the paper's line), a list of what you could not check and why, and a one-
paragraph verdict. Do not fix anything yourself. Do not use the web. Do not print sealed values.
