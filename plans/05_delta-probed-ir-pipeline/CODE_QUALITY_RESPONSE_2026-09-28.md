# Response to the code-quality review of 28 September 2026

Review: `CODE_QUALITY_FINDINGS_2026-09-28.md` (an independent review by Opus 5.5; 5 high, 97 medium, 104 low substantive findings, 4,053 style notes,
a heuristic provenance list). The user's instruction: ignore where warranted, correct where warranted, and add policy so the corrected classes cannot
recur. Every finding below was checked against the code before a decision; where the code had already changed on the morning of the 28th the
decision is stated against the current code. Tool versions: ruff 0.6.9 (the pre-commit pin), Python 3.14 locally, 3.12/3.14 on the servers.

## Why the findings could accumulate

The pre-commit ruff hook covered `src/` and `tests/` only. Everything in `modules/` and `tools/` was linted by nobody, so 1,110 semicolons, 753 long
lines and 33 unchecked `zip()`s piled up there unseen, and the correctness rules the review added (subprocess without `check`, blind excepts,
try/except/pass) were not selected anywhere. That is the root cause; the fix is in the policy section.

## Decisions per class

| class (review count) | decision | what was done |
|---|---|---|
| **High** — three CLI tests fail on a cp1252 pipe (`--help` prints Δ) | corrected | the m05 CLIs make their console safe (`console_utf8_safe`: a terminal keeps its code page with `?` for unencodable characters, a pipe or file gets UTF-8); the tests assert the return code; `tests/conftest.py` strips `PYTHONUTF8`/`PYTHONIOENCODING` from every test's environment so a test can no longer pass because the caller's shell set them — verified with and without `PYTHONUTF8` |
| **High** — 3.12 f-string syntax in two probes under `requires-python >= 3.10` | corrected in the declaration | every interpreter we run is 3.12 or 3.14 (laptop 3.14; hel1-2 envs 3.12/3.14; hel1-18 3.14); `requires-python` and ruff's target are now 3.12; the probes are unchanged |
| **Medium** — `zip()` without `strict` (50) | corrected in modules/tools (33 sites), ignored in probes (17) | every site in modules and tools is `strict=True` after checking that both iterables are built to the same length (symbols/coordinates, pairs/values, ids/predictions, sizes/ratios); the fast test suite and the smokes pass; probes are tier 1 and stay as their runs left them (`B905` ignored under `probes/**`, fixed at promotion) |
| **Medium** — `subprocess.run` without `check` (13 + tests) | corrected | every call now states `check=`; where the return code was already handled (git helpers, the psi4 worker whose `result.json` decides, the informational status digest, Word's PDF export) it is `check=False` with the reason on the line; `tools/rebuild_check.py` no longer runs README commands through a shell (`shlex.split`, argv) |
| **Medium** — `except Exception` (10) and try/except/pass (5) | corrected or reasoned | narrowed where the expected error is known (`ImportError` for the optional psi4 probe, `(OSError, SubprocessError, ValueError)` around the WSL pgrep and the git call); kept with a `# noqa: BLE001 — reason` where catching everything is the design (the psi4 worker records any failure in `result.json`; the corpus runner continues with the next molecule; rdkit raises several C++-backed exception types; experiment loops record and continue; the PubChem retry loop now prints each failed attempt); the silent `pass` in the worker's peak-memory probe now records `None` |
| **Medium** — ten chain scripts without `set -e` | reasoned, and a hook | the ten are launch chains that already ran on their servers; each carries `# no-set-e: … add set -euo pipefail before reusing it`; the three polling/diagnostic scripts state their reason; new hook `check-shell` (`tools/check_shell.py`, 4 tests) refuses any `.sh` that neither fails fast nor states why, and parses each with `bash -n` |
| **Medium** — hard-coded `/root/m05run/…` in the FD grid test; personal `QC_PYTHON` default | corrected | `--psi4-out` argument; `CORPUS_QC_PYTHON` has no default any more and the runner says how to set it |
| **Medium** — `rebuild_check.py` `shell=True` on document commands | corrected | see subprocess row |
| **Medium** — tier-2 docstrings / type hints (7 in `src/dpir`) | corrected | `Harmonic`, `omega_cm`, `atomic_masses_me`, `vpt2`, `report`, `main`, `provenance()` |
| **Medium** — `deep_learning.ipynb` execution counts out of order | accepted, by design | the notebook is executed append-only (`execute_section8.py`): the cells of 23 September keep their outputs, and each dated follow-up section runs in a fresh kernel after the setup and definition cells, so the counts restart per execution; the notebook's metadata records every append-only run. A top-to-bottom re-execution would replace the earlier runs' outputs, which the rule of 28 Sep forbids (module artefacts show the learning); the decision-51 re-run (section 11, 18:2x) follows the same path |
| **Low** — unused imports, f-strings without placeholders, import order, `Optional`/`isinstance` forms, `%`-formatting, lambdas assigned to names (≈ 80) | corrected | ruff autofix over modules and tools, compile-checked, tests green |
| **Low** — unused loop variables (16) | corrected in modules (13), probes untouched | renamed to `_name`; three tuple-unpacking loops by hand |
| **Low** — closures in loops (8) | corrected | loop variables bound as default arguments (`e6_learning_curve`, `e7_t2_sqm`, `stage_readout`, `read_imaginary_second_route`); the review had verified they were called inside their iteration, so no result changes |
| **Low** — dead assignments (15) | corrected in modules (5), probes untouched | removed after reading each: `dis`, `sym`, `text`, `f`, and `e` now logged |
| **Low** — `np.random.seed` (2) | ignored, with a stated reason | the 19 and 26 Sep runs are recorded with that seeding; changing it would silently change a reproduction; `# noqa: NPY002` names the run; new code uses `default_rng` (the rule is active) |
| **Low** — `global` in five scripts | ignored | tier-1 experiment scripts; `build_release.py` sets one flag from `argparse`; not worth a signature change; noted for promotion |
| **Low** — server paths in the chain scripts (10) | ignored | they run on `/root` by design; the `no-set-e` line marks them as one-off launch chains |
| **Low** — `/tmp` in one probe, a >800-line probe, `exec()` in a test | ignored | tier 1; the `exec` reads a script that cannot be imported without pyscf (the review agreed) |
| **Style** — E702/E701 (1,252 in modules/tools), E501 (753) | not adopted today; informative | a `ruff format` pass would rewrite 115 files on the day of the proposal and blur `git blame` for the evidence trail; the rules stay binding in `src/` and `tests/` and are ignored per path in `modules/`, `tools/`, `probes/` (`pyproject.toml`); the review's numbers stand as the backlog for promotion |
| **Style** — C901 / PLR0915 (complexity) | not adopted | promotion criterion (policy point 1), not a lint gate |
| **Provenance** — result writers without a provenance block (≈ 60 scripts) | corrected for the active writers, rule for the rest | `rungC_train`, `rungC_pretrain` and `design_check` now embed `dpir.provenance.provenance()` (commit, dirty flag, host, versions, command) in their JSON records; older scripts keep the records they wrote; every new record writer in `modules/` includes it (policy) |

## Policy changes (in `pyproject.toml`, `.pre-commit-config.yaml`, `QUALITY_POLICY.md`)

1. The ruff hook covers `src/`, `tests/`, `tools/` and `modules/` (executed notebooks and the external mai2025 code excluded). Correctness rules added
   everywhere it runs: `PLW1510`, `S110`, `BLE001`, plus the already-selected `B905`, `B023`, `B007`, `F841`, `NPY002`. Style rules `E501/E701/E702`
   stay binding in tier 2 and informative in tier 1 (per-path ignores).
2. New hook `check-shell`: every `.sh` parses and fails fast or states why.
3. Tests that start a subprocess run it under the plain console environment (conftest fixture) and assert its return code.
4. Python floor 3.12, matching every interpreter in use.
5. Record writers in `modules/` embed `provenance()`.
6. A `# noqa` carries its reason on the line; a bare `# noqa` is not accepted in review.

## Verification

80 fast tests pass (with and without `PYTHONUTF8` in the parent); ruff clean over `modules tools src tests`; every changed file compile-checked;
`check_shell` passes on all 15 scripts; smokes of `rungC_train`, `rungC_pretrain` and `design_check` pass and their records carry provenance;
`rungC_train --help` exits 0 on a plain pipe.
