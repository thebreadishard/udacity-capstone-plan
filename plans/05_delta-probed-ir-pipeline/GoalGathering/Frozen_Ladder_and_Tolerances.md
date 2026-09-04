# Frozen ladder and tolerances — Plan 05

**Status.** Frozen 2026-09-03 in *form*; revised the same day after Round-7 Pass A and Pass B;
amended 2026-09-04 by the user's decisions and revised the same day after Round-8 Pass A and
Round-8 Pass B. Carried from plan 04 with the plan-05 additions marked **[05]**; the
pilot-dependent numbers (§4) are frozen by a dated note **before** any comparison they govern is
scored. After that note, no number may be loosened in either direction. Agrees with
[Overarching_Goal.md](Overarching_Goal.md), whose glossary defines every symbol used here; the
Goal file wins on drift. Costs live in [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md).

---

## 1. Three sentence types, declared up front

- **Accuracy rungs (A).** Laboratory data exists. The claim is *beat the frozen line per band
  against the lab scoreboard* ([Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) §5).
- **Reach rungs (R).** No per-molecule laboratory spectrum exists. The claim is *the pipeline
  ran end-to-end and produced a spectrum with a stated error budget*; comparisons against the
  lines are **theory-vs-theory and labelled as such**. The word "beat" is forbidden on reach
  rungs.
- **[05] Cost sentences.** Exactly two kinds exist, and this is the only place that defines
  them; every other document conforms to this section.
  - **The cost record** — allowed on any rung once printed, and *promised* for every rung that
    ran, **one per mode that ran on the rung**: `K = n (of which 2M = … diagonal, K_off = …
    off-diagonal) at rung R, mode E|G, prior = structural|learned, ρ* = …, PNO extrapolation =
    none|CPS, wall-clock w per probe on machine m, printed by probes/<file>`. Nothing else about
    cost may be written.
  - **The size sentence** — numeric only, in one of two forms, each allowed only after Q8(c)
    has passed for that quantity at R1→R2 and R2→R3 with the structural prior at the same ρ\*
    rule: *mode-E form* (always earnable, because mode E runs on every rung R1–R3 that runs):
    "K_off went n₁ → n₂ → n₃ from R1 to R3 while the mode count went M₁ → M₂ → M₃"; *mode-G
    form* (only if mode G was licensed and ran on R1, R2 **and** R3 — side-project milestones M3,
    M4, M5 with both checks each): the same for K. The adjectives "size-independent", "O(1)",
    "saturates", "does not grow", with or without "-class", are forbidden everywhere, including
    the Module 08 paper.
  - **"Beat" and noise.** A rung carries "beat" language only if the Q6 noise line **of the
    mode that produced its scored Δ₂** (σ_E line for mode E, σ_g line for mode G; §3) passed at
    that rung's size class; otherwise it carries a cost record and no "beat".

## 2. The ladder (rungs and species carried from plan 04; R2 re-read, see the dated note)

