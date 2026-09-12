# Plan 06 — reading note (2026-09-12): Coleman & Moré, "Estimation of sparse Hessian matrices and graph coloring problems"

*Read in full on 2026-09-12 from the open Cornell technical report TR 82-535 (December 1982; 31 pages,
scanned, no text layer — read page by page as images), the report version of the 1984 *Mathematical
Programming* paper (28(3), 243–270, DOI 10.1007/BF02612334; Crossref record verified; the journal text
itself is paywalled and was not opened — page numbers below are the report's). Powell & Toint (1979,
SIAM J. Numer. Anal. 16(6), 1060–1074, DOI 10.1137/0716078) is **not** open anywhere (Semantic Scholar:
closed; SIAM only) and the user cannot download it either; it is on the supervisor's PDF request list
(item 29). Everything attributed to Powell & Toint below is **as reported by Coleman & Moré**, not read.*

## 1. What the paper does (pp. 1–4)

Problem: given the sparsity structure of a symmetric matrix `A`, find directions `d₁ … d_p` such that the
products `A d₁ … A d_p` determine `A` uniquely, with `p` as small as possible (each product = one gradient
difference). Direct methods based on *partitions* of the columns are analysed in §2–5, *triangular
substitution* (indirect) methods in §6–7, numerics in §8. Two negative complexity results and one clear
practical recommendation.

## 2. Definitions and theorems, and how they match ours

| Coleman & Moré | statement (report page) | plan 06 counterpart |
|---|---|---|
| **consistent partition** (p. 4–5) | whenever `a_ij ≠ 0`, the group of column `j` has no other column with a non-zero in row `i` | CPR-valid; our `colGraph`-proper colouring (T1a) |
| **symmetrically consistent partition** (p. 5) | whenever `a_ij ≠ 0`, the group of `j` has no other column with a non-zero in row `i`, **or** the group of `i` has no other column with a non-zero in row `j` | **verbatim our `SymmValid`** (T1b note §2; Lean `SymmValid`) |
| `G_u(A)` intersection graph of the columns; `G_s(A)` adjacency graph (p. 6) | columns adjacent when they share a row / when `a_ij ≠ 0` | `colGraph P` / our `H` |
| **Lemma 2.1** (p. 7) | with non-zero diagonal, `G_u(A) = G_s(A)²` | our remark that `colGraph = H²` when the diagonal is in `P` |
| **symmetric p-colouring** (p. 7) | a proper colouring of `G` that is not a 2-colouring of any path of length 3 | our §3 finding "a constraint on paths of three edges, not on pairs" — now with its name |
| **Theorem 2.2** (p. 8) | with non-zero diagonal: `φ` is a symmetric colouring of `G_s(A)` **iff** it induces a symmetrically consistent partition | the exact characterisation our note asked for; **candidate Lean theorem T1d**: `SymmValid P c ↔ (proper on H) ∧ (no 2-coloured P₄)` given the diagonal in `P` |
| **Theorem 3.1** (p. 10) | `χ(G) ≤ χ_σ(G) ≤ χ(G²)` | our Theorem B |
| **symmetric completion** `G_σ` (p. 10): `G ⊂ G_σ ⊂ G²`, containing for every path `(v₁,v₂,v₃,v₄)` the edge `(v₁,v₃)` or `(v₂,v₄)`; **Theorem 3.2**: `χ_σ(G) = min χ(G_σ)` over symmetric completions | so "symm-valid" is **not** one graph's colouring problem but the minimum over a family of graphs between `G` and `G²` — the precise form of our §3 answer |
| **Theorem 3.3 / §3 end** (pp. 11–12) | for any `G` with `χ(G) ≥ 3` there is a bipartite `B` with `χ_σ(B) = χ(G)`; hence the symmetric colouring decision problem is **NP-complete even on bipartite graphs** | the symmetric count is a heuristic's number, never an exact one — as X1b already treated it |
| **Powell–Toint direct algorithm** `dpt` (p. 14–15) | greedy: repeatedly take the uncoloured vertices in decreasing degree, add `v` to the new class if no path of length ≤ 2 in the *uncoloured* subgraph joins it to the class; property `φ(w) < φ(v₁) = φ(v₂)` for `w` adjacent to both | the algorithm to implement if X1b's greedy is ever replaced |
| **§4 numbers** (Table 4.2, 30 Everstine patterns, n = 59–2680) | `sl` (colour `G²`) 433 colours in total, `ssl` 355, `dpt` 349; lower bound `maxr` 408 for `G²` | the direct symmetric scheme saved **≈ 20 %**, "where 50 % had been hoped" (p. 17) |
| **Theorem 5.2** (p. 19) | dense band matrix, bandwidth β: `χ_σ = χ(G²) = 2β + 1` | symmetry buys **nothing** for direct methods on bands |
| **triangular substitution** (§6, pp. 19–23): choose an ordering π, take the lower triangle `L_π`, colour `G_u(L_π)` consistently, solve rows from the last position backwards by (6.1) `(Ad)_i = a_ij + Σ_{l > i, l ∈ C} a_il`; **Theorem 6.1** `φ` is a triangular colouring iff it colours `G_u(L_π)` for some π; **Theorem 6.3** `χ(G) ≤ max{1+δ(G[W])} ≤ χ_τ(G) ≤ χ(G²)`; **Theorem 6.2** the smallest-last ordering attains the bound `max_k 1 + d(v_k; V_k)` = `maxr(L_π)`, a computable lower bound | our X1c experiment (below) |
| band graphs (p. 21) | `χ_τ = 1 + β` against `χ_σ = 2β + 1` | the halving that direct methods cannot give |
| **§7** | the triangular chromatic number is NP-hard too (Theorems 7.1–7.2) | same status as the symmetric count |
| **§8 numbers** (Table 8.2) | `dpt` 349, `slpt` 248, `slsl` 236 against the lower bound `maxr` 182; `slsl` "less than two colours from χ_τ on average", **45 % better than the symmetry-blind `slo`** (p. 26) | substitution is the scheme that pays |
| §6 caveat (p. 20) | substitution "may magnify errors considerably"; Powell & Toint show magnification only when the ratio of the largest to the smallest component of `d` is large | with 0/1 directions the ratio is 1 — but plan 05's probes are noisy energies, so the propagation through (6.1) must be measured, not assumed |
| open question (p. 28) | `ρ = χ_σ/χ_τ ≥ 1` conjectured, `ρ < 2` unknown; bands show `2 − ρ` arbitrarily small | — |

