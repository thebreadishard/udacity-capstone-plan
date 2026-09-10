# Cold read — Project_Proposal_2026-09-06.md

**Reader.** The student's academic supervisor: an experimental and computational spectroscopist of PAHs, co-author of the anharmonic quartic-force-field papers behind the PAHdb Anharmonic library (Mackie et al. 2015, 2016) and of jet-cooled IR studies of PAHs (Maltseva et al. 2016). First reading, one sitting, sympathetic but exacting.
**Scope.** This file only (`plans/05_delta-probed-ir-pipeline/GoalGathering/Project_Proposal_2026-09-06.md`, 937 lines). No other files, no web. Quotations are exact; line numbers refer to the file as read.
**Date.** 2026-09-08.

Classes: **BLOCKING** — a false, contradictory or unverifiable statement; a claim an insider would object to; a number that disagrees with another number in the document. **MAJOR** — inconsistency between sections; a term used before it is defined; an argument that does not follow; a place where the reader cannot tell what is measured vs asserted vs promised. **MINOR** — wording, redundancy, formatting.

---

## Numbered findings

### 1. The document's own date and its "cold-read before being sent" claim are contradicted by its contents — BLOCKING
- **Lines** 3–4, 66, 153, 242, 250, 252, 591, 710, 801, 901–902.
- **Quoted.** L3–4: "Prepared for supervision review, 6 September 2026." L66: "This document itself was cold-read the same way on 6 September before being sent." L153: "found on 8 September after the first search missed it". L242–243: "finished on 8 September". L250: "was decided on 8 September: measure first". L252: "started that evening and ends on 9 September". L591: "The following were printed between 5 and 6 September". L710: "(6–8 September; result in §3.3)". L801: "(collected 8 September;". L901: "Crossref record, 8 September".
- **What is wrong.** The text is dated 6 September and says it was cold-read on 6 September "before being sent", yet it contains measurements, a decision, references and a whole block of questions dated 8 September, and §8 says its numbers were printed "between 5 and 6 September" while listing the cc-pVTZ scan that ended on the 8th. The reader cannot tell which version she holds, whether the 6-September cold read saw the 8-September material, or which numbers post-date the "closed" review loop (L666).
- **Fix.** Re-date the document (8 September) and its file name; state that the 6-September cold read covered an earlier state and the 8-September additions were not cold-read; correct L591 to "5–8 September".

### 2. "All of these sources were read in full" is contradicted by the reference list — BLOCKING
- **Lines** 385–386 vs 866–868, 907–909.
- **Quoted.** L385–386: "All of these sources were read in full on 6 September 2026 and their conditions transcribed". L867–868 (Brumfield et al. 2012): "Crossref record; content at snippet grade; band origin not read." L909 (Maltseva et al. 2016): "Crossref record; abstract grade."
- **What is wrong.** Two of the laboratory sources named in the preceding paragraph (L383, L404–405) are declared, in the same document, as read only at abstract or snippet grade. For the supervisor, whose own 3 µm data (Maltseva 2016) are being adopted as a scoring column, this is a false statement about her paper.
- **Fix.** Replace with "Chu 1999, Schneider 2024, Pirali 2009, Joblin 1994/1995, Lemmens 2019/2021 were read in full; Maltseva 2016 and Brumfield 2012 are held at abstract/snippet grade and their band tables are requested (§13, item 8)."

### 3. Decisions 20 and 21 are cited but do not exist in §10, which says "all closed" — BLOCKING
- **Lines** 255, 380, 815–816 vs 675–718, 668.
- **Quoted.** L255: "(research note P10, decision 20)". L380: "since the fundamental is read directly — decision 21)". L815–816: "the 0.5 cm⁻¹ upper bound adopted here (decision 21)". L675: "## 10. Decisions the student made (all closed; a supervisor's objection would reopen any of them)". L668: "the decisions of 5–6 September (§10, items 8–19) are such notes."
- **What is wrong.** §10 lists items 1–19 and §9 says the decisions run to item 19; two further numbered decisions are invoked and never stated. Decision 21 fixes a scoring constant (the Q-branch head-to-origin term) and decision 20 the disposition of the anchor's basis-dependent bias — both are things she is being asked to endorse by reading §10.
- **Fix.** Add items 20 and 21 to §10 under an 8-September heading with their text; update L668 to "items 8–21".

### 4. The anchor's own basis-set incompleteness is absent from the error budget, and the expected-effect line is measured against a different, better reference than the anchor — BLOCKING (insider objection)
- **Lines** 241, 358–360, 736–738, 569–571.
- **Quoted.** L241: "cc-pVTZ, the basis the licence rungs use". L358–360 (the error budget): "DFT level, held-out residual, measured noise and space-freezing bias, the share of the family's correction that comes from couplings beyond the locality test's radius, and the matrix–gas shift where matrix data is used." L737–738: "B3LYP/N07D against CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies, mean absolute difference 5.45 cm⁻¹".
- **What is wrong.** The correction Δ₂ is defined against LNO-CCSD(T)/cc-pVTZ (plus a composite MP2 term). CCSD(T)/cc-pVTZ harmonic frequencies are not converged to the few-cm⁻¹ level the beat margins will sit at; the residual basis-set error of a triple-zeta harmonic force field is of the same order as the 5.45 cm⁻¹ effect the plan hopes to buy, and it is systematic per family (C–H stretches and ring modes move differently towards the basis-set limit). The budget lists the local-approximation bias, the noise and the freezing bias, but no term for "distance of the anchor from the canonical CBS harmonic". Worse, the only literature number for the expected effect (L738) is an F12/near-CBS comparison, so the pipeline's anchor and the expected-effect line are not at the same level; a supervisor cannot tell whether the plan expects to recover 5.45 cm⁻¹ or something smaller after cc-pVTZ error is subtracted.
- **Fix.** Add a basis-set line to the anchor licence and to the per-band error budget (a cc-pVTZ→cc-pVQZ or F12 diagonal check at benzene is 61 energies, the same size as the bias line already planned), and restate the expected-effect line at the anchor's own level or say explicitly that it is an upper bound.

