# Reproducing the numbers of the 25 September 2026 package

*Written 25 September 2026, evening (weekend plan, lever 3: "the asset's infrastructure"). One line per number that the reading copy, the cover note,
the two-horizon note and the Uitleg quote; each line gives the command that regenerates it from the committed inputs and the file it writes. Desk
commands run in seconds to minutes on a laptop; the machine runs that produced the raw inputs are named but not repeated (their logs are committed).
Paths are relative to `plans/05_delta-probed-ir-pipeline/`. Python: the system interpreter (3.14; torch 2.14 CPU, rdkit) for modules 05 and 06, the repository `.venv` (3.13; LangGraph) for module 07;
the WSL `qc05` or a rented machine's `m05` environment for anything that imports psi4/pyscf with the corpus.*

## Learning curves and their controls (module 05)

| number | command | writes |
|---|---|---|
| E7 rung B, fixed recipe: ratio 0.47 → 0.45 → 0.43 (a), 0.51 → 0.50 → 0.47 (b); corrected ω 5.9 → 4.7 / 6.0 → 5.1 cm⁻¹ | `python m05/e7_rungB_pairs.py corpus/molecules out/E7_rungB_2026-09-23_analytic --use-analytic --sizes 45,100,all` (in `modules/05_support_predictor/`) | `out/E7_rungB_2026-09-23_analytic.{json,md,log}` |
| tuned curve, stage 1: 0.43 / 0.45 / 0.41 (a), 0.47 / 0.54 / 0.44 (b); slope 1.06× | same with `--tune`, out prefix `out/E7_rungB_tuned_2026-09-25` | `out/E7_rungB_tuned_2026-09-25.{json,md}` |
| tuned curve, stage 2 (loss × optimiser): 100-point 0.42 / 0.52; 175 unchanged | same with `--tune --tune-stage2`, out prefix `out/E7_rungB_tuned2_2026-09-25` | `out/E7_rungB_tuned2_2026-09-25.{json,md}` |
| tuned curve, stage 3 (read-out-aligned loss) | `--tune-stage3 out/E7_rungB_tuned2_2026-09-25.json`, out prefix `out/E7_rungB_tuned3_2026-09-25` | `out/E7_rungB_tuned3_2026-09-25.{json,md}` |
| size extrapolation: 0.66 → 0.62 → 0.59 on > 26 atoms | `python m05/e7_rungB_pairs.py corpus/molecules out/E7_rungB_size26_2026-09-25 --use-analytic --split size:26` | `out/E7_rungB_size26_2026-09-25.{json,md}` |
| E11.1 shuffled labels: 1.12 / 1.09; frequency floor 13.6 / 12.4 | `… out/E11_shuffled_2026-09-25 --use-analytic --shuffle-labels --sizes all` | `out/E11_shuffled_2026-09-25.{json,md}` |
| E11.2 symmetry: coarse 0.52 (model) vs 0.575 (target); orbits 0.066 vs 0.103 | `… out/E11_orbit_dump_2026-09-25 --use-analytic --dump --sizes all --seeds 0` and `python probes/route… ` — target-only files: `out/E11_target_symmetry_2026-09-25.json` (scratch script of 25 Sep 09:3x, coarse key) and `out/E11_target_orbit_symmetry_2026-09-25.json` (orbit key; `e11_extras.orbit_groups`) | `out/E11_orbit_dump_2026-09-25_dump.{json,md}` (+ `_pairs.npz`, local) |
| E11.4 noise floor: median K spread 2.09, plateau bound 6.3 | `python m05/e11_noise_floor.py corpus/molecules out/E11_noise_floor_2026-09-25` | `out/E11_noise_floor_2026-09-25.{json,md}` |
| E11.5 power-law predictions: 1.14× / 1.15× / 1.22× per decade; 0.39 at 1,200 | `python m05/e11_power_law.py out/E7_rungB_2026-09-23_analytic.json out/E7_rungB_size26_2026-09-25.json out/E11_power_law_2026-09-25b_analytic` (the rung-B and size-split JSONs are its inputs) | `out/E11_power_law_2026-09-25b_analytic.{json,md}` |
| E11.8 orbit-averaged labels: −1.6 % (fail) | `… out/E11_orbit_avg_2026-09-25 --use-analytic --orbit-average-targets --dump --sizes 45,100,all` | `out/E11_orbit_avg_2026-09-25.{json,md}` |
| E9 core transfer: 1.72 cm⁻¹ at r = 2, 25 % of columns | `python m05/e9_core_transfer.py` (+ `e9_posthoc_block.py`) | `data/e9/e9_core_transfer_2026-09-24.json` |
| E10 environment once: 3.75 registered, 3.36 torsion-matched | `python m05/e10_environment_once.py --donor smallest` and `--donor nearest-torsion` | `data/e9/e10_environment_once_2026-09-24*.json` |
| module 05 notebook sections 7–10 and report addenda 1–4 | `python notebook/execute_section8.py --from-cell <n_cells>` then `python make_summary.py` | `notebook/deep_learning.ipynb`, `module_summary.{docx,pdf}` |
| layer-B interim release, 25 Sep (60 molecules of the 64 local layer-B folders; 4 skipped with an imaginary mode, as `e7_rungB_pairs.py` skips them) | `python m05/build_release.py corpus/molecules data/corpus_release/layerB_interim_2026-09-25 --layer B --prefer-analytic` (in `modules/05_support_predictor/`; the archive stays out of git) | `data/corpus_release/layerB_interim_2026-09-25_manifest.json` |
| corpus release index (one row per manifest: molecules per layer, deck hashes, skips, archive SHA-256, git status) | `python m05/release_index.py` (`--check` exits 1 when the index is stale) | `data/corpus_release/RELEASES.md` |

