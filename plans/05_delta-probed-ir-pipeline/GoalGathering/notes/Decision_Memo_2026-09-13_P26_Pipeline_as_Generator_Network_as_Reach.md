# Decision memo 2026-09-13 — P26: the pipeline as a training-data generator, the network as the reach route

**Status.** Drafted at the user's request on 13 September 2026 after a discussion the same morning (the user's framing, the assistant's ordering of it, four questions answered). **A proposal, not a decision:** nothing in plan 05 changes until the user adopts it, and — the user's own point — nothing in plan 05 is truly frozen until the supervisor has read the proposal; the internal freeze of 4 September was discipline, not a contract. If adopted, this memo becomes a dated revision of plan 05 (the record stays; no plan 07), the proposal is updated before it is sent, and the numbered decision is next in line. Two of its inputs are measurements still running: the naphthalene xtight factor F (tonight; provisional 2.33) and the gradient-to-energy cost ratio g (M2a, this week).

## 1. The reframing, in three objects

1. **Pipeline A — the product.** Any PAH (composition, size, charge) → a cheap DFT step (geometry, Hessian, intensities) → **the network** → cheap post-processing → the full spectral shape (positions; intensities from DFT; anharmonic and temperature tiers from the existing post-processing layers the plan already names). This must be fast. The network sits inside it and need not produce the spectrum itself.
2. **Pipeline B — the training-data factory.** DFT Hessian + the probed coupled-cluster correction → labels. This is plan 05's present pipeline: expensive, exact where it runs. **A and B are not the same pipeline**; they share the DFT front end and the post-processing, and A uses B only through training.
3. **The network's output object** — the design choice everything hangs on, fixed backwards from two constraints: it must be learnable from what B can afford to produce, and with the cheap post-processing it must suffice for the spectrum.

The user's goal sentence, adopted as the criterion: *the network outputs what makes the project succeed within the compute budget, which is the desktop plus a small, free Snellius allocation.*

## 2. What the network outputs (question 1)