### 5. "energy-only probing cannot produce the three-index cubic constants" is false as written — BLOCKING (insider objection)
- **Lines** 111–114.
- **Quoted.** "energy-only probing cannot produce the three-index cubic constants that PAH combination-band resonances need, so a coupled-cluster anharmonic correction was not merely unnecessary but unbuildable with the probes specified."
- **What is wrong.** Every quartic force field in the tradition the plan opposes and cites (SPECTRO-based QFFs; the hybrid CC/DFT fields of Boese et al. and Bégué et al.) obtains cubic and quartic constants from energies at displaced geometries. What is true is the second half of the sentence — the ± two-amplitude, one- and two-mode probe deck specified here cannot deliver φ_ijk with i≠j≠k. The first clause, read alone, tells a QFF author that the student does not know how QFFs are made.
- **Fix.** "the probe set specified here (single- and paired-mode displacements at two amplitudes) cannot produce the three-index cubic constants … ; obtaining them from energies needs three-mode displacements at coupled-cluster cost, which was ruled out."

### 6. The naphthalene energy-route cost the document computes exceeds its own 168-hour rule, contradicting "within reach of this machine" and "guaranteed route" — BLOCKING (number vs number)
- **Lines** 191–197, 633, 462, 367.
- **Quoted.** L192–195: "48 modes × 4 diagonal energies plus about 0.9 energies per allowed coupling plus the held-out fraction is of order 350–400 energies, i.e. 200–250 hours — a few weeks of unattended laptop time, classified by the 168-hour rule of §8 once the naphthalene time is known". L196–197: "The prior is what brings the energy route at naphthalene within reach of this machine at all". L633: "(168 hours of wall-clock per batch is the line)". L462: "if it fails, the energy route remains the guaranteed route". L191–192: "(naphthalene's will be longer and is measured before the note)".
- **What is wrong.** 200–250 h at a benzene per-energy time that the same sentence says will be longer at naphthalene is already above the 168-h line; by the plan's own rule the R1 energy route is cluster work, yet R1 is where "the anchor licence closes" (L367) and cluster access is only to be requested "when the naphthalene measurements justify it" (L794). The energy route is therefore not guaranteed on the only machine the plan has, and the circularity (R1 needs the cluster; the cluster request needs R1) is not acknowledged.
- **Fix.** Either state that the 168-h rule applies per sub-batch and that R1 is a multi-batch laptop job with a calendar estimate, or state plainly that R1 is expected to be cluster work and reorder the ask in §13 item 5 accordingly. Also correct "a few weeks": 200–250 h is 8–10 days.

### 7. Two different wall-clock figures for the same canonical CCSD(T)/cc-pVTZ benzene energy — BLOCKING (number vs number; probably benign, but unexplained)
- **Lines** 610–611 vs 243, 612–613.
- **Quoted.** L610–611: "Canonical CCSD(T) energy of benzene: 27 s at cc-pVDZ, **755 s and 7.3 GB at cc-pVTZ**." L243: "canonical 14–21 min". L612–613: "61 canonical energies along benzene's 30 modes — is therefore about 13 hours".
- **What is wrong.** 755 s is 12.6 min; the scan's own truth line took 14–21 min per point. The 13-hour bias-line estimate uses 755 s; at the scan's rate it is 14–21 h. The reader cannot tell which is the timing "the pipeline depends on" nor why they differ (load, displaced-geometry symmetry loss, concurrent arms).
- **Fix.** Give one number with its condition (equilibrium, D₆h vs displaced, alone vs alongside the three arms) and re-derive the 13 h from it.

### 8. Five works are cited in the text but absent from the reference list; one is misfiled — MAJOR
- **Lines** 153, 155, 152 vs 849–936.
- **Quoted.** L153: "Mata & Werner 2006, as described by Pinski & Neese 2019", "Russ & Crawford 2004", "Subotnik & Head-Gordon 2005". L155: "Reiher & Neugebauer 2003, read in full". L152: "Käser, Boittier, Upadhyay & Meuwly 2021". L854: "Cited in this proposal (verified by Crossref, arXiv or full text on 2–6 September 2026 unless marked otherwise". L933–934: "Other plan-04 sources carried in the working bibliography and used by the modules … Käser, Boittier, Upadhyay & Meuwly 2021".
- **What is wrong.** Mata & Werner 2006 is the bolded key prior-art find of the whole novelty table; Reiher & Neugebauer is marked "read in full"; none of the five appears in §14, so the verification statement of L854 does not cover them. Käser 2021 is cited in this proposal but filed under "other sources … used by the modules". Reverse check: every §14 entry is cited in the text (Joblin 1994 only at L809).
- **Fix.** Add the five entries with identifiers; move Käser into the cited list.

### 9. Line B's protocol details are asserted while the papers that define it are not held, and the protocol is attributed inconsistently — MAJOR
- **Lines** 526–528, 522, 324–325, 822–824, 899–906.
- **Quoted.** L526–528: "its authors' choices — the 200 cm⁻¹ resonance window, the exclusion of modes below 300 cm⁻¹ from the VPT2, the line profile — are not scored against". L522: "the protocol of Mackie et al. 2015, 2016 and Esposito et al. 2024". L324–325: "the PAHdb-anharmonic standard is B3LYP/N07D with a 200 × 974 integration grid, Esposito et al. 2024". L822–823: "the protocol of the 2024 papers (B3LYP/N07D, the 200 × 974 grid, SPECTRO with symmetry-based resonance polyads, a 200 cm⁻¹ window, modes below 300 cm⁻¹ excluded)". L901–902, 905–906: "Crossref record, 8 September; PDF asked of the supervisor."
- **What is wrong.** §7 states the window and the low-mode exclusion as facts of line B; §13 item 11 asks whether they are; §14 says the Mackie papers have not been read. The reader cannot tell which of these protocol elements was read (in Esposito 2024) and which is inferred. The attribution wanders between "Esposito 2024", "Mackie 2015, 2016 and Esposito 2024" and "the 2024 papers" (plural; one 2024 paper is cited). To the co-author of the 2015/2016 papers, crediting her protocol to a 2024 paper while asking her for her own PDFs reads as not having done the reading.
- **Fix.** One attribution sentence: which element comes from which paper, marked "read" or "to confirm"; drop the assertive form in L526–528 until the PDFs are read.

