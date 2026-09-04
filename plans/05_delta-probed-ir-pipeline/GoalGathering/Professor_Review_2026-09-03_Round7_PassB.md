# Professor review — Round 7, Pass B (adversarial domain)

**Date.** 2026-09-03.
**Role.** Hostile external examiner (computational vibrational spectroscopy / local coupled-cluster
theory / numerical linear algebra / scientific ML). Not trying to help. Trying to find the
month-fourteen failure. No prior context on this project.
**Corpus.** Read in the brief's order, in full: `Professor_Review_2026-09-03_Round7_PassA.md`
(then the patched documents, to check the patches held); root `README.md`; plan-05 `README.md`;
`Why_05_Supersedes_04.md`; `Overarching_Goal.md`; `Research_Note_2026-09-03_Delta_Probing.md`
(including its §8 erratum); `Frozen_Lines_to_Beat.md`; `Frozen_Ladder_and_Tolerances.md`;
`Compute_Budget_2026-09-03.md`; `Distilled_Project_Plan_and_Quality_Checks.md`;
`Relevant_Scientific_Papers.md`; `probes/README.md`; plan 04's
`Professor_Review_2026-09-02_Round6_PassB.md`; `AI_Chats/grok_chat_4.md`. Plans 01–03 stay dead;
nothing below reopens them. Round-6 closures are inherited and not re-litigated.

**Pass A patch check.** The README's "all 21 addressed" list matches what the documents now say:
ρ\* and K_cap exist and are separate (Ladder §3, §4.8–9); Q8 has a three-part form with item 12;
the cost sentence has exactly two forms (Ladder §1) and the Goal's second sentence is conditional
on mode G; the learned prior is barred from R0–R3 and R6; Δ₃/Δ₄ enter Q7 from R0; hold-out
membership is seeded; ρ is defined; Q6 has a bias column; the M05 corpus is widened to dry-run
tensors. The patches held. Two of them created new attack surface (issues 3 and 1 below).

## Literature verified this pass (identifiers; how opened)

Full texts or full-text-equivalent:
- Kitzmiller, Lahm, Olive Dornshuld, Jin, Allen, Schaefer, "Convergent Concordant Mode Approach for
  Molecular Vibrations: CMA-2", *JCTC* **20**, 10886–10898 (2024), DOI 10.1021/acs.jctc.4c01240 —
  PMC11673116, full text.
- Lahm, Kitzmiller, Mull, Allen, Schaefer, "Concordant Mode Approach for Molecular Vibrations",
  *JACS* **144**, 23271–23274 (2022), DOI 10.1021/jacs.2c11158 — Europe PMC record + abstract.
