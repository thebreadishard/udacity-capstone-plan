# Review brief — Round 4, Pass B: adversarial domain review

**Give this only after Pass A's findings are written down.** Pass A was unprimed on purpose. This
one is primed, because the remaining questions are specific and expensive to find by wandering.

---

## Your role

A hostile examiner who does computational chemistry for a living and has read the recent PAH
literature. You are not trying to help. You are trying to find the thing that makes this project
fail in month fourteen.

The student would rather learn now that the plan is wrong than defend it later.

## Standing context

Same as Pass A: master's capstone, one person, ~10 h/week, nothing executed, consumer hardware plus
possibly limited HPC. Plan 02 replaced plan 01 on 2026-08-23 after a literature check showed the
earlier deliverable had been overtaken.

**A legitimate outcome of this review is "the pivot was a mistake and plan 01 was better."** Say so
if you believe it, and say which measurement would settle it.

## The plan in one paragraph

Predict anharmonic infrared band positions and relative intensities for named PAH sizes and charge
states (benzene → naphthalene → anthracene/phenanthrene → pyrene, neutral and cation). Anchor the
electronic structure to a **measured** coupled-cluster rung: canonical CCSD(T) where computable,
DLPNO/LNO-CCSD(T) beyond it, with the local-vs-canonical error published per band family and charge
state. Carry that anchor to production with Δ-learning or fine-tuning of an equivariant MLIP
(MACE-OMOL-0). Get vibrations from a quartic force field built on the MLIP plus GVPT2, escalating to
selected VCI. Get intensities from a dipole moment surface. End in a pre-registered, fail-closed
identification against one frozen JWST/PAHdb product, with a four-term error budget throughout.

## The six attacks, in order of how much damage they do

### 1. The core hypothesis may be backwards

Everything rests on one claim, stated in Distilled §2:

> *The dominant error in current large-PAH IR predictions is electronic-structure error, not
> nuclear-motion error — and it is invisible because nobody quantifies it.*

If nuclear-motion error dominates instead, the whole pivot points the wrong way: the effort belongs
in VCI and resonance treatment, not in coupled cluster.

**What to do:** argue it from the literature you know. Anharmonic constants depend on third and
fourth derivatives; how sensitive are those to the underlying electronic-structure method compared
to the sensitivity of the nuclear-motion treatment? Is there published evidence either way for
aromatics specifically? If the hypothesis is unsupported, say what experiment would decide it and
whether it is affordable here.

### 2. The cost arithmetic has not been done

The plan cites Kumar, Neese & Valeev (2020): DLPNO-CCSD(T)-F12 on 550+ atoms, under three days, one
multi-core machine. **That is a single-point energy.** This plan needs, per rung:

- hundreds of geometries for the Δ-ML set
- gradients (analytic if available, otherwise finite differences — 6N single points per gradient)
- TightPNO settings, which are substantially more expensive than default
- open-shell cations
- and canonical CCSD(T) on benzene and naphthalene as the reference

**The plan does not contain this multiplication.** Do it. Even an order-of-magnitude estimate is
worth more than what is currently there. If it comes out at thousands of core-days, say which rung
the ladder realistically stops at, and whether §5.7's shrink ladder actually rescues it or merely
documents the failure.

This is the single most likely place the plan breaks, and the author knows it.

### 3. A quartic force field at pyrene-scale congestion

The feasibility argument leans on Kotaru et al. (2026): QFF + VPT2 for 21-atom aspirin in about a
minute from an MLP. Pyrene is C₁₆H₁₀ — 26 atoms, 72 vibrational modes, and a fingerprint region with
many near-degenerate pairs. Aspirin is not that.

**What to do:** is semidiagonal-quartic GVPT2 realistic there, or does the resonance structure force
selected VCI on most of the 6–9 μm region? If VCI is effectively mandatory, is *that* affordable, and
does the plan's escalation ladder (§2.1, §6.4) survive contact with it? How many species end up
marked UNRESOLVED?

### 4. Can an MLIP actually carry coupled-cluster-quality third derivatives?

Distilled §5.8 and §6.2 gate cubic force constants on step-size stability, citing Dral et al. on
"wrinkly" surfaces. But the plan asserts rather than demonstrates that a fine-tuned foundation model
reaches that standard.

**What to do:** is there published evidence that fine-tuned foundation-model MLIPs give usable
cubic/quartic constants, as opposed to good energies and forces? MACE-OMOL-0 is pre-trained on hybrid
DFT and fine-tuned on a few hundred CC points — is that enough data to move third derivatives, or
only enough to shift the minimum? If the answer is "nobody has shown this", that is a finding.

### 5. Is the residual contribution real?

The plan concedes that anharmonic PAH IR (Mai 2025, 1704 species to C₂₁₆), VPT2-on-MLP (2021–2026),
transfer learning to CCSD(T) (2021–2023), and IR cascade emission models (Chen 2026) all exist. It
claims the remaining contribution is the *combination* of a measured gold rung, the four-term budget,
and a fail-closed identification.

**What to do:** is that a contribution or a wrapper? Would a referee at a chemistry or astronomy
journal see novelty? Has someone already anchored PAH anharmonic spectra to coupled cluster and you
know of it? Be blunt.

### 6. The effort estimate is a table of guesses

Restructure proposal §10 claims the pivot is roughly effort-neutral: ~440–700 hours removed,
~440–680 added. No row is measured.

**What to do:** which row is most wrong? At 10 h/week, does any version of this finish? Is the
guaranteed-deliverable fallback (option F: small molecules only, done excellently) the honest primary
plan rather than the safety net?

## Also worth your attention

- **The two-part band tolerance** in `Frozen_Ladder_and_Tolerances_2026-08-25.md` §3.1: absolute
  ≤ 10 cm⁻¹ **and** no worse than scaled-harmonic on the same modes. Is the second condition
  achievable, or does it quietly make the whole project impossible? ML-corrected scaling reportedly
  reaches ~5 cm⁻¹.
- **Cations.** Every claim of astrophysical relevance depends on them. Open-shell local coupled
  cluster, open-shell MLIP fine-tuning, and cation experimental standards are each shakier than their
  neutral counterparts. Is the cation half of this ladder realistic?
- **Anything Pass A flagged** that you think is worse than Pass A judged it.

## Output format

Continue the numbering from plan 01's reviews, which reached issue 15 plus a separate Round-3 list.
Use **Round 4, issues 1–N**.

```
Verdict: [green light / conditional / no green light — and for what scope]

## Blocking findings
N. [Title]
   Where: [file, section]
   What: [the problem]
   Evidence: [what you verified, and what you are recalling rather than verifying]
   Why it matters: [consequence]
   What would close it: [in spec / as science — the repository distinguishes these]

## Non-blocking findings
## What passed
## Approval conditions
[What must exist before the next document — the Udacity module mapping — is rewritten]
```

## Rules

- Mark every factual claim you make as **verified** or **recalled**. The repository's own rule is
  "never cite from recall", and a review that breaks it is worth less than no review.
- If a criticism applies to plan 01 as well, say so — it may mean the pivot changed nothing relevant.
- "Inconclusive" is an acceptable verdict on any individual attack.
- Do not rewrite the plan. Find the problem; the author fixes it.