### 10. The summary reports the favourable frozen-space numbers and omits the least favourable one, the anchor-basis bias — MAJOR
- **Lines** 37–42 vs 243–248.
- **Quoted.** L38–41: "their energy scatters by 0.002–0.06 µE_h along a displaced mode, where the same local-CC program re-selecting its spaces at every geometry scatters by 7–11 µE_h at its default settings and 0.05–2.7 µE_h at tight ones." L244–246: "its composite curvature bias grows with the basis: +0.94, +0.06 and +1.58 cm⁻¹ on the three modes against +0.14, +0.03 and +0.36 at cc-pVDZ". L247–248: "The bias is a pure curvature term … and enters Δ₂ directly."
- **What is wrong.** A bias of up to 1.6 cm⁻¹ entering Δ₂ directly at the production basis, against a total expected effect of ~5 cm⁻¹, is the single most consequential measured number in the document and it is not in §1. §11 risk 1 is likewise not updated (see finding 12).
- **Fix.** Add one sentence to §1 with the cc-pVTZ bias and the 9-September re-measurement.

### 11. The bias-vs-overlap explanation does not follow from the three numbers given — MAJOR
- **Lines** 213–217, 244–247.
- **Quoted.** L245–247: "largest where the transported virtual space overlaps the freshly selected one least (smallest singular value 0.36 at the out-of-plane endpoint, 0.57 on the C–C stretch)". Bias by mode (order of L213–216: ring, C–C stretch, out-of-plane): "+0.94, +0.06 and +1.58 cm⁻¹".
- **What is wrong.** The C–C stretch has the second-lowest overlap (0.57) and the smallest bias (0.06); the ring mode has a higher overlap (not given) and a bias fifteen times larger. Two of three modes contradict the stated monotonic relation. If the ordering of the three biases is not the ordering of L213–216, the text does not say so.
- **Fix.** Give all three singular values beside all three biases, name the modes, and either drop the causal sentence or restrict it to the out-of-plane mode.

### 12. §11 risk 1 says the anchor-basis scan is running; §3.3 says it finished — MAJOR
- **Lines** 722–724 vs 241–243.
- **Quoted.** L723: "Remaining exposure: the anchor basis (scan running)". L242–243: "finished on 8 September".
- **Fix.** Update risk 1 with the cc-pVTZ result (smooth: 0.002–0.021 µE_h; bias grows to 1.58 cm⁻¹; tighter-threshold rerun ends 9 September).

