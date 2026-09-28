# Codekwaliteit plan 05 — bevindingen (28 september 2026)

Scope: alle uitvoerbare code (`.py`, `.sh`, `.ps1`, `.ipynb`) in de 29 sub-folders van `plans/05_delta-probed-ir-pipeline/`, behalve `modules/02_opponent_atlas/data/mai2025/Supplementary_Data_Code/` (externe code). Er is geen code gewijzigd.

## Methode

- `ruff 0.16.8` met de projectconfiguratie uit `pyproject.toml` (regels E, F, W, I, B, UP, NPY; regellengte 160).
- Extra ruff-regels voor foutgevoelige patronen: BLE001, E722, S102/S108/S110/S602, PLW0603/PLW1510/PLW2901, PLE, C901, PLR0915, B006/B008/B904.
- Tier 2 (`src/dpir/`): ruff ANN en D1 (de policy eist type hints en docstrings).
- `compile()` op elk `.py`-bestand (Python 3.14): geen syntaxfouten.
- `bash -n` op elk `.sh`-bestand: geen syntaxfouten; plus controle op `set -e`.
- Notebooks: foutuitvoer en volgorde van `execution_count`.
- `pytest -m "not slow"`: 73 geslaagd, 3 gefaald.
- Handmatig nagelopen: alle B023-meldingen (closures in lussen) en alle hard-gecodeerde paden.

Volgens `QUALITY_POLICY.md` hoeft tier 1 (`probes/`, `modules/*/`) alleen te compileren en één keer droog te draaien. De stijlbevindingen in sectie 3 zijn daar dus informatief en worden pas verplicht bij promotie naar tier 2. `src/dpir/` en `tests/` zijn ruff-schoon met de projectconfiguratie.

**Samenvatting:** 5 hoog, 97 middel, 104 laag (inhoudelijke bevindingen per bestand en regel), plus 4053 stijlmeldingen (sectie 3) en een heuristische provenance-lijst (sectie 4).

## 1. Inhoudelijke bevindingen