| Rung | Molecule(s) | Type | Why this rung | Opponents | Lab scoreboard | **[05] what it licenses** |
|---|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ (12 atoms, 30 modes) | A | End-to-end laptop pilot; canonical CCSD(T) **expected** affordable in the anchor basis — plan-02 measured 19.6 s/point at 6-31G* and a failure at ~114 functions with 28 GB on the old machine, provenance only — **measured by the one-point canonical feasibility probe before the pilot note** (§3; Budget §4) | A, B | NIST gas; PAHdb experimental | **Q7 probing licence for Δ₂** against the frozen-space local-CC reference *and* the canonical reference — **the canonical arm is the only one that licenses the space freezing** (Q6 bias), so its feasibility is measured first; Q8(a/b) on the reference Hessian as Q7's sub-item (iv); the zero-CC dry run in both modes with its noise-injection column; the Q6 noise grid at R0; probe M1's assignment log; side-project M2 (after the pilot note) |
| **R1** | naphthalene C₁₀H₈ (18 atoms, 48 modes) | A | The canonical-vs-local-CC licence molecule, conditional exactly as in plan 04: the first R1 probe measures whether canonical (T) runs on the B2 laptop at any usable basis; if not, the licence downgrades to **R0-only plus a declared cross-basis protocol**, stated in every anchor claim | A, B | NIST; PAHdb experimental | **The Q6 smoothness probe** (three modes plus one totally symmetric mode, nine points each, frozen spaces; the σ_E estimator of §3; scatter printed before the pilot note, means sealed); Q6 anchor licence; Q7 at a second size, printed for diagonal-only and full recovery; first Q8(a/b) rung read (on the reference Hessian); expected-effect line printed; side-project M3 (after the note) |
| **R2** | pyrene C₁₆H₁₀ (26 atoms, 72 modes); chrysene C₁₈H₁₂; triphenylene C₁₈H₁₂; tetracene C₁₈H₁₂ (each 30 atoms, 84 modes) | A | First territory beyond PAHdb's anharmonic front | A, B | **Gas (NIST WebBook / NIST-EPA gas-phase IR database, GC-IRD hot-vapour spectra; JCAMP `DELTAX` 4 cm⁻¹, stated resolution 8 cm⁻¹ at snippet grade, no concentration):** pyrene, chrysene, triphenylene — **decidable per family only by the measured band-centre uncertainty rule below; the C–C families are expected inconclusive by construction on this source.** **Matrix (PAHdb experimental uids 334, 282, 291 as recorded in plan-02 probes):** pyrene, tetracene, chrysene. Tetracene has no gas-phase IR (solid-only) and is scored on matrix data only, every family M03-gated. IRMPD = context only | Q6 at R2 size: the **canonical diagonal check at pyrene** (two energies per mode, one mode per family) and the TightPNO/NormalPNO column; the Q6 noise grid at R2 size in the mode(s) used; **prior-free direct-coupling probe** for Q8(a/b); mode E runs; K and K_off printed; Q8(c) first ratio (R1→R2); **the learned prior's licence is earned here** (§3); side-project M4 |
| **R3** | coronene C₂₄H₁₂ (36 atoms, 102 modes) | A | Mulas 2018's molecule (B97-1 QFF, item 6); largest PAH with a usable matrix spectrum (uid 18); no gas-phase IR in the WebBook | A, B (Mulas), C | PAHdb experimental (uid 18), every family M03-gated | direct-coupling probe; mode E runs (mode G in addition if M5 licensed it); Q8(c) second ratio (R2→R3); the size sentence is decided here; **the fragment-vs-whole comparison at the smallest passing radius** (fragment licence part b); the learned prior's licence earned here too; side-project M5 (both checks at coronene) |
| **R4** | circumcoronene-class, C₅₄H₁₈ → ~C₉₆ | R | First rung with no per-molecule lab truth | A, C (theory-vs-theory) | — | expert-judgment datum (Goal, expectations tier 3); the first rung where a spent learned-prior licence may run (§3); **the fragment-vs-whole comparison on a molecule larger than coronene — promised conditional on B3 classification, not bonus** (fragment licence part b′); the **fragment-radius convergence test on circumcoronene's central ring** (part c, first instance); the R6 DFT-Hessian timing probe |
| **R5** | ~C₂₁₆ (top of Mai's set) | R | Meet line C at its own ceiling | A, C | — | as R4 |
| **R6** | C₃₈₄H₄₈-class (for C₃₈₄H₄₈ itself: 432 atoms, 1,290 modes) | R | Only line A exists here, at 4-31G | A (theory-vs-theory) | — | **fragment-probed Δ₂ only**, under the fragment licence (§3), including the **fragment-radius convergence test on the R6 interior** (part c) and, where B3 allows, whole-flake direct couplings as the gold check; the reach certificate; cost record in the same table as R3's, same mode, same prior. **Whole-molecule probing is not promised**: mode E would be ≥ 2,580 energies of a 432-atom molecule |

**Dated note, 2026-09-03 (R2 re-read), confirmed 2026-09-04.** Plan 04's R2 row excluded
triphenylene as having "no laboratory spectrum" and was written before plan 04's own NIST
coverage probe completed. That probe (plan 04 `probes/nist_gas_coverage.py`, raw evidence in
its `nist_cache/`) found gas-phase IR for pyrene, chrysene **and triphenylene**, none for
tetracene (solid-only), none for coronene. The R2 A-scored set is pyrene, chrysene,
triphenylene (gas families where decidable) and tetracene (matrix, M03-gated). Decision 3.
**Addendum after Round-8 Pass B (finding 6):** the Round-8 reviewer verified that the
triphenylene entry is a GC-IRD gas-phase spectrum from the NIST/EPA database with `DELTAX` 4 cm⁻¹
and no resolution or temperature line, that the database description states an 8 cm⁻¹
homogenised resolution (snippet grade; bibliography item 50), and that no concentration data
exist. "Gas families where decidable" is therefore governed by the band-centre-uncertainty rule
below, not by the 4 cm⁻¹ point spacing; the R2 C–C families are **expected inconclusive by
construction** on this source, and decidable C–C scoring at R2 needs a source the plan does not
yet have (PAHdb gas-phase v1.00, jet-cooled or low-temperature cells — the supervisor ask of
Proposal §13.3 is load-bearing).

**Dated note, 2026-09-03 (R6 form), closed 2026-09-04 (decision 1).** R6 is promised as
**fragment-probed Δ₂**, conditional on the fragment licence of §3 and on B3; families that fail
the licence are withdrawn from the R6 certificate with their measured long-range share; if all
scored families fail, R6 is reported with the Distilled §8 sentence. Whole-molecule R6 is not
promised.

**Decidability per family (frozen form; Round-8 Pass B finding 6).** A family is scored against
gas-phase data wherever gas data exists for that molecule and family. It is **decidable** if the
**measured band-centre uncertainty** u_band of the gas scoreboard for that family — the
quadrature sum of (i) the instrument resolution as stated by the source's documentation (never
the JCAMP point spacing), (ii) the centroid precision from the spectrum's signal-to-noise, and
(iii) a **temperature term** for hot-vapour sources (a declared hot-band shift per family from a
pinned reference, or, until one is pinned, the labelled uncertainty "hot-vapour scoreboard,
0 K prediction" with its estimated magnitude) — is smaller than the family's beat margin. M03
prints u_band and the verdict per molecule and family **before the pilot note**; the pilot note's
item 1 records per family *gas-decidable / matrix-gated / inconclusive by construction*. A family
with matrix data only passes through the **M03 matrix–gas gate**: if the M03-measured
|matrix−gas| delta for that family is not smaller than its beat margin, it is scored
**"pre-declared inconclusive on matrix"** — not "beat", not "lost". R0–R1 are gas-scored
throughout against NIST spectra whose u_band M03 measures the same way; they are unconditional
in the sense that no matrix gate applies, and their C–H and CH-oop families are expected
decidable.

**Promised:** R0–R1 scored as accuracy rungs against gas-phase data. R2–R3 scored as accuracy
rungs per family under the decidability rule above and the "beat and noise" rule of §1. R6 per
the dated note above. **[05]** The **cost record** (§1) for every rung and mode that ran; **mode E
runs on every rung R1–R3 that runs**. **[05]** Probe M1 (frozen spaces) as the precondition of
every local-CC probe, under stop 1. **[05]** The fragment licence's parts (a)–(c), part (b′) at R4
conditional on B3 classification.
**Bonus:** R4 and R5 as spectra, anything beyond R6, the diagonal-cubic probe (Δ₃ along scored
modes), the anthracene locality probe, the size sentence itself (it is earned or not; its absence
is not a failure), the side project's milestones M2–M5 (their failure costs the promised set
nothing once M1 has passed), the learned prior's spent licence on R4–R6, and whole-flake direct
blocks at R6.