### 13. The sealing of the M1 raw energies does not protect what it claims to protect, and "quotes only differences" is not true of §3.3 — MAJOR
- **Lines** 552–558, 535–550, 234–238, 246.
- **Quoted.** L552–553: "The first real coupled-cluster correction is computed after the note is committed, so no stopping constant, probe cap, tolerance or margin can be shaped by a result". L555–558: "the author has undertaken not to open them before the pilot note … and this proposal quotes only differences between methods." L235: "reloads its spaces from file exactly (to 10⁻⁴ µE_h)". L237–238: "(overlap between the two landings 0.67)". L246: "smallest singular value 0.36".
- **What is wrong.** The pilot note is written "with seven inputs in hand" (L536–537), input 4 being probe M1; the anchor-licence noise and bias tolerances will therefore be fixed after the author has read the M1 scatter (0.002–0.06 µE_h) and bias (0.03–1.58 cm⁻¹) printed in this very document. Sealing the raw energies while publishing their summary statistics adds nothing to pre-registration of the anchor gate; what the seal genuinely protects (the probing licence's off-diagonal responses) should be named. Separately, overlaps, singular values and reload precision are not "differences between methods".
- **Fix.** State what the pilot note may and may not use from M1 (e.g. "the noise and bias lines are fixed as multiples of the measured M1 values, the multiples chosen before M1 was read" — if that is the case, say so), and reword L556–558.

### 14. What K counts is inconsistent between §8, §5.1 and §3.2 — MAJOR
- **Lines** 599–603, 344, 192.
- **Quoted.** L599–601: "Of the 546 training energies the recovery reached its off-diagonal threshold at 448, of which the first 60 (the single-mode block) fix the diagonal: **K = 448 energies, K_off = 388 energies**". L598–599: "plus the 30 single-mode patterns at a second amplitude (60 energies)". L344: "(Each mode's diagonal costs four energies: a ± pair at each of two amplitudes, §3.4.)" L192: "48 modes × 4 diagonal energies".
- **What is wrong.** At benzene the diagonal cost inside K is 60 (one amplitude); the second-amplitude 60 sit outside the 546 and outside K. §5.1 and the naphthalene arithmetic charge four per mode. Either K = 508 at benzene or the naphthalene estimate over-counts by 96; the reported K, the plan's headline measurement, is ambiguous by ~13 %.
- **Fix.** Define once whether K includes the second-amplitude block and the held-out energies "computed as well", and use the same convention in L192 and L601.

### 15. Benzene's own symmetry-allowed coupling count is never given, and the cheapest test of the symmetry prior is neither reported nor planned — MAJOR
- **Lines** 180–185, 178–180, 601.
- **Quoted.** L182–183: "the benzene rehearsal needed 388 off-diagonal energies for 435 unknowns (§8), so sparsity as such saved nothing". L183–185: "with the symmetry prior naphthalene has **141** same-representation couplings instead of 1,128". L178–180: "enters the deck after the naphthalene rehearsal reproduces the direct surrogate correction with it; until that rehearsal has printed, the banded rule stands as the fallback."
- **What is wrong.** By the same D₆h bookkeeping the document applies to naphthalene, benzene's 30 modes (2a₁g + a₂g + a₂u + 2b₁u + 2b₂g + 2b₂u + e₁g + 3e₁u + 4e₂g + 2e₂u) leave about 14 independent same-representation couplings, not 435 — including exactly one in b₂u, the 1186/1357 pair the rehearsal found strongest. A DFT-only rerun of the benzene rehearsal under the prior costs a few laptop hours (the whole rehearsal was 2 h 30 min) and would test the prior today; the plan instead admits the prior only after an owed naphthalene rehearsal at ten times the cost.
- **Fix.** Print benzene's free-element count beside naphthalene's; rerun the benzene surrogate under the symmetry prior before the pilot note and report K_off against ~14.

### 16. "exact, not assumed" over-states what symmetry gives for a frozen-space local-correlation object — MAJOR (insider objection)
- **Lines** 174–177, 236–240.
- **Quoted.** L174–176: "couplings between modes of **different** irreducible representations are fixed at zero — exact, not assumed". L177: "This prior has no parameters, cannot distort the truth on a symmetric molecule". L236–238: "Two runs at the same displaced geometry landed the fresh localiser on different, symmetry-equivalent orbital sets (overlap between the two landings 0.67)".
- **What is wrong.** The zero is exact for the canonical correction. The measured object is LNO-CCSD(T) in fragment spaces built from localised orbitals that individually break the point group, truncated by per-fragment thresholds, then transported by projection; its energy surface is symmetric only to the extent those truncations are, and the document's own L236–238 shows the localiser is not deterministic under symmetry. Forbidden couplings in the frozen-space Δ₂ are therefore small-but-measurable, not identically zero — and imposing zero hides exactly the artefact the plan should be measuring.
- **Fix.** Keep the prior but add a null: fit a few symmetry-forbidden pairs free at benzene/naphthalene and report their magnitude as part of the anchor's smoothness record; reword L175–177 to "exact for the canonical surface; measured for the frozen-space one".

### 17. The reference against which the probing licence is judged at naphthalene is undefined and, if coupled-cluster, unaffordable by the document's own arithmetic — MAJOR
- **Lines** 336–338, 547–550, 613–614.
- **Quoted.** L336–338: "a **probing licence** at benzene and naphthalene against directly computed reference corrections (at benzene including a canonical coupled-cluster reference, the only one independent of the space freezing)". L549: "no canonical line existing at naphthalene". L613–614 (benzene): "the full canonical reference Hessian by energies (1 + 2·30 + 4·435 = 1,801 energies …) **does not** [fit]".
- **What is wrong.** A directly computed frozen-space LNO Hessian at naphthalene by the same recipe is 1 + 96 + 4·1,128 = 4,609 energies at ≥35 min each — thousands of hours. Either the naphthalene licence is against the DFT surrogate (then it is a rehearsal, not a coupled-cluster licence) or against a subset of directly computed blocks (then which); the text does not say, and the reader cannot tell what is promised at R1.
- **Fix.** State the naphthalene reference set explicitly (e.g. "the 141 allowed couplings computed directly as two-mode points: N energies, M hours").

### 18. The pipeline's DFT engine, production level and VPT2 implementation are unnamed, so the Δ₂ = 0 null row's meaning cannot be judged — MAJOR
- **Lines** 318–331, 345–347, 526–533.
- **Quoted.** L319–321: "**The production DFT level (functional, dispersion correction, basis set, integration grid) is a pre-registered constant that is not yet chosen**". L345–347: "(GVPT2; the implementation is pinned in the pilot note as a pre-registered constant, with named resonance thresholds and a polyad cap". L529–530: "the difference is separated from the coupled-cluster correction by the Δ₂ = 0 null row below, which runs this pipeline's own anharmonic step without the correction."
- **What is wrong.** Nowhere is the DFT program named (analytic dipole second derivatives on a laptop narrows it), nor the candidate VPT2 codes. If the production step is not B3LYP/N07D + SPECTRO, the null row differs from line B in functional, basis, grid, VPT2 code and resonance treatment at once, and its "separation" of anharmonic-treatment effects from the coupled-cluster correction holds only within the pipeline, not against line B. The document leans on the null row to make the comparison fair (L530–533) without saying what it will be.
- **Fix.** Name the engine and the candidate levels/codes now; say which choice makes the null row commensurate with line B and whether that is the default.

### 19. Module 06 "generative pattern proposer" appears once, undefined, and appears to conflict with the hashed deck — MAJOR
- **Lines** 765–768 vs 78–81.
- **Quoted.** L766–767: "the generative pattern proposer (Module 06) — are efficiency experiments on the off-diagonal probe count". L78–81: "The **deck** is the ordered list of displacement patterns for a molecule; it is **hashed**, meaning its order is fixed by a seeded function before any energy is computed, so nobody can reorder the patterns after seeing a result."
- **What is wrong.** A proposer that generates or orders patterns is, on its face, exactly the adaptive reordering the hash forbids. If it only proposes the deck before hashing on DFT-only corpora, say so; otherwise the pre-registration guarantee has a hole.
- **Fix.** Define Module 06 where Module 05 is defined (§6) and state its relation to the hash.

### 20. The R2 C–C "undecidable by construction" argument is not applied consistently with the coronene treatment, and the §13 ask is framed for a source that cannot exist — MAJOR
- **Lines** 401–412, 390–394, 784–789, 883–884.
- **Quoted.** L405–408: "The C–C stretching families at R2 are therefore expected to be undecidable by construction (they carry the largest temperature shifts and the smallest beat margins, so the unknown vapour temperature swamps them". L392–393: "the jet-cooled coronene bands at 7.7 and 8.8 µm lie 10–19 cm⁻¹ from where the hot spectra and the slopes put a cold band". L883–884 (Joblin 1994): "Gas-phase, solid and Ne-matrix PAH spectra 3–20 µm, the hot spectra of the coronene cross-check". L784–785: "Gas-phase or jet-cooled spectra of pyrene, chrysene and triphenylene **in the 6–15 µm region** at better than 8 cm⁻¹ resolution and known temperature".
- **What is wrong.** For coronene the plan combines a known-temperature hot gas-phase spectrum with the Joblin 1995 slopes to place a cold band; for pyrene the same source paper is in hand and the same slopes exist, yet the argument rests on the *unknown* temperature of NIST GC-IR only. Whether Joblin 1994 covers pyrene is not stated; the reader would expect the document to say. Separately, "room temperature" (L43, L403, L787) is not a meaningful qualifier for four- and five-ring PAHs, whose vapour pressure precludes cell absorption at 296 K; the useful ask is "known temperature", which L785 already contains, so L787 undercuts it.
- **Fix.** State which R2 species have known-temperature hot gas spectra in the sources already read, apply the coronene recipe to them or say why not, and drop "room temperature" from the R2 sentences.

### 21. The 3 µm jet-cooled column is promised as an "accuracy" family at R2 although the document itself doubts the fundamentals can be scored — MAJOR
- **Lines** 368, 382–383, 811–813.
- **Quoted.** L368: "accuracy (C–H families; C–C families expected undecidable on the existing gas data, see below)". L382–383: "for the C–H stretch family only, the jet-cooled 3 µm IR–UV ion-dip spectra of Maltseva et al. 2016 as a labelled cold column". L812–813: "whether the assigned features can be scored as fundamentals given the Fermi-resonance polyads in that region."
- **What is wrong.** The defining result of the jet-cooled 3 µm work is that the region is a manifold of resonance polyads in which "the fundamental" is not an isolable stick. A scoreboard of "stick positions per band family" against those spectra is ill-posed unless it scores the polyad pattern (or the intensity-weighted centroid) — and then it is no longer a test of the harmonic correction alone. The ladder table promises accuracy on "C–H families" at R2 as if the out-of-plane (hot GC-IR) and stretch (cold jet) families were equally decidable.
- **Fix.** In the R2 row, split "C–H out-of-plane (hot gas, decidable by margin)" from "C–H stretch (cold jet; scoring rule to be agreed with the source's authors, §13 item 8)" and do not count the latter as promised until the rule exists.

### 22. The side project's memory argument gives no relief at the rung where it is first tested — MAJOR
- **Lines** 432–437, 441–445, 615–617.
- **Quoted.** L436–437: "the fragment structure of the local method should let the memory of reverse-mode differentiation scale with the largest fragment rather than the molecule." L441: "**M2** (benzene, cc-pVTZ; laptop)". L616: "at cc-pVTZ it did not complete within the 22 GB ceiling".
- **What is wrong.** At benzene every LNO fragment spans essentially the whole molecule, so "the largest fragment" is the molecule and reverse-mode AD of a CCSD(T) in that space stores more, not less, than the analytic canonical gradient that already exceeded 22 GB at cc-pVTZ. M2 as specified (benzene, cc-pVTZ, laptop) is therefore the least favourable place to test the memory claim, and its failure would trigger the kill criterion for a reason unrelated to the idea's merit.
- **Fix.** Either run M2 at cc-pVDZ (where the canonical gradient fitted: 13.9 GB) with cc-pVTZ as M3's first item, or state the expected M2 peak memory and the rule for classifying a memory-only failure.

### 23. "no production code offers an analytic nuclear gradient for local CCSD(T)" is asserted while the check that would establish it is listed as owed — MAJOR
- **Lines** 427–428 vs 544–546.
- **Quoted.** L427–428: "The domain review's reading of the software landscape stands: no production code offers an analytic nuclear gradient for local CCSD(T)". L544–546: "a run/no-run check of which local-CC codes produce an analytic gradient at the anchor level at the equilibrium geometry, with memory — owed".
- **Fix.** "believed (review of 4 September); the run/no-run check of §7 item 6 confirms or refutes it before the pilot note."

### 24. The R2 canonical diagonal check at pyrene carries no arithmetic, against the plan's own rule — MAJOR
- **Lines** 368, 588, 617.
- **Quoted.** L368: "a canonical diagonal check at pyrene (expected cluster work; classified by the rule of §8, and skipped with a printed sentence if no cluster time exists)". L588: "Every cost in the plan is a measured slot reading 'not run' until a script prints it." L617: "its memory scales roughly with the fourth power of the basis size".
- **What is wrong.** By the document's own scaling logic a canonical CCSD(T)/cc-pVTZ point of pyrene (roughly 620 basis functions against benzene's 264) is two to three orders of magnitude beyond the 755-s benzene point, and a diagonal line needs 2 × 72 + 1 of them. "Expected cluster work" is an adjective where the plan promises numbers.
- **Fix.** Give the scaled estimate (energies × time × memory) in the row or remove the item until a timed probe on the actual machine exists.

