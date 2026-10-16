# Run specs

One JSON file per run, `<name>.json`, launched with `python tools/runspec.py launch probes/runspecs/<name>.json` (TASKS 63, 15 Oct 2026).
The file is the launch record and is committed; the run's state lives in `probes/watch_state/runs/` (git-ignored), and `probes/watch.sh`
checks every running run through `tools/runspec.py check`. The model and its rules are in the docstrings of `tools/runspec.py`.

```json
{"name": "s3", "purpose": "TASKS 70: the S3 batch on s1", "host": "s1", "workdir": "/root/dpir_s3",
 "command": "bash probes/s3_batch.sh", "sources": [{"local": "probes/s3_batch.sh", "remote": "/root/dpir_s3/probes/s3_batch.sh"}],
 "progress": {"regex": "^=== \\(S3\\) [A-Za-z0-9_]+: done ", "max_gap_minutes": 90},
 "marker_regex": "^=== \\(S3\\) ", "end_regex": "^=== \\(S3\\) all done", "dry_run_args": "--dry-run", "threads": 8,
 "estimate": {"hours": 60, "basis": "S2's 19 molecules took 3.4 days on the same deck"}}
```

- `progress.regex` must match a line the run prints at least every `max_gap_minutes` (10–120). A script whose work sits inside a library
  call prints from a wrapper around the call it already makes (as `repro_2702.py` does from its counted Krylov operator).
- `progress.start_regex`, for a run that first waits for another job: the gap counts from that line on.
- Regexes are POSIX ERE (grep -E): `[0-9]`, not `\d`. In JSON a literal parenthesis is written `\\(`. Write a spec with an editor or the
  Write tool, never through a bash heredoc, which mangles the backslashes.
- `estimate` only with the measurement it comes from; at 1.5× of it the watch reports the run once.
- A laptop command that calls `wsl.exe` with a Linux path starts with `MSYS_NO_PATHCONV=1`, or Git Bash rewrites
  `/mnt/c/…` into a Windows path; call the script directly (not `bash -lc '…'`) so the dry run's arguments reach it.
