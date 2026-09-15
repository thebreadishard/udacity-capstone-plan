# Draft 2026-09-15 — P27: the slow ladder of decision 39, priced on the measured cc-pVDZ energy (proposal, open; for the user after 18:00; nothing applied)

*Written 15 September 07:xx–08:xx while M3's cc-pVDZ cells run (nine of fifteen geometries done at 06:52). The price it uses is the one M3 has already measured — 4,159 s for a naphthalene LNO-CCSD(T)/cc-pVDZ energy at the tight thresholds in the frozen arm, 1.5 GB resident — not M3's verdict, which comes at ≈ 13:45 today and decides whether that price may be used at all (decision 36's conditional). Every number below is marked **m** (measured) or *e* (estimate); an *e* is replaced by the first timed energy of its rung, which is the first job of every rung.*

## 1. What decision 39 asked, and what this note adds

Decision 39 (14 September evening) builds the ladder ring by ring with ions: anthracene and phenanthrene inserted as the isomer test at three rings; pyrene, perylene and coronene as the peri main axis; the acenes as a stress branch with the anchor's own diagnostics printed; cations at the two smallest rungs; the per-family go/no-go read after the three-ring rung. It priced the three-ring rung at "≈ 2–3 desktop-weeks together, estimate".

This note adds three things. **(i) The deck sizes are now counted, not guessed**, from the point group alone (`probes/deck_counts_planar.py`, naphthalene's 141 pairs reproduced as the check): phenanthrene, being C₂v rather than D₂h, allows more than twice as many symmetry-permitted couplings as anthracene, so the isomer pair costs 2,250 energies as full decks — the "2–3 desktop-weeks" of decision 39 holds only for **diagonal-first decks at the tight thresholds**, which is therefore what §4 proposes for the go/no-go. **(ii) The cation gap is given its rows** (obstacle 9), with a physics point that changes the order: naphthalene⁺ is the clean first cation deck; benzene⁺ is Jahn–Teller active and needs a deck-design decision before any energy is spent on it beyond the timing point. **(iii) A calendar to the go/no-go** on the laptop alone and with the desktop, under the measured cc-pVDZ price, so that the 26 September proposal can say when the plan knows whether the size axis transfers.

## 2. Deck sizes per molecule (counted 15 September)

Rule: the symmetry prior (proposal §3.2) keeps couplings between modes of the same irrep. Full deck = 4M + 2E (M modes, E same-irrep pairs, the convention of `duration_table.py`); **H deck** = decision 37 applied (one energy instead of a ± pair for every pattern confined to a non-totally-symmetric irrep); **diagonal H deck** = the single-mode block only (two amplitudes per mode; ± pairs only for the totally symmetric modes); **H + P25** = the H deck with the couplings thinned to the 40 % that plan 06's free DFT rule keeps at benzene (19 of 47 pairs, X10 — an *e* until the naphthalene repeat).

| molecule | rings | group | M | totally symmetric | E | full deck | H deck | diagonal H deck | H + P25 |
|---|---|---|---|---|---|---|---|---|---|
| benzene (R0, as measured) | 1 | D₆h | 30 | 2 | — | **448 m** (the dry run's K, before the prior) | — | 60 | — |
| naphthalene / naphthalene⁺ | 2 | D₂h | 48 | 9 | 141 | 474 | 291 | 114 | 185 |
| anthracene | 3 | D₂h | 66 | 12 | 277 | 818 | 499 | 156 | 293 |
| phenanthrene | 3 | C₂v | 66 | 23 | 584 | **1,432** | 1,015 | 178 | 513 |
| pyrene | 4 | D₂h | 72 | 13 | 332 | 952 | 580 | 170 | 334 |
| tetracene | 4 | D₂h | 84 | 15 | 456 | 1,248 | 759 | 198 | 422 |
| perylene | 5 | D₂h | 90 | 16 | 526 | 1,412 | 858 | 212 | 470 |
| pentacene | 5 | D₂h | 102 | 18 | 682 | 1,772 | 1,075 | 240 | 574 |
| coronene | 7 | D₆h | 102 | — | — | ≈ 842 (duration table; degenerate irreps not recounted here) | — | 204 | — |

Two remarks. The duration table's counts for pyrene (936) and tetracene (1,218) were slightly low; the counts above supersede them by 16 and 30 energies and should replace them when the table is next printed. Chrysene (≈ 2,100) and triphenylene (924), both in today's R2, are not in this table on purpose: Module 03 measured their gas-phase columns undecidable by construction, and under P26 they are better used as network hold-outs at DFT level (the corpus carries them) than as coupled-cluster decks — §6 proposes that.

## 3. The price per energy in cc-pVDZ, and why the ring-by-ring order is also the honest way to extrapolate

| molecule | fragments (valence LMOs) | tight cc-pVDZ energy, laptop | status |
|---|---|---|---|
| benzene | 15 | 180 s | **m** (I7, 14 September) |
| naphthalene | 24 | 4,159 s = 1.15 h (arm C reference 4,403 s); 1.5 GB resident | **m** (M3 cells, 14–15 September) |
| anthracene, phenanthrene | 33 | 2.5–5 h | *e*: 33 fragments at 1.5–3 × naphthalene's 173 s per fragment |
| pyrene | 37 | 3.5–9 h | *e* (2–5 × per fragment) |
| tetracene | 42 | 4–10 h | *e* |
| perylene | 46 | 5–12 h | *e* |
| coronene | 54 | 8–21 h | *e* (3–8 × per fragment) |

The per-fragment cost rose 14-fold from benzene to naphthalene (12 s → 173 s) because the local domains of a two-ring molecule are still growing with the molecule; local correlation methods stop growing per fragment once the molecule is larger than the domain, and where that happens for this engine is exactly what the ring-by-ring ladder measures — three timed points (naphthalene, anthracene, phenanthrene) fit the exponent that prices rungs 4 and 5, which is the "price curve over three sizes" of decision 39. The factors above are the honest band until then; xtight multiplies each by 3.34 (**m** at naphthalene, cc-pVTZ; assumed to carry to cc-pVDZ until M3's xtight cell exists). **Memory:** the naphthalene cc-pVDZ energy ran in 1.5 GB against 19.8 GB at cc-pVTZ, so by estimate every molecule in the table fits the laptop's 25 GB at cc-pVDZ, and the "does not fit" of the duration table's R2–R3 rows is a cc-pVTZ statement. That is the second thing M3 licenses, beside the price.

Desktop = 2.3–3.8 × the laptop, the core-count estimate of the Compute Budget, never timed.

## 4. The three-ring rung, designed for the go/no-go (proposed)

**What the go/no-go needs.** Decision 39 reads it per band family from the transfer 2 → 3 within 2.5 cm⁻¹ for both isomers. The quantity that transfers is the **per-mode diagonal correction** (the network's output; the couplings enter the positions only through the second-order shifts, which the R0/R1 full decks have already characterised). So the go/no-go does not need the couplings of the three-ring molecules; it needs their diagonal blocks, and a sample of couplings only to check that the coupling *pattern* (which pairs are large) is what the R1 deck and P25 predict.

**Deck order at rung 3: diagonal first.** Each isomer's deck is consumed diagonal block first (156 and 178 energies, the H diagonal decks), then the couplings in the hashed order of §3.4 until the stopping rule or the rung's budget stops them. The transfer test is read when both diagonal blocks are complete; the couplings that follow are finishing work, as decision 39 already says of rungs 4–5.

**Thresholds at rung 3: tight.** The transfer test's threshold is 2.5 cm⁻¹ per family; the tight thresholds' bias at benzene was +0.47 / +0.03 / +0.79 cm⁻¹ against xtight's +0.11 / −0.01 / +0.23 (**m**), a fifth of the threshold at worst. The xtight choice of decision 38 protects R1's *agreement* claim, where the laboratory column is a few tenths of a cm⁻¹; it does not bind a transfer test judged at 2.5 cm⁻¹. Proposed: rung 3 at tight, stated as such, with one xtight energy per isomer at q = 0 as the printed bias check (2 × 8–17 h).

**The isomer rule.** A family goes when both isomers transfer within 2.5 cm⁻¹ (RMS over the family's modes, the network trained on R0–R1 plus the corpus predicting, the measured diagonal judging). A family for which one isomer transfers and the other does not is **topology-sensitive**: it is not refused, it is licensed per topology (acene-type / phenacene-type, the classes the corpus can label), and rung 4 must contain one molecule of each class before the family may be claimed above three rings — which the main-axis/stress-branch pairing of decision 39 provides (pyrene and tetracene).

**Cost of the go/no-go under this design** (both isomers, diagonal H decks, 334 energies):

| route | tight cc-pVDZ | xtight cc-pVDZ (for comparison) |
|---|---|---|
| laptop | 35–70 days *e* | 115–230 days *e* |
| desktop | 9–30 days *e* | 30–100 days *e* |
| Snellius, four thin nodes | ≈ 3–10 days *e* (SBU ≈ 6,000–20,000 at 200–300 SBU per naphthalene-size energy × 2–5) | — |

The "2–3 desktop-weeks" of decision 39 is the middle of the tight row. The full decks of both isomers (2,250 energies; 1,514 as H decks) are 160–320 laptop-days at tight even as H decks — desktop-months, not weeks — and are **not** what the decision needs; they are printed here so that nobody reads the go/no-go's price as the rung's price.

**Anchor diagnostics printed per molecule** (decision 39; at rung 3 already, so that the acene branch's first point has a neutral comparison): the T₁ diagnostic of the reference CCSD, the (T) share of the correlation correction to each fundamental, the largest LNO domain size, and for cations ⟨S²⟩ of the UHF reference and the spin contamination after CCSD. A molecule whose T₁ exceeds the conventional threshold (0.02 — its source to be Crossref-verified before the proposal prints it) has its anchor marked "single-reference doubtful" and its rows carry that label; the plan-06 reading note already records that long acenes are expected to reach that region (Hachmann et al. 2007, as cited there), which is why they are the stress branch and not the main axis.

## 5. The cations (obstacle 9; the user, 14 September: "Onthoud dat we dat gat moeten dichten")

**Order changed by physics: naphthalene⁺ first, benzene⁺ as the timing molecule only.** Benzene⁺ has a doubly degenerate electronic ground state in D₆h (the hole sits in the degenerate highest occupied π orbital), so it is Jahn–Teller active: the nuclear frame distorts to D₂h, the two D₂h components are nearly degenerate, and the surface along the pseudorotation coordinate is flat and strongly anharmonic. A static deck of quadratic responses about one D₂h minimum measures a Δ₂ that is well defined for that stationary point but does not describe the observable spectrum without a vibronic treatment that this pipeline does not contain. Naphthalene⁺'s ground state is non-degenerate in D₂h; its deck is the neutral's (474 / 291 / 114 energies), its point group and frozen-space machinery are the neutral's, and it has gas-phase and matrix spectra to score against (sources to be named before Module 03 prints them, under the no-swap rule; none named here from memory). Proposed: **R1⁺ = naphthalene⁺ full H deck**, the first cation of the label plan; **R0⁺ = benzene⁺ timing point** (one cc-pVDZ energy at the D₂h minimum, the ⟨S²⟩ and T₁ printed) and a written decision on whether benzene⁺ gets a deck at all, taken with the supervisor.

**Price: the one number the plan does not have.** `ULNOCCSD_T` exists in the installed pyscf-forge; its (T) kernel is a NumPy reference implementation, not the compiled kernel of the restricted path, so the cation/neutral cost ratio *c* is unknown and may be large. Today's machine slot times it: the shipped unit test, then a small radical (the smoke test the 14 September rule requires), then one benzene⁺ cc-pVDZ tight energy against the neutral's 180 s. Rows for the affordability table, to be filled with *c*:

| deck | energies | price | laptop | status |
|---|---|---|---|---|
| R0⁺ benzene⁺, timing point | 1 | 180 s × *c* | today | the measurement of *c* |
| R1⁺ naphthalene⁺, H deck, xtight cc-pVDZ | 291 | 3.9 h × *c* | 47 days × *c* | after R1; if *c* > 3 the deck runs at tight (14 days × *c*) or on the desktop |
| R1⁺ diagonal H deck only (fallback) | 114 | 3.9 h × *c* | 18 days × *c* | the cation's transfer datum without its couplings |

***c* measured 15 September 15:26 (`probes/results_m4/m4_timing_benzene_cc-pvdz_tight.json`, quiet machine): benzene neutral LNOCCSD_T tight 164 s, benzene⁺ at the same geometry `ULNOCCSD_T` tight 5,096 s (15 + 14 spin-fragments, 4.2 GB, UHF ⟨S²⟩ 0.870 after one stability round) → c = 31.0.** Read into the rows: R1⁺ H deck at xtight ≈ 1,460 laptop-days, at tight ≈ 430, the diagonal H deck at tight ≈ 170 — **no cation deck fits the laptop with the installed unrestricted code**, and on the desktop only the diagonal deck at tight (45–75 days) would. So the remedy is software, as the paragraph below anticipated, and the plan should say so: the first item is a *split* of the 5,096 s between the unrestricted CCSD and the NumPy (T) kernel (one more benzene⁺ run without (T), ≈ 1 h, queued), because only the (T) part is a bounded port — if (T) is most of it, an unrestricted (T) kernel on PySCF's compiled restricted one brings c towards the UCCSD/RCCSD ratio of ≈ 3 and the R1⁺ diagonal deck back to ≈ 16 laptop-days at tight; if the UCCSD dominates, the cation labels are a cluster item and the proposal says so.

If *c* is large because of the NumPy (T) kernel, the remedy is software, not budget: an unrestricted (T) kernel is a bounded port (the restricted compiled kernel exists in PySCF; the user's 13 September rule allows own software), and the Software Changes Ledger would get its row. The plan should say which of the two it does once *c* is measured — it now is — and the split decides which.

## 6. The ladder under P27 (texts proposed for the Ladder §2 and the proposal §5.2; dated revisions)

Labels R0–R6 are kept (they are in every document); the accuracy rungs above naphthalene are split by ring count, and the cations get their own lettered rungs.

| rung | molecule(s) | type | deck | what it decides |
|---|---|---|---|---|
| R0 | benzene | agreement | full, cc-pVTZ xtight (**m** 448 at 76 min) | probing licence; canonical bias line |
| R0⁺ | benzene⁺ | timing point + JT decision | 1 energy | *c*; whether benzene⁺ gets a deck |
| R1 | naphthalene | agreement + CC-adds | H deck, cc-pVDZ xtight if M3 licenses it (291 at 3.9 h *e*: 47 laptop-days) else cc-pVTZ on the cluster | the anchor licence; the first transfer datum |
| R1⁺ | naphthalene⁺ | agreement (gas/matrix columns to be named) + the charge-state transfer datum | H deck, cc-pVDZ | whether the network may be licensed per charge state |
| **R2a** (new) | anthracene + phenanthrene | **transfer, isomer test** | diagonal H decks first (156 + 178), tight; couplings as finishing work | **the go/no-go per family; the price exponent** |
| R2b | pyrene (main axis) + tetracene (stress) | transfer | diagonal-first H decks, only for families that went at R2a | topology classes above three rings; acene diagnostics |
| R2c | perylene (main) + pentacene (stress) | transfer | thin decks, conditional on R2b | the five-ring datum; the acene stress test's expected failure region |
| R3 | coronene | transfer (cold column primary, decision 24) | thin deck | the peri axis at seven rings |
| R4–R6 | as today (network rungs under P26) | reach | — | — |

Chrysene and triphenylene leave R2 and become network hold-outs at DFT level (Module 05's corpus and Module 03's scoreboard keep them); their coupled-cluster decks (≈ 2,100 and 924 energies) are struck. The rungs' per-family sources, the no-swap rule, Q6–Q8 on the full-deck rungs, the seal discipline and the stops are unchanged.

## 7. The calendar to the go/no-go (for the proposal §12, scenario paragraph)

Assumptions: M3 licenses cc-pVDZ (13:45 today decides; if not, every cc-pVDZ row below reverts to the cluster route of the 14 September table); the naphthalene dry run licenses I14 (this week); the laptop is free for the anchor from early November (the R0 pilot, the σ-run and the pilot-note inputs come first, as the README queue says); one anchor job at a time.

| step | laptop alone | with the desktop from November *e* |
|---|---|---|
| R1 naphthalene H deck, xtight cc-pVDZ | 47 days → mid-December 2026 | 12–20 days → late November |
| R0⁺ / R1⁺ | *c*-dependent; R1⁺ diagonal 18 × *c* days | 5–8 × *c* days |
| R2a diagonal decks, tight | 35–70 days | 9–30 days |
| **go/no-go per family** | **February–April 2027** | **December 2026–January 2027** |
| R2b (for the families that went) | after the go, finishing work | February–March 2027 |

The corpus factory (177 laptop-days for layers A + A′ + B, Timing Note of 14 September) competes for the same machine and is not in these rows; on the laptop it displaces the anchor day for day, which is the strongest single argument for the second machine or for running the factory on the cluster's psi4-less nodes with another Hessian engine — a separate decision, not taken here. On the laptop alone the plan reaches its go/no-go before the defense calendar's Module 08 (16 April 2027) but with nothing above three rings measured; with the desktop it reaches it with a quarter of the year left for R2b and the network's licence per family.

## 8. Proposed texts (all as dated revisions, none applied)

- **Proposal §5.2:** the table of §6 above replaces the R2/R3 rows; a sentence after it: "The three-ring rung is the plan's decision point: it is priced at 35–70 laptop-days (estimate, on the measured cc-pVDZ energy of 15 September) and read per family from the diagonal blocks of both isomers; the full decks above naphthalene are finishing work after that reading, not its precondition."
- **Proposal §12, scenario paragraph:** add "The go/no-go on the size axis falls in February–April 2027 on the laptop alone and in December 2026–January 2027 with the desktop; in both scenarios it precedes Module 08."
- **Proposal §13 item 5 (cluster request):** "sized by the measured anchor energy" → "…and containing, if the laptop's go/no-go is a go, the R2b decks (pyrene and tetracene, ≈ 170 + 200 diagonal energies at 3.5–10 h each, estimate) as the allocation's second job".
- **Ladder §2:** the R2a/R2b/R2c rows and the two cation rows; the isomer rule of §4 as a bullet under §3 ("Transfer tests"); the anchor diagnostics as a bullet under §4 ("fixed at the pilot note: the T₁ threshold's source").
- **P26 label plan (Decision Memo §4/§5):** the budget objective gains the two cation rows and the R2a diagonal rows; the "per family and charge state" sentence now has a charge state to point to.
- **Cover note (Dutch, in the user's voice), one sentence after the M3 conditional:** "Als die stap standhoudt, weet het plan in de winter — op mijn laptop uiterlijk in het voorjaar — per bandfamilie of de correctie van twee naar drie ringen overdraagt; alles boven drie ringen is dan afwerking, geen voorwaarde."
- **Mandate ledger obstacle 9:** the rows of §5; status "priced on paper, *c* unmeasured, timing today".
- **duration_table.py:** pyrene 952, tetracene 1,248; new rows for anthracene, phenanthrene, perylene, pentacene, naphthalene⁺ (from `deck_counts_planar.py`).

## 9. What the user decides

1. Rung 3 (R2a) as **diagonal-first decks at tight** with one xtight bias point per isomer — yes / full H decks at xtight (160–320 laptop-days) / other.
2. The **isomer rule** (topology-sensitive families licensed per class, rung 4 must hold one of each class) — yes / stricter (both or refuse) / other.
3. **Naphthalene⁺ first, benzene⁺ timing point only** with the Jahn–Teller decision deferred to the supervisor — yes / benzene⁺ deck anyway / no cations before the go.
4. **Chrysene and triphenylene struck** from the coupled-cluster ladder (network hold-outs at DFT level) — yes / keep as thin decks / no.
5. Whether the **calendar of §7** goes into the proposal §12 as written (with M3's verdict of today filled in) or only the laptop-alone column.
6. Whether the **corpus-factory sentence** of §7 (the factory displaces the anchor day for day on one machine) is said in the proposal's §8 or kept for the annex.

## 10. Bookkeeping if adopted

README: decision 41 under decision 39 with the texts applied; Ladder §2–§4 dated revision; proposal §5.2/§12/§13 dated revision; Decision Memo P26 §4–§5 dated addition; ledger obstacle 9 rows; `duration_table.py` re-printed with the new counts; the affordability table (plan 06 Cost Ladder §5 and the annex) gains the R2a and cation rows; the cover note's sentence. Nothing here touches the running M3 cells or the queue of decision 38c.
