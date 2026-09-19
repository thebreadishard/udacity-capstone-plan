# X22 — the gradient count 2k+1 for molecules without D2h symmetry (19 September 2026, 12:3x; branch C, serves plan 05's gradient route and the price of the label factory)

*Question fixed before the run (script docstring): X14/X21 counted the symmetry-blocked products k on eight high-symmetry PAHs. Does the linear count survive at C2v, Cs and C1, and what does the symmetry prior still save there? Data: the 45 layer-A corpus molecules (B3LYP/6-31G* Hessians at optimised geometries, 39 from the Hetzner run of 18–19 September and six from the laptop). Method: abelian operations found on the geometry itself (tolerance 0.1 bohr), modes symmetry-adapted inside near-degenerate clusters, modes that stay unresolved allowed to couple with everything (a coarser prior, never a finer one), then X21's substitution colouring. Script `x22_pattern_count_low_symmetry.py`; numbers in `x22_pattern_count_low_symmetry.json/.md`.*

## Validation

Naphthalene: 7 operations (D2h), 8 blocks, **k = 9, 19 gradients** — X14/X21's count exactly. Benzene: D2h subgroup found by the in-plane scan, 8 blocks, **k = 6, 13 gradients** — X21's count exactly. Recovery error of a random symmetric matrix from the k products is at machine precision for all 45 molecules.

## Result

| symmetry found | molecules | gradients 2k+1 (range) | 2k+1 / M | energies deck (2·allowed pairs + M + 1) | gradients / energies |
|---|---|---|---|---|---|
| D2h (7 ops) | benzene, naphthalene, anthracene, pyrene, phenazine, biphenylene | 13–27 | 0.35–0.45 | 135–741 | 1/10 – 1/27 |
| C2v / C2h / D2 (3 ops) | 17 (azulene, phenanthrene, fluoranthene, carbazole, fluorene, acridine, stilbene, biphenyl, …) | 25–51 | 0.65–0.76 | 324–1,467 | 1/13 – 1/29 |
| Cs (1 op, the molecular plane) | 19 (quinoline, indole, styrene, naphthoic acid, methylnaphthalenes, phenylpyridines, benzophenone, …) | 55–87 | 1.30–1.42 | 874–2,826 | 1/16 – 1/35 |
| C1 (no op within 0.1 bohr) | 1-naphthol, 2-naphthylamine, 1-aminoanthracene | 103–145 | 2.0 | 2,602–5,185 | 1/25 – 1/36 |

Linear fits over the 45 molecules: gradients ≈ 0.55 M + 24; without any symmetry exactly 2M + 1; the energies deck ≈ 38 M − 768 (it is quadratic — the fit is only the slope over this size range).

## Reading

1. **Linear everywhere, as the docstring predicted; the constant is what changes.** The symmetry prior buys a factor 2–3 over the no-symmetry count at D2h (0.35–0.45 M), a factor 1.3 at C2v/Cs-with-a-C2 (0.7 M), and nothing beyond the in-plane/out-of-plane split at Cs (1.3–1.4 M: the in-plane block of 2N − 3 modes is dense and costs its own size). At C1 the count is the trivial 2M + 1.
2. **The gradient route stays an order of magnitude below the energies route at every symmetry**, 10× to 36×, because the energies deck grows with the number of allowed *pairs* and the gradient deck with the number of *modes*. The saving is largest exactly where the symmetry helps least, since that is where the pairs are most numerous.
3. **What it costs for the label factory.** A typical layer-A molecule (M ≈ 57, Cs) needs ≈ 60–80 gradients, three to four times naphthalene's 19. At cc-pVDZ with g = 3–6 that is 6–16 laptop-days per label instead of 2–4 (calendar of the desk note of 18 September, §4); at cc-pVTZ it is out of the laptop's reach for every molecule but the D2h ones. The label count of §4 there (20–50 molecules) therefore prices at roughly 200–800 laptop-days at cc-pVDZ, or weeks on a cluster — the Snellius question of the 28th, again.
4. **Where more could be saved, stated as untested ideas, not results:** (a) the *local* symmetry of a substituted PAH's core (the ring skeleton of 2-methylnaphthalene is nearly D2h) could be used as an approximate prior with the residual measured — the plan's per-family discipline would make that a licensed shortcut or a refused one; (b) for Cs molecules the dense in-plane block could be thinned by the resonance-denominator ordering of P25 *as a ranking inside the block* — P25 lost as a whole-molecule licence at 0.5 cm⁻¹ (X16) but was never tested at the 5 cm⁻¹ margin the fingerprint references actually resolve. Both are pre-registration candidates, neither is needed for the 28th.
5. **Caveats.** Two of diphenylacetylene's 66 modes stayed unresolved (their characters were 0.28 off ±1 after adaptation; they are allowed to couple with all, so the count 39 is an upper bound for that molecule). 1-naphthol and 2-naphthylamine came out C1 because their OH/NH₂ hydrogens sit out of the ring plane in the optimised geometry; a planar constraint would make them Cs. The ops are found on the geometry, not asserted from the name.

## What it decides

Nothing closes. The gradient route's linear count is confirmed on 45 molecules of every symmetry the corpus has; the constant per symmetry class is now a table the price of the label factory can use. The 18 September desk note's §4 calendar gets a dated pointer to this note; decision rule 2's gate for M2 is unchanged.
