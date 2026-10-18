# Module 08 standalone: the frozen-snapshot plan (18 Oct 2026)

**Decision (18 Oct 2026, 21:4x; the user: 'Ja, leg het zo vast en schuif het naar de schrijffase').** Module 08 is the integration module:
it reads the project's current state from other modules' folders, the website export and the plan's evidence files. A submitted module must
run on its own, without those folders (option 1, 18 Oct). Modules 02–07 were made standalone today. Module 08 waits until the writing phase (Dec 2026 –
Feb 2027), **after** its content is rewritten under decision 63. That rewrite changes the inputs. The licence comes from chain 34 and the
two-DFT proof, not from the rung B reading of 27 Sep. The certificates and counts are from 28 Sep, and the live server worker is no longer
promised. A snapshot built now would have to be built again. This note fixes the design so the build is mechanical. TASKS 78.

## What module 08 reads from outside its folder (inventory of 18 Oct)

| # | Source | Read by | Standalone form |
|---|---|---|---|
| 1 | `website/export/out`: `catalog.json`, `summary.json`, `molecules/<id>.json` | `m08/catalog.py`, `certify.py` | `snapshot/`: catalogue and summary whole; **only** the molecule records the scenarios open, not the whole folder |
| 2 | module 03: `notebook/bands_lab.csv`, `out/u_band_by_record_family.csv`; the family rule cited from `build_lab_tables.py` | `catalog.py` | the two CSVs copied; the rule stays cited by source, checked at the build |
| 3 | module 05: `corpus/manifest.csv` | `candidates.py` (is a candidate new?) | copied |
| 4 | module 05: the licence reading (`out/E7_rungB_layerB_2026-09-27.md`, the rule from the layer B pre-registration) | `licence.py` | **rewritten first** (decision 63), then the files the new licence reads are copied |
| 5 | module 05: chain 34 evaluations (`E7_rungC_chain34_eval_matched_2026-10-09_seed{0,1,2}.json`), T3 intensities (`T3_tz_intensity_matched_c34_seed{0,1,2}_2026-10-09.json`), and the Hessian and APT files they point to | `spectrum.py` | copied: the records and every file opened through them |
| 6 | module 06: the model code and seed 0's weights (not in git) | `candidates.py` (scenario S3) | no weights. S3 reads a recorded candidate, drawn from module 06's committed samples `notebook/out/samples_seed0_T1.0.txt`. Generating a new one stays a plan-repository option |
| 7 | module 07: the `steward` package (`gate`, `rules`, `schema`, `tools`, the rule tables) | `officer.py` (via `sys.path`) | a copied package `steward/` with its source commit recorded; no `sys.path` edit |
| 8 | the plan's `src/dpir/provenance.py` | `run_scenarios.py` | copied with whatever it imports, or the provenance call made by module 08's own code; decided at the build |
| 9 | evidence files: the layer B pre-registration (`GoalGathering/notes/`), `probes/results_m1/…` (E8 locality, the price sources) | `certify.py`, `prices.py` (existence checks, sources) | copied to `snapshot/evidence/` under their plan-relative paths |
| 10 | S5 (`website/export/build_catalog.py`) and S6 (the built site + axe) | `run_scenarios.py --with-catalog` | not runnable standalone. The results say "plan repository only", as S6 already says "not run in this build" |
| 11 | `make_summary.py` (the Rubrics APA 7 template) | the paper's build | stays in the plan repository, as for modules 02–07 |

## Mechanism

- **One root resolver** (`m08/paths.py`): every read goes through `resolve(plan_relative_path)`. Inside the plan repository it reads the
  live file. In the submitted repository it reads `snapshot/<same path>`. A mixture is refused: a path missing from the snapshot raises with
  its name, and nothing falls back to anywhere else.
- **`m08/make_snapshot.py`** (run in the plan repository): runs the scenarios with a recording resolver, copies exactly the files opened
  into `snapshot/`, and writes `snapshot/MANIFEST.json` (path, bytes, sha256, the plan commit, the date). Its size is checked before the commit.
- **Test:** the scenarios run in snapshot mode give the same `results.json` as in plan mode, except the provenance fields.
  `SUBMISSION.txt` lists `snapshot/`, `steward/` and the deliverables. Its `run:` line runs the notebook.

## Order in the writing phase

1. Rewrite the content under decision 63: licence, certificates, counts, and no live worker. The notebook and the paper follow.
2. Root resolver, `make_snapshot.py`, the snapshot-mode test (regression test first, CLAUDE.md "Python code").
3. Build the snapshot; `SUBMISSION.txt`; README sections Files and Repository (`udacity-industry-ai-synthesis`, REVIEW item 6).
4. The dry run with `tools/make_module_repo.sh` in a fresh clone (`-` for no development branch, as for modules 06 and 07).
