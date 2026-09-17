# X20 — gradient noise through the 18-gradient construction (17 September 2026)

*Run: `x20_gradient_noise_propagation.py` and `x20b_prior_bias.py` on the naphthalene dry run's direct Δ₂
(`results_dryrun/naphthalene_sym/stageA_hessians.npz`, 48 modes, B3LYP→BHHLYP stand-in). 200 noise draws
per point. No new energies. Answers the gap X14 left: it recovers exactly from **exact** products, and the
substitution method back-substitutes previously recovered elements, so error could accumulate.*

## The construction, reproduced on the dry run's own data

48 modes, **141 same-irrep pairs** of 1,128 — X14's row (a) count, reproduced here from the stage A irrep
labels rather than from X13's table. Colouring gives **9 products = 18 gradients** for 189 unknown
elements from 432 equations; the dense pattern needs 48 products = 96 gradients for 1,176 unknowns.

## 1. What the prior itself costs

The symmetry prior drops 987 of the 1,128 pairs. On the real Δ₂ those dropped elements are not exactly
zero — largest **2.611 µE_h**, RMS 0.352 µE_h, against 775.9 µE_h for the largest allowed element. What
that truncation costs in the quantity the project measures:

| family | CC-stretch | CH-ip-bend | CH-oop | CH-stretch | ring-ip |
|---|---|---|---|---|---|
| cm⁻¹ | 0.0017 | 0.0003 | 0.0003 | 0.0004 | 0.0003 |

**Worst family 0.0017 cm⁻¹ against a 0.5 cm⁻¹ target.** The prior is free at naphthalene.

## 2. How noise propagates

A product is (g(+q) − g(−q))/2q, so each component carries σ_g·√2/2 at q = 1. Element RMS error and worst
family, averaged over 200 draws:

| σ_g (µE_h per unit q) | 0.1 | 0.5 | 1.0 | 2.0 | 5.0 | amplification |
|---|---|---|---|---|---|---|
| symmetry, substitution (18 grad) — elements | 0.027 | 0.134 | 0.267 | 0.537 | 1.339 | **0.27** |
| symmetry, least squares (18 grad) — elements | 0.020 | 0.101 | 0.203 | 0.403 | 1.006 | **0.20** |
| dense, substitution (96 grad) — elements | 0.071 | 0.353 | 0.706 | 1.418 | 3.535 | **0.71** |
| worst family, cm⁻¹ (all three agree to ~2 %) | 0.009 | 0.047 | 0.095 | 0.19 | 0.46 | |

Three readings.

**Substitution does not amplify.** The feared accumulation along the elimination order does not happen
here: the amplification factor is **0.27**, i.e. the recovered elements are *quieter* than the gradients
that produced them, because 432 equations determine 189 unknowns and the surplus averages noise down.

**Fewer gradients are also less noisy.** The 18-gradient symmetry route has element error 0.27 against
the 96-gradient dense route's 0.71 — the prior removes 987 unknowns, so what is left is better
determined. Cheaper and steadier at once, which is unusual enough to state plainly.

**The whole plan's noise grid fits.** Across σ_g = 0.5 to 5 µE_h per unit q — the range the plan already
uses — the worst family stays between 0.05 and 0.46 cm⁻¹, inside the 0.5 target at every point, with the
top of the range only just inside.

Least squares on the same 18 gradients is about 25 % quieter than substitution in the elements, and the
two are indistinguishable in frequency. It costs nothing extra: same gradients, a 432 × 189 solve instead
of a back-substitution. Worth taking for the margin.

## What this leaves open

- **σ_g itself is unmeasured** for the frozen-space correction. X20 turns that into a specification
  rather than an unknown: **σ_g ≤ 5 µE_h per unit q** keeps the worst family under 0.5 cm⁻¹, with σ_g ≤ 1
  giving a comfortable 0.1 cm⁻¹. That is a number the M2 build (or a bought gradient implementation) can
  be held to.
- Naphthalene only, and the DFT stand-in's Δ₂. The pattern is a symmetry statement and carries over; the
  magnitudes are the stand-in's.
- g, the gradient-to-energy cost ratio at LNO-CCSD(T), is still unmeasured and still needs a machine this
  laptop is not.
