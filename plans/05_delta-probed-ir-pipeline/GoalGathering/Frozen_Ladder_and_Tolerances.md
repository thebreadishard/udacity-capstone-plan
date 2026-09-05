# Frozen ladder and tolerances — Plan 05

**Status.** Frozen 2026-09-03 in *form*; revised the same day after Round-7 Pass A and Pass B;
amended 2026-09-04 by the user's decisions and revised the same day after Round-8 Pass A and
Pass B, Round-9 Pass A and Pass B, and Round-10 Pass A and Pass B; seam check of the Round-10 Pass B
patch 2026-09-04. **Frozen text as of 2026-09-04 (after review rounds 7–10 and the seam check of the Round-10 Pass B patch).** From here on this file changes only by a dated note that names the finding or measurement behind the change; the Ladder is the single binding statement of every rule, and other files cite it rather than restate it. Carried from plan 04 with the plan-05 additions marked **[05]**; the
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
    ran, **one per mode that ran on the rung**: `K = n energies|gradients (mode E: of which 2M = … in the single-mode ± block, K_off = …
    energies (… ± pairs of off-diagonal patterns); K_off at the common threshold ρ*_common = …,
    NOT_RUN until the Q8(c) probe re-prints the record with both neighbours' values) at rung R,
    mode E|G, prior = structural|learned, σ = …, c₀ = …, q₂ block = 2·M_scored energies
    (outside K), RMS_resp = …, ρ_noise = …, c = …, ρ* = …,
    ρ(K) = …, PNO extrapolation = none|CPS, wall-clock w per probe on machine m, printed by
    probes/<file>`. Nothing else about
    cost may be written.
  - **The size sentence** — numeric only, in one of two forms, each allowed only after Q8(c)
    has passed for that quantity at R1→R2 and R2→R3 with the structural prior, both counts read
    from the rungs' stored ρ(n) curves at the **common threshold** ρ\*_common =
    max(ρ\*(R_n), ρ\*(R_{n+1})) (§3 Q8c; ρ\* is rung-dependent, so the record K_off alone would
    report threshold drift as a property of Δ₂): *mode-E form* (always earnable, because mode E runs on every rung R1–R3 that runs):
    "K_off went n₁ → n₂ → n₃ from R1 to R3 while the mode count went M₁ → M₂ → M₃"; *mode-G
    form* (only if mode G was licensed and ran on R1, R2 **and** R3 — side-project milestones M3,
    M4, M5 with both checks each — expected B3-conditional, since M4 and M5 are B3 by the side
    project's own sizing): the same for K. The adjectives "size-independent", "O(1)",
    "saturates", "does not grow", with or without "-class", are forbidden everywhere, including
    the Module 08 paper.
  - **"Beat" and noise.** A rung carries "beat" language only if the Q6 noise line **of the
    mode that produced its scored Δ₂** (σ_E line for mode E, σ_g line for mode G; §3) passed at
    that rung's size class; otherwise it carries a cost record and no "beat".

## 2. The ladder (rungs and species carried from plan 04; R2 re-read, see the dated note)

| Rung | Molecule(s) | Type | Why this rung | Opponents | Lab scoreboard | **[05] what it licenses** |
|---|---|---|---|---|---|---|
| **R0** | benzene C₆H₆ (12 atoms, 30 modes) | A | End-to-end laptop pilot; canonical CCSD(T) **expected** affordable in the anchor basis — plan-02 measured 19.6 s/point at 6-31G* and a failure at ~114 functions with 28 GB on the old machine, provenance only — **measured by the one-point canonical feasibility probe before the pilot note** (§3; Budget §4) | A, B | NIST gas — **cell spectra with stated resolution exist** (the NIST Quantitative IR series, twenty entries at 0.125–1.93 cm⁻¹, and a Coblentz 2 cm⁻¹ gas spectrum at 600 mmHg; WebBook list opened 2026-09-04 by the Round-9 reviewer and the author, item 54; no record states a temperature, so it is read from the series' documentation, item 56); the entry scored is named in the pilot note; PAHdb experimental | **Q7 probing licence for Δ₂** against the frozen-space local-CC reference *and* the canonical reference — **the canonical arm is the only one that licenses the space freezing** (Q6 bias), so its feasibility is measured first; Q8(a/b) on the reference Hessian as Q7's sub-item (iv); the zero-CC dry run in both modes with its noise-injection column; probe M1's continuity diagnostics; side-project M2 (after the pilot note) |
| **R1** | naphthalene C₁₀H₈ (18 atoms, 48 modes) | A | The canonical-vs-local-CC licence molecule, conditional exactly as in plan 04: the first R1 probe measures whether canonical (T) runs on the B2 laptop at any usable basis; if not, the canonical arm at R1 is absent, Q7 at R1 tests the recovery and not the freezing (that sentence printed with the result), and the freezing licence rests on R0 alone, in the basis the feasibility probe allowed (cc-pVTZ, or cc-pVDZ with both arms in that basis) — stated in every anchor claim | A, B | **Room-temperature gas spectrum exists outside the WebBook**: the PNNL/NWIR quantitative vapour-phase database entry (25 °C, 0.1 cm⁻¹, 760 Torr N₂; items 57 and 59, named here before M03 prints anything, as the no-swap rule requires) — R1 is **expected unconditional on it**; the WebBook's hot sources (a Coblentz vapour spectrum at 245 °C, 4 cm⁻¹, and a NIST MS Data Center GC-IRD entry; item 55) are scored as labelled hot columns beside it; Pirali 2009 (item 53) is a room-temperature high-resolution cell source for the CH-oop family as well as the hot-band pin; PAHdb experimental | **The Q6 smoothness probe** (four modes — a C–C stretch, a C–H stretch, a CH-oop mode and one totally symmetric mode — nine points each, both freezing arms, 72 energies; the σ_E estimator of §3; σ_E printed before the pilot note, fit coefficients sealed); Q6 anchor licence; Q7 at a second size, printed for diagonal-only and full recovery; first Q8(a/b) rung read (on the reference Hessian); expected-effect line printed; side-project M3 (after the note) |
| **R2** | pyrene C₁₆H₁₀ (26 atoms, 72 modes); chrysene C₁₈H₁₂; triphenylene C₁₈H₁₂; tetracene C₁₈H₁₂ (each 30 atoms, 84 modes) | A | First territory beyond PAHdb's anharmonic front | A, B | **Gas (NIST WebBook / NIST-EPA gas-phase IR database, GC-IRD hot-vapour spectra; JCAMP `DELTAX` 4 cm⁻¹, stated resolution 8 cm⁻¹ at snippet grade, no concentration):** pyrene, chrysene, triphenylene — **decidable per family only by the measured band-centre uncertainty rule below; the C–C families are expected inconclusive by construction on this source.** **Matrix (PAHdb experimental uids 334, 282, 291 as recorded in plan-02 probes):** pyrene, tetracene, chrysene. Tetracene has no room-temperature gas-phase IR; it is scored on matrix data (every family M03-gated) and on a **labelled cold column** from a jet-cooled 5–18 µm band list (item 61; dated note of 2026-09-05 below) under the u_band rule. IRMPD = context only | Q6 at R2 size: the **canonical diagonal check at pyrene** (two energies per mode, one mode per family) and the TightPNO/NormalPNO column; the Q6 noise grid at R2 size in the mode(s) used; **prior-free direct-coupling probe** for Q8(a/b); mode E runs; K and K_off printed; Q8(c) first ratio (R1→R2); **the learned prior's licence is earned here** (§3); side-project M4 |
| **R3** | coronene C₂₄H₁₂ (36 atoms, 102 modes) | A | Mulas 2018's molecule (B97-1 QFF, item 6); largest PAH with a usable matrix spectrum (uid 18); no gas-phase IR in the WebBook, but five jet-cooled 6–15 µm bands exist (item 62; dated note of 2026-09-05) and are scored as a labelled cold column under u_band | A, B (Mulas), C | PAHdb experimental (uid 18), every family M03-gated | direct-coupling probe; mode E runs (mode G in addition if M5 licensed it); Q8(c) second ratio (R2→R3); the size sentence is decided here; **the fragment-vs-whole comparison at the smallest passing radius** (fragment licence part b); the learned prior's licence earned here too; side-project M5 (both checks at coronene) |
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
0 K prediction" **with a floor written now**: for a source above room temperature u_T ≥
χ_max·(T_source − 296 K) + u_296, for a room-temperature source u_T ≥ u_296, where u_296 is the
0 → 296 K shift term per molecule — 1 cm⁻¹ at benzene, 3 cm⁻¹ at naphthalene, 5 cm⁻¹ at the R2
species (recalled estimates scaling with the thermal vibrational energy; replaced on fetch of
items 52–53 by the pinned paper's room-temperature number) — with χ_max =
0.03 cm⁻¹ K⁻¹ (recalled order of PAH hot-band shift rates; replaced by the pinned reference's
table on fetch — items 52–53) (the linear-from-296 K form is conservative: measured low-temperature slopes are smaller, not
larger — Chakraborty et al. 2021, item 60). **A source whose record states no
temperature takes it from its series' documentation** (for the NIST Quantitative IR series,
item 56, read by M03 before u_band is printed); a source with neither is treated as hot, at
the GC-IRD default and T_source the source's stated temperature (245 °C for the
Coblentz naphthalene vapour entry; the SRD 35 lightpipe temperature once item 50's PDF is read,
until then 250 °C, labelled recalled). A pinned per-family **correction** χ_F·(T_source − 296 K)
from items 52–53 may replace the floor, carrying ±30 % of the correction plus the temperature
uncertainty as u_T; if that brings a C–C family under its margin it is decidable, and the pilot
note says so with the citation) — is smaller than the family's beat margin. M03 prints, per
spectrum, the source class (cell / vapour cell / GC-IRD), the stated temperature and the stated
resolution as columns. M03
prints u_band and the verdict per molecule and family **before the pilot note**; the pilot note's
item 1 records per family *gas-decidable / matrix-gated / inconclusive by construction*. A family
with matrix data only passes through the **M03 matrix–gas gate**: if the M03-measured
|matrix−gas| delta for that family is not smaller than its beat margin, it is scored
**"pre-declared inconclusive on matrix"** — not "beat", not "lost". R0–R1 are gas-scored
throughout against NIST spectra whose u_band M03 measures the same way. **R0 is expected unconditional**:
cell spectra with stated resolution exist (the NIST Quantitative IR series, twenty entries at
0.125–1.93 cm⁻¹; the WebBook records state no temperature, so the measurement temperature is
read from the series' documentation, item 56, before the note; the entry scored is named in the
pilot note). **R1 is scored under the same rule** and is **expected unconditional
too**: the WebBook's naphthalene gas spectra are hot (a 245 °C Coblentz vapour spectrum and a
GC-IRD entry; at χ_max the unpinned floor there is ≈ 7–8 cm⁻¹, above τ), but a room-temperature
quantitative vapour-phase spectrum at 0.1 cm⁻¹ exists in the PNNL/NWIR database (items 57, 59 —
found by the Round-10 reviewer, named here before M03 prints u_band, as the no-swap rule
requires); on it u_band(R1) ≈ √(0.1² + centroid² + u_296²) is expected below τ for every family.
The hot WebBook entries are scored as labelled hot columns; items 52–53 remain the first paid
debt because they pin the hot columns and u_296. No matrix gate applies on R0–R1.

