# PI assessment 2026-09-19 — at which moments, past, present and future, a scientific article from this project is permitted and justified; what the authors we cite would want to learn from us (written at the user's request, 19 September 2026, morning; desk work only — the anchor run was not touched)

*Two words are kept apart throughout. A paper is **permitted** when it makes a claim that is new against the literature it cites, rests on evidence a reader could reproduce from the released runs, and carries its negative results and error bars. It is **justified** when at least one identifiable group would act differently after reading it. The first is a matter of honesty; the second of relevance. Both are required.*

## 1. The literature we cite, grouped by what its authors are trying to do

| line | papers (from §14 of the reading copy) | quality and state of the question | what they would want from us |
|---|---|---|---|
| **L1 — smooth local-correlation surfaces** | Russ & Crawford 2004; Subotnik & Head-Gordon 2005; Mata & Werner 2006; Pinski & Neese 2018/2019; Madriaga & Crawford 2025; Zhang et al. 2024 (PySCFAD) | Method papers of the first rank; the problem (discontinuities of PNO/domain surfaces in finite-difference properties) is *still open in 2025* — Madriaga & Crawford's paper is a statement of it. **Three of the six are unread here (closed access).** | A measured answer: by how much do correlation spaces built once and *transported* (projection + Löwdin) reduce the finite-difference noise of local CCSD(T) curvatures at PAH size; the recipe; the diagnostics (s_min, pre-Löwdin off-diagonals); the size of the projection term; the price of *not* freezing (M2b: the re-fragmenting engine halves a C–C response at its defaults). |
| **L2 — few-measurement Hessians** | Lahm et al. 2022, Kitzmiller et al. 2024, Olive Dornshuld et al. 2026 (CMA); Sanders et al. 2015; Wang et al. 2025 (O1NumHess) | Solid, active; CMA is the direct ancestor of the diagonal part. Their own outlier (a same-representation ring coupling) is our problem statement. | Whether the *difference* Hessian's off-diagonal block can be recovered at all from energies (our answer: not at naphthalene — an identifiability limit, 1,128 unknowns against 493 rows, confirmed by the amplitude test) and how it can from gradients (2k+1, exact, noise damped, count linear in size); which band families need the couplings (shape test: fingerprint yes, C–H stretch no). |
| **L3 — Δ-machine learning** | Käser et al. 2021; Qu et al. 2021; Bowman et al. 2022; Lam et al. 2020 | Strong; all per-molecule surfaces at ≤ 15 atoms; none crosses molecules on harmonic constants. | Cross-molecule learning curves of a CC correction per band family; the label economy (19 gradients per molecule against their 430–2,151 energies); the licence/refusal mechanism as a reporting standard. |
| **L4 — PAH spectra from theory** | Ricca et al. 2026 (PAHdb v4); Mackie et al. 2015, 2016; Esposito et al. 2024 (×2); Mulas et al. 2018; Bos et al. 2025; Mai et al. 2025; line D 2026 (He, Tang, Liu) | The application field; large, careful, DFT-bound; the systematic uncertainty of the scaled-harmonic part is *not reported* (Ricca 2026), and line D reproduces DFT with its errors. The supervisor co-authors two of these. | The per-family systematic error of B3LYP harmonics against CC, as a function of size; whether it drifts along the acene ladder; a licensed correction they can apply to a database; and the finding that the 6–9 µm bands *mix* under the correction (identity 0.83, shifts to 21 cm⁻¹), which touches assignments. |
| **L5 — the experiments** | Pirali 2009; Maltseva 2016; Lemmens 2019, 2021; Brumfield 2012; Joblin 1994, 1995; NIST/PNNL/Schneider | The scoring columns; resolutions 0.1–17 cm⁻¹ depending on the source. | Predictions with error bars for bands they measured, and an honest statement of which reference resolution a claimed accuracy is measured against (the 0.5 cm⁻¹ finding of 17 September). |

## 2. Past — was a paper ever permitted before today?

No. Every measured result to 19 September is on benzene and naphthalene at cc-pVDZ, or on DFT stand-ins. The results with publishable weight are:

- the **smoothness measurement** (M1, the I-series): transported frozen spaces scatter by 0.002–0.06 µE_h along a mode where the same program re-selecting its spaces scatters by 7–11 µE_h — a direct, quantitative answer to L1's open question, but at DZ only, and without having read three of the six papers that own the question;
- the **negative results**: P25's ranking lost its licence at naphthalene (X16); energies-only off-diagonal recovery closed by identifiability (stage C, amplitude test); the borrowed gradient engine does not compute our quantity (M2b). These are valuable as sections, not as papers.

A registered-report-style protocol paper (the pre-registrations exist and are dated) would have been permitted at any time since 13 September, but not justified: no group changes its practice on a protocol without a result.

## 3. Present — 19 September

Not yet, by one measurement and three readings. The nearest paper is L1's (§4, gate A). It needs the cc-pVTZ anchor result (24 September) to show the smoothness holds in the basis the community uses, and it needs Mata & Werner 2006, Russ & Crawford 2004 and Subotnik & Head-Gordon 2005 read in full before any sentence with "new" in it. A PI does not submit against papers the group has not read. Both conditions are calendar items, not obstacles.

## 4. Future — four gates, each with its condition

**Gate A — a communication on transported frozen spaces (L1). October 2026.** Claim: correlation spaces built once and transported by projection make local-CCSD(T) finite-difference force constants smooth to the 10⁻⁸ E_h level at benzene and naphthalene in cc-pVDZ and cc-pVTZ; the projection term is measured (M2's T-M2-3); the re-fragmenting alternative is threshold-sensitive by a factor two on a C–C response. Permitted when: the TZ cells are in (24 Sep) and hold; the three closed papers are read; M2's projection term exists (it needs M2's pieces A–B only, not the full build). Justified because Madriaga & Crawford 2025 asks precisely this and Pinski & Neese 2019 name the remedy without the PAH-size measurement. Venue: J. Chem. Phys. Communication or JCTC Letter. Authors: the student, the supervisor; the developers of the local code acknowledged and asked. Risk: Mata & Werner 2006 may already contain the measurement at small size — then the paper is the size scaling and the transport recipe, or it is a section of gate B.

**Gate B — a methods paper on the difference Hessian from gradient patterns (L2). First quarter 2027.** Claim: the off-diagonal block of the CC−DFT force-constant difference is unrecoverable from energies at naphthalene size (identifiability, amplitude-invariant residual) and exactly recoverable from 2k+1 gradients along symmetry-chosen patterns, k growing linearly where the couplings grow quadratically; noise damped (0.27 amplification); which band families need it (shape test). Permitted when: M2 is done by its pre-registration (T-M2-1..3), the first gradient decks at benzene and naphthalene are licensed against directly computed references on the *real* correction (today's counting is on DFT stand-ins), and X22 has answered whether the linear count survives without D2h symmetry. Justified because the CMA authors' outlier and O1NumHess's plateau are this problem, and because the negative result saves others the energies route. Venue: JCTC.

**Gate C — the main paper: the label factory and the licensed network (L3, L4, L5). Mid to late 2027.** Claim: a per-family coupled-cluster correction to DFT harmonics learned across PAHs, licensed or refused per family against cold gas-phase spectra, with the learning curves, the label count and the systematic error of scaled harmonics per family and size. Permitted when: 20–50 labelled molecules exist (desk note of 18 September, §4), the per-family curves cross or fail to cross the margins, and the comparison to line D and PAHdb is done on the same held-out molecules. Justified because L4 does not report the systematic uncertainty and L3 has never crossed molecules. With the supervisor as co-author; venue by emphasis (A&A / ApJ for the application, JCP for the method). A registered report is the honest form for this one: the licences are pre-stated.

**Gate D — a data paper: the labels themselves. As soon as ~10 molecules carry error bars, in parallel with B.** The CC−DFT per-mode corrections with their noise, the transported-space diagnostics, and the decks, released in the format of Hessian QM9 (Williams et al. 2025). Permitted at ten molecules because the object is the data, not a claim; justified because line D's own abstracts say their predictors weaken at large size for lack of training data — CC labels are what they lack. Venue: Scientific Data or a JCTC data article.

## 5. Conditions the PI imposes on every one of them

1. Every number traces to a run log in the released repository (already the rule); the pre-registrations are cited with their outcomes, wins and losses alike.
2. No claim of novelty against a paper not read in full. Today that blocks three (L1) and two (Mackie 2015, 2016 — PDFs asked of the supervisor).
3. The negative results are in the body, not the supplement: the energies route, P25, the borrowed engine, the tolerance finding.
4. Code, decks and transported-space diagnostics released with the paper; the (T) port (decision 41) under the licence of the code it extends.
5. The supervisor's co-authorship on L4 comparisons is stated in the paper; the comparison is run by the pre-registered protocol, not by choice of molecule.
6. No paper before its gate. A blog is not a paper: the lab notebook may say today what a paper may say only after the gate.

## 6. What the cited authors would want to know from us *now*, before any paper

- **L1:** the benzene/naphthalene smoothness numbers and the transport recipe — they could test it in their own codes this month.
- **L2:** that energies cannot recover the off-diagonal difference block at 18 atoms, and why; the 2k+1 count.
- **L3:** the label economy and the licence idea.
- **L4:** that the 6–9 µm bands mix under the correction, and that the "0.5 cm⁻¹" many of us quote is one reference's uncertainty.
- **L5:** which of their bands we intend to score, named before we print numbers.

All of this is in the public lab notebook already, dated. That is the right place for it until the gates open.

## Dated addition, 22 September 2026, 18:2x — gate E prerequisite (2) scheduled

The hypothesis for Mackie et al. 2021's "cause not known" went to the supervisor today (`notes/Email_Draft_2026-09-22_Mackie2021_Hypothesis.md`). Prerequisite (2) — the two-route diagnostic on naphthalene and a four-ring PAH at their level — is scheduled on hel1-14 (route 2 in the to-do; smoke test: SCF 37 s, one analytic Hessian 28.3 min at 16 threads with 18.1 GB peak (342 basis functions); 97 Hessians ≈ 46 h for one step size on hel1-14, 91 h for two — on a CCX53 roughly half; the lowest harmonic frequencies 179 / 189 cm⁻¹ as expected for the out-of-plane modes). The paper question stays open until it reports; a reply from the supervisor with Hessians of a failed case would replace the four-ring reproduction.

## Dated addition, 20 September 2026, 19:4x — the three L1 papers and Mackie 2015/2016 are read; gate A's claim is reworded

The prerequisite 'read in full before any sentence of novelty' is met for items 67, 68, 69 and 12 (`notes/Reading_Note_2026-09-20_Supervisor_PDFs_L1_Smoothness_and_Mackie.md`). Gate A's claim as written on 19 September — 'correlation spaces built once and transported by projection make local-CCSD(T) finite-difference force constants smooth' — overstates the novelty: Mata & Werner 2006 §II state that freezing domains at the reference structure for numerical gradients and Hessians is the standard remedy, in Molpro practice before 2006. **Reworded claim:** LNO-type correlation spaces (localised occupied orbitals and pair-density-defined natural-orbital virtual subspaces) have no atom-list domain that can be frozen; we transport them to displaced geometries by projection, semicanonicalise them, measure the projection term and the reload error (0.0002 µE_h round trip; fresh vs transported PM match 1.000), and show at benzene and naphthalene in cc-pVDZ and cc-pVTZ that the finite-difference force constants from transported spaces are smooth at the 10⁻⁸ E_h level, with the even/odd diagnostic as the chemist's smoothness test (Subotnik & Head-Gordon's criterion). Prior art to cite in the first paragraph: Russ & Crawford 2004 (the problem), Subotnik & Head-Gordon 2005 (bump functions), Mata & Werner 2006 (fixed and merged PAO domains), Pinski & Neese 2018/2019 (PNO relaxation terms), ORCA's fixed domains for DLPNO-MP2. Gate A's date (October 2026) and its remaining prerequisite (the TZ anchor, REPORT.md ≈ 25 September) are unchanged. Gate C/D gain a motivation sentence from Mackie 2016 §VI (family-wide generalisation of anharmonic effects without a QFF per molecule) and line B's numbers from the source.

## Dated addition, 21 September 2026 — a candidate gate E: a methods note on finite-difference noise in quartic force constants

**What was measured (20–21 September, benzene, B3LYP/6-31G*, psi4 1.10.2 + pyVPT2 0.1.2 on hel1-14):** the semi-diagonal quartic constants derived by second finite differences of psi4 Hessians disagree between their two independent routes by a median of 22 cm⁻¹ and up to 1,265 cm⁻¹; the package's own check cannot see it; the resulting VPT2 fundamentals are unusable (−217 cm⁻¹ on the ring breathing mode). psi4 has no analytic B3LYP Hessian, so the input Hessians are finite differences of gradients; the default step of 0.05 in reduced coordinates is far too small for that input. The two-route statistic (`probes/qff_from_hessians.py`) is a general diagnostic that any QFF code can print.

**What it does and does not say about Mackie et al. 2021's 'cause unknown':** their instabilities (anharmonic corrections of hundreds of cm⁻¹ in out-of-plane bends of larger PAHs) arose in Gaussian with analytic Hessians, so our exact mechanism (finite differences of finite differences) is not theirs. What we can say is weaker and testable: numerical noise in the semi-diagonal quartic constants, amplified by small steps and by small denominators of low-frequency out-of-plane modes, produces exactly that symptom, and a two-route or symmetry-partner check exposes it where the usual checks are silent. We have not discovered their cause; we have a hypothesis with a diagnostic.

**Gate E (candidate, not scheduled): a short methods note** — 'Two-route consistency of finite-difference quartic force constants: a diagnostic, with PAH examples'. Prerequisites before it is justified: (1) **done 21 September evening, as predicted** — the step-size test (0.05 → 0.20 with psi4 FD Hessians: route disagreement median 22.4 → 2.3 cm⁻¹, maximum 1,265 → 110) and the analytic-Hessian test (pyscf, same 61 geometries, step 0.05: median 0.1, maximum 47 inside degenerate pairs only); pre-registration and results in `probes/results_vpt2/PREREGISTRATION_2026-09-21_FD_noise_demonstration.md`; the 5-point psi4 variant was stopped as redundant; (2) the same diagnostic run on naphthalene and one four-ring PAH at the PAHdb-anharmonic protocol's level as far as we can reproduce it (B3LYP/N07D, 200×974 grid, analytic Hessians via pyscf), with the out-of-plane modes' constants and their route differences tabulated; (3) the numerics literature read in full (Barone 2005 on VPT2 implementation; the Gaussian/SPECTRO step-size conventions; Bloino, Biczysko & Barone 2012 on resonances; any prior two-route check); (4) **done 21 September** — the upstream fixes are offered: pyVPT2 route-consistency report (philipmnel/pyvpt2#58 with issue #57), pyscf-forge #212 and #213; the note would report a repaired tool, not a complaint, once they are merged or answered. Earliest plausible: November 2026, after the 28 September conversation and gate A. The supervisor's group is the natural co-reader, and their own hypotheses in Mackie 2021 §5 are the first thing to test against.

## Dated addition, 2026-09-23 15:3x — a second candidate element, and the odds of the method re-estimated

**What was measured (23 September, CCX53):** E6, pre-registered on 19 September, read the couplings of the correction matrix as flat against data for every
mode-basis model (ratio to the zero rule 1.00 / 1.9 / 1.3 at 45, 100, 175 molecules; slopes 0.00 to −0.04). E7, pre-registered the same morning, traced it to the
target (sign-blind descriptors, locality lost in the mode transform), measured where the correction lives (parameter-free projection: three quarters on the
diagonal + atom-sharing pairs + ring bond–bond pairs of the primitive internals), and showed that a network asked for that local object learns the couplings from
the same 175 molecules: ring coupling ratio 0.43 / 0.47 on the two hold-outs, corrected frequencies 4.7 / 5.1 cm⁻¹ against 23 for no correction, MLP and trees
agreeing to two decimals. One hold-out molecule failed until its target was found to be a finite-difference artefact (psi4's default grid), replaced by an
analytic second route.

**What it could become:** a methods element rather than a paper on its own — "a learned force-field correction is local in internal coordinates and should be
predicted there" is close to Pulay's SQM argument and would be read as such by an insider; its novelty is the measurement (the projection ceilings) and the
learning-curve evidence that the mode basis fails for a structural reason. It belongs in the proposal's §6 and, if E8 confirms the same locality for the
coupled-cluster correction, in the paper on the learned layer. Prerequisites: E8 (benzene running, naphthalene pre-authorised), the gradient term, and a
CC-trained instance of the pairwise model on the first thin decks.

**Odds of the method (re-estimated for the user at 14:0x):** step 1 (28th) 85 %; the learned layer learns what it needs on the DFT–DFT proxy 80 % (was 45);
transfer to the CC correction 60 % (was 50) — E8 is the measurement; affordable with desktop + small Snellius 60 % (was 65; the out-of-plane family stays
on TZ after M3's first-family loss, the in-plane bend family is licensed for DZ after the second); full mandate ≈ 35 % (was 30); a defensible, per-family
licensed pipeline ≈ 70 % (was 65). The decisive next measurement is E8 (≈ €2, one night).

## Dated addition, 2026-09-24 06:4x — odds re-estimated after E8 (the user asked again)

E8 (benzene, CCSD(T)/cc-pVDZ) read the coupled-cluster correction as pairwise local: 92 % in the pattern of decision 49, 98 % with pairs two bonds
apart, ring couplings recovered only with the latter (0.34). It also priced the label: one canonical CCSD(T) gradient of naphthalene takes hours on a
CPX62; symmetry cuts naphthalene from 108 to 30 gradients, but substituted molecules have no symmetry to cut.

| question | 23 Sep | 24 Sep | why |
|---|---|---|---|
| step 1 — the conversation of the 28th carries a defensible plan | 85 % | 85 % | unchanged; E8's outcome and the corrected corpus add evidence, the anchor's third family is still running |
| the learned layer learns what it needs on the DFT–DFT proxy | 80 % | 80 % | E7 stands; the twenty imaginary-mode molecules may add rows |
| the same holds for the coupled-cluster correction | 60 % | **75 %** | E8: local in the same pattern, one bond further; transfer between cores is naphthalene's read-out (running) |
| affordable with desktop + small Snellius | 60 % | **55 %** | canonical CC Hessians are far dearer than the "≈ 4 days" I wrote; the label route must be LNO-CC energies plus sparse probing, and that is not yet measured on a real molecule |
| full mandate (large PAH in, spectral shape out, trained by 2027) | 35 % | **40 %** | the representation risk is largely retired; the cost risk is now the main one |
| a defensible, per-family licensed pipeline | 70 % | **75 %** | two families read, one won; data quality guarded twice |

Levers with tests (in order): (1) **sparse probing** — ΔF lives on pattern (d), so a Hessian correction needs displacements along far fewer directions
than 3N; plan 06's recovery theorems say how many; test on benzene's 72 gradients without new compute (reconstruct ΔH_CC from a pattern-chosen
subset); (2) **naphthalene E8** (running) — transfer between cores; (3) **the LNO-CC label cost on one substituted molecule** at the anchor's
thresholds, measured before any deck is bought; (4) cations (obstacle 9) — the corpus still has none.

## Dated addition, 2026-09-24 21:4x — odds re-estimated after the anchor (the user asked again)

Measured since the morning: the sparse-probe lever on benzene's 72 gradients is worth 1.2–1.5×, not the 3–5× hoped for; symmetry is the real count
lever (6× on benzene, 3.6× on naphthalene) and substituted molecules do not have it (`PreRegistration_2026-09-24_Sparse_Probe_Count.md`). The (T)
gradient phase of pyscf is single-threaded, so canonical CC Hessians of anything larger than naphthalene are out as labels (ledger 18:3x, 19:3x).
The anchor finished (21:02): the third family (C–C stretch) came out between the win and lose lines, so the DZ-anchored deck is licensed for one
family of three and the anchor stays cc-pVTZ for two thirds of the deck (`M3_TZ_MODE31_READING_2026-09-24.md`). On the other side of the ledger:
the anchor's fifteen TZ points took eight laptop-days, ≈ 9 h per LNO-CCSD(T)/cc-pVTZ energy of naphthalene — the first measured price of a
TZ label, and lower than the calendar assumed; the corpus release was corrected twice by the second route; the factory can re-optimise the
fifteen saddle points.

| question | 24 Sep 06:4x | 24 Sep 21:4x | why |
|---|---|---|---|
| step 1 — the conversation of the 28th carries a defensible plan | 85 % | 85 % | the anchor is read in full before the date; nothing new against it |
| the learned layer learns what it needs on the DFT–DFT proxy | 80 % | 80 % | unchanged (E7 stands; the release is cleaner) |
| the same holds for the coupled-cluster correction | 75 % | 75 % | naphthalene E8 still running (Saturday) |
| affordable with desktop + small Snellius | 55 % | **50 %** | sparse probing buys little; symmetry does not carry to substituted molecules; two of three families stay TZ; the LNO-CC label price on a substituted molecule is still unmeasured |
| full mandate (large PAH in, spectral shape out, trained by 2027) | 40 % | **35 %** | follows the cost line; the representation risk is retired, the cost risk is now the whole risk |
| a defensible, per-family licensed pipeline | 75 % | **80 %** | three families read against pre-registered criteria, one licensed, two TZ with measured increments in the error budget; the noise principle held twice |

Levers with tests (in order; none lowers the goal):
1. **Transfer the core, probe the substituent.** Symmetry cuts the parent's probe count; locality (pattern (d)) says a substituent changes ΔH only in
   its neighbourhood. Test on the existing corpus, no new compute: reconstruct the DFT–DFT ΔH of the mono-substituted layer-A2 molecules from the
   parent core's block plus the columns within two bonds of the substituent; pass bars in the E9 pre-registration of 22:0x (corrected-frequency RMS ≤ 3.3 cm⁻¹, ring coupling ratio ≤ 0.5). *(Corrected 21:5x: the first wording cited the benzene compact-basis ceiling of the sparse-recovery test as if it were an E7 number.)*
   If it passes, the label cost of a substituted molecule is the cost of its substituent's neighbourhood, not 3N.
2. **The LNO-CC label price on one substituted molecule**, cc-pVDZ at the anchor thresholds, on the CCX53 after naphthalene E8 (Saturday): energies
   along the neighbourhood directions of lever 1 only; the anchor's ≈ 9 h per TZ point of naphthalene is the yardstick. Pass: a full correction under
   two CCX53-days at DZ.
3. **Naphthalene E8** (running; Saturday morning): transfer of the local pattern between cores.
4. **Decision 45 densification** (running; Saturday midday): σ of the out-of-plane family closes the error budget's largest term.
5. **Cations** (obstacle 9): still no rows; the next corpus run after the 28th adds benzene⁺ / naphthalene⁺.

## Dated addition, 2026-09-24 22:0x — lever 1 tested the same evening: E9 passes on the proxy

E9 (pre-registered 22:0x, read 21:5x — the stamp of the registration was written before the clock was read again; the file order is registration,
run, outcome): with the parent core's ΔH block carried over and only the Hessian columns within two bonds of the substituent probed (25 % of the
gradients, no symmetry), the DFT–DFT correction of 182 substituted molecules comes back to 1.72 cm⁻¹ in corrected frequency (zero rule 23.1) and
0.13 in ring coupling ratio; the substituent's own atoms alone (12 %) give 2.19. Probe only and transfer only both fail (18.7 and 10.0 cm⁻¹).

| question | 21:4x | 22:0x | why |
|---|---|---|---|
| affordable with desktop + small Snellius | 50 % | **55 %** | the count lever for substituted molecules exists on the proxy: a label costs its neighbourhood (¼ of the gradients, ⅛ at the substituent alone); still to be confirmed at CC (lever 2) |
| full mandate | 35 % | **40 %** | follows the cost line |
| the other four lines | — | unchanged | |

Lever 2 is now sharply defined: one substituted molecule, LNO-CCSD(T)/cc-pVDZ at the anchor thresholds, energies along the neighbourhood
directions only (≈ 6 atoms × 3 × 2 displacements ≈ 36 energies, or the equivalent gradients), on the CCX53's idle cores after naphthalene E8 or on
a third server; the anchor's ≈ 9 h per naphthalene TZ point and the CCX53's 20,998 s per CC gradient are the yardsticks. Pass: a full correction
of a 25-atom molecule under two CCX53-days at DZ.

## Dated addition, 2026-09-24 22:5x — the idea not had before: labels per environment type, not per molecule (E10)

The user asked for the best new idea to raise the odds. Proposed and tested the same evening: if ΔH lives within two bonds, the neighbourhood
block of a substituent is a property of its environment and can be measured once, on the smallest host, and assembled into every molecule that
contains it — the label price becomes independent of molecule size (fragment additivity, measured rather than assumed, for a learned CC
correction). E10 on the proxy: between as registered (3.75 cm⁻¹), 11 of 15 substituent types within the bars under a torsion-matched donor
(pooled 3.36, ceiling 1.92), the four rotor types not. The odds lines are left where the 22:0x addendum put them until L2 prices the first
donor at the coupled-cluster level; the cost lever now has three measured parts (E9 neighbourhood 4×, E10 environment-once ≈ 2.7× on the layer,
symmetry 6× on the cores) and one unmeasured price (L2, running).

## Dated addition, 2026-09-25 07:0x — odds re-estimated with a long-term line (the user: "nu met een regel: lange termijn")

Since 22:0x yesterday: E10 between (11 of 15 substituent types transplant; rotors do not); L2's reference point > 9.5 h for one LNO-CCSD(T)/cc-pVDZ
energy of a 25-atom molecule at the anchor thresholds (fail bar > 2 h); the layer-B learning-curve run started on two CPX62 with the proof standard
pre-registered (`PreRegistration_2026-09-25_Proof_of_Learning_Layer_B.md`); the first two saddle-point pairs converge to the same true minimum;
the two-horizon note of 06:3x.

| question | 24 Sep 22:0x | 25 Sep 07:0x | why |
|---|---|---|---|
| step 1 — the conversation of the 28th carries a defensible plan | 85 % | 85 % | the anchor is read, the proof plan is registered and running; nothing new against it |
| the learned layer learns what it needs on the DFT–DFT proxy | 80 % | 80 % | unchanged until the 300-table; the honest status is in the 06:3x note (diagonal yes, couplings yes on unseen scaffolds, flat on bare parents) |
| the same holds for the coupled-cluster correction | 75 % | 75 % | naphthalene E8 Saturday; L2 changes the price, not the transferability |
| affordable with desktop + small Snellius (by 2027) | 55 % | **45 %** | L2: the LNO-CCSD(T) energy route at anchor thresholds is out for substituted molecules of 25 atoms; E10 recovers part (labels per environment type); the cheaper tier is unmeasured |
| full mandate (large PAH in, spectral shape out, trained by 2027) | 40 % | **35 %** | follows the cost line |
| a defensible, per-family licensed pipeline | 80 % | 80 % | unchanged |
| **long term (≈ 2030): a versioned ΔH network on CC labels whose held-out error keeps falling with each release and reaches the per-family noise floor for the mandate's molecules** | — | **60 %** | for: locality and transferability measured four ways, label definitions frozen and versioned, cost is not a blocker on this horizon, the proof standard is registered; against: the equivariant model is unbuilt, hold-out (a) is flat so far, size extrapolation and cations untested, and a decade needs continuity of attention and funding that no measurement can give |

Levers, in the order they now stand: (1) the layer-B curve (running; first table at 300 in days) — the proof itself; (2) the cheaper correlation tier for
labels (L2b: LNO-CCSD without (T), looser thresholds, MP2-anchored decks per family) — pre-registration this week, one energy each on the CCX53
when it is free; (3) naphthalene E8 (Saturday) for core-to-core transfer; (4) the size-extrapolation split on today's data (desk); (5) cations
(queued behind route 2); (6) the equivariant model, after the 28th, rerun on the same table.

*Correction 09:0x (25 September):* the bare-parent numbers quoted this morning (ratio 0.82 → 0.82 → 0.81, corrected RMS 10.0 → 9.5 → 9.3) are the 23 September run with benzene's corrupted finite-difference target; with the second-route target (E7 rung B `--use-analytic`, recorded in the ledger of 23 September 12:5x) hold-out (a) reads **0.47 → 0.45 → 0.43** and **5.9 → 5.1 → 4.7 cm⁻¹** at 45 → 100 → 175 — learning, not flat. The couplings of the bare parents are learned at the same level as the unseen scaffolds; what remains short is the slope (1.14× per decade on the ratio, 1.49× on the RMS, against the registered 1.5×). The odds lines do not move on this alone (the proof line already sat at 80 %); the reason for not raising it is the slope, not a flat curve.
