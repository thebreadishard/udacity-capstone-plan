# Professor Review — Round 10, Pass A (cold read after the Round-9 Pass B patches)

**Date:** 2026-09-04. **Reviewer role:** cold reader with no memory of Rounds 7–9; no web access;
judged only against the text in the workspace. **Brief:**
[Review_Brief_2026-09-04_Round10_PassA.md](Review_Brief_2026-09-04_Round10_PassA.md).
**Read in full, in the brief's order:** root `README.md`, `plans/README.md`, plan-05 `README.md`,
Overarching_Goal (glossary first), Why_05_Supersedes_04, Frozen_Ladder_and_Tolerances,
Distilled_Project_Plan_and_Quality_Checks, Compute_Budget_2026-09-03, `probes/README.md`,
Side_Project_2026-09-04_ModeG_Gradients, Frozen_Lines_to_Beat, Relevant_Scientific_Papers
(items 1–53 and both debt lists), Capstone_Mapping, Project_Proposal_2026-09-03,
Research_Note_2026-09-03_Delta_Probing, Professor_Review_2026-09-04_Round9_PassB. Plans 01–04
not opened; the Round 7–9 briefs and the other reviews not opened. Arithmetic below is mine,
from the numbers in the text (atom and mode counts, the noise-line derivation), not from any
source outside the workspace. Issues are numbered 1–20 continuously across the two lists.

---

**Verdict: not yet — the three Round-9 changes (symmetrised response, projection-only frozen
space, R0-only unconditional) are in the text and mostly consistent, but the patch left the
Ladder and the Distilled plan disagreeing with themselves on three things a Pass B would have
to assume settled: which σ the symmetrised response carries, what unit K and the hold-out are
counted in, and whether the per-mode σ or the pooled σ gates Q6. All seven blocking items are
in-spec sentence fixes; none needs a measurement. Patch them, then proceed to Pass B.**

---

## Blocking findings

### 1. Two σ's for the symmetrised response: σ(R_s) = σ_E/√2 contradicts the √6 noise-line derivation in the same section, and ρ_noise does not say which σ it divides by
**Where:** Ladder §3 "K is a measurement, not a choice"; Ladder §3 "Q6 has thresholds";
Distilled §3 "Responses" and "Hold-out and residual ρ; the noise floor"; Goal glossary
(ρ_noise).
**What.** Ladder §3 writes: "**K counts energies in mode E (a ± pair counts 2) and gradients in
mode G**; ρ, RMS_resp and ρ_noise are defined on R_s, with σ(R_s) = σ_E/√2." Distilled §3
"Responses" repeats "σ(R_s) = σ_E/√2". But R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) has three noisy
inputs: if ΔE(0) carries the same per-point scatter σ_E as the displaced points, Var(R_s) =
¼(σ_E² + σ_E²) + σ_E² = 1.5·σ_E², so σ(R_s) = σ_E·√(3/2) ≈ 1.22·σ_E, not σ_E/√2 ≈ 0.71·σ_E. The
Ladder's own Q6 bullet counts ΔE(0)'s noise: "mode E's three-point second difference
(E₊ − 2E₀ + E₋)/q_s² has σ = σ_E·√6/q_s²" — and (E₊ − 2E₀ + E₋)/q_s² is exactly 2R_s/q_s², so
that sentence implies σ(R_s) = σ_E·√6/2 = σ_E·√1.5. The two statements in one section differ by
a factor √3. σ_E/√2 is right only if ΔE(0) is treated as an exact, shared reference — which may
be the intent (one reference energy, its error a common offset to every response, not per-pattern
scatter) but is nowhere said, and a common offset in every R_s is not fitted by a quadratic form
½pᵀΔ₂p unless the solver carries a constant. Then the stopping rule: Ladder §3 defines
"ρ_noise(rung, mode) = σ(mode, size)/RMS_resp(rung), where σ is the per-point scatter σ_E or
σ_g of the §3 estimator"; Distilled §3 "**ρ_noise** = σ(mode)/RMS_resp(rung), σ the per-point
scatter of the Q6 estimator"; Goal glossary "**ρ_noise** = σ/RMS of the rung's held-out
responses". RMS_resp is the RMS of R_s; the numerator is σ_E, the scatter of a single energy, not
of R_s. Whether ρ_noise uses σ_E, σ_E/√2 or σ_E·√1.5 is a factor of up to √3 in ρ\*, and the
"equivalently, the held-out χ² per point with σ as the per-point sigma first falls to c²" clause
inherits the same ambiguity.
**Why it matters.** ρ\* = c·ρ_noise decides K, the promised cost record, and the "at noise"
floor (c·ρ_noise ≥ 0.5); a √2–√3 error in ρ_noise moves K on every rung and can flip a rung
between "recovered" and "at noise". The dry run's c is read at one convention and the real run
may apply another.
**What would close it (in spec).** One sentence in Ladder §3, mirrored in Distilled §3 and the
glossary: whether ΔE(0) is a single shared reference whose scatter is a common offset (then say
so, and say the solver fits or the responses are re-referenced to it) or a noisy point like the
others (then σ(R_s) = σ_E·√(3/2)); and "ρ_noise = σ(R_s)/RMS_resp with σ(R_s) = …" — the
same σ(R_s) in the χ² clause and in the Q6 line's √6.
**Status:** open.

