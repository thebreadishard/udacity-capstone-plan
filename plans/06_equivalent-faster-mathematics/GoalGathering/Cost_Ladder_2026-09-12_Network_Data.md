# Cost ladder 2026-09-12 (evening) — what it would take to make plan 05 cheap enough to run many times, lever by lever, with what is measured and what is not

*Written in the autonomous evening block against the user's statement of plan 06's goal: either solve the molecular Schrödinger problem a new way within the gold standard's error, or make plan 05 so cheap that conclusions come sooner, the pipeline can run many times, and the data for the supervisor's network (plan 05 decision 32) can be generated. This note prices the second branch. Every number is marked **m** (measured, with its file) or *e* (estimate, with its rule); nothing here is a decision. Sources: plan 05 `Compute_Budget_2026-09-03.md`, `notes/Decision_Memo_2026-09-12_P13_Compute_Route.md`, the dry-run report; plan 06 X1c, X1d, X8, X9, X10, the item-33 reading note.*

## 1. What "cheap enough" has to mean in numbers

The unit is **one molecule's correction Δ₂ at the anchor's level**: a deck of local-CC energies (or gradients) at fixed geometry. Plan 05's R1 deck for naphthalene is 96 + 96 + 282 = **474 energies** (proposal §3.2; 2M diagonal ± pairs for two functionals' worth of reference points plus the off-diagonal part under the symmetry prior). Measured per-energy prices:

| price per energy | value | source |
|---|---|---|
| benzene, cc-pVTZ, tight, frozen arm | 36 min **m** | `results_m1/benzene_ccpvtz_tight.log` |
| benzene, cc-pVTZ, xtight, frozen arm | 76 min **m** (factor 2.1) | `results_m1/XTIGHT_READIN.md` |
| naphthalene, cc-pVTZ, tight | 11.5 h **m**, 19.8 GB | `results_timing/naphthalene_cc-pvtz_tight.json` |
| naphthalene, cc-pVTZ, xtight | running; *e* 42–54 h from fragments 1–2 | live log; decided Monday |
| desktop (16 cores), naphthalene tight | *e* 3–5 h (core-count rule, never timed) | Budget desktop paragraph |
| Snellius thin node, naphthalene tight | *e* 1.5–2.5 h wall, 200–300 SBU | Budget Snellius note |

So the R1 deck as planned costs, on the laptop, **1.3–3 years**; on the desktop **4–16 months**; on Snellius **15–60 node-days** (P13 memo §3). "Many times" — say a training set of tens of PAHs at R1–R2 size — is therefore out of reach by any route without a change in the deck or in the price per point. That is the branch plan 06 has to move.

## 2. The levers, each with its factor and its status

