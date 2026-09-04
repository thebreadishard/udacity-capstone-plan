# Overarching Goal — Plan 05 Δ-Probed IR Pipeline

**Status.** Prime directive as of 2026-09-03; revised the same day after Round-7 Pass A and
Pass B; amended on 2026-09-04 by seven user decisions and two user directives, and revised again
the same day after Round-8 Pass A and Pass B and after Round-9 Pass A and Pass B and Round-10 Pass A. Supersedes plan 04's Goal file; plan 04's folder stays in
the tree as a read-only record (decision 2). Draft; not complete as a plan. Every other plan-05
document must agree with this file; if they drift, this file wins and the other file is patched.

## Glossary (defined here; every other file uses these terms without redefining them)

- **Δ** = local coupled cluster minus DFT, as force constants near equilibrium: **Δ₂** the
  Hessian correction, **Δ₃** cubic, **Δ₄** semi-diagonal quartic. Only Δ₂ is promised.
- **Local CC** = DLPNO-CCSD(T) (domain-based local pair natural orbital) or LNO-CCSD(T) (local
  natural orbital): controlled locality truncations of CCSD(T). **PNO/LNO spaces**: the
  per-pair / per-fragment virtual spaces those methods truncate to. **Frozen spaces**: those
  spaces held fixed at the reference geometry for every probe. **CPS** = complete-PNO-space
  extrapolation. **TightPNO / NormalPNO** = threshold presets.
- **Mode E** = Δ₂ recovered from energies only; **mode G** = from analytic local-CC gradients.
- **Pattern** = one simultaneous multi-atom displacement geometry; **q_s** = its amplitude in
  dimensionless normal-coordinate units; **response** = in mode E the symmetric combination
  R_s(p) = ½[ΔE(+p) + ΔE(−p)] − ΔE(0) of the CC−DFT energy difference over the pattern pair ±p
  (Ladder §3; the first-order term Δ₁·p cancels), in mode G the CC−DFT gradient difference at a
  pattern; every pattern enters the deck as the pair ±p, which carries **one deck index** and is
  the hold-out unit; **R_a** = ½[ΔE(+p) − ΔE(−p)], the antisymmetric by-product (Δ₁·p + O(p³));
  **Δ₁** = the CC−DFT gradient at the DFT equilibrium geometry (not zero; a by-product, never a
  geometry correction).
- **ρ** = the held-out residual (Distilled §3); **ρ\*** = the stopping threshold c·ρ_noise, computed per rung and mode (only c is frozen); **f_h** = the
  held-out fraction; **K** = the measured count of energies (mode E; a ± pair counts 2) or gradients (mode G) at
  which ρ ≤ ρ\*; in mode E,
  K = 2M + K_off with M the number of modes and **K_off** the off-diagonal count; **K_cap** =
  the pilot-note cap on K.
- **Structural prior** = the fixed, parameter-free, frequency-banded regulariser of the
  recovery (band width **w**); **learned prior** = the Module-05 Transformer's predicted
  support; **the licence** = the conditions under which the learned prior may enter a rung
  (Ladder §3).
- **τ** = the smallest beat margin (pilot-note item 2); **τ₇** = the Q7 agreement tolerance in
  cm⁻¹ per family; **d₇** = the Q7 discriminability factor; **r_c** = fitted locality length
  (measured); **r_f** = the smallest passing fragment radius (measured); **r_max**, **ε₈**
  (long-range share), **η₈** (coupling disagreement, absolute form: a fraction of the pair's
  distance-class coupling scale **S**), **γ** (saturation factor), **h** (Cartesian probe step) = the Q8
  numbers (pilot-note item 12); **σ_E**, **σ_g** = the Q6 per-point noise scatters in mode E /
  mode G (√(SSR/(n − p)) about a low-order polynomial fit, **pooled per freezing arm** over the four
  Q6 modes — the pooled value gates, the per-mode values are printed; Ladder §3); **ρ_noise** = σ_resp/RMS of
  the rung's held-out responses, σ_resp = σ(R_s) = σ_E/√2 in mode E and σ_g in mode G;
  **ρ\*_common** = max(ρ\*(R_n), ρ\*(R_{n+1})), the threshold Q8(c) reads both rungs' K at; **c** = the stopping constant (ρ\* = c·ρ_noise; item 8);
  **u_band** = the measured band-centre uncertainty of a laboratory band (resolution, centroid
  precision, temperature term); **the fragment licence** = parts (a), (b), (b′), (c) of Ladder
  §3.
