# Module 02 — provenance and status (project notes; not part of the Udacity submission text)

**Required sentence.** This table is parsed from the public NASA Ames PAHdb v4.00 computed library
(DOI 10.3847/1538-4365/ae1c38). It is computed science data, not AI-generated, and it is the
*opponent* of this project's pipeline, not its training data.

## Sources and how they were obtained (read 2026-09-10 from the PAHdb site)

| library | file | size | obtained how |
|---|---|---|---|
| Theoretical (computed) **v4.00**, 2024-06-27, 10,749 species — line A | XML | 46.65 MB gzip (503 MB unpacked) | PAHdb download form |
| Anharmonic **v1.00**, 2026-07-01, 45 species — line B | XML | 878 kB | PAHdb download form |
| Experimental **v3.10**, 84 species (matrix; Module 03's) | XML | 3.88 MB | PAHdb download form |
| Line C — Mai et al. 2025 MLMD spectra, 1,704 species at 50/300/600 K | `Supplementary.zip` on Zenodo, DOI 10.5281/zenodo.14998197 (version 10.5281/zenodo.15771437) | 102 MB | direct download 2026-09-10 with the user's permission; data CC BY-NC-SA 4.0, code Apache-2.0 |
| Cheap line — Bos et al. 2025 ML-scaled spectra and pickled SVR models | ACS Omega Supporting Information, seven files, 20.5 MB unpacked | 8.9 MB zip | Europe PMC's public copy (`…/rest/PMC12750190/supplementaryFiles`), placed in `data/` on the user's instruction 2026-09-10, sha256 `3443b354f5a1285e…`; unpacked in `data/bos2025_si/` |

The PAHdb form (`…/pahdb/theoretical/4.00/download/view`) asks for an e-mail address ("to track the
users of the data"), name and company on first use, and agreement to cite Boersma+ 2014,
Bauschlicher+ 2018, Mattioda+ 2020 and Ricca+ 2026 plus the per-species references; a link is then
e-mailed. **The student fills that form; no tool enters personal data into a form.** Downloaded files
go into `data/` (git-ignored); every output records the file's sha256 and the XML root attributes, so
the version is pinned by hash, not by the file name.

## Status

- 2026-09-10: parser written and tested on a synthetic fixture; all three PAHdb libraries parsed
  (files obtained by the student through the form); Mai 2025 archive fetched; line C (1,705 species,
  positions only) and the cheap line (81 species, 6,591 bands) read in; notebook and report written.
  Findings in [Research_Note_2026-09-10_Opponent_Atlas.md](../../GoalGathering/notes/Research_Note_2026-09-10_Opponent_Atlas.md):
  benzene absent from the theoretical library; scale factors as stored 0.9794 / 0.9691 / 0.9597 (the
  v3.00 factors of Bauschlicher 2018; the v4.00 paper's refit is not in the file — decision 30: line A
  is the library as served); 4-31G from n_C = 212; C₃₈₄H₄₈ present (uid 617, 4447); line B covers
  benzene, naphthalene, pyrene, tetracene.
- 2026-09-11: deliverables reshaped to the Udacity rubric (Rubrics/02): `notebook/data_workflow.ipynb`
  (Setup / Ingestion / Cleaning with two documented functions / EDA function / five figures / Summary),
  `README.md` in the rubric's short form, `requirements.txt` by `pip freeze`, `module_summary.docx/.pdf`
  in the Udacity APA 7 template (Rubrics/APA7_template.docx) with the required Danchev (2022) citation.
- Owed: the student's own pass before submission (due 25 September 2026); the symmetry-unique
  local-environment count for C₃₈₄H₄₈ (R6 input).

## Files

- `build_opponent_atlas.py` — the parser (streaming `iterparse`; schema from the AmesPAHdbPythonSuite
  parser and its cut-down test file). Outputs per library into `out/<database>_<version>/`:
  `species.csv`, `bands.csv.gz`, `c384_class.csv`, `SUMMARY.md`. Synthetic fixture `data/_synthetic_test.xml`.
- `build_line_c_table.py` — line C: peak lists from the Mai 2025 spectra (three temperatures + EXP set).
- `build_cheap_line_table.py` — the cheap line: the Bos 2025 SI table joined to PAHdb uids.
- `notebook/make_notebook.py` — writes and executes `data_workflow.ipynb` (figures in `notebook/figures/`);
  `notebook/species_pahdb_theoretical_4.00.csv` is the tabular dataset the notebook loads (a copy of
  `out/theoretical_4.00/species.csv`).
- `make_summary.py` — fills the APA 7 template into `module_summary.docx` and converts it to PDF.
- `REPORT.md` — the long-form project report (superset of the summary; the plan's record).

## Schema notes that matter for the comparison

- `<frequency scale="…">` stores the **scaled** value; the atlas keeps both the stored value and
  `frequency / scale`.
- The route comment (`#becke3lyp/4-31G …`) is the only place the basis is written; 32 species do not
  name one (`chkbas`).
- Intensities are in km/mol (PAHdb convention), the same unit as the laboratory scoreboard's.
- The anharmonic library's `<mode>` elements are VPT2 transitions (overtones and combinations
  included), without symmetry labels; the line profile is not in the file.