| Ernst | Folder | Bestand | Regel(s) | Kwaliteitsissue | Oplossing |
|---|---|---|---|---|---|
| hoog | probes | m1_frozen_spaces.py | 532 | f-string-syntax die pas vanaf Python 3.12 bestaat, terwijl `pyproject.toml` `requires-python >=3.10` / `target-version py310` opgeeft; het script start niet op 3.10/3.11 | De geneste expressie vooraf aan een variabele toekennen (of andere aanhalingstekens/geen backslash in de `{}` gebruiken), of `requires-python` naar `>=3.12` zetten als dat de bedoeling is |
| hoog | probes | route2_vs_lab.py | 56 | f-string-syntax die pas vanaf Python 3.12 bestaat, terwijl `pyproject.toml` `requires-python >=3.10` / `target-version py310` opgeeft; het script start niet op 3.10/3.11 | De geneste expressie vooraf aan een variabele toekennen (of andere aanhalingstekens/geen backslash in de `{}` gebruiken), of `requires-python` naar `>=3.12` zetten als dat de bedoeling is |
| hoog | tests | test_design_check.py |  | Test `test_cli_runs_on_a_synthetic_directory` faalt op Windows: het aangeroepen script crasht bij `--help` met `UnicodeEncodeError` (de helptekst bevat `Δ`, stdout is een pipe met cp1252); door `subprocess.run` zonder `check` ziet de test alleen een lege stdout | In de test `env={**os.environ, "PYTHONIOENCODING": "utf-8"}` meegeven en `returncode`/`stderr` asserten, of in de CLI-scripts `sys.stdout.reconfigure(encoding="utf-8")` aanroepen |
| hoog | tests | test_rungC_aggregation.py |  | Test `test_cli_switch_is_wired_in_both_drivers` faalt op Windows: het aangeroepen script crasht bij `--help` met `UnicodeEncodeError` (de helptekst bevat `Δ`, stdout is een pipe met cp1252); door `subprocess.run` zonder `check` ziet de test alleen een lege stdout | In de test `env={**os.environ, "PYTHONIOENCODING": "utf-8"}` meegeven en `returncode`/`stderr` asserten, of in de CLI-scripts `sys.stdout.reconfigure(encoding="utf-8")` aanroepen |
| hoog | tests | test_rungC_elements.py |  | Test `test_cli_switches_are_wired` faalt op Windows: het aangeroepen script crasht bij `--help` met `UnicodeEncodeError` (de helptekst bevat `Δ`, stdout is een pipe met cp1252); door `subprocess.run` zonder `check` ziet de test alleen een lege stdout | In de test `env={**os.environ, "PYTHONIOENCODING": "utf-8"}` meegeven en `returncode`/`stderr` asserten, of in de CLI-scripts `sys.stdout.reconfigure(encoding="utf-8")` aanroepen |
| middel | modules/02_opponent_atlas | make_summary.py | 197 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/03_lab_scoreboard | build_lab_tables.py | 160 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/03_lab_scoreboard | make_summary.py | 237 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/03_lab_scoreboard | shape_score.py | 48 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/04_calibrated_harmonic | make_summary.py | 200 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/05_support_predictor/corpus | analytic_hessians.py | 52 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/corpus | build_manifest.py | 72 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/corpus | cation_rows.py | 35 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/corpus | cation_rows.py | 40 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/05_support_predictor/corpus | fd_grid_test_benzene.py | 11 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/corpus | fd_grid_test_benzene.py | 10 | psi4-uitvoerbestand hard-gecodeerd op `/root/m05run/...`; faalt op elke andere machine | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| middel | modules/05_support_predictor/corpus | psi4_worker.py | 43, 77, 81, 84 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/corpus | psi4_worker.py | 84 | `try`/`except`/`pass`: fout wordt stil ingeslikt | Minstens loggen (`logging.warning(..., exc_info=True)`) of een smallere uitzondering vangen |
| middel | modules/05_support_predictor/corpus | run_corpus.py | 75, 84, 104 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/corpus | run_corpus.py | 28, 183, 208 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/05_support_predictor/corpus | run_corpus.py | 30, 187 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/m05 | e10_environment_once.py | 68 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e11_extras.py | 18, 104, 116 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e11_power_law.py | 44 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e6_learning_curve.py | 125, 280, 281, 282 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e7_rungB_pairs.py | 274, 421 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e7_t2_ceilings.py | 64 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | e7_t2_posthoc.py | 97 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | embedding_experiments_E.py | 38, 222 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | embedding_experiments_E.py | 203 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/m05 | embedding_skipgram_E5.py | 109 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/m05 | inspect_hessian_qm9.py | 46 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | learning_curve_layerA.py | 61, 165, 167 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | learning_curve_layerA.py | 140 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/m05 | learning_curve_layerA_v2_descriptors.py | 127, 128 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | learning_curve_layerA_v2_descriptors.py | 154 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/05_support_predictor/m05 | ring_survey.py | 64 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/m05 | target_diagnostics_E4.py | 82 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/05_support_predictor/notebook | deep_learning.ipynb |  | Opgeslagen notebook heeft niet-oplopende `execution_count`: de uitvoer is niet van boven naar beneden gereproduceerd | Kernel herstarten en alle cellen in volgorde uitvoeren (bv. met `nbclient`), dan opslaan |
| middel | modules/06_generative_candidates/m06 | baseline_ngram.py | 41 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/06_generative_candidates/m06 | data.py | 27 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/06_generative_candidates/notebook | generative_model.ipynb | cell 15:3 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | modules/07_agentic_workflows | run_scenarios.py | 32 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | modules/07_agentic_workflows | run_scenarios.py | 33 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | modules/standout_pattern_proposer/notebook | pattern_proposer.ipynb | cell 10:20 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | anchor_single_point_timing.py | 64, 148, 154 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | benzene_benchmark_map.py | 53 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | canonical_gradient_timing.py | 45 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | chain_corpus_after_anchor.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | deck_counts_planar.py | 32, 37 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | dh_diagonal_baseline.py | 112 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | dryrun_dft_delta_recovery.py | 111, 237, 242, 632, 701, 773 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | dryrun_dft_delta_recovery.py | 46 | `try`/`except`/`pass`: fout wordt stil ingeslikt | Minstens loggen (`logging.warning(..., exc_info=True)`) of een smallere uitzondering vangen |
| middel | probes | dryrun_symmetry_prior.py | 129, 163 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | e8_between_extension.py | 70, 84 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | e8_cc_hessian_fd.py | 46 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | e8_cc_locality.py | 72, 144 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | e8_sparse_recovery_benzene.py | 161 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | l2_lno_price.py | 37 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | l2b_tiers_benzene.py | 31 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | l3_ulno_price.py | 38 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | l3_ulno_price.py | 112 | `except Exception` vangt alles, ook programmeerfouten | Alleen de verwachte uitzonderingen vangen (bv. `OSError`, `ValueError`, `KeyError`) en de fout loggen |
| middel | probes | launch_detached.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | m1_frozen_spaces.py | 106 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | m1_frozen_spaces.py | 468 | `try`/`except`/`pass`: fout wordt stil ingeslikt | Minstens loggen (`logging.warning(..., exc_info=True)`) of een smallere uitzondering vangen |
| middel | probes | m2a_gradient_cost_ratio.py | 89, 118 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | m2a_gradient_cost_ratio.py | 87 | `try`/`except`/`pass`: fout wordt stil ingeslikt | Minstens loggen (`logging.warning(..., exc_info=True)`) of een smallere uitzondering vangen |
| middel | probes | m2b_pyscfad_response.py | 68 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | m4_cation_timing.py | 178 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | m4_cation_timing.py | 135 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | probes | m4_cation_timing.py | 153 | `try`/`except`/`pass`: fout wordt stil ingeslikt | Minstens loggen (`logging.warning(..., exc_info=True)`) of een smallere uitzondering vangen |
| middel | probes | naph_level_smoke.py | 16 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | pyscf_hessians_for_qff.py | 45 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | qff_from_hessians.py | 241 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | r0_convention_check.py | 27, 29 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | r0_geometry_check.py | 26, 31 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | r0_geometry_check_oop.py | 25 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | route2_naphthalene.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | route2_optimise.py | 31 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | route2_vs_lab.py | 54 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | run_after_lanes_ccx53.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | run_cations_after_route2.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | run_e8_ccx53.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | run_e8_handover.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | run_e8_naph_extras.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | run_e8_naph_parallel.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | probes | symmetrise_geometry.py | 32, 90 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | probes | vpt2_benzene.py | 61, 138 | `zip()` zonder `strict=`: bij ongelijke lengtes wordt stil afgekapt (in numerieke code een verborgen fout) | `zip(..., strict=True)` gebruiken (Python >=3.10) |
| middel | src/dpir | provenance.py | 19, 22 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | src/dpir | provenance.py | 28 | Tier 2: publieke functie zonder docstring | Docstring toevoegen |
| middel | src/dpir | qff.py | 60 | Tier 2: publieke klasse zonder docstring (policy eist docstrings) | Docstring toevoegen |
| middel | src/dpir | qff.py | 67 | Tier 2: publieke methode zonder docstring | Docstring toevoegen |
| middel | src/dpir | qff.py | 119, 485 | Tier 2: publieke functie zonder docstring | Docstring toevoegen |
| middel | src/dpir | qff.py | 372, 416, 485 | Tier 2: ontbrekend return-type (policy eist type hints) | Return-type toevoegen |
| middel | src/dpir | qff.py | 416, 485 | Tier 2: ontbrekende type-annotatie voor argument (policy eist type hints) | Type hints toevoegen |
| middel | tests | test_design_check.py | 82, 86 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | tests | test_rungC_aggregation.py | 76 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | tests | test_rungC_elements.py | 61, 63 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | tools | backup_data.py | 73 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | tools | modules_fresh_check.sh |  | Bash-script zonder `set -e`/`set -euo pipefail`: een mislukte stap laat de keten doorlopen | `set -euo pipefail` bovenaan zetten (en waar een fout bewust getolereerd wordt `\|\| true` gebruiken) |
| middel | tools | rebuild_check.py | 124, 155 | `subprocess.run` zonder `check=`: een mislukt subproces wordt stil genegeerd (in `tests/` verbergt dit de oorzaak van de drie falende tests) | `check=True` meegeven, of `returncode` expliciet controleren en `stderr` in de foutmelding opnemen |
| middel | tools | rebuild_check.py | 155 | `subprocess.run(..., shell=True)` met commando's uit een document: alles wat in dat document staat wordt als shell-commando uitgevoerd | Commando's met `shlex.split` naar een lijst omzetten en zonder `shell=True` draaien, of de bron van de commando's expliciet als vertrouwd documenteren |
| laag | modules/02_opponent_atlas | build_cheap_line_table.py | 15, 16 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/02_opponent_atlas | c384_environments.py | 42 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/02_opponent_atlas | make_summary.py | 7 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/02_opponent_atlas/notebook | data_workflow.ipynb | cell 3:1 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/03_lab_scoreboard | build_lab_tables.py | 26 | Import niet bovenaan module/cel | Imports naar boven verplaatsen; bij bewuste `sys.path`-manipulatie `# noqa: E402` toevoegen |
| laag | modules/03_lab_scoreboard | build_lab_tables.py | 206, 262, 277, 290 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/03_lab_scoreboard | build_lab_tables.py | 209 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | modules/03_lab_scoreboard | dft_mode_families.py | 52 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/03_lab_scoreboard | shape_score.py | 18 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/04_calibrated_harmonic/notebook | modeling.ipynb | cell 9:8 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/corpus | analytic_hessians.py | 14 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/corpus | build_manifest.py | 8 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/corpus | fd_grid_test_benzene.py | 5 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/corpus | read_imaginary_second_route.py | 78 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | modules/05_support_predictor/corpus | run_corpus.py | 77 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/corpus | run_corpus.py | 15 | Default `QC_PYTHON` is een persoonlijk Windows-pad (wel overschrijfbaar via `CORPUS_QC_PYTHON`) | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | modules/05_support_predictor/corpus | saddle_restarts.py | 15 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/corpus | saddle_restarts.py | 49 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/05_support_predictor/m05 | build_release.py | 90 | `global` wordt gebruikt om moduleconstanten vanuit `main()` te wijzigen | Waarden als parameter of via een config-object doorgeven |
| laag | modules/05_support_predictor/m05 | e11_extras.py | 85 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | modules/05_support_predictor/m05 | e6_learning_curve.py | 256, 257, 258, 259 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | modules/05_support_predictor/m05 | e7_rungB_pairs.py | 50 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | modules/05_support_predictor/m05 | e7_rungB_reread_analytic.py | 59 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/m05 | e7_t2_posthoc.py | 25 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/m05 | e7_t2_sqm.py | 101 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/m05 | e7_t2_sqm.py | 145, 146 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | modules/05_support_predictor/m05 | e9_core_transfer.py | 101 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/m05 | embedding_experiments_E.py | 27 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/m05 | embedding_skipgram_E5.py | 100 | `global` wordt gebruikt om moduleconstanten vanuit `main()` te wijzigen | Waarden als parameter of via een config-object doorgeven |
| laag | modules/05_support_predictor/m05 | learning_curve_layerA.py | 101 | Legacy `np.random.seed` | `rng = np.random.default_rng(seed)` gebruiken en `rng` doorgeven |
| laag | modules/05_support_predictor/m05 | learning_curve_layerA.py | 105 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/m05 | learning_curve_layerA_v2_descriptors.py | 31 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/m05 | ring_survey.py | 65, 69 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | modules/05_support_predictor/m05 | smoke_test.py | 23 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/notebook | deep_learning.ipynb | cell 3:1 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/05_support_predictor/notebook | deep_learning.ipynb | cell 14:3 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/05_support_predictor/notebook | deep_learning.ipynb | cell 18:7 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/06_generative_candidates/m06 | data.py | 4 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/06_generative_candidates/m06 | evaluate.py | 3 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/06_generative_candidates/m06 | fetch_pubchem_aromatics.py | 17 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/06_generative_candidates/m06 | fetch_pubchem_aromatics.py | 41 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/06_generative_candidates/m06 | model.py | 2 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/06_generative_candidates/m06 | train.py | 26 | Legacy `np.random.seed` | `rng = np.random.default_rng(seed)` gebruiken en `rng` doorgeven |
| laag | modules/06_generative_candidates/notebook | generative_model.ipynb | cell 3:8, cell 3:11 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/06_generative_candidates/notebook | generative_model.ipynb | cell 14:3, cell 11:21 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/06_generative_candidates/notebook | generative_model.ipynb | cell 14:11, cell 14:12 | Import niet bovenaan module/cel | Imports naar boven verplaatsen; bij bewuste `sys.path`-manipulatie `# noqa: E402` toevoegen |
| laag | modules/07_agentic_workflows | make_summary.py | 8 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/07_agentic_workflows/notebook | agentic_system.ipynb | cell 3:1, cell 3:7 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/07_agentic_workflows/notebook | make_notebook.py | 9 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | modules/07_agentic_workflows/steward | policy.py | 34 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/07_agentic_workflows/steward | tools.py | 36 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | modules/standout_pattern_proposer | run_simulation.py | 31 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | modules/standout_pattern_proposer | stage_readout.py | 84 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | modules/standout_pattern_proposer | stage_readout.py | 119 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | modules/standout_pattern_proposer/notebook | pattern_proposer.ipynb | cell 2:12 | Import niet bovenaan module/cel | Imports naar boven verplaatsen; bij bewuste `sys.path`-manipulatie `# noqa: E402` toevoegen |
| laag | probes | amplitude_test.py | 115 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | probes | anchor_single_point_timing.py | 210, 212 | `global` wordt gebruikt om moduleconstanten vanuit `main()` te wijzigen | Waarden als parameter of via een config-object doorgeven |
| laag | probes | bandwidth_rule_redesign.py | 23 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | bandwidth_rule_redesign.py | 42 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | canonical_gradient_timing.py | 47 | Hard-gecodeerde `/tmp`-map | `tempfile.mkdtemp()` / `tempfile.gettempdir()` gebruiken |
| laag | probes | chain_corpus_after_anchor.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | check_half_deck.py | 1 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | dh_diagonal_baseline.py | 96 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | dryrun_dft_delta_recovery.py | 506, 592 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | dryrun_dft_delta_recovery.py | 632, 701, 773 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | probes | dryrun_dft_delta_recovery.py |  | Zeer lang script (>800 regels) | Opsplitsen in functies/modules; bij promotie naar tier 2 verplicht (policy punt 1) |
| laag | probes | dryrun_symmetry_prior.py | 119 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | probes | dryrun_symmetry_prior.py | 263, 264 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | probes | dryrun_symmetry_prior.py | 276 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | duration_table.py | 53 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | duration_table.py | 55, 136 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | probes | e8_cc_hessian_fd.py | 14 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | e8_cc_locality.py | 12 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | e8_symmetry.py | 34 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | e8_symmetry.py | 96 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | probes | host_guard.sh |  | Bash-script zonder `set -e`; bij een polling-/diagnosescript is dat bewust (een lege `pgrep`/`grep` is daar normaal) | Zo laten, maar `set -u` en `pipefail` gebruiken en fouten per stap expliciet afhandelen; de reden in een commentaarregel vastleggen |
| laag | probes | l2_lno_price.py | 114 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | l2_lno_price.py | 101 | `global` wordt gebruikt om moduleconstanten vanuit `main()` te wijzigen | Waarden als parameter of via een config-object doorgeven |
| laag | probes | launch_detached.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | m03_band_uncertainty.py | 115, 219 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | m03_band_uncertainty.py | 61 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | probes | m1_frozen_spaces.py | 277, 281 | `global` wordt gebruikt om moduleconstanten vanuit `main()` te wijzigen | Waarden als parameter of via een config-object doorgeven |
| laag | probes | m2a_gradient_cost_ratio.py | 20 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | m2a_gradient_cost_ratio.py | 153, 154 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | probes | m2b_pyscfad_response.py | 128 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | probes | matched_control.py | 49 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |
| laag | probes | naph_level_smoke.py | 6 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | q10_coverage.py | 23 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | qff_from_hessians.py | 121 | Lusvariabele wordt niet gebruikt | Hernoemen naar `_` of `_naam` |
| laag | probes | route2_naphthalene.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_after_lanes_ccx53.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_cations_after_route2.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_e8_ccx53.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_e8_handover.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_e8_naph_extras.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | run_e8_naph_parallel.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | probes | shape_test_couplings.py | 76 | Lokale variabele wordt toegekend maar nooit gebruikt (dode code of een vergeten gebruik) | Nagaan of de waarde gebruikt had moeten worden; zo niet, de toekenning verwijderen |
| laag | probes | state.sh |  | Bash-script zonder `set -e`; bij een polling-/diagnosescript is dat bewust (een lege `pgrep`/`grep` is daar normaal) | Zo laten, maar `set -u` en `pipefail` gebruiken en fouten per stap expliciet afhandelen; de reden in een commentaarregel vastleggen |
| laag | probes | symmetrise_geometry.py | 15 | Ongebruikte import | Import verwijderen (`ruff check --fix --select F401`) |
| laag | probes | t1_transfer_test.py | 80 | Functie/lambda in een lus bindt de lusvariabele niet. Handmatig gecontroleerd: overal wordt de closure binnen dezelfde iteratie aangeroepen, dus nu geen fout, wel een valkuil bij latere wijzigingen | Lusvariabele als default-argument binden (`lambda s, tr=tr: ...`) of de functie buiten de lus definiëren met expliciete parameters |
| laag | tests | test_e8_frozen_guard.py | 13 | `exec()` op broncode | Aanvaardbaar in een test die een script inleest; anders de functie importeren in plaats van `exec` |
| laag | tools | backup_loop.sh |  | Bash-script zonder `set -e`; bij een polling-/diagnosescript is dat bewust (een lege `pgrep`/`grep` is daar normaal) | Zo laten, maar `set -u` en `pipefail` gebruiken en fouten per stap expliciet afhandelen; de reden in een commentaarregel vastleggen |
| laag | tools | modules_fresh_check.sh |  | Server-/machinespecifieke absolute paden (`/root/...`, `/mnt/c/Users/...`) hard-gecodeerd | Pad via argument of omgevingsvariabele (met een relatief default t.o.v. `Path(__file__)`) meegeven |
| laag | tools | rebuild_check.py | 154 | Lusvariabele wordt binnen de lus overschreven | Een nieuwe naam gebruiken voor de afgeleide waarde |

