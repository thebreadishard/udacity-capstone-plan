# Result note 2026-09-12 (evening) — X9: the correction is *longer*-ranged than the DFT Hessian, not shorter (T3′ loses at benzene)

*Script `experiments/x9_dft_vs_correction_profiles.py`; tables `x9_dft_vs_correction_profiles.md` / `.json`. Test of Conjecture T3′ (T3 proof-plan note §4) on plan 05's sealed benzene dry-run tensor (stand-in Δ = BHHLYP − B3LYP, 6-31G*). Sanity: frequencies recomputed from the mass-weighted DFT Hessian match the dry run's list to 2 × 10⁻⁵ cm⁻¹. Every number from the files.*

## 1. Question and pre-stated losing condition

T3′ said: the long-range parts of the CC and DFT Hessians are mean-field and cancel in the difference, so the correction Δ₂ should decay faster in bond-graph distance than the Hessian itself — the property that would make a sparse deck or a sparse product pattern possible for Δ₂ even where it is not for H. Losing condition, written before running: the ratio ‖Δ[A,B]‖ / ‖H_DFT[A,B]‖ does not fall with graph distance, and Δ's band-level dependence on far blocks is not a small fraction of H_DFT's.

## 2. Result: the ratio rises

| bond-graph distance | pairs | median ‖H_DFT[A,B]‖ | median ‖Δ[A,B]‖ | median ratio Δ / H_DFT |
|---|---|---|---|---|
| 0 (on-atom) | 12 | 1.22e-4 | 3.28e-6 | 0.027 |
| 1 (bonded) | 12 | 3.57e-5 | 1.32e-6 | 0.037 |
| 2 | 18 | 5.05e-6 | 2.43e-7 | 0.048 |
| 3 | 21 | 1.48e-6 | 9.57e-8 | 0.065 |
| 4 | 12 | 6.12e-7 | 3.33e-8 | 0.054 |
| 5 (para H…H) | 3 | 7.52e-7 | 4.20e-8 | 0.056 |

Both objects decay with distance, the Hessian by a factor ≈ 200 from distance 0 to 5, the correction by ≈ 80. **The correction decays more slowly**: its share of the Hessian doubles from the on-atom blocks (2.7 %) to distance 3 (6.5 %). By pair type the effect is sharpest where the π system lives: for C–C pairs the ratio is 3.4 % on-atom, 5.4 % bonded, **19 % at distance 2 (meta) and 26 % at distance 3 (para)** — X5's "flat ring" seen again, now relative to the mean field.

Band level (X2's exact rule; zero every block at graph distance ≥ d*):

| blocks kept | H_DFT alone: max band shift | Δ alone: max band shift | ratio |
|---|---|---|---|
| distance < 1 | 401.8 cm⁻¹ | 37.0 cm⁻¹ | 0.09 |
| distance < 2 | 164.3 | 32.0 | 0.19 |
| distance < 3 | 146.6 | 13.1 | 0.09 |

The correction's far-block dependence is a tenth to a fifth of the Hessian's — but the Hessian is forty times larger, so relative to its own size the correction depends on its far blocks *more*. Both halves of the losing condition are met. **T3′ is falsified at benzene** (stand-in caveat: a DFT−DFT difference, not CC − DFT; a functional difference is itself a correlation-type correction, so the direction of the effect is expected to carry, its size not).

## 3. Why this is the physically expected answer, in hindsight

The DFT Hessian is dominated by bonded force constants — short-ranged by construction. The correction is a change in the *correlation* treatment, and in benzene the correlation that differs between functionals (and, at the anchor, between CC and DFT) is the π correlation of the ring, which is delocalised over all six carbons. So the correction inherits the range of the π system, not of the bonds. This is the same statement as T3's rate-∝-gap: the correction's range is set by the electronic gap, the Hessian's by the bonds. T3′ had the cancellation argument backwards for this class: what cancels between CC and DFT is the short-range bonded part, and what remains is the delocalised part.

## 4. What changes

- **T3′ closed at benzene** (norm and band level). The T3 proof plan keeps T3 (both Hessians decay; the difference with the slower rate) and drops the hope that the difference is easier than its parts. Ledger S1: the correction is *the* long-range object of the problem at this size.
- **For plan 05's cost question** this is the strongest negative of the evening for real-space routes: Δ₂ is less sparse than H, so nothing that relies on Δ₂ being local beyond what H is can be licensed at benzene; the mode-space deck with the symmetry prior (X10) remains the route where the counts are small.
- **For the large PAHs** the reading is the one from the T3 audit: the correction's range follows the π system and its gap; as the gap closes with size the correction gets longer-ranged, not shorter. Naphthalene's tensor (graph distance ≤ 5, C–C up to 5) tests whether the C–C ratio keeps rising beyond one ring — the pre-stated question for X9 on naphthalene.
- Nothing enters plan 05's frozen text.
