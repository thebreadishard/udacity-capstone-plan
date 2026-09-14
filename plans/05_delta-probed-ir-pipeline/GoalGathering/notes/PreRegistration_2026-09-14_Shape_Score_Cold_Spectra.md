# Pre-registration 2026-09-14 — the shape score against jet-cooled gas-phase spectra (mandate ledger idea I3), written before any network output exists

*Purpose. The user's success criterion for the reach product (P26 memo addendum, 13 September) is "a network that predicts the **spectral shape** of larger PAHs more reliably than the existing methods, or with a grounded error budget smaller than theirs". Positions at 2.5–5 cm⁻¹ are decidable only at R0–R1; but cold gas-phase **shapes** — positions and relative intensities of the whole 5–18 µm band list — exist for tetracene (item 61) and for coronene, peropyrene, ovalene and hexa-peri-benzocoronene (item 62), molecules of R2–R3 size and beyond. This note fixes, before any prediction is made, how a predicted spectrum is scored against those lists, what it is compared with, and what loses. It adds no rule to the Ladder; it defines an evaluation that the Ladder's cost and claim rules leave free (theory-vs-theory on the reach rungs remains labelled as such; this score is a laboratory-referenced *shape* comparison, not a "beat" on positions).*

## 1. The data (fixed)

| molecule | source | bands in 5–18 µm | resolution term | status |
|---|---|---|---|---|
| tetracene C₁₈H₁₂ | Lemmens et al. 2019, Table A.2 (item 61) | 34 with relative intensities (two without) | FELIX bandwidth ≈ 1 % of ν (u_res 7–17 cm⁻¹) | transcribed (`modules/03_lab_scoreboard/out/cold_columns_items61_62.csv`) |
| coronene C₂₄H₁₂ | Lemmens, Rijs & Buma 2021, Table A1 p. 9 (item 62) | 12 in 5–18 µm with relative intensities (+ 8 at 3 µm, OPO) | FELIX ≈ 1 %; OPO 0.1 cm⁻¹ | transcribed (same file) |
| peropyrene C₂₆H₁₄, ovalene C₃₂H₁₄, hexa-peri-benzocoronene C₄₂H₁₈ | Lemmens, Rijs & Buma 2021, Table A1 pp. 9–10 (item 62) | to be counted at transcription | as coronene | **to transcribe from rendered pages, with the HBC/coronene block boundary already resolved on 13 September** (no anchor job running when rendered) |

Only bands the source tabulates enter; nothing is read off figures. The 3 µm OPO bands are scored as their own family (the C–H stretch polyad region: intensities only, per decision 25's caution on fundamentals there).

## 2. The score (fixed)

For a molecule M and a family F (Module 03's frequency-window rule, `build_lab_tables.FAMILY_RULE`; the C–H out-of-plane window split by hydrogen-adjacency class only where the source assigns it), with laboratory bands {(ν_k, I_k)} normalised so that Σ_k I_k = 1 over the whole tabulated 5–18 µm list, and a predicted stick list {(ω_j, A_j)} normalised the same way:

1. **Binned shape distance.** Both lists are binned on a fixed grid of **10 cm⁻¹** (the Ladder's astronomical resolution floor; coarser than every FELIX bandwidth in the window, so the laboratory's own u_res does not dominate) from 550 to 2000 cm⁻¹ and each family window is normalised to unit sum; the score per family is the **earth mover's distance** between the two binned distributions in cm⁻¹ (the L1 distance of the cumulative distributions × bin width) — the same metric line D uses (He et al. 2026), so that a comparison with line D is on its own terms.
2. **Family-weight error.** The absolute error of the family's share of the total intensity, |Σ_F A − Σ_F I|, in percentage points — the quantity the 6.2/7.7/8.6/11.2 µm ratios of the astronomical use depend on.
3. **Position term (informational, not scored below 10 cm⁻¹).** For the family's strongest laboratory band, the distance to the nearest predicted stick of at least a quarter of that band's intensity; printed in cm⁻¹ beside u_res; counts as agreement when ≤ max(10 cm⁻¹, u_res).

The per-molecule score is the intensity-weighted mean of (1) over families; (2) is reported per family; (3) per band.

## 3. What is compared (fixed), per molecule

| column | what | provenance |
|---|---|---|
| **A** | PAHdb v4.00 scaled harmonic sticks (line A) | Module 02 atlas, version-frozen |
| **B** | PAHdb Anharmonic v1.00 where the molecule exists (coronene: Mulas 2018 lineage; else empty) | Module 02 |
| **D** | the line-D public model of He, Mai & Wang 2026 (MIT weights, SMILES in) — run only after the user permits its installation; until then empty | bibliography item 77 |
| **0** | this pipeline with Δ₂ = 0 (DFT harmonic + DFT anharmonic + DFT intensities): the null column | pipeline |
| **P** | pipeline B's own output where a deck exists (R3 coronene thin deck, if run) | pipeline |
| **N** | pipeline A (the network) where licensed for the family | P26 |

## 4. Losing and winning conditions (fixed before any column exists)

- **Losing condition for the goal sentence on shape:** on the molecules of §1, column N's intensity-weighted shape distance is not smaller than *both* A's and D's on at least two of the three families 6.2/7.7 µm, 8.6 µm, 11–13 µm, per molecule; then the network is not "better than what exists" on shape for that molecule and the sentence says so.
- **Winning condition:** N smaller than A and D on all three families on at least three of the five molecules, with the family-weight error under 10 percentage points — and the same on the Δ₂ = 0 null column *not* holding (otherwise the improvement is the anharmonic step's, not the correction's).
- **No verdict** where a column is empty; an empty D column (installation not permitted) is printed as such, never assumed.

## 5. Costs and order

Zero coupled-cluster energies. Transcription of the three remaining species: an hour with rendered pages (allowed when no anchor job runs). The scoring script joins Module 03's cold columns to any stick list; it is written when the first column beyond A exists. The D column needs `pip install torch rdkit` into a fresh environment (the user's permission; Software Changes Ledger row on the day).

## 6. Caveats written now

Jet-cooled absorption is not astronomical emission; the score judges shape at 0 K in absorption, which is what every column predicts. The FELIX bandwidth is a per-band resolution term, not a position uncertainty of the stick; positions below 10 cm⁻¹ are not scored here. Relative intensities in the source tables are peak-normalised, not integrated; the family-weight term therefore carries the source's own peak-vs-area ambiguity, printed as a caveat until a digitised spectrum allows integration.
