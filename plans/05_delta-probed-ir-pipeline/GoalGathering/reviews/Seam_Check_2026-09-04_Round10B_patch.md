# Seam check — the Round-10 Pass B patch (2026-09-04)

Cold mechanical read against `Seam_Check_Brief_2026-09-04_Round10B_patch.md`. No web; no
chemistry judged. Files read: the plan README (Round-10 Pass B record), Goal, Ladder, Distilled,
Budget, Why_05, Frozen_Lines, bibliography, probes README, Mapping, Proposal, Side project,
plans/README, root README; the research note grepped and its §9 tail read. No `\1` / `\2` or
other regex residue found anywhere in the frozen documents (the only `\1` is the README's
historical mention of the Round-10 Pass A repair).

Verdict: 19 seams

## Seams (numbered; file, section, quote both sides, one-line fix)

1. **Distilled §1 still scores R1 per family with its C–C families inconclusive.**
   Distilled §1 Claim: "on the gas-phase rungs — R0 unconditionally, R1 per family under the
   Ladder §2 rule, its C–C families expected inconclusive by construction on the hot-vapour NIST
   sources unless a hot-band correction is pinned".
   Goal, prime directive: "expected unconditional on R0 and R1 (room-temperature cell spectra
   with stated resolution exist for both …)"; Ladder §2 decidability paragraph: "R1 … is
   expected unconditional too".
   Fix: rewrite the clause as "R0 and R1 expected unconditional on their room-temperature
   sources (Ladder §2), the hot WebBook naphthalene entries as labelled hot columns".

2. **Bibliography "Method debts" still makes items 52–53 the only route to decidable C–C
   families at R1.**
   Relevant_Scientific_Papers, Method debts: "the first paid debt, because a pinned per-family
   correction is the only route to decidable C–C families on the existing gas data at R1 and R2".
   Ladder §2 decidability paragraph: "on it u_band(R1) ≈ √(0.1² + centroid² + u_296²) is expected
   below τ for every family … items 52–53 remain the first paid debt because they pin the hot
   columns and u_296".
   Fix: change "at R1 and R2" to "at R2, and the only pin for the R1 hot columns and u_296".

3. **probes README 2a carries the flat "+ 1 cm⁻¹" beside the per-molecule u_296 in one sentence.**
   probes README 2a: "the temperature term (pinned hot-band correction with ±30 % and the
   temperature uncertainty, or the Ladder §2 floor χ_max·(T_source − 296 K) + 1 cm⁻¹; …
   u_296 per molecule per Ladder §2)".
   Ladder §2: "u_T ≥ χ_max·(T_source − 296 K) + u_296, for a room-temperature source u_T ≥ u_296,
   where u_296 is the 0 → 296 K shift term per molecule — 1 cm⁻¹ at benzene, 3 cm⁻¹ at
   naphthalene, 5 cm⁻¹ at the R2 species".
   Fix: replace "+ 1 cm⁻¹" with "+ u_296" and drop the trailing "u_296 per molecule per Ladder §2"
   or keep it as the only mention.

4. **Budget §4.1 says per-response noise and per-energy noise in the same paragraph.**
   Budget §4.1, first half: "then the same recoveries with Gaussian noise at a grid of σ values
   added to every response, K and ρ printed per σ".
   Budget §4.1, second half: "Noise is injected per energy (independent ε on every displaced
   energy; one shared ε₀ per molecule for the reference, drawn once; per component in mode G),
   the column indexed by σ_E".
   Fix: change "added to every response" to "injected per energy (below), R_s formed from the
   noisy energies" and "per σ" to "per σ_E".

5. **Budget §4.2 M1 still prints the two-arm "fresh" difference.**
   Budget §4.2: "prints the continuity diagnostics … and E(displaced, frozen) − E(displaced,
   fresh) per point, without a verdict".
   Ladder §3 frozen-space bullet: "Probe M1 … prints … E(A) − E(B) and E(A) − E(C); for arm C
   also the localiser's functional value"; probes README 2: "E(A) − E(B), E(A) − E(C) per point
   (arms per Ladder §3)".
   Fix: replace with "E(A) − E(B) and E(A) − E(C) per point (arms per Ladder §3)".