- **RMS_resp** = the RMS of a rung's held-out responses; **ρ_max** = 0.5, the frozen ceiling
  below which ρ\* must lie for the stopping rule to be evaluated (Ladder §3); **n_min(G)** = the
  mode-G minimum pattern count (pilot-note item 9); **S** = the coupling scale of a pair's
  distance class (near / mid / far), written S_class where the class matters — "η₈·S" anywhere
  means η₈·S_class; **resolved pair** = a pair whose direct coupling is at least 3σ_coupling,
  with σ_coupling = σ_E/(2h²); **at noise** = a pair below that floor, or a rung-and-mode whose
  c·ρ_noise ≥ ρ_max; **re-projected** = evaluated in the frozen space as Ladder §3 defines it
  (stored occupied and virtual vectors transported by projection onto the displaced geometry's
  occupied and virtual spaces and Löwdin-orthonormalised; no localiser and no assignment at a
  displaced geometry); **σ_g^assumed** = 2.8·τ·q_s, the value mode G's c and K_cap are read
  at in the pilot note (item 8); **continuity diagnostics** = M1's per-point printout of the
  smallest singular value of the occupied overlap S_oo(x) = C_occ(0)ᵀ S(x) C_occ(x) and the
  largest pre-Löwdin off-diagonal, for both transported halves; **shell** = the fragment-radius
  unit, a complete ring shell around the pair or region served; **pending (b′)** = the fragment
  licence's state when (b) failed at one shell at coronene and only (b′) can test two shells;
  **u_T** = u_band's temperature term, with **T_source** the source's stated temperature,
  **χ_max** = 0.03 cm⁻¹ K⁻¹ (recalled) its unpinned slope and **χ_F** a pinned per-family slope
  (items 52–53).
- **AD / FD** = automatic differentiation / finite differences; **GC-IRD** = gas-chromatography
  infrared detection, the vapour-phase instrument behind the NIST/EPA library; **IRMPD** =
  infrared multiple-photon dissociation; **SRD 35** = NIST Standard Reference Database 35, the
  NIST/EPA gas-phase infrared database; **BHLYP** = Becke half-and-half exchange with LYP
  correlation (50 % exact exchange), the dry run's high-exchange partner.
- **Gates**: **Q0–Q8** integrity gates, **P0–P5** science gates (Distilled §7). **Rungs
  R0–R6**; **A** = accuracy rung, **R** = reach rung. **Budgets B1** (human hours), **B2** (own
  machine), **B3** (cluster or rented time). **M1–M5** = the frozen-space probe (main project)
  and the side project's milestones. **Reading 1 / reading 2** = the two readings of the
  rubric's dataset-reuse clause (Mapping §3 M04). **The pilot note** = the dated note that
  freezes the pilot-dependent numbers (Ladder §4). **The dated notes of Ladder §2** = the R2
  re-read note and the R6-form note.
- **CMA** = the Concordant Mode Approach (items 42–43): **CMA-0** diagonal-only high-level
  force constants in a low-level mode basis; **CMA-2** with diagnostic-selected off-diagonals.
- **GVPT2** = resonance-explicit second-order vibrational perturbation theory; **MD-ACF** =
  spectrum from the dipole autocorrelation of molecular dynamics; **QFF** = quartic force field.

## Prime directive

