# Handoff — review gate, 14 November 2026

Written from a cloud session so the Remote Control session "Udacity capstone plan"
(laptop, context ~906k of 1M) can pick up after compaction. Source: that
session's own transcript, turns 19:44–19:55 UTC. Its laptop process ended at 20:05:43 UTC (`host_exit`); the
session was archived automatically and unarchived on the user's word.

## State on the laptop (not on GitHub)
- The work below is **uncommitted** in the laptop's working tree on `master` (the tree was reported dirty, 0 unpushed
  commits). Staged digest at the reviewer's read: `a1552be2b9d99775`; `review_gate.py` was ahead of the index (`AM`).
- Rule `unreviewed_landing` in `tools/hooks/guard.py` is set to **`log_only`**: it logs to `hooks.log`, refuses nothing.
- 113 tests green (`tests/test_review_gate.py`, `tests/test_hooks_guard.py`), including a near-miss table of command forms.
- The session said it lands **nothing on `master`** until the user decides the two points below.

## What the gate does
Review at landing, not per commit:
- commits on a branch are free;
- `git merge <branch>` reviews `HEAD...<branch>`; `git pull` reviews against the upstream (own refspec respected);
- `git commit` on `master` counts as landing;
- `rebase` / `cherry-pick` onto `master` are refused (recovery flags such as `--abort` always pass);
- a merge or pull on a branch lands nothing; a command naming another repo (`-C`, `--git-dir`) is out of scope;
- the record in `tools/reviews.jsonl` carries what landed (`"lands": ...`); each line is read separately and a bad line
  names file, line and fault instead of crashing.

## What the reviewer found and what was fixed
9 bypasses and 8 ways it blocked real work. Fixed: `git rebase --abort` refused; a commit in the pyscf fork refused on
this repo's index; one bad `reviews.jsonl` line crashing every commit; `git merge -m 'msg' branch` reading the message as
the branch (now a table of value-taking options); `git -c core.hooksPath=/dev/null commit`, `git.exe`, `/usr/bin/git`
not recognised by the command-word reader (also fixed for two older rules).

## Waiting for the user
1. **Coverage.** Still unwatched routes to `master`: `git reset --hard <branch>`, `git branch -f master <branch>`,
   `git push origin <branch>:master`, `git am`, a commit in detached HEAD. Proposal: move the gate into git's own hooks
   (`pre-commit`, `pre-merge-commit`, `reference-transaction`), which fire however the command is written.
2. **Cost.** With `REVIEWED = ("*")` every task-board line costs a fresh reviewer. Proposal: gate code and tests only;
   `TASKS.md`, the ledger, `probes/results_m1/**` and `out/**` pass without review.

After the decisions: one fresh reviewer over the final diff before it lands on `master`, as the rule itself prescribes.