**Charge.** All rungs are **neutral species** unless a rung's pilot note names a charge state.
The reasons, written under the inheritance rule (Goal): B3LYP spin contamination for radical
cations degrades the DFT baseline the correction rides on; the canonical reference arm doubles
in cost for open shells; most cation laboratory data is matrix or IRMPD, which the scoreboard
rules already gate. Open-shell LNO-CCSD(T) exists in the candidate code (item 48, fetched), so
the rule is a per-rung choice, not a capability limit; a pilot note may name a charge state for a
rung with those three points addressed.

**Ordering.** R0 before anything. M1 before any local-CC probe. The canonical feasibility probe
before the pilot note. R1 before any local-CC-based accuracy claim. **[05]** Q7 must pass at R0
and R1 before any Δ₂ enters a scored spectrum at any rung; the R0–R1 scored spectra themselves
are produced only after Q7 has printed. The Q6 noise line of the mode used must have passed at
the size class before any "beat" sentence. Q8(a/b) must be printed at R1 (reference), R2 and R3
(direct couplings) and Q8(c) at R1→R2 and R2→R3 before any size sentence is worded. Reach rungs may
not start before R3 has been **scored** (scored includes lost and pre-declared inconclusive) and,
for fragment probing, before the R3 fragment-vs-whole comparison has printed.

