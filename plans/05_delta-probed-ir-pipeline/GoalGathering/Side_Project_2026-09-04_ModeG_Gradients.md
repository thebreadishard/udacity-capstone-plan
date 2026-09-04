# Side project — analytic local-CC gradients with frozen domains (mode G)

**Status.** Pre-registered side project, dated 2026-09-04, opened by user decision ("punt 2:
niet akkoord — we kunnen de software uitbreiden"). Nothing here is a result. This note is
committed **before** any line of the side project's code exists, so that its milestones, its
kill criterion and what happens on success or failure cannot be shaped by how it goes.

**Relation to the plan.** Mode E (energy-only probing) remains the **guaranteed route**: every
promise of plan 05 holds without this side project. The side project's purpose is to make
**mode G** — Δ₂ recovered from analytic local-CC gradients, at O(1)-class probe counts — real
on rungs R1–R3, where no production code offers it today. If it succeeds, mode G becomes the
primary route on R1–R3 by dated note and the size sentence becomes earnable; if it fails, the
plan continues in mode E and the failure is reported with its measured reason.

---

## 1. Why this is feasible at all (the argument of record)

1. **The gradient exists in one open code.** PySCFAD (Zhang, Li, Ye, Berkelbach & Chan, JCP
   161, 014109, 2024; bibliography item 33) computes LNO-CCSD(T) nuclear gradients by
   automatic differentiation, open source, Python/JAX, fragment-parallel over MPI, benchmarked
   on molecules to about 29 atoms. The underlying LNO-CC energy code is in pyscf-forge
   (item 48: the 1.1.0 changelog of 2026-02-20 lists "LNO-CCSD for molecules and PBC
   systems"; the (T) variant is stated in the PySCF ten-year overview, item 49, at snippet
   level — **M1 verifies which of LNO-CCSD / LNO-CCSD(T) the released code actually offers, and
   where PySCFAD's LNO-CC gradient code lives**, since the PySCFAD README fetched on 2026-09-04
   does not mention it). Nothing has to be derived by hand.
2. **Our frozen-domain design removes the hard term.** The general local-CC gradient must
   differentiate through the geometry dependence of domains and PNO/LNO spaces. Plan 05
   freezes those spaces at the reference geometry for every probe (Ladder §3). On that
   surface the AD gradient with fixed LNO spaces — which is what PySCFAD already does — is the
   **exact** derivative of the surface being probed. What is an approximation in general is
   exact for us.
3. **One codebase closes both software gaps.** Psi4 cannot freeze domains; ORCA freezes them
   for DLPNO-MP2 only. In PySCF/PySCFAD the fragment definitions and LNO vectors are Python
   objects that can be stored at the reference geometry and reloaded at every probe geometry.
   The same code therefore supplies mode E's frozen-domain energies *and* mode G's gradients.
4. **Verification is cheap and already planned.** The gradient is checked against finite
   differences of the same frozen-domain energies at benzene and naphthalene — energies the
   R1 smoothness probe produces anyway.

## 2. Scope (what is built, and what is not)

**Built:**

- (a) **Frozen LNO spaces across displacements** in pyscf-forge's LNO-CCSD(T): store the
  fragment list, the localized occupied orbitals and each fragment's LNO vectors at the
  reference geometry; at a displaced geometry, map localized orbitals by maximal overlap and
  reuse the stored spaces. Print a deck hash of the frozen spaces.
- (b) **Per-fragment reverse-mode AD with graph release** in PySCFAD's LNO-CCSD(T) gradient,
  so that peak memory scales with the largest fragment, not the molecule; checkpointing /
  rematerialisation of the (ov|vv)-class intermediates; optional disk offload per fragment.
- (c) **The probe interface**: given a pattern geometry, return E_CC − E_DFT and ∇E_CC − ∇E_DFT
  with frozen spaces, in the response format Distilled §3 defines for mode G.

**Not built:** hand-derived Lagrangians; anything for ORCA or Psi4; (T)-gradient theory beyond
what PySCFAD already differentiates; GPU ports; any change to the recovery solver.

## 3. Milestones and the kill criterion (frozen now)

| # | Milestone | Pass condition (printed by a `probes/` script) | Machine |
|---|---|---|---|
| M1 | Frozen LNO spaces reproduce the reference energy | E(reference geometry, reloaded spaces) − E(reference geometry, fresh spaces) = 0 to 10⁻⁹ E_h; at a displaced benzene geometry the frozen-space energy is smooth along one mode (second-difference scatter under the Q6 noise line at q_s = 0.5) | B2 laptop |
| M2 | Gradient correct at benzene | AD gradient with frozen spaces vs central finite differences of the frozen-space energy, cc-pVTZ: max component deviation ≤ 10⁻⁵ E_h/bohr | B2 laptop |
| M3 | Gradient correct and affordable at naphthalene | same check at naphthalene/cc-pVTZ; wall-clock per gradient and peak memory printed; peak memory ≤ 28 GB | B2 laptop |
| M4 | Pyrene fits somewhere | one gradient at pyrene/cc-pVTZ with frozen spaces, peak memory and wall-clock printed, on the laptop (per-fragment offload) or on a B3 machine under the budget's preconditions | B2 or B3 |

**Kill criterion.** The side project stops, by dated note, if **M3 is not reached within 12
weeks of B1 hours logged to its bucket (see §4), or if M2 fails after the AD and the
finite-difference reference have both been re-derived once**. A stopped side project is
reported with its last printed milestone; mode E continues unchanged. The 12-week figure is a
checkpoint in plan 05's sense: crossing it forces a dated decision (continue knowingly, with
the plan-01 alarm on the table / stop), never a silent overrun.

