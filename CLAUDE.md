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
next check. Keep it current — a task that starts or ends changes a row, with the clock's stamp; the ledger keeps the outcome.

## Editing
One python patch script per edit round, in the scratchpad, built on `plans/05_delta-probed-ir-pipeline/tools/patch_file.py`
(`patch`, `append`, `insert_after_line`): exact-string `assert` on every anchor, the whole new text built in memory, then `os.replace` a
temp file over the original. Never open the target for
writing before the assertions pass — that emptied a probe script on 14 September.

## Long runs
- A quiet multi-day run gets no timed check-in. Arm one alarm-only watchdog: status to a log file,
  stdout only on a failure that needs a decision. Silence means healthy. Dry-run it once before arming;
  a false-positive pattern wakes the session all night.
- A timer here is a Monitor process, not a cron job. `CronList` and the scheduled-task list being empty
  proves nothing — look in `ps -ef`.
- Compile-check and dry-run every script a queued job will run. Smoke-test on water before the real run.

## Committing
Never `git add -A`: the run directories are written live and `results_vpt2/benzene_vpt2_psi4.out` is
75 MB of psi4 scratch. Name the paths. Compile-check first.

## Evidence
Every number in a document traces to a run log or a source. `probes/check_reading_copy_numbers.py`
audits the reading copy; write the equivalent script for any check that repeats. Mechanical checks are
scripts, not model passes.
