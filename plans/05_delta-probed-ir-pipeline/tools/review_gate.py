"""Code and tests are reviewed by an independent reviewer before they join the trunk (the user, 14 and 16 November 2026).

The review is of the whole change, once, at the point where it would become part of what we have - not of every commit on the way
there. Work on a branch is free. A hook cannot perform a review; it can only refuse the move of the trunk that would land an
unreviewed change. This module is the one implementation of that decision; `tools/install_git_hooks.py` installs the two small
shims that call it.

**Where the check sits.** In git's own `reference-transaction` hook, state `prepared` (githooks(5), section "reference-transaction",
https://git-scm.com/docs/githooks#_reference_transaction: the hook reads `<old-value> SP <new-value> SP <ref-name> LF` lines on
stdin and a non-zero exit in the prepared state aborts the transaction). Every update of the trunk ref passes there however the
command was written and whoever typed it: commit, amend, merge, pull, fast-forward, rebase, cherry-pick, am, reset, branch -f,
update-ref, fetch into the trunk, a push into this repository. The old value on stdin is all zeros when the caller named none
(`git update-ref <ref> <new>`), so the gate reads the trunk's present value itself. `pre-push` is the same decision for a remote's
trunk, which no local ref transaction sees: what is pushed there must already be on the local trunk, or be a reviewed landing.

**What is reviewed** (the user, 16 Nov 2026: only code and tests). `review_gate.json`, beside this file, is the one place: the
trunk, the `log_only` switch and the reviewed set, validated when it is read. A path is reviewed when a class under `reviewed`
matches it and nothing under `never_reviewed` does; everything else lands without a record. The classes and why:
  code            what runs: Python (tests included), shell, PowerShell and cmd scripts, C, Lean, the website's source
  notebooks       the modules' notebooks are delivered code; a re-run that only changes outputs asks for a review too - the price
  patches         applied to third-party libraries before a run, so they are code
  run specs       a spec names the command a multi-day run executes and the lines that prove its progress
  tooling config  pyproject, pre-commit, CI workflows, the Claude hooks' settings, the guard's mode, requirements, this gate's own
                  configuration - a line there changes what every other check does
  agent rules     the root CLAUDE.md: every session works under it
`never_reviewed` wins over every class: run outputs (`**/out/**`), fetched results (`probes/results_m1/**`, which holds copies of
scripts as they ran), the ledger and notes (`GoalGathering/**`), the task board and the tracked review log.

**The key.** A review belongs to a pair of code states: the reviewed paths of the trunk it lands on, and the reviewed paths of
what the trunk would then hold - each a digest over (path, mode, blob) of every reviewed path in that tree. Both are read from
git objects, so the key is reproducible; a record cannot be replayed onto other code, because the key names the code before as
well as after; and a task-board row staged beside reviewed code, or a notes-only commit landing in between, does not make a
review stale. Equal digests mean no reviewed path changes, which is decision (b) itself.

**The records.** `<git common dir>/review-gate/records.jsonl`, one JSON line per review, shared by every worktree and outside any
tree - a record tracked in the tree could never name the tree that contains it. `tools/reviews.jsonl` is the tracked copy for
later readers, written by `export` after the fact; nothing reads it back. `decisions.log` beside the records takes one line per
judged move of the trunk.

    python tools/review_gate.py status [--staged | --merge <ref> | --tip <ref> | --unseen]   what lands, its reviewed paths, its key
    python tools/review_gate.py check  [--staged | --merge <ref> | --tip <ref> | --unseen]   exit 1 when it would be refused
    python tools/review_gate.py record [...] --reviewer <id> --findings <n> --verdict <text> [--note <text>] [--key <key>]
    python tools/review_gate.py hook reference-transaction <state> | hook pre-push    what the shims call, updates on stdin
    python tools/review_gate.py repair                                              set malformed record lines aside
    python tools/review_gate.py export                                              copy the records into tools/reviews.jsonl

`--staged` is a commit while HEAD is the trunk, `--merge` a merge or pull of <ref> into it (a fast-forward when it can be one),
`--tip` the trunk pointed straight at <ref> (reset, branch -f, push), `--unseen` a move of the trunk that no hook saw.

**What no hook sees.** git's files backend writes a copied or renamed branch without any ref transaction (tested on git 2.56:
`git branch -C <branch> <trunk>` fires nothing, `-M` only the deletion of the trunk), and a call with `-c core.hooksPath=...` or
an edit under `.git` runs no hook at all. So every judged move is written to `decisions.log` with the trunk's commit before
and after, and the next hook compares: a trunk that is not where the last judged move left it was moved unseen, and that move
is judged first, from the commit the gate last knew - like any landing, with `record --unseen` as its record. Until it has
one, no further move of the trunk and no push of it passes. `install` writes the first line, so the gate starts from the trunk
as it is.

**Decisions a reader should know.**
* Moving the trunk back to one of its own ancestors is allowed and logged: an undo lands nothing that was not there.
* Deleting the trunk lands nothing and is logged. Refusing it would do harm: `git branch -M <branch> <trunk>` deletes
  <branch> before it asks about the trunk and does not put it back when refused (tested); the renamed trunk is caught as an
  unseen move instead. Creating the trunk is a landing onto no code at all. Making it a symbolic ref is refused: later moves
  would no longer name it.
* It fails closed. A git that does not answer, an unreadable configuration, a malformed line in the records or in the
  decisions log, or a crash refuses the move with the reason. Both files live outside every tree, so mending them needs no
  landing: `repair` moves bad record lines to `records.rejected.jsonl`, and a bad line of `decisions.log` is deleted by hand
  (the message names it). A landing that changes no reviewed path never opens the records at all.
* `log_only` in `review_gate.json` is the one switch: while it is true the gate judges, logs and prints what it would refuse, and
  refuses nothing.

**Limits, stated rather than hidden.** Independence is asserted, not verified: the record names the reviewer. A hook is local:
a move made past it is caught at the next move it does see, not when it happens, and not at all in a clone without the
shims or after `decisions.log` is removed; `install_git_hooks.py check` says whether the shims are in place. A refusal comes
after git has built what it would land: a refused fast-forward, pull or reset leaves the index and the working tree changed,
and `check` before the command avoids that. A commit made elsewhere is judged when it arrives on the local trunk.
"""
from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path

