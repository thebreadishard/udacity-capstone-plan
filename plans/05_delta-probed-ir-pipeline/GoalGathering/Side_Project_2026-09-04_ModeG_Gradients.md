# Side project — analytic local-CC gradients with frozen spaces (mode G)

**Status.** Pre-registered side project, dated 2026-09-04, opened by user decision ("punt 2:
niet akkoord — we kunnen de software uitbreiden"); revised the same day after Round-8 Pass A
(issues 3–7, 16) and Round-8 Pass B (findings 5, 9, 15, 17, 18). Nothing here is a result. This
note is committed **before** any line of the side project's code exists, so that its
milestones, its kill criterion and what happens on success or failure cannot be shaped by how
it goes.

**Relation to the plan.** Mode E (energy-only probing) is the **guaranteed route** — guaranteed
*given* a frozen-space local-CC energy code, which is main-project work (probe M1 below, under
Ladder stop 1), not this side project's. This side project starts where mode E's needs end: it
aims to make **mode G** — Δ₂ recovered from analytic local-CC gradients with frozen spaces —
real on rungs R0–R3. Mode E runs on every rung R1–R3 that runs; where this side project's
milestone licenses mode G, mode G runs **in addition** (Ladder §3). If it fails (M2–M5), every
promise of plan 05 holds in mode E and the failure is reported with its measured reason.

**Notation.** See the Goal's glossary. M1 is the main-project frozen-space probe; M2–M5 are the
milestones below; τ is the smallest beat margin (pilot-note item 2); q_s the pattern amplitude
(item 13); σ_g the mode-G noise scatter (Ladder §3 estimator); B1–B3 the budgets.

---

## 1. Why this is feasible at all (the argument of record, with its facts and its hedges)

1. **The engine exists in released open code — verified, not hedged.** Zhang, Li, Ye,
   Berkelbach & Chan (JCP 161, 014109, 2024; bibliography item 33) report LNO-CCSD(T) nuclear
   gradients by automatic differentiation in PySCFAD, fragment-parallel over MPI, benchmarked on
   molecules to about 29 atoms. On 2026-09-04 the Round-8 Pass B reviewer and then the author's
   own fetch (item 49) found the code: **`pyscfad/lno/`** contains `lno_base.py`, `ccsd.py`,
   `ccsd_t.py`, `_checkpointed.py` and MPI variants, with an `examples/lno/` directory; the
   gradient is `jax.grad` of the differentiable energy, so there is no separate "gradient file".
   The released energy code in **pyscf-forge `pyscf/lno/`** contains `lnoccsd_t.py`,
   `ulnoccsd_t.py` and `ulnoccsd.py` (item 48): **(T) is present, closed- and open-shell**; the
   changelog line "LNO-CCSD" was a summary. What remains unmeasured is behaviour with frozen
   spaces (M1, M2) and memory at PAH sizes (M3, M4): the paper gives no GB figures and no
   gradient-vs-energy wall-clock, only that memory is dominated by ⟨ov|vv⟩ with `jax.checkpoint`
   recomputation and that the (T) backward pass is computed on the fly.
2. **Frozen spaces as a differentiable object — the plan's own reasoning, defined precisely and
   tested by M1–M2.** Ladder §3 defines the object: stored localized occupied orbitals and
   per-fragment LNO vectors in the AO basis; at a displaced geometry, occupied orbitals mapped by
   maximal overlap (assignment printed), stored virtual vectors **projected onto the new
   virtual space and Löwdin-orthonormalised**; the correlation energy is evaluated in that
   space. Between assignment switches E_frozen(x) is smooth. **If the projection is inside the
   differentiated graph**, the AD gradient is the exact derivative of E_frozen; if it is outside
   (NumPy, or `stop_gradient`), the gradient misses the response of the energy to the geometry
   dependence of the projected space — a term that is not zero for a truncated CC energy
   (non-stationarity with respect to kept/discarded virtual rotations; Pinski & Neese report
   "dramatic errors" when PNO constraints are omitted for relaxed properties, item 51, record
   grade). M2 prints that term. **The maximal-overlap assignment is discrete** and can switch
   along symmetric modes of the two D₆h rungs (benzene, coronene); a switch is a µE_h-class
   discontinuity that free spaces do not have — M1's assignment log and the Q6 grids (which now
   include a totally symmetric mode) are built to see it.
3. **One codebase closes both software gaps.** Psi4 cannot freeze domains; ORCA freezes them
   for DLPNO-MP2 only. In PySCF/PySCFAD the fragment definitions and LNO vectors are Python
   objects — M1 tests whether they can be stored, projected and reloaded as §1.2 requires.