6. **Budget §4.5 smoothness probe still runs "with and without frozen spaces".**
   Budget §4.5: "nine points each at q ∈ [−1, 1], TightPNO, with and without frozen spaces".
   Ladder §3 Q6 bullet: "per freezing arm — arms A and B of the §3 object"; probes README 5:
   "arms A and B of the Ladder §3 object (never arm C)".
   Fix: replace "with and without frozen spaces" with "arms A and B of the Ladder §3 object
   (never arm C)".

7. **Side project keeps "the fresh arm" and E(displaced, fresh) in four places.**
   Side project §1.2: "M1's continuity diagnostics (singular values of the overlaps, the fresh
   arm's localiser functional)"; §2: "print the continuity diagnostics and E(displaced, frozen)
   − E(displaced, fresh) per point"; §3 M1 row: "the fresh arm's localiser functional and
   overlap with the transported set) and E(displaced, frozen) − E(displaced, fresh) in µE_h";
   §7 risk 3: "a residual localiser artefact in the fresh arm".
   Side project §1.3 (same file): "arm A needs a small, commit-pinned override"; Ladder §3:
   "E(A) − E(B) … E(A) − E(C); for arm C also the localiser's functional value".
   Fix: "the fresh arm" → "arm C"; "E(displaced, frozen) − E(displaced, fresh)" → "E(A) − E(B)
   and E(A) − E(C)" in §2 and the M1 row.

8. **c₀ is promised in the cost record but the record form and probe 6 do not carry it.**
   Ladder §3 K bullet: "c₀ = R_s(q_s) − ½Δ₂,ii q_s² is over-determined across those modes; its
   mean is subtracted from every response before the recovery and printed in the cost record
   beside σ".
   Ladder §1 record form: "σ = …, RMS_resp = …, ρ_noise = …, c = …, ρ* = …, ρ(K) = …" (no c₀);
   §1 adds "Nothing else about cost may be written". probes README 6: "the cost record with
   σ(R_s), RMS_resp, ρ_noise, c, ρ(K)" (no c₀); its bonus-probe sentence still reads "two extra
   energies per mode; a reported number" without the mandatory / c₀ role.
   Fix: add "c₀ = …" after "σ = …" in the §1 form and in probe 6's record list, and append
   "(mandatory on the scored modes: the same energies identify c₀, Ladder §3)" to probe 6's
   bonus sentence.

9. **The two mandatory q₂ energies per scored mode are uncounted against 2M and K_off.**
   Ladder §3 K bullet: "on every scored family's mode the single-mode block carries R_s at two
   amplitudes, q_s and q₂ (the two extra energies of the diagonal-cubic bonus, now mandatory on
   the scored modes)".
   Ladder §3 guard (ii): "the Q0 deck's first block is the 2M single-mode patterns (±q_s along
   each DFT mode …) … so K_off = K − 2M"; Ladder §1 form: "of which 2M = … in the single-mode ±
   block"; Goal glossary: "K = 2M + K_off"; Distilled §3 Patterns: "whose first block in mode E
   is the 2M single-mode ±q_s energies".
   Fix: one sentence in Ladder §3 saying whether the q₂ pairs count in K (then the block is
   2M + 2·M_scored and the §1 form and K_off definition change) or sit outside K as
   bonus-probe energies, and echo it in the Goal glossary K entry.

10. **Goal step 3 and Distilled route (a) still name the scored harmonic part as Δ₂ alone.**
    Goal, Method skeleton 3: "Spectra via the resonance-explicit routes … on DFT-plus-Δ₂";
    Distilled §3 Anharmonic machinery: "GVPT2 on DFT anharmonic constants with the Δ₂-corrected
    harmonic part".
    Ladder §3: "Rule: the scored harmonic part is Δ₂ + Σ_j φ_iij^DFT δq_j"; Goal step 4 and
    Distilled §3 Responses carry the term.
    Fix: append "plus the first-order geometry term of Ladder §3" to both phrases.

11. **The null arm is "Δ₂ = 0" in Distilled P4(a) and "Δ = 0" everywhere else.**
    Distilled §7 P4: "(a) Δ₂ = 0 (DFT harmonic + DFT anharmonic, no CC correction) … the Δ₂=0
    arm's family mean |error|".
    Ladder §3: "the Δ = 0 null arm … unaffected"; Goal, known risks: "P4's Δ=0 null row";
    Proposal §7: "The Δ=0 arm — DFT harmonic plus DFT anharmonic, no coupled-cluster correction".
    Fix: relabel P4(a) "Δ = 0 (no Δ₂ and no Δ₁ geometry term)" so the label covers the
    now-load-bearing Δ₁.

