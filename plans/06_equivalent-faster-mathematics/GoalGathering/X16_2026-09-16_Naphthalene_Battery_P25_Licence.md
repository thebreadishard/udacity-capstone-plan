# X16 at naphthalene — the pre-registered tensor battery, and P25's licence test: **LOSE** (run 16 September 2026, 09:03)

*Script `experiments/x16_tensor_tests.py --molecule naphthalene_sym` (written 13 September, before the naphthalene tensor existed; the benzene self-test with its assertions passed again today before this run). Input: plan 05's symmetrised naphthalene stage A of 15 September — the stand-in correction Δ₂ = H_BHHLYP − H_B3LYP at 6-31G* in the mode basis (`D2_direct_Q`), irreps from the D₂h character analysis of the modes (141 same-irrep pairs, as `deck_counts_planar.py` counts). Outputs `experiments/x16_tensor_tests_naphthalene_sym.{md,json}`. The licence rule is P25 §3 as pre-stated: the DFT-only ranking wins if it reaches 0.5 cm⁻¹ with at most half of the eligible pairs and within a factor 1.5 of the oracle-magnitude count.*

## X10 — which off-diagonal pairs must be measured, and can DFT alone say which

| ranking | pairs needed for ≤ 0.5 cm⁻¹ | for ≤ 0.1 cm⁻¹ |
|---|---|---|
| P1 — DFT-only, by the resonance denominator 1/\|ω_i² − ω_j²\| | **76** of 141 | 82 |
| P2 — oracle, by \|Δ₂,ij\| | 33 | 74 |
| P3 — oracle, by the measured drop-one effect | 22 | 47 |

All 141 eligible pairs kept: 0.004 cm⁻¹ (the symmetry prior is exact to that level); none kept: 13.24 cm⁻¹. Spearman rank correlation of the DFT-only denominator with the drop-one effect: 0.632 (benzene: the same predictor selected 19 of 47).

**P25 licence: n(P1) = 76 > half of the eligible pairs (70.5), and 76 > 1.5 × n(P2) = 49.5 → LOSE.** At benzene the free DFT ordering found the pairs that matter with 19 of 47; at naphthalene it needs more than half of them, and 2.3 times what an oracle on the element sizes needs. The resonance denominator is a weak guide once the spectrum is dense: naphthalene's 48 modes give many near-degenerate pairs whose coupling is small, and some well-separated pairs whose coupling is large.

## X11 — substitution products on the selected patterns

| pattern | pairs | k (products) | gradients 2k | recovery error |
|---|---|---|---|---|
| P1 DFT-only (76 pairs) | 76 | 5 | 10 | 2 × 10⁻¹⁶ |
| P2 oracle (33) | 33 | 4 | 8 | 1 × 10⁻¹⁶ |
| P3 oracle (22) | 22 | 3 | 6 | 1 × 10⁻¹⁶ |
| symmetry prior, all 141 eligible | 141 | **9** | 18 | 0 |
| dense | 1,128 | 48 | 96 | 0 |

The count of 9 products for the symmetry prior — quoted since 13 September from the irrep table alone — is now a recovery on a real (stand-in) tensor: exact to 10⁻¹⁶.

## X9 and X8 (the same numbers as the standalone X9 run of this morning)

Median block-norm ratio Δ/H_low by bond-graph distance 0.035 / 0.050 / 0.051 / 0.070 / 0.080 / 0.101 / 0.198 / 0.210 (d = 0 … 7); zeroing Δ's blocks at d ≥ 4 still moves a band by 10.5 cm⁻¹, at d ≥ 5 by 5.4, at d ≥ 6 by 0.4. X8: keeping 99.99 % of the Frobenius norm (152 of 171 atom-pair blocks) still moves a band by 0.9 cm⁻¹; 99.9 % (105 blocks) by 7.9.

## What follows (the decision rule, read today)

- **P25 is not licensed.** Lever B of the cost ladder (couplings × 0.4 by a free DFT rule) leaves every affordability table: the naphthalene deck under decisions 36–37 is 291 energies with levers G and H only; the "+ B" rows in the cost ladder §5 and in P27 are struck with today's date.
- **Both closing conditions of branch C now hold** (g unmeasurable on the laptop at the coupled-cluster level, 14 September; P25 not licensed, 16 September). Under the rule the cost branch closes at the 15 October review; nothing is scheduled to change that between now and then. The verdict is written here and read there.
- **The symmetry prior's 9 products stand**; they matter only if a gradient becomes available on a larger machine (the gradient route of the main plan's side project).
- **Branch M is unchanged** (X9 and X8 confirm at two rings what benzene showed).
- For the main plan: the deck's hashed order and stopping rule remain the only economy on the couplings; the per-family go/no-go of P27 (diagonal-first decks) does not depend on P25 and stands.
