# Research note — the R0 laboratory scoreboard, first print (probe 2a, Module 03) — 2026-09-10

**Purpose.** Module 03's first deliverable, built while the naphthalene timing occupies the laptop:
the benzene gas-phase scoreboard from the NIST Quantitative Infrared Database record (Chu, Guenther,
Rhoderick & Lafferty 1999, item 56; WebBook CAS 71-43-2, `$NIST SOURCE=QUANT-IR`), printed by
`probes/m03_band_uncertainty.py` into `probes/results_m03/benzene/SCOREBOARD_benzene_quantir_1p93.md`
and `.json`. Every number below is copied from that print; the script's constants are all listed
there as pilot-note candidates. Nothing in the Ladder changes; the decidability rule is applied as
frozen (Ladder §2, with the dated note of 2026-09-06 for the temperature term).

## 1. The source record

The record held is the plan-02 cache copy of the WebBook's QUANT-IR entry at **1.929 cm⁻¹
resolution, boxcar apodisation** (header: NIST Analytical Chemistry Division, gas, 23 °C, benzene
primary gas standard, 1 L/min flow, 3,526 points 575.65–3974.61 cm⁻¹, y in (µmol/mol)⁻¹ m⁻¹ base 10);
copied to `probes/scoreboards/benzene/C71432_quantir_res1.93_boxcar.jdx`, sha256 printed in the
scoreboard. It is one of the twenty QUANT-IR entries the WebBook lists for benzene (item 54,
0.125–1.93 cm⁻¹, five apodisations); the 0.125 cm⁻¹ entry is the one the Ladder's R0 paragraph
expects and is **not held** — fetching it is asked of the user below. Contrary to item 54's note,
the record header does state a temperature (23 °C), consistent with Chu §2.3's 296 K correction.

## 2. What the print says (benzene, four IR-active fundamentals)

| family | DFT mode(s), irrep | peak (cm⁻¹) | centroid | u_band (cm⁻¹) | A (km/mol) | certified |
|---|---|---|---|---|---|---|
| C–H out-of-plane | 4, a₂u | 672.86 | 673.13 | 3.2 | 104.6 ± 1.7 (source) ± 0.4 (baseline) | yes |
| C–H in-plane bend | 13–14, e₁u | 1036.54 | 1035.53 | 3.2 | 8.2 ± 0.1 ± 0.3 | yes |
| C–C stretch | 20–21, e₁u | 1481.93 | 1487.44 | 3.2 | 15.7 ± 0.3 ± 0.4 | **no** (H₂O window 1325–1900) |
| C–H stretch | 27–28, e₁u | 3046.39 | 3067.99 | 3.2 | 74.2 ± 1.2 ± 0.6 | yes |

u_band = √(res² + u_c² + cal² + u_296²) with res = 1.929 (the record's stated resolution), u_c ≤
0.085 (FWHM/(2·S/N); S/N 104–4,984), cal = 0.0042 (Chu §2.4), **u_296 = 2.55 cm⁻¹** for every
family (§3). Without the temperature term u_band is 1.93 cm⁻¹, i.e. the resolution. Against the
candidate margins printed with the table, every family is decidable at 5 and 10 cm⁻¹ and none at
2 cm⁻¹; the pilot note fixes the margins. The observed/harmonic-DFT ratios are 0.952–0.970 (B3LYP/6-31G*),
inside the pre-registered matching window 0.90–1.00; no maximum above 2 % of ν11 lies outside the
four integration windows.

**Two rules were changed while building, before any comparison existed, and are recorded as
such.** (i) The integration window first stopped at the first local minimum on either side of the
peak, which cut benzene's ν11 to its Q branch (44.6 km/mol); a 5 %-of-peak threshold then lost the
P/R wings (31.0), the Q branch being sixty times higher than the wings. The rule now is the
contiguous region above 3σ of the baseline noise (measured in 2400–2500 cm⁻¹), at most ±150 cm⁻¹,
and the window is printed per band; neighbouring bands inside it are integrated with it (the C–H
stretch row is the 3,013–3,127 cm⁻¹ band system, which is why its centroid sits 22 cm⁻¹ above its
peak). (ii) Maxima inside a scored window are not listed as unassigned bands (the ν11 wing
structure had filled that list).

## 3. Two things for the user

**P21 — the temperature term at benzene.** The frozen rule gives u_296 by item 52's Bose model
with the floor slope 0.044 cm⁻¹ K⁻¹ (benzene has no measured slope) and ν_m = the mean of the DFT
modes below 700 cm⁻¹ (415, 415, 622, 622, 695 → 554 cm⁻¹; θ = 797 K, n̄(296) = 0.073): **2.55 cm⁻¹**,
the same for every family. It is the largest term in u_band and would stay so on the 0.125 cm⁻¹
record. For R0 as an agreement rung (decision 28) this means "agree within ≈ 2.6 cm⁻¹ ⊕ the
pipeline's budget", which is lenient for benzene. The Ladder already allows the alternative: a
**pinned per-family correction** with ±30 % as u_T. At benzene the pipeline can compute that
correction itself — the 296 K shift of each fundamental from the DFT anharmonic constants, Σ_k
X_ik n̄_k(296 K), which is exactly item 52's model with the real bath instead of one mean mode. If
the shifts are of order 1 cm⁻¹, u_T falls to ≈ 0.3 cm⁻¹ and u_band to ≈ 0.35 on the 0.125 record.
Options: (a) keep the floor as printed; (b) pre-register the computed correction with ±30 % for
R0 and R1 (both room-temperature sources), printed by 2a from the pipeline's own X_ik before any
CC number exists. The note proposes (b); it is a change to a scoreboard constant, not to the rule.

**Fetch request.** The 0.125 cm⁻¹ boxcar QUANT-IR benzene record from the WebBook (item 54's list;
`cbook.cgi?ID=C71432&Type=IR-SPEC&Index=<n>` in JCAMP form), ≈ 400 kB; with it the resolution term
drops from 1.93 to 0.12 cm⁻¹ and the peak positions gain a decimal. The script takes it with
`--jdx` and `--tag quantir_0p125`, and both prints stay on file (the pilot note names the entry
scored; no swap after a comparison exists).

## 4. Owed next in Module 03

R1: the PNNL naphthalene record (Schneider 2024 / Sharpe 2004, items 57, 59 — not held as a
file; the record must be obtained from PNNL) and Pirali's sixteen resolved fundamentals (item 53,
held; a table transcription with the 0.5 cm⁻¹ head-to-origin term of decision 21). R2/R3: the
WebBook GC-IRD entries (plan-02/04 caches: pyrene, chrysene, triphenylene), the jet-cooled lists of
items 61–62 and the Joblin hot columns (item 64). Each is a run of the same script with a source
class and its own constants; the families come from each molecule's dry-run mode table, which for
naphthalene and larger does not exist yet (the naphthalene dry run is owed).
