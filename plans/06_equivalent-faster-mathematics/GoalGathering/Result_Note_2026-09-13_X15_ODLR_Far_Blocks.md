# Result note 2026-09-13 — X15: the far blocks of PAH Hessians are low-rank in norm but not at 0.5 cm⁻¹ (ODLR fails plan 05's tolerance for the mean field)

*Script `experiments/x15_odlr_far_blocks.py`; tables `x15_odlr_far_blocks.md` / `.json`. Inputs: plan 02's B3LYP/6-31G* Hessians of eight PAHs (git 57a7910). Serves the decision rule's branch M (the ODLR restatement of T3 proposed in the O1NumHess reading note) and branch C (lever C beyond the symmetry prior). Every number from the files. Pre-stated losing condition (reading note §3): r* above a third of the block dimension.*

## 1. What was measured

For each molecule, two atom groups along the long inertial axis — the first and last third ("distant thirds") and the two halves — and the block H_AB of the mass-weighted Hessian between them: its singular values, its numerical rank at relative thresholds 10⁻², 10⁻³, 10⁻⁴, and **r\***, the smallest rank at which replacing H_AB (and H_BA) by its rank-r truncation moves no harmonic band by more than 0.5 cm⁻¹.

## 2. Result

| molecule | groups (distant thirds) | min A–B distance | block | singular values (rel.) | band shift with far blocks zeroed | **r\*** | r\*/dim |
|---|---|---|---|---|---|---|---|
| naphthalene | 6/6 | 4.7 bohr | 18×18 | 1, 0.48, 0.25, 0.12, … | 44.7 cm⁻¹ | 14 | 0.78 |
| anthracene | 8/8 | 9.4 | 24×24 | 1, 0.18, 0.09, 0.06, … | 4.3 | 9 | 0.38 |
| tetracene | 10/10 | 9.3 | 30×30 | — | 19.3 | 13 | 0.43 |
| chrysene | 10/10 | 8.3 | 30×30 | — | 3.4 | 9 | **0.30** |
| phenanthrene | 8/8 | 5.4 | 24×24 | — | 14.8 | 15 | 0.62 |
| pyrene | 8/8 | 5.4 | 24×24 | — | 28.4 | 19 | 0.79 |
| triphenylene (1 imag.) | 10/10 | 6.4 | 30×30 | — | 21.9 | 20 | 0.67 |
| coronene (1 imag.) | 12/12 | 7.1 | 36×36 | — | 257 | 30 | 0.83 |

Halves (larger, adjacent blocks): r\*/dim 0.51–0.89 for all eight; zeroing them shifts bands by 120–430 cm⁻¹.

**In norm, ODLR is visible** — the singular values of the far blocks fall by an order of magnitude within a handful of terms (anthracene: second singular value 0.18 of the first), which is what O1NumHess reports and exploits, and what its 6–12 cm⁻¹ errors on conjugated chains reflect. **At 0.5 cm⁻¹ it is not usable:** even the two best cases — the linear acenes, whose end rings sit 9.3–9.4 bohr apart — need 9 of 24 (anthracene) and 13 of 30 (tetracene) singular directions; only chrysene reaches the pre-stated third exactly (9 of 30, 0.30), anthracene misses it (0.38), every other molecule fails it by a wide margin. The compact PAHs (pyrene, coronene) have no genuinely distant groups at this size (5–7 bohr, two to four bonds), and there the far blocks need most of their rank.

## 3. Reading

1. **The X8 lesson holds for rank as it held for norm:** a structure that is real in the Frobenius sense (decaying singular values) can still be unusable at band level, because band positions are a global function of the force-constant matrix and 0.5 cm⁻¹ is a small fraction of the far blocks' effect (4–260 cm⁻¹ here). O1NumHess is honest about this — it aims at thermochemistry and a few cm⁻¹ — and plan 05 aims at an order of magnitude tighter.
2. **For T3:** the restatement proposed in the O1NumHess reading note ("Δ₂ = local + low-rank") can only be a *norm-level* conjecture; as a statement about what plan 05 may drop or truncate at its tolerance it is false already for the mean-field Hessian at these sizes. The correction Δ₂ is a separate object (X15 on naphthalene's Δ₂ when the BHHLYP half exists), but the mean field sets the expectation, and X9 showed the correction to be the longer-ranged of the two.
3. **For lever C beyond the symmetry prior:** an ODLR-type reduction of the product count on low-symmetry PAHs is not licensed at 0.5 cm⁻¹ by this test; the symmetry prior (X14: k = largest irrep block, exact) remains the only licensed structure, and for low-symmetry PAHs the gradient route degrades towards mode G's 2·3N gradients — which still beats an energy deck of order N² whenever g is below N/2 or so (X14 §2).
4. **Caveat on the files:** triphenylene and coronene carry one imaginary mode each in plan 02's Hessians; their rows are indicative only. The acenes and chrysene are clean.

## 4. What changes

- Ledger S1: X15 done — ODLR of the DFT Hessian's far blocks holds in norm, fails at 0.5 cm⁻¹ (r\*/dim 0.30–0.83); T3's ODLR form is filed as a norm-level conjecture only. Branch M's 1 December review has one more closed door.
- Cost ladder lever F: the ODLR route added and marked "not licensed at tolerance (X15)".
- Decision rule §2: X15 row added, done.
- Nothing enters plan 05's frozen text; O1NumHess stays the reference for "few gradients" with its accuracy class stated beside it.
