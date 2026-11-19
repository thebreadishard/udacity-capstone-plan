# TASKS 262: 'hold-out' in the Udacity modules' code. The list, 19 Nov 2026

**Method.** `scan_holdout.py` (in this scratchpad) tokenises every `.py` file and every notebook code cell in `modules/02`–`08`
(it skips `__pycache__` and `out/`). It matches `hold-out`, `holdout`, `held out`, `held_out` and `heldout`, case-insensitive, and
sorts each hit by token kind: NAME = identifier, COMMENT, a string that opens a statement = docstring, a string on a `print`,
`help=`, `raise`, label or title line = reader-visible. It also reads notebook markdown and stored outputs. The raw hits are in
`holdout_hits.txt` (553 lines, same folder). I sorted the string hits by hand into "means test set (a)/(b)" and "means
something else". The scanner's automatic `record_key` and `string_other` classes were wrong in places, so the counts below are
the corrected ones. **[SUB]** = a file the module's `SUBMISSION.txt` puts on the repository's `main`. Other files (builders, the
`m05/` research code) are only in the repository's history and dev branch.

**Submitted or frozen.** Only module 05 is stated as submitted and append-only (TASKS 262 itself; its notebook carries
append-only executions, PROVENANCE notes of 24 Sep to 3 Nov). Modules 02–07 have a `SUBMISSION.txt` (18 Oct). Their READMEs'
"Submitted as the repository …" sections name the planned GitHub repositories, but nothing I grepped says Udacity has received
them. Module 06 is waiting on its seed-2 reproduction: the runspec `m06_seed2_repro` ended 14 Nov with exit 0, but the board's
Waiting line still lists it as open, so check that. Module 07 is waiting on the Vocareum key. Module 08 has no
`SUBMISSION.txt` yet (TASKS 223).

## Per module