CONFIG = Path(__file__).with_suffix(".json")
TRACKED_LOG = Path(__file__).with_name("reviews.jsonl")
STATE_DIR = "review-gate"            # under git's common directory, shared by every worktree
RECORDS = "records.jsonl"
REJECTED = "records.rejected.jsonl"
DECISIONS = "decisions.log"
GIT_TIMEOUT_S = 30                   # every git call the gate makes; a git that hangs is a refusal with this reason, not a hung hook
ID_LENGTH = 20                       # hex digits kept of each code-state digest
RECORD_FIELDS = ("key", "reviewer", "findings", "verdict")
CONFIG_FIELDS = ("trunk", "log_only", "reviewed", "never_reviewed")
SHOWN_PATHS = 6
_TRUNK = re.compile(r"refs/heads/[A-Za-z0-9._/-]+")   # it is written into an sh hook, so nothing a shell would read


class GateError(Exception):
    """The gate cannot decide or was asked something it refuses; the message is the reason."""


def _name_pattern(name: str) -> str:
    return re.escape(name).replace(r"\*", "[^/]*").replace(r"\?", "[^/]")


@functools.cache
def _matcher(pattern: str) -> re.Pattern[str]:
    """A path pattern as a regular expression: `**` is any number of directories (as the last part: everything below), `*`
    and `?` stay within one name, and nothing else is special."""
    *directories, last = pattern.split("/")
    parts = ["(?:[^/]+/)*" if d == "**" else _name_pattern(d) + "/" for d in directories]
    parts.append(".+" if last == "**" else _name_pattern(last))
    return re.compile("".join(parts))


def _patterns(label: str, value: object) -> tuple[str, ...]:
    """A validated list of path patterns: repository-relative, forward slashes, `**` for any depth."""
    if not isinstance(value, list) or not all(isinstance(p, str) for p in value):
        raise GateError(f"{label}: a list of path patterns is expected, not {value!r}")
    for pattern in value:
        parts = pattern.split("/")
        if "\\" in pattern or not all(parts) or any("**" in part and part != "**" for part in parts):
            raise GateError(f"{label}: '{pattern}' is not a repository-relative pattern: forward slashes, no empty part, "
                            "and ** only as a whole part")
    return tuple(value)


