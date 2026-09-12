# Result note 2026-09-12 (evening) — X10: which off-diagonal pairs must be measured, and DFT alone can (mostly) say which

*Script `experiments/x10_dft_predictable_pairs.py`; tables `x10_dft_predictable_pairs.md` / `.json`. Direction S4 ("reduce the target"), on plan 05's sealed benzene dry-run tensor (stand-in Δ = BHHLYP − B3LYP) and its symmetry-prior file. Every number from the files. A candidate for a plan-05 proposal, **not** a proposal: one molecule, one stand-in.*

## 1. Question

X2 showed that only a handful of off-diagonal Δ₂ elements move any band by more than 0.5 cm⁻¹, all of them between modes of the same irreducible representation. Plan 05's symmetry prior already excludes the other pairs. The remaining question is whether the same-irrep pairs that *matter* can be told apart from those that do not **before** anything is measured — with DFT information only, which is free. Second-order perturbation theory gives the lever: an element Δ_ij shifts bands by roughly Δ_ij² / |ω_i² − ω_j²|, and the denominator is known from the DFT Hessian. The pre-stated losing condition for the DFT-only rule: it needs more than half the eligible pairs to reach 0.5 cm⁻¹.

## 2. Result

Eligible pairs at benzene: 57 same-irrep pairs, of which 10 join the two components of one degenerate E level (no independent element; the accidental A1g/B1u near-degeneracy at 1020 cm⁻¹ is kept because its element is real and moves a band by 1.7 cm⁻¹) — 47 ranked. Keeping the diagonal and all 47, zeroing the other 388 elements: bands move 0.002 cm⁻¹, so the symmetry prior is exact to that level. Dropping every off-diagonal element: 19.6 cm⁻¹.

| ranking of the 47 pairs | pairs needed for ≤ 0.5 cm⁻¹ | naive energies 2M + 2n | pairs for ≤ 0.1 cm⁻¹ |
|---|---|---|---|
| P1 — DFT-only, 1/‖ω_i² − ω_j²‖ | **19** | 98 | 19 |
| P2 — oracle magnitude ‖Δ_ij‖ (a perfect learned prior) | 17 | 94 | 19 |
| P3 — oracle effect (the best possible order) | 6 | 72 | 16 |

Rank correlation of P1 with the measured drop-one effect: Spearman 0.75 (the oracle magnitude: 0.83). The DFT-only rule passes its losing condition (19 < 23.5) and lands within two pairs of a perfect element-size prior. Its top of the list is the right one — the accidental near-degeneracy (1.7 cm⁻¹) and the pair (15, 18) at 1186/1357 cm⁻¹ that carries 19.6 of the 19.6 cm⁻¹ — and its misses are pairs whose element is large despite a wide denominator (the E2g/E2g and E1u/E1u pairs between 1070–1210 and 1530–1660 cm⁻¹, effects 0.5–1.0 cm⁻¹), which the denominator alone cannot see and a learned prior on ‖Δ_ij‖ could.

## 3. What it would be worth, stated with its caveats

- In the naive count (2 energies per diagonal mode, 2 per kept pair) the benzene deck would be 98 energies against the measured K = 448. The naive count is a lower bound: the dry run's deck adds off-diagonal energies in batches of 40 and buys, with them, the noise column and the stopping test of decisions 8/12; the per-pair cost convention was read from `deck.json` the same evening: 30 single + 30 q2 patterns for the diagonal (2 per mode), 184 two-mode patterns for 92 distinct pairs (2 per pair, 38 of them held out), and 120 multi-mode patterns of 3–6 modes (23 held out) — so 2M + 2n is the deck's own price for its single and pair patterns, and the measured K = 448 additionally contains the multi-mode patterns, the hold-out and the stopping rule's extra batches. Even so, the ratio of *pairs* (19 of 47 eligible, of 435 total) is the number that carries over, and it is a factor 2.5 below the symmetry prior alone.
- **This is a different kind of saving from S5's.** Substitution (S5) reduces the number of *measurements* per element and pays only with gradients; X10 reduces the number of *elements* and pays with energies as they are. It is what direction S4 always meant, now with a free rule and a measured count.
- **It is not a licence.** One molecule, one stand-in functional pair; at benzene the eligible pairs are few because the symmetry is high. Naphthalene (D2h, more modes per irrep, smaller denominators between more pairs) is the test that decides whether the rule keeps a useful fraction; a rule that selects most pairs there has saved nothing. The pre-stated form for naphthalene: same three rankings, same losing condition (more than half the eligible pairs).
- **Relation to Module 05.** The learned Δ₂-support predictor is, in this table, an attempt to move from P1 towards P2 (Spearman 0.75 → 0.83, pairs 19 → 17). At benzene that gain is two pairs; whether it is worth a network is exactly the effect-size question of the pilot note's item 5, and X10 gives the pilot note a measured baseline: **the free rule is the line a learned prior must beat.**

## 4. What changes

- Ledger S4: alive and sharpened; **candidate proposal P25 to plan 05** (a DFT-only pair ranking inside the symmetry prior, with the naphthalene repeat as its licence test) — written as a candidate only; the user decides whether it is drafted.
- Plan 05's pilot note, item 5 (P3 effect size): X10's P1 line is the baseline any learned prior must beat; noted for the skeleton, not entered in the frozen text.
- Nothing else moves.

## 5. Addendum the same evening — X11: the two savings stack

`experiments/x11_sparse_pattern_products.py` counts Powell–Toint substitution products (X1c's code) on the patterns X10 selects:

| pattern (mode space, benzene) | pairs | direct energies (2M + 2n) | maxr | products k | gradients 2k |
|---|---|---|---|---|---|
| diagonal + X10's P1 top-19 (DFT-only rule) | 19 | 98 | 3 | **4** | 8 |
| diagonal + P2 top-17 (oracle magnitude) | 17 | 94 | 3 | 3 | 6 |
| diagonal + P3 top-6 (oracle effect) | 6 | 72 | 2 | 2 | 4 |
| symmetry prior alone (all 47 eligible pairs) | 47 | 154 | 7 | 7 | 14 |
| X1c's noise pattern θ = 0.5 µE_h | 87 | 234 | 6 | 7 | 14 |
| dense | 435 | 930 | 30 | 30 | 60 |

The substitution count falls with the pattern (7 → 4 under the free rule), so lever B (fewer elements) and lever C (products with gradients) of the cost ladder **do stack**: a benzene correction good to 0.5 cm⁻¹ would take 8 gradients under the free DFT rule, 14 under the symmetry prior alone, against the 448 energies of the measured deck — if g is small and the engine has a gradient. Recovery verified exact (≤ 2 × 10⁻¹⁶) on every row. Same caveats as §3: one molecule, one stand-in, naive energy count.

