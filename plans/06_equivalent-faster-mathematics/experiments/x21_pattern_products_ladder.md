# X21 — the pattern-product count across the molecule ladder (17 September 2026)

*Run: `x21_pattern_products_ladder.py`. Counting only — the pattern is block-diagonal by irrep, so the
colouring depends on the irrep block sizes alone. Same colouring code as X14 (x1c), same deck sizes as
`deck_counts_planar.py`. Recovery error 0.0e+00 at every molecule: exact at every size, not just at
naphthalene. Rewritten in the evening; the afternoon version is superseded — see the last section.*

## The count

| molecule | M | same-irrep pairs | H deck (energies) | products k | gradients 2k | break-even g |
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
k ≈ M/5.7 across the ladder: 6 products at benzene, 18 at pentacene, while the pairs go 52 → 682. The
advantage **grows** with molecule size, which is the direction the project needs. Phenanthrene is the
stress case: C2v has four irreps, so 584 eligible pairs against anthracene's 277 at the same mode count
and a product count of 23 — and it still breaks even at 22.1.

## What the energy deck supplied, read from the proposal rather than assumed

The afternoon version of this note kept 2M single-mode energies beside the gradients, for c₀, φ_iii and
Δ₄, and arrived at a whole-deck saving of 1.7× at naphthalene. That kept a block the plan does not use
that way. The reading copy (§3.2–3.3) states the pipeline: GVPT2 on **the DFT anharmonic constants**,
the **Δ₂-corrected harmonic part**, and a **first-order geometry term** — "the coupled-cluster force at
the DFT geometry — the odd part of the totally symmetric single-mode ± pairs whose even part gives the
diagonal". Intensities come from the DFT dipole derivatives. So the energy deck supplies three things
and nothing else:

| supplied by the single-mode energy block | under the gradient route |
|---|---|
| the diagonal of Δ₂ (even part) | inside the 2k products — X14 row (a) covers the diagonal |
| the CC force at the DFT geometry (odd part, totally symmetric modes) | **one gradient at the reference geometry**, all M components at once |
| c₀, and Δ₄ to clean the energy read | c₀ is not a frequency input; Δ₄ cleaned a read that no longer happens |

**The deck becomes 2k + 1 gradients and no energies.** The cubic and quartic constants were never the
deck's job; they come from DFT, as in the L1//L0 composite schemes plan 06's own literature pass found.

## What it costs, at the measured g

g for LNO-CCSD(T), M2a cell 3, benzene 6-31G, three repeats each: **5.71 at eight threads** (the setting
the deck runs at) and **7.19 at four threads** on a machine running three jobs (t_E 14.0 vs 26.0 s, t_grad
79.9 vs 186.8 s — the gradient parallelises better than the energy). The eight-thread value is the
headline; the four-thread value is the conservative bound.

| molecule | old deck (energies) | gradients 2k+1 | at g = 5.71 | saving | at g = 7.19 | saving |
|---|---|---|---|---|---|---|
| benzene | 139 | 13 | 74 | 1.9× | 93 | 1.5× |
| naphthalene | 291 | 19 | 108 | **2.7×** | 137 | 2.1× |
| anthracene | 499 | 25 | 143 | 3.5× | 180 | 2.8× |
| phenanthrene | 1,015 | 47 | 268 | 3.8× | 338 | 3.0× |
| pyrene | 580 | 27 | 154 | 3.8× | 194 | 3.0× |
| tetracene | 759 | 31 | 177 | 4.3× | 223 | 3.4× |
| perylene | 858 | 33 | 188 | 4.6× | 237 | 3.6× |
| pentacene | 1,075 | 37 | 211 | **5.1×** | 266 | 4.0× |

## The day's three readings of one number, for the record

| when | reading | why it changed |
|---|---|---|
| 08:0x | ≈ 5× at naphthalene | Δ₂ part only, at the one-repeat g = 4.07 |
| 11:3x | 1.7× | kept 2M energies for cubic/quartic terms the plan takes from DFT; g still 4.07 |
| 17:5x | 2.1× | deck is 2k + 1 gradients per the proposal's own text; g = 7.19 from three repeats at four threads |
| 18:14 | **2.7×** (2.1× conservative) | eight-thread control: g = 5.71 at the production thread count; 7.19 kept as the bound |

Two things still move this table: the eight-thread control on g, and the quartic contamination of the
gradient-difference read at q = 1, which X14/X20 treat as exact and which stage C's mode G measured only
on the DFT stand-in (family errors 0.05–0.21 cm⁻¹ at 96 gradients). Neither moves the break-even column.
