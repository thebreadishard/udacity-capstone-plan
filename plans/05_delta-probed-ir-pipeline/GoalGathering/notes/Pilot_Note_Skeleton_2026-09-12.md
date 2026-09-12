# Pilot note — skeleton with the measured inputs filled in (2026-09-12 evening; NOT the pilot note)

*The Ladder (§4, "Frozen at the pilot note") fixes the form of the pilot note now and its numbers later. This
skeleton lists, item by item, what the note must fix, which measured inputs already exist (value and file), what is
still missing, and where the user has a choice. It contains **no local-CC Δ₂ number and no pipeline-vs-lab
number** (none exists; the benzene reference energies stay sealed), so writing it does not breach the order rule of
Ladder §3 ("Order of the pilot inputs"). It becomes the pilot note only when the prerequisites of §A are all met and
the user fills the choices of §C; then it is committed as a dated note and the sealed fits are opened.*

## A. Prerequisites (Ladder §4 (a)–(f)) — status

| prerequisite | status 2026-09-12 | source |
|---|---|---|
| (a) R0 pilot: geometry, DFT Hessian, harmonic bands, timings, zero-CC dry run in both modes with the noise-injection column, at R0 **and at the largest sizes the laptop affords** | benzene: **done** (dry run of 2026-09-05; mode E K = 448 at ρ_off under the P1+P2 reading, mode G 60–96; σ_E pooled 0.147 µE_h; c-vs-K curves for σ_E = 0.5/1/2 µE_h). Naphthalene: **geometry only** (B3LYP/6-31G*, 2026-09-08); its DFT dry run (two functionals, Hessians, both modes) is owed — hours of psi4, after the anchor job | `probes/results_dryrun/benzene/REPORT.md`, `results_dryrun/naphthalene/geometry.json` |
| (b) scoreboard re-read probe with M03's u_band table | **done today**: u_band per gas band (floor form), 4,218 × 31 table, `U_BAND.md`; the GC-IRD temperature is a labelled assumption (item 50 read: SRD 35 documents none) | `modules/03_lab_scoreboard/` |
| (c) canonical feasibility probe (one canonical CCSD(T) energy of benzene in the anchor basis on the laptop) | **done**: cc-pVTZ canonical CCSD(T) 755 s, peak 7.3 GB (2026-09-10); cc-pVDZ 27 s | `probes/results_timing/benzene_cc-pvtz_tight.json` |
| (d) gradient run/no-run at equilibrium | **done**: canonical CCSD(T) gradient at cc-pVDZ runs (1,399 s, 13.9 GB); the local-CC engine has **no** analytic gradient (no-run); the AD route is the side project (M2) | `probes/results_timing/benzene_cc-pvdz_canonical_gradient.json` |
| (e) probe M1 (frozen spaces) | **done**: arm A smooth to σ 0.003–0.044 µE_h at tight and xtight; the anchor runs at xtight (decision 20); decision 33 basis terms implemented | `probes/results_m1/`, README decisions 20, 33 |
| (f) the **R1 smoothness probe's σ** (M1 at naphthalene, arm A along the probed modes; fits sealed) | **not run — and now the blocker, see §D**: at xtight one naphthalene energy is ≈ 2 days on the laptop (measured tonight, fragments 1–2; whole energy running), so a 27-point smoothness scan is ≈ 50 laptop-days; a 9-point scan ≈ 18 | this note §D |

## B. The fifteen items of Ladder §4 — what each fixes, what is in hand, what is missing