| lever | what it changes | factor on the R1 deck | status of the number | what it costs in accuracy or in prerequisites |
|---|---|---|---|---|
| **A. tight instead of xtight** (a plan-05 threshold choice, not plan-06 mathematics) | price per energy | ÷ 2.1 at benzene **m**; ÷ 3.6–4.7 at naphthalene *e* (model), measured Monday | measured at benzene | composite bias +0.47/+0.03/+0.79 cm⁻¹ at tight against +0.11/−0.01/+0.23 at xtight (decision 20, **m**); a decision the user took the other way for a reason |
| **B. fewer off-diagonal elements by a free DFT rule** (plan 06 X10, direction S4) | number of energies | pairs 47 → 19 at benzene **m** (factor 2.5 on the off-diagonal part); on the R1 deck's 282 off-diagonal energies *e* → ≈ 115, deck 474 → ≈ 300 | measured at benzene on the stand-in; **naphthalene repeat is the licence test** | none in accuracy at benzene (0.5 cm⁻¹ held by construction of the test); risk: at lower symmetry the rule may select most pairs |
| **C. substitution probing with gradients** (plan 06 S5, decision 34) | number of measurements: 6–7 products × 2 gradients | deck 474 → 12–14 **g** energy-equivalents: wins if g < 34–40 *e*; at g = 4 the deck is ≈ 50 | algebra proved (Lean), noise mild (X1d **m**), count measured at benzene (X1c **m**); **g unmeasured**, and the engine has no gradient (item 33 read: not printed anywhere) | needs the side project's gradient (M2, weeks); energies-only version costs *more* than the deck (P24 §2, X8 **m**) |
| **D. a full Hessian from gradients** (plan 05's mode G) | measurements | 2·3N = 108 gradients at naphthalene → 108 g energy-equivalents: wins if g < 4.4 *e*; dry run K_G = 64–96 gradients at benzene **m** | same prerequisite as C | same as C; C beats D only where the pattern is sparse (X8 dense row) |
| **E. engine levers from the reading** (multi-orbital fragments; item 33 S2 C: the one-orbital scheme "nearly three times more expensive") | price per energy | *e* up to ÷ 3 | reported by others for their engine; **unmeasured in ours** (one fragment per LMO today) | a software change in the LNO layer; ledger row when tried |
| **F. a smaller correction to measure at all** (plan 06 S1/S3: locality, π-only) | which elements exist | none licensed: X9 shows the correction is *longer*-ranged than the Hessian at benzene (**m**); X6 (π share) not yet run | negative at benzene | — |

Combinations that are additive: A × B (thresholds and element count are independent) → 474 → ≈ 300 energies at 2.1–4.7× lower price: **the deck in ≈ 1.5–5 months on the desktop, ≈ 1 week on four Snellius nodes** (*e*, from the P13 rows). **B stacks with C** (X11, measured the same evening on benzene: the substitution count on the X10-selected pattern is 4 products = 8 gradients, against 7 products = 14 gradients on the symmetry prior alone and 30 on the dense pattern). C or D with a measured small g is the only lever that changes the *order of magnitude*, and it is the only one that also grows with size (X8 brackets).

## 3. What this says about "running the pipeline many times"

- **With what is measured today** (A and B, both still to be confirmed at naphthalene): one R1-size molecule costs ≈ 300 energies at 3–12 h each on a desktop or a node — days to weeks per molecule, not months. A training set of tens of naphthalene-size molecules becomes a cluster-months project, not a fantasy; a training set at pyrene size (72 modes, per energy an unmeasured 5–10× naphthalene) does not.
- **With gradients at small g** (C or D): tens of energy-equivalents per molecule; the pipeline could run across the corpus. This is why the ladder's step 4 (measure g in PySCFAD with frozen spaces) is the single most valuable number the project can still buy, and why it is weeks of software work, not a reading.
- **The network's own precondition is not a cost question.** Decision 32 requires (i) that the correction's range at R2–R3 be short enough for a transferable model to exist. X9 is the first data on that: at benzene the correction is the long-range object, its range following the π system, and T3's audit says the range grows as the gap closes with size. A network trained on Δ₂ blocks would have to learn a quantity that gets *less* local towards the sizes it is meant for. That does not close decision 32 — the condition is written to be measured at R2–R3 — but it sets the expectation, and it makes the family-level labels (band positions per family, P19's transfer test) the likelier training target than atom-pair blocks.

## 4. The order in which the numbers arrive

1. **Monday:** the naphthalene xtight factor (lever A's naphthalene column, P13).
2. **After the naphthalene DFT dry run (hours, in the machine queue):** X10 on the naphthalene tensor (lever B's licence), X8/X9 real-pattern rows (lever F's second chance beyond one ring), X1c on the tensor (lever C's count at R1).
3. **Weeks, the user decides:** g (levers C/D), and with it the answer to whether plan 06 changes plan 05's order of magnitude.
4. **When tried:** lever E's factor in our engine (a ledger row).

Nothing in this note is a plan-05 change; the levers that are ready for a proposal (B, after step 2) go through a dated note as decision 34 did.