## 3. Frozen now (not pilot-dependent)

- **Reporting unit:** cm⁻¹ per band; families = CH-stretch (~3.3 µm), CC modes (6.2 / 7.7 /
  8.6 µm), CH-oop by adjacency class (solo / duo / trio / quartet, 10–15 µm).
- **Resolution floor:** no claim finer than **10 cm⁻¹** in any astronomical framing; a
  lab-facing claim may be finer only if u_band *and* the declared controls (ρ, local-CC noise
  floor, threshold sensitivity) support it, printed by the comparison probe — never finer than
  the scoreboard's own uncertainty (~1 cm⁻¹ bind).
- **Matrix tolerance:** working convention **15 cm⁻¹**; binding value = the Module-03 measured
  one, frozen in the pilot note (§4 item 4). Gas-phase preferred over matrix wherever both exist
  and u_band allows.
- **Comparison form (pre-registered):** paired per-band absolute error, pipeline vs line, on
  identical lab bands; per family; mean ± spread. ≥3 seeds for every ML component.
  **Inconclusive is a publishable outcome.** The scoreboard is never a training, validation or
  pattern-design input of the pipeline (Distilled Q4; the M04 baseline is the declared exception).
- **No lab band may be scored twice under different windows.**
- **[05] Anchor basis fixed per rung in the deck, and the same basis on both arms of every
  comparison**: cc-pVTZ for R0 and R1 (the licence rungs); the R2–R6 basis is a deck number
  frozen before that rung's first probe. The Q6 bias line compares Δ₂(frozen) and Δ₂(canonical)
  in the same basis; if the canonical feasibility probe shows cc-pVTZ canonical CCSD(T) does not
  fit the B2 laptop at R0, the bias line is measured in the largest basis that does (cc-pVDZ)
  with the frozen arm re-run in that basis, labelled, or the R0 canonical Hessian is the first B3
  request — a dated note says which.
- **[05] The promised correction is Δ₂ only.** No CC correction to cubic or quartic constants
  is promised; the diagonal-cubic probe is a bonus number. DFT anharmonic constants are computed
  for a family set closed under the resonance search **to closure depth one** (a scored family
  mode's partners; the partners' own diagonal anharmonicity from their 1-D cut only), bounded by
  the polyad cap; the pilot note prints the closed set's size and Hessian count per rung.
- **[05] K is a measurement, not a choice — with a noise-aware stopping rule.** Patterns are
  consumed in the hashed order of the Q0 deck. At each count n the held-out residual ρ(n)
  (Distilled §3) is computed together with its **noise floor** ρ_noise(rung, mode) =
  σ(mode)/RMS_resp(rung), where σ is the per-point scatter σ_E or σ_g measured by the R1
  smoothness probe (item 13) and RMS_resp the RMS of the rung's own held-out responses. **K is
  the smallest n at which ρ(n) ≤ ρ\* with ρ\* = c·ρ_noise**, c ≥ 1 the pilot-note constant of item
  8; equivalently, the held-out χ² per point with σ as the per-point sigma first falls to c². K is
  never written down before the rung runs; K_off = K − 2M in mode E. The pilot note freezes a
  **cap K_cap** per rung and per mode (item 9) from the **noise-injected** dry run (Distilled §3,
  Budget §4.1) — never from the noiseless one. If ρ has not reached ρ\* by K_cap, the rung's Δ₂
  is "not recovered at cap" (§5.4), and the cap is never raised to rescue it.
- **[05] Hold-out membership is decided before any response exists:** by a seeded rule in the
  Q0 deck (deck seed + pattern index), fraction f_h (item 10).