### 25. No calendar: the document has no dates for the pilot note, R0–R3, the module deadlines or the end of the project — MAJOR
- **Lines** 453–454, 637, 771–772.
- **Quoted.** L453–454: "if M3 is not reached within twelve calendar weeks of the pilot note's commit date". L637: "Human hours are logged and not capped." L771–772: "Module deadlines are administrative facts; a module may ship a fail-closed state to meet its date".
- **What is wrong.** Every deadline is relative to an undated event. A supervisor signing a capstone proposal needs to see when the pilot note is expected, when R0 and R1 print, when the cluster request must be made, and what is delivered if the programme ends after R1. The 200–250 h naphthalene estimate (finding 6) makes this urgent.
- **Fix.** One dated table: pilot note; R0; R1; R2 classification; cluster request; R3; write-up; the module dates.

### 26. The supervisor's conflict of interest with line B and with the R2 cold column is not named — MAJOR
- **Lines** 522, 383, 828–830, 899–909.
- **Quoted.** L828–830: "Whether the comparison of §7 … is, in her judgment, the fair way to put a coupled-cluster harmonic correction next to her method". L522: "the **PAHdb Anharmonic library v1.00** … the protocol of Mackie et al. 2015, 2016". L383: "the jet-cooled 3 µm IR–UV ion-dip spectra of Maltseva et al. 2016".
- **What is wrong.** The supervisor is an author of opponent line B and of an R2 scoring source, and is asked to rule on the fairness of the comparison against "her method". The design already contains the protections (frozen version, pre-registered margins, Δ₂ = 0 null row, leakage rules) but they are never tied to the conflict, and a reviewer of the finished capstone will ask.
- **Fix.** One sentence in §7 or §13: name the overlap and state that the frozen version and pre-registration are the mitigation, and that the supervisor's role on line B is advisory on protocol facts, not on margins.

