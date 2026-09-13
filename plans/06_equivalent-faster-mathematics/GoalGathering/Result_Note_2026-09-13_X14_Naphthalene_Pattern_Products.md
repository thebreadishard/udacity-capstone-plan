# Result note 2026-09-13 — X14: on naphthalene's real symmetry pattern, 9 substitution products (18 gradients) recover the whole R1 correction; the gradient route beats plan 05's 474-energy deck whenever g < 26

*Script `experiments/x14_naphthalene_symmetry_pattern_products.py`; tables `x14_…md` / `.json`. Input: X13's naphthalene mode table (48 B3LYP modes with D2h irreps, plan 02's Hessian at the dry-run geometry). No correction tensor is needed: the substitution count depends on the sparsity pattern alone, and plan 05's symmetry prior fixes that pattern from the DFT modes. Counting code X1c's (Powell–Toint substitution, Coleman & Moré's lower bound maxr, recovery verified to 2 × 10⁻¹⁶). Every number from the files.*

## 1. Result

| pattern (mode space, M = 48) | pairs | maxr | products k | gradients 2k | g* against the R1 deck (474 energies) |
|---|---|---|---|---|---|
| (a) symmetry prior: diagonal + all 141 eligible pairs — **what plan 05 measures at R1** | 141 | 9 | **9** | **18** | **26.3** |
| (b) diagonal + top 40 % of eligible pairs by 1/‖ω_i² − ω_j²‖ (benzene's X10 ratio, a bracket) | 56 | 4 | 4 | 8 | 59.2 |
| (c) diagonal + top 50 % (P25's licence boundary) | 70 | 5 | 5 | 10 | 47.4 |
| (d) dense (mode G) | 1,128 | 48 | 48 | 96 | 4.9 |

Row (a) is the number the ladder lacked: at R1, with no prior beyond the symmetry plan 05 already uses, **eighteen gradients replace 474 energies**. The gradient route therefore beats plan 05's own R1 deck as long as one gradient costs fewer than 26 energies — and that bar is set before M2a runs, by a pattern the correction cannot change (it can only be sparser than the symmetry pattern, never denser).

## 2. Why k is 9, and what that says about size

maxr = 9 = the number of modes in naphthalene's largest irrep (Ag, X13). The symmetry pattern is block-diagonal by irrep; substitution on a dense block of b modes needs b products; the blocks are read in parallel by the same probe vectors. So under the symmetry prior alone, **k equals the largest irrep block**, not the pair count: benzene 7 (its largest same-symmetry block, X11), naphthalene 9, and for a PAH with M modes and point group of order |G| roughly M/|G| to M/4 depending on how the irreps fill. The energy deck grows with the *pairs* (∝ M²/|G|); the products grow with the *block* (∝ M/|G|). That is the structural reason the gradient route gains with size — the same conclusion X8 reached for connectivity patterns, now on the pattern plan 05 actually uses, and without X8's licence problem (mode-space, symmetry-exact, band-exact by construction: the pattern drops nothing).

For low-symmetry PAHs (C_s, C_2v) the blocks are large and k approaches M/2–M; the route then degrades towards mode G (2M gradients), which still beats an energy deck of order M² whenever g is below M/2. The X8 brackets and this row bracket the same statement from two sides.

## 3. What changes

- **The cost ladder's lever C** gets its R1 number: 18 gradients against 474 energies, g* = 26 (was "12–14 g, wins if g < 34–40" extrapolated from benzene's 6–7 products — the products are more, the deck is larger, the crossover is 26).
- **M2a's pre-registered reading** keeps its thresholds (g ≤ 6 / ≤ 20 / > 20); X14 adds the R1 bar as a dated line: g < 26 at naphthalene size is where the gradient route starts to pay against plan 05's own deck.
- **P25** (rows b–c) would lower k from 9 to 4–5 if benzene's ratio carried over — a further factor 2 on top, tensor-dependent, and the licence test decides.
- Nothing enters plan 05's frozen text.