- **[05] Frozen spaces — the object, written once.** At the reference geometry the local-CC code
  stores the localized occupied orbitals and each fragment's LNO (or PNO) vectors in the AO
  basis. At a displaced geometry: the localized occupied orbitals are mapped to the stored ones
  by maximal overlap and the **assignment permutation is printed**; the stored virtual-space
  vectors are **projected onto the new geometry's virtual space and Löwdin-orthonormalised**; that
  projected, orthonormalised set is "the frozen space", and the correlation energy is evaluated in
  it. For mode G the projection is **inside the differentiated graph**. Every local-CC probe
  evaluation at a displaced geometry uses frozen spaces so defined. **Probe M1** tests that the
  candidate code (the pyscf-forge LNO code, item 48) can do this and prints, along one totally
  symmetric, one degenerate and one non-symmetric benzene mode, the assignment permutation and
  E(displaced, frozen) − E(displaced, fresh) per point, without a verdict. A code that cannot
  freeze spaces is reported under stop 1 (as of 2026-09-04: ORCA documents freezing for
  DLPNO-MP2 only; Psi4 documents none).
- **[05] The structural prior is frequency-banded** (Distilled §3): off-diagonal Δ₂ elements
  between DFT modes closer than w are unpenalised; outside the band they carry the ℓ₁ penalty;
  plus a low-rank term. **w and the weights are fixed from the dry run by a stated rule** (item
  13): w = the smallest band width at which the dry run's full recovery reproduces the direct
  DFT−DFT Δ₂ within τ₇ on every family at the largest dry-run size, and the ℓ₁ and low-rank
  weights by the dry run's held-out ρ minimum on the noise-injected column — printed, not chosen.
  The dry-run pair is **B3LYP against a functional with markedly more exact exchange**
  (BHLYP-class or Hartree–Fock), never two functionals of one family.
- **[05] Pattern amplitudes come from the Q6 step grid**: the largest step at which the R1
  smoothness probe's σ is under the noise line of the mode used; never chosen to make a recovery
  converge.
- **[05] Probe patterns are hashed** in the Q0 deck before the first probe runs; off-diagonal
  blocks the dry run flags as large receive explicit two-mode patterns in that deck; adding,
  removing or re-weighting patterns after any residual is known is a Distilled §4 deviation.