**What success means.** M3 passed: mode G is licensed on R1 and the gradient-availability
probe (Compute_Budget §4.2) prints "yes" there. M4 passed: mode G is licensed on R2, and R3
is classified by the rule with the measured wall-clock. On each rung where mode G is licensed,
the pilot note's K_cap(G) is filled from the dry run and the cost record carries `mode G`.

## 4. Budget and the plan-01 alarm

- **B1**: a **separate bucket, "side project: mode G"**, so that its hours are visible on their
  own line. Human hours remain uncapped (Goal, Hours); the 12-week figure above is a checkpoint
  on *this bucket*, not a cap on the project.
- **The plan-01 alarm applies here first.** Plan 01 died of two-thirds of its hours on
  infrastructure. This side project *is* infrastructure and has no rubric module of its own.
  If its bucket exceeds the sum of the M02–M04 buckets at any monthly review, a written review
  of what the hours are buying is mandatory before the next hour is logged to it.
- **B2/B3**: M1–M3 are laptop work; M4 may classify as B3 and then waits on the budget's three
  preconditions like any other B3 object.

## 5. What changes in the plan on success (by dated note, not now)

- Goal, "Cost" question: mode G becomes the primary case on the rungs where it is licensed;
  mode E stays the guaranteed route and the reported fallback.
- Ladder §1: the mode-G size sentence is no longer labelled bonus on licensed rungs.
- Distilled §3, anchor level: the deck names LNO-CCSD(T) in PySCF/PySCFAD with frozen LNO
  spaces as the anchor code for licensed rungs.
- Distilled §3, patterns: mode-G patterns (a gradient gives 3N responses per pattern) replace
  the 2M diagonal floor on licensed rungs; K is measured as before.
- The withdrawn Δ₃/Δ₄ promise **may be reopened by a further dated note** — gradients at
  two-mode displacements give the three-index cubic constants that energies cannot — but this
  note does not reopen it.

## 6. What changes on failure

Nothing in the promised set. The cost record on every rung says `mode E`; the size sentence
is not written; this note's last milestone table is attached to the Module 08 paper as the
measured reason.

## 7. Risks named now

1. **Time sink (the plan-01 failure mode)** — mitigated by the separate bucket, the 12-week
   checkpoint and the alarm rule of §4.
2. **JAX memory on a 32 GB laptop** — per-fragment graph release is the design answer; if it is
   not enough at pyrene, M4 is B3 work and says so.
3. **(T) under AD on frozen spaces** — numerically untested in this setting; M2/M3 measure it
   directly against finite differences.
4. **Being overtaken** — if the PySCF or ORCA developers release a frozen-domain local-CC(T)
   gradient first, this side project switches to using it and reports the switch; the
   milestones stay the same.
5. **Scope creep into the recovery solver or GPU work** — excluded by §2; a change needs a new
   dated note.

## 8. Provenance and verification status

PySCFAD paper: item 33 (arXiv abstract read; full text read by the Round-7 Pass B reviewer).
PySCFAD repository and pyscf-forge LNO-CCSD(T): items 48–49, statuses as recorded in the
bibliography on 2026-09-04. The frozen-domain argument of §1.2 is this plan's own reasoning,
not a published result; M1–M2 are the measurements that test it.