Build **one pipeline**: any individual aromatic molecule in, an infrared spectrum out —
and make that spectrum's **band positions demonstrably more accurate than the best prediction
currently available anywhere for that molecule**, wherever the laboratory data can decide it:
unconditional on R0 (cell spectra exist; their measurement temperature is read from the
source's documentation before the note); on R1–R3 per family, gas-scored families
decidable only where the scoreboard's **measured band-centre uncertainty** u_band is smaller
than the beat margin (the R1 and R2 C–C families are expected inconclusive by construction on the
NIST hot-vapour sources unless a hot-band correction is pinned before the pilot note, and the
plan says so now) and matrix-scored families
behind the M03 matrix–gas gate (undecidable families pre-declared inconclusive); and never on
reach rungs, where the
deliverable is a labelled theory-vs-theory spectrum, conditional on cluster access. Positions
are the scored quantity; intensities are reported, not part of this criterion.

**And record what the coupled-cluster part cost, as a measured probe count per rung.** The
**guaranteed route is mode E**: K = 2M + K_off local-CC energies with frozen spaces, where the
open cost question lives in K_off; it is guaranteed given a frozen-space local-CC energy code,
which is main-project probe M1 under Ladder stop 1. **The aimed-for route is mode G**: Δ₂ from
analytic local-CC gradients with frozen spaces, where each pattern returns 3N responses instead
of one. No production code offers it today; plan 05 **builds** it in a pre-registered side
project with frozen milestones and a kill criterion
([Side_Project_2026-09-04_ModeG_Gradients.md](Side_Project_2026-09-04_ModeG_Gradients.md);
decision 5). **Mode E runs on every rung R1–R3 that runs**; on every rung where the side project's
milestone licenses it, mode G runs **in addition** and the rung carries two cost records. The
cost record is promised for every rung and mode that ran.
**The only size sentence the thesis may write is numeric** (Ladder §1): how K (mode G) or K_off
(mode E) went from R1 to R3 against how M went. No cost adjective is ever written, in this file
or any other.

The success criterion is **relative and measured**, not absolute. "Chemical precision" is not
the promise; *beating the frozen lines where the data can decide it* is. The opponents are
named and versioned in [Frozen_Lines_to_Beat.md](Frozen_Lines_to_Beat.md) and may not be
swapped after a comparison has been scored. The scoreboard is laboratory data, never another
calculation.

## The scientific questions — three, one per claim type

The accuracy/reach split ([Frozen_Ladder_and_Tolerances.md](Frozen_Ladder_and_Tolerances.md)
§1) is binding; the questions are never concatenated into one claim:

> **Accuracy (rungs R0–R3).** Can a per-molecule pipeline — DFT geometry, harmonic Hessian
> and anharmonic constants, plus a **probed coupled-cluster correction Δ₂ to the harmonic
> force constants**, recovered with the structural prior from K local-CC responses with frozen
> spaces — produce infrared band positions that measurably beat scaled-harmonic DFT (PAHdb
> v4.00), the in-house calibrated harmonic baseline, and — where its coverage reaches —
> DFT-ceiling MLMD (Mai 2025), per band against laboratory spectra?
>
> **Cost (all rungs that ran).** How many local-CC evaluations did the correction need under
> the noise-aware stopping rule, per rung — K = 2M + K_off in mode E on every rung, and K in
> mode G where licensed — and did K_off (and K, where mode G ran on all three) saturate between
> R1, R2 and R3, read at a common threshold (Q8c)?
>
> **Reach (rung R6).** Can the same pipeline — with Δ₂ obtained by **fragment probing**, under
> the fragment licence of Ladder §3 (Q8 on direct couplings at R2–R3; the fragment-vs-whole
> comparison at R3 at the smallest passing radius and, conditional on B3, on a larger molecule
> at R4; a fragment-radius convergence test on the R6 interior itself) — produce a spectrum
> with a stated error budget at sizes where no anharmonic or CC-quality prediction exists at
> all, with its cost record printed beside R3's? **Whole-molecule probing at R6 is not
> promised**: in mode E it is at least 2M = 2,580 local-CC energies of a 432-atom molecule.

**Where CC is spent, and why only there.** The promised correction is harmonic (Δ₂). The
hybrid quartic-force-field literature (items 14, 27, and the Esposito 2024 naphthalene work,
item 45) puts the coupled-cluster pay-off in the quadratic constants and leaves cubic and
quartic constants at DFT level; and the energy-only probes of mode E cannot produce the
three-index cubic constants φ_ijk that PAH combination-band resonances need (Round-7 Pass B
issue 3). Plan 05 therefore promises **no CC correction to anharmonic constants**. A
**diagonal-cubic bonus probe** (Δ₃ along each scored family's mode, from the antisymmetric combinations of the single-mode
± block plus one further amplitude: two extra energies per mode)
reports how large that correction would have been. The DFT cubic and semi-diagonal quartic
constants are computed for a family set **closed under the resonance search to depth one**
(partner modes displaced too; partners' own diagonal anharmonicity from their 1-D cut; bounded
by the polyad cap; size and Hessian count printed in the pilot note).

**What is scored.** Band **positions**. Intensities are computed from DFT dipole derivatives
and reported with provenance; no CC correction to dipoles is promised — local-correlation
domain changes produce micro-hartree discontinuities that wreck finite-difference field
properties even with fixed PNO dimensions (item 30, full text read) — and they are *scored* only
where the pilot note names a gas-phase intensity scoreboard. Band pairing is fixed in the pilot
note, never chosen by "strongest band in a window".

## Method skeleton (to be distilled)

Per molecule, with the rung chosen by the declared size ladder:

1. **Geometry + harmonic Hessian + dipole derivatives** at a declared DFT level (B3LYP-class,
   basis frozen per rung), analytic, on the B2 laptop's CPU through R3 (it has no CUDA-class
   GPU; any GPU Hessian is rented B3 time). At R6 this Hessian is itself a B3 object unless a
   timed probe at the R4 species shows otherwise. DFT cubic and semi-diagonal quartic constants
   from finite differences of the analytic DFT Hessian along the resonance-closed family set.