- **[05] Order of the pilot inputs, and what they may not contain.** The pilot note is written
  with: the lab side (including M03's u_band table); the opponent side; the **zero-CC dry run**
  (both modes, with its noise-injection column); probe M1's printout; the **canonical feasibility
  probe** (one canonical CCSD(T) energy of benzene in the anchor basis on the B2 laptop:
  wall-clock, peak memory, extrapolated to the Hessian count); the gradient-availability probe
  **as a run/no-run at the equilibrium geometry only**; the **R1 smoothness probe's σ only** — its
  script prints σ_E (and σ_g where a gradient runs) per mode and per freezing arm and writes the
  fitted polynomial coefficients (which contain the diagonal Δ₂ elements) to a hashed, sealed file
  that is opened only after the note is committed; and single-point timings. **No local-CC Δ₂
  number, diagonal or otherwise, is readable when ρ\*'s constant, K_cap, τ₇ or the beat margins
  are written.** The R0 local-CC probe batch, the Q7 references and the side project's M2–M5 all
  run **after** the note.
- **[05] Mode E runs on every rung R1–R3 that runs.** On a rung where mode G is licensed, mode
  G runs **in addition**; the rung carries two cost records; Q8(c) is computed per mode over the
  rungs that mode ran, so the mode-E size sentence is always earnable and the mode-G one wherever
  mode G ran on all three.
- **[05] The learned prior: earned on R2–R3, spent on R4–R6.** On R0–R3 the scored spectrum is
  always the structural recovery; no neural network is on the promised accuracy path.
  *Earning:* on R2 and on R3, both recoveries are run on the **same responses** — the
  structural recovery to its K and the prior-assisted recovery to its (smaller) K — and the
  prior-assisted Δ₂ must agree with the structural Δ₂ **per scored family within τ₇** (the same
  per-family RMS harmonic-frequency metric as Q7); the structural recovery's own Q8(a/b) on
  direct couplings must have passed at that rung; the direct couplings must agree with the
  prior-assisted blocks within η₈ (absolute form below); P3 must have shown a saving on the
  dry-run corpus **and its effect size on the PAH held-out tensors is reported beside it**.
  *Spending:* on R4–R6, a prior-assisted recovery may be the only full recovery, provided the
  licence was earned at **both** R2 and R3, the rung's direct-coupling probe agrees with the
  prior-assisted blocks within η₈, and the cost record says `prior = learned`. On a spent-licence
  rung the scored spectrum depends on the learned prior; the certificate says so, cites the two
  earning rungs, and carries the rung's direct-coupling agreement as its prior-independent number.
  No Q8(c) ratio or size sentence mixes priors.
- **[05] The fragment licence** (decision 1; Goal, "The goal binds"; Round-8 Pass B finding 4).
  Fragment probing may produce a rung's Δ₂ only when all of the following have printed:
  (a) Q8(a/b) on direct couplings at R2 and R3 for the scored families;
  (b) the **fragment-vs-whole comparison at R3** — coronene's Δ₂ recovered whole and recovered
  from capped fragments **at the smallest fragment radius r_f that passes**, agreeing per scored
  family within τ₇; r_f is printed against coronene's own radius, and if no r_f smaller than the
  molecule passes, that is printed as the result and part (b) has failed;
  (b′) the same comparison **on a molecule larger than coronene** (circumcoronene-class, R4),
  **promised conditional on B3 classification** of the whole-molecule batch, since it is the only
  comparison on a fragment that is not the whole molecule;
  (c) the **fragment-radius convergence test on the rung's own interior**: for the deck-chosen
  interior and edge pairs, the family-projected direct couplings (Q8(a) below) computed from
  fragments of radius r_f and r_f + one ring carved from the rung's own DFT geometry, agreeing
  within the absolute η₈; first instance on circumcoronene's central ring at R4, then on the R6
  flake; whole-flake direct couplings, where B3 allows, as the gold check.
  Families that fail any part are withdrawn from that rung's certificate with the measured share.
- **[05] Q8 has a fixed form** (Distilled Q8) and is computed on **directly measured
  couplings** wherever it decides anything: (a) the measured quantity per atom pair (A, B) and
  scored family F is the **family-projected coupling** ∂²ΔE/∂u_A∂u_B, u the family mode's local
  direction at each atom, by four-point mixed differences of ΔE at Cartesian step h (a deck
  number, of order 0.1 Å per atom; item 12) — **four energies per (pair, family)**; the full 3×3
  block only for the deck's near pair at each rung as a check. These couplings against
  interatomic distance are fitted to A·exp(−r/r_c) — r_c is a measured output — with the pass
  test that pairs beyond r_max carry no more than a fraction ε₈ of Σ(coupling²); at R0–R1 the
  couplings come from the reference Hessian, at R2–R3 from the prior-free direct probe; the
  recovered couplings are printed beside them. **Agreement metric (absolute form):** the
  disagreement |recovered − direct| is normalised by the rung's coupling scale
  S = √(Σ direct² / n_pairs), and a pair passes if it is ≤ η₈·S; a pair whose direct coupling is
  below 3σ_coupling (σ_coupling = σ_E·√(something like 4)/(4h²) per the four-point formula,
  printed) is reported **"at noise"** and enters the fit with its uncertainty, never as a
  pass/fail. A disagreement beyond η₈·S on a resolved pair is a Q7-class breach. (b) per scored
  family, the share of the family's Δ-shift carried by pairs beyond r_max is ≤ ε₈, computed with
  the direct far couplings substituted into the recovered Δ₂; (c) saturation, **same mode and
  same prior at both rungs, at the same ρ\* rule**: in mode E on K_off — K_off(R_{n+1}) ≤
  γ·K_off(R_n) for R1→R2 and R2→R3 — and in mode G on K over the rungs mode G ran. r_max, ε₈,
  η₈, γ and h are pilot-note item 12.
- **[05] Q6 has thresholds** (item 13), each a formula frozen now with its numbers filled at
  the pilot note, and **one estimator**: along each probe mode, ΔE(q) (mode E) or the
  gradient-difference component g(q) (mode G) is sampled at nine points on q ∈ [−1, 1] (spacing
  0.25) per freezing arm; **σ_E is the RMS residual of ΔE(q) about a least-squares polynomial of
  degree 4**, and **σ_g the RMS residual of g(q) about a polynomial of degree 3** — the per-point
  scatters the noise lines were derived for. The **mode-E noise line**: σ_E ≤ 0.82·τ·q_s²; the
  **mode-G noise line**: σ_g ≤ 2.8·τ·q_s; both evaluated for each grid step q_s ∈ {0.25, 0.5,
  1.0} from the one σ (the formula, not the data, supplies the q_s dependence), τ the smallest
  beat margin of item 2, all in one energy unit; measured along a C–C stretch, a C–H stretch, a
  CH-oop mode **and one totally symmetric mode** at R1 and at the R2-size family. The **bias
  line**: |Δ₂(frozen) − Δ₂(canonical)| ≤ τ per R0 mode in the same basis and, diagonal-only, per
  pyrene family mode. The **threshold line**: TightPNO−NormalPNO frequency delta ≤ τ, else CPS
  extrapolation is mandatory and every probe counts double in the classification rule.
- **[05] The cost-sentence rule of §1** binds every document.

## 4. Frozen at the pilot note (form fixed now, numbers then)

Written into a dated pilot note after (a) the **R0 pilot** — geometry, DFT Hessian, harmonic
bands, timings, the zero-CC dry run in both modes with its noise-injection column at R0 and at
the largest sizes the laptop affords, **no local-CC Δ₂ and no pipeline-vs-lab number** — (b) the
**scoreboard re-read probe** with M03's u_band table, (c) the canonical feasibility probe, (d)
the gradient run/no-run at equilibrium, (e) probe M1 and (f) the R1 smoothness probe's σ (fits
sealed). Committed **before any local-CC Δ₂ number is readable and before any pipeline-vs-lab
number exists for any molecule**. The 2026-09-04 decisions are recorded in it by reference.

