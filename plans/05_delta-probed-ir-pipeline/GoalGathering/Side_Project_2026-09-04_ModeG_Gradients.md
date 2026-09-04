# Side project — analytic local-CC gradients with frozen spaces (mode G)

**Status.** Pre-registered side project, dated 2026-09-04, opened by user decision ("punt 2:
niet akkoord — we kunnen de software uitbreiden"); revised the same day after Round-8 Pass A
(issues 3–7, 16). Nothing here is a result. This note is committed **before** any line of the
side project's code exists, so that its milestones, its kill criterion and what happens on
success or failure cannot be shaped by how it goes.

**Relation to the plan.** Mode E (energy-only probing) is the **guaranteed route** — guaranteed
*given* a frozen-space local-CC energy code, which is main-project work (probe M1 below, under
Ladder stop 1), not this side project's. This side project starts where mode E's needs end: it
aims to make **mode G** — Δ₂ recovered from analytic local-CC gradients with frozen spaces —
real on rungs R1–R3, where no production code offers it today. If it succeeds, mode G is the
route on the rungs it licenses; if it fails (M2–M5), every promise of plan 05 holds in mode E
and the failure is reported with its measured reason.

**Notation.** See the Goal's glossary. M1–M5 are the milestones below; τ is the smallest beat
margin (pilot-note item 2); q_s the pattern amplitude (item 13); B1–B3 the budgets.

---

## 1. Why this is feasible at all (the argument of record, with its hedges)

1. **A gradient of this kind is reported in one open code.** Zhang, Li, Ye, Berkelbach & Chan
   (JCP 161, 014109, 2024; bibliography item 33) report LNO-CCSD(T) nuclear gradients by
   automatic differentiation in PySCFAD, fragment-parallel over MPI, benchmarked on molecules
   to about 29 atoms. **Where that code lives is not yet located** (the PySCFAD README fetched
   2026-09-04 does not mention it; item 49) and the released pyscf-forge LNO code is listed as
   **LNO-CCSD**, the (T) variant being snippet-grade (items 48–49). Locating the code and
   verifying (T) is M2's first step, not an assumption of this note.
2. **Frozen spaces are expected to remove the hard term — this is the plan's own reasoning,
   not a published result.** The general local-CC gradient must differentiate through the
   geometry dependence of domains and PNO/LNO spaces. Plan 05 freezes those spaces at the
   reference geometry (Ladder §3). *If* the frozen spaces are held fixed as coefficient vectors
   in the moving AO basis and the maximal-overlap mapping is inside the differentiated graph,
   the AD gradient is the derivative of the surface actually probed. Whether the mapping step
   can be differentiated, and how large its geometry dependence is at q_s ≈ 0.5–1, is what M2
   measures; Round-8 Pass B is asked to attack exactly this.
3. **One codebase would close both software gaps.** Psi4 cannot freeze domains; ORCA freezes
   them for DLPNO-MP2 only. In PySCF/PySCFAD the fragment definitions and LNO vectors are
   Python objects — M1 tests whether they can be stored at the reference geometry and reloaded
   at displaced geometries.
4. **Verification is cheap.** Gradients are checked against finite differences of the same
   frozen-space energies at benzene and naphthalene — and, because that check cannot see
   non-smoothness the two share, against the Q6 noise lines as well (§3).

## 2. Scope (what is built, and what is not)

**Main-project work, not this side project (M1, under Ladder stop 1):** frozen LNO spaces
across displacements in pyscf-forge's LNO-CC — store the fragment list, the localized occupied
orbitals and each fragment's LNO vectors at the reference geometry; at a displaced geometry map
localized orbitals by maximal overlap and reuse the stored spaces; print a deck hash of the
frozen spaces. Mode E needs this whether or not the side project exists.

**Built here:**

- (a) **Locate and verify the engine**: PySCFAD's LNO-CC gradient code and version; whether
  (T) is differentiated in the released code; whether pyscf-forge's LNO code is CCSD or
  CCSD(T). Printed as the first side-project output.
- (b) **Per-fragment reverse-mode AD with graph release**, so that peak memory scales with the
  largest fragment, not the molecule; checkpointing / rematerialisation of the (ov|vv)-class
  intermediates; optional disk offload per fragment.
- (c) **Frozen spaces inside the differentiated graph** (the maximal-overlap mapping
  differentiated, or its geometry dependence measured and bounded).
- (d) **The probe interface**: given a pattern geometry, return E_CC − E_DFT and ∇E_CC − ∇E_DFT
  with frozen spaces, in the response format Distilled §3 defines for mode G.

**Not built:** hand-derived Lagrangians; anything for ORCA or Psi4; (T)-gradient theory beyond
what the located code already differentiates; GPU ports; any change to the recovery solver.

## 3. Milestones and the kill criterion (frozen now)

Before the pilot note, the gradient-availability probe is **run/no-run at the equilibrium
geometry only** (Compute_Budget §4.2) — no displaced-geometry gradient, hence no Δ₂ column,
exists before the note (Round-8 Pass A issue 6). M2–M5 run **after** the pilot note.

| # | Milestone | Pass condition (printed by a `probes/` script) | Machine |
|---|---|---|---|
| M1 (main project) | Frozen LNO spaces reproduce the reference energy | E(reference geometry, reloaded spaces) − E(reference geometry, fresh spaces) = 0 to 10⁻⁹ E_h; at displaced benzene geometries along one mode the frozen-space energy's second-difference scatter is **printed** (the verdict against the Q6 noise line waits for the pilot note's τ) | B2 laptop |
| M2 | Engine located; gradient correct and smooth at benzene | (a) printed; AD gradient with frozen spaces vs central finite differences of the frozen-space energy, cc-pVTZ: max component deviation ≤ 10⁻⁵ E_h/bohr; **and** the mode-G noise line of Q6 (σ_g ≤ 2.8·τ·q_s along the three Q6 modes) under the line at the deck's q_s | B2 laptop |
| M3 | Gradient correct, smooth and affordable at naphthalene | same two checks at naphthalene/cc-pVTZ; wall-clock per gradient and peak memory printed; peak memory ≤ 28 GB | B2 laptop |
| M4 | Pyrene fits somewhere | one gradient at pyrene/cc-pVTZ with frozen spaces, both checks, peak memory and wall-clock printed, on the laptop or on a B3 machine under the budget's preconditions | B2 or B3 |
| M5 | Coronene run/no-run | one gradient at coronene/cc-pVTZ with frozen spaces; run/no-run, wall-clock and peak memory printed (this is the gradient-availability probe's answer at R3) | B3 by expectation |

**Kill criterion.** The side project stops, by dated note, if **M3 is not reached within 12
calendar weeks of the pilot note's commit date**, or if M2's correctness check fails after the
AD and the finite-difference reference have both been re-derived once. A stopped side project
is reported with its last printed milestone; mode E continues unchanged. The 12-week figure is
a checkpoint in plan 05's sense: crossing it forces a dated decision (continue knowingly, with
the plan-01 alarm on the table / stop), never a silent overrun.