| module | means test set (a)/(b) | reader-visible | identifiers | record keys (keep) | verdict |
|---|---|---|---|---|---|
| 02 opponent atlas | — | 0 | 0 | 0 | nothing to do |
| 03 lab scoreboard | — | 0 | 0 | 0 | nothing to do |
| 04 calibrated harmonic | **no**: "held out" = leave-one-molecule-out CV predictions | 12 in [SUB] notebook (1 markdown, 1 comment, 7 print/figure labels, 3 stored outputs); 13 in the builders `make_notebook.py`, `make_summary.py` | 0 | 0 | **out of scope**: "test set" would be wrong here; leave as is |
| 05 support predictor (submitted, append-only) | yes, mostly: hold-outs (a), (b), (c), (s) | [SUB] notebook: 41 markdown lines; 4 `print` f-strings (cells 26, 48, 57, 63); 3 table column headers `"hold-out"` (cells 54, 63, 66); 3 legend labels (cell 26); 1 comment (cell 84); 14 stored-output lines | [SUB]: 0 (the `holdout_a`/`holdout_b` in cells 48/51 are record keys) | [SUB]: `SZ['holdout_a']`, `SZ['holdout_b']` (read), `dict(holdout_a=…, holdout_b=…)` into `results.json` (cell 51) | **frozen**: any notebook change means re-executing stored outputs. See decision (1) |
| 05, dev code `m05/*.py` (not on `main`) | mixed | 58 docstrings, ~37 printed or `help=` texts, 15 comments, ~70 other message strings (34 of them in `notebook/make_notebook.py`, the builder's copy of the notebook prose) | 16 names: `SMOKE_HOLDOUT`, `holdout_twins`, `holdout_twins_dropped`, `_holdout_arguments`, `holdout_c`, `holdout_c_ids`, `HOLDOUT_C_FILE`, `HOLDOUT_R4_FILE`, `holdout_r4_ids`, `holdout_numbers`, `holdout` | ~28: `holdout_twins` (setting, written to records), `holdout_*` JSON keys | **do not touch**: `rungC_train.py`/`rungC_config.py` are the live trainer (the v1.4 search runs them now), and `--holdout-twins` is a CLI flag stored in run records. Some hits mean validation (`--inner-val`, `--val-fraction`) or CV anchor folds (`rungC_cc_transfer.py --held`), not test sets |
| 06 generative candidates | yes: its held-out **test** split of PubChem molecules | [SUB] notebook: 2 markdown lines (cells 13, 20); 1 plot label `"held-out test"` (cell 15); 1 summary f-string (cell 26) and its stored output; builders: 4 strings in `make_notebook.py`, 4 in `make_summary.py` (report PDF) | 0 (`m06/*.py` has no hits) | 0 | small and open: 4 notebook texts + 8 builder strings; it already says "test" in two of them. Do it in the same execution as seed 2's appended reproduction |
| 07 agentic workflows | — | 1 stored output: a rule-table row quoting the 25 Sep incident "hold-out (a) 'flat'" | 0 | 0 | keep: it quotes a record |
| 08 industry synthesis (no SUBMISSION yet; the snapshot will ship `m08/`) | yes: test sets (a), (b) | 29 docstrings (`accuracy.py` 10, `seen.py` 6, `live_certificate.py` 3, `demo_page.py`, `licence.py`, `show.py`, `spectrum.py` 2 each, `pipeline.py` 1, `tests/test_m08.py` 1); 2 comments; 4 `raise ValueError` messages (`accuracy.py` 121, 148, 214, 235); certificate and page strings ~30 (`accuracy.py` HOLDOUTS/CLEAN_A descriptions, `seen.py` TEXT sentences, `licence.py` caveats, `live_certificate.py`, `demo_page.py` table headers, `certify.py` table header, `make_summary.py` 2); no CLI help | 5 names: `HOLDOUTS` (accuracy, licence, seen, tests), `holdouts` (local, accuracy and tests), `holdout`, `holdout_ids` (seen), `holdout_twins_setting()` (accuracy) | `"holdouts"` (accuracy record and certificate JSON, ~12 reads), `"holdout_twins"`, the role values `"trained_and_held_out"`, `"stereoisomer_held_out"`, the folder `holdout_a_apt_2026-11-01` | the certificate strings are already TASKS 146's rebuild. 262's part here is the docstrings, error messages and the 5 identifiers |

**Totals (reader-visible / identifiers / record keys), in code a reviewer can open on `main`:** 04: 12/0/0 (out of scope),
05: ~52 plus 14 outputs/0/3 (frozen), 06: 4/0/0, 07: 1/0/0 (keep), 08: ~65/5 names (48 uses)/~17 (after the snapshot).
Dev-only `m05/`: ~180/16 names/~28 (do not touch).

## Decisions and conflicts for the user

1. **Module 05's notebook prose.** Row 262 says "module 05's notebook prose belongs here", but the notebook is submitted and
   append-only. There are two options. (a) Leave it, and add one dated append-only markdown cell: "the hold-outs (a), (b) of
   this notebook are the test sets of the lessons". (b) Change nothing. Rewriting 41 lines would break append-only.
2. **Module 08's identifiers conflict between two rows.** TASKS 146 (from closed 261) says "code identifiers keep 'hold-out'".
   TASKS 262 says variables and arguments a reviewer reads become test set. One of the two rows has to change. If 262 wins,
   the rename is 5 names, done in `m08/` on a branch with the certificate pin (`tests/data/m08_certificates_pin.json`) as the
   unchanged-output test. `tests/test_m08.py:141` asserts the licence caveat text `on hold-out ({h}) rests on`, so it moves
   with `licence.py`. m08 is also the product's pipeline, so the rename is not free.
3. **Record keys stay** everywhere (`holdouts`, `holdout_a`, `holdout_twins`, role values, folder names), as the row says.
4. **Module 04 stays as it is**: its "held out" is cross-validation, not a test set.
