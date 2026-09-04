# Review brief — Round 9, Pass B: did the Round-8 closures hold?

**Give this only after Round-9 Pass A's findings are written down and addressed.**

---

## Your role

The same hostile examiner as Rounds 7 and 8, or a colleague of equal hostility. Round-8 Pass B
returned *conditional* and wrote: "whether those closures hold is for a further pass to say."
You are that pass. Your job is narrower than Round 8's: for each of Round-8 Pass B's eight
blocking findings and ten non-blocking ones, decide **closed / re-worded / open** with the
deciding sentence, then attack only what the closures themselves introduced. Do not re-open
Round 6 or Round 7 items unless a Round-8 closure re-broke them.

Your verdict must be one of: **green light** (for which scope, under which written conditions),
**conditional** (name the conditions and whether each is in-spec or a measurement), or **no
green light** (name what must change). If the R0–R1 programme and the promised set beyond R1
deserve different verdicts, give both.

## Standing context

Everything in the Round-8 Pass B brief still holds. Since then: the eight blocking closures
(Q6 estimator; noise-aware stopping rule; absolute η₈; four-part fragment licence; frozen-space
object with M1 assignment log and M2 projection term; u_band decidability; mode E on every rung;
anchor basis and the canonical feasibility probe) and the ten non-blocking ones; decision 7
closed (nothing submitted; the draft QM9 repo will be renamed); the author's own fetch of the
PySCFAD and pyscf-forge listings.

## What to read

Round-9 Pass A's findings first (`Professor_Review_2026-09-04_Round9_PassA.md`; if addressed,
the documents will say so). Then the full plan-05 set in the README's reading order (Goal
glossary first), then `Professor_Review_2026-09-04_Round8_PassB.md` for the eighteen items you
are checking. Web access is allowed; cite what you open; mark what you recall.

## Part 1 — the eighteen Round-8 closures

For each of Round-8 Pass B's findings 1–18: closed / re-worded / open, with the sentence that
decides it. Where a closure is "re-worded", say what a *closed* version would say.

## Part 2 — attacks on what the closures introduced

### A. The σ estimator

σ_E is the RMS residual of nine ΔE(q) points about a degree-4 polynomial. With nine points and
five fitted coefficients there are four residual degrees of freedom: what is the statistical
uncertainty of σ_E itself, and can a single outlier (one assignment switch) hide in the fit or
dominate it? Is a degree-4 fit on q ∈ [−1, 1] able to absorb genuine Δ₃/Δ₄ structure so that
σ_E measures noise and not physics — or does it absorb noise too? Is the mode-G estimator
(degree 3 on the gradient component) consistent with the mode-E one (the derivative of a
degree-4 polynomial is degree 3 — yes; say whether the two σ's are then comparable). Recommend
a grid or a degree if the plan's is wrong.

### B. The noise-aware stopping rule

ρ\* = c·ρ_noise with ρ_noise = σ/RMS_resp(rung). RMS_resp depends on the pattern amplitude q_s
(fixed from the Q6 grid) and on the *size* of Δ₂ at that rung (unknown until probed). If Δ₂ is
small at a rung (a family where DFT is already right), RMS_resp is small, ρ_noise is large, and
ρ ≤ c·ρ_noise is reached quickly — at a K that has not resolved anything. Is that the right
behaviour ("no correction to recover, stop early") or a loophole ("K looks small because the
signal was small")? Does the cost record's K then mean the same thing across rungs? Propose the
sentence that makes it honest (e.g. the cost record carries RMS_resp and σ alongside K).

### C. The absolute η₈ and the coupling scale S

S = √(Σ direct²/n_pairs) over the deck's pair list. Show with the reviewer's own numbers (near
C–C coupling ≈ 2.8×10⁻³ E_h/bohr², far pairs at noise ≈ 10⁻⁵) how S depends on the near/mid/far
mix, and whether a mid pair — the only pairs where physics and prior can disagree — can ever
fail at a plausible η₈. If the test is decided by the near pairs, say what to normalise by
instead (per-distance-shell scale; or a fixed multiple of σ_coupling).

### D. The fragment licence, parts (b), (b′), (c)

(b) at coronene "at the smallest passing radius r_f": with coronene's radius ≈ 3.7 Å and a
π-conjugated correction, can any r_f smaller than the molecule pass, and what does the plan
report if none does (it says "that is the result" — is R6 then licensed or not?). (b′) at
circumcoronene "conditional on B3 classification": if B3 never materialises, is R6 licensed on
(a), (b), (c) alone — and is that enough? (c) "fragments of radius r_f and r_f + one ring carved
from the rung's own DFT geometry": for an interior pair of C₃₈₄H₄₈, how large are those
fragments (atoms, basis functions at the R6 deck basis), and is the convergence test itself
affordable on the named machine or B3? Which r_f does R6 use — coronene's, circumcoronene's, or
its own? Say whether the licence, as written, can be earned at all under the plan's own budgets.

### E. The frozen-space object and M2's projection term

Ladder §3 now defines the frozen space as the stored LNO vectors projected onto the displaced
geometry's virtual space and Löwdin-orthonormalised, with maximal-overlap mapping of the
occupied orbitals. Two questions. (i) Is the *fragment* definition itself frozen (which
localized orbitals belong to which fragment), and what happens when the occupied localized
orbitals at a displaced geometry are not a permutation of the reference ones (mixing, not
switching)? (ii) M2's third number is AD(projection inside) − AD(projection under stop_gradient).
Is "projection inside the graph" differentiable through the Löwdin step (matrix inverse square
root — yes, away from degeneracy) and through the maximal-overlap assignment (a discrete
argmax — no)? What does JAX do at an assignment switch, and does M1's assignment log catch a
switch that occurs *between* grid points?

### F. u_band and the temperature term

The decidability rule's temperature term is "a declared hot-band shift per family from a pinned
reference, or, until one is pinned, the labelled uncertainty with its estimated magnitude". Who
estimates the magnitude, from what, and can it be set small enough to make a family decidable?
Is there a published PAH hot-band shift measurement the plan could pin now (cite if you find
one)? Does u_band, as defined, make the **R0–R1** NIST bands (benzene, naphthalene) decidable
for the C–C families, or does the same problem reach the licence rungs?

### G. The canonical feasibility probe and the bias line

One canonical CCSD(T) energy of benzene at cc-pVTZ on a 32 GB laptop, "extrapolated to the
Hessian count". What extrapolation factor is defensible (a numerical Hessian by central
differences along 30 modes = 61 energies; a canonical gradient-based Hessian = 12×3×2 = 72
gradients, each several × an energy)? If the probe says days, is "days" inside the 168 h
checkpoint or B3? Is the fallback (cc-pVDZ, both arms) adequate for a *bias* line whose purpose
is to see the freezing error — does the freezing bias depend strongly on basis?

## Also worth your attention

- Whether Round-8's non-blocking 11 (learned-prior licence residuals) and 12 (M05/M06 rubric
  fit) are now closed or merely acknowledged.
- The change table's rows 28–32 against the documents.
- Whether any closure introduced a **new pilot-note input** that leaks a local-CC Δ₂ number
  (the canonical feasibility probe is one energy; the u_band table is lab-side; the
  noise-injection column is DFT-only — confirm).

## Output format

```
Verdict: [green light / conditional / no green light — and for what scope]

## Part 1 — Round-8 closures
1–18. [closed / re-worded / open — deciding sentence]

## Blocking findings
N. [Title] — Where / What / Evidence / Why it matters / What would close it

## Non-blocking findings
…

## Attack-by-attack disposition (A–G)

## What would settle it
```

Use **Round 9, issues 1–N**.