### 2. K's counting unit is still mixed: "pattern count", "K_off ≥ 1", and a record form "in ± pairs" survive beside "a ± pair counts 2"
**Where:** Distilled §3 "K" row; Ladder §3 "K is a measurement" (guard ii); Ladder §1 cost
record form; Goal glossary; probes README 1.
**What.** Goal glossary: "**K** = the measured count of energies (mode E; a ± pair counts 2) or
gradients (mode G)". Ladder §3: "**K counts energies in mode E (a ± pair counts 2)** … Patterns
are consumed in the hashed order of the Q0 deck, pairs together." Against that: Distilled §3 K
row — "the smallest pattern count n, in hashed order, at which ρ(n) ≤ ρ\* = c·ρ_noise"; Ladder
§3 guard (ii) — "the rule is evaluated only for n > 2M, so K_off = K − 2M ≥ 1", repeated in
Distilled §3 "K_off = K − 2M ≥ 1 in mode E". If pairs are consumed together and a pair counts 2,
K_off is even and its minimum is 2, not 1; "≥ 1" is only true if n counts patterns or half-pairs.
The Ladder §1 record form reads "K = n energies|gradients (mode E: of which 2M = … in the
single-mode ± block, K_off = … in ± pairs of off-diagonal patterns …)" — "K_off = … in ± pairs"
can be read as a count of pairs. Nor does either document say at what cadence ρ(n) is evaluated:
per energy (impossible — R_s needs both halves of the pair) or per pair (then n steps by 2 and
"smallest n" should say so). For the cap: Budget §4.1 says the dry run's "Responses are the
symmetric combinations R_s over ± pairs exactly as in the real run", but probes README 1 (the
script that prints the dry-run K) says only "the dry-run K and K_off per mode at a declared ρ"
with no ± pair and no unit; K_cap (item 9) is "derived from the noise-injected dry-run K", so if
that script counts patterns and the R0 script (README 6, "the R0 responses (symmetric
combinations over ± pairs) in hashed order, K(R0) and K_off at ρ\*") counts energies, K_cap is
off by two.
**Why it matters.** K is the thesis's third sentence type; a factor-of-two ambiguity in its unit
and in K_cap is not a wording seam, it is the deliverable.
**What would close it.** "K_off = K − 2M ≥ 2 (one ± pair)"; "ρ(n) is evaluated after each
complete pair, n in energies"; the record form "K_off = … energies (… ± pairs)"; probes README 1
gains "K in energies, a ± pair counting 2, exactly as README 6".
**Status:** open.

### 3. Hold-out membership is decided per "pattern index" while the glossary's pattern is one geometry — nothing says the two halves of a ± pair are held out together
**Where:** Ladder §3 "Hold-out membership is decided before any response exists"; Distilled §3
"Hold-out and residual ρ"; Goal glossary "Pattern".
**What.** Ladder §3: "by a seeded rule in the Q0 deck (deck seed + pattern index), fraction f_h
(item 10)." Distilled §3: "a fraction f_h of patterns, chosen by the seeded deck rule before any
response exists, never enters the recovery." Goal glossary: "**Pattern** = one simultaneous
multi-atom displacement geometry … every pattern enters the deck as ±p." Under the glossary's
definition +p and −p are two geometries; if the deck indexes geometries, the seeded rule can
place +p in the hold-out and −p in the training set, and then neither R_s(p) (which needs both)
is computable on either side — or, worse, the implementation silently uses the pair for both.
The brief's loophole ("can the second half of a pair be dropped after the first half's response
is known?") is closed by Distilled §4 ("Adding, removing or re-weighting patterns after any
residual is known" is a deviation) only if the pair is the unit that rule protects.
**What would close it.** One clause: "the hold-out unit is the pair ±p (one deck index per
pair); a pair is never split between hold-out and training"; the glossary's "Pattern" says
whether p or the pair ±p carries the deck index.
**Status:** open.

