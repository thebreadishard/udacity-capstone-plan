# Research note — the opponent atlas, first print (Module 02) — 2026-09-10

**Purpose.** Module 02's first deliverable: the three PAHdb libraries parsed into tidy tables by
`modules/02_opponent_atlas/build_opponent_atlas.py` (outputs in `modules/02_opponent_atlas/out/`,
one folder per library, each `SUMMARY.md` carrying the source file's sha256 and the XML root
attributes). The files were obtained by the user through the PAHdb download form on 2026-09-10;
the Mai et al. 2025 archive was fetched from Zenodo with the user's permission the same evening.
Every number below is copied from the printed summaries or from a pandas query on the printed
tables. This note records what the atlas *says*; the exploratory figures and the module report
follow.

**Required sentence.** This table is parsed from the public NASA Ames PAHdb v4.00 computed library
(DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the
*opponent* of this project's pipeline, not its training data.

## 1. The three libraries as served

| library | root attributes | species | bands (transitions) | source sha256 (first 16) |
|---|---|---|---|---|
| theoretical (line A) | database=theoretical, version=4.00 | **10,749** (4,479 neutral; charges −1: 1,231, +1: 2,162, +2: 2,868, +3: 9) | **2,517,399** | `0d8cb460b8c13b9a` |
| anharmonic (line B) | database=anharmonic, version=1.00 | **45** (42 neutral, 3 cations) | **95,189** (VPT2 states incl. overtones and combinations; e.g. benzene 464, naphthalene 1,222) | `2fb7a77608d57169` |
| experimental (Module 03's matrix library) | database=experimental, version=3.10 | **84** (50 neutral) | 3,896 band entries; 36 species carry a digitised laboratory spectrum | `b8b487777bd584a7` |

The uncompressed theoretical XML is 503 MB (the site's "46.65 MB" is the gzip); the streaming
parser handles it in a few minutes on the laptop.

## 2. What line A contains, and does not

- **Basis.** From the Gaussian route comment: 10,703 species at 6-31G*, **14 at 4-31G** (C₂₁₂H₄₄,
  C₂₆₈H₅₂, C₂₇₇H₄₅, C₂₉₄H₄₂²⁺, C₃₈₄H₄₈ and their charge states), 32 with `chkbas` (the basis read
  from a checkpoint — Mg/Fe/Si-containing species) or another functional (one BP86/6-31+G*).
  The **4-31G regime starts at n_C = 212**; the largest 6-31G* species has n_C = 294. The
  101–386-carbon bin holds 750 + 24 = **774 species**, the number the v4.00 paper gives.
- **Scale factors as stored.** `<frequency scale="…">` stores the *scaled* value (naphthalene's
  C–H stretch 3065.0 with scale 0.9597 → 3193.7 unscaled, a B3LYP/6-31G* harmonic value). For the
  6-31G* species the three factors are **0.9794 (below ≈ 1,088 cm⁻¹), 0.9691 (≈ 1,077–1,744) and
  0.9597 (above ≈ 2,590)**; for the 4-31G species 0.9563 / 0.9523 / 0.9595; smaller sets carry
  0.9097, 0.9908, 1.0145, 1.0051 and others. **Not one of the 2,517,399 bands carries the factors
  0.964 / 0.979 / 0.975 that Frozen_Lines §2 quotes from the v4.00 paper.** The atlas scores the
  library as served; the paper's numbers are re-read against its text before the pilot note
  (dated note in Frozen_Lines).
- **Ladder presence.** **Benzene is absent** from the theoretical library (no C₆H₆ at any charge),
  so line A has no R0 entry; naphthalene uid 330; pyrene 334 and 387 (C₁₆H₁₀ isomers), five
  C₁₈H₁₂ isomers (uids 211, 280, 282, 291, 2355), coronene uid 18 (6-31G* in v4.00); 5,110
  species with 54 ≤ n_C ≤ 216.
- **Debt 6 answered.** **C₃₈₄H₄₈ is in v4.00: uid 617 (neutral, 4-31G, 1-A1g, 1,290 modes) and
  uid 4447 (dication)**; no other species between 300 and 400 carbons. `c384_class.csv`.

## 3. What line B contains

45 species from benzene (uid 100000) to C₁₈H₁₂, including 22 cyano/isocyano derivatives, indole,
indene, biphenylene, and three cations. On the ladder: **benzene, naphthalene (330), pyrene (334)
and tetracene (282)**; **chrysene, triphenylene and coronene are absent**, so line B exists at R0,
R1 and two of the four R2 species and not at R3. The route field holds only the species name; the
method (B3LYP/N07D, VPT2 with polyads) is documented in the papers, not in the file. Transitions
carry frequency and intensity but **no symmetry label** in this library. Benzene's strongest
entries: 675.37 cm⁻¹ (114.5 km/mol), the C–H stretch polyad 3041–3106 (25.2 + 24.7 + 19.9 + 19.3 +
9.9 + 7.1), 1481.01 (5.9); 24 of its 464 entries exceed 1 km/mol. Beside the laboratory scoreboard
of the same day (673.90 on the 0.125 cm⁻¹ record; 105.3 km/mol) these are the numbers the pilot
note's null row will be judged against — recorded here, not scored.

## 4. The other two lines

- **Line C (Mai et al. 2025).** The Zenodo archive (`Supplementary.zip`, 102,343,899 bytes, sha256
  `8c3688f9f18e0f6a…`) holds the code, the two model pickles, the 1,704 PAHdb geometries, and the
  spectra as text files per species in three zips — **50 K, 300 K and 600 K**, "qm0" = without
  quantum correction — plus the 49 experimentally tested species. **Read in the same evening**
  (`build_line_c_table.py`, `out/lineC_mai2025/`): **1,705 species** (1,704 PAHdb uids at all three
  temperatures + the EXP set), spectra on a 1 cm⁻¹ grid 300–3800 cm⁻¹ with intensities *normalised
  per spectrum* — so **line C carries positions only**, no absolute intensities and no stick list;
  412,938 maxima extracted (≥ 5 % of each spectrum's maximum, ≥ 3 cm⁻¹ apart, parabolic apex).
  Ladder: benzene absent; naphthalene 330; pyrene 334 and 387; seven C₁₈H₁₂ isomers; coronene 18;
  largest species C₂₁₆H₃₆ (uid 615).
- **Cheap line (Bos et al. 2025).** The Supporting Information (seven files, 20.5 MB: two
  spreadsheets, three zips, a 13.5 MB text file and a PDF) is served by Europe PMC's supplementary
  endpoint for PMC12750190 as well as by ACS; the Europe PMC copy entered `data/` on the user's
  instruction. **Read the same evening** (`build_cheap_line_table.py`, `out/cheapline_bos2025/`):
  the SI's ML-scaled table covers **81 species** (all PAHdb theoretical uids, n_C 10–50; the paper's
  "almost all of the 4000+ compounds" is not what the SI holds), **6,591 bands**, the authors' own
  B3LYP/4-31G harmonic frequencies with a *uniform* conventional factor 0.962 and the SVR prediction
  beside them (SVR − conventional: mean −0.4 cm⁻¹, mean absolute 3.9, range −18 to +21); the 465
  training instances carry no species identifier. Ladder: benzene absent; naphthalene 330; pyrene
  334, 387; C₁₈H₁₂ 280, 282, 291; coronene 18.

## 5. Consequences to record elsewhere

1. Frozen_Lines §2: the scale factors as stored; benzene absent from line A; debt 6 paid.
2. Proposal §7 / Ladder R0 row: benzene is an agreement rung (decision 28) — nothing is "beaten"
   there and no line is an opponent at R0; the atlas only says which **printed comparison columns**
   exist beside the laboratory band: line B, and the cheap line's method (its own table, being
   PAHdb-theoretical-based, also lacks benzene). Line A's column at R0 is empty by construction.
3. Line B's R2 coverage is pyrene and tetracene only; chrysene and triphenylene are scored against
   line A and the cheap line.
4. Line C is a positions-only opponent (normalised spectra); the intensity comparison of decision 18
   has opponents A and B only. The cheap line exists as a *table* for 81 species (R1–R3 all present)
   and as a *method* (pickled SVR on five computed features) for the rest; at R0 the only table
   that contains benzene is line B's, printed beside the laboratory band for information (decision
   28), not as a line to beat.