2. **Δ-probing (Δ₂).** A hashed, ordered set of displacement patterns, each entered as the pair ±p so
   the mode-E response is the symmetric combination that cancels the CC−DFT force term (Ladder
   §3): the single-mode block first, then simultaneous multi-atom
   displacements built so every atom's local displacement space is complete, plus explicit
   two-mode patterns for every off-diagonal block the zero-CC dry run flags as large (CMA-2's
   diagnostic, written as a pattern rule before any response exists). Amplitudes are chosen
   **from** the Q6 step grid (the largest step under the noise line), never the reverse. At
   every pattern, local CC and DFT are evaluated **with frozen spaces**. Patterns are consumed in
   hashed order; the recovery (sparse, in the DFT normal-mode basis, structural prior) is
   re-solved as patterns accrue, and **K is the count at which ρ first falls below ρ\***.
   Licences: Q6 (anchor noise in the mode used, bias and threshold sensitivity against frozen
   formulas), Q7 (recovery vs direct references at R0–R1, printed for the diagonal-only and the
   full recovery), Q8 (locality on **directly measured** blocks, and saturation).
3. **Spectra** via the **resonance-explicit routes** frozen in plan 04 — GVPT2 with named
   thresholds and a polyad cap; MD-ACF on a *defined* DFT-plus-Δ potential (Distilled §3); or
   CH-stretch unscored at that rung — on DFT-plus-Δ₂. **Raw VPT2 without resonance treatment
   is forbidden on promised families.** No scale factor on anharmonic output.
4. **Error budget**: every claimed band carries its measured error sources — DFT level; ρ;
   local-CC noise floor and space-freezing bias against the Q6 formulas; the long-range share
   of the family's correction measured on direct couplings (Q8b); matrix–gas shift where matrix
   data is used.

