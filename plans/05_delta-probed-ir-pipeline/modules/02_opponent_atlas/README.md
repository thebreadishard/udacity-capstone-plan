# Module 02 — the opponent atlas

**Required sentence.** This table is parsed from the public NASA Ames PAHdb v4.00 computed library
(DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the
*opponent* of this project's pipeline, not its training data.

**What this module delivers** (Capstone_Mapping, Module 02; Uitleg ch. 7): one tidy band table from
the PAHdb computed library — uid, formula, charge, size, band position, intensity, scale factor,
basis — with an exploratory analysis (coverage by size, charge and family; where the 4-31G regime
starts; which ladder rungs have entries; which C₃₈₄H₄₈-class species exist = frozen-lines debt 6),
figures, and a short report. No training.

## Sources and how they are obtained (read 2026-09-10 from the PAHdb site)

| library | file | size | obtained how |
|---|---|---|---|
| Theoretical (computed) **v4.00**, 2024-06-27, 10,749 species — line A | XML | 46.65 MB | PAHdb download form |
| Anharmonic **v1.00**, 2026-07-01, 45 species — line B | XML | 878 kB | PAHdb download form |
| Experimental **v3.10**, 84 species (matrix; Module 03's) | XML | 3.88 MB | PAHdb download form |
| Line C — Mai et al. 2025 MLMD spectra, 1,704 species at 50/300/600 K | `Supplementary.zip` on Zenodo, DOI 10.5281/zenodo.14998197 (version 10.5281/zenodo.15771437) | 102 MB | direct download; data CC BY-NC-SA 4.0, code Apache-2.0 |
| Cheap line — Bos et al. 2025 ML-scaled spectra and pickled SVR models | ACS Omega Supporting Information, seven files (two xlsx, three zips, a 13.5 MB txt of geometries, a PDF), 20.5 MB unpacked | 8.9 MB zip | Europe PMC's public copy (`…/rest/PMC12750190/supplementaryFiles`), placed in `data/` on the user's instruction 2026-09-10, sha256 `3443b354f5a1285e…`; unpacked in `data/bos2025_si/` |

The PAHdb form (`…/pahdb/theoretical/4.00/download/view`) asks for an e-mail address ("to track the
users of the data"), name and company on first use, and agreement to cite Boersma+ 2014,
Bauschlicher+ 2018, Mattioda+ 2020 and Ricca+ 2026 plus the per-species references; a link is then
e-mailed. **The user fills that form; this repository never enters personal data into a form.**
Downloaded files go into `data/` (git-ignored); every output records the file's sha256 and the XML
root attributes, so the version is pinned by hash, not by the file name.

## Status 2026-09-10

All three PAHdb libraries parsed (files obtained by the user through the form the same evening);
the Mai 2025 Zenodo archive fetched with permission. First findings in
[Research_Note_2026-09-10_Opponent_Atlas.md](../../GoalGathering/Research_Note_2026-09-10_Opponent_Atlas.md):
benzene absent from the theoretical library; scale factors as stored 0.9794 / 0.9691 / 0.9597;
4-31G from n_C = 212; C₃₈₄H₄₈ present (uid 617, 4447); line B covers benzene, naphthalene, pyrene,
tetracene. Owed: line C's table from the Mai spectra zips, the Bos SI, the EDA notebook with
figures, the report.

## Files

- `build_opponent_atlas.py` — the parser (streaming `iterparse`, schema from the AmesPAHdbPythonSuite
  parser and its cut-down test file, read 2026-09-10). Outputs per library into `out/<database>_<version>/`:
  `species.csv`, `bands.csv.gz`, `c384_class.csv`, `SUMMARY.md`. Tested on a two-species synthetic file
  built from the schema (`data/_synthetic_test.xml`, kept as the parser's fixture) until the real files
  arrive.
- `notebook/` — the EDA notebook and figures (to be written once the real files are parsed).
- `REPORT.md` — the module report (to be written).

## Schema notes that matter for the comparison

- `<frequency scale="…">` stores the **scaled** value; the atlas keeps both the stored value and
  `frequency / scale`. Whether the stored value is scaled or unscaled is verified on the real file
  against the v4.00 paper's three factors (0.964 / 0.979 / 0.975) before any use — the synthetic
  test cannot decide that.
- The route comment (`#becke3lyp/4-31G …`) is the only place the basis is written; the atlas parses
  it and prints the species whose comment does not name a basis.
- Intensities are in km/mol (PAHdb convention); the scoreboard's laboratory intensities are in the
  same unit (Module 03), so the intensity comparison of decision 18 needs no conversion.
- The anharmonic library's `<mode>` elements are stick positions after VPT2; the line profile is not
  in the file (Frozen_Lines §3).
