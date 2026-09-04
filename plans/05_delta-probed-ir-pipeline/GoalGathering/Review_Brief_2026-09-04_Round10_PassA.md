# Review brief — Round 10, Pass A: cold read after the Round-9 Pass B patches

**Give this to the reviewer first. Do not give Pass B until Pass A's findings are written down.**

---

## Your role

A careful, sceptical reader with no memory of Rounds 7–9. Round-9 Pass B changed three things
that run through the whole set at once — the mode-E response is now a symmetric combination
over ± pattern pairs, the frozen space is transported by projection with no orbital assignment,
and only R0 is scored unconditionally — plus nine smaller closures. The patch touched the Goal,
Ladder, Distilled plan, Budget, probes README, side project, Mapping, Proposal, Frozen_Lines,
bibliography, change table and research note. Your question:

> **Does this document set say what it thinks it says, and is any of it unsupported?**

You are not judging the chemistry. Pass B does that.

## Context you need

- Master's capstone plan, one person, human hours uncapped. The B2 machine is a named laptop
  (8 cores, 31.3 GB usable, no CUDA GPU). **Nothing has been executed; no code exists.** All seven
  user decisions are closed; nothing is open.
- **Plan 05** is current; plans 01–04 are read-only records in the tree. Do not review them.
- Review history is in the plan README's review record (Rounds 7, 8, 9, each with two passes).
  **Round-9 Pass B's patches were never re-read**; that is why you are here.
- **Calibration warning:** drafted by an AI assistant with the student by find-and-replace across
  fourteen files in one sitting. Seams live where a new object (R_s, ± pairs, transported
  orbitals, continuity diagnostics, the temperature floor, "pending (b′)", ρ\*_common, pooled σ,
  36 gradients) was introduced in one file and an older phrasing survives in another.

## What to read (in this workspace; do not fetch GitHub), in order