Known risks, named now, each with the gate that measures it: frozen-space local-CC energies
may not be smooth at the micro-hartree level that mode E needs — the published fixed-PNO-
dimension remedy failed for field derivatives (item 30) and nuclear displacements are untested
(Q6, with thresholds); Δ₂ may not be near-diagonal in the DFT mode basis for aromatic ring
modes — CMA-0 fails on exactly those (item 43) — which is why the prior is banded and Q7 prints
diagonal-only and full recoveries side by side; Δ may not be local, or local for C–H modes and
not for the delocalised C–C families (Q8a/b on direct couplings, per family); K_off may grow with
the near-degenerate manifold (Q8c); mode G may not materialise (the side project's kill
criterion); the local-approximation error itself grows with acene length (item 44; the
TightPNO/NormalPNO and CPS columns of Q6); the CC correction may not improve on DFT-level
anharmonicity on some families (P4's Δ=0 null row) or may lose to calibrated harmonics, whose
fitted factors already absorb the mean of a ~5 cm⁻¹ harmonic difference (item 45, snippet
grade; a P2 outcome) — both publishable.

## Temperature and emission (the 0 K question) — carried from plan 04

Scored product = **0 K absorption** against laboratory data. Emission after UV heating in
three declared tiers: **tier 1 promised** — post-process through the published NASA Ames
cascade model (AmesPAHdbPythonSuite), inherited machinery, honestly labelled; **tier 2
conditional** — temperature-dependent shifts from MD on the *defined* DFT-plus-Δ potential
(Distilled §3), protocol written only after the tier-2 lab references are pinned (bibliography
debt 4 unpaid); **tier 3 not promised**. "Tier" here is an emission tier; the size tiers of the
expectations section below are numbered separately.

## Size and compute (carried, with the plan-05 additions)

- **Size:** the method must work on super-large aromatics — **including C₃₈₄H₄₈-class species
  (the 101–386-carbon PAHdb bin) and larger**. Whether C₃₈₄H₄₈ itself has a PAHdb v4.00 entry
  is an unpaid check (frozen-lines debt 6); the R6 target species is chosen from the atlas.
  R6 is reached by fragment probing under the fragment licence (decision 1; Ladder §3).
- **Compute:** the plan must not die on compute. Start on the current laptop — the B2 machine
  named in the budget (decision 6: an 8-core Ryzen 7 260, 32 GB, no CUDA-class GPU; replaced
  only if a probe shows it necessary) — with the R0 pilot and a **zero-CC dry run** of the
  probing machinery (Δ between B3LYP and a high-exact-exchange functional, run in **both**
  modes since DFT gradients exist, at any size the DFT Hessian affords); escalate to UvA
  supercomputer access or rented GPU time when a rung demands it, under
  [Compute_Budget_2026-09-03.md](Compute_Budget_2026-09-03.md): human hours **logged, never
  capped**; own-machine wall-clock as **checkpoints**; cluster node-hours and rented GPU-hours
  under per-rung dated notes after timed probes. The classification rule is
  `wall_clock_per_probe × K_cap × c_CPS` against the 168 h checkpoint.

## Scope boundaries

- The degree **ends at Module 09**. No Horizon documents, no Projects 10–12.
- Light–matter dynamics is **out** (plan-03 Pass B verdict, one scope, one clock — kept because
  it serves the goal, not by inheritance).
- JWST spectra motivate the work; **species identification is not a promise**.
- No sub-tolerance language: observational meaning ends around 10 cm⁻¹; matrix data carries
  its own measured shift; ~1 cm⁻¹-class accuracy is claimed **only if** the lab comparison and
  the declared controls (ρ, local-CC noise floor, threshold sensitivity) all allow it — and
  never on matrix data.
- **No transferable, train-once spectrum model** — because motif transfer of band positions
  was measured to fail (plan-02 probes), not because plan 04 said so. Every molecule gets its
  own probed Δ₂. The learned prior **earns its licence on R2 and R3 and spends it on R4–R6**
  (Ladder §3): on R0–R3 the scored spectrum is always the structural recovery; on R4–R6 a
  prior-assisted recovery may be the only full recovery, and the certificate then says that the
  spectrum depends on the learned prior and how that dependence was checked.

## The goal binds; methods are means (user directive, 2026-09-04)

The user's ruling on fragment probing, recorded verbatim in substance: *it is not for the
user to dictate whether probing in fragments is allowed. If it works and the goal is reached
with it, fine; if it does not work, then not. The goal must not drop out of sight. The goal
must be reached: a pipeline that works.* Consequences, so this directive cannot be quoted
against the freeze:

1. **Fragment probing is a permitted method, not a scope question.** Whether it is *used* at
   R6 is decided by the **fragment licence** (Ladder §3), which is measurement and nothing but
   measurement: (a) Q8(a/b) on directly measured couplings at R2 and R3 for the scored
   families; (b) the **fragment-vs-whole comparison at R3** — coronene probed whole *and* from
   fragments at the smallest radius r_f that passes, the two Δ₂ agreeing per family within τ₇,
   r_f printed against coronene's own radius; (b′) the same comparison **on a molecule larger
   than coronene** at R4, promised conditional on B3 classification — the only comparison on a
   fragment that is not the whole molecule; and (c) a **fragment-radius convergence test on the
   rung's own interior** (direct couplings from fragments of radius r_f and r_f + one shell carved
   from the rung's DFT geometry, agreeing within the absolute η₈; r_f is the R3 value from (b), or
   (b′)'s if larger; run once, the passing radius printed in the certificate; a probe batch
   classified like any other), first on circumcoronene's central ring, then on the R6 flake; whole-flake direct couplings, where B3 allows, as the
   gold check. A measurement that could not fail for the reason that matters — the interior
   differing from anything measured — is not a licence, which is why (b′) and (c) exist.