12. **Plan README "Not yet done" lists the first paid literature debt twice, the older one stale.**
    README, Not yet done, bullet 2: "The first paid literature debts: items 52–53 (hot-band
    slopes), 56–57 and 59 (the R0 and R1 source conditions), 60 — read before M03 prints u_band."
    README, Not yet done, bullet 3: "The first paid literature debt: items 52–53 (PAH hot-band
    shift rates) read before M03 prints u_band."
    Fix: delete bullet 3.

13. **Distilled's header stops at Round-10 Pass A while its status line has both passes.**
    Distilled, header paragraph: "Revised 2026-09-04 after Round-8 (A, B), Round-9 (A, B) and
    Round-10 Pass A."
    Distilled, Status: "revised the same day after Round-8, Round-9 and Round-10 (both passes
    each)".
    Fix: header → "Round-10 (A, B)".

14. **Budget's status line lists no Round-10 revision although §4.1/§3 were patched and §5
    requires every revision listed.**
    Budget, Status: "every revision is listed here — Round-8 Pass A/B … Round-9 Pass A … and
    Round-9 Pass B (2026-09-04: symmetrised dry-run responses; M1 by projection; …)" (ends there);
    §5: "the status line lists every revision".
    README Round-10 Pass B record: "(1) the dry run injects noise per energy …; (8) a units
    paragraph in Budget §3"; Budget §3 "Units." and §4.1 "Noise is injected per energy" exist.
    Fix: append "Round-10 Pass A (2026-09-04: K in energies; 61 / 72 / 1,801) and Round-10 Pass B
    (2026-09-04: per-energy noise injection and c₀ in §4.1; §3 units paragraph)".

15. **Mapping's status line stops at Round-10 Pass A although M03 and M08 carry the PNNL patch.**
    Mapping, Status: "revised 2026-09-04 after the user's decisions, Round-8 (A, B), Round-9
    (A, B) and Round-10 Pass A".
    Mapping M03: "R1 is expected decidable throughout on the PNNL/NWIR room-temperature record";
    M08: "R0–R1 expected unconditional under the pilot note (room-temperature sources named)"
    (both Round-10 Pass B closure 4).
    Fix: "Round-10 (A, B)".

16. **Proposal header counts two cold reads and six passes; its §9 describes four rounds.**
    Proposal header: "revised 4 September 2026 after the student's decisions and a second
    cold-read review … Six external review passes of this plan".
    Proposal §9: "The third round (4 September, two passes) … A fourth round (4 September)
    re-read those patches: all twelve closures held, and its domain pass added four more"
    (Rounds 7–10, two passes each = eight).
    Fix: header → "after the student's decisions and four review rounds … Eight external review
    passes".

17. **Side project's status line predates the Round-9/10 facts its text cites.**
    Side project, Status: "revised the same day after Round-8 Pass A (issues 3–7, 16) and
    Round-8 Pass B (findings 5, 9, 15, 17, 18)".
    Side project §1.2: "no localiser and no assignment at a displaced geometry — Round-9 Pass B
    finding 2"; §1.3: "the released LNO class takes the localized occupied set as an input but
    rebuilds the LNO spaces on every call (item 48), so arm A needs a small, commit-pinned
    override" (Round-10 Pass B closure 6).
    Fix: extend the status line with "Round-9 Pass B (finding 2) and Round-10 Pass B (arms A/B/C,
    item 48)".

18. **Why_05's row-provenance sentence has no home for row 33.**
    Why_05, "What plan 05 changes": "Rows 1–17 date from 2026-09-03; rows 18–27 from the
    2026-09-04 decisions and Round-8 Pass A; rows 28–32 from Round-8 Pass B."
    Why_05 status: "Round-10 Pass B (rows 28–29 amended; row 33 added)"; table row 33 exists;
    plan README reading order: "in one table (33 rows)".
    Fix: append "; row 33 from Round-10 Pass B".

19. **plans/README layout block names three review rounds; its own text names four.**
    plans/README, Layout: "README.md          orientation and reading order; Round-7, Round-8 and
    Round-9 review record".
    plans/README, same file: "Plan 05's review record is in its own README: Rounds 7, 8, 9 and
    10 (both passes each) run and addressed."
    Fix: "Round-7 to Round-10 review record".

## Checked and consistent (the objects 1–10, one line each)