**Dated note 2026-09-05 (R2/R3 gas-phase sources; permitted change under the freeze — names its
finding).** An exhaustive web search on 2026-09-05
([Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md](Research_Note_2026-09-05_R2_GasPhase_MidIR_Sources.md);
27 queries, 15 DOIs Crossref-verified) found **no room-temperature gas-phase 6–15 µm spectrum for
pyrene, chrysene, triphenylene, tetracene or coronene**. It did find three cold or partial sources,
added here as **labelled cold columns** scored under the u_band rule like every other source:
(i) **tetracene**, jet-cooled IR-UV ion-dip, 5–18 µm, ≈ 30 tabulated band centres (item 61) —
its resolution term is the free-electron-laser bandwidth (≈ 1 % of the frequency, 7–15 cm⁻¹
across the window), so its C–C families are **expected inconclusive by construction** unless the
source states a narrower width; (ii) **coronene**, jet-cooled at T_rot ≈ 2 K, five tabulated
6–15 µm bands (item 62), same bandwidth caveat — the first gas-phase datum for R3;
(iii) **pyrene**, one rotationally resolved band near 8.5 µm (item 63): a single cold band origin,
usable as a one-line check, not a scoreboard. The hot heat-pipe spectra of Joblin et al. 1994/1995
(items 52 and 64) remain the source of temperature coefficients. Consequence: the expected
verdict for the R2 C–C families is unchanged (inconclusive by construction on the existing data);
the supervisor ask (Proposal §13.3) stands and is now known to have no public answer; tetracene
and coronene gain a cold column whose decidability u_band decides, not this note.

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
  in the same basis. **The canonical feasibility probe** (Budget §4.1b) prints one canonical
  CCSD(T) energy of benzene at cc-pVTZ on the B2 laptop and extrapolates its wall-clock and peak
  memory to **two counts** — and, where the code has it, also runs **one canonical CCSD(T)
  gradient** of benzene (PySCF ships `pyscf/grad/ccsd_t.py`; directory listing fetched
  2026-09-04 by the reviewer and the author), so the gradient-to-energy factor is measured, not
  typed; only the count factors are deck numbers —: the Q6 bias
  line (61 = 1 + 2·30 energies — the diagonal along benzene's 30 modes) and the full canonical
  reference Hessian that Q7(i) and Q7(iv) consume (72 = 2·36 canonical CCSD(T) gradients, ± along
  the Cartesian coordinates if the chosen code has
  them, printed; else 1,801 = 1 + 2·30 + 4·C(30,2) energies by central mixed differences in the modes). **"Fits"** means extrapolated
  wall-clock ≤ the 168 h checkpoint **and** peak memory ≤ 31.3 GB, per object. If the bias line
  does not fit at cc-pVTZ it is measured in the largest basis that does (cc-pVDZ) with the frozen
  arm re-run in that basis, labelled, or is the first B3 request; if only the bias line fits,
  Q7(i) at R0 compares to the local-CC reference only, Q7(iv) reads the reference Hessian from
  the local-CC arm, and the full canonical Hessian is the first B3 request — that sentence is
  printed with the R0 result and a dated note says which. The **expected** printout, written now
  so it is not a contingency: the bias line fits and the full reference does not. A bias line
  measured in cc-pVDZ is a **lower bound** on the cc-pVTZ freezing bias (the bias scales with the
  LNO truncation error, which is larger at TZ); the TZ arm's freezing then stays unlicensed, and
  "beat" language from the TZ arm requires the DZ bias ≤ τ/2.
- **[05] The promised correction is Δ₂ only.** No CC correction to cubic or quartic constants
  is promised; the diagonal-cubic probe is a bonus number. DFT anharmonic constants are computed
  for a family set closed under the resonance search **to closure depth one** (a scored family
  mode's partners; the partners' own diagonal anharmonicity from their 1-D cut only), bounded by
  the polyad cap; the pilot note prints the closed set's size and Hessian count per rung.
- **[05] K is a measurement, not a choice — with a noise-aware stopping rule.** **Every pattern
  p enters the Q0 deck as the pair ±p, and the mode-E response is the symmetric combination**
  R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) = ½ pᵀΔ₂ p + O(p⁴): the first-order term Δ₁·p — the CC−DFT
  force at the DFT geometry, which is not zero and, by the Round-9 reviewer's recalled order of magnitude, several
  times the Δ₂ signal per bond at q_s = 1 (the R_a by-product measures it) — and the cubic term cancel exactly. The antisymmetric
  combination R_a(p) = ½[ΔE(+p) − ΔE(−p)] = Δ₁·p + O(p³) gives Δ₁ from the single-mode block
  and φ_iii from the second amplitude. **Δ₁ is load-bearing, not a by-product** (Round-10 Pass B
  finding 3): the recovered Δ₂ is the Hessian correction at the DFT minimum, and the corrected
  surface's own minimum lies at δq_j = −Δ₁,j/(ω_j + Δ₂,jj) along the totally symmetric modes; the
  harmonic constants there differ by Σ_j φ_iij δq_j, a per-band shift ≈ ½ Σ_j φ_iij^DFT δq_j of
  recalled order 0.5–2 cm⁻¹. **Rule:** the scored harmonic part is Δ₂ + Σ_j φ_iij^DFT δq_j — the
  first-order corrected-surface-minimum term, with φ_iij from the DFT cubic set (which therefore
  includes the totally symmetric modes; item 7) and δq_j from Δ₁ — printed per band in the error
  budget with Δ₁ per totally symmetric mode; **no atom is moved and no geometry is
  re-optimised**; the Δ = 0 null arm and the Q7 comparison (recovered vs reference Δ₂ at the DFT
  geometry) are unaffected. The mode-G
  response ∇ΔE(p) − ∇ΔE(0) removes Δ₁ by construction. **K counts energies in mode E (a ± pair
  counts 2) and gradients in mode G**; **ΔE(0) is one shared reference energy per rung**, computed once; its error c₀ is a common
  offset to every R_s, not per-pattern scatter. At a single pattern amplitude that offset is
  **collinear with a uniform shift of every diagonal element** (½ pᵀ(Δ₂ + λI)p = ½ pᵀΔ₂p +
  ½ λ q_s²), so no fitted constant can separate them and an unhandled c₀ would shift every
  recovered frequency by c₀/q_s² with the same sign (5 µE_h → 1.1 cm⁻¹; Round-10 Pass B
  finding 2). **It is identified, not fitted:** on every scored family's mode the single-mode
  block carries R_s at two amplitudes, q_s and q₂ (the two extra energies of the diagonal-cubic
  bonus, now mandatory on the scored modes), so Δ₂,ii = 2[R_s(q₂) − R_s(q_s)]/(q₂² − q_s²) is
  c₀-free and c₀ = R_s(q_s) − ½Δ₂,ii q_s² is over-determined across those modes; its mean is
  subtracted from every response before the recovery and printed in the cost record beside σ.
  **Counting:** the q₂ energies (two per scored mode, 2·M_scored in all) are **outside K**: K
  counts the ±q_s single-mode block (2M) and the off-diagonal pairs (K_off), so K = 2M + K_off
  stands; the q₂ block is its own line in the cost record and does not enter Q8(c).
  The same two-amplitude read removes the quartic contamination Δ₄,iiii q_s²/12 on the scored
  modes exactly; on the multi-atom patterns that term is a labelled bias of order 0.1–1 cm⁻¹
  (recalled scales), printed after the note from the sealed degree-4 fits. The per-response scatter is therefore **σ(R_s) = σ_E/√2** (the two displaced
  energies), and ρ, RMS_resp and ρ_noise are defined on R_s with that σ: ρ_noise = σ(R_s)/RMS_resp
  and the χ² clause below uses σ(R_s). (The √6 in the Q6 noise-line derivation treats E₀ as an
  independent noisy point; that is the conservative convention for the threshold and is kept as
  such — it is not the response σ.) Patterns are consumed in the hashed order of the Q0 deck,
  pairs together, and **ρ(n) is evaluated after each complete pair, n counted in energies**. At
  each count n the held-out residual ρ(n)
  (Distilled §3) is computed together with its **noise floor** ρ_noise(rung, mode) =
  σ_resp(mode, size)/RMS_resp(rung), where σ_resp is σ(R_s) = σ_E/√2 in mode E and σ_g in mode G, with σ_E, σ_g the pooled per-arm scatters of the §3 estimator
  from the **largest Q6 noise measurement at or below the rung's size that exists before the
  rung's first probe** (the R1 smoothness probe's σ for R0–R1; the R2-size measurement for R2
  and above; which one, printed in the cost record) and RMS_resp the RMS of the rung's own
  held-out responses. **K is the smallest n at which ρ(n) ≤ ρ\* with ρ\* = c·ρ_noise**, c ≥ 1
  the pilot-note constant of item 8; equivalently, the held-out χ² per response with σ(R_s) (mode E) or σ_g (mode G) as the
  per-response sigma first falls to c². **Two guards close the rule.** (i) **Floor:** the trivial
  recovery Δ₂ ≡ 0 has ρ = 1 at every n, so the rule is evaluated only when ρ\* < ρ_max = 0.5 (a
  frozen number: a recovery at ρ = 0.5 explains three quarters of the held-out response
  variance); if c·ρ_noise ≥ 0.5, the rung's responses in that mode are **"at noise"**, K reads
  NOT_RUN(at noise), no Δ₂ is recovered in that mode, and the Distilled §8 sentence is written.
  (ii) **Minimum count:** in mode E the Q0 deck's first block is the **2M single-mode patterns**
  (±q_s along each DFT mode — the CMA-0 block), consumed before any multi-atom pattern, and the
  rule is evaluated only for n > 2M, so K_off = K − 2M ≥ 2 (one ± pair); in mode G there is no diagonal block
  (M single-mode gradients would already be a full Hessian, which mode G exists to avoid) and
  the rule is evaluated only for n ≥ n_min(G), a count frozen in item 9 beside K_cap(G) from the
  noise-injected gradient-mode dry run. K is never written down before the rung runs. The pilot
  note freezes a **cap K_cap** per rung and per mode (item 9) from the **noise-injected** dry run
  (Distilled §3, Budget §4.1) — never from the noiseless one. If ρ has not reached ρ\* by K_cap,
  the rung's Δ₂ is "not recovered at cap" (§5.4), and the cap is never raised to rescue it. The
  cost record carries σ, RMS_resp, ρ_noise, c and ρ(K) beside K, so a small K on a rung with
  small responses reads as what it is.
