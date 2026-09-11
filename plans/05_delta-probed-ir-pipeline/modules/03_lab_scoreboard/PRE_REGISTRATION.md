# Module 03 — pre-registration of the matrix–gas hypothesis test (frozen 2026-09-11, before the join)

This note fixes the form of Module 03's one hypothesis test **before any matrix band has been
matched to any gas-phase peak** (Capstone_Mapping §M03: "pre-registered hypothesis test, form frozen
before the data is joined"; Ladder §2, the matrix–gas gate). It is committed on its own, ahead of the
scripts that compute the join. Anything below may later change only by a dated note that names the
reason and keeps the result obtained under this form.

## Question

Is the offset between a band's position in an argon matrix (PAHdb experimental library) and its
position in the gas phase (NIST WebBook records) zero, per band family? This is the quantity the
Ladder's matrix gate consumes for the molecules that have matrix data only (pilot-note item 4).

## Data (all held in this repository before this note)

| side | source | records used | fixed by |
|---|---|---|---|
| matrix | PAHdb experimental library v3.10, parsed by Module 02 (`../02_opponent_atlas/out/experimental_3.10/`, source XML sha256 `b8b48777…`) | neutral naphthalene (uid 330), anthracene (265), pyrene (334), chrysene (291) — the four neutral species that also have a gas-phase record below | Hudgins & Sandford 1998 conditions: Ar, 10 K, 0.9 cm⁻¹ resolution (item 8, read) |
| gas, primary | NIST WebBook, `$NIST SOURCE=MSDC-IR` (NIST/EPA gas-phase GC-IRD series, SRD 35), plan-04 and plan-02 caches | `C91203_0` naphthalene, `C120127_0` anthracene, `C129000_0` pyrene, `C218019_0` chrysene | `##STATE=gas`, `##DELTAX=4.0`; resolution 8.0 cm⁻¹ per the series' description (item 50, snippet grade); temperature not stated (hot lightpipe) |
| gas, secondary (labelled, not pooled) | Coblentz vapour record `C91203_1` naphthalene, 245 °C, 4 cm⁻¹ | naphthalene only | printed as its own column |

Benzene (gas only), triphenylene (gas only) and tetracene (matrix only) cannot be paired and are
excluded from the test; they stay in the dataset for the descriptive part.

## Definitions (fixed)

1. **Gas peak.** A local maximum of the absorbance record (transmittance records converted by
   A = −log₁₀ T) with prominence ≥ 5 σ and S/N ≥ 10, where σ is the robust noise (1.4826 × MAD) of the
   linearly detrended 2400–2500 cm⁻¹ window of the same record. Position = apex of the parabola through
   the maximum and its two neighbours. FWHM measured on the record; u_c = FWHM / (2 · S/N).
2. **Matching (the join).** For each gas peak, the candidate matrix bands are those of the same species
   within ±20 cm⁻¹ of the gas position (window = the published 0–15 cm⁻¹ order of matrix shifts, Hudgins
   & Sandford 1998, plus the 4 cm⁻¹ grid). The candidate with the **largest matrix intensity** is taken.
   One-to-one: if two gas peaks select the same matrix band, the closer gas peak keeps it and the other
   is left unmatched; no second choice. Unmatched gas peaks and unmatched matrix bands are counted and
   printed.
3. **Quantity.** Δ = ν_matrix − ν_gas per matched pair, in cm⁻¹. Δ is the offset between the two sources
   *as they exist* (10 K matrix against a hot vapour); it is not corrected to equal temperature. That is
   deliberate: it is the offset the scoreboard will face.
4. **Family.** The frequency-range rule of Module 02 (`FAMILY_RULE`), applied to the gas position.
5. **Minimum size.** A family with fewer than 6 pairs is reported as *inconclusive by construction*
   (the smallest two-sided exact Wilcoxon p at n = 5 is 0.0625, above α); it is not tested.

## Test (fixed)

- **H₀ (per family):** the distribution of Δ is symmetric about 0 (median offset zero).
  **H₁:** it is not (two-sided).
- **Statistic:** Wilcoxon signed-rank (Wilcoxon 1945) on Δ, `scipy.stats.wilcoxon(d, zero_method="wilcox",
  alternative="two-sided", method="auto")`; W and p printed per family with n.
- **α = 0.05**, Holm–Bonferroni across the families tested.
- **Secondary, declared:** the same test on all pairs pooled, α = 0.05, printed beside the per-family
  results and never substituted for them.
- **Printed, not tested:** per family n, median Δ, mean, SD, a 95 % bootstrap percentile interval of the
  median (10,000 resamples, seed 0), and the share of pairs with |Δ| ≤ 8 cm⁻¹ (the gas resolution).
- **Outcomes allowed:** reject H₀ / do not reject H₀ / inconclusive by construction. All three are
  reported as found. Not rejecting H₀ is *not* evidence of zero shift; the report says so.

## Assumptions declared

Pairs are treated as exchangeable within a family; bands of one molecule are not fully independent,
and four molecules carry the whole test — a limitation stated in the report, not repaired here. No
normality is assumed. The 8 cm⁻¹ gas resolution and the 4 cm⁻¹ grid bound how small an offset this
data can show; the report prints u_c and u_res beside every Δ.

## What this note does not decide

The beat margin per family and the verdict *matrix-gated / decidable / inconclusive by construction*
belong to the pilot note (Ladder §2). This module prints the numbers the pilot note will consume.