4. **Verification is cheap, and one check is genuinely new.** Gradients are checked against
   finite differences of the **same re-projected frozen-space energies** at benzene and
   naphthalene, and against the Q6 mode-G noise line (because AD and FD agree on a non-smooth
   surface, correctness is not smoothness). The PySCFAD paper validated its LNO-CC gradients
   against canonical CCSD(T) AD gradients only, never against finite differences of its own LNO
   energy; M2 would be the first AD-vs-FD check of a frozen-space LNO surface.

## 2. Scope (what is built, and what is not)

**Main-project work, not this side project (M1, under Ladder stop 1):** frozen spaces across
displacements in pyscf-forge's LNO-CC — the Ladder §3 object: store; map by maximal overlap;
project and orthonormalise; evaluate; print the assignment permutation and E(displaced, frozen)
− E(displaced, fresh) per point; deck-hash the stored spaces. Mode E needs this whether or not
the side project exists.

**Built here:**

- (a) **Confirm and pin the engine**: PySCFAD and pyscf-forge commit hashes and versions used;
  whether (T) is differentiated end-to-end in `pyscfad/lno/ccsd_t.py` as released. Printed as
  the first side-project output.
- (b) **Per-fragment reverse-mode AD with graph release**, so that peak memory scales with the
  largest fragment, not the molecule; checkpointing / rematerialisation of the ⟨ov|vv⟩-class
  intermediates (building on `_checkpointed.py`); optional disk offload per fragment.
- (c) **Frozen spaces inside the differentiated graph**: the maximal-overlap mapping and the
  projection/orthonormalisation of Ladder §3 implemented as JAX operations, with a switch to
  place the projection under `stop_gradient` for M2's diagnostic.
- (d) **The probe interface**: given a pattern geometry, return E_CC − E_DFT and ∇E_CC − ∇E_DFT
  with frozen spaces, in the response format Distilled §3 defines for mode G.

**Not built:** hand-derived Lagrangians; anything for ORCA or Psi4; (T)-gradient theory beyond
what the released code differentiates; GPU ports; any change to the recovery solver.

## 3. Milestones and the kill criterion (frozen now)

Before the pilot note, the gradient-availability probe is **run/no-run at the equilibrium
geometry only** (Compute_Budget §4) — no displaced-geometry gradient, hence no Δ₂ column, exists
before the note. M2–M5 run **after** the pilot note.

| # | Milestone | Pass condition (printed by a `probes/` script) | Machine |
|---|---|---|---|
| M1 (main project) | Frozen spaces exist and behave | (i) E(reference geometry, reloaded spaces) − E(reference geometry, fresh spaces) = 0 to 10⁻⁹ E_h (a round-trip sanity check); (ii) along one **totally symmetric**, one **degenerate** and one non-symmetric benzene mode, nine points on q ∈ [−1, 1]: the assignment permutation per point and E(displaced, frozen) − E(displaced, fresh) in µE_h — the freezing bias and any switch, **printed without a verdict** (the τ it would be judged against does not exist yet) | B2 laptop |
| M2 | Engine pinned; gradient correct, smooth, and its projection term measured, at benzene | (a) printed; AD gradient (projection inside the graph) vs central finite differences of the **re-projected** frozen-space energy, cc-pVTZ: max component deviation ≤ 10⁻⁵ E_h/bohr; the Q6 **mode-G noise line** (σ_g ≤ 2.8·τ·q_s, Ladder §3 estimator) under the line at the deck's q_s along the Q6 modes; and a **third printed number**: AD(projection inside) − AD(projection under `stop_gradient`) at one displaced geometry per Q6 mode — the size of §1.2's hole | B2 laptop |
| M3 | Gradient correct, smooth and affordable at naphthalene | the same three printouts at naphthalene/cc-pVTZ; wall-clock per gradient and peak memory printed; peak memory ≤ 28 GB | B2 laptop |
| M4 | Pyrene fits somewhere | one gradient at pyrene/cc-pVTZ with frozen spaces, correctness (FD along the Q6 modes, six energies) and σ_g, peak memory and wall-clock printed, on the laptop or on a B3 machine under the budget's preconditions | B2 or B3 |
| M5 | Coronene: both checks | one gradient at coronene in the R3 deck basis with frozen spaces: run/no-run, wall-clock, peak memory, **and** AD-vs-FD along the three Q6 modes (six frozen-space energies) and σ_g at the R3 size class — the two checks the licensing rule requires | B3 by expectation |

