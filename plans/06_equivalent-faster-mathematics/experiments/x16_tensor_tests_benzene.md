# X16 — tensor test battery on benzene (2026-09-13 09:34; irreps from stageC_symmetry_prior.json)

## X10 — eligible pairs 47; all kept → 0.002 cm⁻¹; none → 19.58 cm⁻¹; Spearman P1 vs P3 0.754

| ranking | pairs for 0.5 cm⁻¹ | for 0.1 cm⁻¹ |
|---|---|---|
| P1 DFT-only | **19** | 19 |
| P2 oracle magnitude | **17** | 19 |
| P3 oracle effect | **6** | 16 |

**P25 licence:** n(P1) = 19, n(P2) = 17, half of eligible = 23.5 → **WIN** (win: DFT-only ranking reaches 0.5 cm-1 with at most half the eligible pairs AND within a factor 1.5 of the oracle-magnitude count; lose: more than half the eligible pairs, or a factor above 1.5).

## X11 — substitution products

| pattern | pairs | maxr | k | gradients 2k | recovery error |
|---|---|---|---|---|---|
| P1 DFT-only | 19 | 3 | **4** | 8 | 1.1e-16 |
| P2 oracle magnitude | 17 | 3 | **3** | 6 | 0.0e+00 |
| P3 oracle effect | 6 | 2 | **2** | 4 | 0.0e+00 |
| symmetry prior (all eligible) | 47 | 7 | **7** | 14 | 1.1e-16 |
| dense | 435 | 30 | **30** | 60 | 0.0e+00 |

## X9 — correction / mean field by bond-graph distance (median block-norm ratio)

| d | pairs | ratio |
|---|---|---|
| 0 | 12 | 0.0268 |
| 1 | 12 | 0.0369 |
| 2 | 18 | 0.0482 |
| 3 | 21 | 0.0647 |
| 4 | 12 | 0.0543 |
| 5 | 3 | 0.0559 |

Band shift from zeroing blocks at graph distance ≥ d*: d*=2: H_low 164.3, Δ 32.0 cm⁻¹; d*=3: H_low 146.6, Δ 13.1 cm⁻¹; d*=4: H_low 26.1, Δ 2.7 cm⁻¹; d*=5: H_low 17.9, Δ 0.9 cm⁻¹

## X8 — real-pattern rows (Frobenius retention → band shift)

| retention | blocks kept | max band shift (cm⁻¹) |
|---|---|---|
| 0.9 | 20 of 78 | 41.69 |
| 0.99 | 37 of 78 | 14.28 |
| 0.999 | 63 of 78 | 5.23 |
| 0.9999 | 74 of 78 | 0.81 |