### 4. Does the per-mode σ or the pooled σ gate Q6? Ladder §3 says both, in adjacent bullets; Budget §4.5 tests per mode
**Where:** Ladder §3 "Q6 has thresholds"; Ladder §3 "Pattern amplitudes come from the Q6 step
grid"; Budget §4.5; Distilled §8.
**What.** Ladder §3 Q6: "**One σ per freezing arm, pooled over the four modes** (ν = 16 in
mode E), the per-mode values printed beside it … the noise lines are evaluated on the pooled σ".
Two bullets earlier, Ladder §3 amplitudes: "Stated plainly: with one σ per mode and a line that
rises with q_s, q_s = 1.0 passes whenever any grid step does … a mode whose σ fails at q_s = 1.0
fails Q6 in that mode (Distilled §8 sentence) and is not rescued by a smaller step." Budget §4.5:
"the script prints **σ_E as the RMS residual about a degree-4 polynomial fit** per mode and arm
against the Q6 lines at each grid step" — a per-mode test. Distilled §8's sentence "Mode [E|G]
fails Q6 at Rn at q_s = 1.0 (σ = … vs the line …); no smaller step is tried; no Δ₂ is recovered
in that mode at Rn" uses "mode" for E/G, so it cannot be the per-vibrational-mode sentence the
amplitude bullet points to. As written the text implies both: the pooled σ is the gate (Q6
bullet) and a single vibrational mode can fail Q6 on its own σ (amplitude bullet, Budget).
**Why it matters.** With ν = 4 per mode the Ladder itself says a per-mode σ "has a 90 % range of
[0.42, 1.54]·σ"; whether such a number can fail a rung is the difference between a gate and a
coin toss, and the pilot note freezes q_s "per mode" (item 13) from this test.
**What would close it.** State once: the pooled σ per arm gates the noise line at the size
class; per-mode σ's are printed and flagged (informational), and the pattern amplitude per mode
is chosen from the pooled verdict — or, if a per-mode gate is wanted, adopt the 17-point grid
the Round-9 reviewer offered and say so. Then align the amplitude bullet, Budget §4.5 and the
Distilled §8 sentence (which needs a per-family/per-mode variant if per-mode gating stays).
**Status:** open.

### 5. Why_05 change-table row 31 is destroyed: a literal `\1` back-reference replaced both columns
**Where:** Why_05_Supersedes_04, "What plan 05 changes — the complete list", the row after 30.
**What.** The row reads, in full: `\1; Round 9: both halves transported by projection, no
localiser or assignment at displaced geometries | Ladder §3, Side project |`. The row number,
the plan-04 column and the plan-05 column are gone (the find-and-replace's capture group was
never expanded); only the appended Round-9 clause and the "Where" column survive. Plan-05
README reading-order item 2 says "every change relative to plan 04, in one table (32 rows)" and
the README Round-9 Pass A record says "(11) change table rows 7/21/22 corrected, rows ordered,
32 rows" — the table now has 31 whole rows and one fragment. The Round-9 Pass B review (Part 1,
"Also-worth items") read this row as "rows 28–32 match the documents", so the damage is the
Round-9 Pass B patch itself.
**What would close it.** Restore row 31 (plan 04: unfrozen domains / no frozen-space object;
plan 05: the frozen-space object written once — stored occupied and virtual vectors, transported
by projection and Löwdin-orthonormalised, probe M1 with continuity diagnostics; Round 9: both
halves by projection, no localiser or assignment).
**Status:** open.

### 6. "R0–R1 … unconditional" survives in the Mapping's Module 08 and in the root README's "current objective"
**Where:** Capstone_Mapping §3 "Module 08 — the pipeline, assembled and scored"; root
`README.md` "The current objective (plan 04 wording; plan 05 keeps it and changes the anchor
method)" and the "Plan 04 product" paragraph above it.
**What.** Goal prime directive: "unconditional on R0 (room-temperature gas cell spectra exist);
on R1–R3 per family". Ladder §2: "**R0 is unconditional** … **R1 is per family under the same
rule as R2**". Mapping M08: "Runs: R0–R1 accuracy comparisons under the pilot note (gas-phase,
unconditional); R2–R3 per family under the decidability rule and the per-mode Q6 noise gate".
Root README, under a heading that says plan 05 keeps this wording: "judged per band against
laboratory data **where that data can decide it** — gas-phase rungs unconditionally, larger rungs
via the measured matrix–gas gate, never on reach rungs"; and above it, "'beat' claims are
unconditional only on the gas-phase rungs (benzene, naphthalene)" (that paragraph is labelled
plan-04 wording "kept as written", which covers it only if a reader accepts the banner's "where
they say 'current', read plan 05" as also meaning "where they say naphthalene is unconditional,
read per family"). Everywhere else — Distilled §1, Frozen_Lines criterion, Why_05 row 28,
Proposal §5.2, probes README 2a, Mapping M03 — the R1-per-family form is in.
**Why it matters.** M08 is the module that ships the scored comparison; its paragraph is what a
grader reads. The root README is the first thing anyone reads.
**What would close it.** M08: "R0 unconditional; R1–R3 per family under the decidability rule".
Root README: one clause in the "current objective" paragraph ("R0 unconditionally, R1–R3 per
family by the measured band-centre uncertainty"), and a parenthesis on the plan-04 paragraph.
**Status:** open.

### 7. The anthracene probe's 133 energies is the diagonal-only count, but the probe is described as "a full numerical Δ₂ … Q8(a) per pair"
**Where:** Budget §4.9; probes README 9; Research note §8 (source of the number); Proposal §8.
**What.** Budget §4.9: "**Anthracene locality probe** (dated bonus, B2 or B3 by the rule;
≈ 2×66+1 = 133 frozen-domain local-CC energies): a full numerical Δ₂ printed as Q8(a) per pair
and as the mode-basis matrix per family — the cheapest direct test of whether the C–C block is
long-ranged". probes README 9: "≈ 133 frozen-space local-CC energies): full numerical Δ₂ minus
B3LYP; Q8(a) per pair and the mode-basis matrix per family". 2×66+1 is the ± single-mode block
plus the reference for anthracene's 66 modes — the CMA-0 block, which yields the 66 diagonal
elements Δ₂,ii in the DFT mode basis and nothing off-diagonal. A "full numerical Δ₂" by central
differences in 66 modes is 1 + 2·66 + 4·C(66,2) = 8,713 energies; Q8(a)'s per-pair
family-projected couplings are, by the Ladder's own form, "four energies per (pair, family)" from
mixed differences — a different set of geometries from the single-mode block. So either the count
is right and the probe cannot print Q8(a) per pair or the mode-basis off-diagonal blocks, or the
purpose is right and the count is wrong by a large factor (or is the direct-coupling probe's
4 × pairs × families). The Proposal's "about 130 energies" inherits it. The sentence is "arithmetic
that matters", and its purpose ("the cheapest direct test of whether the C–C block is
long-ranged") is exactly the off-diagonal information 133 energies do not contain. Also "frozen-
domain" (Budget §4.9) is the one survivor of the pre-glossary term; everywhere else it is "frozen
spaces".
**What would close it.** Decide what the probe is — (a) the anthracene diagonal Δ₂,ii (133
energies; then it is not a Q8(a) read and says so), or (b) a direct-coupling probe on anthracene
with the deck's pair list (4 × pairs × families energies, count printed) — and write the same
sentence in Budget §4.9, probes README 9 and Proposal §8.
**Status:** open.

