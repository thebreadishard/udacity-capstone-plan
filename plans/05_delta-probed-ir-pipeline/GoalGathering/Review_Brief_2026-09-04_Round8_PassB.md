# Review brief — Round 8, Pass B: re-assessment after the Round-7 patches and the user's decisions

**Give this only after Round-8 Pass A's findings are written down and addressed.**

---

## Your role

The same hostile examiner as Round 7 Pass B, or a colleague of equal hostility. You did not
write the Round-7 review, but you have it (it is in the folder), and your first job is to check
whether its six blocking items were **actually closed by the patches** or only re-worded. Your
second job is to attack what is new since then: the user's five decisions and two directives of
2026-09-04, and the side project that builds analytic local-CC gradients.

**A legitimate outcome is still "no green light".** Round 7 returned *conditional*. Your verdict
must be one of: green light for the promised set as now written; conditional (name the
conditions, and say whether they are in-spec or measurements); no green light (name what would
have to change).

## Standing context

Everything in the Round-7 Pass B brief still holds. Since then: the promised correction is Δ₂
only; mode E is the *guaranteed* route; a pre-registered side project aims to make mode G real
by extending PySCFAD's LNO-CCSD(T) AD gradient to frozen LNO spaces and PAH sizes; fragment
probing at R4–R6 is "a method decided by Q8", and R6 is promised as fragment-probed Δ₂; the
learned prior may enter promised rungs under a per-rung licence; M05 is a Δ₂-support
Transformer on an aromatic-heavy Hessian-QM9 corpus; the R2 set is pyrene, chrysene,
triphenylene (gas) and tetracene (matrix); the B2 machine is an 8-core laptop with 32 GB and no
CUDA GPU. Two user directives now sit in the Goal: "the goal binds; methods are means" and
"inheritance is not authority".

## What to read

Round-8 Pass A's findings first (`Professor_Review_2026-09-04_Round8_PassA.md`; if findings
were addressed, the documents will say so). Then the full plan-05 set in the plan README's
reading order, including the mapping, the proposal and the side-project note; then
`Professor_Review_2026-09-03_Round7_PassB.md` for the six items you are checking.

You may and should use web search and fetch. Cite what you opened; mark what you recalled.

## Part 1 — did the six Round-7 closures hold?

For each, answer *closed / re-worded / open* with the sentence that decides it:

1. **Q6 thresholds.** Is the noise line a formula a script can evaluate, with every symbol
   defined (σ_E, τ, q_s, the step grid)? Is the bias line measurable at R0 with what the plan
   will actually compute? Is the pattern amplitude really chosen *from* the grid and never the
   reverse?
2. **Banded prior.** Is the band width w a deck number with a rule, or a free parameter? Does
   the dry-run pair (B3LYP vs a high-exchange functional) produce a Δ whose off-diagonal
   structure is a fair calibration for CC−DFT? Is diagonal-only vs full recovery printed as
   promised?
3. **Δ₃/Δ₄ removed.** Is any trace of a CC anharmonic promise left? Is the resonance-closed
   family set defined tightly enough that the DFT cubic/quartic differencing is bounded?
4. **CMA cited, novelty rewritten.** Fair to CMA? Does the residual novelty statement in the
   research note §8 survive a second look — in particular, does anyone already do banded /
   sparse recovery of the off-diagonal block from multi-mode displacements?
5. **Cost question re-anchored.** With the side project now aiming at mode G, is the Goal's
   cost sentence coherent (guaranteed vs aimed-for), and is the size sentence's licence
   (Ladder §1) unambiguous about which mode and which prior?
6. **Q8 on direct blocks.** Is the direct-block probe specified well enough to be run (which
   pairs, how many, what displacement, how the 3×3 block is extracted from four-point
   differences of energies)? Is the "recovered vs direct" agreement test a real check or a
   tautology for pairs the deck chose because they were expected to be small?

## Part 2 — attacks on what is new

### A. The side project's physics claim

The note's §1.2 says: on a surface with frozen LNO spaces, the AD gradient with fixed spaces is
the *exact* derivative. Check this. Frozen spaces at the reference geometry are defined in the
reference geometry's AO basis; at a displaced geometry the AOs move with the nuclei. What
exactly is held fixed — coefficients in the moving AO basis, or the spaces after re-projection
by maximal overlap? Is the resulting energy a smooth function of the nuclei, and is its
derivative what the AD code computes if the projection step is inside or outside the
differentiated graph? If the projection is outside, the "exact derivative" claim has a hole
exactly the size of the projection's geometry dependence. Say how large that hole is at
q_s ≈ 0.5–1 and whether M2 (AD vs finite differences of the *same* frozen energy) would catch
it — note that finite differences of the same frozen-space energy would agree with an AD
gradient that also ignores the projection term, so M2 may pass while both are wrong relative
to the smooth surface. What check would expose that?

