"""New comments by others on our pull requests and issues in other projects (TASKS 105; on dxtb#278 the maintainer asked 'Can this be
merged?' on 18 Oct 2026 and nobody here saw it for five days).

  new [--seed]   every thread outside our own repositories that involves us and changed in the last WINDOW_DAYS days: its comments,
                 reviews and review comments by people other than us (bots left out) that are not in the seen file yet — printed one line
                 each and recorded, so each is reported once; --seed records them without printing (the first run)

The watch runs `new` once per cycle and reports what it prints. The reply stays the user's, in their own words (pyscf's AI_POLICY.md;
the memory 'GitHub replies need consultation').
"""
from __future__ import annotations

import argparse
import sys
from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from pathlib import Path

from upstream_check import gh_json

ME = "thebreadishard"
WINDOW_DAYS = 30
SEEN = Path(__file__).resolve().parents[1] / "probes" / "watch_state" / "github_seen.txt"


def threads(api: Callable, since: datetime) -> list[dict]:
    """Issues and pull requests that involve us, in repositories not ours, updated since `since`."""
    q = f"involves:{ME}+-user:{ME}+updated:>={since:%Y-%m-%d}"
    return api(f"search/issues?q={q}&per_page=100")["items"]


def by_others(entries: list[dict]) -> list[dict]:
    return [e for e in entries if (e.get("user") or {}).get("login") not in (None, ME) and (e.get("user") or {}).get("type") != "Bot"]


def contributions(api: Callable, item: dict) -> list[tuple[str, dict]]:
    """(key, entry) of every comment, review and review comment on one thread by someone else; the key is unique across GitHub."""
    repo = item["repository_url"].split("/repos/", 1)[1]
    n = item["number"]
    out = [(f"comment:{c['id']}", c) for c in by_others(api(f"repos/{repo}/issues/{n}/comments?per_page=100"))]
    if "pull_request" in item:
        out += [(f"review:{r['id']}", r) for r in by_others(api(f"repos/{repo}/pulls/{n}/reviews?per_page=100"))]
        out += [(f"review_comment:{c['id']}", c) for c in by_others(api(f"repos/{repo}/pulls/{n}/comments?per_page=100"))]
    return out


def line(item: dict, entry: dict) -> str:
    repo = item["repository_url"].split("/repos/", 1)[1]
    when = (entry.get("created_at") or entry.get("submitted_at") or "")[:16].replace("T", " ")
    text = " ".join((entry.get("body") or entry.get("state") or "").split())[:110]
    return f"{repo}#{item['number']} {entry['user']['login']} {when}: {text} — {entry.get('html_url', item['html_url'])}"


def new(api: Callable = gh_json, seen_file: Path = SEEN, seed: bool = False, now: datetime | None = None) -> list[str]:
    """The lines of contributions not seen before, recorded as seen; with `seed` recorded but not returned."""
    seen = set(seen_file.read_text(encoding="utf-8").split()) if seen_file.exists() else set()
    since = (now or datetime.now(UTC)) - timedelta(days=WINDOW_DAYS)
    fresh = [(key, line(item, entry)) for item in threads(api, since) for key, entry in contributions(api, item) if key not in seen]
    if fresh:
        seen_file.parent.mkdir(parents=True, exist_ok=True)
        with seen_file.open("a", encoding="utf-8") as f:
            f.writelines(key + "\n" for key, _ in fresh)
    return [] if seed else [text for _, text in fresh]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="mode", required=True)
    sub.add_parser("new").add_argument("--seed", action="store_true", help="record what is there now without reporting it")
    a = p.parse_args(argv)
    lines = new(seed=a.seed)
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
