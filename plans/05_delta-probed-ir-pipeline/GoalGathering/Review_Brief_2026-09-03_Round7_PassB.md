# Review brief — Round 7, Pass B: adversarial domain review

**Give this only after Pass A's findings are written down and addressed.** Pass A was unprimed
on purpose. This one is primed, because the remaining questions are specific and expensive to
find by wandering.

---

## Your role

A hostile examiner who does computational vibrational spectroscopy / local coupled-cluster
theory / numerical linear algebra / scientific ML for a living. You are not trying to help. You
are trying to find the thing that makes this project fail in month fourteen.

The student would rather learn now that the plan is wrong than defend it later.

**A legitimate outcome of this review is "plan 05 is a mistake — go back to plan 04" or
"neither plan is affordable."** Say so if you believe it, and name the measurement that would
settle it. Plans 01–03 are dead; do not rehabilitate them.

## Standing context

Master's capstone, one person; human hours uncapped by directive; laptop first (being
replaced; GPU unknown); UvA cluster access a decided collaboration, not an allocation; rented
GPU time counted under the same preconditions. Nothing has been executed under plan 05.
Plan 05 keeps plan 04's **relative** criterion (beat frozen, versioned lines per band against
laboratory data on R0–R3, matrix-gated on R2–R3; *reach* C₃₈₄H₄₈-class with a stated error
budget and no "beat"), and adds a **cost claim**: the number K of coupled-cluster evaluations
per molecule is measured per rung and expected to saturate with size. Read the ladder before
attacking; the accuracy/reach split is inherited and already survived Round 6; **the new
attackable joint is the locality bet and the recovery machinery.**

## What to read

Same workspace rules as Pass A. Read Pass A's findings first —
`Professor_Review_2026-09-03_Round7_PassA.md` (it must exist as a file in this folder before
you start; if findings were addressed, the frozen docs will say so). Then the corpus: README
banners, plan README, Why_05_Supersedes_04, Overarching_Goal, Research_Note_2026-09-03,
Frozen_Lines_to_Beat, Frozen_Ladder_and_Tolerances, Compute_Budget_2026-09-03, Distilled,
Relevant_Scientific_Papers, probes/README; plan 04's Round-6 Pass B
(`../../04_cc-anchored-ir-pipeline/GoalGathering/Professor_Review_2026-09-02_Round6_PassB.md`)
for what is already settled; and the source conversation
[../../../AI_Chats/grok_chat_4.md](../../../AI_Chats/grok_chat_4.md).

## The plan in one paragraph

Per molecule: DFT geometry, analytic DFT Hessian and dipole derivatives (GPU where available);
DFT cubic/semi-diagonal quartic constants on the promised families' modes. Then **Δ-probing**:
Δ = local CC (DLPNO- or LNO-CCSD(T), domains frozen at the reference geometry) minus DFT, as
force constants; a hashed set of K simultaneously multi-displaced geometries (O1NumHess-class
pattern construction, plus mode-targeted cuts); Δ₂ recovered by sparse recovery in the DFT
normal-mode basis (near-diagonal ℓ₁ prior plus an off-diagonal low-rank term), Δ₃/Δ₄ on the
scored families by least squares; **mode E** (energies only, K ≈ 2M + K_off) or **mode G**
(gradients, K expected O(1)) per rung by a timed probe; a held-out fraction f_h of probes gives
the residual. Licences: Q6 (local CC vs canonical; frozen vs free domains), **Q7** (recovered
Δ₂ vs a direct reference Δ₂ at R0–R1, plus a shuffled-probe null), **Q8** (Δ₂ locality decay
and K side by side at R1–R3). Spectra: GVPT2 or MD-ACF, resonance-explicit, on DFT-plus-Δ; no
scale factor. One controlled comparison (P3): a Transformer Δ-prior vs an uninformed prior at
matched K — never on the promised path. Null rows: Δ=0 must lose P2; noise input must fail;
shuffled probes must fail Q7.

## The seven attacks, in order of how much damage they do

### 1. The CC−DFT correction is not short-ranged in a conjugated π system