2. **The no-transfer rule is clarified, not weakened.** It forbids transferring *spectra or
   band positions* between molecules (the motif-atlas failure plan 02 measured). A
   locality-verified electronic correction, measured on one region and applied to another
   region whose local environment is the same within r_max, is a method whose validity the
   fragment licence measures per family; it is labelled as such in every certificate that uses
   it.
3. **R6 stays a promised object**, as fragment-probed Δ₂, conditional on the fragment licence
   and on B3. If the licence fails for a family, that family's correction is withdrawn from
   the R6 certificate with the measured long-range share; if it fails for all scored families,
   R6 is reported with the fail-closed sentence of Distilled §8 — the goal was kept in sight
   and the method was measured to fall short of it, which is a result.
4. **The honesty rules remain the way the goal is pursued, not a reason to stop short of it.**
   No gate in this plan exists to avoid the large molecules; every gate exists so that the
   pipeline can be taken there without lying about what it delivers.

## Inheritance is not authority (user directive, 2026-09-04)

Nothing is forbidden in plan 05 because plan 04 forbade it. A rule from an earlier plan survives
here only if it still serves the goal or rests on a measurement that still stands. If knowledge
transfer makes plan 05 succeed, it is allowed. Decided under this rule: the no-transfer rule is
kept for spectra and band positions (a measurement); fragment probing is licensed by
measurement; the learned prior is licensed by measurement (Ladder §3). **The walk of the other
inherited rules (Round-8 Pass B finding 13):** *no scale factor on anharmonic output* — goal
(the tier-2 expectation "natively, without any generic scale factor"; a scaled anharmonic
spectrum against fitted opponents would be fit-vs-fit); *positions scored, intensities
reported* — measurement, now verified: the NIST/EPA gas-phase spectra carry no concentration
data and matrix intensities never score, and item 30 bars a CC dipole correction; *neutral
species only* — re-justified as a per-rung choice, not a capability limit (Ladder §2 "Charge":
B3LYP spin contamination for radical cations, the doubled canonical arm, matrix/IRMPD-only
cation data; open-shell LNO-CCSD(T) exists in the candidate code), with the pilot note free to
name a charge state for a rung; *no tier-2 pre-registration before references* — goal (a
protocol without a pinned scoreboard cannot be scored); *the matrix–gas gate and its gas-side
twin u_band* — measurement; *B3LYP-class baseline DFT* — goal (P1 and P2 compare like with like
against line A; written in Distilled §3); *the 10 cm⁻¹ astronomical floor and the ~1 cm⁻¹ bind*
— goal and measurement respectively. No inherited rule now rests on habit.

## Decisions of 2026-09-04 (all closed; recorded here so this file, which wins on drift, carries them)

1. **Fragment probing** — a permitted method, used at R6 under the fragment licence; R6 promised
   as fragment-probed Δ₂, conditional on that licence and on B3; whole-molecule R6 not promised.
2. **All plan folders stay in the tree**; plans 01–03 restored as read-only records.
3. **The R2 A-scored set** as re-read against the coverage probe stands: pyrene, chrysene,
   triphenylene (gas families), tetracene (matrix, M03-gated).
4. **Module 05 adopted**: a Transformer predicting the support of Δ₂ in the DFT mode basis;
   corpus = an aromatic-heavy subset of public Hessian QM9 plus recomputed B3LYP Hessians (size
   fixed by dated note after the B2 Hessian timing is printed), PAH tensors held out as test
   set only; success = the P3 saving and the licence, not accuracy; reuse clause under reading 1
   with the reading-2 fallback executable mid-module.
5. **The promised set**: the harmonic-only correction (Δ₂) is accepted; mode E is the guaranteed
   route and is *not* accepted as a limit — mode G is built in the side project; R6 per
   decision 1.