### 27. "inconclusive by measurement" for the jet-cooled coronene 7.7 and 8.8 µm families demotes the cold data in favour of a hot extrapolation — MAJOR (insider objection)
- **Lines** 392–394, 384–385, 743.
- **Quoted.** L392–394: "the jet-cooled coronene bands at 7.7 and 8.8 µm lie 10–19 cm⁻¹ from where the hot spectra and the slopes put a cold band, so those two cold families are inconclusive by measurement, not by expectation." L743: "the cold jet-cooled lists for tetracene and coronene are scored as labelled columns."
- **What is wrong.** A pipeline that predicts a 0 K band has, in a jet-cooled band, the most direct laboratory truth that exists; the disagreement with a linear extrapolation of hot-band slopes over several hundred kelvin says more about the extrapolation than about the jet. Treating the two as equal witnesses and declaring the family inconclusive throws away the best data at R3. (Item 7 of §13 asks the right question; the rule in §5.2 does not wait for the answer.)
- **Fix.** Score against the jet-cooled band as the primary cold column with the FEL bandwidth as its uncertainty; report the hot-extrapolated position as a second column; mark the family inconclusive only if the two columns give opposite verdicts.

### 28. Terms and labels used before or without definition — MAJOR (by the rubric; low weight)
- **Lines** 330, 241, 255, 150, 154.
- **Quoted.** L330: "the Module-05 corpus uses B3LYP" (Module 05 first defined L468–472). L241: "the basis the licence rungs use" (never defined; R0–R1?). L255: "(research note P10, decision 20)" (P10 external, decision 20 absent). L150: "MP2/haTZ modes". L154: "Ethereal AI (Bos et al. 2025)".
- **Fix.** Define "licence rungs" in the Terms list; move the Module 05 gloss forward or add it to Terms; expand haTZ; explain or drop "Ethereal AI".

### 29. §10's heading dates conflict with item 16 and with §9's description of items 8–19 — MAJOR
- **Lines** 698, 710–711, 669–671.
- **Quoted.** L698: "**5–6 September 2026, after the first measurements.**" L710: "The cc-pVTZ frozen-space scan with its canonical truth line ran (6–8 September; result in §3.3)". L669–670: "Items 8–16 and 19 were made on the DFT-only rehearsal, the frozen-space probe and the timings".
- **Fix.** Split item 16 (and 20, 21) under an 8-September heading.

### 30. "Three measurements and one literature search" undercounts the searches — MINOR
- **Line** 34. **Quoted.** "Three measurements and one literature search have been made since the plan was written". The document describes a 5-September source search (L401), a 6-September novelty search (L144) and an 8-September find (L153). **Fix.** "two literature searches, and a third finding on 8 September".

### 31. "a few weeks" for 200–250 hours — MINOR
- **Line** 194. **Quoted.** "i.e. 200–250 hours — a few weeks of unattended laptop time". 200–250 h is 8–10 days at one job at a time. **Fix.** "eight to ten days, longer at naphthalene's per-energy time".

### 32. Modes are identified by frequency only; the insider wants the irreps — MINOR
- **Lines** 169–171, 213–217. **Quoted.** "the strongest pair at 1186 and 1357 cm⁻¹"; "a non-degenerate C–C stretch at 1357 cm⁻¹, which belongs to the same irreducible representation as the 1186 cm⁻¹ mode". These are the b₂u Kekulé stretch and b₂u C–H bend — the pair every DFT benchmark of benzene struggles with; saying so would make the rehearsal's headline result immediately recognisable. **Fix.** Add the symmetry labels (a₁g, b₂u, e₁g) to L213–216 and L169.

### 33. "at least two energies per vibrational mode" vs "four energies" per mode — MINOR
- **Lines** 305–306 vs 344. **Quoted.** "costs at least two energies per vibrational mode — 2,580 coupled-cluster energies"; "(Each mode's diagonal costs four energies". Consistent only because of "at least"; under the plan's own protocol the number is 5,160. **Fix.** Use the protocol's number.

### 34. "seventeen of eighteen held" — the eighteen is not derivable from the text — MINOR
- **Line** 657. **Quoted.** "(seventeen of eighteen held; the exception was re-patched and re-read in the fourth round; then twelve of twelve)". §9 names six, four and two items (twelve). **Fix.** Say what the eighteen were.

### 35. Reference list order and form — MINOR
- **Lines** 878, 897–899. "Olive Dornshuld" is filed between Fusè and Joblin; "Mai" precedes "Mackie". Initials appear for some entries only (explained at L855, but the explanation makes the list look half-verified). **Fix.** Alphabetise; either initials everywhere or nowhere.

### 36. "her" in §13 while the rest of the document says "the supervisor" — MINOR
- **Lines** 829, 831, 833, 844. **Quoted.** "in her judgment", "which DFT level she would regard", "in her group's work", "one she would sign". **Fix.** "the supervisor's".

### 37. "the 2024 papers" (plural) — MINOR
- **Line** 822. **Quoted.** "computed with the protocol of the 2024 papers". One 2024 paper is cited (Esposito et al.). See also finding 9. **Fix.** Name the paper(s).

### 38. Mean absolute difference conflated with a mean — MINOR
- **Lines** 735–739. **Quoted.** "The opponents' fitted scale factors already absorb the mean of a harmonic difference that Esposito et al. 2024 (§14) measured for benzene: … mean absolute difference 5.45 cm⁻¹". A scale factor absorbs the signed mean (multiplicative); a MAD says nothing about how much of it is absorbable. **Fix.** "absorb the signed mean of that difference; the MAD of 5.45 cm⁻¹ bounds what remains to buy per family".

### 39. The coronene hot spectra are unsourced where they are used — MINOR
- **Lines** 392, 809, 883–885. In §5.2 "the hot spectra" has no citation; Joblin et al. 1994 is identified only in §13 item 7 and in §14, and is not in the "read in full" list of L385 though its entry says "read in full 2026-09-06". **Fix.** Cite Joblin 1994 at L392 and add it to the per-rung source list.