The entire size claim rests on Δ₂ decaying with interatomic distance. But B3LYP's best-known
failure in polyacenes and graphene flakes is **delocalisation error**: wrong bond-length
alternation, over-delocalised π density, the wrong Kekulé/quinoidal balance, and in long acenes
an unphysical singlet instability. Those errors are collective; their signature in the Hessian
is a *long-range* correction to the C–C stretching block (the 6.2/7.7 µm families), not a local
one. The plan's locality evidence comes from energies (DLPNO, srΔML, MOB-ML), not curvatures,
and from saturated or weakly conjugated systems.

**What to do:** from the literature you can verify (cite, do not recall), what is known about
the range of the CC−DFT Hessian correction in conjugated systems? Is there a published
CCSD(T)-vs-B3LYP harmonic-frequency comparison on acenes or PAHs from which the *mode
character* of the largest deltas can be read? If the largest Δ₂ elements live in delocalised
C–C modes, Q8 fails on exactly the families the astronomy needs (6.2, 7.7 µm) while passing on
C–H modes — say whether the plan would detect that per family (Q8 is written per atom pair,
not per family) or misread it as "local". Name the cheapest probe that settles it (a naphthalene
or anthracene CC-vs-DFT numerical Hessian is affordable).

### 2. Energy-only recovery cannot see Δ₂ above the local-CC noise floor

In mode E, a diagonal Δ₂ element is a second difference of *energy differences* along a DFT
mode. Local-CC energies carry a noise floor from domain construction (Madriaga & Crawford
report ~1 μE_h jumps; the plan freezes domains to remove them — but frozen domains have their
own bias as the geometry moves). The signal is a shift of a few to a few tens of cm⁻¹ in a
frequency, i.e. a small fraction of a small second derivative, divided by a step size that must
stay inside the frozen-domain validity range.

**What to do:** do the arithmetic. For a typical PAH mode (say a 1,300 cm⁻¹ C–C stretch, a
1,600 cm⁻¹ one, a 3,050 cm⁻¹ C–H stretch, an 850 cm⁻¹ CH-oop), what step size and what energy
precision are needed to resolve a 5 cm⁻¹ correction to the harmonic frequency by central
differences? Compare with a credible local-CC energy precision with and without frozen domains
(cite thresholds and their documented energy effects). If mode E is noise-limited at the beat
margin, the plan's promised path (mode E is the default) does not license "beat" language at
all, and only mode G — which the plan admits may not exist for DLPNO-CCSD(T) — can carry it.
Say whether Q6's smoothness probe is written tightly enough to catch this before R2.

### 3. Mode G does not exist, so K = O(1) is a hope, not a plan

The plan's own bibliography says ORCA advertises no analytic DLPNO-CCSD(T) gradient, Psi4's
DLPNO page does not mention gradients, and the only local-CC(T) gradient found is an
automatic-differentiation implementation on medium molecules. The "size-independent" sentence
in the Goal survives only in mode G.

**What to do:** verify the gradient landscape as of your reading (ORCA, Psi4, MRCC LNO, Molpro
PNO-LCCSD, PySCFAD) — cite what you checked. If no production code offers a local-CC(T)
gradient at coronene size with frozen domains, what is the honest cost model? Assess the
plan's fallback (CCSD-level gradients plus energy-only (T)) — is a DLPNO-CCSD gradient
available anywhere, and does splitting (T) off preserve the accuracy the criterion needs? If
mode E is the only real mode, K grows with M and the Goal's second sentence must be rewritten
or cut. Say which.

### 4. The off-diagonal low-rank / sparsity structure holds for Hessians of local methods, not necessarily for Δ

O1NumHess's O(1) argument rests on the Hessian's off-diagonal blocks between distant atom
groups being low-rank (a local electronic term plus a low-rank near-resonance term). Sanders'
compressed sensing rests on the *full* Hessian being near-diagonal in a cheap method's
eigenbasis. Plan 05 applies both ideas to Δ = CC − DFT and assumes Δ inherits the friendlier
structure. It may inherit the *worse* one: if DFT's error is in the delocalised block, Δ in
the DFT eigenbasis is *not* near-diagonal exactly where it matters.

