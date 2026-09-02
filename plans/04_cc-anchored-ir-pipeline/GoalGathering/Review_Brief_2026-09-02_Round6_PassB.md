# Review brief — Round 6, Pass B: adversarial domain review

**Give this only after Pass A's findings are written down.** Pass A was unprimed on purpose.
This one is primed, because the remaining questions are specific and expensive to find by
wandering.

---

## Your role

A hostile examiner who does computational vibrational spectroscopy / coupled-cluster theory /
scientific ML for a living. You are not trying to help. You are trying to find the thing that
makes this project fail in month fourteen.

The student would rather learn now that the plan is wrong than defend it later.

**A legitimate outcome of this review is "plan 04 is a mistake."** Say so if you believe it,
and name the measurement that would settle it. Plans 01–03 are dead; do not rehabilitate them
unless you can name an affordable measurement that reopens one.

## Standing context

Master's capstone, one person, ~10 h/week human attention. Laptop first (being replaced; all
recorded timings are old-machine provenance); UvA cluster access is a decided collaboration but
not yet an allocation — reach rungs are explicitly blocked on it. Nothing has been executed.
Plan 04's criterion is **relative**: beat the frozen, versioned state-of-the-art lines per band
against laboratory data on rungs R0–R3; *reach* C₃₈₄H₄₈-class with a stated error budget (no
"beat" language there). Read the ladder before attacking; the accuracy/reach split is the
plan's main honesty device and also its most attackable joint.

## What to read

Same workspace rules as Pass A. Read Pass A's findings first —
`Professor_Review_2026-09-02_Round6_PassA.md` (it must exist as a file in this folder before
you start; if findings were addressed, the frozen docs will say so). Then the same corpus:
README banners, plan README, Overarching_Goal, Frozen_Lines_to_Beat,
Frozen_Ladder_and_Tolerances, Compute_Budget_2026-09-02, Capstone_Mapping,
Distilled_Project_Plan_and_Quality_Checks, Relevant_Scientific_Papers, probes/README, and the
source conversation [../../../AI_Chats/grok_chat_4.md](../../../AI_Chats/grok_chat_4.md).

## The plan in one paragraph

Per molecule: DFT geometry + best affordable Hessian; a Transformer-family ML surface /
correction trained on self-generated **DLPNO-CCSD(T)** points (normal-mode + short-MD sampling;
later VAE-proposed, always re-labelled); VPT2 or MD-ACF spectra from that surface; **no scale
factor on anharmonic output**. Anchors licensed by an **R1 canonical-vs-DLPNO check**
(canonical CCSD(T) affordable to ~naphthalene, measured in plan 02). One controlled comparison:
**Δ-learning vs direct DLPNO fit**. Opponents: PAHdb v4.00 scaled harmonic (line A), the
small-molecule anharmonic front + in-house ML-corrected-scaling baseline (line B / M04), Mai
2025 MLMD (line C). Scoreboards: PAHdb experimental (Ar matrix, 15 cm⁻¹ tolerance), NIST
gas-phase, IRMPD. Gates Q0–Q5 (integrity), P0–P5 (science) with mandatory null rows: Δ=0 must
lose or the anharmonic claim is void. Emission: inherited cascade model, tier 1 only promised.

## The six attacks, in order of how much damage they do

### 1. The matrix scoreboard cannot resolve the claimed improvement

The plan's own measured floor (plan-02 probes): scaled-harmonic quartet error ≈ 7 cm⁻¹ mean vs
Ar-matrix data, and the matrix shift tolerance is 15 cm⁻¹. If anharmonic corrections buy a few
cm⁻¹, the *scoreboard's own systematic* (matrix shift, site effects, temperature) may exceed
the effect being claimed. A "beat" verdict measured against data whose uncertainty is larger
than the difference between the two methods is not a verdict.

**What to do:** from the lab literature you can verify (cite, do not recall), what is the
honest per-band uncertainty of matrix-isolation positions vs gas-phase for PAHs of rungs
R0–R3? Which rungs have *gas-phase* coverage sufficient for a resolvable comparison? If only
benzene/naphthalene do, say whether the promised R2–R3 "beat" claims are decidable at all, and
what the plan should promise instead (gas-phase-only families? IRMPD cations? inconclusive
pre-declared?). This attack, if it lands, does not kill the pipeline — it kills the *criterion*.

### 2. DLPNO curvatures and the fiction of the R1 license

