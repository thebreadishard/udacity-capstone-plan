# Compute budget — the distinction plan 02 never made

**Date:** 2026-08-27 · **Status:** planning fact, measured · **Supersedes nothing; corrects a premise**

Plan 02 has one number for effort: roughly 10 hours per week. Every cost argument in
the plan, including §5.9 and the scope reduction frozen on 2026-08-26, rests on it.

That number conflates two resources that are not the same thing and do not have the
same size.

| resource | amount | what it limits |
|---|---:|---|
| **Human attention** | ~8 h/week | decisions, analysis, writing, gates |
| **Wall-clock compute** | ~168 h/week | how much arithmetic gets done |

The laptop is idle while its owner is at work on other projects, and idle again while
he sleeps. It is available 24 hours a day. **The two budgets differ by a factor of
twenty-one**, and the plan has been treating them as one.

---

## 1. What the freeze actually assumed

[Frozen_Ladder_and_Tolerances_2026-08-26.md](Frozen_Ladder_and_Tolerances_2026-08-26.md)
justified cutting the promise back to benzene and naphthalene like this:

> At TightPNO cost per single point, with a 10 h/week human budget and no confirmed
> HPC allocation, benzene is comfortable, naphthalene is plausible, and everything
> above it is not a promise anyone should make.

Read it carefully: a *human* budget is used to bound a *machine* cost. That is the
conflation, stated outright, in the document that set the scope.

## 2. The measured scaling

Full frequency jobs at B3LYP/6-31G* — geometry optimisation, Hessian and dipole
derivatives, 8 threads — timed on this laptop:

| molecule | atoms | wall time |
|---|---:|---:|
| benzene | 12 | 8.1 min |
| naphthalene | 18 | 28.0 min |
| anthracene | 24 | 86.0 min |
| **phenanthrene** | **24** | **40.1 min** |

A log–log fit over the first three gives

$$t \;[\text{min}] = 1.73\times10^{-3}\, N^{3.39}$$

which reproduces those three to within 10 %.

**And then phenanthrene arrived and broke it.** Anthracene and phenanthrene are
isomers: same formula, same atom count, same basis-set size. One took 86 minutes
and the other 40.

**A factor of two, at identical size.** Cost depends on molecular *shape* — how
quickly the geometry optimiser converges, how the density is distributed — and not
on atom count alone. Every extrapolation below therefore carries a factor-of-two
uncertainty that the fit does not express, and the honest reading of the tables is
"this order of magnitude", never "this many hours".

The exponent must be re-fitted as larger molecules land, and the fit needs a
shape descriptor before it deserves to be called a model.

## 3. What 168 h/week buys — harmonic

Extrapolated from the fit above. **Estimates, not measurements.**

| molecule | formula | atoms | one frequency job |
|---|---|---:|---:|
| pyrene | C₁₆H₁₀ | 26 | 1.8 h |
| chrysene, triphenylene, tetracene | C₁₈H₁₂ | 30 | 2.9 h |
| coronene | C₂₄H₁₂ | 36 | 5.4 h |
| ovalene | C₃₂H₁₄ | 46 | 12.3 h |
| **circumcoronene** | C₅₄H₁₈ | 72 | **56 h** |

Circumcoronene is a 54-carbon PAH of the size class that actually carries the
interstellar bands. Harmonic DFT on it is **a long weekend**, unattended.

## 4. What 168 h/week buys — anharmonic

A quartic force field by numerical differentiation of analytic Hessians needs roughly
$6N$ displaced Hessians. Hessians without dipole derivatives are cheaper by the
measured factor of 2.3.

| molecule | atoms | Hessians | total | at 168 h/week |
|---|---:|---:|---:|---:|
| benzene | 12 | 72 | 4.1 h | 0.02 weeks |
| naphthalene | 18 | 108 | 24.1 h | 0.14 weeks |
| anthracene | 24 | 144 | 85.0 h | 0.51 weeks |
| pyrene | 26 | 156 | 120.7 h | 0.72 weeks |
| coronene | 36 | 216 | 502.9 h | 2.99 weeks |

**An anharmonic DFT force field for pyrene is five days of a machine that is otherwise
doing nothing.** The plan currently promises neither pyrene nor anharmonic DFT beyond
naphthalene.

## 5. What this does NOT change

Three things, and the first is the one that matters.

**The gold rung is still unmeasured.** Every number above is DFT. Coupled cluster is
orders of magnitude dearer, and *this project has never timed one*. Gate G1a exists
precisely to fix that, and it is still open. Nothing in this document licenses a claim
about what coupled cluster can reach.

**The human budget is unchanged.** Eight hours a week still has to cover every
decision, every gate, every piece of writing and every judgement about whether a
result means anything. More compute produces more results to judge, and judging is the
scarce half.

**Wall clock is not the only machine limit.** 31 GB of RAM and a single 8-core node
still bound what fits. Circumcoronene at 56 h is a time estimate, not a memory one.

## 6. The bottleneck moved, and that changes what to optimise

If compute were scarce, the right instinct is to compute less and think harder about
which calculation to run.

It is not scarce. So the right instinct inverts:

- **Queue generously.** A calculation that might be useful costs a night of a machine
  that would otherwise be off. The cost of running it is near zero; the cost of
  needing it in three weeks and not having it is three weeks.