**What to do:** state the conditions under which Δ₂ is sparse in the DFT normal-mode basis,
and whether they are the same conditions as attack 1. Is the recovery well-posed if the
near-diagonal prior is wrong — does ℓ₁ regularisation then *suppress* the off-diagonal Δ the
spectrum needs, producing a confidently wrong Δ that passes a held-out residual test on the
probes it was designed from? Judge whether Q7's reference comparison (at R0–R1 only, small
molecules where everything is local) can license the structure assumption at R3 and beyond.

### 5. Δ₃/Δ₄ on the scored families is not a small add-on

GVPT2 for a band family needs cubic constants coupling that family's modes to *every* mode
they resonate with, and Fermi/Darling–Dennison resonances in PAHs are dense (Mulas 2018). The
plan probes Δ₃/Δ₄ "on the promised families' modes" by 1-D/2-D cuts. If the CC correction to a
resonance partner's cubic constant is what moves the band, mode-targeted cuts miss it.

**What to do:** for pyrene or coronene, from Mulas 2018 or the PAHdb anharmonic method papers,
how many cubic constants materially affect the CH-oop and C–C families? Is the plan's
harmonic-first allocation (CC into Δ₂, DFT for anharmonic constants unless probed) defensible
from the hybrid-QFF literature *for PAHs*, or only for small semi-rigid molecules? If DFT cubic
constants suffice, say so and the plan is stronger than it claims; if not, Δ₃ probing scales
badly and the cost picture changes.

### 6. Frozen domains: smooth but biased

Freezing domains and pair lists at the reference geometry removes discontinuities; it also
freezes an approximation that was optimal at one geometry. For the step sizes mode E needs
(attack 2) the bias may be negligible; for mode-targeted cuts of Δ₃/Δ₄ (larger displacements)
it may not be. And the plan's Q7 reference is computed *with the same frozen domains*, so a
frozen-domain bias is invisible to Q7 by construction.

**What to do:** what does the local-correlation literature say about domain-freezing error vs
displacement amplitude (Werner group frozen-domain derivative work; the ORCA DLPNO-MP2
`StoreDLPNOData` documentation; anything on PNO-space consistency along a coordinate)? Name
the one canonical check that would expose the bias at R0 (benzene canonical CCSD(T) is
affordable), and whether Q6 as written performs it.

### 7. The deep-learning module is a rubric hostage

Module 05 must ship a Transformer with a controlled comparison. The plan's Transformer is a
Δ-prior trained on "the published corpus of probed Δ tensors from earlier rungs" — at most
four molecules' worth before R2 is done, and the promised path never uses it. That is either an
honest efficiency experiment or a toy model bolted on to satisfy a rubric, and a grader will
ask which.

**What to do:** is there enough data for a deep-learning project at all (count the tensors and
the probes)? Would a prior trained on DFT-vs-DFT dry-run Δ tensors (unlimited, any size) be a
legitimate pre-training corpus, and does the plan's Q4/Q3 discipline allow it? If the M05
object cannot be made load-bearing, say so now — the mapping has not been written yet, and it
is cheaper to hear it before than after.

## Also worth your attention

- **Is the "never done" claim true?** The research note says the combination (recovery of a
  CC−DFT force-constant difference by O(1)/compressed-sensing probing; extension to Δ₃/Δ₄)
  was not found on 2026-09-03. Try to falsify it: hybrid QFF papers, Δ-Hessian schemes,
  "difference Hessian" finite-difference tricks, local-correlation frequency work by the
  Werner, Neese, Kállay, Valeev or Crawford groups, compressed-sensing vibrational work after
  2015. A prior instance does not kill the plan, but it must be cited and the novelty sentence
  rewritten.
- **The fragment-probing open decision.** If Δ is local enough for whole-molecule probing to
  saturate, is fragment probing even needed for R6? If Δ is *not* local enough, fragment
  probing is wrong by the same measurement. Say whether the open decision is real or moot.
- **The DFT Hessian at R6.** C₃₈₄H₄₈-class species on GPU at 6-31G*/4-31G: memory and time
  on hardware this student can rent — is the *global part* itself a B3 object?
- **Charge states, matrix decidability, intensities, tier 2** — all inherited from Round 6;
  flag only if plan 05 made any of them worse.
- **Anything Pass A flagged** that you think is worse than Pass A judged it.

## Output format

Plan 04 used Round 6. Use **Round 7, issues 1–N**.

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

A valid verdict is that plan 05 should not proceed. Write that if you believe it.