| # | fixes | in hand (measured) | missing | user's choice |
|---|---|---|---|---|
| 1 | exact band list per molecule (uid / CAS, window, class); per family *gas-decidable / matrix-gated / inconclusive by construction*, with u_band | Module 03: 318 gas peaks (8 records), 3,896 matrix bands; u_band per gas band; matrix–gas offsets +3.3…+5.9 cm⁻¹ (6 families); R0 QUANT-IR u_band 2.55; hot GC-IRD u_band 8.6–16.2 → C–C families inconclusive by construction on that source, as the Ladder foresaw | PNNL naphthalene record (R1's room-temperature source; licensed database, user), cold columns 61–62 (tetracene, coronene), Q9 hydrogen-adjacency sub-families for C–H oop | which margin form: floor or ±30 %-corrected hot columns |
| 2 | beat margin per family (lab + opponent side only); promised families closed; expected-effect line | opponents printed (Module 02: line A as served, decision 30; benzene absent from A; line B 45 species); M04 baseline = line A (MAE 6.49 vs 6.40); Esposito benzene 5.45 cm⁻¹ line ready | margins themselves | **the margins per family** (the central choice) |
| 3 | P-gate numbers (0 imaginary; no scale factor on anharmonic output) | dry run: 0 imaginary at benzene; policy text ready | — | none |
| 4 | matrix shift tolerance as measured by Module 03 | +3.3…+5.9 cm⁻¹ median offsets (hot gas vs 10 K matrix), pooled p 1.6e-10; Coblentz 245 °C column +1.4 | equal-temperature shift not measurable from these sources | tolerance value (from the offsets or from item 52's Ne–gas columns) |
| 5 | P3 effect size (learned prior's required saving in K or ρ at fixed K), also on PAH held-out tensors | dry-run K = 448 mode E; the structural prior's K (57 same-representation pairs → K ≈ 220–380 at R1); **plan 06 X10 (12 Sep evening): a free DFT-only ranking (resonance denominators within an irrep) already selects 19 of 47 eligible pairs for 0.5 cm⁻¹ at benzene, a perfect element-size prior 17 — the baseline a learned prior must beat** | Module 05 corpus (factory timing test owed); X10 repeated on naphthalene | effect size |
| 6 | M04 baseline recipe | **done** (RECIPE.md ea9c07c; ridge α = 1, LOMO, MAE) | — | none |
| 7 | resonance handling per rung; closed family set at depth one + totally symmetric modes; sizes printed | dry run's family/irrep table for benzene | the r₃/r₄ thresholds and polyad cap; naphthalene's closed set | thresholds (candidates: Fusè et al. 2024 κ_E 0.01/0.005, DDR gap < 100 cm⁻¹ — item 28) |
| 8 | stopping constant c per mode on ρ_off (decision 12) | dry run: mode E at σ_E = 0.5 µE_h: K = 490 for c = 1–3 on ρ_off (ρ_noise,off 0.068, ρ_dry,off 0.204); at σ_E = 1.0: 496–498; mode G: 64–96 | σ_E of the R1 smoothness probe (prerequisite f) — the σ that selects the row | c |
| 9 | K_cap per rung and mode, from the noise-injected dry-run K by a stated factor; n_min(G) | benzene rows above | naphthalene dry run (a) | the factor |
| 10 | hold-out fraction f_h and seed | — | — | f_h, seed |
| 11 | Q7 tolerance τ₇ (≤ smallest beat margin) and d₇ | u_band table bounds the margins from below | margins (item 2) | τ₇, d₇ |
| 12 | Q8 numbers: r_max, ε₈, η₈, γ, step h, direct-coupling pair list per rung | X5 of plan 06 (2026-09-12): at benzene 93.5 % of ‖Δ₂‖²_F on atoms + bonds, carbon ring flat — informs the pair classes near/mid/far | naphthalene tensor | the numbers |
| 13 | Q6 numbers: τ in the noise lines, bias line, threshold formulas; q_s per rung and mode; CPS decision; band width w and weights | M1: σ and the estimator; q_s = 1.0 at benzene; decision 20 (xtight) and 33 (basis terms) | τ (from item 2), q_s at R1 | CPS: not needed at xtight? (record) |
| 14 | Q9 inputs (decision 27): family list with C–H oop split by hydrogen adjacency, τ_F, the two rules, LOMO protocol | family rule of Module 02/03 (frequency ranges) | DFT mode-vector families (owed, Module 03) | none beyond item 2 |
| 15 | Q10 pass thresholds (overall k = 2 coverage, per-rung floor) | `probes/q10_coverage.py` pre-registered tonight: arithmetic fixed, no verdict until thresholds set; readiness table 47 rows | — | **the two thresholds** (candidates: overall k = 2 ≥ 0.90; per-rung floor ≥ 0.80 — proposals, not decisions) |

## C. The user's choices, collected (nothing else is a choice)

margins per family (2) · matrix tolerance (4) · P3 effect size (5) · resonance thresholds (7) · c (8) · K_cap factor (9) ·
f_h and seed (10) · τ₇, d₇ (11) · Q8 numbers (12) · Q10 thresholds (15) · the form of the hot-column temperature term (1).

## D. The blocker: prerequisite (f) at the anchor's thresholds

The Ladder asks for the R1 smoothness probe's σ before the note, "fits sealed". Written on 2026-09-04, when one
naphthalene energy was priced in hours. Tonight's measurement puts one xtight naphthalene energy at ≈ 2 days on the
laptop, so the 27-point scan of probe M1 at R1 is ≈ 50 laptop-days and even 9 points ≈ 18. Three ways to satisfy the
letter and the intent, for the user to choose between (a proposal, not a decision):

1. **σ at tight thresholds, 9 points, one mode** (11.5 h per energy → ≈ 4 days): σ is a smoothness property of the
   frozen arm and did not change between tight and xtight at benzene (0.003–0.044 µE_h at both), so σ(tight) is a
   measured stand-in for σ(xtight), labelled as such; the bias line is not needed for the note (it is CC-vs-CC).
2. **σ at xtight on the first machine that can afford it** (the desktop or the cluster's first job after the
   timing), and the note waits for it — consistent with P13's timing.
3. **Use benzene's σ with a labelled size extrapolation** — the weakest option; the Ladder's item 8 reads c "at
   the σ_E the R1 smoothness probe printed", so this would need a dated amendment.

**Decided by the user the same evening = decision 35: option 1** (σ at tight, 9 points, one mode — the C–C stretch family, largest σ at benzene), launched right after the naphthalene timing and the naphthalene DFT dry run; option 2 as the check when the R1 machine exists.

## E. What this skeleton is not

Not the pilot note (no dated commitment, no sealed fits opened, no choices made); not a change to any frozen text.
When the prerequisites are met, this file is copied to `Pilot_Note_<date>.md`, the choices filled, the sealed
`m1_sealed_energies.sha256` referenced, and the README's owed list updated.