1. The exact band list per molecule (uid / NIST CAS, window, class); every §3 family with lab
   data for a promised molecule must appear; per family: *gas-decidable / matrix-gated /
   inconclusive by construction*, with u_band.
2. The "beat" margin per family, from the lab and opponent side only; the list of promised
   families closed in the same note; and the **expected-effect line**: "the literature scale of
   Δ₂ at R1 is ≈ 5 cm⁻¹ mean absolute harmonic difference (item 45, **snippet grade**,
   verify-on-use); the P2 hypothesis is that the per-family scatter of Δ₂ exceeds the margin
   after the opponents' fitted factors absorb its mean; **the R2 C–C families are expected
   inconclusive by construction on the NIST gas scoreboard.**"
3. The P-gate numbers (0 imaginary frequencies tolerance; scale-factor policy: **none** on
   anharmonic output; a harmonic fallback declares its factor and fit set).
4. The **matrix shift tolerance** as measured by Module 03.
5. The **P3 effect size**: the reduction in K, or in ρ at fixed K, that the learned prior must
   deliver on the dry-run corpus to count; **reported on the PAH held-out tensors as well**.
6. The **M04 baseline recipe** (features, tuning budget, seeds).
7. **Resonance handling per rung** (carried): GVPT2 with named r₃/r₄ thresholds and a polyad
   cap; or MD-ACF on the defined DFT-plus-Δ potential (only if the deck names one); or
   CH-stretch unscored — with the **resonance-closed family set at closure depth one**, its size
   and Hessian count printed.
8. **[05] The stopping constant c** (ρ\* = c·ρ_noise; c ≥ 1) per mode, chosen from the
   noise-injected dry run's K-vs-σ curves, and the response type the residual is computed on
   in each mode (Distilled §3).
9. **[05] K_cap per rung and per mode (E and G)**, derived from the **noise-injected** dry-run K
   at that rung's molecule (or the largest dry-run size available), at the σ the R1 smoothness
   probe printed, by a factor stated in the note. Both are filled for every rung regardless of
   local-CC gradient availability; a mode-G cap is simply unused on a rung where mode G is not
   licensed.
10. **[05] The hold-out fraction f_h and the hold-out seed.**
11. **[05] The Q7 tolerance τ₇** (recovered vs reference Δ₂, prior-assisted vs structural Δ₂, and
    fragment vs whole Δ₂, as per-family RMS harmonic frequency difference, cm⁻¹), **no larger
    than the smallest beat margin of item 2**; and the **discriminability factor** d₇. No Q7
    result exists when they are written.