0. [README.md](../../../README.md), [plans/README.md](../../README.md)
1. [../README.md](../README.md) — review record (Round 9 entries especially); "Not yet done"
2. [Overarching_Goal.md](Overarching_Goal.md) — the glossary first
3. [Why_05_Supersedes_04.md](Why_05_Supersedes_04.md)
4. [Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
5. [Distilled_Project_Plan_and_Quality_Checks.md](Distilled_Project_Plan_and_Quality_Checks.md)
6. [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md)
7. [../probes/README.md](../probes/README.md)
8. [Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md)
9. [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md)
10. [Relevant_Scientific_Papers.md](Relevant_Scientific_Papers.md) (items 1–53, statuses)
11. [Capstone_Mapping.md](Capstone_Mapping.md)
12. [Project_Proposal_2026-09-03.md](Project_Proposal_2026-09-03.md)
13. [Research_Note_2026-09-03_Delta_Probing.md](Research_Note_2026-09-03_Delta_Probing.md)
    (status line: the frozen documents win over the note)
14. [Professor_Review_2026-09-04_Round9_PassB.md](Professor_Review_2026-09-04_Round9_PassB.md)
    — its 12 findings, so you can check each closure is in the text and consistent across files

## The five questions

**1. Contradictions.** Quote both sides. Look especially for:

- **The symmetrised response.** Is "response" one object everywhere (Goal glossary, Goal step 2,
  Distilled §3 "Responses" / "Patterns" / hold-out row, Ladder §3, Budget §4.1 dry run, probes
  README 1 and 6)? Does every sentence that counts K count energies in mode E (a ± pair = 2)?
  Is the 2M single-mode block described consistently (M modes × ±q_s = 2M energies) and does
  K = 2M + K_off still hold with K_off in energies? Is hold-out membership decided per pattern or
  per pair (it must be per pair, or one half of a pair trains while the other tests)? Does the
  R6 whole-molecule floor "≥ 2,580 energies" still follow? Does the Q6 noise line, derived for
  E₊ − 2E₀ + E₋, sit consistently beside σ(R_s) = σ_E/√2 — or do two documents give two σ's for
  the same object? Does any document still describe the mode-E response as "the energy
  difference at the pattern geometry minus at equilibrium"?
- **The frozen space.** Any survivor of "maximal overlap", "assignment", "permutation", "switch"
  outside the historical review-record lines and the research note's erratum? Are M1's printed
  quantities the same list in Ladder §3, Budget §4.2, probes README 2, side project §1.2 / §2 /
  M1 row? Does the side project's kill criterion or risk 3 still speak of switches? Is the
  glossary's "re-projected" consistent with the Ladder's object?
- **R0 unconditional, R1 per family.** Goal prime directive, Ladder §2 (R0/R1 rows, the
  decidability paragraph, the dated notes), Distilled §1/§8, Frozen_Lines criterion, Mapping M03,
  Proposal §5.2 / §11 / §13.3, Why_05 row 28, probes README 2a: do all say R0 unconditional and
  R1 per family, with the same expected verdict for R1's C–C families? Is the temperature floor
  formula identical wherever it appears (χ_max·(T_source − 296 K) + 1 cm⁻¹; 1 cm⁻¹ at room
  temperature)? Are items 52–53 cited with the same grade everywhere (52 not opened; 53 Crossref
  record)? Does anything still say "unconditional on the gas-phase rungs (R0–R1)" or "R0–R1
  unconditional"?
- **The fragment licence.** "ring" vs "shell" wording; "one comparison at one shell" and
  "pending (b′)" present in Goal item 1, Ladder §3, Distilled §8, Budget §4.12–13, probes README
  13–15, Proposal §5.2? Is part (c) classified by Budget §2 everywhere it is costed? Does the
  360-energy figure carry its arithmetic?
- **ρ\*_common.** Ladder §1 (record form and size sentence), Ladder §3 Q8(c), Distilled Q8, Goal
  cost question, probes README 12–13: the same definition (max of the two rungs' ρ\*)?
- **σ = √(SSR/(n − p)), pooled per arm.** Ladder §3, Distilled Q6, probes README 5, Budget §4.5:
  the same estimator; the same pooling; does any sentence still say "per mode" σ decides a
  verdict? Is σ_g^assumed (item 8) consistent with σ_g now being pooled over 3N components?
- **36 gradients.** Side project M2–M5, Budget §4.7/8/11/12, probes README 6/8/12/13, side
  project §4 budget: consistent, and is M4/M5's classification by Budget §2 stated where the
  milestone is defined?
- **The Round-9 review record** in the plan README: does each of the 12 closure claims match the
  text? Any decided-vs-open survivors ("Round 9 Pass B owed", "five review passes")?
- The two debt lists; "Method debts" vs items 52–53; the research note's closing bullets vs the
  frozen documents.

**2. Unsupported claims.** Candidates: the WebBook facts (benzene Quantitative IR series;
naphthalene 245 °C vapour and GC-IRD; "opened by reviewer and author" — is the author's
opening recorded for both?); the `pyscf/grad/ccsd_t.py` listing; item 52's snippet slope; χ_max
= 0.03 (recalled — labelled so everywhere?); the 1 cm⁻¹ room-temperature floor (recalled?); the
coronene geometry claim (two ring-closed interior radii) — is it presented as reasoning or as a
measurement; the "several times the Δ₂ signal per bond" claim for Δ₁·p — does it carry its
provenance (Round-9 Pass B finding 1, recalled bond-length differences)? Any timing used as a
budget.

**3. Number drift.** 72 energies; 36 gradients; 8 re-projected energies for the FD check; 360
fragment energies; 61 / 72 / 1,801; 2,580; 133; 204; ν = 4 / 16; the 90 % range; bibliography
count (53) and the README's "items 23–5x new"; change-table row count (32) and the README.

**4. Loopholes.** Try to defeat:

- **K_cap in energies.** The dry run's K (which K_cap is derived from) must be counted the same
  way as the real run's K (energies, pairs). Does any document say so? If the dry run counted
  patterns and the real run counts energies, K_cap is off by two.
- **The ± pair and the hash.** Patterns are consumed in hashed order "pairs together": is the
  pair defined in the deck before hashing, and can the second half of a pair be dropped after
  the first half's response is known?
- **"Pending (b′)".** Can a pending licence let any R6 work start? Can (b′) itself run without
  B3? If B3 never materialises, what does the plan report for R6 — and is that sentence in
  Distilled §8?
- **ρ\*_common.** Both rungs reached it; but is K_off at ρ\*_common read from the same hashed
  order and hold-out as the record K_off? Could a rung's curve be re-run to reach a lower ρ?
- **The temperature floor.** For a room-temperature source the floor is 1 cm⁻¹; who decides a
  source is "room temperature" when the JCAMP carries no temperature line (the benzene Coblentz
  entry says pressure, not temperature)? Is the default then hot or cold?
- **σ pooled per arm.** If one of four modes fails its own line but the pooled σ passes, what
  happens — is the per-mode value informational or gating? Say which the text implies.
- **The feasibility probe's one gradient.** "Where the code has it": who decides which code, and
  is the gradient's timing allowed to set the "fits" verdict for the 72-gradient object without
  the count factor being frozen?

**5. Unreadable without the author.** With the Goal's glossary as the single definition point:
does the glossary define R_s, R_a, Δ₁, ρ\*_common, S_oo, "continuity diagnostics", "shell",
"pending (b′)", χ_max, T_source, "pooled σ"? Any acronym used before it is defined? Any
pointer to a section number that moved?

## Output format

```
Verdict: [one line — internally sound enough to proceed to Pass B?]

## Blocking findings
1. [Title]
   Where: [file, section]
   What: [what is wrong]
   Why it matters: [consequence if unfixed]
   Status: [open]

## Non-blocking findings
…

## What passed
…
```

Use **Round 10, Pass A, issues 1–N**. **Do not write Pass B in the same file.**