- **[05] Hold-out membership is decided before any response exists:** by a seeded rule in the
  Q0 deck (deck seed + pair index: **one deck index per pair ±p, and the pair is the hold-out
  unit** — a pair is never split between hold-out and training), fraction f_h (item 10).
- **[05] Frozen spaces — the object, written once.** At the reference geometry the local-CC code
  stores the localized occupied orbitals and each fragment's LNO (or PNO) vectors in the AO
  basis. At a displaced geometry **both halves are transported by projection, and nothing is
  re-localised or assigned**: the occupied set is C_occ(x) = Löwdin[P_occ(x) C_occ(0)], P_occ(x)
  the projector onto the displaced geometry's occupied space (no localiser runs at a displaced
  geometry, so no assignment exists and no permutation can switch — Round-9 Pass B finding 2:
  π localisation on the D₆h rungs is soft, and re-localise-and-assign would mix, not switch); the
  stored virtual-space vectors are likewise **projected onto the new geometry's virtual space and
  Löwdin-orthonormalised**; that projected, orthonormalised pair of sets is "the frozen space",
  and the correlation energy is evaluated in it. The map is analytic while the overlaps are
  nonsingular (for |q| ≤ 1 the smallest singular value is 1 − O(q²)); for mode G the projection is
  **inside the differentiated graph** for both halves. **The three arms, written once:** **A** =
  frozen–frozen (the probe object: transported occupied set and transported LNO spaces); **B** =
  transported occupied set with fresh LNO spaces built on it (the released code as is, with the
  transported set passed as its localized-orbital input — the pyscf-forge LNO class takes the
  localized occupied orbitals as an input and rebuilds the LNO spaces on every call, item 48), so
  E(A) − E(B) is the virtual-freezing bias in isolation; **C** = fresh localiser and fresh LNO
  spaces (the production energy; on the D₆h rungs it carries the localiser's landing). **Arm A
  needs one small override of the LNO-space construction to accept the stored, transported
  vectors** — a subclass whose commit hash the deck pins. Q6's "without frozen spaces" arm is
  **B**, never C, so localiser arbitrariness is not attributed to freezing; M1 prints all three. Every local-CC probe
  evaluation at a displaced geometry uses frozen spaces so defined. **Probe M1** tests that the
  candidate code (the pyscf-forge LNO code, item 48) can do this and prints, along one totally
  symmetric, one degenerate and one non-symmetric benzene mode, per point: the **continuity
  diagnostics** — the smallest singular value of the occupied overlap S_oo(x) = C_occ(0)ᵀ S(x)
  C_occ(x) and the largest off-diagonal of the pre-Löwdin overlap, for both halves — and
  E(A) − E(B) and E(A) − E(C); for arm C also the localiser's functional value and its overlap
  with the transported set, so the localiser's landing arbitrariness is
  visible in the "fresh" column and not attributed to freezing. All without a verdict. **M1's raw
  displaced energies are not printed**: they go to the same hashed, sealed file as the R1 fit
  coefficients (they would otherwise make three benzene Δ₂,ii readable before the note). A code that cannot
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
- **[05] Pattern amplitudes come from the Q6 step grid**: the largest step at which the
  smoothness probe's σ is under the noise line of the mode used; never chosen to make a recovery
  converge. Stated plainly: with **one pooled σ per arm** (Q6 bullet) and a line that rises with
  q_s, q_s = 1.0 passes whenever any grid step does, so the grid is a single test at q_s = 1.0 and
  the three lines are printed for the record; **the pooled σ gates**: if it fails at q_s = 1.0,
  Q6 fails for that mode (E or G) at that size class (Distilled §8 sentence) and is not rescued by
  a smaller step. The per-vibrational-mode σ's are informational, printed beside the pooled
  value, with one flag rule: a per-mode σ above twice the pooled σ is flagged in the pilot note
  as a candidate non-smooth mode and its family carries that flag on the scoreboard (under
  homogeneity the flag fires falsely ≈ 0.3 % of the time, P(χ²₄ > 16); the worst Cartesian case,
  the C–H stretch, is one of the four). q_s is one
  number per rung and per mode E/G.
- **[05] Probe patterns are hashed** in the Q0 deck before the first probe runs; off-diagonal
  blocks the dry run flags as large receive explicit two-mode patterns in that deck; adding,
  removing or re-weighting patterns after any residual is known is a Distilled §4 deviation.
- **[05] Order of the pilot inputs, and what they may not contain.** The pilot note is written
  with: the lab side (including M03's u_band table); the opponent side; the **zero-CC dry run**
  (both modes, with its noise-injection column); probe M1's printout (its raw displaced energies
  sealed with the R1 fit coefficients; only the difference column and the continuity diagnostics
  are printed); the **canonical feasibility
  probe** (one canonical CCSD(T) energy of benzene in the anchor basis on the B2 laptop:
  wall-clock, peak memory, extrapolated to the Hessian count); the gradient-availability probe
  **as a run/no-run at the equilibrium geometry only**; the **R1 smoothness probe's σ only** — its
  script prints σ_E per mode and per freezing arm (no σ_g exists before the note; item 8 says
  what mode G's constants are read at) and writes the
  fitted polynomial coefficients (which contain the diagonal Δ₂ elements) to a hashed, sealed file
  that is opened only after the note is committed; and single-point timings (Δ₁ at equilibrium is
  readable from the run/no-run gradients and is not a pilot-note input). **No local-CC Δ₂
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
  structural recovery to its K_struct and the prior-assisted recovery to its K_prior, with
  **K_prior < K_struct required** at both rungs (a prior that saves nothing on real responses
  earns nothing) — and the
  prior-assisted Δ₂ must agree with the structural Δ₂ **per scored family within τ₇** (the same
  per-family RMS harmonic-frequency metric as Q7); the structural recovery's own Q8(a/b) on
  direct couplings must have passed at that rung; the direct couplings must agree with the
  prior-assisted blocks within η₈ (absolute form below); P3 must have shown a saving on the
  dry-run corpus **and its effect size on the PAH held-out tensors is reported beside it**
  (informational, not gated: the licence is earned on the probed PAHs themselves, not on the
  corpus).
  *Spending:* on R4–R6, a prior-assisted recovery may be the only full recovery, provided the
  licence was earned at **both** R2 and R3, the rung's direct-coupling probe agrees with the
  prior-assisted blocks within η₈, and the cost record says `prior = learned`. On a spent-licence
  rung the scored spectrum depends on the learned prior; the certificate says so, cites the two
  earning rungs, and carries the rung's direct-coupling agreement as its prior-independent number.
  No Q8(c) ratio or size sentence mixes priors.
- **[05] The fragment licence** (decision 1; Goal, "The goal binds"; Round-8 Pass B finding 4).
  Fragment probing may produce a rung's Δ₂ only when all of the following have **passed** (for
  (b): passed, or its pending state resolved by a passing (b′)):
  (a) Q8(a/b) on direct couplings at R2 and R3 for the scored families;
  (b) the **fragment-vs-whole comparison at R3** — coronene's Δ₂ recovered whole and recovered
  from capped fragments, agreeing per scored family within τ₇. **The fragment, written once:**
  ring-closed, hydrogen-capped, carved **unrelaxed** from the rung's DFT geometry, its radius
  counted in ring shells around the pair or region it serves, in the rung's deck basis. At
  coronene, **by the shell rule**, the fragments containing an interior pair are exactly two — the
  central ring (one shell) and the whole molecule (the central ring plus one, two or three
  peripheral rings are ring-closed pieces but not shells) — so (b) is **one comparison at one shell for interior
  pairs** (edge pairs use the ring-closed three- to five-ring pieces), not a scan; **(b) is scored
  per family on the pairs that carry ≥ (1 − ε₈) of that family's Δ-shift** (Q8(b)'s own share):
  the interior pairs for the C–C families, the edge pieces for the C–H and CH-oop families (the
  central ring has no hydrogen, so interior pairs carry no CH-family shift and would agree
  trivially); r_f = one shell
  if it passes. If one shell fails, the two-shell hypothesis is **untestable at coronene** and the
  licence is **pending (b′)** — earned only if (b′) passes at two shells on circumcoronene, not
  earned otherwise; that is printed as the result, never "failed" (no two-shell whole-molecule
  test smaller than circumcoronene exists: the two-shell fragment around a ring *is*
  circumcoronene, around a bond ovalene); **(c)'s R4 instance may run under a pending licence**
  — fragments only, laptop work by expectation — and is printed, but it does not resolve the
  pending state; only (b′) does;
  (b′) the same comparison **on a molecule larger than coronene** (circumcoronene-class, R4),
  **promised conditional on B3 classification** of the whole-molecule batch, since it is the only
  comparison on a fragment that is not the whole molecule and the only test of two shells;
  (c) the **fragment-radius convergence test on the rung's own interior**: for the deck-chosen
  interior and edge pairs, the family-projected direct couplings (Q8(a) below) computed from
  fragments of r_f and r_f + one shell carved from the rung's own DFT geometry, agreeing within
  the absolute η₈; first instance on circumcoronene's central ring at R4, then on the R6 flake;
  whole-flake direct couplings, where B3 allows, as the gold check. **(c) is a probe batch like
  any other**: its energy count is printed (three pairs per class × three classes × the scored families ×
  four energies × two radii = 72 × families; ≈ 360 for five families, at R6 on coronene- and
  circumcoronene-size fragments if r_f = two shells) and it is classified by Budget §2's rule;
  the expectation, not a verdict: laptop work at one shell, B3 at two. **Which r_f:** (c) uses the R3 value from (b); if (b′) ran and
  its smallest passing radius is larger, that larger value; (c) is run once at (r_f, r_f + one
  shell) and is not re-run at a larger radius without a dated note before the second run; the R6
  fragment probe uses the radius at which (c) passed on the R6 flake, printed in the certificate.
  If neither (b) nor (b′) found a passing radius smaller than its molecule, the licence is not
  earned and R6 is not fragment-probed (Distilled §8, all-families refusal).
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
  disagreement |recovered − direct| is normalised by the coupling scale of the pair's
  **distance class**: the deck's pair list has three classes by bond count — **near** = bonded, **mid** = two or three bonds apart, **far** =
  four or more — with an **equal frozen count per class** (item 12; at least three pairs per
  class); the probe prints S_class, n_class, σ_coupling and the class windows, S_class =
  √(Σ_class direct² / n_class), and a pair passes if it is ≤ η₈·S_class ("η₈·S" anywhere in this
  plan means η₈·S_class; the mid class is the one the test is meant to bite on, and a near pair
  cannot carry a mid pair). A pair whose direct coupling is below 3σ_coupling is reported **"at
  noise"** and enters the fit with its uncertainty, never as a pass/fail, where **σ_coupling =
  σ_E/(2h²)**: the four-point mixed difference [ΔE(+,+) − ΔE(+,−) − ΔE(−,+) + ΔE(−,−)]/(4h²)
  with independent per-point scatter σ_E has standard deviation σ_E·√4/(4h²) — printed. A
  disagreement beyond η₈·S_class on a resolved pair is a Q7-class breach. (b) per scored
  family, the share of the family's Δ-shift carried by pairs beyond r_max is ≤ ε₈, computed with
  the direct far couplings substituted into the recovered Δ₂; (c) saturation, **same mode and
  same prior at both rungs, both counts read from the rungs' stored ρ(n) curves at the common
  threshold ρ\*_common = max(ρ\*(R_n), ρ\*(R_{n+1}))** — both rungs reached it, since each reached
  its own ρ\* ≤ ρ\*_common; the record K and the common-threshold K are both printed and Q8(c)
  uses the latter, and the ratio is also printed at a frozen reference ρ_ref = 0.3 wherever
  both stored curves reach it, informational: in mode E on K_off — K_off(R_{n+1}) ≤
  γ·K_off(R_n) for R1→R2 and R2→R3 — and in mode G on K over the rungs mode G ran. r_max, ε₈,
  η₈, γ and h are pilot-note item 12.