- **Order by what each job decides**, never by size. This was already applied today:
  reordering the molecule queue moved the decisive bay measurement from eleven hours
  out to four.
- **Spend the human hours on judgement.** Anything a human does that a script could
  have done is drawn from the budget that is actually short.
- **Batch across a whole session.** Deciding what to run next should happen once per
  human session, not once per job.

## 7. Design rules for unattended compute

Every long-running calculation from here on must satisfy all seven. The current
locality probe already satisfies 1–4.

| # | Rule | Why |
|---|---|---|
| 1 | Each job writes its result the moment it finishes | A run killed at hour nine keeps eight hours of work |
| 2 | The skip rule requires the **complete** artefact set | A half-written result must not be mistaken for a finished one |
| 3 | A failure never stops the queue | One non-converging geometry must not cost a night |
| 4 | Store the expensive intermediate, not just the summary | The Hessian costs an hour; re-deriving a number from it costs a second |
| 5 | Append a timestamped line per job to a run log | So elapsed time is a measurement rather than a memory |
| 6 | Regenerate a status file after every job | One glance answers "where is it", without reading logs |
| 7 | Nothing waits for a human except a gate | If a script needs an answer at 03:00, the design is wrong |

## 8. What must be measured next

Items 1 and 2 were answered the same afternoon this document was written, by the
batch runner in §10. They are kept here with their answers because the answers
change what the remaining items mean.

1. ~~A coupled-cluster single point on benzene, timed.~~ **Done.** CCSD(T)/6-31G* runs
   in **19.6 s**. The gold rung is not out of reach on this machine; it is out of reach
   at a useful *basis*.
2. ~~Whether it is affordable at all.~~ **Bounded.** CCSD(T) fails at 114 basis functions
   even with 28 GB, and succeeds at 102. The wall is the (T) step's in-core $O^3V^3$
   storage, not the method and not the molecule.
3. **Where the wall sits in molecule size** at the basis that fits. Queued as
   `01d_cc_naphthalene_631gs`, 156 basis functions, expected to fail and thereby
   bracket the gold rung to within one molecule.
4. **A shape term for the cost model**, or an explicit admission that there is none.
5. **A memory ceiling measurement** for the DFT side: the largest molecule that fits in
   31 GB, found by trying rather than by estimating.

## 9. Effect on the frozen scope

## 9. Effect on the frozen scope

**The freeze is not reopened by this document, and must not be.**

Its stated reasoning contains the conflation identified in §1, so the *premise* is now
known to be partly wrong. But its *conclusion* concerns the gold rung, and the gold
rung is exactly the thing still unmeasured. A scope built on an unmeasured cost cannot
be widened on the strength of a different cost that was measured instead.

The governance already says how this ends: a freeze is superseded by a **new dated
document**, never edited. The condition for writing that document is item 1 and 2 of
§8 — a timed coupled-cluster single point and Hessian.

Until then the promise stands at benzene and naphthalene, neutral, and everything
above it remains bonus. What has changed is that the *bonus* is now considerably more
likely to be delivered.

---

## 10. Measured the same afternoon, by the runner this document argued for

Written before any of it existed, §8 called a timed coupled-cluster single point "the
missing number in the entire plan". The batch runner produced four in six minutes.

| job | basis functions | outcome |
|---|---:|---|
| CCSD(T) / cc-pVDZ, 24 GB | 114 | **failed** — not enough memory (ccsd) |
| CCSD(T) / cc-pVDZ, 28 GB | 114 | **failed** — same |
| CCSD / cc-pVDZ | 114 | **19.6 s** |
| CCSD(T) / 6-31G* | 102 | **19.6 s**, E = −231.530413 |

Read together: **CCSD(T) on benzene runs on this laptop in twenty seconds.** The wall
is neither the method nor the molecule — it is the perturbative triples step, whose
in-core storage goes as $O^3V^3$ and lands near 14 GB at 102 basis functions and 22 GB
at 114. Drop the (T) and cc-pVDZ fits; keep the (T) and shrink the basis and it fits.

So the gold rung exists on hardware already owned, at a basis this project would
rightly call inadequate. Canonical CCSD(T) tops out near 110 basis functions here.

**That is why the plan named ORCA and DLPNO — except that was an assumption then and
is a measurement now.** It also sharpens what the freeze in §9 is waiting for: not
whether coupled cluster runs, but whether a *local* coupled cluster reaches a basis
worth the name.

---

## Where the numbers come from

| source | what it holds |
|---|---|
| [compute_budget_2026-08-27.py](../probes/compute_budget_2026-08-27.py) | the fit and every extrapolation in this document |
| [hardware_capability_2026-08-27.py](../probes/hardware_capability_2026-08-26.py) | the first timings, and the machine specification |
| [results_dft_locality/](../probes/results_dft_locality/) | the three measured jobs the fit is built on |

## Open

- **The cost model has no shape term.** Anthracene and phenanthrene are isomers and
  differ by a factor of two in wall time. Until the fit carries something beyond atom
  count, every projection here is an order of magnitude rather than a number.
- Every anharmonic figure in §4 assumes $6N$ Hessians, which is a textbook count and
  not something this project has verified for its own pipeline.
- §3 and §4 predate the coupled-cluster measurements in §5 and have not been redone
  with them.