---

## Non-blocking findings

### 8. Status lines and counts that stopped at Round 8
**Where:** Ladder status line; Distilled status line; Mapping status line; Proposal §9; plan-05
README reading-order item 9.
**What.** Ladder: "revised the same day after Round-8 Pass A and Round-8 Pass B" — no Round 9,
although §2 and §3 carry Round-9 text ("Round-9 Pass B finding 1", "finding 2"). Distilled:
"revised the same day after Round-8 Pass A and Pass B" — same. Mapping: "revised 2026-09-04
after the user's decisions and Round-8 Pass A" — it carries Round-8 Pass B and Round-9 content
(M06 display criteria, u_band, items 52–53). Proposal §9 narrates Round 7 and Round 8 and ends
"Whether those closures hold is for a further pass to say" — Round 9 (both passes) is not
mentioned in §9 at all, though §5.2 cites "The third review (4 September)" and the header counts
"Six external review passes". README item 9: "bibliography with per-item verify status (items
23–51 new)" — the bibliography has 53 items, 52–53 added by Round 9 and cited from the README's
own Round-9 record. Mapping §5's items are numbered 1, 4, 2, 3.
**Status:** open.

### 9. The 360-energy figure does not carry its arithmetic, and "(c) … at two shells B3" pre-empts the classification rule it cites
**Where:** Ladder §3 fragment licence (c); Budget §4.13; probes README 15.
**What.** Ladder §3: "its energy count is printed (three pairs per class × the scored families ×
four energies × two radii — of order 360 fragment energies at R6 …)". 3 × F × 4 × 2 = 24F; 360
needs F = 15, or — what the Round-9 reviewer actually computed — 9 pairs (three per class × three
classes) × ≈ 5 families × 4 × 2. The class count (3) is missing from the product and the family
count is nowhere stated (the reporting-unit bullet lists CH-stretch, three C–C bands and four
CH-oop adjacency classes, which is 3, 5 or 8 families depending on how one counts). Same
sentence: "at r_f = one shell it is laptop work, at two shells B3" and Budget §4.13 "laptop at one
shell, B3 at two" — stated as fact, while the same sentence says "(c) is a probe batch like any
other … classified by Budget §2's rule", whose input is a timed probe that does not exist. Label
the B3 expectation as an expectation.
**Status:** open.

### 10. "One ring" survives once
**Where:** probes README 15.
**What.** "direct couplings from fragments of radius r_f (Ladder §3's rule: R3's value, or (b′)'s
if larger) and r_f + one ring carved from the R6 DFT geometry" — the Ladder, Goal item 1 (c),
Budget §4.13 and README 14 all say "r_f + one shell", and the Ladder defines the radius "counted
in ring shells". Under that definition "one ring" is ambiguous (the central ring plus one
peripheral ring is a ring-closed piece that is not a shell). Same file, two lines later: "B3 at
two shells".
**Status:** open.