## 3. What this changes for plan 06

1. **Our definition is the literature's.** `SymmValid` is Coleman & Moré's *symmetrically consistent
   partition* word for word, and Theorem 2.2 is the graph characterisation we had guessed at (no
   2-coloured path of length 3). T1b is therefore a formalisation of their §2 direct method; the T1b note's
   §3 ("no fixed graph") is their Theorem 3.2 in negative form.
2. **Next Lean target, T1d:** Theorem 2.2 — `SymmValid P c ↔ proper on H ∧ no 2-coloured P₄`, under
   "diagonal in P". Small; all ingredients in the file.
3. **The scheme that beats the deck is substitution, not direct reading.** X1c (below) applies their
   recipe to the benzene pattern: 6–7 products, against 8–18 (CPR) and 7–14 (direct symmetric), with
   the lower bound `maxr = 6` met at every θ but the smallest. At 2M energies per product that is
   **360–420 energies against K = 448** — the first count in plan 06 that undercuts the deck without a
   cheap-gradient assumption. The price is the one the paper names: substitution propagates errors, and
   plan 05's probes carry noise σ_E. The next test is therefore numerical, on the same tensor: add the
   per-element noise of X2 to the probes and print the recovered-matrix error after substitution against
   the direct schemes' error. Until that is printed, X1c is a count, not a route.
4. **S5's condition is now two-sided.** Products beat the deck if (a) a product costs ≲ 2M energies *and*
   substitution noise is tolerable (X1c + the noise test), or (b) a product is much cheaper than 2M
   energies (the M2 gradient question). Ledger updated accordingly.

## 4. X1c — the triangular-substitution count on the benzene pattern (`experiments/x1c_triangular_substitution.py`)

Ordering π = smallest-last on the pattern graph; colouring of `G_u(L_π)` by two sequential heuristics
(the better one reported, each checked proper); `maxr` = Theorem 6.2's lower bound; recovery of a random
symmetric matrix with the pattern by (6.1), maximum absolute error printed.

| σ_E (µE_h) | θ (µE_h) | off-diag > θ | maxr (lower bound) | (d) triangular colours | recovery error | energies at 2M per product |
|---|---|---|---|---|---|---|
| 0.5 | 0.25 | 87 | 6 | **7** | 2.2e-16 | 420 |
| 0.5 | 0.50 | 66 | 6 | **6** | 2.8e-16 | 360 |
| 0.5 | 1.25 | 51 | 6 | **6** | 2.2e-16 | 360 |
| 0.5 | 2.50 | 45 | 6 | **6** | 2.8e-17 | 360 |
| 1.0 | 0.50 | 66 | 6 | **6** | 2.2e-16 | 360 |
| 1.0 | 1.00 | 53 | 6 | **6** | 2.2e-16 | 360 |
| 1.0 | 2.50 | 45 | 6 | **6** | 1.1e-16 | 360 |
| 1.0 | 5.00 | 44 | 6 | **6** | 2.2e-16 | 360 |

The four counts side by side (X1b + X1c), θ = 0.5 µE_h: pattern-graph colouring 4 (invalid), CPR 15,
direct symmetric 12, triangular substitution 6; Coleman & Moré's Theorem 6.3 order `χ(H) ≤ χ_τ ≤ χ(H²)`
holds here as 4 ≤ 6 ≤ 15, and their observation that substitution roughly halves the direct count (45 %
on their test set) is 6 against 12 here.

## 5. Powell & Toint 1979, as reported (not read)

Per Coleman & Moré: first to show that symmetry can give significant gains; two methods detailed — a
direct method (partitions in which two columns of a group may share a row `i` only if column `i` sits in
an earlier group; C&M note these are symmetrically consistent, and give a 6×6 example where the
Powell–Toint condition needs 4 groups and a general symmetrically consistent partition 3) and a lower
triangular substitution method; the smallest-last ordering rediscovered independently as the ordering
that minimises the maximum row count of `L_π`; the error-magnification result quoted above. **On the
supervisor's list (item 29)** for the original algorithms and the magnification theorem.

## 6. Ledger and document changes

- Orientation: S5 row rewritten (counts 8–18 / 7–14 / **6–7**, condition two-sided); references gain
  Coleman & Moré 1984 (+ the TR 82-535 copy in `Papers/plan06/`, git-ignored).
- T1b note: §3 and §5 annotated with the confirmation; §6 points to X1c.
- Lean: docstrings of `SymmValid`/`recover₂_probe` cite the definition's source; T1d listed as owed.
- Plan 05 PDF request list: item 29, Powell & Toint 1979.