- Mulas, Falvo, Cassam-Chenaï, Joblin, *JCP* **149**, 144102 (2018), arXiv:1809.05669 — arXiv PDF,
  full text (text-extracted; the plan's copy of this identifier is confirmed).
- Wang, Luo, Wang, Liu, "O1NumHess", arXiv:2508.07544 — arXiv HTML full text.
- Sanders, Andrade, Aspuru-Guzik, *ACS Cent. Sci.* **1**, 24 (2015) — PMC4827532 full text.
- Madriaga & Crawford, *JPCA* **129**, 10014 (2025), DOI 10.1021/acs.jpca.5c05210 — PMC12581137
  full text (the plan's bibliography item 30 says "PMC fetch blocked"; it opened for me).
- Altun, Ghosh, Riplinger, Neese, Bistoni, "Addressing the System-Size Dependence of the Local
  Approximation Error in Coupled-Cluster Calculations", *JPCA* **125**, 9932 (2021),
  DOI 10.1021/acs.jpca.1c09106 — PMC8607505 full text.
- Zhang, Li, Ye, Berkelbach, Chan, "Performant automatic differentiation of local coupled cluster
  theories", *JCP* **161**, 014109 (2024), arXiv:2404.03129 — abstract + HTML v1.
- "Overview of Developments in the MRCC Program System" — PMC11874011 full text (bibliography
  item 34's Mester et al. record).
- ORCA manuals: 6.1.1 detailed change log (orca-manual.mpi-muelheim.mpg.de/contents/appendix/
  detailedchangelog.html); 6.0 "Single Point Energies and Gradients"; 6.1 §3.9 MP2 (the
  `StoreDLPNOData`/`RefBaseName` section); 6.0 MDCI page. Psi4 manual "DLPNO-CCSD(T)" page.
  Molpro manual "Local correlation methods with pair natural orbitals (PNOs)" page.
- Williams et al., "Hessian QM9", arXiv:2408.08006 — arXiv abstract.

Abstract or record level only (numbers from abstracts or search-result snippets are marked
"snippet" where used):
- Esposito, Fortenberry, Boersma, Allamandola, *JCP* **160**, 211101 (2024), DOI 10.1063/5.0208597
  — Europe PMC abstract; the "B3LYP/N07D vs CCSD(T)-F12b/cc-pVTZ-F12 harmonic MAD 5.45 cm⁻¹"
  figure is from a search snippet of the paper body (AIP and Chapman full texts returned 403).
- Mackie et al., *JCP* **143**, 224314 (2015), DOI 10.1063/1.4936779 — Europe PMC abstract.
- Hrenar, Rauhut, Werner, *JPCA* **110**, 2060 (2006), DOI 10.1021/jp055578f — abstract (snippet).
- El Azhary, Rauhut, Pulay, Werner, *JCP* **108**, 5185 (1998); Rauhut & Werner, *PCCP* **3**, 4853
  (2001) — abstracts (snippets).
- Bégué, Carbonnière, Pouchan, *JPCA* **109**, 4611 (2005) — ACS abstract text via snippet ("absolute
  mean deviation of less than 0.8 %" is in the abstract).
- Reiher & Neugebauer, *JCP* **118**, 1634 (2003) and *PCCP* (2004) mode-tracking — snippets.
- Yang, Ma, Lu, Bian, "threshold-selecting Hessian", *JPCA* **128**, 3024 (2024) — snippet.
- Datta, Kossmann, Neese, *JCP* **145**, 114101 (2016) (DLPNO-CCSD first-order properties,
  unrelaxed) — snippet. Jiang et al. (Psi4 DLPNO-CCSD(T)), *JCP* **161**, 082502 (2024) — snippet.
- Acene B3LYP instability statements (hexacene triplet instability at B3LYP/6-31G(d); symmetry
  breaking from heptacene) — snippets of secondary sources, not the primary papers.
- GPU4PySCF: the "84-atom / 30 min A100 Hessian" figure appears in the search snippet of
  arXiv:2404.09452's PDF — still snippet grade, as the plan's bibliography says.

Recalled, not verified this pass: Martin, Taylor & Lee 1997 benzene CCSD(T) force field details;
Castiglioni–Zerbi effective-conjugation-coordinate theory beyond the snippet; numerical values of
ORCA's NormalPNO/TightPNO cutoffs (T_CutPNO 3.33×10⁻⁷ / 10⁻⁷); the energy carried by a single
PNO at the cutoff; Molpro's legacy PAO-domain LMP2/LCCSD analytic gradients; radical/edge-state
character of large zigzag-edged flakes; Kumar 2020 timings and Sylvetsky 2020 (verified last round,
not reopened).

---

**Verdict: conditional — green light only for a measurement programme at R0–R1 (dry run,
gradient-availability probe, Q6 with frozen thresholds, Q7, a prior-free locality probe, one
canonical diagonal check at pyrene), and only after the six blocking items below are written in;
no green light for the promised set as it stands (R0–R3 "beat" with Δ₃/Δ₄ on the promised path,
the mode-G cost question as the primary cost question, R6 as a whole-molecule probed object).**

Plan 05 is not a mistake relative to plan 04: for the same coupled-cluster information (the
CC−DFT curvature) it pays for a strictly smaller object, and every one of its licence probes is
cheaper than plan 04's first factory batch. It is a mistake as currently *promised* in three
places: it promises an anharmonic Δ that its probes cannot construct; it hangs its cost question
on a gradient that, on the verified landscape, will not run at R2–R3; and its recovery prior is
contradicted by the one published experiment closest to this design (CMA-2 on aromatics). The
"never done" sentence is false as written — the diagonal mode-E floor is the Concordant Mode
Approach applied to a difference — and must be rewritten with citation. None of that requires
going back to plan 04. "Neither is affordable" applies to R6 as a whole-molecule mode-E object;
it does not apply to R0–R3.

---

## Blocking findings

### 1. Mode E is noise-limited unless the frozen-domain energy is smooth at the µE_h level, and Q6 — the gate that would find out — has no frozen threshold, so it cannot breach

**Where:** Distilled Q6 (pass column: "deltas, noise and bias printed; breach **is** Ladder stop
4"); Ladder §4 items 1–12 (no Q6 item); Ladder §5.4 ("a licence probe breaches its frozen
threshold — Q6 …"); Distilled §3 "Patterns … Amplitudes fixed in the deck"; Research note §4.3.

**What — the arithmetic the brief asked for.** Let q be the dimensionless normal coordinate of a
DFT mode with harmonic wavenumber ω̃. The diagonal Δ₂ element in mode E is the central second
difference of ΔE(q) = E_CC(q) − E_DFT(q) at step q_s: Δ̂₂ = [ΔE(+q_s) − 2ΔE(0) + ΔE(−q_s)]/q_s².
With an uncorrelated energy error σ_E per CC point, σ(Δ̂₂) = √6·σ_E/q_s². A wavenumber
resolution δω̃ needs σ(Δ̂₂) ≤ 2δω̃ (since ω ∝ √k and k = ω̃ in these units), i.e.

  σ_E ≤ (2/√6)·δω̃·q_s² ≈ 0.82·δω̃·q_s²  — **independent of the mode's frequency.**

With 1 cm⁻¹ = 4.556 µE_h: for δω̃ = 5 cm⁻¹ the tolerable per-point error is **18.6 µE_h at
q_s = 1**, **4.7 µE_h at q_s = 0.5**, **1.2 µE_h at q_s = 0.25**; for the 1 cm⁻¹ scoreboard bind
divide by five (0.9 µE_h at q_s = 0.5). What q_s means in Cartesian terms (x₀ = 5.81 Å/√(μ·ω̃)):
C–H stretch 3,050 cm⁻¹ (μ ≈ 1.08 amu) 0.10 Å per unit q; C–C 1,600 (μ ≈ 6) 0.06 Å; C–C 1,300
(μ ≈ 4) 0.08 Å; CH-oop 850 (μ ≈ 1.1) 0.19 Å. So a q_s = 0.5 probe moves the leading atoms by
0.03–0.10 Å, and the energy rise being differenced is ½ω̃q_s² = 160–380 cm⁻¹ (0.7–1.7 mE_h).
Note one thing the plan never says in its own favour: because the differenced quantity is Δ, not
E, the central-difference contamination is (q_s²/12)·Δ₄, not (q_s²/12)·E₄, so q_s ≈ 1 is
legitimate for Δ₂ where it would not be for a full Hessian — the tolerance can be the 18.6 µE_h
figure, not the 1.2 µE_h one, *if* the frozen-domain bias at q_s = 1 is small.

Against that: **free domains.** Madriaga & Crawford (verified, full text) measure correlation-energy
discontinuities of ~1 µE_h, largest 6.09 µE_h, for *water* (10 electrons) under a field, and show
they destroy finite-difference second and third derivatives ("errors exceeding 100 %"). Each
discontinuity is one pair's PNO set crossing the cutoff; coronene has of order 2,000 correlated
pairs, so the expected jump density per displacement is one to two orders of magnitude higher
(inference, not measured). Free-domain mode E is dead at the 5 cm⁻¹ level for anything past
benzene. **Frozen domains.** ORCA 6.1 §3.9 (verified) freezes, for DLPNO-MP2 numerical
derivatives, the pair lists, the domains (MO-PAO, MO-Aux) and "the number of PNOs for each pair …
the ones with the highest occupation numbers are kept", with localized orbitals mapped by maximal
overlap; the manual's own words are that without this "large errors can occur". That is exactly
the remedy Madriaga & Crawford tested and rejected for field derivatives: "simply fixing the
dimensions of the PNO space for each pair of occupied orbitals cannot overcome such variations",
because the PNO *character* mixes across the truncation boundary. Whether small nuclear
displacements mix PNOs less violently than 0.001 au field steps is not known to me and is not in
the plan's literature; it is precisely what Q6's "second-difference noise vs step, with and
without frozen domains" would measure. And Psi4's DLPNO page (verified) documents no domain
reuse at all; the PySCFAD LNO paper (verified) treats LNO spaces as fixed in the derivative and
says the resulting errors "tend to be small, provided that the correlation domains are properly
converged" — for gradients, on ≤29-atom molecules.

**The spec hole.** Q6 prints "deltas, noise and bias" and "breach is stop 4", but Ladder §4 freezes
no Q6 number: items 1–12 are band lists, margins, P-gates, matrix tolerance, P3 size, M04 recipe,
resonance route, ρ\*, K_cap, f_h, τ₇, Q8 numbers. A gate with no threshold cannot breach. The
pattern amplitude q_s is "fixed in the deck" with no rule tying it to the noise floor it must
beat.

**Why it matters.** This is the plan's default mode at every rung the gradient probe says "no",
which on the verified landscape (issue 5) is R2–R3 at least. If the frozen procedure is not smooth
to a few µE_h across q_s = 0.5–1 displacements, mode E cannot resolve a 5 cm⁻¹ Δ₂, the recovery
fits noise, ρ\* is reached by chance or never, and Q7 at R0 (benzene: 12 atoms, essentially no
truncated pairs) will pass while telling you nothing about coronene. Round 6 Pass B finding 2
("curvature noise may swallow the signal") was closed in plan 05 by freezing domains; the freeze
is a hypothesis with a published negative analogue, not a closure.

**What would close it.**
- *In spec:* add pilot-note item 13: the Q6 noise threshold as the formula above with τ = the
  smallest beat margin of item 2 and q_s from the deck — σ_E(q_s) ≤ 0.82·τ·q_s² — measured at R0
  and at the R2-size family Q6 already names, with and without frozen data, on a step grid
  (q_s = 0.25, 0.5, 1.0); and a bias threshold: |Δ₂(frozen) − Δ₂(canonical)| along each R0 mode
  ≤ τ in wavenumber. Both are formulas, freezable now. State in Distilled §3 that the pattern
  amplitude is chosen *from* the Q6 step grid, never the reverse. Add Madriaga & Crawford's
  fixed-dimension result to the research note as the named risk of "frozen domains"; and record
  that Psi4 has no freezing option (stop 1 fires for Psi4 unless implemented).
- *As science:* the smoothness probe itself, run on naphthalene (not benzene) with the frozen
  DLPNO data along three modes (a C–C stretch, a C–H stretch, a CH-oop), 9 points each at
  q ∈ [−1, 1], TightPNO, and the second-difference scatter printed against the formula. Roughly
  30 local-CC energies of naphthalene: hours on a workstation. If the scatter is above the
  q_s = 0.5 line, mode E carries no "beat" language and only mode G or CPS-extrapolated energies
  (Altun et al., which doubles the point count) remain.

### 2. Δ₂ is not near-diagonal in the DFT normal-mode basis for aromatic ring modes — the published experiment closest to this design says so — and the plan's structural prior, its dry-run calibration and its mode-E floor all assume it is

**Where:** Distilled §3 "Structural prior" ("ℓ₁ penalty on off-diagonal elements (near-diagonal
prior) plus an off-diagonal low-rank term; … regularisation weights … fixed in the deck from the
dry run"); Research note §2 property 3 ("if DFT modes are approximately the true modes, the Δ
Hessian in that basis is close to diagonal"); Distilled §3 "Modes" (K = 2M + K_off, 2M "the
diagonal floor"); Compute_Budget §4.1 (dry run = "Δ between two DFT functionals"); Goal step 2.

**What.** Write Δ₂ in the DFT eigenbasis: Δ = LᵀH_CC L − Λ_DFT. Its off-diagonal elements are the
off-diagonal elements of the CC Hessian in the DFT mode basis, i.e. the DFT–CC mode rotation. For
two modes split by δω₁₂ and rotated by θ, the off-diagonal element is c ≈ 2ω·δω₁₂·θ, and
*dropping it* (which an ℓ₁ prior does) mis-places each frequency by ≈ δω₁₂·θ². In a PAH C–C/C–H
manifold (coronene: ~30 modes between 1,100 and 1,650 cm⁻¹, mean spacing ~20 cm⁻¹) a 30°
rotation between DFT and CC mode compositions costs ≈ 5 cm⁻¹ per mode; 45° costs ≈ 12 cm⁻¹ —
the beat-margin scale, exactly in the 6.2/7.7/8.6 µm families. And c itself (2·1,500·20·0.5 ≈
3×10⁴ cm⁻²) is *larger* than a typical diagonal element (a 5 cm⁻¹ correction at 1,500 cm⁻¹ is
2·1,500·5 = 1.5×10⁴ cm⁻²). The near-diagonal prior is therefore not a mild regulariser; where
mode compositions differ it is the wrong model.

**Evidence (verified).** CMA-2 (Kitzmiller et al. 2024, full text) is this design without the Δ:
high-level (CCSD(T)/cc-pVTZ) force constants in the normal-mode basis of a low level (MP2 or
B3LYP), diagonal first ("CMA-0A"), off-diagonals added by a diagnostic. Diagonal-only is
excellent on average (MAE 0.11 cm⁻¹ over 1,501 frequencies) — and fails on aromatics: pyridine
CMA-0A errors "up to −22.61, 27.60 cm⁻¹" from "aromatic ring vibrations that couple antisymmetric
ring stretching deformations with CH in-plane rocks", with "benzene, pyrrole, and furan" flagged
in the same breath; the cure was to compute the off-diagonals explicitly (ξ = 0.04 for pyridine).
That is the plan's R0 molecule. Second, O1NumHess (full text): even for a *single* DFT Hessian,
the conjugated polyene C₃₂H₃₄ gives frequency MADs of ~6–12 cm⁻¹ against ~2–5 cm⁻¹ for
saturated systems, and the authors state the Hessian's locality "tends to be worse" when other
electronic states are energetically close. Δ = CC − DFT inherits the worse of the two Hessians'
structure, and the DFT side is the one with the delocalisation error. Third, Sanders et al. (full
text): the compressed-sensing recovery is sparse only in a basis where cheap and expensive modes
agree, and the QM Hessian needed ~30 % of columns on anthracene precisely because MM3 modes and
DFT modes differ; "quantum mechanical Hessians don't scale as favorably as MM3 Hessians".

**Three consequences the plan does not state.** (a) The 2M "diagonal floor" of mode E is the
CMA-0 approximation; on aromatic CC/CH-bend manifolds the science is in K_off, and K_off is the
number that may grow with M. (b) The regularisation weights are "fixed in the deck from the dry
run", and the dry run is "Δ between two DFT functionals" — unspecified which. Two functionals of
similar exact-exchange fraction share the same mode compositions and produce a Δ that *is*
near-diagonal; a deck calibrated on it freezes a prior, a ρ\* and a K_cap that the CC Δ then
violates. (c) The plan's own null for this — Q7's discriminability clause and shuffled null —
runs at R0–R1 only; at R2–R3 a prior that suppresses c produces a Δ whose held-out residual can
still meet a ρ\* derived from (b).

**Why it matters.** This is attack 4 landing on the promised recovery, not on a bonus arm. A
confidently wrong Δ₂ in the CC-stretch block is the failure the astronomy cares about (6.2/7.7 µm
are the diagnostic bands) and the one Q7 at benzene may or may not catch (CMA-2 says benzene is a
flagged case — so Q7 at R0 is a genuinely informative test, which is to the plan's credit).

**What would close it.**
- *In spec:* (i) Replace "near-diagonal prior" by a **frequency-banded** prior: ℓ₁ on off-diagonals
  only *outside* a band |ω_i − ω_j| > w (w a deck number, e.g. 100 cm⁻¹), off-diagonals inside the
  band unpenalised, plus the low-rank term — this is CMA-2's lesson written as a regulariser, and
  it keeps the real-space locality claim (Q8) separate from the mode-basis sparsity claim. (ii)
  Fix the dry-run pair so that it brackets delocalisation error: B3LYP against a functional with
  markedly more exact exchange (BHLYP or HF−B3LYP), never two functionals of the same family; say
  so in Compute_Budget §4.1 and Distilled Q7's dry-run column. (iii) Add CMA-2's diagnostic idea
  as a pattern-design rule: off-diagonal blocks flagged large in the dry-run Δ are given explicit
  2-mode patterns in the hashed deck (before responses exist — the M06 rule already allows this).
  (iv) Rewrite Distilled §3 "Modes" so that K_off, not K, is the mode-E cost quantity Q8(c) tests,
  and say that K_off is expected to grow with the size of the near-degenerate manifold until
  proven otherwise.
- *As science:* at R1, print the recovered Δ₂ in the DFT mode basis against the Q7 reference,
  as a matrix, and the frequency error of the *diagonal-only* recovery separately (CMA-0 on Δ).
  If diagonal-only is within τ₇ on all families at naphthalene, the plan is stronger than it
  claims; if it fails on the C–C families, K_off is the project.

### 3. The promised Δ₃/Δ₄ cannot be built from the probes the plan specifies, and the literature the plan cites says it is not needed — delete it from the promised set

**Where:** Distilled §3 "Patterns" ("mode-targeted 1-D/2-D cuts along the promised families' DFT
modes for Δ₃/Δ₄"), "Structural prior" ("Δ₃/Δ₄ on the scored families by least squares on the
mode-targeted responses"); Distilled Q7(ii); Goal accuracy question ("Δ₃/Δ₄ on the scored band
families, from R0 onward"); Ladder R0 licence cell; Why_05 change 1, 3, 6; Research note §4.4.

**What.** GVPT2 for a family fundamental i needs the cubic constants that couple i to its
resonance partners: φ_ijj for ν_i ≈ 2ν_j and **φ_ijk (three distinct indices)** for
ν_i ≈ ν_j + ν_k, plus the semi-diagonal quartics φ_iijj. Mulas et al. 2018 (full text) obtain
these by numerically differentiating *analytic Hessians* along each mode (step 0.01 Å·amu^½),
which yields all φ_i** in one sweep; they note the full quartic field would cost 36N² Hessians and
compute only the semi-diagonal set. In *mode E* the plan has energies only. A 1-D cut along q_i
gives φ_iii and φ_iiii; a 2-D cut along (q_i, q_j) gives φ_iij, φ_ijj, φ_iijj. **No 1-D or 2-D cut
gives φ_ijk.** The combination-band resonances that matter for PAH bands — CH-oop overtones and
low-frequency combinations at 1,500–1,800 cm⁻¹ against the 6.2 µm C–C stretches; the CH-stretch
polyads Mulas describes as mixtures whose "leading" harmonic state carries as little as 12 % —
are φ_ijk resonances. So the Δ₃ the plan can actually recover is the wrong subset of constants,
and correcting φ_iij at CC level while leaving φ_ijk at DFT level is an inconsistent QFF. In mode
G a gradient at displaced (q_i, q_j) gives φ_ijk for all k — but mode G is the mode that may not
exist (issue 5).

**Does it matter?** The hybrid literature the plan itself cites says the CC pay-off is in the
quadratic constants: Bégué et al. 2005 (abstract verified) — CCSD(T) quadratic + B3LYP
cubic/quartic, "absolute mean deviation of less than 0.8 %"; the Barone/Puzzarini CC/DFT hybrid
line (snippet level) — same allocation, "reliability and overall good performances". Esposito et
al. 2024 (abstract verified; details snippet) reach 3-quanta CH-overtone assignments on naphthalene
with a B3LYP/N07D QFF and use CCSD(T)-F12b only for harmonic frequencies. Nothing I could open
shows a CC correction to a PAH cubic constant moving a scored fundamental by more than the beat
margin. So the harmonic-first allocation is defensible *for PAHs at the level of the available
evidence* — and the Δ₃/Δ₄ promise buys nothing the literature says is needed while adding an
unbuildable object to Q7 and to the accuracy claim.

**One related hole at DFT level.** Distilled §3 row 2: DFT cubic/quartic "from finite differences
of the analytic DFT Hessian along the promised families' modes" — this *does* give all φ_i** for
family modes i (Mulas's construction restricted), which is enough for resonances *involving* a
family fundamental. It is not enough for the reduced-dimensionality VPT2 the plan cites (bib 28)
if the "family" set excludes the partners' own diagonal anharmonicity; the pilot note's resonance
route (item 7) must say the family set is closed under the r₃/r₄ resonance search (partners'
modes are displaced too). That is 2 extra DFT Hessians per partner mode — cheap — and it is not
written.

**Why it matters.** Pass A issue 6 moved Δ₃/Δ₄ *into* the promised path from R0 and into Q7. That
made the plan internally consistent and scientifically worse: the accuracy claim now promises,
from benzene onward, a term that mode E cannot produce and that no cited source says is needed.
Q7(ii) will either be scored on the buildable subset (φ_iii, φ_iij) and pass vacuously, or fail on
φ_ijk it never had.

**What would close it.**
- *In spec:* remove Δ₃/Δ₄ from the promised set and from Q7. The promised object becomes "Δ₂ on
  all modes; DFT cubic/semi-diagonal quartic constants with the family set closed under the
  resonance search". Why_05 changes 1, 3, 6 and the Goal's accuracy question are edited to match.
  Keep a Δ₃ *diagonal* probe (φ_iii along each family mode, 4 energies per mode) as a labelled
  bonus arm that reports how big the CC correction to the diagonal cubic is; if it is below τ on
  the R0–R1 families, that is a published reason the allocation was right. This also closes Pass
  A issue 6 by deletion rather than by licence.
- *As science:* the bonus probe above at benzene and naphthalene.

### 4. The "never done" sentence is false as written: the mode-E diagonal floor is the Concordant Mode Approach applied to a difference, and the plan must cite it and rewrite the novelty claim

**Where:** Research note §2 ("What the 2026-09-03 search did not find … any application of
compressed-sensing or O(1)-gradient Hessian recovery to the *difference* …") and §6; Distilled
§2 neighbour table (O1NumHess / Sanders row: "not found in the 2026-09-03 search"); plan-05 README
"Provenance"; Frozen_Lines §1 last sentence.

**What.** Lahm et al., *JACS* 2022 (record verified) and Kitzmiller et al., *JCTC* 2024 (full
text): "high-level harmonic frequencies can be evaluated via CMA from a collection of single-point
energies that essentially scales linearly in the number of atoms"; Level B = B3LYP/6-31G(2df,p)
or MP2, Level A = CCSD(T)/cc-pVTZ; diagonal force constants in the low-level normal-mode basis
first (CMA-0), off-diagonals selected by a cheap diagnostic level (CMA-2, "all matrix elements ξ_ij
greater than a user-given threshold … will be explicitly computed"; ~33 off-diagonals, ~33 % extra
cost on the G2 set); tested on 120+ then 111 molecules, up to 17 atoms. Computing F_A,ii in the
Level-B basis and computing Δ_ii = F_A,ii − F_B,ii are the same measurement. What CMA does not
do: local CC, frozen domains, ℓ₁/low-rank recovery of the off-diagonal block from multi-mode
patterns, PAH sizes, a locality/saturation measurement, or cubic/quartic constants. Those remain
the proposal. Two further prior instances the sentence should name: mode-tracking (Reiher &
Neugebauer 2003, snippet: selected modes at high level by Davidson subspace iteration with few
gradients, "even very useful for small molecules that are treated with highly correlated …
methods, e.g. coupled cluster") for the "selected modes at CC cost O(few gradients)" idea; and the
fact, stated in the O1NumHess paper (full text), that compressed-sensing Hessian recovery *from
gradients at randomly displaced geometries* is already Aspuru-Guzik's, with an O(log N) gradient
count — so Sanders 2015 is not "columns only".

**Why it matters.** The brief says a prior instance does not kill the plan but must be cited and
the sentence rewritten. Beyond honesty, CMA-2 is the strongest evidence for issue 2 and the
template for its cure; a plan that does not know CMA exists will re-derive CMA-0's aromatic
failure at R0 and call it a surprise.

**What would close it.**
- *In spec:* bibliography items 42–43 (Lahm 2022; Kitzmiller 2024) with status OK; Research note
  §8 erratum: "the diagonal mode-E recovery is CMA-0 applied to Δ; CMA-2's diagnostic-selected
  off-diagonals are the nearest published alternative to the ℓ₁/low-rank recovery"; Distilled §2
  gains a CMA row ("does: CCSD(T) diagonals in DFT modes from single points, small molecules;
  this plan still asks: the same on a local-CC−DFT difference with frozen domains at PAH sizes,
  the off-diagonal block by sparse recovery, locality and K measured"); README Provenance and
  Frozen_Lines §1 drop "no probe-based CC force-constant correction at any size" and say what was
  found. Add mode-tracking as a cited alternative in the research note.
- *As science:* none; this is a citation.

### 5. On the verified gradient landscape mode G will not run at R2–R3, so the plan's primary cost question (Q8c in mode G) reads NOT_RUN by construction; the honest cost question is K_off in mode E, and whole-molecule mode E at R6 is a ≳10³-point object that the open fragment decision, not B3, decides

**Where:** Goal prime directive second paragraph and "Cost" question; Ladder §1 size claim, §2 R6
row ("K(R6) in the same table as K(R3), same mode, same prior") and "Promised … R6 reached as a
reach rung, conditional on B3"; Goal open decision 1; Research note §4.1 fallback ("CCSD-level
gradients plus energy-only (T)"); Compute_Budget §3–4.

**What — the landscape as of this reading (all verified this pass).**
- **ORCA 6.1/6.1.1** change log: no DLPNO-CCSD or DLPNO-CCSD(T) analytic gradient; canonical
  CCSD(T) gradients present (a UHF-CCSD(T) gradient accuracy fix is logged). ORCA 6.0 gradient
  page: DLPNO-MP2 (RHF) analytic gradients and second derivatives; nothing for DLPNO-CC. The
  DLPNO-CCSD "analytic derivatives" in the literature (Datta, Kossmann, Neese 2016, snippet) are
  orbital-unrelaxed first-order *properties*, not nuclear gradients. No ORCA 6.2 notes found.
- **Psi4** DLPNO-CCSD(T) page: energies; closed-shell RHF only; no gradient, no domain reuse.
- **MRCC** overview (full text): analytic gradients for HF, KS, MP2, canonical CC(n)/CI(n), LR-CC;
  none for LNO-CCSD or LNO-CCSD(T).
- **Molpro** PNO-LCCSD(T) manual page: no gradient, no frequency statement; a benchmark paper
  found in passing states PNO methods "have no implementation of analytical forces in MOLPRO"
  (snippet). The Werner group's *analytic* local-CC gradients (Rauhut & Werner 2001, abstract) are
  the older PAO-domain LCCSD, not PNO-LCCSD(T) (that the legacy code still offers them is recalled,
  not verified).
- **PySCFAD** LNO-CCSD(T) AD gradients (full text v1): benchmarked on the Baker set (3–29 atoms)
  and a [NiFe]-hydrogenase model (549 orbitals); LNO spaces held fixed in the derivative; memory
  dominated by ⟨ov|vv⟩ with recomputation during back-propagation; AIMD demonstration on
  H⁺(H₂O)₆. Nothing at coronene/TZ size; nothing about wall-clock relative to the energy.
- **Canonical** CCSD(T) gradients exist (ORCA 6.1; Psi4 DF-CCSD(T), Bozkaya & Sherrill 2017,
  snippet) and are a legitimate mode-G engine at R0–R1 and possibly pyrene/DZ on a workstation —
  but then "local CC with frozen domains" is not what is being probed, and the cost is B3 at R3.

So: mode G at R1 is plausible (PySCFAD or canonical); at R2–R3 it is a research project (PySCFAD
LNO-CCSD(T)/TZ gradients on 26–36 atoms, memory unknown) or a B3 canonical job. Q8(c) "in mode G at
R1, R2 and R3" — the one condition under which the plan may write a size claim — will most
probably read NOT_RUN, and the plan already knows it (Goal "Known risks"). The fallback in
Research note §4.1 (CCSD gradients + energy-only (T)) has no engine either: no production
DLPNO-CCSD nuclear gradient exists in any code I checked, and splitting (T) off would put the
(T) part back into mode E with all of issue 1.

**Cost model that follows.** Mode E: K = 2M + K_off local-CC energies per molecule — coronene
≥ 204 + K_off; issue 2 says K_off is the unknown. That is still a factor 30–50 below plan 04's
asserted 10⁴ points; it is the plan's real, defensible advantage and it is not O(1). **R6:** for
C₃₈₄H₄₈ (1,290 modes) whole-molecule mode E is ≥ 2,580 + K_off local-CC energies of a 432-atom
molecule. Psi4's own sizing table (verified) puts 1,500-atom DLPNO-CCSD(T) at 3 TB RAM; the
grok_chat_4 per-point assertion for coronene is "tens of minutes to hours"; scaling that to 432
atoms and multiplying by 2,600 points gives a number at the scale of a national allocation
(inference on an assertion — the plan's rules forbid using it as a budget, and I use it only to
say that "conditional on B3" understates what R6 is). Fragment probing (Goal open decision 1) is
the only route by which R6's CC cost stops depending on M — and fragment probing is valid only if
Q8 shows locality, which is exactly the property issue 2 and attack 1 doubt for the delocalised
block. The open decision is therefore real, and it decides whether R6 is a promised object at all;
it cannot wait until R4.

**Why it matters.** The Goal presents mode G as the designed path and mode E as the fallback. On
the evidence the design is mode E, and the plan's promised cost record will say "mode E; K =
2M + K_off; no size claim" at every rung above R1. That is an honest sentence, but a Module 08 that
was written to earn a size claim and never could is a rubric and defence problem the plan should
not carry for fourteen months.

**What would close it.**
- *In spec:* (i) Rewrite the Goal's "Cost" question with mode E as the primary case: "in mode E,
  did K_off saturate between R1, R2 and R3 (Q8c on K_off)?", mode G as the bonus case if the
  gradient probe says yes at all three rungs. (ii) Ladder §1: allow a second numeric cost
  sentence for mode E ("K_off went n₁ → n₂ → n₃ while M went M₁ → M₂ → M₃"), with the same
  adjective ban. (iii) Delete the CCSD-gradient + (T)-energy fallback from Research note §4.1 or
  mark it "no engine found (2026-09-03)". (iv) Move open decision 1 before the pilot note and make
  R6's promised form depend on it explicitly: "R6 is promised only as fragment-probed Δ₂ on the
  interior environments, conditional on Q8(a/b) passing at R2–R3 and on B3; whole-molecule
  probing at R6 is not promised." If the user decides fragments are transfer and out, R6 leaves
  the promised set (Round 6 Pass B finding 5 said the same for plan 04's R6).
- *As science:* the gradient-availability probe (probes/README item 3), extended with one PySCFAD
  LNO-CCSD(T) gradient at naphthalene/cc-pVTZ with wall-clock and peak memory printed, and one at
  pyrene if the first fits the machine. That is the whole of what decides mode G.

### 6. Q8 is measured on a recovered Δ₂ that the prior has already shaped, so it can certify locality the recovery imposed; the plan has no prior-free locality measurement above R1, and the per-family test inherits the same object

**Where:** Distilled Q8 (a), (b) ("per atom pair, ‖Δ₂ block‖ vs distance …"; "computed by zeroing
those blocks and recomputing the shift"); Ladder §3 Q8 bullet; Ladder R2/R3 rows ("Q8(a/b) second/
third read"); Why_05 closing section.

**What.** Q8(a) fits A·exp(−r/r_c) to the 3×3 blocks of the *recovered* Δ₂ in the atom basis;
Q8(b) zeroes the recovered long-range blocks and recomputes a family shift. Both are functions of
the recovery's output. The recovery is regularised (issue 2) by a prior that penalises exactly the
mode-basis off-diagonals through which a long-range, collective correction expresses itself, and
its patterns are O1NumHess-class — built on the assumption that the answer is local (the
displacement set is constructed "so every atom's local displacement space is complete"; the
off-diagonal-low-rank property is the premise, verified full text). A recovery built on a
locality premise, scored by a residual on probes designed under that premise, will return a local
Δ₂ whose Q8 fit passes. At R0–R1 the Q7 reference (full numerical local-CC Hessian) breaks the
circle; at R2–R3 nothing does, and those are the rungs where the collective π error grows (Altun
et al., full text: the DLPNO error on acenes grows roughly linearly with ring count; O1NumHess:
Hessian locality worsens as low-lying states approach; the acene B3LYP instability from hexacene
onward, snippet level). The brief's question — would the plan detect a delocalised C–C
correction per family, or misread it as local — has the answer: Q8(b) is per family, which is
right, but it is computed on an object that cannot contain what it is looking for if the prior
removed it.

**Evidence on the mode character of the largest Δ₂ (the brief's question).** I could not open a
per-mode CCSD(T)-vs-B3LYP table for an acene. What exists and I verified at abstract/snippet level:
Esposito et al. 2024 compared B3LYP/N07D with CCSD(T)-F12b/cc-pVTZ-F12 harmonic frequencies for
benzene and naphthalene (MAD 5.45 cm⁻¹, snippet); the mode-resolved table is in a full text that
returned 403 twice. CMA-2 (full text) identifies the largest low-level/high-level *mode
composition* disagreements in aromatics as ring-stretch/CH-in-plane-rock couplings, i.e. the
1,000–1,650 cm⁻¹ block, not C–H stretches or CH-oop. That is the block the 6.2/7.7/8.6 µm families
live in. It is consistent with the attack; it is not a measurement of Δ₂'s range on an acene, and
the plan should not pretend one exists in either direction.

**Why it matters.** Q8 is the plan's central bet and its own stated losing condition. A losing
condition that the machinery cannot reach is not pre-registered; it is decorative.

**What would close it.**
- *In spec:* (i) Q8(a/b) at R0–R1 are computed on the *reference* Δ₂ and on the recovered Δ₂ and
  the two r_c and long-range shares are printed side by side; a disagreement larger than ε₈ is a
  Q7-class breach. (ii) At R2–R3 add a **prior-free block probe**: for n_p atom pairs chosen by
  the deck at distances spanning the molecule (near, mid, far — in the π system, not C–H pairs),
  the 3×3 Δ₂ block is measured *directly* by 4-point finite differences of ΔE along paired
  atomic displacements (≈ 12 local-CC energies per pair with frozen data; 5 pairs ≈ 60 energies).
  Q8(a) is then fitted to the direct blocks, and the recovered blocks are compared to them. This
  is cheap relative to K and it is the only Q8 above R1 that the prior cannot pass for you. (iii)
  Q8(b) computed with the direct far blocks substituted into the recovered Δ₂ before the shift is
  recomputed.
- *As science — the cheapest probe that settles attack 1:* at **anthracene** (24 atoms, 66 modes;
  the acene where the collective error is already visible and a numerical local-CC Hessian is
  ≈ 2×66 + 1 = 133 energies, or 24 gradients if mode G exists at that size), a full frozen-domain
  DLPNO-CCSD(T)/cc-pVTZ numerical Hessian minus B3LYP, printed as Q8(a) per pair *and* as the
  mode-basis matrix per family. If the C–C-stretch block carries long-range pairs beyond r_max
  while C–H blocks do not, that is the answer, per family, before any R2 money is spent. Naphthalene
  (R1) is cheaper (97 energies) and is already in the plan; anthracene is the first acene where
  B3LYP's π error is not benzene-small, and it costs about the R2 pyrene batch. I would run it
  between R1 and R2 as a dated bonus with a fail-closed reading.

---

## Non-blocking findings

### 7. The whole CC pay-off at R1 is of the order of the beat margin, and part of it is already absorbed by the opponents' fitted scale factors

**Where:** Frozen_Lines §6 (7.1 cm⁻¹ quartet floor; PAHdb's three fitted scale factors); Distilled
P2 opponents (line A, M04 calibrated harmonic); Goal "Known risks" last clause.
**What.** The only PAH-class CCSD(T)-vs-B3LYP harmonic comparison I found gives a mean absolute
harmonic difference of ~5.45 cm⁻¹ on naphthalene (Esposito 2024, snippet). A scale factor fitted
to gas-phase bands (line A) and an M04 calibrated harmonic baseline both absorb the *mean* of that
difference per family; what remains for Δ₂ to buy is the mode-to-mode scatter about the mean,
which is smaller. The plan already says it may lose to calibrated harmonics and calls it
publishable. **Why it matters:** the defence should say the expected effect size out loud before
R0, not discover it in P2. **What would close it:** the pilot note's item 2 (margins) is
accompanied by an expected-effect line: "Δ₂ literature scale at R1 ≈ 5 cm⁻¹ MAD harmonic
(Esposito 2024; snippet, verify-on-use); the P2 hypothesis is that the family scatter of Δ₂
exceeds the margin". Nothing else.

### 8. The frozen-domain bias and the local-approximation error grow with size; CPS extrapolation is the published remedy and it doubles every probe

**Where:** Distilled Q6 (TightPNO vs NormalPNO column), Q0 deck ("local-CC code + thresholds");
Compute_Budget §3.
**What.** Altun et al. 2021 (full text): DLPNO-CCSD(T)/cc-pVDZ absolute-energy error on acenes
grows ≈ linearly with ring count — 4.50 kcal/mol at octacene with TightPNO (T_CutPNO = 10⁻⁷),
11.42 at 10⁻⁶, reduced to 1.04 by CPS(6/7) extrapolation (two T_CutPNO values per point). A
7 mE_h bias whose geometric modulation across a q = 1 displacement is even 1 % is 70 µE_h — above
the 18.6 µE_h line of issue 1 (inference). Q6's TightPNO-vs-NormalPNO frequency delta is the right
instrument to see it and has no threshold (issue 1); the deck has no CPS option. **What would close
it:** deck field "PNO extrapolation: none | CPS(6/7)"; if Q6's threshold delta exceeds τ at the
R2-size family, CPS becomes mandatory and K's wall-clock doubles — recorded in the classification
rule. The R0 canonical arm cannot see this (benzene has almost no truncated pairs); the R1 canonical
arm is the first that can, and it is conditional. The one canonical check that exposes the bias at
a size where it exists: a **diagonal-only** canonical CCSD(T)/cc-pVDZ Δ₂ along one mode per family
at *pyrene* (2 energies × 5 modes, 26 atoms, ~250 basis functions — hours per point on a
workstation or a TeraChem GPU node), compared with frozen-DLPNO and free-DLPNO along the same
modes. Q6 as written performs this at R0 only.

### 9. Module 05 as specified is a rubric hostage; it can be made honest, but only by naming the corpus and the target now

**Where:** Distilled §5–§6; Ladder §3 learned-prior bullet; Rubrics/README dataset rule (via Pass
A issue 18).
**What — the count.** Probed CC Δ tensors by the end of R3: R0 1, R1 1, R2 4, R3 1 = **7**, and by
the time Module 05 is likely written, **2**. A Transformer with an equivariant attention stack
trained on two tensors is a toy, and the P3 comparison on the dry-run corpus is the only version
with data. The dry-run corpus is unlimited but unspecified (which functional pair, which species,
how many). **What would make it load-bearing without touching the promised path:** (i) a
DFT-vs-DFT Δ₂ corpus at scale — thousands of molecules — built from a public Hessian set plus one
laptop-affordable second level; Hessian QM9 (Williams et al., arXiv:2408.08006, verified: 41,645
ωB97x/6-31G* Hessians) plus B3LYP/6-31G* Hessians recomputed on QM9 subsets gives a Δ₂ =
ωB97x − B3LYP tensor per molecule, with the exact-exchange contrast issue 2 asks for; (ii) the
target redefined from "a prior for Δ₂ blocks" to "the support of Δ₂ in the DFT mode basis" (which
off-diagonals are large) — CMA-2's Level-C diagnostic learned instead of computed — evaluated by
P3 on the dry-run corpus at matched K. Q4 is untouched (no lab data), Q3's molecule split becomes
meaningful, and the rubric's "public before the project starts" clause is met by Hessian QM9
itself; whether the recomputed B3LYP side counts as reuse is the mapping's call, as the plan says.
If the user will not accept a DFT–DFT target for the deep-learning module, say now that M05 is a
demonstration and defend it as one.

### 10. The R6 DFT Hessian is itself a B3 object, and the Goal's phrasing implies otherwise

**Where:** Goal step 1 ("on GPU where the deck names one … stays per molecule"); Compute_Budget §3
GPU-Hessian row (NOT_RUN, "B2 or B3").
**What — arithmetic.** C₃₈₄H₄₈ at 4-31G: 384×9 + 48×2 = 3,552 basis functions (6-31G*: 5,856 with
6d); 3N = 1,296 CPKS perturbations. The derivative-density/Fock storage for one batch of all
perturbations is 1,296 × 3,552² × 8 B ≈ 131 GB, so the Hessian must be batched to host/disk; the
GPU4PySCF release notes (snippet) say the DF Hessian was refactored "to reduce memory usage,
support larger systems". Scaling the snippet-grade 84-atom/def2-TZVPP/30-min A100 figure by
(432/84)³–⁴, corrected for the smaller basis per atom, gives tens to a couple of hundred A100-hours
per Hessian, plus the geometry optimisation. That is rentable and it is B3 by the plan's own
definition, not "own machine, GPU or not". PAHdb computed these at 4-31G on CPU clusters (line A's
paper, verified last round) for the same reason. **What would close it:** Compute_Budget §3 row
"DFT Hessian on GPU" gains "R6: B3 unless a timed probe on the R4 species shows otherwise"; Goal
step 1 drops the implication that the global part is always own-machine.

### 11. Inherited items — no worsening, one improvement, one wording

Charge states (neutral rule), matrix decidability (now per family with a measured gas grid),
intensities (reported, not scored), tier 2 (blocked on debt 4; MD-ACF potential now defined) —
plan 05 made none of these worse; the per-family decidability rule is an improvement on Round 6
finding 1. One wording: Distilled Q7 "at R0 also canonical CCSD(T) minus DFT (the only reference
independent of the freezing)" is correct and should be echoed in the Ladder R0 licence cell, which
currently says "against local-CC *and* canonical references" without saying which one licenses
the freezing.

### 12. Pass A items I judge worse than Pass A did

- **Pass A 13** (Q7 shares frozen domains): with Madriaga & Crawford's fixed-dimension result on
  file, this is not an "unstated limit" but the mechanism of issue 1; folded there.
- **Pass A 6** (Δ₃/Δ₄ unlicensed): the patch licensed an unbuildable object; issue 3.
- **Pass A 8** (locality asserted): the patch turned it into "the bet", correctly; issue 6 says
  the bet's referee (Q8) is not independent above R1.
- **Pass A 20** (mixed modes in the ratio): closed in spec; on the landscape of issue 5 the ratio
  will be NOT_RUN, so the closure is moot and the mode-E ratio must be defined instead.

### 13. Small verified corrections to the record

- Research note §4.4 / Why_05: Mulas 2018 used **B97-1** (TZ2P for pyrene, 6-31G\* for coronene),
  not B3LYP; the plan's line-B description ("anharmonic DFT-QFF") is fine, the functional is
  not named anywhere and should be, since the P2 comparison against Mulas is functional-specific.
- Research note §2 quotes O1NumHess as "tested at DFT level only" — correct (B3LYP-D3/def2-SV(P),
  BDF code); add that its worst covalent case is a conjugated polyene (MAD 6–12 cm⁻¹), which is the
  evidence for issue 2 sitting inside a paper the plan already fetched.
- Bibliography item 30: the PMC full text is reachable; "PMC fetch blocked" can be retried and the
  μE_h figures cited properly (1 μE_h typical, 6.09 μE_h largest, water/aug-cc-pVDZ).
- Research note section order: §8 precedes §7. Cosmetic.

---

## Attack-by-attack disposition (brief order)

| # | Attack | Lands? | Disposition |
|---|---|---|---|
| 1 | CC−DFT correction not short-ranged in a π system | **Partly — blocking through issue 6** | No per-mode acene CCSD(T)-vs-B3LYP table could be opened; CMA-2 and O1NumHess (verified) put the low-level/high-level disagreement in the ring-stretch/CH-rock block; Altun (verified) shows the local-CC error itself grows with acene length. Q8(b) is per family (good) but is computed on a prior-shaped object (bad). Cheapest settling probe: anthracene frozen-DLPNO numerical Hessian minus B3LYP, per pair and per family (~133 energies). |
| 2 | Energy-only recovery below the local-CC noise floor | **Yes — blocking, issue 1** | σ_E ≤ 0.82·δω̃·q_s²: 18.6 µE_h at q_s = 1, 4.7 at 0.5, 1.2 at 0.25 for 5 cm⁻¹; free domains fail (Madriaga & Crawford, verified); frozen domains are the fixed-dimension remedy those authors found insufficient for fields; Q6 has no frozen threshold. Mode E does not license "beat" until the smoothness probe prints under the line. |
| 3 | Mode G does not exist | **Yes — blocking, issue 5** | Verified: no local-CC(T) nuclear gradient in ORCA 6.1.1, Psi4, MRCC, Molpro PNO; PySCFAD AD gradients to 29 atoms; canonical gradients exist. Fallback (CCSD gradient + (T) energy) has no engine. Cost question must be re-anchored on K_off in mode E; R6 whole-molecule mode E is out of any budget; fragment decision decides R6. |
| 4 | Off-diagonal structure holds for Hessians, not Δ | **Yes — blocking, issue 2** | Δ's off-diagonals in the DFT basis are DFT/CC mode rotations; dropping one costs δω₁₂·θ²; CMA-2 (verified) shows diagonal-only fails on aromatic ring modes by ±20–28 cm⁻¹; the near-diagonal ℓ₁ prior is wrong where it matters; dry-run pair must bracket exact exchange; Q7 at R0–R1 cannot license the prior at R3. |
| 5 | Δ₃/Δ₄ not a small add-on | **Yes — blocking, issue 3, closed by deletion** | φ_ijk unreachable from 1-D/2-D energy cuts (Mulas, verified, uses Hessians along modes); hybrid literature (Bégué, verified abstract) says CC cubic constants are not needed; plan is stronger without the promise. Family set must be closed under the resonance search at DFT level. |
| 6 | Frozen domains: smooth but biased | **Yes — blocking via issue 1; bias part non-blocking issue 8** | ORCA freezes pair lists, domains, PNO counts (verified); PNO-character mixing is the documented residual; Werner-group frozen-domain structures "minor changes" (abstracts); size-growing local error (Altun, verified). Canonical diagonal check at pyrene; Q6 does it at R0 only. |
| 7 | Deep-learning module a rubric hostage | **Yes — non-blocking, issue 9** | 7 CC tensors by R3, 2 by Module 05. Hessian QM9 (verified) plus a recomputed second level gives a real DFT–DFT corpus; target should be the Δ₂ support (CMA-2's diagnostic). Q4/Q3 allow it; the mapping decides reuse. |

**Also-worth items:** novelty → issue 4 (falsified in part; CMA). Fragment probing → real, not
moot, and it decides R6 (issue 5). R6 DFT Hessian → B3 object (issue 10). Inherited items → no
worsening (issue 11). Pass A items worse than judged → issue 12.

---

## What would settle "is plan 05 a mistake?"

Plan 05 as **a measurement programme at R0–R1 that decides, with printed numbers, whether a
frozen-domain local-CC−DFT curvature correction is smooth, recoverable and local** is not a
mistake; it is cheaper than any plan-04 probe and it answers plan 04's Round-6 finding 2 with
data instead of averaging. Plan 05 as **the promised set now written** is a mistake in three
places (issues 1–3, 5), each cheaper to fix on paper than to discover at R2.

Measurements that settle it, in the order they decide things, all fail-closed:

1. **Smoothness under the line (issue 1).** Naphthalene, frozen DLPNO data, three modes, 9 points
   each at q ∈ [−1, 1], TightPNO: second-difference scatter vs σ_E ≤ 0.82·τ·q_s². ~30 energies.
   Above the line at q_s = 0.5 → mode E carries no beat language; the plan continues as a mode-G /
   CPS experiment or stops with a measured reason.
2. **Gradient availability, with memory (issue 5).** One PySCFAD LNO-CCSD(T)/cc-pVTZ gradient at
   naphthalene, then pyrene: wall-clock and peak memory. Decides whether Q8(c)-in-mode-G exists
   anywhere above R1, and therefore whether the size claim is a sentence the thesis can ever earn.
3. **Diagonal-only vs full recovery at R1 (issue 2).** The Q7 comparison printed twice — CMA-0 on
   Δ and the full ℓ₁/low-rank recovery — against the numerical reference, per family. If
   diagonal-only is within τ on the C–C families, K_off is small and the plan is stronger than it
   claims; if not, K_off is the project and its growth from R1 to R3 is the real cost question.
4. **Prior-free locality at anthracene (issue 6).** Frozen-DLPNO numerical Hessian minus B3LYP
   (~133 energies): Q8(a) on the *direct* blocks, per pair and per family. If the 6.2/7.7 µm block
   is carried by pairs beyond r_max while C–H blocks are not, the reach story needs a different
   object than fragments, and R6 leaves the promised set now rather than at R3.
5. **Canonical diagonal check at pyrene (issue 8).** Two CCSD(T)/cc-pVDZ energies per mode along
   one mode per family: frozen-DLPNO bias at a size where truncated pairs exist. Decides whether
   CPS extrapolation (2× every probe) is mandatory.

Until 1–3 have printed, R2–R3 "beat" and any cost sentence beyond "mode E; K = 2M + K_off" are
promises made against the literature. Do not go back to plan 04: its object was larger and its
probes were dearer. Do not promise R6 as a whole-molecule mode-E object under any allocation this
project might hold; decide fragments first, or drop R6 as Round 6 already advised for plan 04.

---

*Pass B complete. No frozen document was edited. Identifiers verified this pass are listed at the
top and are not scored-module cites; verify-on-use still applies.*
