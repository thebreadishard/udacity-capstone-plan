# Seam check — the Round-10 Pass B patch only (2026-09-04)

Not a review round. A mechanical consistency check of one patch, after which the plan-05 text
is frozen (changes only by dated note).

## Your role

A cold reader with no memory of the reviews. No web. No judgement of the chemistry. One
question only: **do the objects introduced by the Round-10 Pass B patch appear identically
everywhere they appear, and does any older wording survive that contradicts them?**

## The objects (each introduced today, each in several files)

1. **Per-energy noise injection** in the dry run (ε on every displaced energy; one shared ε₀
   per molecule; column indexed by σ_E; per component in mode G) — Budget §4.1, Distilled §3
   "Dry run", probes README 1, Ladder §4 items 8–9.
2. **c₀, the shared reference energy's offset**, identified from the second amplitude on the
   scored modes and subtracted, never fitted; the two extra energies of the diagonal-cubic
   bonus now mandatory on the scored modes — Ladder §3, Distilled §3 "Responses" and
   "Diagonal-cubic bonus probe", Goal glossary and step 2, probes README 6, Ladder §1 record
   form (does it carry c₀?).
3. **Δ₁ as a load-bearing term**: the scored harmonic part is Δ₂ + Σ_j φ_iij^DFT δq_j; no atom
   moved; the DFT cubic set gains the totally symmetric modes — Ladder §3, Ladder §4 item 7,
   Distilled §3, Goal glossary (Δ₁) and step 4, Why_05 row 33, Distilled §9 claim ladder (does
   any claim step still describe the scored spectrum as "DFT plus Δ₂" without the term?), Goal
   "forbidden quotes" and the Δ = 0 null arm.
4. **Arms A / B / C** of the frozen space; Q6's reference arm is B; arm A needs a pinned
   override — Ladder §3 (object and Q6 bullet), probes README 2 and 5, Budget §4.2 and §4.5,
   side project §1.2 / §1.3 / M1 row / M2 row, bibliography item 48. Any survivor of
   "with and without frozen spaces", "E(displaced, fresh)", "the fresh arm"?
5. **R1 expected unconditional on the PNNL/NWIR record** (items 57, 59), the hot WebBook
   entries as labelled hot columns, Pirali 2009 also a room-temperature source, Maltseva 2016
   for the R2 C–H family — Goal prime directive, Ladder §2 (R1 row and decidability paragraph),
   Distilled §1 and §8, Frozen_Lines criterion and §5 table, Mapping M03 and M08, Proposal
   §5.2 / §11 / §13.3, probes README 2a, Why_05 row 28, root README, plans/README. Any
   survivor of "R1 per family", "R1's C–C families expected inconclusive", "only R0
   unconditional", "hot sources only"?
6. **u_296 per molecule** (1 / 3 / 5 cm⁻¹, recalled) in the temperature floor — Ladder §2,
   Goal glossary (u_T), probes README 2a. Any survivor of "+ 1 cm⁻¹"?
7. **ρ_ref = 0.3** informational read; **the 2× flag's false-positive rate**; **mode-G size
   sentence B3-conditional**; **`max_memory` = 28,000 MB** in the feasibility probe; **DFT
   grid and thresholds as Q0 deck numbers**, the **DFT-arm floor** — each in the files the
   README's Round-10 Pass B record names.
8. **Fragment (b) scored per family on the shift-carrying pairs; (c)'s R4 instance may run
   under a pending licence** — Ladder §3, Distilled §8, probes README 13–14, Goal item 1.
9. **Bibliography items 57–60** cited with the same grade everywhere; the Method debts list;
   the README's item count; **change-table row 33** and the README's row count (33).
10. **Status lines** of Goal, Ladder, Distilled, Budget, Mapping, Why_05, proposal header;
    plans/README and root README banners; the plan README's "Not yet done".

Also: any `\1`, `\2` or other regex residue anywhere in the frozen documents; any sentence
that now contradicts itself inside one paragraph because a clause was inserted mid-sentence.

## Read

The plan-05 set in the README's reading order, but you may read selectively: search for the
objects above and read every paragraph that mentions them, plus the status lines. Read the
README's Round-10 Pass B record (17 closure claims) and check each is in the text.

## Output

`Seam_Check_2026-09-04_Round10B_patch.md` in this folder:

```
Verdict: [clean / N seams]
## Seams (numbered; file, section, quote both sides, one-line fix)
## Checked and consistent (the objects 1–10, one line each)
```

No blocking/non-blocking split. No chemistry. End with "Seam check complete".
