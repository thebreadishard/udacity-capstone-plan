# X21 — the pattern-product count across the molecule ladder (17 September 2026)

*Run: `x21_pattern_products_ladder.py`. Counting only — the pattern is block-diagonal by irrep, so the
colouring depends on the irrep block sizes alone. Same colouring code as X14 (x1c), same deck sizes as
`deck_counts_planar.py`. Recovery error 0.0e+00 at every molecule: exact at every size, not just at
naphthalene.*

## The count

| molecule | M | same-irrep pairs | H deck (energies) | products k | gradients | break-even g |
|---|---|---|---|---|---|---|
| benzene | 30 | 52 | 139 | 6 | 12 | 11.6 |
| naphthalene | 48 | 141 | 291 | 9 | 18 | **16.2** |
| anthracene | 66 | 277 | 499 | 12 | 24 | 20.8 |
| phenanthrene (C2v) | 66 | 584 | 1,015 | 23 | 46 | 22.1 |
| pyrene | 72 | 332 | 580 | 13 | 26 | 22.3 |
| tetracene | 84 | 456 | 759 | 15 | 30 | 25.3 |
| perylene | 90 | 526 | 858 | 16 | 32 | 26.8 |
| pentacene | 102 | 682 | 1,075 | 18 | 36 | **29.9** |

**The gradient count grows linearly with the mode count while the pair count grows quadratically.**
k ≈ M/5.7 across the ladder: 6 products at benzene, 18 at pentacene, while the pairs go 52 → 682. That is
the whole scaling argument in one line, and it says the advantage **grows** with molecule size — which is
the direction the project needs, since the goal is large PAHs.

Phenanthrene is the useful stress case: C2v has only four irreps, so it carries 584 eligible pairs
against anthracene's 277 at the same mode count, and its product count doubles to 23. Even there the
break-even is 22.1. Lower symmetry costs, but does not break the route.

## What it costs at the measured g

M2a cell 3 (17 September, one repeat, provisional) gives **g = 4.07** for LNO-CCSD(T). Against that:

| molecule | Δ₂ from gradients alone | total, keeping the 2M single-mode block for c₀, φ_iii, Δ₄ | saving |
|---|---|---|---|
| benzene | 2.8× cheaper | 60 energies + 12 gradients = 109 vs 139 | 1.3× |
| naphthalene | 4.0× cheaper | 96 + 18 = 169 vs 291 | **1.7×** |
| anthracene | 5.1× cheaper | 132 + 24 = 230 vs 499 | 2.2× |
| phenanthrene | 5.4× cheaper | 132 + 46 = 319 vs 1,015 | 3.2× |
| pyrene | 5.5× cheaper | 144 + 26 = 250 vs 580 | 2.3× |
| tetracene | 6.2× cheaper | 168 + 30 = 290 vs 759 | 2.6× |
| perylene | 6.6× cheaper | 180 + 32 = 310 vs 858 | 2.8× |
| pentacene | 7.3× cheaper | 204 + 36 = 351 vs 1,075 | 3.1× |

## Correction to the note of 17 September 08:0x

That note said the gradient route is "about 5× cheaper" at naphthalene. That figure is the **Δ₂ part
alone** (4.0× at the measured g). The 18 gradients give Δ₂ and nothing else; c₀, the cubic φ_iii and the
diagonal quartic Δ₄ still have to be read from the single-mode ± block, which is 2M = 96 energies at
naphthalene. Counting those, the honest saving on the whole deck is **1.7×**, not 5×.

The saving grows with size for the same reason the break-even does: the diagonal block grows linearly
while the deck it replaces grows quadratically. At pentacene it is 3.1×.

## What this does and does not settle

- **Settles:** the route scales. The advantage does not shrink at the sizes the project cares about; it
  grows. Coronene (D6h, degenerate irreps, not counted here) should be better still and is worth adding.
- **Does not settle:** g. 4.07 is one repeat at 6-31G on a contended machine; the three-repeat run and
  the thread-count control are running. Everything in the right-hand columns moves with that number, and
  the break-even column does not.