## Route 2 (naphthalene at Mackie's level) and the laboratory comparison

| number | command | writes |
|---|---|---|
| two-route disagreement median 0.0 / p90 0.2 / max 3.6 cm⁻¹; VPT2 fundamentals | `PYTHONPATH=src python -m dpir.qff probes/results_m1/route2/naph_hessians_d010 --disp 0.10 --out probes/results_m1/route2/qff_naphthalene_d010` | `probes/results_m1/route2/qff_naphthalene_d010{,.npz}` |
| noise structure (Spearman, per-band spread) | `python probes/route_noise_structure.py probes/results_m1/route2/qff_naphthalene_d010.npz` | stdout (quoted in the ledger, 25 Sep 17:1x) |
| ν48 −0.7, ν47 +1.9, ν46 +0.2; RMS 1.2 cm⁻¹ | `PYTHONPATH=src python probes/route2_vs_lab.py probes/results_m1/route2/qff_naphthalene_d010.npz modules/03_lab_scoreboard/out/origin_columns_naphthalene.csv modules/03_lab_scoreboard/out/naphthalene_dft_modes.md probes/results_m1/route2/ROUTE2_NAPHTHALENE_VS_LAB_2026-09-25.md` | `probes/results_m1/route2/ROUTE2_NAPHTHALENE_VS_LAB_2026-09-25.md` |
| the 97 Hessians themselves (46 min each, hel1-14) | `probes/route2_naphthalene.sh` (pyscf B97-1 / CADPAC-TZ2P analytic Hessians; log committed) | `probes/results_m1/route2/naph_hessians_d010/*.json` |

## The anchor, E8 and the cations (machine runs; read-out scripts)

| number | command | writes |
|---|---|---|
| anchor family readings (mode 12 lose, 22 win, 31 between) | `python probes/m3_family_reading.py 31 -6.0` on `probes/results_m1/naphthalene_cc-pvtz_tight_m3/` | `probes/results_m1/M3_TZ_MODE31_READING_2026-09-24.md` |
| E8 benzene locality one bond further | `probes/e8_*` read-outs on `probes/results_m1/e8_benzene_ccpvdz/` | `E8_locality_benzene*` (see the E8 pre-registration's outcome section) |
| cation rows (benzene⁺ 683 s, naphthalene⁺ 2,443 s) and prices (benzene⁺ reference 3,564 s) | `corpus/cation_rows.py` with `decks/deck_v1_cation.json`; `probes/l3_ulno_price.py rows/<m> price/<m> --threads 16 --max-memory 24000` (hel1-14); read-out: `python probes/cation_price_readout.py probes/results_m1/cations/benzene/l3_price.json` | `/root/cations/rows/*`, `probes/results_m1/cations/*/l3_price.json` (fetched; benzene⁺ complete 25 Sep 20:55 UTC) |

## Modules 06 and 07

| number | command | writes |
|---|---|---|
| module 06 baseline: validity 0.030, uniqueness 0.855, novelty 0.996 | `python m06/baseline_ngram.py data/pubchem_aromatics_2026-09-24.csv out/baseline_ngram_2026-09-25.json` | `out/baseline_ngram_2026-09-25.json` |
| module 06 quick check / full run | `M06_QUICK=1 python notebook/make_notebook.py` (check) or `M06_REUSE=1 python notebook/make_notebook.py` (full, weights from `m06/train.py` runs) | `notebook/generative_model.ipynb`, `notebook/results.json` |
| module 07: 8/8 scenarios, 11 tests | `.venv/Scripts/python -m pytest modules/07_agentic_workflows/tests -q`; `python run_scenarios.py --policy rules`; `python notebook/make_notebook.py`; `python make_summary.py` | `out/scenario_results_*.json`, `notebook/agentic_system.ipynb`, `Agentic_AI_System_Design_Report.{docx,pdf}` |

## Audits

| check | command |
|---|---|
| every number of the reading copy traces to a source | `python probes/check_reading_copy_numbers.py GoalGathering/Project_Proposal_2026-09-26_Reading_Copy.md README.md QUALITY_POLICY.md GoalGathering/*.md GoalGathering/notes/*.md modules/05_support_predictor/out/*.md modules/05_support_predictor/*.md probes/results_m1/*.md probes/results_m1/*/REPORT.md` (25 Sep: 488 tokens, 1 benign miss) |
| the state of the machines | `bash probes/state.sh` |

## Rebuild and diff

`python tools/rebuild_check.py` audits this file: every output named above must exist, be tracked by git and be clean (25 Sep 22:5x: two open items,
the cation folder and the module 06 results, both awaiting their runs). `python tools/rebuild_check.py --run <text>` re-runs the desk rows whose first
column contains the text (`all` for every desk row; machine rows are skipped) with the matching interpreter (module 07 rows in the repository `.venv`, the rest in the interpreter running the script), compares each output with HEAD (JSON numbers to
1 %, text byte-for-byte, time stamps and run times ignored) and restores equivalent rebuilds so the working copy stays clean. First use, 25 Sep 22:5x: the
E11.5 row rebuilt to the same numbers. The machine runs are reproduced only from their committed logs and raw inputs.
