# Plan 06 — result note X1d (2026-09-12): plan 05's noise through the three recovery schemes

*Printed by `experiments/x1d_noise_propagation.py` on plan 05's sealed benzene dry-run tensor (the same tensor
and θ grid as X1, X1b, X1c). Full table in `experiments/x1d_noise_propagation.md`. The question, left open by
X1c and by Coleman & Moré's warning (1984, §6: substitution "may magnify errors considerably"): does the
6–7-product substitution scheme survive plan 05's per-element noise?*

## Set-up

- Noise: X2's rule, unchanged — every measured number carries Gaussian noise of standard deviation σ_E/2
  (E_h per q²), σ_E = 0.5 and 1.0 µE_h. A probe entry `(A d_k)_i` is one measured number; a directly
  measured element is one measured number. 200 noise draws per case.
- Truth: the full tensor (all 435 off-diagonal elements). The schemes assume the pattern above θ, so their
  error contains the truncation of the elements below θ as well as the noise; the noise-free column isolates
  the truncation.
- Schemes: (b) CPR direct read, (c) symmetric direct read, (c′) the same with both sides averaged where both
  are readable, (d) triangular substitution with X1c's ordering and colouring, and (e) plan 05's deck as the
  noise reference: every element measured once (its measured cost is K = 448 energies).
- Metric: the largest shift of any harmonic band position against the true tensor (cm⁻¹; X2's threshold is
  0.5 cm⁻¹), plus element errors in µE_h.

## Result (σ_E = 0.5 µE_h, θ = 0.5 µE_h — the working case of X1b/X1c)

| scheme | products | band shift, truncation only | band shift with noise, median / 95th pct | element RMS (median) | element max (95th pct) |
|---|---|---|---|---|---|
| (b) CPR direct | 15 | 0.037 | 0.067 / 0.093 | 0.158 | 1.03 |
| (c) symmetric direct | 12 | 0.051 | 0.073 / 0.101 | 0.166 | 1.06 |
| (c′) symmetric, averaged | 12 | 0.051 | 0.069 / 0.099 | 0.161 | 1.04 |
| **(d) triangular substitution** | **6** | 0.085 | **0.099 / 0.133** | 0.211 | 1.90 |
| (e) deck, every element | (448 energies) | 0.000 | 0.067 / 0.094 | 0.249 | 0.95 |

Across the whole grid (both σ_E, four θ each): no trial of (b), (d) or (e) ever moves a band by more than
0.5 cm⁻¹; (c)/(c′) exceed it in 1–12 % of the trials only at the coarsest patterns (θ ≥ 2.5 µE_h at σ_E =
1.0), and there the truncation, not the noise, is the cause (0.39–0.44 cm⁻¹ noise-free).

## Reading

1. **Substitution magnifies the noise, but mildly.** In band positions (d) sits at 1.4–1.5 × the deck's
   noise (0.099 against 0.067 median; 0.133 against 0.094 at the 95th percentile); in the worst single
   element at 2 × (1.90 against 0.95 µE_h). Nothing like the "considerable" magnification the paper warns of
   for ill-scaled directions: with 0/1 directions and short substitution chains (30 modes) the propagation
   stays bounded. The element RMS of every scheme is *below* the deck's, because fewer noisy numbers enter.
2. **The direct schemes carry no magnification at all** ((b), (c) at the deck's noise level) — their cost is
   the number of products, not the accuracy.
3. **What limits accuracy at coarse θ is truncation, not noise:** dropping the elements below 2.5–5 µE_h
   already moves a band by 0.15–0.44 cm⁻¹ before any noise. So the pattern threshold, not the scheme, is the
   accuracy knob — the same lesson as X2 (six pairs carry the positions).
4. **Consequence for S5.** At benzene the substitution scheme with 6 products recovers the tensor to within
   plan 05's own noise budget (0.1 cm⁻¹ against 0.5). Combined with X1c: **6 products ≈ 360 energies at
   X1's convention of 2M energies per product, against the deck's measured 448, at comparable accuracy.**
   Two conditions remain, both about *plan 05's engine*, not about the algebra: (i) a Hessian–vector product
   by finite differences must really cost ≲ 2M energies with noise σ_E per component (X1's convention; a
   two-sided product from energies alone costs more, and the frozen-space arm must be shown to give the
   product to that noise); (ii) the pattern must be known before the probes — plan 05's symmetry prior and,
   later, Module 05's learned prior supply it, and a wrong pattern is a truncation error of the kind in
   point 3. Whether 360 against 448 is worth a second measurement layer is a plan-05 decision, not plan 06's;
   what plan 06 can now say is that at benzene the algebra is sound, the count is real and the noise is
   tolerable.
5. **Next test for S5:** the same four schemes on the naphthalene tensor when it exists (does the
   substitution count stay near the lower bound maxr, and does the product-to-deck ratio improve with size
   — the deck grows with M², the substitution count with the maximum row count of the pattern).

## Ledger change

S5: **alive** — condition (a) of the two-sided condition (X1c) is now met at benzene as far as noise is
concerned; open: the engine-side cost of a product with noise (a plan-05 measurement) and the naphthalene
repeat. X1d done.

## Correction of the cost convention (same evening, while writing plan 05's P24)

The line "6 products ≈ 360 energies at X1's convention of 2M energies per product" inherits X1's convention,
and that convention assumes a gradient costs M energies — one-sided first differences, an accuracy plan 05 does
not accept. A second-order Hessian–vector product from energies alone costs ≈ 4M = 120 energies per product
(four points per component), so **6 products ≈ 720 energies at benzene, more than the deck's 448**. With two
analytic gradients per product (the side project's M2) the cost is 2g per product in energy units, i.e. 12g for
six — an order of magnitude below the deck if g ≲ 10. The reading of this note therefore stands for the
*algebra and the noise*; the *energy comparison* is: energies only — no gain at benzene; gradients — a large
gain that grows with size. Plan 05's P24 note carries the full table; the ledger row is corrected.