**What success means.** Mode G is *licensed* on a rung when (i) the milestone for that rung's
molecule passed both checks (M2 → R0, M3 → R1, M4 → R2, M5 → R3), and (ii) the gradient probe
printed "run" there. No pilot-note item changes: K_cap(G) for every rung is frozen in the note
from the **gradient-mode dry run** (DFT gradients exist, so the DFT-vs-DFT dry run is run in
both modes; Compute_Budget §4.1), and the cost record simply carries `mode G`. "Beat" language
on a mode-G rung requires Q6's mode-G noise line to have passed at that rung's size class, like
mode E's (Ladder §1).

## 4. Budget and the plan-01 alarm

- **B1**: a **separate bucket, "side project: mode G"**, for M2–M5 and items (a)–(d). M1 hours
  are booked to *pipeline infrastructure* (they are main-project work). One bucket per entry
  (the booking rule); the kill clock is calendar time from the pilot note, so it cannot be
  stopped by booking elsewhere.
- **The plan-01 alarm applies here first.** Plan 01 died of two-thirds of its hours on
  infrastructure. This side project *is* infrastructure and has no rubric module of its own.
  **Review every 4 calendar weeks from the pilot note's commit date**: if the side-project
  bucket exceeds the pipeline-infrastructure bucket at any review, a written review of what
  the hours are buying is mandatory before the next hour is logged to it.
- **B2/B3**: M2–M3 are laptop work; M4–M5 may classify as B3 and then wait on the budget's
  three preconditions like any other B3 object.

## 5. What changes in the plan on success (by dated note, not now)

- Goal, "Cost" question: mode G is the route on the rungs it licenses; mode E stays the
  guaranteed route and the reported fallback.
- Ladder §1: the mode-G size sentence needs M2–M5 (licences at R1, R2, R3) and Q8(c) on K.
- Distilled §3, anchor level: the deck names the located LNO-CC code with frozen spaces for
  licensed rungs.
- Distilled §3, patterns: mode-G patterns (a gradient gives 3N responses per pattern) replace
  the 2M diagonal floor on licensed rungs; K is measured as before.
- The withdrawn Δ₃/Δ₄ promise **may be reopened by a further dated note** — gradients at
  two-mode displacements give the three-index cubic constants that energies cannot — but this
  note does not reopen it.

## 6. What changes on failure

Nothing in the promised set, **provided M1 (main project) passed**; if M1 fails, Ladder stop 1
fires for the anchor code regardless of this side project. On side-project failure the cost
record on every rung says `mode E`; the mode-G size sentence is not written; this note's last
milestone table is attached to the Module 08 paper as the measured reason.

## 7. Risks named now

1. **Time sink (the plan-01 failure mode)** — mitigated by the separate bucket, the calendar
   12-week checkpoint and the 4-weekly alarm rule of §4.
2. **JAX memory on a 32 GB laptop** — per-fragment graph release is the design answer; if it is
   not enough at pyrene, M4 is B3 work and says so.
3. **The frozen-space mapping is not differentiable, or its geometry dependence is not small**
   — then §1.2's argument has a hole the size of that dependence; M2 measures it and Pass B is
   asked to size it in advance.
4. **(T) under AD on frozen spaces** — numerically untested in this setting, and possibly not
   in the released code at all (item 48); M2 verifies both.
5. **Being overtaken** — if the PySCF or ORCA developers release a frozen-space local-CC(T)
   gradient first, this side project switches to using it and reports the switch; the
   milestones stay the same.
6. **Scope creep into the recovery solver or GPU work** — excluded by §2; a change needs a new
   dated note.

## 8. Provenance and verification status

PySCFAD paper: item 33 (arXiv abstract read; full text read by the Round-7 Pass B reviewer).
PySCFAD repository and pyscf-forge LNO code: items 48–49 (repository page and changelog fetched
2026-09-04; gradient code unlocated; (T) snippet-grade). The frozen-space argument of §1.2 is
this plan's own reasoning, not a published result; M1–M2 are the measurements that test it.