### 11. The temperature floor: the 1 cm⁻¹ room-temperature term is unlabelled, and no rule says what a source with no stated temperature is
**Where:** Ladder §2 decidability paragraph; probes README 2a; Ladder §2 R0 row.
**What.** The formula is identical where it appears (Ladder §2 "u_T ≥ χ_max·(T_source − 296 K)
+ 1 cm⁻¹, for a room-temperature source u_T ≥ 1 cm⁻¹"; README 2a "χ_max·(T_source − 296 K)
+ 1 cm⁻¹"); χ_max = 0.03 is labelled "recalled" in both places it is given (Ladder §2; Method
debts). The 1 cm⁻¹ floor is not labelled at all — it comes from the Round-9 reviewer's recalled
benzene estimate ("of order −0.5 to −1 cm⁻¹ (recalled)"). Second, the rule has two branches,
"above room temperature" and "room-temperature source", keyed to "T_source the source's stated
temperature", and gives a default only for one source class ("the SRD 35 lightpipe temperature
once item 50's PDF is read, until then 250 °C, labelled recalled"). The benzene Coblentz gas entry
the R0 row lists states a pressure ("a Coblentz 2 cm⁻¹ gas spectrum"), not a temperature; the R0
row says "the entry scored is named in the pilot note". If that entry were named, who decides it
is room temperature? Write the default now: an entry with no stated temperature and no
documented cell is treated as hot (the GC-IRD default) unless its source documentation states
otherwise; R0's "unconditional" then rests, as intended, on the Quantitative IR series entries
that state their conditions.
**Status:** open.

### 12. The WebBook facts that decide R0 and R1 have no bibliography entry; the benzene list is recorded as opened by the reviewer only
**Where:** Ladder §2 R0 and R1 rows; Relevant_Scientific_Papers (no item); Proposal §5.2.
**What.** R0 row: "WebBook list opened 2026-09-04 by the Round-9 reviewer"; R1 row: "WebBook list
opened 2026-09-04 by the reviewer and the author". The naphthalene facts (245 °C vapour, GC-IRD,
no room-temperature gas spectrum) carry the author's opening; the benzene facts (the Quantitative
IR series at 0.125–1.93 cm⁻¹, the Coblentz 2 cm⁻¹ gas entry) — on which "R0 is unconditional"
rests — do not. Neither list has a bibliography item, so "verify-on-use … every identifier
re-fetched" has nothing to point at. Proposal §5.2 says of the R2 source "the 8 cm⁻¹ homogenised
resolution rests on a database description snippet and the vapour temperature on recall; both
are graded so in the bibliography" — item 50 grades the resolution; the 250 °C recall is graded
in Ladder §2, not in the bibliography.
**Status:** open.

### 13. "Several times the Δ₂ signal per bond" carries its provenance in the Ladder and not in the Distilled plan; the provenance is recalled numbers
**Where:** Ladder §3 "K is a measurement"; Distilled §3 "Responses".
**What.** Ladder: "the first-order term Δ₁·p — the CC−DFT force at the DFT geometry, which is not
zero and is several times the Δ₂ signal per bond at q_s = 1 (Round-9 Pass B finding 1)".
Distilled: "which cancels the first-order term Δ₁·p (the CC−DFT force at the DFT geometry,
several times the Δ₂ signal per bond)". The Round-9 review derived the ratio from "Recalled scale:
B3LYP and CCSD(T) aromatic C–C bond lengths differ by 0.001–0.003 Å … k ≈ 0.42 E_h/bohr²", both
listed under "Recalled, not opened". The Ladder's citation is to the review, not to a source; the
Distilled has no citation. Since the sentence justifies the ± pair design (a good design
regardless of the ratio), label it "recalled order of magnitude; the R_a by-product measures it".
**Status:** open.

