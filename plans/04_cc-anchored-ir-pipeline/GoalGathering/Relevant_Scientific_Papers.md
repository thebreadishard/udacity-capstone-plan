# Relevant scientific papers — Plan 04

**Rule.** Do not cite from recall in a scored document. Every identifier below is re-fetched
before it enters a Module 03–09 reference list. A `plan-02/03 record` or `NOT FETCHED` status
is not a cite. Statuses: **OK (2026-09-02)** = landing page / Crossref / arXiv / full text
fetched this pass; **record** = identifier carried from the plan-02/03 bibliographies (git
history), re-verify at first scored use; **NOT FETCHED** = named debt.

| # | Use in plan 04 | Working identifier | Verify |
|---|---|---|---|
| 1 | **Line A** — PAHdb computed library v4.00 | Ricca, Boersma, Maragkoudakis, Roser, Shannon, Allamandola, Bauschlicher, ApJS **282**, 7 (2026). DOI 10.3847/1538-4365/ae1c38 | **OK (2026-09-02)** — IOP full text (open access). 10,749 species; 6-31G*, 4-31G above 200 C; scale factors 0.964/0.979/0.975 on 25 gas-phase bands; size bin to 386 C; systematics "currently unquantified"; N_carbon,max = 384 in their Orion Bar fit |
| 2 | Line A scale-factor lineage (v3.00) | Bauschlicher, Ricca, Boersma, Allamandola, ApJS **234**, 32 (2018). DOI 10.3847/1538-4365/aaa019 | **OK (2026-09-02)** — via the PAHdb citations block; landing not opened. Fetch landing at first scored use |
| 3 | PAHdb v2.00 (website/tools paper) | Boersma et al., ApJS **211**, 8 (2014). DOI 10.1088/0067-0049/211/1/8 | **OK (2026-09-02)** — via the PAHdb citations block |
| 4 | **Scoreboard** — PAHdb laboratory spectra | Mattioda et al., ApJS **251**, 22 (2020). DOI 10.3847/1538-4365/abc2c8 | **OK (2026-09-02)** — via the PAHdb citations block. Experimental library now v3.10 (2023-04-13, 84 species); gas-phase library v1.00 (2026-07-01, 5 spectra) per the versions page |
| 5 | **Line C** — MLMD anharmonic to C₂₁₆ | Mai, Wang, Pan, Schörghuber, Kovács, Carrete, Madsen, MNRAS **541**, 3073 (2025); arXiv:2503.05120 (v3) | **OK (2026-09-02)** — arXiv abstract. MNRAS landing **NOT FETCHED** — debt. 1,704 species, several temperatures, linear scaling, DFT-teacher ceiling |
| 6 | **Line B** — anharmonic DFT-QFF pyrene/coronene | Mulas, Falvo, Cassam-Chenaï, Joblin, JCP **149**, 144102 (2018). DOI 10.1063/1.5050087; arXiv:1809.05669 | **record** (plan-02, verified 2026-08). Its own limit: "the accuracy of the underlying calculations of the quartic force field" |
| 7 | **Cheap line** — ML-corrected DFT scaling | Bos et al., "Ethereal AI…", ACS Omega **10**(50), 62282 (2025). DOI 10.1021/acsomega.5c10225 | **OK (2026-09-02)** — Crossref record (title, authors, venue, dates, CC licence). **MAE value not re-read** (ACS 403) — debt before quoting a number |
| 8 | Matrix lab source behind PAHdb entries | Hudgins & Sandford, J. Phys. Chem. A **102**, 329 (1998). DOI 10.1021/jp9834816 | **record** (verified 2026-08-28 via Crossref; closed access; PAHdb carries the spectra per-uid) |
| 9 | Modern gas-phase/IRMPD standard at rung R2 (cations) | Tang et al., JCP **163**, 044304 (2025); arXiv:2504.11898 | **record** (plan-02). Warning it carries: harmonic+scaling often already fits band profiles — where anharmonicity pays must be shown, not assumed |
| 10 | Transformer-family precedent for M05 | Ji et al., DetaNet, arXiv:2510.04227 (2025) | **record** (plan-02). Equivariant tensor-attention; IR/Raman from MLMD/RPMD |
| 11 | Tier-1/2 emission machinery template | Chen, Li & Li, A&A (2026); arXiv:2607.20015 | **record** (plan-02). VPT2 + microcanonical cascade for cyanonaphthalenes, at B3LYP — the electronic-structure gap this plan attacks sits under it |
| 12 | PAHdb Anharmonic v1.00 method papers | Mackie et al. 2015–2022; Esposito et al. 2024a–c (per the v4.00 outlook) | **NOT FETCHED** — debt. Pin before any scored comparison against line B's PAHdb half |
| 13 | Closest precedent for the M05 method, and its warning | Lam, Abdul-Al, Allouche, JCTC (2020). DOI 10.1021/acs.jctc.9b00964; arXiv:1909.12661 | **record** (plan-02). QM harmonic + ML anharmonic corrections, 37 molecules; RMSD 21/23 cm⁻¹ — cited so tolerances are not quietly relaxed to match it |
| 14 | Origin of the hybrid split (harmonic anchor + cheap anharmonic) | Boese, Klopper, Martin, Mol. Phys. **103**, 863 (2005). DOI 10.1080/00268970512331339369; arXiv:physics/0411065 | **record** (plan-02) |
| 15 | DLPNO caveat on delocalized π | Sylvetsky & Martin (2020) — TightPNO (the tightest standard DLPNO threshold set) needed for delocalized systems | **record** (plan-02; exact identifier must be re-pulled from the plan-02 bibliography in git history before use). Directly feeds the R1 license check and the roughness stop-condition |
| 16 | Δ-learning precedent (~10² high-level points suffice) | Käser & Meuwly, arXiv:2103.05491; and Käser et al., arXiv:2109.08407 | **record** (plan-02; note the plan-02 lesson that these two were once confused with each other — check filenames against text) |
| 17 | DLPNO-CCSD(T) method / ORCA | Neese group — exact method + software citations | **NOT FETCHED** — debt. Pin the specific DLPNO-CCSD(T) paper(s) and the ORCA release before the M05 corpus deck is frozen |
| 18 | Boundary-edge codes (M02 atlas parsing) | Hansen et al. 1996; Caporossi & Hansen 1998, J. Chem. Inf. Comput. Sci. **38**, 610 | **record** (named in the v4.00 paper) — fetch at M02 |
| 19 | Rubric-required M03 methods citation | Huebner et al., PLOS ONE **19**(5): e0295726 (2024). DOI 10.1371/journal.pone.0295726 | **record** (plan-03, verified 2026-09-01; issue number is 5, not 1; Huebner is a coauthor) |
| 20 | Temperature-dependent PAH band shifts (tier 2 scoreboard) | Joblin-era measurements — exact papers not identified | **NOT FETCHED** — debt. Identify and pin before any tier-2 pre-registration |

## Named debts (same list as Frozen_Lines §7, kept in sync)

1. Bos 2025 full text → the actual MAE (item 7).
2. Mackie/Esposito anharmonic method papers (item 12).
3. MNRAS landing for Mai 2025 (item 5); Mulas 2018 landing re-fetch (item 6).
4. Joblin-era T-dependence references (item 20).
5. DLPNO/ORCA method citations (item 17); Sylvetsky & Martin exact identifier (item 15).
6. C₃₈₄H₄₈ per-species presence in PAHdb v4.00 (boundary-edge/formula search) — an M02 task.

**Status.** Working bibliography after the 2026-09-02 survey pass. Not a claim that plan 04 is
complete.