## 2. Toelichting stijlregels

| Regel | Issue | Oplossing |
|---|---|---|
| E702 | meerdere statements op één regel (`;`) | Eén statement per regel; `ruff format` splitst ze automatisch |
| E701 | statement na `:` op dezelfde regel | Blok op een nieuwe regel zetten; `ruff format` |
| E501 | regel langer dan 160 tekens | Regel afbreken of `ruff format` draaien |
| E401 | meerdere imports op één regel | Eén import per regel (`ruff check --fix`) |
| I001 | imports niet gesorteerd | `ruff check --fix --select I` |
| F541 | f-string zonder placeholders | `f`-prefix weghalen (`ruff check --fix`) |
| UP031 | `%`-formattering i.p.v. f-string | Omzetten naar f-string |
| UP009 | overbodige `# -*- coding: utf-8 -*-` | Coding-regel verwijderen (`--fix`) |
| UP020 | `io.open` i.p.v. `open` | `open` gebruiken (`--fix`) |
| UP045 | `Optional[X]` i.p.v. `X | None` | `X | None` schrijven (`--fix`) |
| E731 | lambda toegekend aan naam | `def` gebruiken |
| E703 | overbodige `;` aan regeleinde | `;` verwijderen (`--fix`) |
| C901 | functie te complex (McCabe >10) | Functie opsplitsen in kleinere functies |
| PLR0915 | functie met >50 statements | Functie opsplitsen; I/O scheiden van rekenwerk (policy punt 1) |