### 14. Glossary gaps for the Round-9 objects
**Where:** Goal glossary; plan-05 README "Glossary" summary.
**What.** The glossary defines R_s, "re-projected", σ_g^assumed, u_band. Not defined there,
though used as terms in the frozen documents: **R_a** (Ladder §3, Distilled §3), **Δ₁** (only
"Δ₂, Δ₃, Δ₄" are listed under Δ), **ρ\*_common** (Ladder §1 record form, §3 Q8(c), Distilled Q8,
probes README 12 — the definition max(ρ\*(R_n), ρ\*(R_{n+1})) appears in the Ladder and Distilled,
consistently, but the Goal's cost question says only "read at a common threshold (Q8c)"),
**S_oo** and **continuity diagnostics** (Ladder §3, Budget §4.2, probes README 2, side project),
**shell** (the fragment radius unit), **pending (b′)**, **χ_max**, **T_source**, **u_T**, **χ_F**,
**pooled σ**. The glossary's σ_E entry reads "RMS residuals about a low-order polynomial fit",
which in letter is the √(SSR/n) the Ladder forbids ("never √(SSR/n), which under-reads σ by
√(4/9)"); it should say √(SSR/(n − p)), pooled per arm. The README's glossary summary list
(reading-order item 3) predates Round 9 and names none of R_s, R_a, ρ\*_common, u_band. Budget §3
uses "bf" (basis functions) undefined. No acronym is used before its glossary definition; no
section pointer I followed had moved (Ladder §5.4, §4.9, Budget §4.1b, Distilled §7/§8 all
resolve).
**Status:** open.

### 15. The fragment licence's lead sentence says "printed", not "passed"; the coronene "exactly two radii" is definitional, not geometric
**Where:** Ladder §3 fragment licence (lead sentence and (b)); Distilled §4; Mapping M07.
**What.** Ladder: "Fragment probing may produce a rung's Δ₂ only when all of the following have
printed: (a) … (b) … (b′) … (c)"; Distilled §4 forbids "starting R6 … as a fragment probe before
the fragment licence (Ladder §3) has printed parts (a), (b), (b′ where classified affordable) and
(c)"; Mapping M07: "none before the fragment licence's four parts (a), (b), (b′), (c) have
printed". A failed (b) has printed. The Ladder's closing sentence ("If neither (b) nor (b′) found
a passing radius smaller than its molecule, the licence is not earned and R6 is not
fragment-probed") and the "pending (b′)" clause close the loophole for (b)/(b′), and Distilled §8
carries the pending sentence ("R6 is not fragment-probed and the licence is neither earned nor
failed") — so the brief's questions are answered: a pending licence starts no R6 fragment
probing; (b′) needs no B3 if circumcoronene's whole batch classifies as B2; if B3 never exists
the Distilled §8 sentence is written. But "printed" should read "passed (or, for (b), passed or
pending resolved by (b′))" in all three places. Separately, Ladder §3 (b): "At coronene the
ring-closed fragments containing an interior pair are exactly two — the central ring (one shell)
and the whole molecule" is presented as a fact of geometry; it is a consequence of counting the
radius in complete shells (the central ring plus one, two or three peripheral rings are
ring-closed, H-cappable pieces that contain the interior pair, excluded only by the shell rule).
Say "by the shell rule" so a reader who knows coronene does not stop there.
**Status:** open.

### 16. Proposal survivors and internal contradictions
**Where:** Proposal §5.3, §7, §8, §9.
**What.** (a) §5.3: "If it succeeds, the gradient route is the plan's primary route on the rungs
it licenses" — the Goal: "on every rung where the side project's milestone licenses it, mode G
runs **in addition** and the rung carries two cost records"; no document ranks the modes, and the
side project §5 defers what changes on success to a dated note. (b) §8: "the benzene probe batch
and its references (the rung where a canonical coupled-cluster Hessian is expected to be
affordable — the only datum is a 2026-08 single-point timing on an older machine …)" against the
Ladder §3 "The **expected** printout, written now so it is not a contingency: the bias line fits
and the full reference does not." (c) §7 "seven inputs in hand — the laboratory side …, the
opponent side, a DFT-only dry run …, the frozen-space probe M1, a one-point canonical feasibility
probe, a run/no-run gradient check at equilibrium, and the naphthalene noise-floor measurement"
is a different seven from Budget §4's seven pre-note items (1, 1b, 2, 2a, 3, 4, 5 — which include
the R0 pilot and the u_band re-read and not "the opponent side"), and §8's pre-note list omits the
u_band re-read. (d) §9 (issue 8). (e) §11 risk 7 "an four-weekly". None of these changes the
plan; all would mislead a supervisor reading the proposal alone.
**Status:** open.

### 17. Side project: M2's "max component deviation" against an eight-energy FD check; M4 has no run/no-run although the licensing rule needs one
**Where:** Side project §3 M2, M4, M5 rows and "What success means"; Budget §4.3.
**What.** M2: "AD gradient (projection inside the graph) vs central finite differences of the
**re-projected** frozen-space energy, cc-pVTZ: max component deviation ≤ 10⁻⁵ E_h/bohr" — a
component-wise check of a 3N-vector needs 6N re-projected energies (72 at benzene); M4 and M5
specify "FD along the four Q6 modes, eight re-projected energies", which checks four projections,
not components. M2's FD energy count is not stated; say whether M2 is Cartesian (72) or
mode-projected (8) and use one criterion. Second: "Mode G is *licensed* on a rung when (i) the
milestone for that rung's molecule passed both checks … and (ii) the gradient probe printed 'run'
there" — the pre-note gradient probe runs "at the equilibrium geometry of benzene and naphthalene"
only (Budget §4.3), so for R2 and R3 the "run" must come from M4/M5; M5's row has "run/no-run",
M4's does not. The 36-gradient count itself is consistent everywhere (side project M2–M5, Budget
§4.11–12, probes README 6/12/13), and M4/M5 are classified by Budget §2 where they are defined.
**Status:** open.

### 18. Two small debt-list and erratum seams
**Where:** Frozen_Lines §7 debt 4 / bibliography item 20; Research note §9 last bullet.
**What.** Item 20: "Temperature-dependent PAH band shifts (tier-2 scoreboard) | Joblin-era
measurements — not identified | **NOT FETCHED** (debt 4)" and debt 4 "Joblin-era T-dependence
references (item 20)" — while item 52 now identifies Joblin et al. 1995 "Role of the temperature"
and item 53 Pirali 2009. Either item 20 points to 52–53 or the two are different debts (tier-2
emission scoreboard vs the u_band term); say which. Research note §9: "no maximal-overlap
assignment — §8's 'assignment switches' are a design artefact that no longer exists" — §8
contains no such phrase (the assignment object entered with Round-8 Pass B, after §8 was
written); the erratum should point at the Round-8/9 Ladder text, not at §8.
**Status:** open.