DLPNO-CCSD(T) is a controlled truncation for *energies*; its locality thresholds create
non-smoothness that an ML surface will faithfully fit as noise, and its error on delocalized π
systems grows with size (the bibliography's own Sylvetsky/Martin caveat, and the source
conversation's own warning). The plan licenses DLPNO anchors by one canonical check at R1
(C₁₀H₈) and then uses them at C₁₆–C₂₄ and beyond.

**What to do:** is a naphthalene-sized canonical check a *license* or a fig leaf for coronene?
What would a real license look like (TightPNO vs NormalPNO curvature deltas? per-size spot
checks? smoothness probes along normal modes — and does the plan's stop-condition 4 actually
trigger on them)? If DLPNO curvature noise at R2–R3 exceeds the anharmonic signal, the Δ-arm
of the controlled comparison degenerates to the DFT baseline — say whether the plan would
detect that (P3 effect size ≈ 0) or misread it.

### 3. VPT2 at coronene from a fitted surface, and the resonance problem the plan never names

Mulas 2018 needed explicit resonance handling (Fermi resonances, polyads) to do anharmonic
pyrene/coronene from a QFF. The distilled plan says "VPT2 or MD-ACF spectra; declared per
rung" and never mentions resonances at all. VPT2 without resonance treatment produces garbage
exactly in the CH-stretch region the ladder promises; MD-ACF at low internal energy has its
own sampling/width problems.

**What to do:** name the missing machinery. Is "VPT2 or MD-ACF" a method choice or a deferred
decision disguised as one? What does the pilot note have to freeze about resonance handling
*before* R2, and can this plan's author (one person, 10 h/week) realistically implement it?

### 4. The point-factory arithmetic at the promised rungs

R2–R3 need ML surfaces trained on DLPNO points. The source conversation asserts tens of
minutes–hours per coronene point and ~10⁴ points; the plan correctly labels that an assertion
and blocks cluster work on preconditions. But the *promised* rungs R2–R3 are accuracy rungs:
if the point factory for them is a cluster object and the cluster never materializes, the
promise fails — and the budget file's B2 (168 h laptop per rung pilot) may not carry a
C₁₆–C₂₄ factory.

**What to do:** with verifiable published DLPNO timings (cite), bracket a C₁₆H₁₀ point at
TZ-quality on one workstation. Multiply by a defensible minimum point count for a usable
surface (the plan never states one — that omission is itself a finding). Does R2 fit under B2?
If not, R2 silently depends on B3, and the plan's "promised" set depends on an allocation that
does not exist. Name the first timed probe that would force the stop.

### 5. Intensities: promised in the criterion, unsupported in the machinery

The prime directive scores "band positions and intensities." Matrix-isolation intensities are
notoriously unreliable; PAHdb experimental A-values carry their own caveats; the distilled
plan's intensity story is one line (dipole derivatives at the declared level) with no
intensity gate, no intensity tolerance, and no intensity column in the comparison form.

**What to do:** decide whether intensities are actually scoreable at any rung. If not, the
honest fix is to demote intensities to reported-not-scored — but that weakens the criterion
sentence in the Goal file. Name which document has to change and how. Check also: does the
per-band pairing even survive when intensity determines *which* band is "the" band (plan 02's
"strongest band in window" bug lives exactly here — the repository's own history warns
about it).

### 6. The reach claim at C₃₈₄H₄₈ is either unaffordable or unfalsifiable

R6 promises "reached": end-to-end spectrum + error budget. C₃₈₄H₄₈ is 432 atoms, 1290 modes.
Even the DFT Hessian is a serious cluster object (PAHdb did it at 4-31G); anything anharmonic
on top multiplies it; and with no lab data and no CC check possible at that size, the "stated
error budget" is extrapolated from R0–R3 — a number no measurement at R6 can contradict.

**What to do:** attack both horns. (a) Affordability: what does one B3LYP/4-31G-class Hessian
at 432 atoms cost on a mid-size allocation — is R6 even reachable within any budget this
student will hold? (b) Falsifiability: what could make the R6 error budget *wrong* in a way
anyone could detect? If the answer is "nothing", say what the reach claim is actually worth
scientifically, and whether Module 08 should promise it.

## Also worth your attention

- **Charge states.** The ladder's rungs are implicitly neutral; JWST's population is ~half
  cations, and the strongest modern gas-phase data at R2 is IRMPD on *cations*. Is neutral-only
  a scope choice the documents ever state? If not, that is a silent scope hole.
- **The 840 h.** Same class as every earlier plan's calendar finding: T0 is not a date;
  the buckets are caps. Is the promised set (R0–R3 scored + R6 reached + modules 02–09)
  arithmetically inside 840 h at all?
- **Tier-2 emission.** Pre-registered "measured bonus" — check the pre-registration is
  actually specified anywhere (it is not yet; the Joblin-era scoreboard is an admitted debt).
- **The M04 derived-table decision** (user accepted reading 1 without mentor pre-approval):
  assess the actual grader exposure and whether the declared fallback is executable mid-module.
- **Anything Pass A flagged** that you think is worse than Pass A judged it.

## Output format

Plan 03 used Round 5. Use **Round 6, issues 1–N**.

```
Verdict: [green light / conditional / no green light — and for what scope]

## Blocking findings
N. [Title]
   Where: [file, section]
   What: [the problem]
   Evidence: [what you verified, and what you are recalling rather than verifying]
   Why it matters: [consequence]
   What would close it: [in spec / as science — the repository distinguishes these]
```

A valid verdict is that plan 04 should not proceed. Write that if you believe it.