12. **[05] The Q8 numbers**: r_max, ε₈, η₈ (absolute form), γ, the Cartesian step h, and the
    direct-coupling pair list per rung (which atom pairs, at which distances; for R4 and R6,
    interior and edge pairs on the fragments).
13. **[05] The Q6 numbers**: τ inserted into the two noise lines, the bias line and the
    threshold formulas of §3 with the §3 estimator; the pattern amplitude q_s per mode chosen from
    the R1 smoothness grid; the CPS decision; the band width w and regularisation weights of the
    structural prior by the §3 rule.

## 5. Stop conditions and escalation (declared in advance)

1. **Probe M1 fails — no code can freeze spaces at the anchor level — or the anchor code is
   otherwise unavailable, or the B2 laptop underperforms:** the rung stops; the missing binary,
   option or measurement is named. Do not substitute a different level, or unfrozen spaces, and
   keep the rung's name.
2. **A rung crosses a machine checkpoint:** a dated decision note is mandatory — continue
   knowingly, reroute to B3, or stop. Silent overrun is forbidden, and so is ducking under a
   checkpoint by coarsening the basis, loosening thresholds, dropping CPS once mandatory,
   raising c, raising K_cap, enlarging q_s beyond the Q6 line, or dropping patterns. **Human
   hours are never a stop condition.**
3. **Cluster or rented-GPU access not formalised when first needed:** reach rungs stop and the
   stop is reported.
4. **A licence probe breaches its frozen threshold** — Q6 (noise line of the mode used at the
   rung's size class; bias line; threshold line without CPS), **Q7** (Δ₂ outside τ₇, or the
   discriminability clause failed, or the shuffled-probe null passed, or recovered and direct
   couplings disagree beyond η₈·S on a resolved pair), **Q8(a/b)** on direct couplings (no
   locality, or a family's correction carried by long-range pairs), **Q8(c)** (no saturation),
   the **learned-prior licence** (prior-assisted vs structural beyond τ₇), the **fragment
   licence** (any of (a), (b), (b′), (c)), or **ρ not reaching ρ\* by K_cap**: a measured result,
   reported as such. Q6-noise breach at a size class: that mode carries no "beat" language
   there; the rung continues as a cost record and, if the other mode or CPS is licensed, under
   that. Q6-bias or Q7 or K_cap breach: Δ₂ does not enter a scored spectrum on the affected
   families at that rung; the pre-declared fallback is **DFT harmonic + DFT anharmonic, with Δ₂
   applied only on families where Q7 passed, labelled per family** — it competes under the same
   protocol and may lose. Q8(a/b) or fragment-licence breach on a family: that family's Δ₂ is
   reported with its long-range share and carries no accuracy claim finer than that share; at R6
   the family is withdrawn from the certificate. Learned-prior licence breach at R2 or R3: the
   prior is not spent on any rung. **Q8(c) breach: no size sentence** — the plan does not fall
   back to a point factory whose affordability no plan has measured.
5. **A promised accuracy rung loses to a line:** published with the paired table.

## 6. What this ladder refuses (carried, with additions)

- No global QFF of a huge molecule as a deliverable.
- No whole-molecule "gold rung" language above R1; anchors are "local-CC, R1-checked".
- No motif-transfer claim: every molecule gets its own probed Δ₂ — or, at R6, a
  fragment-probed Δ₂ under the fragment licence, labelled as such (a method decided by
  measurement, not a transfer of spectra). **[05]** The learned prior is not a transfer claim:
  it earns a per-rung licence against the structural recovery on the same data, and on spent
  rungs the certificate names it.
- No CC correction to anharmonic constants as a promise; no "coupled-cluster anharmonic"
  language; no "coupled-cluster quality" as an accuracy adjective.
- No editing this ladder after a rung it governs has been scored, except by dated deviation
  note committed before the affected number is known.
- **[05]** No cost sentence outside the two forms of §1; no K written before it is measured;
  no Q8 ratio across mixed modes or mixed priors; no Q8 verdict computed on recovered couplings
  alone above R1; no "beat" from a mode whose noise line did not pass; no decidability verdict
  from a point spacing.
