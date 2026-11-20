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

## Corrections to the inventory, 20 November 2026 08:18

The table above is the inventory of 18 October and stays. The licence was rewritten in between (decision 65, v1.4), so four of its rows
no longer describe what the code reads. Read from the code on 20 November 2026:

| # | Was | Is |
|---|---|---|
| 4 | module 05: the licence reading `out/E7_rungB_layerB_2026-09-27.md` and the layer-B rule | `licence.py` → `accuracy.carried_accuracy()` reads module 05's `out/MODELS_STATUS.json`, then for the carried measurement networks the six evaluation records `out/v14/E7_rungC_v14s3clean_c00_control_eval_clean_seed{0,1,2}.json` and `…_a8read_seed{0,1,2}.json`, the product-error record `…_product_error.json` and the training record `…c00_control.json`. `product_error_record` also hashes the three `.pt` checkpoints where they are present (`accuracy.py`, `P.sha16`), which the recorder would copy |
| 5 | module 05: chain 34 evaluations and T3 intensities, read by `spectrum.py` | no longer read by the scenarios or the notebook. `spectrum.shape` reads `corpus/molecules/<id>/` (geometry, the B3LYP Hessian, the APT file); `spectrum.test_prediction` still reads chain 34's `out/T3_tz_folds_c34_seed*_fold_<mid>.npz`, and only `website/export/build_catalog.py` calls it |
| 7 | module 07: the `steward` package and "the rule tables" | the package and `rules/rules_v2.json` (41 rules), the default table `officer.py` loads |
| 9 | evidence files: the layer B pre-registration, … | the layer-B pre-registration is no longer named on a certificate (20 Nov); `certify.py` reads module 05's `out/ANCHORS_STATUS.json` (decision 62) and the evidence paths the export names |

Two rows were missing:

| # | Source | Read by | Standalone form |
|---|---|---|---|
| 12 | **code** of module 05 (`m05/`, `corpus/`), of `probes/` and of `src/dpir`, imported through `sys.path`, not through `paths.resolve`: `model_registry`, `network_kind`, `rungC_train`, `rungC_infer`, `rungC_equivariant`, `rungC_intensities`, `rungC_settings_added`, `learning_curve_layerA`, `anchor_registry`, `run_corpus`, `apt`, `promotion_read`, `chain35_read`, `scale_factor_baseline`, `dpir.provenance` and what they import — 34 files, and torch, rdkit and scipy | `pipeline.py:73-88`, `accuracy.py:17-20`, `licence.py`, `own_spread.py`, `spectrum.py` (`_m05`), `run_scenarios.py` | **open.** In a fresh clone `import m08.certify` fails at these imports, so the notebook cannot run there. The snapshot-mode test does not see it: it runs inside the plan repository, where the code is importable. See below |
| 13 | one stored pipeline run: `probes/results_m1/pipeline_benzene_anharmonic_v3_2026-11-19/benzene/certificate.json` | `stored_run.py` (the notebook's section 3.7) | copied: `make_snapshot.py` opens it under the recorder after the scenarios |

**What row 12 needs (looked at on 20 November 2026, not done).** The certificate and the licence need three things from that code: the model
registry's reading (`model_registry.read_status`, `carried_keys`, `checkpoint_key`), the evaluation-record readers
(`promotion_read.load_eval_arm`, `reported`, `FAMILIES`, `QUANTITIES`; `chain35_read`'s two lines; `rungC_settings_added`;
`network_kind`) and `rungC_intensities.mode_intensities` for the heights. None of that trains or runs a network. But
`m05/model_registry.py` imports torch at its top, `accuracy.py` reaches it through `m08.pipeline`, which also imports the trainer and
the inference code, and `licence.py` takes five constants from `m08/own_spread.py`, which imports the pipeline. Two ways out:
(a) vendor the 34 files into the snapshot and give `pipeline.py`'s `sys.path` lines a resolver, keeping torch in `requirements.txt`;
(b) decouple: make `model_registry`'s torch import lazy (a change in `m05/`), move the registry reads, `M05`, `NETWORK` and `sha16` out
of `pipeline.py` and the own-spread constants out of `own_spread.py` into light modules, so that a catalogue certificate imports no
training code — then only the light readers need vendoring. (b) touches `m05/`, which a running search imports; it waits for that
search to end. Until one of the two is done, step 3's snapshot build gives a repository whose notebook does not run.