### 19. The feasibility-probe counts (61 / 72 / 1,801) are consistent but carry no arithmetic, and count in two different coordinate sets
**Where:** Ladder §3 anchor-basis bullet; Budget §4.1b; probes README 1b.
**What.** 61 = 1 + 2·30 (the diagonal along benzene's 30 modes — stated); 1,801 = 1 + 2·30 +
4·C(30,2) (a full Hessian by central mixed differences in the 30 normal modes — not stated);
72 = 2 × 36 (± along the 36 Cartesian coordinates — not stated). The gradient count is Cartesian
while the energy count is in normal modes (60 gradients in the mode basis would do); a reader
cannot check "only the count factors are deck numbers" without the products. One parenthesis
each. The "fits" rule and the one measured gradient are otherwise sound: the count factors are
frozen, the gradient's timing is measured, and "where the code has it" names PySCF's
`pyscf/grad/ccsd_t.py` (Ladder §3, Budget §4.1b, README 1b, all "fetched 2026-09-04 by the
reviewer and the author" — consistent with the Round-9 review's listing).
**Status:** open.

### 20. The cost record's ρ\*_common column cannot be filled when the record is first printed
**Where:** Ladder §1 cost record form; probes README 6, 12, 13.
**What.** The record form carries "K_off at the common threshold ρ\*_common = …" per rung, but
ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1})) needs the next rung; R1's record (README 8) is printed
before R2 runs, and R2 has two neighbours (R1→R2 and R2→R3 give two common thresholds). Say that
the record is printed with that column NOT_RUN and re-printed by the Q8(c) probe with both
common-threshold K_off values (README 12 already says "both K_off values printed"), or move the
column to the Q8(c) printout. The definition itself is the same in Ladder §1, §3 Q8(c), Distilled
Q8 and README 12; the Goal's cost question says "common threshold" without the max form (issue
14). The brief's loophole — re-running a rung to reach a lower ρ — is closed by Distilled §4
("Adding, removing or re-weighting patterns after any residual is known") and by "read from the
rungs' stored ρ(n) curves", since the stored curve is the record.
**Status:** open.

---

## What passed

Checked and consistent across the set; the author should not touch these:

- **The symmetrised response as one object.** R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) with the Δ₁·p
  and cubic terms cancelling is identical in Goal glossary, Goal step 2, Ladder §3, Distilled §3
  "Patterns"/"Responses", Budget §4.1 (the dry run uses R_s "exactly as in the real run"), probes
  README 6 and the research note §9. No document still says "the energy difference at the
  pattern geometry minus at equilibrium". The 2M single-mode block is "M modes × ±q_s" everywhere
  it is described; K = 2M + K_off holds with K_off in energies wherever the unit is stated
  (issue 2 is about the places it is not). The R6 floor "≥ 2,580 energies" = 2 × 1,290 follows and
  is the same in Goal, Ladder §2, Proposal §4 and the note §8; "≥ 204 + K_off" for coronene
  = 2 × 102 in Why_05 and the note.
- **The diagonal-cubic bonus** is "two extra energies per mode" in Goal, Distilled §3 and probes
  README 6, with the antisymmetric combination R_a as the source — Round-9 finding 12 closed.
- **The frozen space by projection.** Occupied and virtual vectors transported by projection and
  Löwdin-orthonormalised, no localiser, no assignment at a displaced geometry: Goal glossary
  ("re-projected"), Ladder §3, Budget §4.2, probes README 2, side project §1.2/§2/M1, and the
  research note §9 agree. The only "maximal overlap"/"assignment"/"permutation" survivors are the
  plan README's Round-8 Pass B record line (historical) and the side project's own account of
  why the earlier design was dropped (labelled as such). M1's printed list — smallest singular
  value of the occupied overlap, largest pre-Löwdin off-diagonal, both halves, E(frozen) −
  E(fresh) per point, no verdict, raw energies sealed — is the same in Ladder §3, probes README 2
  and the side-project M1 row (Budget §4.2 omits the fresh arm's localiser functional; a
  shortening, not a contradiction). The kill criterion and risk 3 no longer speak of switches.
- **R0 unconditional, R1 per family** in Goal prime directive, Ladder §2 (R0/R1 rows, the
  decidability paragraph, the dated notes), Distilled §1, Frozen_Lines criterion, Mapping M03,
  Proposal §5.2, Why_05 row 28, probes README 2a — the same expected verdict (R1 C–C inconclusive
  by construction unless a correction is pinned; C–H and CH-oop expected decidable). No "R0–R1
  unconditional" survivor outside issue 6. Items 52–53 carry the same grade everywhere (52
  "reference known, not opened", the snippet slope labelled snippet; 53 Crossref record, numbers
  not read), and the "first paid debt" wording is the same in README, Ladder §2, Why_05 row 28
  and the Method debts. Decided-vs-open: no "Round 9 Pass B owed", no "five review passes";
  "Six external review passes" (Proposal header) is correct; decision 7 is closed everywhere.