- **[05] Q6 has thresholds** (item 13), each a formula frozen now with its numbers filled at
  the pilot note, and **one estimator**: along each probe mode, ΔE(q) (mode E) or the
  gradient-difference component g(q) (mode G) is sampled at nine points on q ∈ [−1, 1] (spacing
  0.25) per freezing arm — arms A and B of the §3 object; **σ_E = √(SSR/(n − p))** of ΔE(q) about a least-squares polynomial of degree 4 (n = 9 points,
  p = 5 coefficients, ν = 4 per mode — never √(SSR/n), which under-reads σ by √(4/9)); **σ_g
  likewise about a polynomial of degree 3 (p = 4)**, with g(q) = ∇ΔE·∂x/∂q the gradient component
  along the same dimensionless q, and **pooled over all 3N Cartesian components** (each fitted to
  its own degree-3 polynomial; ν = 5·3N). **One σ per freezing arm, pooled over the four modes**
  (ν = 16 in mode E), the per-mode values printed beside it — a single-mode σ from ν = 4 has a
  90 % range of [0.42, 1.54]·σ; the noise lines are evaluated on the pooled σ and the pilot note
  records its 90 % interval. Studentised residuals are printed per point and |r| > 2.5 is
  flagged as a candidate discontinuity beside M1's continuity diagnostics. These are the
  per-point scatters the noise lines were derived for; σ_E is the scatter of ΔE(q) with **both
  arms' numerical noise included** (the DFT arm's grid-quadrature error is geometry-dependent at
  the µE_h scale; the DFT grid and the SCF/CC convergence thresholds are Q0 deck numbers, and the
  dry run prints the DFT-arm floor from its own single-mode block). Both lines come from one convention — the
  single-mode estimate of a diagonal element must have σ(Δ̂₂,ii) ≤ 2τ: mode E's three-point
  second difference (E₊ − 2E₀ + E₋)/q_s² has σ = σ_E·√6/q_s², giving σ_E ≤ (2/√6)·τ·q_s² ≈
  0.82·τ·q_s²; mode G's central first difference (g₊ − g₋)/(2q_s) has σ = σ_g/(√2·q_s), giving
  σ_g ≤ 2√2·τ·q_s ≈ 2.8·τ·q_s (arithmetic, not a measurement). The **mode-E noise line**: σ_E ≤
  0.82·τ·q_s²; the **mode-G noise line**: σ_g ≤ 2.8·τ·q_s; both evaluated for each grid step q_s ∈ {0.25, 0.5,
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
   CH-stretch unscored — with the **resonance-closed family set at closure depth one, plus the
   totally symmetric modes** (for the first-order geometry term of §3), its size and Hessian
   count printed.
8. **[05] The stopping constant c** (ρ\* = c·ρ_noise; c ≥ 1) per mode, read off the
   noise-injected dry run's K-vs-σ curves — for mode E at the σ_E the R1 smoothness probe
   printed; for mode G at **σ_g^assumed = 2.8·τ·q_s**, the mode-G noise line itself (the worst
   admissible noise), labelled an assumption because no σ_g exists before the note; M2 prints its
   measured σ_g against it — and the response type the residual is computed on in each mode
   (Distilled §3).
9. **[05] K_cap per rung and per mode (E and G)**, derived from the **noise-injected** dry-run K
   at that rung's molecule (or the largest dry-run size available), at the same σ per mode as
   item 8 (σ_E measured; σ_g^assumed for mode G), by a factor stated in the note; together with
   the **mode-G minimum count n_min(G)** (§3) from the same dry run. All are filled for every
   rung regardless of local-CC gradient availability; a mode-G cap is simply unused on a rung
   where mode G is not licensed.
10. **[05] The hold-out fraction f_h and the hold-out seed.**
11. **[05] The Q7 tolerance τ₇** (recovered vs reference Δ₂, prior-assisted vs structural Δ₂, and
    fragment vs whole Δ₂, as per-family RMS harmonic frequency difference, cm⁻¹), **no larger
    than the smallest beat margin of item 2**; and the **discriminability factor** d₇. No Q7
    result exists when they are written.
12. **[05] The Q8 numbers**: r_max, ε₈, η₈ (absolute form), γ, the Cartesian step h, and the
    direct-coupling pair list per rung (which atom pairs, in which bond-count class — near, mid,
    far — with equal counts per class; for R4 and R6, interior and edge pairs on the fragments).
13. **[05] The Q6 numbers**: τ inserted into the two noise lines, the bias line and the
    threshold formulas of §3 with the §3 estimator; the pattern amplitude q_s (one per rung and per mode E/G) from the pooled verdict on the R1
    smoothness grid; the CPS decision; the band width w and regularisation weights of the
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
