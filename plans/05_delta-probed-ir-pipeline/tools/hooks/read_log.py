"""The hook log as a table for the review with the user (TASKS 64, 15 Oct 2026): per rule the number of hits, how many were exempted, and its
distinct examples (first line of the command or the path, at most --examples per rule). Whether a hit was right is the review's judgement;
this only gathers.

    python tools/hooks/read_log.py [--log probes/watch_state/hooks.log] [--since 2026-10-15T17:49] [--examples 8]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import guard  # noqa: E402  (the rules' order, decisions and incidents)


def load(log: Path, since: str | None = None) -> list[dict]:
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()] if log.exists() else []
    return [e for e in entries if since is None or e["time"] >= since]


def table(entries: list[dict], examples: int = 8) -> list[str]:
    by_rule: dict[str, list[dict]] = defaultdict(list)
    for e in entries:
        by_rule[e["rule"]].append(e)
    span = f"{entries[0]['time']} to {entries[-1]['time']}" if entries else "no entries"
    lines = [f"# Hook log, {len(entries)} hits ({span})", "", "| rule | decision | hits | exempted | incident |", "|---|---|---|---|---|"]
    for r in guard.RULES:
        hits = by_rule.get(r.name, [])
        lines.append(f"| {r.name} | {r.decision} | {len(hits)} | {sum(1 for e in hits if e.get('exempt'))} | {r.incident} |")
    for r in guard.RULES:
        seen: list[str] = []
        for e in by_rule.get(r.name, []):
            first = e["excerpt"].splitlines()[0][:150] if e["excerpt"] else "(empty)"
            if first not in seen:
                seen.append(first)
        if seen:
            lines += ["", f"## {r.name}: {len(seen)} distinct", ""]
            lines += [f"{n}. `{s}`" for n, s in enumerate(seen[:examples], 1)]
            if len(seen) > examples:
                lines.append(f"... and {len(seen) - examples} more")
    unknown = sorted(set(by_rule) - {r.name for r in guard.RULES})
    if unknown:
        lines += ["", f"Rules in the log that the guard no longer has: {', '.join(unknown)}"]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--log", type=Path, default=guard.LOG)
    ap.add_argument("--since", default=None, help="ISO time; earlier entries are left out")
    ap.add_argument("--examples", type=int, default=8)
    a = ap.parse_args()
    print("\n".join(table(load(a.log, a.since), a.examples)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