@dataclass(frozen=True)
class GateConfig:
    """The trunk, the one switch and the reviewed set, checked before anything is judged."""

    trunk: str
    log_only: bool
    reviewed: dict[str, tuple[str, ...]]
    never_reviewed: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.trunk, str) or not _TRUNK.fullmatch(self.trunk):
            raise GateError(f"trunk {self.trunk!r}: a full branch ref is expected, like refs/heads/master")
        if not isinstance(self.log_only, bool):
            raise GateError(f"log_only {self.log_only!r}: true or false is expected")
        if not self.reviewed or not all(self.reviewed.values()):
            raise GateError("reviewed: at least one class, and no class without a pattern - an empty set would review nothing")

    def reviewed_class(self, path: str) -> str | None:
        """The class a path is reviewed under, or None; an exclusion wins over every class."""
        if any(_matcher(p).fullmatch(path) for p in self.never_reviewed):
            return None
        return next((label for label, patterns in self.reviewed.items()
                     if any(_matcher(p).fullmatch(path) for p in patterns)), None)


def load_config(path: Path = CONFIG) -> GateConfig:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise GateError(f"{path}: the gate's configuration cannot be read: {e}") from e
    if not isinstance(raw, dict) or sorted(raw) != sorted(CONFIG_FIELDS):
        raise GateError(f"{path}: exactly the fields {', '.join(CONFIG_FIELDS)} are expected")
    if not isinstance(raw["reviewed"], dict):
        raise GateError(f"{path}: reviewed is expected as class name -> list of patterns")
    reviewed = {label: _patterns(f"reviewed.{label}", patterns) for label, patterns in raw["reviewed"].items()}
    return GateConfig(raw["trunk"], raw["log_only"], reviewed, _patterns("never_reviewed", raw["never_reviewed"]))


@dataclass(frozen=True)
class Review:
    """What a reviewer reports back, checked before it is written."""

    reviewer: str
    findings: int
    verdict: str
    note: str | None = None

    def __post_init__(self) -> None:
        if not self.reviewer.strip() or not self.verdict.strip():
            raise GateError("a review names its reviewer and says what was done with the findings")
        if self.findings < 0:
            raise GateError(f"findings {self.findings}: a count, never negative")


@dataclass(frozen=True)
class Landing:
    """A change of the trunk's reviewed code: where it comes from, the key of its review, and the reviewed paths that differ."""

    what: str
    selector: str              # the command-line form that names this landing again, for the message that asks for a record
    base: str | None           # the commit the trunk is at, None when there is no trunk yet
    tree: str                  # the commit or tree the trunk would hold
    key: str
    paths: tuple[str, ...]


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str
    key: str | None = None
    move: tuple[str | None, str | None] | None = None    # the trunk's commit before and after, for a move this hook governs


class NothingToJudge(Exception):
    """The command line asked about a landing that is none; the message says why, and the answer is exit 0."""


def code_id(entries: dict[str, str]) -> str:
    """The digest of one code state: every reviewed path with its mode and blob."""
    text = "\0".join(f"{path}\0{entries[path]}" for path in sorted(entries))
    return hashlib.sha256(text.encode("utf-8", errors="surrogateescape")).hexdigest()[:ID_LENGTH]


def _oid(value: str) -> str | None:
    """A hook's object name, None for git's all-zeros 'no object'."""
    return None if set(value) == {"0"} else value


def _short(rev: str | None) -> str:
    return rev[:10] if rev else "nothing"


def _parse_record(line: str) -> dict:
    """One record line as a dict; ValueError with what is wrong."""
    entry = json.loads(line)
    if not isinstance(entry, dict):
        raise ValueError(f"a {type(entry).__name__}, not a review")
    missing = [k for k in RECORD_FIELDS if k not in entry]
    if missing:
        raise ValueError(f"a review without {', '.join(missing)}")
    return entry


def _record_lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []


def read_records(path: Path) -> list[dict]:
    """Every review on record. A bad line is named with its number and the way out, and refuses the landing that asked."""
    out = []
    for n, line in enumerate(_record_lines(path), start=1):
        try:
            out.append(_parse_record(line))
        except ValueError as e:
            raise GateError(f"{path}: record {n} is not a review ({e}). `python tools/review_gate.py repair` sets such lines "
                            f"aside in {REJECTED} and keeps the rest; the file is outside every tree, so mending it lands "
                            "nothing.") from e
    return out


