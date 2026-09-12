# Result note 2026-09-12 (evening) — X8: how the substitution-product count scales with size, and why benzene cannot license any sparse Cartesian pattern

*Script `experiments/x8_size_scaling_substitution.py`; printed tables `experiments/x8_size_scaling_substitution.md` and `.json`. Model form of step 2 of plan 05's evidence ladder ("does plan 06 make plan 05 cheaper?"), run because the naphthalene tensor does not exist yet. Every number below is from those files.*

## 1. Question

X1c counted 6–7 Powell–Toint substitution products on the real benzene Δ₂ pattern in mode space; X5 found the same correction in mass-weighted Cartesian space concentrated on atoms and bonds (93.5 % of ‖Δ₂‖²_F). If a sparsity pattern could be written down from connectivity alone, one could count products against elements for molecules whose tensor nobody has, and see whether the products-to-elements ratio improves with size. X8 does that for three connectivity patterns — (a) bonded pairs, (b) heavy-atom pairs within one ring (5.6 bohr) plus C–H bonds, (c) all C–C pairs plus C–H bonds — on benzene, naphthalene (dry-run geometries) and honeycomb-lattice PAHs generated in the script (anthracene, phenanthrene, tetracene, pyrene, coronene, C₅₄H₁₈, C₉₆H₂₄, C₁₅₀H₃₀, C₃₈₄H₄₈), with X1c's counting code imported unchanged and the recovery verified numerically (max error ≤ 5 × 10⁻¹⁶) up to 3N = 216. Generator check: the lattice naphthalene has C₁₀H₈ and 19 bonds, as the dry-run geometry.

## 2. The calibration result, which is the result

Before trusting a connectivity pattern, X8 tests it on the one real Cartesian Δ₂ it has (benzene, X5's transform; unit check against the stored mode-space correction 2.5 × 10⁻¹⁵), and — this is the step X5 did not take — asks what dropping the blocks outside the pattern does to the **harmonic band positions** (X2's exact rule):

| pattern at benzene | blocks kept of 78 | ‖Δ₂‖²_F retained | max band shift from the dropped blocks | bands moved > 0.5 cm⁻¹ | elements | products k | g* = elements / 2k |
|---|---|---|---|---|---|---|---|
| real, keep 90 % | 20 | 0.904 | **41.7 cm⁻¹** | 25 of 30 | 144 | 6 | 12.0 |
| real, keep 95 % | 27 | 0.953 | 21.4 | 26 | 207 | 15 | 6.9 |
| real, keep 99 % | 37 | 0.990 | 14.3 | 21 | 297 | 18 | 8.2 |
| real, keep 99.9 % | 63 | 0.999 | 5.2 | 13 | 531 | 26 | 10.2 |
| real, keep 99.99 % | 74 | 0.9999 | 0.8 | 3 | 630 | 33 | 9.5 |
| model (a) bonded | 24 | 0.934 | 32.3 | 24 | 180 | 9 | 10.0 |
| model (b) ring = (c) all-CC at benzene | 33 | 0.988 | 14.8 | 22 | 261 | 18 | 7.2 |
| dense | 78 | 1 | 0 | 0 | 666 | 36 | 9.25 |

**Frobenius retention is not band accuracy.** Blocks carrying 1 % of the norm move bands by 14 cm⁻¹; the far H–H and C–H blocks (norms ≈ 10⁻⁷ in the file's units, X5) are small against the on-atom blocks but not against what a band position feels (a change of 10⁻⁷ a.u. in ω² at 1,000 cm⁻¹ is ≈ 2 cm⁻¹). Band accuracy at plan 05's 0.5 cm⁻¹ needs 74 of the 78 blocks. X5's "all 78 blocks above 3× the noise floor" said this already in other words: **at benzene the Cartesian Δ₂ is dense at the noise level, and none of the connectivity patterns is licensed.** X1c/X1d escaped this because they thresholded in mode space at multiples of the noise, which keeps everything a band feels — the reason X1d's reconstruction stayed within 0.5 cm⁻¹.

The dense row is the known baseline: for a dense pattern the substitution count is 3N, one product per coordinate, and g* = (3N + 1)/4 ≈ 9 at benzene — nothing but plan 05's mode G (a Hessian from 2·3N gradients). Substitution improves on it only where the pattern is sparse, and at benzene it is not.

## 3. The size series, read as brackets

With that caveat the series says what substitution *could* give if blocks beyond one ring fall below the noise floor — a property benzene cannot show, because in benzene nothing is farther than one ring:

| pattern | products k across the series | elements | g* at naphthalene → C₃₈₄H₄₈ | energies-only products (4·3N·k) vs elements |
|---|---|---|---|---|
| (a) bonded | 9 at every size (bounded degree) | 279 → 7,992 (∝ N) | 15.5 → 444 | ≈ 6× the elements at every size |
| (b) one ring deep | 18 → 30 (bounded) | 459 → 22,059 (∝ N) | 12.8 → 368 | ≈ 7× |
| (c) all C–C pairs | 30 → 1,152 (∝ carbons) | 585 → 664,848 (∝ carbons²) | 9.8 → 289 | ≈ 9–11× |

Three readings. (i) **With energies only, substitution never pays** in any bracket at any size: a product costs 4·3N energies under plan 05's second-order convention, six to eleven times the elements. This repeats P24 §2 for the whole size range. (ii) **With gradients**, g* grows with size in every bracket, even the pessimistic (c) — because elements grow faster than products. Whether the real correction follows (a), (b), (c) or none of them beyond one ring is a tensor question. (iii) **The first molecule that can answer it is naphthalene**; the script's real-pattern rows (retention levels and the noise-floor pattern) run unchanged on its tensor the day the DFT dry run exists.

## 4. What changes

- Plan 05's evidence ladder, step 2: the model form is done and **negative at benzene** for Cartesian sparsity (no connectivity pattern is band-accurate there); the step stays open as a tensor measurement at naphthalene, now with a ready script and a pre-stated reading: a pattern is licensed only if its dropped blocks move no band by more than 0.5 cm⁻¹ (X2's rule), and the products-to-elements ratio is read only for licensed patterns.
- Plan 06 ledger S5: unchanged in status (alive, conditional on gradients); the Cartesian route adds the explicit warning that norm-based sparsity is not band-based sparsity. S1 gains a data point against real-space locality at the band level: at benzene nothing is droppable.
- Nothing enters plan 05's frozen text; no decision proposal follows from X8.