**(b) One correction per DFT normal mode, plus the few couplings the resonance-denominator rule selects** (plan 06 X10/P25: at benzene 19 of 47 symmetry-allowed pairs; the diagonal carries the band shifts, X2: −18 to +81 cm⁻¹, while only six couplings move a band by more than 0.5 cm⁻¹). From the DFT modes and this output the corrected Hessian and the harmonic spectrum follow in seconds. **(c) Per-family band corrections** (P19's object) are the aggregated, scoreable label on which the licence tests run. Not chosen: the full Δ₂ matrix (long-ranged and dense in real space — X8, X9, X15 — and mostly irrelevant to band positions), and any spectral quantity the cheap layers already supply.

The network is **charge- and spin-aware in its inputs from day one** (question 2): its architecture and labels carry charge and multiplicity; whether it may *speak* about a charge state is a licence question per state (§6), not an architecture question.

## 3. The rungs, re-read

- **R0–R1 (benzene, naphthalene): truth rungs, unchanged** — agreement with laboratory data, the opponents printed, the anchor at xtight (decision 20 stands for the anchor).
- **R2–R3 (pyrene class, coronene): transfer tests with thin decks, not full measurements.** The duration table of 13 September shows full symmetry-prior decks at R2–R3 to be out of reach on every route considered (thousands of desktop-days; the decks, not the machines). What R2–R3 must deliver in this framing is a *held-out check* of the network's per-family predictions: the diagonal of selected modes per family (and the P25 couplings) measured on one or two molecules of the class — the Budget's own "family- and mode-selective scoring", now with a purpose.
- **R4–R6 (circumcoronene class to C₃₈₄H₄₈): network predictions with a labelled uncertainty**, licensed per family and per charge state by the transfer tests below. The Ladder's R6 form ("fragment-probed Δ₂ only") is retired to an optional check where a fragment run is affordable; the deliverable for C₃₈₄H₄₈ becomes a *predicted* correction, said to be one. Module 02's count (56 symmetry-unique fragments of 600) remains the input for any such check.

## 4. The factory (pipeline B), re-scoped as a numbers machine

- **Per molecule:** the diagonal (2 energies per mode) plus the P25-selected couplings (2 per pair) — at naphthalene ≈ 100–140 energies instead of 474 — **or**, if M2a licenses gradients, 2 × (largest irrep block) gradients (X14: 18 at naphthalene); the switch between the two is g < ≈ 5–6 for the diagonal-plus-couplings deck.
- **Which molecules:** neutral closed-shell aromatics in numbers — small ones cheaply (a benzene-class diagonal deck is 60 energies at 36 min, a day and a half) and PAHs as far up as the budget reaches; Module 05's DFT–DFT corpus (11,321 molecules) as pre-training; per family a thin hold-out on the largest class still affordable.
- **Cations, phased (question 2):** the open-shell engine exists in our stack — pyscf-forge exports `ULNOCCSD` and `ULNOCCSD_T` (the latter a `_slow` implementation, untested by us); pyscf has canonical UCCSD; **PySCFAD has no unrestricted local CC**, so the gradient route is neutral-only for now. Cations enter as the second data class after one timed test on a small cation, by the energies route, with their own licence.
- **tight or xtight for training data (question 4): a measured choice, not decided now.** R0–R1 stay at xtight (truth). The first training molecule is measured at both thresholds; the threshold that buys the most transferable accuracy per desktop-day is then chosen, and the choice is a dated note. This does not reverse decision 20; it applies its method to a different purpose.

## 5. The budget objective, stated as a number the plan must print

Old: "afford the R2–R3 decks". New: **N molecules of stated classes, correctly labelled, within 365 desktop-days plus a small Snellius allocation**, with N a function of the measured F, g and P25 ratio, printed by `probes/duration_table.py` when they exist. Provisional arithmetic (F = 2.33, desktop = 2.3–3.8 × laptop, estimated): full decks 1.6–2.6 naphthalene-class molecules per year; diagonal + P25 couplings ≈ 8–12; gradients at g = 5 ≈ 30–50; benzene-class molecules in the hundreds on any route. The honest reading: **without P25 or gradients there is no training set within the year**; with both, there may be one. That is why the user's condition for the desktop (§6) is right.

## 6. Evidence before anything is bought or sent (question 3)

The user orders the desktop only when there is evidence the plan can succeed and the supervisor has approved. Evidence, in increasing weight:

1. **F and g** (this week): the price per molecule in both production modes; molecules-per-year as a printed number.
2. **P25 licensed at naphthalene** (days, after the BHHLYP Hessian; `x16_tensor_tests.py`): the deck shrinks without gradients.
3. **The first transfer test** (the crux of this framing): does a per-mode correction learned on one molecule say anything about another, per family? Pre-registered here in two stages: **T-1** on the DFT–DFT stand-in tensors that exist or are about to (benzene, naphthalene; later anthracene/pyrene from plan 02's B3LYP Hessians plus one BHHLYP Hessian each — hours of psi4): the per-family diagonal correction of naphthalene predicted from benzene's by the simplest rule (same family, same correction per unit ω), against the measured one; **T-2** the same with one real CC hold-out at tight. Losing condition, written now: if the per-family transfer error at T-1 exceeds the family's laboratory margin (Module 03's u_band; ≈ 2.5 cm⁻¹ at R0 gas phase) for the C–H stretch and C–C stretch families, the numbers-machine framing does not carry to the sizes it is meant for, and the plan falls back to §9.

The proposal is not sent before 1 and 2; 3 is either done before sending or named in it as the first milestone with its losing condition.

*The user agreed on 13 September ("Akkoord met T-1 en de verliesdrempel; wacht op F") to the form of T-1 and to the losing threshold above; the memo itself waits for F before adoption.*

## 7. What changes in which document, if adopted

| document | change |
|---|---|
| Frozen Ladder §… (rungs) | R2–R3 "transfer tests with thin decks"; R4–R6 "network predictions, licensed per family and charge state"; R6's fragment-probed form → optional check |
| Decision 32 (network) | from stand-out follow-up to the reach route; its losing condition becomes the licence (per family, τ_F) |
| Compute Budget | the objective of §5; the per-rung cost sentences become per-molecule cost sentences; the duration table's second variant with thin decks |
| Proposal §1, §3, §6, §12 | the two pipelines; the output object; the calendar as molecules-per-year; the §12 table (questions settled: desktop as (e), Snellius on 4 nodes, R3 row kept and labelled, M2a row in, module rows as "hours") |
| Modules 05 and 06 | from efficiency experiments to core: the network (05) and the deck proposer (06) are pipeline A's engine |
| Pilot note skeleton | item 5's effect size becomes the transfer-test threshold; item 15's coverage applies to the training classes |
| Plan 06 | unchanged in content; its decision rule's branch C now serves §5 directly |

## 8. What stays

The truth rungs and their opponents; the scoreboard and u_band; the pre-registration discipline (recipes and losing conditions before data); the probing algebra and the frozen spaces as the measuring instrument; Modules 02–04 as built; the house rules (measured not asserted, never cite from recall, dated notes).

## 9. Risks and the fallback

- **Too few CC-labelled molecules to learn transfer** (the central risk; the Δ-learning literature used hundreds of CC points for one molecule). Mitigation: pre-train on the DFT–DFT corpus; make the output small (§2); test transfer at T-1 before spending CC time. Fallback if T-2 fails: pipeline B stays a per-molecule measurement for what is affordable, and the network is only a prior (Module 05's original role); R4–R6 lapse with that sentence.
- **Open-shell cost unknown** (ULNO-CCSD(T)_slow): one timed test before cations are promised.
- **Transfer that holds at naphthalene and fails at pyrene**: exactly what the thin hold-outs on R2 are for; the licence is per family, so partial success is reportable.

## 10. Bookkeeping if adopted

Decision number next in line; the dated revision of the Ladder, the Budget and the proposal (§7); a software-ledger row when the open-shell engine is first run; `duration_table.py` gains the molecules-per-year block and the thin-deck variant; the pilot-note skeleton updated. The plan-06 decision rule is unchanged; its 15 October date now also decides §5's number.