- **The fragment licence.** "One comparison at one shell" and "pending (b′)" are in Goal item 1
  (via the Ladder), Ladder §3, Distilled §8, Budget §4.12, probes README 13 and Proposal §5.2
  (in words); part (c) is "classified by Budget §2" in Ladder §3, Budget §4.13, README 14–15;
  Goal item 1 (c) carries the "which r_f" rule (Round-9 finding 11 closed); the fragment is
  written once (ring-closed, H-capped, unrelaxed, radius in shells); "shell" wording everywhere
  except issue 10.
- **ρ\*_common** = max(ρ\*(R_n), ρ\*(R_{n+1})), same mode and same prior, both counts printed:
  Ladder §1, Ladder §3 Q8(c), Distilled Q8, probes README 12–13 (issue 20 is about when it can be
  filled, not what it is).
- **The estimator** σ = √(SSR/(n − p)) with n = 9, p = 5 (degree 4) in mode E and p = 4 (degree 3)
  in mode G, pooled over the four modes per arm (ν = 16) and over 3N components in mode G,
  studentised residuals printed, |r| > 2.5 flagged: Ladder §3, Distilled Q6, probes README 5,
  side project M2 (issue 4 is about what gates, issue 1 about which σ the response carries).
  σ_g^assumed = 2.8·τ·q_s is a per-component scatter and remains consistent with a σ_g pooled
  over components; the 2.8 = 2√2 derivation sits beside 0.82 in the Ladder and is echoed in the
  note §9. ν = 4 / 16 and the 90 % range [0.42, 1.54] appear once each, in the Ladder, and are
  not contradicted.
- **36 gradients** (nine per Q6 mode) for M2–M5 in side project, Budget §4.11–12, probes README
  6/12/13; M4/M5 classified by Budget §2 in the milestone rows; M3's 28 GB explained; the
  side-project §4 budget and the kill clock unchanged. 72 energies for the R1 smoothness probe
  (4 × 9 × 2) in Ladder §2, Budget §4.5, README 5, Proposal §8. 8 re-projected energies in M4/M5
  (issue 17 is about M2 only).
- **The Round-9 review record** in the plan README: all twelve closure claims are in the text
  (1 R_s; 2 projection and continuity diagnostics; 3 R0-only, the floor, items 52–53; 4 the
  fragment written once, pending (b′), (c) classified, 360; 5 ρ\*_common; 6 √(SSR/(n − p)) pooled;
  7 36 gradients, σ_g pooled over 3N, M4/M5 classified; 8 M1 raw energies sealed; 9 one canonical
  gradient, expected outcome, DZ lower bound; 10 bond-count classes with S_class; 11 Goal item 1
  (c); 12 two extra energies). Ten are consistent across files; 1 and 6 are the ones issues 1–4
  are about.
- **Unsupported-claim candidates that are labelled.** `pyscf/grad/ccsd_t.py`: "directory listing
  fetched 2026-09-04 by the reviewer and the author" in all three places. Item 52's slope:
  snippet grade, in the bibliography only. χ_max = 0.03: "recalled" wherever given. The
  250 °C lightpipe temperature: "labelled recalled". The Hessian-QM9 size range: "recalled by the
  Round-8 reviewer, to be verified". The side project's memory sizing: "recorded as an
  expectation, not a number". No timing is used as a budget: every slot reads NOT_RUN; the Round-9
  reviewer's hour estimates appear only in the review, and the Ladder's "expected printout" carries
  no hours. Item 25's 84-atom/30-min figure is quarantined as a snippet in three places.
- **The debt lists.** Frozen_Lines §7 and the bibliography's "Named debts" are identical; the
  Method debts carry items 52–53 as "now named" and the χ_max recall; the research note's status
  line and §9 closing bullets match the frozen documents (issue 18 excepted).
- **Number drift not found** for 61 / 72 / 1,801 (Ladder, Budget, README 1b, plan README record),
  2,580, 204, 36, 72 energies, ν = 4/16, the 90 % range, the bibliography count (53 items; only
  the README's "23–51" lags, issue 8), and the change-table count (32 claimed; the table has 32
  row slots, one of them destroyed — issue 5).
- **The feasibility probe's decision rule** — "fits" = ≤ 168 h and ≤ 31.3 GB per object, the
  count factors frozen, one gradient measured, the DZ bias line a lower bound with "beat" from the
  TZ arm requiring DZ bias ≤ τ/2, the expected printout written as expected — is the same in
  Ladder §3, Budget §4.1b, probes README 1b and Distilled Q7/§8.
- **Section pointers** all resolve (Ladder §5.4, §4.9, §4 items 8–13; Budget §2, §4.1b;
  Distilled §7, §8; Mapping §3 M04 for "reading 1/2"); no acronym is used before the glossary
  defines it.

Pass A complete
