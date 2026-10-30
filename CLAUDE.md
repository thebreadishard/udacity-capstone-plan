# Working rules for this repository

## Cost — read this before your first tool call
Three documents here are large: the reading copy (~52k tokens), the obstacle ledger (~33k), the plan 05
README (~24k). Every tool call resends everything already in the session, so a file read once is paid for
again on every later call in that session. On 16 September 2026 three subagents each read a whole
document and the account's monthly spend limit was hit twice in one morning.

**Never read one of those three in full, and never hand one whole to a subagent.** Get what you need with
`grep -n 'pattern' FILE | cut -c1-200`, `sed -n 'A,Bp' FILE`, or `tail`. If a task genuinely needs a
whole document — a cold read, a rewrite — say what it will cost and ask first. That is a decision for
the user, not a default.

## Where do we stand
Run `bash plans/05_delta-probed-ir-pipeline/probes/state.sh`. It prints running jobs, the last
heartbeats, memory, uncommitted files and the last ledger entries in about 40 lines. Use it instead of
reading the ledger. Only grep the ledger when the digest points at something specific.
Then read `plans/05_delta-probed-ir-pipeline/TASKS.md` (since 26 September 2026): one row per open task with its reason, place and
next check. Keep it current — a task that starts or ends changes a row, with the clock's stamp; the ledger keeps the outcome, and a
closed row moves to `TASKS_closed.md` with `tools/tasks_board.py archive` (since 27 October 2026; `check` runs in pre-commit). Every
open row opens with its class — PROOF, PRODUCT (the end product's quality: never dropped), DELIVERABLE, OPS, LATER — and its topic
(since 30 October 2026: Accuracy, Third-party, Documentation, Udacity, Literature, Pipeline, Supervisor, Operations; `tasks_board.py view`
lists them by topic) and its state (Now, User, Event: an open task is one we can do now; a waiting row names what it waits for with
`*Waits for:*`), and names its next check; it says where things stand, not its history; a duplicate is merged, a decision of the user's is a line in 'Waiting'.

## Editing
One python patch script per edit round, in the scratchpad, built on `plans/05_delta-probed-ir-pipeline/tools/patch_file.py`
(`patch`, `append`, `insert_after_line`; `patch_many` when an edit round touches several files): exact-string `assert` on every anchor, the whole new text built in memory, then `os.replace` a
temp file over the original. Never open the target for
writing before the assertions pass — that emptied a probe script on 14 September.

## Long runs
- A quiet multi-day run gets no timed check-in. Arm one alarm-only watchdog: status to a log file,
  stdout only on a failure that needs a decision. Silence means healthy. Dry-run it once before arming;
  a false-positive pattern wakes the session all night.
- A timer here is a Monitor process, not a cron job. `CronList` and the scheduled-task list being empty
  proves nothing — look in `ps -ef`.
- Compile-check and dry-run every script a queued job will run. Smoke-test on water before the real run.
- Since 15 October 2026 every run is launched through `tools/runspec.py launch probes/runspecs/<name>.json`: the spec names the log lines
  that prove progress and how long they may stay away, whatever the run's expected length (the #2702 repro ran 37 h without one).
- Since 19 October 2026 (the user: we want to see whether something is stuck, without hours of uncertainty): a library's own log is
  on (pyscf through `probes/library_log.py`, level 5, into a `pyscf.log` beside the outputs); every own log line is flushed and every
  run's Python is unbuffered (runspec sets PYTHONUNBUFFERED); a laptop run states its peak memory, and launch and resume refuse it past
  the budget for all laptop runs together (13 GB; a WSL run cites its `probes/wsl_capped.sh` cgroup cap as the bound). The watch stamps
  `probes/watch_state/watch_heartbeat`; state.sh says NOT RUNNING past 25 min. Look at runs with `runspec.py check --peek` — a plain
  `check` by hand uses up one-time events the watch must see (anchors3's end, 19 Oct).

## Hooks
`tools/hooks/guard.py` (plan 05) runs before every shell, Edit and Write call and after every edit: eight rules from incidents
(TASKS 64). A refused call names its rule and reason; fix the call rather than exempting it. `# hook-exempt: <reason>` is for a case the
user asked for, and is logged.

## Python code
Since 16 October 2026 (the user: clean-code best practices in every change we write or adjust) a Python change meets these, checked
before the commit — ruff's project set is the floor, not the bar:
- **One job per function.** Past ~50 statements, ~12 branches or ~6 parameters it is split, or its settings become one validated config
  object (pydantic or a frozen dataclass), not a long argument list.
- **Configuration is explicit and checked up front.** Defaults are the carried recipe; an older recipe is a named preset. Options that do
  not combine are refused before any data is loaded — never ignored, never refused after the first seed has trained. No
  `getattr(obj, "setting", default)` for settings and no attributes bolted onto an object after it is built.
- **Fail loudly.** `raise` with the reason, never `assert` for a runtime check (`python -O` strips it), no silent fallback.
- **One implementation** of every constant and formula, imported where needed.
- **No dead code**: unused variables, unused `# noqa`, commented-out code and stale docstrings go in the same change.
- **Resources** through context managers; a record is written to a temp file and moved over the target.
- **Types and names**: type hints on every public function; names say what a thing is (matrix notation H, B, F stays — it is the paper's).
- **Comments** say why, not what; a date or incident only where it explains a guard. History belongs in git and the ledger.
- **Tests**: a test for every switch; a refactor of code a run uses starts with a regression test that pins the current output, on a
  branch in its own worktree (the laptop's queued chains run from this checkout).
- Check (since 27 October 2026, the user: one config, the touched lines): `tools/ruff_gate.py` applies pyproject.toml's ruff set to every
  line written or changed, and to the whole function around such a line for the function-size rules; a new file is checked whole. It runs
  by itself after every Edit/Write (the hook acts), in pre-commit on the staged lines and in CI on the pushed commits; by hand
  `python tools/ruff_gate.py <file>[:start-end]`. The ignored rules are the paper's notation — single-letter indices, Greek — and physical
  constants. Every finding is fixed or carries a `# noqa: <rule>  <reason>`. Lines nobody touched are TASKS 139, cleaned where no run
  depends on the file.
  First file brought to it: `m05/rungC_train.py` (16 Oct 2026: 46 findings → 0, the record of a pinned run unchanged to the bit).

## Committing
Never `git add -A`: the run directories are written live and `results_vpt2/benzene_vpt2_psi4.out` is
75 MB of psi4 scratch. Name the paths. Compile-check first.

## Evidence
Every number in a document traces to a run log or a source. `probes/check_reading_copy_numbers.py`
audits the reading copy; write the equivalent script for any check that repeats. Mechanical checks are
scripts, not model passes.

Two rules since the lambda incident of 29 September 2026 (six days of CCSD(T) Hessians computed with the CCSD
lambda because `Gradients(mycc).kernel()` looked right and its pair checks passed):
- **A new library call in a production path cites the upstream test or example that makes the same call**, by
  file name, in the launch note or the ledger entry. pyscf's own `grad/test/test_ccsd_t.py` showed the correct
  usage the whole time; five minutes of reading against three lost days.
- **A registration's read script runs on synthetic records with the regime's edge cases before the registration is committed** (15 Oct
  2026: a line-2 fit through numerically-zero floors forecast 10¹⁰ cm⁻¹). **A claim about 'the model' names the head that runs**, read
  from the carried recipe, not from memory (the same evening a floor test analysed a head the recipe does not use).
- **"Validated" is written only with the number and the counterpart**: not "validated on benzene" but "gradient
  against finite differences of the energy on water, 1e-7". A validation claim without a number counts as not done,
  and a later reader (including a later session of me) may not build on it.