## 3. Stijlmeldingen per bestand

| Folder | Bestand | Meldingen (regel × aantal) |
|---|---|---|
| GoalGathering/architecture | 51_deltaH_model_pytorch.py | E702×6, E501×1 |
| modules/02_opponent_atlas | build_cheap_line_table.py | E702×9, E501×5, E701×2, E401×1, I001×1 |
| modules/02_opponent_atlas | build_line_c_table.py | E702×11, E701×7, E501×3, E401×1, I001×1 |
| modules/02_opponent_atlas | build_opponent_atlas.py | E702×18, E701×12, E501×3, E401×1, I001×1, C901×1, PLR0915×1 |
| modules/02_opponent_atlas | c384_environments.py | E702×23, E501×9, E701×8, I001×2 |
| modules/02_opponent_atlas | make_summary.py | E702×12, E501×9, E701×6, E401×1, I001×1 |
| modules/02_opponent_atlas/notebook | data_workflow.ipynb | E702×38, E501×13, E401×2, I001×2, E701×1 |
| modules/02_opponent_atlas/notebook | make_notebook.py | E501×29, E731×2, I001×1, E702×1 |
| modules/03_lab_scoreboard | build_lab_tables.py | E501×8, E401×2, I001×2, C901×1, PLR0915×1 |
| modules/03_lab_scoreboard | cold_columns_item62_grandpahs.py | E501×14, E702×5 |
| modules/03_lab_scoreboard | cold_columns_items61_62.py | E501×13, E702×5 |
| modules/03_lab_scoreboard | dft_mode_families.py | E501×7, E702×3, I001×1 |
| modules/03_lab_scoreboard | make_summary.py | E702×25, F541×14, E701×7, E501×7, E401×1, I001×1 |
| modules/03_lab_scoreboard/notebook | analysis.ipynb | E702×32, E501×8, I001×2, E401×2 |
| modules/03_lab_scoreboard/notebook | make_notebook.py | E501×17, E731×2, I001×1 |
| modules/03_lab_scoreboard | origin_columns_naphthalene.py | E501×9, E702×2 |
| modules/03_lab_scoreboard | shape_family_weights_check.py | E702×6, E501×4, I001×1 |
| modules/03_lab_scoreboard | shape_score.py | E702×28, E501×12, UP031×3, E701×2, I001×1 |
| modules/04_calibrated_harmonic | build_training_table.py | E501×5, E401×2, I001×1 |
| modules/04_calibrated_harmonic | make_summary.py | E702×24, F541×8, E501×8, E701×6, E401×1, I001×1 |
| modules/04_calibrated_harmonic/notebook | make_notebook.py | E501×18, E731×2, I001×1 |
| modules/04_calibrated_harmonic/notebook | modeling.ipynb | E702×30, E501×7, UP031×5, I001×2, E701×2, E401×1 |
| modules/05_support_predictor/corpus | analytic_hessians.py | E702×35, E501×5 |
| modules/05_support_predictor/corpus | build_manifest.py | E702×7, E501×4, E701×2, C901×2, E401×1, I001×1 |
| modules/05_support_predictor/corpus | cation_rows.py | E702×16, E501×9, E701×1 |
| modules/05_support_predictor/corpus | check_results.py | E702×5, E501×1 |
| modules/05_support_predictor/corpus | fd_grid_test_benzene.py | E702×10, E401×2, I001×1, E501×1 |
| modules/05_support_predictor/corpus | merge_shards.py | E702×11, E701×2, C901×1 |
| modules/05_support_predictor/corpus | psi4_worker.py | E702×31, E501×7, I001×4, E401×2, PLR0915×1 |
| modules/05_support_predictor/corpus | read_imaginary_second_route.py | E702×16, E501×4, C901×1, PLR0915×1 |
| modules/05_support_predictor/corpus | run_corpus.py | E702×39, E501×21, E701×9, E401×2, I001×2, C901×1, PLR0915×1 |
| modules/05_support_predictor/corpus | saddle_restarts.py | E702×13, E501×2 |
| modules/05_support_predictor/corpus | status.py | E401×1, I001×1, E501×1, E702×1 |
| modules/05_support_predictor/m05 | build_corpus.py | E702×6, E401×1, I001×1 |
| modules/05_support_predictor/m05 | build_release.py | E702×4, E501×3, PLR0915×1 |
| modules/05_support_predictor/m05 | deltah_model.py | E702×6, E501×1 |
| modules/05_support_predictor/m05 | e10_environment_once.py | E702×35, E701×19, E501×18, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e11_extras.py | E702×28, E501×19, E701×14, I001×1, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e11_noise_floor.py | E702×15, E501×1 |
| modules/05_support_predictor/m05 | e11_power_law.py | E702×12, E501×3 |
| modules/05_support_predictor/m05 | e6_learning_curve.py | E702×32, E501×11, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e7_rungB_diag_a.py | E702×7, E501×2, E401×1, I001×1 |
| modules/05_support_predictor/m05 | e7_rungB_pairs.py | E702×90, E501×52, E701×12, C901×2, PLR0915×2, E401×1, I001×1, F541×1 |
| modules/05_support_predictor/m05 | e7_rungB_reread_analytic.py | E702×24, E501×9, F541×1, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e7_t1_sign_test.py | E702×25, E501×7, I001×1 |
| modules/05_support_predictor/m05 | e7_t2_ceilings.py | E702×20, E501×6, I001×2, E401×1 |
| modules/05_support_predictor/m05 | e7_t2_posthoc.py | E702×41, E501×9, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e7_t2_sqm.py | E702×45, E501×6 |
| modules/05_support_predictor/m05 | e9_core_transfer.py | E702×31, E701×9, E501×8, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | e9_posthoc_block.py | E702×22, E701×5, E501×3, PLR0915×1 |
| modules/05_support_predictor/m05 | embedding_experiments_E.py | E702×44, E701×4, E501×1, PLR0915×1 |
| modules/05_support_predictor/m05 | embedding_skipgram_E5.py | E702×20, E501×4, I001×1, E701×1, C901×1, PLR0915×1 |
| modules/05_support_predictor/m05 | inspect_hessian_qm9.py | E702×11, E501×7, E401×2, I001×1 |
| modules/05_support_predictor/m05 | learning_curve_layerA.py | E702×17, E701×4, E501×1 |
| modules/05_support_predictor/m05 | learning_curve_layerA_v2_descriptors.py | E702×10, E701×6, E501×2, I001×1, C901×1 |
| modules/05_support_predictor/m05 | ring_survey.py | E702×23, E501×7, E401×2, E701×2, I001×1, F541×1, C901×1 |
| modules/05_support_predictor/m05 | rungC_pretrain.py | PLR0915×1 |
| modules/05_support_predictor/m05 | rungC_train.py | C901×2, PLR0915×2 |
| modules/05_support_predictor/m05 | smoke_test.py | E702×6, E401×2, I001×1 |
| modules/05_support_predictor/m05 | sync_model.py | I001×1 |
| modules/05_support_predictor/m05 | target_diagnostics_E4.py | E702×13, E501×3, I001×1, E701×1 |
| modules/05_support_predictor | make_summary.py | E501×49, E702×12 |
| modules/05_support_predictor/notebook | deep_learning.ipynb | E702×126, E501×65, E701×7, I001×4, E401×2, E703×2 |
| modules/05_support_predictor/notebook | execute_section8.py | E702×15, E501×5 |
| modules/05_support_predictor/notebook | make_notebook.py | E501×71, E702×1 |
| modules/06_generative_candidates/m06 | baseline_ngram.py | E702×13, E501×1 |
| modules/06_generative_candidates/m06 | data.py | E702×5, E701×1 |
| modules/06_generative_candidates/m06 | evaluate.py | E702×5 |
| modules/06_generative_candidates/m06 | fetch_pubchem_aromatics.py | E702×17, E501×3, C901×1, PLR0915×1 |
| modules/06_generative_candidates/m06 | model.py | E702×11 |
| modules/06_generative_candidates/m06/tests | test_m06.py | E702×12 |
| modules/06_generative_candidates/m06 | train.py | E702×28, E501×2, I001×1, PLR0915×1 |
| modules/06_generative_candidates | make_summary.py | E501×23, E702×16 |
| modules/06_generative_candidates/notebook | generative_model.ipynb | E702×69, E501×39, I001×6, E701×3, E401×2 |
| modules/06_generative_candidates/notebook | make_notebook.py | E501×41 |
| modules/07_agentic_workflows | make_summary.py | E501×59, E702×6 |
| modules/07_agentic_workflows/notebook | agentic_system.ipynb | E702×20, E501×14, I001×3, E701×3, E401×2 |
| modules/07_agentic_workflows/notebook | make_notebook.py | E501×14 |
| modules/07_agentic_workflows | run_scenarios.py | E702×6, E501×2, I001×1 |
| modules/07_agentic_workflows/steward | gate.py | E501×6, C901×1 |
| modules/07_agentic_workflows/steward | graph.py | E702×8, E501×4, C901×1 |
| modules/07_agentic_workflows/steward | policy.py | E501×11, E702×2, I001×1, C901×1 |
| modules/07_agentic_workflows/steward | schema.py | UP045×2 |
| modules/07_agentic_workflows/steward | tools.py | E702×1 |
| modules/07_agentic_workflows/tests | test_gate.py | E501×6, E702×3, I001×1 |
| modules/standout_pattern_proposer | deck_cost_readout.py | E501×2 |
| modules/standout_pattern_proposer | make_summary.py | E501×9 |
| modules/standout_pattern_proposer | merge_shards.py | E501×3 |
| modules/standout_pattern_proposer/notebook | make_notebook.py | E501×17 |
| modules/standout_pattern_proposer/notebook | pattern_proposer.ipynb | E702×21, E501×16, I001×5, E401×2, E701×1 |
| modules/standout_pattern_proposer | paired_readout.py | E702×4, F541×1 |
| modules/standout_pattern_proposer | run_export.py | E501×2 |
| modules/standout_pattern_proposer | run_simulation.py | E501×5, C901×1, PLR0915×1 |
| probes | amplitude_test.py | UP031×5, E401×1, I001×1, PLR0915×1 |
| probes | anchor_single_point_timing.py | E702×7, E501×4, UP009×1, I001×1, PLR0915×1 |
| probes | bandwidth_rule_redesign.py | E401×1, I001×1, F541×1, C901×1, PLR0915×1 |
| probes | benzene_benchmark_map.py | E501×5, PLR0915×1 |
| probes | canonical_gradient_timing.py | UP009×1, I001×1, E501×1 |
| probes | check_half_deck.py | E401×1, I001×1 |
| probes | check_reading_copy_numbers.py | E501×2 |
| probes | deck_counts_planar.py | E702×2 |
| probes | dh_diagonal_baseline.py | E702×41, E501×14, E701×3, E731×1, C901×1, PLR0915×1 |
| probes | dipole_derivatives.py | UP031×2, I001×1 |
| probes | dryrun_dft_delta_recovery.py | E702×29, PLR0915×3, C901×3, UP009×1, I001×1, F541×1, E501×1 |
| probes | dryrun_symmetry_prior.py | E702×36, E501×9, E701×5, I001×2, C901×2, UP009×1, E401×1, PLR0915×1 |
| probes | duration_table.py | E501×30, E702×24, E731×1, E701×1, F541×1, C901×1, PLR0915×1 |
| probes | e8_between_extension.py | E702×32, E501×4, PLR0915×1 |
| probes | e8_cc_hessian_fd.py | E702×45, E501×4, C901×1, PLR0915×1 |
| probes | e8_cc_locality.py | E702×64, E501×9, F541×1, PLR0915×1 |
| probes | e8_compare_hessians.py | E702×8, E501×1 |
| probes | e8_sparse_probe_count.py | E702×25, E501×12, C901×1 |
| probes | e8_sparse_recovery_benzene.py | E702×44, E501×9, C901×1, PLR0915×1 |
| probes | e8_symmetry.py | E702×34, E501×2, C901×1, PLR0915×1 |
| probes | factory_to_stageA.py | E702×8, UP009×1, I001×1, E501×1 |
| probes | i14_odd_part_dft.py | I001×1, E702×1 |
| probes | l2_lno_price.py | E702×45, E501×9, E701×3, I001×2, PLR0915×1 |
| probes | l2b_tiers_benzene.py | E702×44, E501×6, I001×1, E701×1, PLR0915×1 |
| probes | l3_ulno_price.py | E702×56, E501×11, E701×8, I001×2, PLR0915×1 |
| probes | m03_band_uncertainty.py | E702×33, E501×10, E701×9, E401×1, I001×1, F541×1, C901×1, PLR0915×1 |
| probes | m1_basis_scf_mp2_line.py | E501×6, E702×5, UP009×1, E401×1, I001×1, PLR0915×1 |
| probes | m1_basis_sensitivity.py | E501×2, UP009×1, E401×1, I001×1, E702×1 |
| probes | m1_canonical_truth.py | I001×2, E501×2, UP009×1, E702×1, PLR0915×1 |
| probes | m1_frozen_spaces.py | E702×14, E501×4, UP009×1, C901×1, PLR0915×1 |
| probes | m1_noise_option_b.py | E501×5 |
| probes | m1_odd_part_symmetry.py | E501×4, E702×3, E401×1, I001×1 |
| probes | m1_xtight_readin.py | E702×8, E501×8, UP009×1, E401×1, I001×1 |
| probes | m2a_gradient_cost_ratio.py | E702×41, E501×14, I001×6, E401×1, E701×1, C901×1, PLR0915×1 |
| probes | m2b_pyscfad_response.py | UP031×11, E702×7, E731×2, I001×1 |
| probes | m3_family_reading.py | E702×7, E501×2 |
| probes | m4_cation_timing.py | E702×15, I001×1 |
| probes | make_qff_displacements.py | E702×2, I001×1 |
| probes | matched_control.py | UP031×6, E702×3, E401×1, I001×1 |
| probes | naph_level_smoke.py | E702×4, E401×1, I001×1, E501×1 |
| probes | naphthalene_geometry.py | UP009×1, E401×1, I001×1 |
| probes/patches | apply_pyscf_forge_dfvvvv_patch.py | UP020×3, E702×2, E401×1, I001×1 |
| probes/patches | apply_pyscf_forge_numpy2_cp_patch.py | UP020×3, E702×2, E401×1, I001×1 |
| probes | pyscf_hessians_for_qff.py | E702×13, I001×1 |
| probes | q10_coverage.py | E501×11, E401×2, UP009×1, I001×1, E702×1 |
| probes | q4_check.py | E401×1, I001×1 |
| probes | qff_from_hessians.py | E702×45, E501×9, C901×2, F541×1, PLR0915×1 |
| probes | r0_convention_check.py | E702×11, E401×1, I001×1, E501×1 |
| probes | r0_diagonal_reading.py | E702×15, E501×10, PLR0915×1 |
| probes | r0_geometry_check.py | E702×18, E501×3, E401×1, I001×1 |
| probes | r0_geometry_check_oop.py | E702×12, E401×1, I001×1, E701×1 |
| probes | r0_table_2026-09-28.py | E501×7, E702×5 |
| probes | reduced_coords.py | E702×1 |
| probes | route2_optimise.py | E501×2 |
| probes | route2_vs_lab.py | E501×16, E702×12, E701×2, I001×1 |
| probes | route_noise_structure.py | E702×9, I001×1 |
| probes | shape_test_couplings.py | UP031×6, PLR0915×1 |
| probes | t1_transfer_test.py | E702×14, E501×9, I001×1, E731×1, E701×1, PLR0915×1 |
| probes | vpt2_benzene.py | E501×4, I001×1, C901×1, PLR0915×1 |
| probes | vpt2_checkpoint.py | E702×3, C901×1 |
| tools | patch_file.py | E702×2 |