### 40. "Every number … was printed by a script" vs the arithmetic estimates — MINOR
- **Lines** 5–6, 193–195, 612–614, 617. **Quoted.** L5–6: "Every number in it that describes this project's own performance was printed by a script in the folder `probes/` and can be re-run". The 200–250 h, 13 h, 378 h and "hundreds of GB" are arithmetic, not printouts. **Fix.** "printed by a script or derived by arithmetic shown in place".

### 41. Where the first-order geometry term's force comes from is not stated — MINOR
- **Lines** 351–353, 659–660. Paired displacements cancel the CC force in Δ₂ (L659–660); the geometry term needs it. It is available as the odd part of the single-mode ± pairs; say so.

### 42. The two-word quotation from Ricca et al. 2026 — MINOR
- **Lines** 15–16. **Quoted.** "whose systematic uncertainties its own current paper calls 'currently unquantified'". Give the sentence, or paraphrase; a two-word quote invites the accusation of quoting out of context against the opponent's own paper.

### 43. M1-μ status not updated — MINOR
- **Lines** 512–514. **Quoted.** "owed after the cc-pVTZ scan". The scan finished on 8 September (L242); state whether M1-μ has started or when it will.

---

## (a) How the opponents and the laboratory sources read to an insider

**PAHdb and the Anharmonic library (lines A and B).** The document is, in outline, accurate and respectful: it names the level (B3LYP/N07D), the code (SPECTRO), the resonance treatment (symmetry-based polyads), freezes a version, restricts the comparison to stick positions per family, and — the fairest device in the plan — insists on a Δ₂ = 0 null row so that a win cannot be claimed for the coupled-cluster correction when it belongs to the pipeline's own anharmonic step (L526–533, L560–563). It also says, correctly, that the pipeline leaves the anharmonic constants at DFT level "as they do" (L154). Three things grate. First, the protocol is credited to "Esposito et al. 2024" or "the 2024 papers" in three places (L324, L822, L835) and to Mackie 2015/2016 in one, while §14 admits the Mackie PDFs have not been read and asks the supervisor for them; the protocol details then asserted in §7 (200 cm⁻¹ window, <300 cm⁻¹ exclusion) are therefore inferred, not read (finding 9). Second, the vocabulary — "opponents", "beat", "losing", "win" — is defined (L69, L517) but is applied to the supervisor's own work throughout, and the conflict of interest that creates is never written down (finding 26). Third, there is no expected-effect line for line B at all: the only literature figure (5.45 cm⁻¹, L738) is a harmonic difference against line A's level; how far the anharmonic library already sits from the jet-cooled and gas-phase data — the numbers in the 2015/2016 papers themselves — is not quoted, so the reader cannot see what margin the plan expects to have over line B. Nothing is condescending; the omission of the library's own measured accuracy is the inflation by absence.

**The jet-cooled data.** Maltseva 2016 is correctly described as 3 µm IR–UV ion-dip spectroscopy, but is held at "abstract grade" (L909) while being adopted as a scoring column and declared "read in full" (finding 2), and the plan promises "accuracy (C–H families)" at R2 on it (finding 21) although its own item 8 concedes the Fermi-resonance problem. Lemmens 2019/2021 are handled well: the FEL bandwidth is asked for, the "0.5–1 %" figure is right, and the tetracene list is scored as a cold column. The treatment of the coronene 7.7/8.8 µm bands is where an insider objects: the jet-cooled band is the closest thing to the pipeline's own 0 K observable, and the plan lets a 10–19 cm⁻¹ disagreement with a hot-band extrapolation render the families "inconclusive by measurement" (finding 27). The plan should trust the jet.

**NIST and PNNL.** These are treated carefully and accurately: 296 K, 0.12 cm⁻¹, the uncertified water/CO/CO₂ windows and the consequent exclusion of the 1480 cm⁻¹ band; the PNNL 25/50 °C discrepancy noticed and deferred to the record header. The hot NIST GC-IR spectra are correctly labelled as temperature-unknown. The only gap is the R2 asymmetry with coronene: a known-temperature hot gas source is used for coronene and not for pyrene (finding 20).

**Missing.** Matrix-isolation sources are named only in the "other" list (L934: Hudgins & Sandford 1998; Mattioda et al. 2020) though matrix scoreboards gate R2–R3; the matrix–gas shift term of the error budget (L360) has no stated source or magnitude; and the actual list of scored bands per family — which bands, at which wavelengths — appears nowhere, so "family" remains a category rather than a list.

## (b) The questions in §13

Items 1–6 are well posed and answerable in a meeting; item 5 is properly conditional. Of the 8-September list: item 7 (FEL bandwidth per measurement; the coronene 7.7/8.8 µm discrepancy) is squarely hers and answerable. Item 8 (Maltseva 2016 tables and bandwidth; whether fundamentals are scorable in the 3 µm polyads) is answerable and is the question that decides finding 21 — it should be asked before, not after, R2's C–H stretch family is promised. Item 9 (Pirali's Q-head offset) is not her paper; she may know. Item 10 (PNNL temperature) she cannot know; the "asked only if" clause is correct. Items 11 and 12 (whether all 45 v1.00 spectra follow one protocol; downloadable stick lists; line profile) are questions for the library's curators at Ames as much as for her, and item 11 misattributes the protocol to "the 2024 papers"; she will answer for 2015/2016 and redirect the rest. Item 13 is fair and important, but it is the conflict-of-interest question without the label (finding 26). Item 14 is answerable. Item 15 presumes a protocol fact (the <300 cm⁻¹ exclusion) that finding 9 shows is not yet established; ask "does the protocol exclude low modes, and if so how" rather than "whether excluding … drops their couplings". Items 16–17 are fine.

Missing, given the rest of the document: (i) which reference level counts as the truth for the harmonic correction — CCSD(T)/cc-pVTZ, its CBS extrapolation, or F12 — and whether she accepts a cc-pVTZ anchor with the basis-set error unbudgeted (finding 4); (ii) the calendar — when the pilot note, R0 and R1 are expected and what is delivered if the programme ends at R1 (finding 25); (iii) whether she agrees that the jet-cooled coronene bands should be the primary cold truth (finding 27); (iv) her view of the matrix–gas shift term and its sources; (v) the enumerated band list per family she would regard as the fair scoreboard; (vi) whether "opponent" is acceptable language for line B in the written thesis.