6. **B2 is the current ASUS Vivobook 18 M1807HA-S8022W** (Ryzen 7 260, 8C/16T, 32 GB DDR5,
   Radeon 780M, no CUDA GPU); a replacement only if a probe shows it necessary.

7. **The Foundations module and QM9** (raised by Round-8 Pass A issue 20) — **Decision 7 (closed 2026-09-04):** no capstone module has been submitted to the school. A draft Foundations project on QM9 exists in the user's GitHub account (`ai-programming-foundations-project`) but was never submitted; the user will rename or archive that repository so that a fresh Module 02 built on the plan's opponent atlas takes its place. Consequences: the mapping's M02 row is a plan, not a record; the Module-05 corpus (Hessian QM9) faces no "reused from a previous capstone project" exposure from module 02, since nothing was submitted — the reading-2 fallback stays a named debt as ordinary insurance; the renamed draft is mentioned in the M02 report's provenance paragraph so no grader mistakes it for a submission.

## Forbidden quotes (this thesis)

Do not write any of the following as a Module 08 result:

- "Chemically precise infrared lines."
- "We beat PAHdb / Mai 2025" without the pre-registered per-band comparison printed by a probe.
- "We identified PAHs in a JWST spectrum."
- "The pipeline works to C₃₈₄H₄₈" unless that molecule's rung actually ran and was scored.
- **"Size-independent", "O(1)", "does not grow with the molecule", "saturates", or any cost
  adjective, with or without "-class"** — cost is reported as the printed record (Ladder §1)
  and, after Q8(c), as the printed ratios; never as an adjective.
- "A coupled-cluster anharmonic correction" — none is promised; the diagonal-cubic probe is a
  reported bonus number.
- "Coupled-cluster quality" as an accuracy adjective — the anchor is "local-CC, R1-checked"
  (Ladder §6).
- "Decidable" for a family whose u_band M03 has not printed, or from a point spacing.
- "Never done before" — the diagonal mode-E recovery is CMA-0 applied to a difference (items
  42–43); what the search did not find is stated in the Research note §8 and nowhere else.
- Any band position without its measured error source named.

## Value hierarchy (user directive 2026-09-02, carried because it is the goal)

Beating the lines on benzene is **not the point**; the small rungs license and calibrate. **The
destination is the territory where nothing exists yet**: super-large aromatics that no method
has ever treated beyond scaled-harmonic DFT. Winning small is not a precondition for going
large; scoring honestly is. The honesty rules are how unknown territory is entered, not why it
is avoided.

## Expectations per size tier (user directive 2026-09-03, carried in substance)

1. **Small (R0–R1):** truth is known; the pipeline must **agree** within the stated margin.
2. **Medium (R2–R3):** land within the margin **natively, without any generic scale factor**.
3. **Large (R4–R5, bonus):** named-expert judgment, expert and question fixed in a dated note
   before any R4 spectrum exists — a datum, not a quote.
4. **Super-large (R6):** **earned trust**, citing the tier record exactly as it stands.

## Hours (user directive 2026-09-03, carried)

**No cap on human hours anywhere in this plan.** Hours are logged, never limited; no deadline
is a gate; machine checkpoints survive as honesty devices only. Udacity module deadlines are
school facts handled in the mapping, never a science gate.

## What is inherited

From plans 01–04, method-agnostic and kept because each serves the goal: measured-not-asserted
probes; never cite from recall; pre-registration, frozen splits with hashes, ≥3 seeds, tuning
parity; declared effect size, inconclusive publishable; escalation ladders declared in advance,
stopping is a result; fail-closed reporting; deviations as dated notes committed before the
affected number is known. From plan 02: the lab-comparison machinery (git history and the
restored folder). From plan 04 specifically: the opponents, scoreboards, ladder, tolerances,
gates and both Round-6 reviews with their closures.

## Industry frame (carried)

Reliability-gated spectral prediction for laboratory astrophysics and aerosol/combustion
diagnostics: a per-molecule spectrum **with a quantified error budget**, or an explicit refusal
naming the rung that could not be afforded — now with the cost of that spectrum stated as a
measured probe count, so a database keeper can price a species before asking for it.
