"""Every change is reviewed by an independent reviewer before it joins the trunk (the user, 14 November 2026).

The review is of the whole change, once, at the point where it would become part of what we have - not of every commit on the way
there. Work on a branch is free. This project commits straight to master most of the time, so 'before the merge' is read as 'before
it lands on the trunk, by whichever route': a merge brings a branch's diff, a commit on the trunk brings its own.

A hook cannot perform a review; it can only refuse the call that would land it. So this is the record and the refusal:

    python tools/review_gate.py digest [--incoming <ref>]            the digest of what would land
    python tools/review_gate.py check --staged                       a commit while HEAD is the trunk: the staged diff
    python tools/review_gate.py check --incoming <ref>               a merge or a pull: what <ref> would bring (HEAD...<ref>)
    python tools/review_gate.py record --reviewer <id> --findings <n> --verdict <text> [--note <text>] [--incoming <ref>]

`tools/hooks/guard.py`'s `unreviewed_landing` rule asks the right one of those before a commit on the trunk and before a merge or a
pull, and refuses the call when it fails. The record is one line per review in `tools/reviews.jsonl`, tracked by git, so that a
later reader can see who reviewed a change, how many findings it had and what was done with them.

Three honest limits, which the record states rather than hides:

* **The digest is of what would land**, computed with `tools/reviews.jsonl` itself excluded - otherwise writing the record would
  change the diff it is about. Stage or finish the branch first, then have it reviewed, then land it. Different content gives another
  digest and needs another review, which is the point.
* **Independence is asserted, not verified.** The gate cannot tell a fresh reviewer from this session talking to itself; the record
  names the reviewer so that the claim is at least written down and auditable.
* **A commit on a branch is not checked at all**, which is the rule's own shape: the branch is reviewed when it comes home.

What is reviewed: everything, which is what the rule says. REVIEWED is the one place to narrow it if the user ever wants records and
task-board rows to pass without a reviewer.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
REPO = PLAN.parents[1]
RECORDS = PLAN / "tools" / "reviews.jsonl"
TRUNK = "master"   # what "merged with what we have" means in this repository
# excluded from the digest: this file is written between the review and the commit, so including it would make every review stale
EXCLUDED = (":(exclude)plans/05_delta-probed-ir-pipeline/tools/reviews.jsonl",)
REVIEWED = ("*",)   # every path; the one place to narrow the rule


def _git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                          check=False)


def landing_diff(incoming: str | None) -> str:
    """What would land on the trunk: a branch's own changes since the merge base, or the staged diff.

    The reviewed paths only, and never the review record itself - it is written between the review and the landing, so
    counting it would make every review stale the moment it is recorded.
    """
    where = ["--cached"] if incoming is None else [f"HEAD...{incoming}"]
    done = _git("diff", "--no-color", *where, "--", *REVIEWED, *EXCLUDED)
    if done.returncode != 0:
        raise SystemExit(f"git diff {' '.join(where)} failed (exit {done.returncode}): {done.stderr.strip()[-300:]}")
    return done.stdout


def on_trunk() -> bool:
    """Is HEAD the trunk? A commit elsewhere is not a landing and is not checked.

    A git that cannot answer is not an answer: the gate refuses rather than passing a commit it knows nothing about (14 Nov 2026).
    """
    done = _git("rev-parse", "--abbrev-ref", "HEAD")
    if done.returncode != 0:
        raise SystemExit(f"git rev-parse --abbrev-ref HEAD failed (exit {done.returncode}): {done.stderr.strip()[-200:]}")
    return done.stdout.strip() == TRUNK


def digest_of(diff: str) -> str:
    return hashlib.sha256(diff.encode("utf-8")).hexdigest()[:16]


REQUIRED = ("digest", "reviewer", "findings", "verdict")


def records() -> list[dict]:
    """Every review on record, each line read on its own.

    A bad line raises with its number and what is wrong, instead of a traceback: this file is an append-only JSONL tracked by git,
    so it is a merge-conflict site, and a conflict's '<<<<<<< HEAD' used to crash the gate into refusing every commit there was
    (14 Nov 2026, the independent review).
    """
    if not RECORDS.is_file():
        return []
    out = []
    for n, line in enumerate(RECORDS.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as e:
            raise SystemExit(f"{RECORDS}:{n} is not a review: {e.msg}. A merge conflict in this file reads like this; resolve it, "
                             "keeping every line of both sides.") from None
        if not isinstance(entry, dict):
            raise SystemExit(f"{RECORDS}:{n} is a {type(entry).__name__}, not a review")
        missing = [k for k in REQUIRED if k not in entry]
        if missing:
            raise SystemExit(f"{RECORDS}:{n} is a review without {', '.join(missing)}")
        out.append(entry)
    return out


def review_of(digest: str) -> dict | None:
    return next((r for r in reversed(records()) if r["digest"] == digest), None)


def files_landing(incoming: str | None) -> list[str]:
    """The files the landing touches, over exactly the paths the digest covers."""
    where = ["--cached"] if incoming is None else [f"HEAD...{incoming}"]
    done = _git("diff", "--name-only", *where, "--", *REVIEWED, *EXCLUDED)
    if done.returncode != 0:
        raise SystemExit(f"git diff --name-only {' '.join(where)} failed (exit {done.returncode}): {done.stderr.strip()[-200:]}")
    return [line for line in done.stdout.splitlines() if line.strip()]


def what_lands(incoming: str | None) -> str:
    return f"what {incoming} would bring onto {TRUNK}" if incoming else f"the staged diff for {TRUNK}"


def check(incoming: str | None) -> int:
    """Exit 0 when what would land has a review on record, 1 with the reason when it does not.

    Nothing lands anywhere but the trunk, for a commit as for a merge: work on a branch is free and comes home reviewed
    (14 Nov 2026, the independent review found the merge path checking every branch).
    """
    if not on_trunk():
        print(f"review gate: HEAD is not {TRUNK}, so this lands nothing; the branch is reviewed when it comes home")
        return 0
    diff = landing_diff(incoming)
    if not diff.strip():
        print(f"review gate: {what_lands(incoming)} is empty, so there is nothing to review")
        return 0
    digest = digest_of(diff)
    found = review_of(digest)
    if found is None:
        print(f"review gate: {what_lands(incoming)} ({digest}, {len(files_landing(incoming))} file(s)) has no independent "
              "review.\n  Have a fresh reviewer read it, then: python tools/review_gate.py record --reviewer <agent id> "
              "--findings <n> --verdict <what was done>"
              + (f" --incoming {incoming}" if incoming else "")
              + "\n  The rule is the user's, 14 Nov 2026: a change is reviewed before it joins the trunk.")
        return 1
    print(f"review gate: {digest} reviewed by {found['reviewer']} ({found['findings']} finding(s)): {found['verdict']}")
    return 0


def record(reviewer: str, findings: int, verdict: str, note: str | None, incoming: str | None) -> int:
    diff = landing_diff(incoming)
    if not diff.strip():
        raise SystemExit(f"{what_lands(incoming)} is empty: there is no change to record a review of")
    if findings < 0:
        raise SystemExit(f"findings {findings}: a count, never negative")
    entry = {"digest": digest_of(diff), "date": time.strftime("%Y-%m-%d %H:%M"), "reviewer": reviewer,
             "findings": findings, "verdict": verdict, "files": files_landing(incoming), "lands": what_lands(incoming)}
    if note:
        entry["note"] = note
    with RECORDS.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"review gate: recorded {entry['digest']} reviewed by {reviewer}, {findings} finding(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="what", required=True)
    sub.add_parser("on-trunk", help=f"exit 0 when HEAD is {TRUNK}")
    for name, help_text in (("digest", "print the digest of what would land"),
                            ("check", "exit 1 when what would land has no review on record"),
                            ("record", "write the review of what would land")):
        p = sub.add_parser(name, help=help_text)
        p.add_argument("--incoming", help=f"the ref a merge or a pull would bring onto {TRUNK}; omit it for the staged diff")
        if name == "record":
            p.add_argument("--reviewer", required=True, help="the independent reviewer: a fresh agent's id, or a person's name")
            p.add_argument("--findings", type=int, required=True, help="how many findings it reported")
            p.add_argument("--verdict", required=True, help="what was done with them, in one line")
            p.add_argument("--note", help="anything a later reader would want")
    a = ap.parse_args(argv)
    if a.what == "on-trunk":
        return 0 if on_trunk() else 1
    if a.what == "digest":
        print(digest_of(landing_diff(a.incoming)))
        return 0
    if a.what == "check":
        return check(a.incoming)
    return record(a.reviewer, a.findings, a.verdict, a.note, a.incoming)


if __name__ == "__main__":
    sys.exit(main())