## (c) Verdict

She could not sign this text as it stands, but the reasons are almost all fixable in a day and none of them is the science: the document is unusually honest about what is measured, asserted and promised, its null tests are the right ones, and the frozen-space measurement is the correct first experiment. What blocks a signature is that the document contradicts itself about when it was written and cold-read, says her paper was read in full when the reference list says it was not, invokes two decisions that do not exist, computes a naphthalene cost that its own rule classifies as cluster work while calling the route guaranteed on the laptop, and — the one substantive scientific gap — budgets every error of the anchor except the basis-set error of the anchor itself, against an expected effect of the same size taken from an F12 reference. The first change she would ask for is that one: put the anchor's distance from the basis-set limit into the anchor licence and the per-band budget (a 61-energy cc-pVQZ or F12 diagonal line at benzene, sized exactly like the bias line already planned), and restate the expected-effect line at the anchor's own level. The second is a single dated page: pilot note, R0, R1, cluster request, R3, module dates. With those, and the provenance corrections of findings 1–3, this is a proposal she would put her name to.

---

**Counts.** BLOCKING 7 (findings 1–7) · MAJOR 22 (findings 8–29) · MINOR 14 (findings 30–43).


---

## Closures — 2026-09-10

Applied to `Project_Proposal_2026-09-06.md` by two patch scripts (scratchpad, `patch_coldread_proposal*.py`); every
change is in the proposal's running text, which is still editable until the supervisor has read it.

| # | closure |
|---|---|
| 1 | header now dates the revisions (6 → 10 September) and names both cold reads; §9 sentence corrected |
| 2 | "read in full" restricted to the nine sources that were; Maltseva at abstract grade, asked for in §13 item 8 |
| 3 | §10 gained the block "8–10 September" with decisions 20–26 and 28 (27 reserved for the parked P19); §9 "items 8–28" |
| 4 | P12 / decision 26: basis-set line in the anchor licence and the per-band budget with the measured DZ→TZ figures; expected-effect line declared an upper bound; **inputs (ii) and (iii) pending** |
| 5 | cubic-constants sentence restated: this probe set cannot produce φ_ijk; three-mode displacements at CC cost could |
| 6 | naphthalene energy-route arithmetic corrected to K = 2M + K_off (250–300 energies, 150–180 h at benzene's per-energy time, six to eight days); the per-energy time at naphthalene is being measured (P13); **rewritten when it prints** |
| 7 | 755 s labelled as the idle equilibrium point; displaced points 850–1,270 s; truth line 13–21 h |
| 8 | references added: Käser 2021, Mata & Werner 2006, Pinski & Neese 2018/2019, Reiher & Neugebauer 2003, Russ & Crawford 2004, Subotnik & Head-Gordon 2005 (reading status and identifier provenance stated per entry); Brumfield 2012 updated to read-in-full |
| 9 | line-B protocol attributed to the two 2024 papers held and read; library-wide applicability asked in §13 item 11 |
| 10 | summary now states the cc-pVTZ frequency bias as the least favourable number |
| 11 | overlap sentence gives the three s_min values and says the bias is not monotonic in them |
| 12 | risk 1 carries the measured anchor-basis result and the rerun |
| 13 | sealing paragraph says what the hash protects and why quoting M1 summary statistics shapes nothing |
| 14 | K defined once (2M + K_off), diagonal cost sentences aligned (33 likewise) |
| 15 | benzene: 57 same-irrep pairs, K_off 210 vs 388 (run of 10 September, decision 22) |
| 16 | "exact for the canonical surface, measured for the frozen-space object" (decision 23, with the surrogate null ≤ 2 µE_h) |
| 17 | naphthalene probing-licence reference = the full deck, every same-irrep pair measured directly |
| 18 | engines named (psi4 1.11, pyscf-forge LNO-CCSD(T) in PySCF 2.14; VPT2 a pilot-note constant); null-row commensurability tied to §13 item 13 |
| 19 | Module 06 defined in Terms and stated to propose before hashing |
| 20 | R2 sentences: "known temperature" instead of "room temperature"; pyrene's hot heat-pipe spectrum (Joblin 1994/1995) named with the coronene recipe |
| 21 | decision 25 (already applied 2026-09-08) |
| 22 | M2 at cc-pVDZ first; cc-pVTZ repeat opens M3; memory-only failure recorded, not killing — **side-project rule changed without a user decision; flagged** |
| 23 | left as written: the gradient-availability claim is a literature statement with its sources in the bibliography; the check named by the finding (a run) is the side project's M2 |
| 24 | pyrene canonical diagonal: scaled arithmetic in the row (≈ 80 h and ≈ 220 GB per energy, 145 energies) |
| 25 | calendar in §12 (2026-09-09) |
| 26 | conflict-of-interest paragraph in §7 |
| 27 | decision 24 (already applied 2026-09-08) |
| 28 | Terms: licence rungs, Module 05/06; haTZ and Ethereal AI expanded |
| 29 | §10 heading "5–8 September"; §9 "5–10 September" |
| 30 | "two literature searches, with a third literature finding" |
| 31 | "six to eight days" |
| 32 | irreps given for the two naphthalene modes named (both b₂u) |
| 33 | 5,160 energies for the 432-atom molecule under the protocol |
| 34 | the "seventeen of eighteen" sentence replaced by a pointer to the review files |
| 35 | new entries inserted alphabetically; the list's form otherwise left |
| 36 | "the supervisor" throughout §13 |
| 37 | "the two 2024 papers" with identifiers |
| 38 | signed mean vs mean absolute difference separated |
| 39 | coronene hot column sourced (Joblin 1994/1995) in the source list |
| 40 | "or is arithmetic shown in place on such numbers" |
| 41 | geometry-term force = odd part of the single-mode ± pairs |
| 42 | Ricca quotation paraphrased |
| 43 | M1-μ scheduled after the R1 timings, before the pilot note |

Finding 23 is the only one closed without a text change; findings 4 and 6 remain half-open on measurements, not on wording.