### B. The side project's feasibility numbers

PySCFAD's LNO-CC gradient is demonstrated to 29 atoms. Naphthalene is 18, pyrene 26, coronene
36. With cc-pVTZ, what are the fragment sizes, and is per-fragment reverse-mode AD memory on a
32 GB machine plausible at naphthalene (M3) — cite the paper's memory statements. Is "12 weeks
of logged hours" a reasonable checkpoint for M1–M3 for one person with an AI assistant, or a
fantasy? Where exactly does the LNO-CC gradient code live (the bibliography says the PySCFAD
README does not mention it)? Verify: is (T) differentiated in the released code, and is
pyscf-forge's released LNO code CCSD or CCSD(T)?

### C. The learned-prior licence

The prior may now enter promised rungs after (i) a P3 saving on the dry-run corpus and (ii) a
prior-free reference check at the rung. At R2–R3 the prior-free reference is the direct-block
probe — a handful of atom pairs. Can a prior that is wrong in the *mode-basis off-diagonal
block* pass a check that only looks at a few *real-space* blocks? If yes, the licence is not a
licence for the quantity that matters (the C–C-family frequencies). What would close it (a
prior-free diagonal-plus-band recovery at R2 as the reference? a family-level check?).

### D. Fragment probing as "a method decided by Q8"

Q8 is measured at R2–R3 on whole molecules of 26–36 atoms. R6 is a 432-atom flake probed in
fragments. Between them, nothing is measured on an actual fragment scheme unless R4 runs
(bonus). Is a coronene-size locality verdict a licence for fragment probing on a flake whose
interior has no edge within r_max of it — i.e., a different electronic environment from
anything measured? What is the cheapest measurement that would license fragments *on a
fragment* (a circumcoronene-size flake probed both whole and in fragments, compared)? Should
that be promised rather than bonus, given the user's directive that the goal binds?

### E. "Inheritance is not authority" — what else does it reopen?

The directive says a plan-04 rule survives only if it serves the goal or rests on a
measurement. Walk the inherited rules (no scale factor on anharmonic output; positions scored,
intensities reported; neutral species only; no tier-2 pre-registration before references;
matrix–gas gate; no motif transfer) and say for each whether it rests on a measurement, on the
goal, or on plan-04 habit. Any rule in the third class is now unsupported under the plan's own
directive and must be either re-justified or dropped.

### F. Decidability at R2 after the re-read

Triphenylene is now scored on gas-phase families. Verify that NIST actually has a gas-phase IR
spectrum for triphenylene (CAS 217-59-4) and at what resolution; the plan's ~4 cm⁻¹ figure is
from its own coverage probe. Does the decidability rule (gas grid smaller than the beat margin)
have a chance at 4 cm⁻¹ against margins of a few cm⁻¹, or is R2 gas-scoring inconclusive by
construction for the C–C families?

### G. The rubric fit of M05 and M06 after the decisions

M05 now trains on Hessian QM9 plus recomputed B3LYP Hessians; the mapping calls it reading 1.
Read the Module 05 rubric's dataset clauses yourself and say whether a grader would accept a
derived quantity (ωB97x−B3LYP Hessian differences) as "publicly available … not reused". M06's
VAE proposes displacement patterns; is a pattern proposer a "generative AI" project under the
Module 06 rubric or a stretch?

## Also worth your attention

- The plan-01 alarm in the side-project note: is the trigger ("exceeds the sum of the M02–M04
  buckets") measurable before those modules exist?
- Whether Round-7 Pass A's item on the pilot-note inputs still holds now that the R1
  smoothness probe (local-CC energies!) precedes the note.
- The proposal's honesty about the conditional verdict and about what was decided by whom.

## Output format

```
Verdict: [green light / conditional / no green light — and for what scope]

## Part 1 — Round-7 closures
1–6. [closed / re-worded / open — deciding sentence]

## Blocking findings
N. [Title] — Where / What / Evidence / Why it matters / What would close it

## Non-blocking findings
…

## What would settle it
[the cheapest measurements, in order]
```

Use **Round 8, issues 1–N**.