1. Per-energy noise injection — identical in Budget §4.1 (second half), Distilled §3 "Dry run",
   probes README 1, Ladder §4 items 8–9 and §3 (c, K_cap "never from the noiseless one"), Proposal
   §7; only the Budget §4.1 first half survives (seam 4).
2. c₀ — the identification (second amplitude on the scored modes, subtracted, never fitted) reads
   the same in Ladder §3, Distilled §3 "Responses" and "Diagonal-cubic bonus probe", Goal glossary
   and step 2 context, probes README 1, Budget §4.1; the record form and probe 6 omit it (seam 8)
   and the q₂ energies are uncounted (seam 9).
3. Δ₁ load-bearing — Ladder §3 rule, Ladder §4 item 7 (totally symmetric modes added), Distilled
   §3 "Responses", Goal glossary (Δ₁) and step 4, Why_05 row 33, research note §9, Distilled §9
   step 3 (Q7 at the DFT geometry, unaffected) agree; "no atom is moved" in all; two phrases still
   say Δ₂ alone (seam 10); the null-arm label differs (seam 11).
4. Arms A / B / C — Ladder §3 (object and Q6 bullet "arms A and B"), probes README 2 and 5, Goal
   glossary, Side project §1.3, bibliography item 48 (API fact, "arm B is free, arm A needs a
   small override"), Method debts (arm-A override pinned) agree; survivors in Budget §4.2 / §4.5
   and Side project §1.2 / §2 / M1 row / §7.3 (seams 5–7).
5. R1 expected unconditional on PNNL/NWIR (items 57, 59), hot WebBook entries as labelled hot
   columns, Pirali 2009 also room-temperature, Maltseva 2016 for the R2 C–H family — Goal prime
   directive, Ladder §2 (R1 row and decidability paragraph), Frozen_Lines criterion and §5 table,
   Mapping M03 and M08, Proposal §5.2 / §11 / §13.3, probes README 2a, Why_05 row 28, root README,
   plans/README, research note §9 (Round-10 bullet supersedes the dated Round-9 one), bibliography
   items 53, 55, 57–59 agree; survivors in Distilled §1 and the Method debts (seams 1–2). The plan
   README's Round-9 paragraph ("only R0 … R1 is per family") is a dated review record, not a
   survivor.
6. u_296 per molecule (1 / 3 / 5 cm⁻¹, recalled) — Ladder §2 and Goal glossary (u_T, u_296)
   agree; probes README 2a carries both the new term and the old "+ 1 cm⁻¹" (seam 3).
7. ρ_ref = 0.3 (Ladder §3 Q8c, informational); the 2× flag's false-positive rate (Ladder §3,
   ≈ 0.3 %, P(χ²₄ > 16)); mode-G size sentence B3-conditional (Ladder §1); `max_memory` =
   28,000 MB and peak RSS (probes README 1b); DFT grid and thresholds as Q0 deck numbers (Distilled
   Q0; Ladder §3 Q6 "both arms' numerical noise"); the DFT-arm floor (Ladder §3 Q6, probes README
   1, Budget §4.1, Distilled §3 dry run) — each present where the README record places it, no
   contradiction found.
8. Fragment (b) scored per family on the shift-carrying pairs (Ladder §3, probes README 13,
   Budget §4.12 "one comparison at one shell for interior pairs"); (c)'s R4 instance may run under
   a pending licence without resolving it (Ladder §3, Distilled §8 pending sentence, probes README
   14); Goal item 1 (b)/(c) consistent in substance.
9. Bibliography items 57–60 present with one grade each (57: Crossref by the author, full text by
   the reviewer, author's read owed; 58: Crossref, abstract by the reviewer; 59: Crossref, not
   read; 60: HTML full text by the reviewer, author's read owed) and cited at that grade in Ladder
   §2, Frozen_Lines §5, Goal, README; Method debts list carries 56, 57/59, 60 and the arm-A
   override; README "items 23–60 new" matches the table; change table has 33 rows and the README
   says 33; the provenance sentence lags (seam 18).
10. Status lines — Goal, Ladder, Why_05, plans/README table row, root README table row and banner,
    plan README "Not yet done" (Round 11 bullet) carry Round-10 Pass B; Distilled header (seam
    13), Budget (seam 14), Mapping (seam 15), Proposal header (seam 16), Side project (seam 17),
    plans/README layout line (seam 19) do not; the "Not yet done" list duplicates one bullet
    (seam 12).

Seam check complete
