# X14 — substitution products on naphthalene's real symmetry pattern (mode space, M = 48; 2026-09-17 07:59)

Pattern from X13 (B3LYP modes, D2h irreps): 141 eligible pairs of 1128. Counting code: X1c's; recovery verified numerically. g* = 474 / (2k): the gradient-to-energy cost ratio below which 2k gradients cost fewer energy-equivalents than plan 05's R1 deck (plan 05 proposal §3.2: 96 + 96 + 282).

| pattern | pairs | elements | naive energies 2M + 2n | maxr | k (products) | gradients 2k | **g\* vs R1 deck (474)** | g\* vs naive | recovery error |
|---|---|---|---|---|---|---|---|---|---|
| (a) symmetry prior: diagonal + all eligible pairs | 141 | 189 | 378 | 9 | **9** | 18 | **26.3** | 21.0 | 0.0e+00 |
| (b) diagonal + top 40 % of eligible pairs by 1/|ω_i²−ω_j²| (56) | 56 | 104 | 208 | 4 | **4** | 8 | **59.2** | 26.0 | 5.6e-17 |
| (c) diagonal + top 50 % of eligible pairs by 1/|ω_i²−ω_j²| (70) | 70 | 118 | 236 | 5 | **5** | 10 | **47.4** | 23.6 | 2.2e-16 |
| (d) dense | 1128 | 1176 | 2352 | 48 | **48** | 96 | **4.9** | 24.5 | 0.0e+00 |

Reading: row (a) is the bar M2a's g must clear for the gradient route to beat plan 05's own R1 deck at naphthalene with no prior beyond symmetry; rows (b)–(c) are brackets for what P25's rule could add if its benzene ratio carried over (a tensor question); row (d) is mode G's 2·M gradients. The pattern is the DFT one (B3LYP modes, plan 02's Hessian); the correction's own pattern at R1 is unknown until the BHHLYP half exists.

Constants: {"R1_deck_energies": 474, "R1_deck_source": "plan 05 proposal §3.2: 96 + 96 + 282", "fractions": [0.4, 0.5], "random_seed": 0, "input": "x13_naphthalene_mode_table.json (naphthalene: modes with irreps and frequencies)"}