# Result note 2026-09-12 (evening) — X12: the DFT Hessian's own decay per bond is the same from benzene to pyrene (≈ ×0.25–0.29 per bond), and it is not truncatable either

*Script `experiments/x12_dft_hessian_decay_series.py`; tables `x12_dft_hessian_decay_series.md` / `.json`. Inputs: plan 02's B3LYP/6-31G* Hessians for nine PAHs, extracted from git commit `57a7910` by the script itself (the arrays were removed from the tree on 2026-09-06). Mean-field half of the T3/T3′ question; no correction tensor beyond benzene exists yet. Every number from the files.*

## 1. What was measured

For each molecule the mass-weighted Hessian was cut into 3×3 atom-pair blocks and the median block norm tabulated per bond-graph distance; a log-linear fit gives the decay factor per bond, once over all distances ≥ 1 and once restricted to distances 1–4 (the range every molecule has, and the range above the far-block floor). X2's exact harmonic rule then gives the band shift from zeroing every block at graph distance ≥ d*. Sanity: the highest C–H stretch lies at 3203–3240 cm⁻¹ for all nine; triphenylene and coronene carry one imaginary mode each in plan 02's stored Hessians (their geometries were not fully converged there — the ratios read here are insensitive to that, the band tests less so; both flagged).

## 2. Result

| molecule | C | max graph distance | decay factor per bond, d = 1–4 | all d ≥ 1 | band shift from zeroing blocks at d ≥ 4 |
|---|---|---|---|---|---|
| benzene | 6 | 5 | 0.277 | 0.38 | 26 cm⁻¹ |
| naphthalene | 10 | 7 | 0.251 | 0.34 | 29 |
| anthracene | 14 | 9 | 0.252 | 0.42 | 30 |
| phenanthrene | 14 | 9 | 0.257 | 0.44 | 48 |
| pyrene | 16 | 9 | 0.268 | 0.51 | 53 |
| tetracene | 18 | 11 | 0.271 | 0.53 | 138 |
| chrysene | 18 | 11 | 0.260 | 0.56 | 61 |
| triphenylene (1 imag.) | 18 | 9 | 0.293 | 0.58 | 246 |
| coronene (1 imag.) | 24 | 9 | 0.351 | 0.66 | 123 |

Three readings.

1. **The mean field has one decay length.** Over the first four bonds the block norm falls by a factor 3.4–4.0 per bond for every molecule from benzene to chrysene (0.25–0.29), coronene a little slower (0.35, one imaginary mode in its file). That is the short-ranged, bonded-force-constant behaviour T3's audit assumed for the DFT side, and it is size-independent — the reference against which the naphthalene correction's profile (X9 on naphthalene) is to be read. The all-distance fits rise with size only because the far tail (distances 5–11, medians 10⁻⁸–10⁻⁷) sits on a floor that a longer molecule samples more of; the restricted fit is the honest number.
2. **Not even the DFT Hessian is truncatable at band level.** Zeroing blocks beyond three bonds shifts bands by 26–246 cm⁻¹. So the lesson of X8 ("norm-sparsity is not band-sparsity") holds for the mean field as well: harmonic band positions are a global functional of the force-constant matrix, and Cartesian block truncation is the wrong operation for anything that must hold 0.5 cm⁻¹. Whatever locality is worth for plan 05, it will have to be spent inside the electronic-structure step (the local-CC fragments, S1's actual home), not on the Hessian's blocks.
3. **What X9 said at benzene, read against this series:** the correction's share of the Hessian rose from 2.7 % on-atom to 6.5 % at three bonds, i.e. the correction decays *more slowly* than a factor ≈ 3.6 per bond. If that holds at naphthalene, the correction's decay factor per bond is above 0.28 there; T3 would put it at a value that grows as the gap closes. The naphthalene tensor will give the first second point.

## 3. What changes

- Ledger S1: the mean-field decay length is measured across the series (a constant ≈ 0.25–0.29 per bond); the correction's is measured at one point (benzene, slower than the mean field). No route in plan 06 or plan 05 may assume Cartesian block truncation of any Hessian-like object at 0.5 cm⁻¹ — now shown for nine molecules.
- Plan 05 machine queue: plan 02's stored Hessians are the B3LYP half of the DFT dry runs for naphthalene, anthracene, pyrene and others (geometry check done for naphthalene: identical within 5 × 10⁻⁴ bohr), so the second-functional Hessians are what those dry runs cost.
- Nothing enters plan 05's frozen text.