def _replace_text(path: Path, text: str) -> None:
    """The whole new text to a temp file, then moved over the target: a reader never sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _unreviewed(landing: Landing) -> str:
    shown = ", ".join(landing.paths[:SHOWN_PATHS]) + (", ..." if len(landing.paths) > SHOWN_PATHS else "")
    read = f"`git diff {landing.base} {landing.tree}`" if landing.base else f"everything in {landing.tree}"
    return (f"{landing.what} changes {len(landing.paths)} reviewed path(s) ({shown}) and has no review on record "
            f"(key {landing.key}).\n"
            f"  Have a fresh reviewer read {read} over those paths (`review_gate.py status {landing.selector}` lists them), "
            "answer the findings, then:\n"
            f"  python tools/review_gate.py record {landing.selector} --key {landing.key} --reviewer <id> --findings <n> "
            "--verdict <one line>\n"
            "  and repeat the command. git may already have put the refused content into the index and the working tree (a "
            "fast-forward, a pull and a reset do): `git status` shows it, and `git reset --hard HEAD` takes it out again, "
            "with any uncommitted work of your own.\n"
            "  The user, 14 and 16 Nov 2026: code and tests are reviewed before they join the trunk.")


@dataclass(frozen=True)
class Gate:
    """The decision, for the repository git finds from `cwd` (None: the process's own directory and git environment)."""

    config: GateConfig
    cwd: Path | None = None

    # ------------------------------------------------------------ reading the repository

    def git(self, *args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
        try:
            done = subprocess.run(["git", *args], cwd=self.cwd, capture_output=True, text=True, encoding="utf-8",
                                  errors="surrogateescape", timeout=GIT_TIMEOUT_S, check=False)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise GateError(f"git {' '.join(args)} did not run: {e}") from e
        if done.returncode not in ok:
            raise GateError(f"git {' '.join(args)} failed (exit {done.returncode}): {done.stderr.strip()[-300:]}")
        return done

    def state_file(self, name: str) -> Path:
        common = self.git("rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip()
        return Path(common) / STATE_DIR / name

    def commit_of(self, rev: str) -> str | None:
        """The commit a revision names, None when it names nothing."""
        return self.git("rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", ok=(0, 1)).stdout.strip() or None

    def named_commit(self, ref: str) -> str:
        commit = self.commit_of(ref)
        if commit is None:
            raise GateError(f"'{ref}' names no commit in this repository")
        return commit

    def is_ancestor(self, older: str, newer: str) -> bool:
        return self.git("merge-base", "--is-ancestor", older, newer, ok=(0, 1)).returncode == 0

    def reviewed_entries(self, treeish: str | None) -> dict[str, str]:
        """path -> 'mode type blob' for every reviewed path of a tree; no tree has none."""
        if treeish is None:
            return {}
        entries = {}
        for item in self.git("ls-tree", "-r", "-z", "--full-tree", treeish).stdout.split("\0"):
            meta, tab, path = item.partition("\t")
            if tab and self.config.reviewed_class(path):
                entries[path] = meta
        return entries

    # ------------------------------------------------------------ what would land

    def landing(self, base: str | None, tree: str, what: str, selector: str) -> Landing:
        before, after = self.reviewed_entries(base), self.reviewed_entries(tree)
        paths = tuple(sorted(p for p in before.keys() | after.keys() if before.get(p) != after.get(p)))
        return Landing(what, selector, base, tree, f"{code_id(before)}..{code_id(after)}", paths)

    def staged(self) -> Landing | None:
        """A commit of the index while HEAD is the trunk; None when HEAD is elsewhere and a commit lands nothing."""
        if self.git("symbolic-ref", "--quiet", "HEAD", ok=(0, 1)).stdout.strip() != self.config.trunk:
            return None
        tree = self.git("write-tree").stdout.strip()
        return self.landing(self.commit_of(self.config.trunk), tree, f"the staged index, committed on {self.config.trunk}",
                            "--staged")

    def merged(self, ref: str) -> Landing:
        """A merge or a pull of `ref` into the trunk: its tip when the trunk can fast-forward, the merged tree otherwise."""
        trunk, tip = self.commit_of(self.config.trunk), self.named_commit(ref)
        if trunk is None or self.is_ancestor(trunk, tip):
            return self.landing(trunk, tip, f"a fast-forward of {self.config.trunk} to {ref}", f"--merge {ref}")
        done = self.git("merge-tree", "--write-tree", trunk, tip, ok=(0, 1))
        if done.returncode == 1:
            raise GateError(f"{ref} does not merge into {self.config.trunk} without conflicts, so what would land is not known "
                            "yet: start the merge, resolve, stage, and ask again with --staged")
        return self.landing(trunk, done.stdout.split()[0], f"a merge of {ref} into {self.config.trunk}", f"--merge {ref}")

    def pointed_at(self, ref: str) -> Landing:
        """The trunk set to `ref` as it is: reset, branch -f, update-ref, a push."""
        return self.landing(self.commit_of(self.config.trunk), self.named_commit(ref), f"{self.config.trunk} pointed at {ref}",
                            f"--tip {ref}")

    # ------------------------------------------------------------ the decision

    def review_of(self, key: str) -> dict | None:
        """The last review recorded for a key."""
        return next((r for r in reversed(read_records(self.state_file(RECORDS))) if r["key"] == key), None)

    def judge_landing(self, landing: Landing) -> Verdict:
        if not landing.paths:
            return Verdict(True, f"{landing.what}: no reviewed path changes, so no review is asked")
        found = self.review_of(landing.key)
        if found is None:
            return Verdict(False, _unreviewed(landing), landing.key)
        return Verdict(True, f"{landing.what}: reviewed by {found['reviewer']} ({found['findings']} finding(s)): "
                             f"{found['verdict']}", landing.key)

    def judge_move(self, old: str | None, new: str | None, selector: str | None = None) -> Verdict:
        """A move of the trunk from commit `old` to `new`, as a ref transaction or a push reports it."""
        trunk = self.config.trunk
        if old == new:
            return Verdict(True, f"{trunk} stays at {_short(new)}")
        if new is None:
            return Verdict(True, f"{trunk} is deleted at {_short(old)}: nothing lands")
        if new.startswith("ref:"):
            return Verdict(False, f"{trunk} would become a symbolic ref ({new}); later moves of the trunk would not name it, so "
                                  "the gate could not see them")
        if old and self.is_ancestor(new, old):
            return Verdict(True, f"{trunk} moves back from {_short(old)} to its own ancestor {_short(new)}: an undo lands "
                                 "nothing that was not there")
        return self.judge_landing(self.landing(old, new, f"{trunk} moving {_short(old)} -> {_short(new)}",
                                               selector or f"--tip {new}"))

    # ------------------------------------------------------------ a move no hook saw

    def last_seen(self) -> tuple[str | None, str | None] | None:
        """The trunk's commit before and after the last move a hook judged here; None before the first."""
        path = self.state_file(DECISIONS)
        lines = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        for n in range(len(lines), 0, -1):
            try:
                entry = json.loads(lines[n - 1])
            except ValueError as e:
                raise GateError(f"{path}: line {n} is not a decision ({e}), so where the gate last left {self.config.trunk} "
                                "is not known. Delete that line; the file is outside every tree.") from e
            if isinstance(entry, dict) and entry.get("trunk") == self.config.trunk:
                return entry["trunk_before"], entry["trunk_after"]
        return None

    def unseen_move(self) -> tuple[str | None, str | None] | None:
        """(the commit the gate last knew, the trunk now) when the trunk is not where the last judged move left it."""
        seen, now = self.last_seen(), self.commit_of(self.config.trunk)
        if seen is None or now in seen:
            return None
        return seen[1] or seen[0], now           # after a deletion the last commit the trunk had is the one to compare with

    def unseen(self) -> Landing | None:
        """The unseen move as a landing, for the command line; None when there is none."""
        move = self.unseen_move()
        if move is None:
            return None
        if move[1] is None:
            raise GateError(f"{self.config.trunk} was deleted without this hook: there is no trunk to judge")
        return self.landing(move[0], move[1], f"{self.config.trunk} moved {_short(move[0])} -> {_short(move[1])} unseen",
                            "--unseen")

    def judge_unseen(self) -> Verdict | None:
        """The verdict on a move of the trunk no hook saw; None when the trunk is where the gate left it."""
        move = self.unseen_move()
        if move is None:
            return None
        inner = self.judge_move(move[0], move[1], "--unseen")
        lead = (f"{self.config.trunk} was moved {_short(move[0])} -> {_short(move[1])} without this hook (a branch copied or "
                "renamed over it, hooks switched off, an edit under .git), and that move is judged before any other. ")
        return replace(inner, reason=lead + inner.reason)

    def after_unseen(self, judge: Callable[[], list[Verdict]]) -> list[Verdict]:
        """The verdicts of `judge`, behind the one on an unseen move - alone when the gate refuses that one."""
        unseen = self.judge_unseen()
        if unseen is None:
            return judge()
        if not unseen.allowed and not self.config.log_only:
            return [unseen]
        return [unseen, *judge()]

    def baseline(self, hook: str) -> bool:
        """Start the journal from the trunk as it is, unless it has a line for this trunk already; whether it was written."""
        if self.last_seen() is not None:
            return False
        now = self.commit_of(self.config.trunk)
        self.log(hook, Verdict(True, f"the gate starts from {self.config.trunk} at {_short(now)}", move=(now, now)), lands=True)
        return True

    def judge_push(self, new: str | None, remote_old: str | None) -> Verdict:
        """A push to a remote's trunk: free for what the local trunk already holds, a landing like any other for the rest."""
        local = self.commit_of(self.config.trunk)
        if new and local and self.is_ancestor(new, local):
            return Verdict(True, f"push of {_short(new)} to a remote's {self.config.trunk}: it is on the local trunk, where the "
                                 "gate read it")
        if remote_old and self.commit_of(remote_old) is None:
            return Verdict(False, f"push to a remote's {self.config.trunk}: its present commit {_short(remote_old)} is not in "
                                  "this repository, so what the push would change cannot be read. Fetch first.")
        return self.judge_move(remote_old, new)

    # ------------------------------------------------------------ the hooks

    def on_reference_transaction(self, state: str, updates: str) -> list[Verdict]:
        """One verdict per update of the trunk in a prepared transaction; the trunk's present value is read here, because
        stdin carries zeros for an update whose caller named no old value."""
        if state != "prepared":
            return []
        targets = [parts[1] for line in updates.splitlines() if len(parts := line.split(" ")) == 3
                   and parts[2] == self.config.trunk]
        if not targets:
            return []
        old = self.commit_of(self.config.trunk)
        moves = [new for new in map(_oid, targets) if new != old]
        if not moves:                            # the trunk stays where it is: `git reset --hard HEAD` must always work
            return []
        return self.after_unseen(lambda: [replace(self.judge_move(old, new), move=(old, self._commit_after(new)))
                                          for new in moves])

    def _commit_after(self, new: str | None) -> str | None:
        """The commit the trunk holds once an update lands: the journal compares commits, also for a symbolic value."""
        return self.commit_of(new.removeprefix("ref:")) if new and new.startswith("ref:") else new

    def on_pre_push(self, updates: str) -> list[Verdict]:
        """One verdict per pushed ref that lands on a remote's trunk: `<local ref> <local oid> <remote ref> <remote oid>`."""
        pushes = [(_oid(parts[1]), _oid(parts[3])) for line in updates.splitlines()
                  if len(parts := line.split(" ")) == 4 and parts[2] == self.config.trunk]
        return self.after_unseen(lambda: [self.judge_push(new, remote_old) for new, remote_old in pushes]) if pushes else []

    def log(self, hook: str, verdict: Verdict, *, lands: bool) -> None:
        """One line of the journal. A governed move also says where it leaves the trunk: at the new commit when the
        transaction goes on (`lands`), at the old one when the gate refuses it."""
        entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "hook": hook, "allowed": verdict.allowed,
                 "refused": not verdict.allowed and not self.config.log_only, "key": verdict.key,
                 "reason": verdict.reason.splitlines()[0]}
        if verdict.move:
            entry.update(trunk=self.config.trunk, trunk_before=verdict.move[0],
                         trunk_after=verdict.move[1] if lands else verdict.move[0])
        path = self.state_file(DECISIONS)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")

    def settle(self, hook: str, verdicts: list[Verdict]) -> int:
        """Log every verdict, print the refusals, and give the hook's exit code: non-zero only when the gate acts."""
        refused = [v for v in verdicts if not v.allowed]
        acts = bool(refused) and not self.config.log_only
        for verdict in verdicts:
            self.log(hook, verdict, lands=not acts)
        prefix = "review gate (log only, nothing is refused): " if self.config.log_only else "review gate: "
        for verdict in refused:
            print(prefix + verdict.reason, file=sys.stderr)
        return 1 if acts else 0

    # ------------------------------------------------------------ the records

    def record(self, landing: Landing, review: Review) -> dict:
        if not landing.paths:
            raise GateError(f"{landing.what}: no reviewed path changes, so there is nothing to record a review of")
        path = self.state_file(RECORDS)
        read_records(path)                       # a malformed file is mended first, never appended to
        entry = {"key": landing.key, "date": time.strftime("%Y-%m-%d %H:%M"), "reviewer": review.reviewer,
                 "findings": review.findings, "verdict": review.verdict, "paths": list(landing.paths), "lands": landing.what}
        if review.note:
            entry["note"] = review.note
        _replace_text(path, "".join(line + "\n" for line in [*_record_lines(path), json.dumps(entry, sort_keys=True)]))
        return entry

    def repair(self) -> tuple[int, int]:
        """Move the lines that are not reviews to the rejected file; (kept, set aside)."""
        path = self.state_file(RECORDS)
        good, bad = [], []
        for line in _record_lines(path):
            try:
                _parse_record(line)
            except ValueError:
                bad.append(line)
            else:
                good.append(line)
        if bad:                                  # the rejected file first: a crash between the two writes loses nothing
            rejected = path.with_name(REJECTED)
            _replace_text(rejected, "".join(line + "\n" for line in [*_record_lines(rejected), *bad]))
            _replace_text(path, "".join(line + "\n" for line in good))
        return len(good), len(bad)

    def export(self, target: Path) -> int:
        """Add the records the tracked log does not hold yet; the number added."""
        path = self.state_file(RECORDS)
        read_records(path)
        have = _record_lines(target)
        new = [line for line in _record_lines(path) if line not in have]
        if new:
            _replace_text(target, "".join(line + "\n" for line in [*have, *new]))
        return len(new)


# ---------------------------------------------------------------- the command line

def run_hook(gate: Gate, hook: str, state: str | None, updates: str) -> int:
    """What a shim calls. Anything that keeps the gate from deciding refuses the move with the reason - unless log_only."""
    try:
        if hook == "pre-push":
            verdicts = gate.on_pre_push(updates)
        elif state is None:
            raise GateError("hook reference-transaction needs the state git passed")
        else:
            verdicts = gate.on_reference_transaction(state, updates)
        return gate.settle(hook, verdicts)
    except Exception as e:  # noqa: BLE001  fail closed: an unforeseen crash must refuse the move, not let it pass unjudged
        acting = not gate.config.log_only
        print(f"review gate{'' if acting else ' (log only, nothing is refused)'}: could not judge this move of "
              f"{gate.config.trunk}, so it is refused: {type(e).__name__}: {e}", file=sys.stderr)
        return 1 if acting else 0


def _selected(gate: Gate, a: argparse.Namespace) -> Landing:
    if a.merge:
        return gate.merged(a.merge)
    if a.tip:
        return gate.pointed_at(a.tip)
    landing = gate.unseen() if a.unseen else gate.staged()
    if landing is None and a.unseen:
        raise NothingToJudge(f"{gate.config.trunk} is where the last judged move left it: nothing moved it unseen")
    if landing is None:
        raise NothingToJudge(f"HEAD is not {gate.config.trunk}, so a commit here lands nothing; the branch is reviewed when it "
                             "comes home (--merge or --tip says what that would bring)")
    return landing


def _judged(gate: Gate, a: argparse.Namespace, landing: Landing) -> Verdict:
    """The verdict the hook would give: an unseen move first, and a --tip as the bare move of the trunk it is, so an undo
    passes there as it does at the hook."""
    unseen = gate.judge_unseen()
    if unseen is not None and (a.unseen or not unseen.allowed):
        return unseen
    return gate.judge_move(landing.base, landing.tree) if a.tip else gate.judge_landing(landing)


def _status(gate: Gate, a: argparse.Namespace, landing: Landing) -> int:
    verdict = _judged(gate, a, landing)
    print(f"review gate: {landing.what}")
    print(f"  trunk     {gate.config.trunk} at {_short(landing.base)}")
    print(f"  key       {landing.key}")
    print(f"  reviewed paths that change: {len(landing.paths)}")
    for path in landing.paths:
        print(f"    [{gate.config.reviewed_class(path)}] {path}")
    print(f"  verdict   {'passes' if verdict.allowed else 'REFUSED'}: {verdict.reason}")
    print(f"  mode      {'log_only: the hook refuses nothing yet' if gate.config.log_only else 'the hook refuses'}")
    return 0


def _check(gate: Gate, a: argparse.Namespace, landing: Landing) -> int:
    verdict = _judged(gate, a, landing)
    print(f"review gate: {verdict.reason}")
    return 0 if verdict.allowed else 1


def _record(gate: Gate, a: argparse.Namespace, landing: Landing) -> int:
    if a.key and a.key != landing.key:
        raise GateError(f"the key given, {a.key}, is not the key of {landing.what} now ({landing.key}): the code changed after "
                        "the review, and the change needs its own")
    entry = gate.record(landing, Review(a.reviewer, a.findings, a.verdict, a.note))
    print(f"review gate: recorded {entry['key']} reviewed by {entry['reviewer']}, {entry['findings']} finding(s), "
          f"{len(entry['paths'])} reviewed path(s)")
    return 0


_LANDING_COMMANDS = {"status": _status, "check": _check, "record": _record}


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="what", required=True)
    about = {"status": "what would land on the trunk, its reviewed paths and its key",
             "check": "exit 1 when what would land would be refused", "record": "write the review of what would land"}
    parsers = {name: sub.add_parser(name, help=text) for name, text in about.items()}
    for parser in parsers.values():
        which = parser.add_mutually_exclusive_group()
        which.add_argument("--staged", action="store_true", help="a commit of the index on the trunk (the default)")
        which.add_argument("--merge", metavar="REF", help="a merge or a pull of REF into the trunk")
        which.add_argument("--tip", metavar="REF", help="the trunk pointed straight at REF")
        which.add_argument("--unseen", action="store_true", help="a move of the trunk that no hook saw")
    p = parsers["record"]
    p.add_argument("--reviewer", required=True, help="the independent reviewer: a fresh agent's id, or a person's name")
    p.add_argument("--findings", type=int, required=True, help="how many findings it reported")
    p.add_argument("--verdict", required=True, help="what was done with them, in one line")
    p.add_argument("--note", help="anything a later reader would want")
    p.add_argument("--key", help="the key the reviewer was given; refused when the code has changed since")
    hook = sub.add_parser("hook", help="what the installed shims call, with the updates on stdin")
    hook.add_argument("hook", choices=("reference-transaction", "pre-push"))
    hook.add_argument("rest", nargs="*", help="reference-transaction: the state; pre-push: the remote's name and URL")
    sub.add_parser("repair", help=f"move malformed record lines to {REJECTED}")
    export = sub.add_parser("export", help="add the records to the tracked log, for later readers")
    export.add_argument("--to", type=Path, default=TRACKED_LOG, help="the tracked log (default: %(default)s)")
    return ap


def _dispatch(gate: Gate, a: argparse.Namespace) -> int:
    if a.what == "repair":
        kept, aside = gate.repair()
        print(f"review gate: {kept} record(s) kept, {aside} malformed line(s) moved to {gate.state_file(REJECTED)}")
        return 0
    if a.what == "export":
        print(f"review gate: {gate.export(a.to)} record(s) added to {a.to}")
        return 0
    try:
        landing = _selected(gate, a)
    except NothingToJudge as e:
        print(f"review gate: {e}")
        return 0
    return _LANDING_COMMANDS[a.what](gate, a, landing)


def main(argv: list[str] | None = None) -> int:
    a = _parser().parse_args(argv)
    for stream in (sys.stdout, sys.stderr):      # a path git reports may hold what the console cannot encode
        stream.reconfigure(errors="backslashreplace")
    try:
        gate = Gate(load_config())
        if a.what == "hook":
            state = a.rest[0] if a.hook == "reference-transaction" and a.rest else None
            return run_hook(gate, a.hook, state, sys.stdin.read())
        return _dispatch(gate, a)
    except GateError as e:
        print(f"review gate: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