**Kill criterion.** The side project stops, by dated note, if **M3 is not reached within 12
calendar weeks of the pilot note's commit date**, or if M2's correctness check fails after the
AD and the finite-difference reference have both been re-derived once. A stopped side project
is reported with its last printed milestone; mode E continues unchanged. The 12-week figure is
a checkpoint in plan 05's sense: crossing it forces a dated decision (continue knowingly, with
the plan-01 alarm on the table / stop), never a silent overrun.

**What success means.** Mode G is *licensed* on a rung when (i) the milestone for that rung's
molecule passed **both checks** — correctness against re-projected finite differences and the
mode-G noise line at that size class (M2 → R0, M3 → R1, M4 → R2, M5 → R3) — and (ii) the
gradient probe printed "run" there. No pilot-note item changes: K_cap(G) and the stopping
constant for mode G are frozen in the note from the **gradient-mode, noise-injected dry run**
(Compute_Budget §4.1). On a licensed rung mode G runs in addition to mode E and the rung carries
two cost records. "Beat" language from mode G requires its noise line to have passed (Ladder
§1).

## 4. Budget and the plan-01 alarm

- **B1**: a **separate bucket, "side project: mode G"**, for M2–M5 and items (a)–(d). M1 hours
  are booked to *pipeline infrastructure* (they are main-project work), which makes that bucket
  large early and the alarm below correspondingly quiet at first — said here so it is not a
  surprise. One bucket per entry (the booking rule); the kill clock is calendar time from the
  pilot note, so it cannot be stopped by booking elsewhere.
- **The plan-01 alarm applies here first.** Plan 01 died of two-thirds of its hours on
  infrastructure. This side project *is* infrastructure and has no rubric module of its own.
  **Review every 4 calendar weeks from the pilot note's commit date**: if the side-project
  bucket exceeds the pipeline-infrastructure bucket at any review, a written review of what
  the hours are buying is mandatory before the next hour is logged to it.
- **B2/B3**: M2–M3 are laptop work; M4–M5 may classify as B3 and then wait on the budget's
  three preconditions like any other B3 object. The Round-8 reviewer's recalled sizing
  (cc-pVTZ: naphthalene ≈ 412 functions, ⟨ov|vv⟩ per fragment of order 8 GB — M3 plausible on
  32 GB; pyrene ≈ 620 functions, of order 30 GB — B3; coronene ≈ 888) is recorded as an
  expectation, not a number; M3 and M4 print the facts.

## 5. What changes in the plan on success (by dated note, not now)

- Goal, "Cost" question: mode G's K on the rungs it licenses stands beside mode E's K_off.
- Ladder §1: the mode-G size sentence needs M3, M4 and M5 (both checks each) and Q8(c) on K.
- Distilled §3, anchor level: the deck pins the PySCFAD/pyscf-forge commits used.
- Distilled §3, patterns: mode-G patterns (a gradient gives 3N responses per pattern) run
  alongside the mode-E patterns on licensed rungs; K is measured per mode as before.
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
3. **The frozen-space surface is not smooth on the D₆h rungs** (assignment switches), or the
   projection term is large — M1's assignment log and M2's third number measure both; a
   gradient that is exact for a non-smooth surface is as noisy as the energies, which is why the
   mode-G noise line is part of every milestone.
4. **(T) under AD on frozen spaces** — the code exists (item 48–49, fetched); its numerical
   behaviour on projected spaces is M2's measurement.
5. **Being overtaken** — if the PySCF or ORCA developers release a frozen-space local-CC(T)
   gradient first, this side project switches to using it and reports the switch; the
   milestones stay the same.
6. **Scope creep into the recovery solver or GPU work** — excluded by §2; a change needs a new
   dated note.

## 8. Provenance and verification status

PySCFAD paper: item 33 (arXiv abstract read; full text read by the Round-7 and Round-8 Pass B
reviewers — memory statements and the canonical-only validation come from the Round-8 reading).
PySCFAD `pyscfad/lno/` and pyscf-forge `pyscf/lno/` directory listings: fetched by the Round-8
Pass B reviewer and again by the author on 2026-09-04 (items 48–49). The frozen-space object of
§1.2 is defined in Ladder §3 and is this plan's own construction, modelled on ORCA's DLPNO-MP2
mechanism (item 29); M1–M2 are the measurements that test it. Pinski & Neese on omitted PNO
constraints: item 51, record grade.
