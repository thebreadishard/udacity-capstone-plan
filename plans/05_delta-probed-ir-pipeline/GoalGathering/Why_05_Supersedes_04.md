# Why plan 05 supersedes plan 04

**Status.** Argument of record, 2026-09-03. Plan 04 is **not** wrong; it is superseded because
its cost sits in the wrong object. Plan 04's folder is **kept in the tree** for now — removing
it is the user's decision, not this document's; plans 01–03 remain git history only.

## What plan 04 got right and plan 05 keeps verbatim

Everything that was governance rather than method: the relative and measured criterion; the
accuracy/reach split; the frozen opponents and scoreboards; the M03 matrix–gas decidability
gate; resonance-explicit routes only; no scale factor on anharmonic output; positions scored,
intensities reported; the three separated budgets with human hours uncapped; the pilot note
written before any pipeline-vs-lab number; mandatory null rows; fail-closed sentences; the
four-tier expectations; the value hierarchy (unknown territory is the goal). Plan 04's Round-6
Pass A and Pass B findings, and the user decisions that closed them, **bind plan 05 too** and
are not re-litigated.

## The block plan 04 could not lift

Plan 04's Round-6 Pass B (2026-09-02) found, and the plan accepted, that:

- the R2–R3 point factory (~10⁴ local-CC points per molecule, source-conversation assertion)
  is a B3 object without an allocation (finding 4);
- R6 is either unaffordable or unfalsifiable as promised (finding 5);
- local-CC curvature noise may swallow the anharmonic signal (finding 2, Q6).

Plan 04 answered with honesty devices (classification rule, fail-closed R6, Q6 probes). It did
not change the arithmetic. On 2026-09-03 the user reported an independent assistant's estimate
that a single large PAH would still take "many, many hours" of supercomputer time under plan
04 — an assertion, but the same direction as everything measured or asserted before it.

The reason is structural. Plan 04 pays coupled-cluster prices to learn a *whole surface* over
3N−6 coordinates, almost all of which DFT already describes; the CC anchor's only new
information is the CC−DFT difference, which is small, smooth and short-ranged. A method whose
cost grows with the size of the surface cannot reach C₃₈₄H₄₈-class species on any allocation
this project will hold.

## What plan 05 changes

One thing: **where the coupled-cluster budget is spent and how it is collected.**

| | Plan 04 | Plan 05 |
|---|---|---|
| Object paid for at CC level | a per-molecule surface (10³–10⁴ points) | the **CC−DFT force-constant correction Δ** (Δ₂ first; Δ₃/Δ₄ on scored families) |
| How CC data is collected | sampled geometries, learned by a neural surface | **probed**: a hashed set of simultaneously multi-displaced geometries, Δ recovered by sparse recovery in the DFT normal-mode basis |
| Point count with size | grows with the surface | intended to **saturate** (measured, per rung: K) — the whole bet, and a probe |
| Where CC enters the spectrum | anharmonic correction on a DFT Hessian | **harmonic Δ₂ first** (where the hybrid-QFF literature says CC pays most), then Δ₃/Δ₄ |
| Local-CC noise | averaged by the fit; Q6 smoothness probe | **domains frozen at the reference geometry** for every probe; noise floor measured with/without freezing (Q6) |
| Machine | CPU laptop → cluster | GPU DFT Hessians where available; local CC as before; cluster/rented GPU under B3 rules |
| Deep-learning component | Transformer surface (the thesis object) | Transformer **Δ-prior** for the recovery — an efficiency experiment (P3), never the promised route |

Changes of *frozen intent* relative to plan 04, each recorded here so Pass A cannot mistake
them for drift: (i) Distilled §3 "anharmonic machinery" no longer contains a learned surface
as the promised route; (ii) the P3 comparison axis changes from Δ-learning-vs-direct to
learned-prior-vs-uninformed-prior at matched probe count; (iii) the Q-gates gain Q7 (probing
licence) and Q8 (locality decay); (iv) the pilot note gains K and r_c and loses N_min.

## What plan 05 does not change

The ladder, its rungs and its claim types; the opponents; the scoreboards; the tolerances;
the three budgets and the hours directive; the module skeleton 02–09; the no-transfer rule as
plan 04 wrote it (fragment probing, which would touch it, is an **open user decision**, not
part of the promised set).

## The measurement that would say plan 05 was a mistake

If, at R1–R3, the Δ₂ elements between atoms do **not** decay with distance (Q8), or the
recovered Δ₂ does not reproduce a directly computed reference within the beat margin at the
frozen K (Q7), plan 05 has no size advantage over plan 04 and says so. Those two probes are
cheap relative to any point factory and run before any reach rung. A plan-05 that fails them
is reported as "Δ is not local / not recoverable at this size, measured thus"; it does not
quietly become plan 04 with a new name.