## 4. Provenance (heuristisch, handmatig te bevestigen)

De policy eist een provenance-kop (git-hash, commando, versies, machine) op elk resultaatbestand van een probe. De onderstaande scripts schrijven bestanden (`open(..., 'w')`, `json.dump`, `np.save*`, `to_csv`, `savefig`, `write_text`) maar bevatten het woord `provenance` nergens. Een deel zal via een andere route stempelen of alleen figuren schrijven; daarom is dit een controlelijst en geen vaststelling.

**Oplossing:** elk resultaatbestand afsluiten met `dpir.provenance.provenance_block()`, of voor figuren de git-hash in de metadata/bijschrift zetten.

| Folder | Scripts |
|---|---|
| modules/02_opponent_atlas | build_cheap_line_table.py, build_opponent_atlas.py, c384_environments.py |
| modules/02_opponent_atlas/notebook | make_bands_derived.py, make_notebook.py |
| modules/03_lab_scoreboard | build_lab_tables.py, cold_columns_item62_grandpahs.py, cold_columns_items61_62.py, dft_mode_families.py, origin_columns_naphthalene.py, shape_family_weights_check.py, shape_score.py |
| modules/03_lab_scoreboard/notebook | make_notebook.py |
| modules/04_calibrated_harmonic | build_training_table.py |
| modules/05_support_predictor/corpus | analytic_hessians.py, build_manifest.py, cation_rows.py, merge_shards.py, psi4_worker.py, read_imaginary_second_route.py, rehash_layerB.py, run_corpus.py, saddle_restarts.py, status.py |
| modules/05_support_predictor/m05 | build_corpus.py, build_release.py, design_check.py, e10_environment_once.py, e11_extras.py, e11_noise_floor.py, e11_power_law.py, e6_learning_curve.py, e7_rungB_pairs.py, e7_rungB_reread_analytic.py, e7_t1_sign_test.py, e7_t2_ceilings.py, e7_t2_posthoc.py, e7_t2_sqm.py, e9_core_transfer.py, e9_posthoc_block.py, embedding_experiments_E.py, embedding_skipgram_E5.py, inspect_hessian_qm9.py, learning_curve_layerA.py, learning_curve_layerA_v2_descriptors.py, release_index.py, ring_survey.py, rungC_pretrain.py, rungC_stage_pick.py, rungC_train.py, smoke_test.py, sync_model.py, target_diagnostics_E4.py |
| modules/05_support_predictor/notebook | make_notebook.py |
| modules/06_generative_candidates/m06 | baseline_ngram.py, fetch_pubchem_aromatics.py, train.py |
| modules/06_generative_candidates/notebook | make_notebook.py |
| modules/07_agentic_workflows | run_scenarios.py |
| modules/07_agentic_workflows/notebook | make_notebook.py |
| modules/standout_pattern_proposer | deck_cost_readout.py, merge_shards.py, readout.py, run_export.py, run_simulation.py, stage_readout.py |
| modules/standout_pattern_proposer/notebook | make_notebook.py |
| modules/standout_pattern_proposer/pp | core.py, embed_scorer.py, scorer.py |
| probes | amplitude_test.py, anchor_single_point_timing.py, bandwidth_rule_redesign.py, benzene_benchmark_map.py, canonical_gradient_timing.py, dh_diagonal_baseline.py, dipole_derivatives.py, dryrun_dft_delta_recovery.py, dryrun_symmetry_prior.py, duration_table.py, e8_between_extension.py, e8_cc_hessian_fd.py, e8_cc_locality.py, e8_sparse_probe_count.py, e8_sparse_recovery_benzene.py, factory_to_stageA.py, i14_odd_part_dft.py, l2_lno_price.py, l2b_tiers_benzene.py, l3_ulno_price.py, lno_checkpoint.py, m03_band_uncertainty.py, m1_basis_scf_mp2_line.py, m1_basis_sensitivity.py, m1_canonical_truth.py, m1_frozen_spaces.py, m1_noise_option_b.py, m1_odd_part_symmetry.py, m1_xtight_readin.py, m2a_gradient_cost_ratio.py, m2b_pyscfad_response.py, m4_cation_timing.py, make_qff_displacements.py, matched_control.py, naphthalene_geometry.py, q10_coverage.py, r0_convention_check.py, r0_diagonal_reading.py, r0_geometry_check.py, r0_geometry_check_oop.py, r0_table_2026-09-28.py, route2_optimise.py, route2_vs_lab.py, shape_test_couplings.py, symmetrise_geometry.py, t1_transfer_test.py, vpt2_benzene.py |
| probes/patches | apply_pyscf_forge_dfvvvv_patch.py, apply_pyscf_forge_numpy2_cp_patch.py |
