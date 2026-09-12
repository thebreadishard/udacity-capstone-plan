# X8 — size scaling of the substitution-product count against the element count, Cartesian connectivity patterns (2026-09-12 19:25)

Counting code: X1c's (smallest-last ordering, two sequential colourings of the column-intersection graph of L_π, the smaller proper one; maxr = Coleman & Moré's lower bound; recovery verified numerically where 3N ≤ 250). Patterns are 3×3 atom-pair blocks from connectivity: (a) bonded, (b) ring = heavy-atom pairs within 5.6 bohr + C–H bonds, (c) all-CC = every C–C pair + C–H bonds. g* = elements / (2k): the gradient-to-energy cost ratio below which two gradients per product cost fewer energies than measuring the elements one by one.

## Benzene calibration on the real Cartesian Δ₂ (X5's transform of the sealed dry-run tensor)

Unit check: the mode-space projection LᵀΔH_yL against the stored D2_direct_Q, relative max difference 2.5e-15. Band effect = exact harmonic positions (X2's rule) with the blocks outside the pattern set to zero, against the full correction.

| pattern | blocks kept (upper, of 78) | ‖Δ‖²_F retained | max band shift from dropped blocks (cm⁻¹) | bands > 0.5 / > 0.05 | elements | maxr | k | g* | recovery error |
|---|---|---|---|---|---|---|---|---|---|
| real, keep 90 % of ‖Δ‖²_F | 20 | 0.904 | 41.69 | 25 / 30 | 144 | 6 | **6** | 12.0 | 2.2e-16 |
| real, keep 95 % of ‖Δ‖²_F | 27 | 0.953 | 21.38 | 26 / 30 | 207 | 12 | **15** | 6.9 | 1.1e-16 |
| real, keep 99 % of ‖Δ‖²_F | 37 | 0.990 | 14.28 | 21 / 30 | 297 | 18 | **18** | 8.2 | 1.1e-16 |
| real, keep 99 % of ‖Δ‖²_F | 63 | 0.999 | 5.23 | 13 / 22 | 531 | 24 | **26** | 10.2 | 2.2e-16 |
| real, keep 99 % of ‖Δ‖²_F | 74 | 1.000 | 0.81 | 3 / 19 | 630 | 30 | **33** | 9.5 | 2.2e-16 |
| model (bonded) | 24 | 0.934 | 32.26 | 24 / 30 | 180 | 9 | **9** | 10.0 | 2.2e-16 |
| model (ring) | 33 | 0.988 | 14.81 | 22 / 30 | 261 | 18 | **18** | 7.2 | 1.1e-16 |
| model (all-CC) | 33 | 0.988 | 14.81 | 22 / 30 | 261 | 18 | **18** | 7.2 | 1.1e-16 |
| dense (all 78 blocks; X5: all above 3× the noise floor) | 78 | 1.000 | 0.00 | 0 / 0 | 666 | 36 | **36** | 9.2 | 0.0e+00 |

Generator check — naphthalene: dry-run geometry C10H8, 19 bonds; lattice C10H8, 19 bonds.

## Size series

### (a) bonded

| molecule | C | H | 3N | elements | maxr | k | g* | energies: products by energies only (4·3N·k) | recovery error |
|---|---|---|---|---|---|---|---|---|---|
| benzene (dry run) | 6 | 6 | 36 | 180 | 9 | **9** | 10.0 | 1296 | 1.7e-16 |
| naphthalene (dry run) | 10 | 8 | 54 | 279 | 9 | **9** | 15.5 | 1944 | 4.4e-16 |
| anthracene | 14 | 10 | 72 | 378 | 9 | **9** | 21.0 | 2592 | 3.3e-16 |
| phenanthrene | 14 | 10 | 72 | 378 | 9 | **9** | 21.0 | 2592 | 2.2e-16 |
| tetracene | 18 | 12 | 90 | 477 | 9 | **9** | 26.5 | 3240 | 3.3e-16 |
| pyrene | 16 | 10 | 78 | 417 | 9 | **9** | 23.2 | 2808 | 1.1e-16 |
| coronene | 24 | 12 | 108 | 594 | 9 | **9** | 33.0 | 3888 | 4.4e-16 |
| C54H18 | 54 | 18 | 216 | 1242 | 9 | **9** | 69.0 | 7776 | 7.2e-16 |
| C96H24 | 96 | 24 | 360 | 2124 | 9 | **9** | 118.0 | 12960 | — |
| C150H30 | 150 | 30 | 540 | 3240 | 9 | **9** | 180.0 | 19440 | — |
| C384H48 | 384 | 48 | 1296 | 7992 | 9 | **9** | 444.0 | 46656 | — |

### (b) ring, one ring deep

| molecule | C | H | 3N | elements | maxr | k | g* | energies: products by energies only (4·3N·k) | recovery error |
|---|---|---|---|---|---|---|---|---|---|
| benzene (dry run) | 6 | 6 | 36 | 261 | 18 | **18** | 7.2 | 2592 | 1.1e-16 |
| naphthalene (dry run) | 10 | 8 | 54 | 459 | 18 | **18** | 12.8 | 3888 | 2.2e-16 |
| anthracene | 14 | 10 | 72 | 657 | 18 | **18** | 18.2 | 5184 | 2.8e-16 |
| phenanthrene | 14 | 10 | 72 | 666 | 18 | **18** | 18.5 | 5184 | 4.4e-16 |
| tetracene | 18 | 12 | 90 | 855 | 18 | **18** | 23.8 | 6480 | 4.4e-16 |
| pyrene | 16 | 10 | 78 | 777 | 18 | **21** | 18.5 | 6552 | 2.2e-16 |
| coronene | 24 | 12 | 108 | 1215 | 21 | **21** | 28.9 | 9072 | 6.7e-16 |
| C54H18 | 54 | 18 | 216 | 2889 | 21 | **24** | 60.2 | 20736 | 4.4e-16 |
| C96H24 | 96 | 24 | 360 | 5283 | 21 | **27** | 97.8 | 38880 | — |
| C150H30 | 150 | 30 | 540 | 8397 | 21 | **30** | 139.9 | 64800 | — |
| C384H48 | 384 | 48 | 1296 | 22059 | 21 | **30** | 367.6 | 155520 | — |

### (c) all C–C pairs

| molecule | C | H | 3N | elements | maxr | k | g* | energies: products by energies only (4·3N·k) | recovery error |
|---|---|---|---|---|---|---|---|---|---|
| benzene (dry run) | 6 | 6 | 36 | 261 | 18 | **18** | 7.2 | 2592 | 4.2e-17 |
| naphthalene (dry run) | 10 | 8 | 54 | 585 | 30 | **30** | 9.8 | 6480 | 2.2e-16 |
| anthracene | 14 | 10 | 72 | 1053 | 42 | **42** | 12.5 | 12096 | 2.2e-16 |
| phenanthrene | 14 | 10 | 72 | 1053 | 42 | **42** | 12.5 | 12096 | 2.2e-16 |
| tetracene | 18 | 12 | 90 | 1665 | 54 | **54** | 15.4 | 19440 | 2.8e-17 |
| pyrene | 16 | 10 | 78 | 1326 | 48 | **48** | 13.8 | 14976 | 1.1e-16 |
| coronene | 24 | 12 | 108 | 2808 | 72 | **72** | 19.5 | 31104 | 0.0e+00 |
| C54H18 | 54 | 18 | 216 | 13473 | 162 | **162** | 41.6 | 139968 | 1.1e-16 |
| C96H24 | 96 | 24 | 360 | 41976 | 288 | **288** | 72.9 | 414720 | — |
| C150H30 | 150 | 30 | 540 | 101925 | 450 | **450** | 113.2 | 972000 | — |
| C384H48 | 384 | 48 | 1296 | 664848 | 1152 | **1152** | 288.6 | 5971968 | — |

## Reading

1. **Frobenius retention is not band accuracy.** At benzene the blocks outside the connectivity patterns carry 1–7 % of ‖Δ₂‖²_F and still move harmonic bands by 15–32 cm⁻¹; band accuracy at plan 05's 0.5 cm⁻¹ needs 74 of the 78 blocks (99.99 % of the norm). X5's statement that all 78 blocks lie above 3× the noise floor said the same thing in other words: at benzene the Cartesian Δ₂ is dense at the noise level, and none of the patterns (a)–(c) is licensed there. (In mode space X1c/X1d thresholded at multiples of the noise, which is why their reconstruction kept band positions within 0.5 cm⁻¹.)

2. **What the size series therefore is.** Under (a) and (b) the pattern graph has bounded degree, so maxr and k stay bounded while the elements grow ∝ N; under (c) k grows ∝ number of carbons while the elements grow ∝ carbons², so g* still grows. These are brackets for what substitution *could* give if far blocks (beyond one ring) fall below the noise floor — a property benzene cannot show, because in benzene nothing is farther than one ring. The naphthalene tensor (after plan 05's DFT dry run) is the first molecule that can: step 2 of the ladder stays a tensor question, and this script is ready to count it (the real-pattern rows) the day it exists.

3. **The dense row is the known baseline.** For a dense pattern the substitution count is 3N (one product per coordinate), and g* = (3N+1)/4 ≈ 9 at benzene: this is nothing but plan 05's mode G (a Hessian from 2·3N gradients). Substitution only improves on it where the pattern is sparse. None of this is a saving: with energies only, one product costs 4·3N energies (plan 05's second-order convention), and g is unmeasured (plan 05 ladder step 4).

Constants: {"bond_cutoff_bohr": {"CC": 3.0, "CH": 2.4}, "R_CUT_bohr_ring": 5.6, "lattice_CC_A": 1.4, "lattice_CH_A": 1.08, "retention_levels": [0.9, 0.95, 0.99, 0.999, 0.9999], "energies_per_product_energies_only": "4 * 3N (second order, plan 05 convention)", "VERIFY_MAX_DIM": 250, "random_seed": 0}