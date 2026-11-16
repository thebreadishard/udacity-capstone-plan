"""Code and tests are reviewed by an independent reviewer before they join the trunk (the user, 14 and 16 November 2026).

The review is of the whole change, once, at the point where it would become part of what we have - not of every commit on the way
there. Work on a branch is free. A hook cannot perform a review; it can only refuse the move of the trunk that would land an
unreviewed change. This module is the one implementation of that decision; `tools/install_git_hooks.py` installs the two small
shims that call it.

**Where the check sits.** In git's own `reference-transaction` hook, state `prepared` (githooks(5), section "reference-transaction",
https://git-scm.com/docs/githooks#_reference_transaction: the hook reads `<old-value> SP <new-value> SP <ref-name> LF` lines on
stdin and a non-zero exit in the prepared state aborts the transaction). An update of the trunk ref passes there however the
command was written and whoever typed it: commit, amend, merge, pull, fast-forward, rebase, cherry-pick, am, reset, branch -f,
update-ref, fetch into the trunk, a push into this repository. The old value on stdin is all zeros when the caller named none
(`git update-ref <ref> <new>`), so the gate reads the trunk's present value itself. `pre-push` is the same decision for a remote's
trunk, which no local ref transaction sees: what is pushed there is the local trunk, a commit the trunk has held, or a reviewed
landing.

**What is reviewed** (the user, 16 Nov 2026: only code and tests). `review_gate.json`, beside this file, is the one place: the
trunk, the `log_only` switch and the reviewed set, validated when it is read. **The hook reads it from the trunk commit the move
starts from**, never from the working tree, so a change of the set or of the switch is itself a landing that is judged by the
configuration before it. A trunk that holds no configuration yet (it does not exist, or the gate has not landed on it) is judged
by the file beside this module; `install` refuses such a trunk, so that case is a repository in repair. A path is reviewed when a
class under `reviewed` matches it and nothing under `never_reviewed` does; everything else lands without a record:
  code            what runs: Python (tests included), shell, PowerShell and cmd scripts, C, Lean, the website's source
  notebooks       the modules' notebooks are delivered code; a re-run that only changes outputs asks for a review too - the price
  patches         applied to third-party libraries before a run, so they are code
  test data       `tests/data/**`: a pinned expectation is half of its test
  tooling config  pyproject, requirements and environment lists, the Lean lakefile, .gitattributes, pre-commit, CI workflows,
                  the Claude hooks' settings, everything under tools/hooks, this gate's own configuration - a line there
                  changes what every other check does
  agent rules     the root CLAUDE.md: every session works under it
Not reviewed by the user's decision: run specs and chain files (launch records, validated by the runspec schema at launch).
`never_reviewed` wins over every class: run outputs (`**/out/**`), fetched results (`probes/results_m1/**`), the ledger and
notes (`GoalGathering/**`), the task board and the tracked review log. Accepted limit: a code-like file under `out/` or
`results_m1/` lands unreviewed (those hold copies of scripts as they ran); a script that a run or a tool executes never lives
there.

**The key.** A review belongs to a pair of code states: the reviewed paths of the trunk it lands on, and the reviewed paths of
what the trunk would then hold - each a digest over (path, mode, blob) of every reviewed path in that tree. Both are read from
git objects, with replacement refs switched off (`GIT_NO_REPLACE_OBJECTS`), so the key is reproducible; a record cannot be
replayed onto other code, because the key names the code before as well as after; and a task-board row staged beside reviewed
code, or a notes-only commit landing in between, does not make a review stale. The decision reads trees, the journal and the
records, never ancestry, so grafts and a shallow boundary cannot bend it.

**The records.** `<git common dir>/review-gate/records.jsonl`, one JSON line per review, shared by every worktree and outside any
tree - a record tracked in the tree could never name the tree that contains it. `tools/reviews.jsonl` is the tracked copy for
later readers, written by `export` after the fact; nothing reads it back. `decisions.log` beside the records is the journal: one
line per judged move, with the trunk's commit before and after. Both are appended under a lock file; a lock left by a process
that died is broken once it is a minute old, and `locks.log` says so.

    python tools/review_gate.py status [--staged | --merge <ref> | --tip <ref> | --unseen]   what lands, its reviewed paths, its key
    python tools/review_gate.py check  [--staged | --merge <ref> | --tip <ref> | --unseen]   exit 1 when it would be refused
    python tools/review_gate.py record [...] --reviewer <id> --findings <n> --verdict <text> [--note <text>] [--key <key>]
    python tools/review_gate.py hook <name> --trunk <ref> [...]                     what the shims call, updates on stdin
    python tools/review_gate.py repair                                              set malformed record and journal lines aside
    python tools/review_gate.py export                                              copy the records into tools/reviews.jsonl

`--staged` is a commit while HEAD is the trunk, `--merge` a merge or pull of <ref> into it (a fast-forward when it can be one),
`--tip` the trunk pointed straight at <ref> (reset, branch -f, push), `--unseen` a move of the trunk that no hook saw.

**What no hook sees.** git's files backend writes a copied or renamed branch without any ref transaction (tested on git 2.56:
`git branch -C <branch> <trunk>` fires nothing, `-M` only the deletion of the trunk), and a call with `-c core.hooksPath=...` or
an edit under `.git` runs no hook at all. So the next hook compares: a trunk that is not where the journal's last line left it
was moved unseen, and that move is judged first, from the commit the gate last knew - like any landing, with `record --unseen`
as its record, and under the configuration of that last known commit, not the one the unseen move brought. Until it has
one, no further move of the trunk and no push of it passes, except a move back to a commit the gate let the trunk onto.
`install` writes a baseline line - the first one, and again when the journal left the trunk on a commit it does not hold
(what landed under log_only) - so the gate starts from the trunk as it stands.

**Decisions a reader should know.**
* The trunk may always move to a commit the gate itself let it onto (a journal line marked `held`): an undo lands nothing
  that was not there. Being an ancestor is not enough - `git merge -s ours <branch>` makes any branch an ancestor without
  landing a line of it - and neither is having been found on the trunk: a commit that arrived unseen, or landed only
  because of log_only, is judged like any other when the trunk goes there again.
* Deleting the trunk lands nothing and is logged. Refusing it would do harm: `git branch -M <branch> <trunk>` deletes
  <branch> before it asks about the trunk and does not put it back when refused (tested); the renamed trunk is caught as an
  unseen move instead. Creating the trunk is a landing onto no code at all. Making it a symbolic ref is refused: later moves
  would no longer name it.
* It fails closed. A git that does not answer, an unreadable configuration, a malformed line in the records or the journal, or
  a crash refuses the move with the reason; `repair` sets the bad lines of both files aside, and both live outside every tree,
  so mending them needs no landing. A landing that changes no reviewed path never opens the records at all.
* `log_only` in `review_gate.json` is the one switch: while the trunk's configuration says true the gate judges, logs and prints
  what it would refuse, and refuses nothing - also when the installation is broken (the shim then reads the same line itself).
* Exit codes of `hook`: 0 lets the move pass, 3 refuses it; anything else is a gate that could not run, which the shim treats
  as a broken installation.

**Limits, stated rather than hidden.** Independence is asserted, not verified: the record names the reviewer. A hook is local:
a move made past it is caught at the next move it does see, not when it happens, and not at all in a clone without the shims or
after `decisions.log` is removed; `install_git_hooks.py check` says whether the shims are in place. `git push --no-verify`
skips `pre-push`, and a remote runs none of this: the remote's trunk is protected only by the guard's rule against that flag
and by what the remote itself enforces. A refusal comes after git has built what it would land, so a refused fast-forward or
pull leaves the index and the working tree changed (the message names the command that puts them back); `check` before the
command avoids that. A commit made elsewhere is judged when it arrives on the local trunk. The shim runs this file from the
main checkout's working tree, so an uncommitted edit of it changes the gate: running the trunk's copy instead would put a git
call and a cache in front of every trunk move and take away the way to try a mended gate before it lands, while the file is a
reviewed path and an edit of it shows in `git status`. If this file does not compile, `install_git_hooks.py` cannot be
imported either: restore the file (`git checkout -- tools/review_gate.py`) before `uninstall`.
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

CONFIG = Path(__file__).resolve().with_suffix(".json")
TRACKED_LOG = Path(__file__).with_name("reviews.jsonl")
STATE_DIR = "review-gate"            # under git's common directory, shared by every worktree
RECORDS = "records.jsonl"
DECISIONS = "decisions.log"
REJECTED = {RECORDS: "records.rejected.jsonl", DECISIONS: "decisions.rejected.log"}
GIT_TIMEOUT_S = 30                   # every git call the gate makes; a git that hangs is a refusal with this reason, not a hung hook
LOCK_WAIT_S = 10
LOCK_STALE_S = 60                    # nothing the gate does under a lock takes a second
ID_LENGTH = 20                       # hex digits kept of each code-state digest
RECORD_FIELDS = ("key", "reviewer", "findings", "verdict")
CONFIG_FIELDS = ("trunk", "log_only", "reviewed", "never_reviewed")
SHOWN_PATHS = 6
REFUSED = 3                          # the hook's exit code for a refusal, apart from every code a crash can give
BROKEN = 2
_TRUNK = re.compile(r"refs/heads/[A-Za-z0-9._/-]+")   # it is written into an sh hook, so nothing a shell would read


class GateError(Exception):
    """The gate cannot decide or was asked something it refuses; the message is the reason."""


class NothingToJudge(Exception):
    """The command line asked about a landing that is none; the message says why, and the answer is exit 0."""


# ---------------------------------------------------------------- the configuration

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


def _no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """json keeps the last of two equal keys, and the shim's grep finds the first: `log_only` written twice would be one
    thing to the gate and another to the shim. Such a file is no configuration."""
    keys = [key for key, _ in pairs]
    twice = sorted({key for key in keys if keys.count(key) > 1})
    if twice:
        raise ValueError(f"the key {', '.join(twice)} is there more than once")
    return dict(pairs)


def parse_config(text: str, source: str) -> GateConfig:
    try:
        raw = json.loads(text, object_pairs_hook=_no_duplicate_keys)
    except ValueError as e:
        raise GateError(f"{source}: the gate's configuration cannot be read: {e}") from e
    if not isinstance(raw, dict) or sorted(raw) != sorted(CONFIG_FIELDS):
        raise GateError(f"{source}: exactly the fields {', '.join(CONFIG_FIELDS)} are expected")
    if not isinstance(raw["reviewed"], dict):
        raise GateError(f"{source}: reviewed is expected as class name -> list of patterns")
    reviewed = {label: _patterns(f"reviewed.{label}", patterns) for label, patterns in raw["reviewed"].items()}
    return GateConfig(raw["trunk"], raw["log_only"], reviewed, _patterns("never_reviewed", raw["never_reviewed"]))


def load_config(path: Path = CONFIG) -> GateConfig:
    """The configuration as a file holds it: the delivered set, and the fallback for a trunk that has none."""
    try:
        return parse_config(path.read_text(encoding="utf-8"), str(path))
    except OSError as e:
        raise GateError(f"{path}: the gate's configuration cannot be read: {e}") from e


# ---------------------------------------------------------------- git, and the configuration the trunk holds

_NAMES_A_REPOSITORY = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE", "GIT_PREFIX")


def run_git(cwd: Path | None, *args: str, ok: tuple[int, ...] = (0,), own_checkout: bool = False,
            ) -> subprocess.CompletedProcess[str]:
    """One git call of the gate: real objects only (no replacement refs), bounded in time, an unexpected exit is the reason.
    `own_checkout` asks about the checkout `cwd` is in, whatever repository a hook's GIT_* variables name."""
    env = {k: v for k, v in os.environ.items() if not (own_checkout and k in _NAMES_A_REPOSITORY)}
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    try:
        done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="surrogateescape", timeout=GIT_TIMEOUT_S, check=False, env=env)
    except (OSError, subprocess.TimeoutExpired) as e:
        raise GateError(f"git {' '.join(args)} did not run: {e}") from e
    if done.returncode not in ok:
        raise GateError(f"git {' '.join(args)} failed (exit {done.returncode}): {done.stderr.strip()[-300:]}")
    return done


@functools.cache
def common_dir(cwd: Path | None) -> Path:
    return Path(run_git(cwd, "rev-parse", "--path-format=absolute", "--git-common-dir").stdout.strip())


@functools.cache
def tracked_config_path() -> str:
    """The configuration's path inside the repository's trees, asked of the checkout this file is in - the main one or a
    linked worktree, the path is the same (16 Nov 2026: derived from the main checkout, it failed in every worktree)."""
    return run_git(CONFIG.parent, "rev-parse", "--show-prefix", own_checkout=True).stdout.strip() + CONFIG.name


@functools.cache
def commit_at(cwd: Path | None, rev: str) -> str | None:
    """The commit a revision names, None when it names nothing. Asked once per process: no ref moves while the gate runs."""
    return run_git(cwd, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}", ok=(0, 1)).stdout.strip() or None


def config_on(cwd: Path | None, commit: str | None, path: str) -> GateConfig | None:
    """The configuration a commit holds at `path`, None when it holds none."""
    if commit is None:
        return None
    blob = run_git(cwd, "cat-file", "blob", f"{commit}:{path}", ok=(0, 128))
    if blob.returncode == 0:
        return parse_config(blob.stdout, f"{commit[:10]}:{path}")
    if run_git(cwd, "ls-tree", "--full-tree", commit, "--", path).stdout.strip():
        raise GateError(f"{commit[:10]}:{path} is there and cannot be read: {blob.stderr.strip()[-200:]}")
    return None


def read_journal(cwd: Path | None, trunk: str) -> list[tuple[str | None, str | None, bool]]:
    """(trunk before, trunk after, held) of every move judged for this trunk, oldest first. `held` says the gate let the
    trunk onto `after`: only such a commit is one the trunk may return to."""
    return [(e["trunk_before"], e["trunk_after"], e.get("held") is True)
            for e in read_state(common_dir(cwd) / STATE_DIR / DECISIONS) if e.get("trunk") == trunk]


def last_known(journal: list[tuple[str | None, str | None, bool]]) -> str | None:
    """The commit the journal's last line left the trunk at; after a deletion, the last commit it had."""
    return journal[-1][1] or journal[-1][0]


def open_gate(cwd: Path | None = None, trunk: str | None = None, config_path: str | None = None) -> Gate:
    """The gate for the repository git finds from `cwd`, under the configuration of the commit the gate last knew the trunk
    at: the trunk itself - at a hook, the commit the move starts from - unless it was moved unseen, and then the journal's
    last commit, so that an unseen move is never judged by the configuration it brought. `trunk` and `config_path` are what
    a shim was installed with; without them the file beside this module and its own checkout say."""
    name = trunk or load_config().trunk
    if not _TRUNK.fullmatch(name):
        raise GateError(f"trunk {name!r}: a full branch ref is expected, like refs/heads/master")
    now, journal = commit_at(cwd, name), read_journal(cwd, name)
    judged_from = now if not journal or now == journal[-1][1] else last_known(journal)
    try:
        config = config_on(cwd, judged_from, config_path or tracked_config_path()) or load_config()
    except GateError as e:
        raise GateError(f"{e}\n  No move of {name} can be judged while that commit holds this configuration, the one that "
                        "would mend it included: `python tools/install_git_hooks.py uninstall`, land the mended file, "
                        "`install` again.") from e
    if config.trunk != name:
        raise GateError(f"the configuration on {name} names {config.trunk} as the trunk: land that change on {config.trunk} "
                        "too and run `python tools/install_git_hooks.py install`")
    return Gate(config, cwd)


# ---------------------------------------------------------------- reviews, records, the journal

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
    """A change of the trunk's reviewed code: where it comes from, the reviewed paths that differ, and the key of its review."""

    what: str
    selector: str              # the command-line form that names this landing again, for the message that asks for a record
    base: str | None           # the commit the trunk is at, None when there is no trunk yet
    tree: str                  # the commit or tree the trunk would hold
    paths: tuple[str, ...]
    key: str | None            # None when no reviewed path changes: such a landing has no review to look up


@dataclass(frozen=True)
class Verdict:
    allowed: bool
    reason: str
    key: str | None = None
    move: tuple[str | None, str | None] | None = None    # the trunk's commit before and after, for the journal
    happened: bool = False     # an unseen move: the trunk is there already, whatever this transaction's fate


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


def _parse_decision(line: str) -> dict:
    """One journal line as a dict; ValueError with what is wrong. A line that names a trunk says where it left it."""
    entry = json.loads(line)
    if not isinstance(entry, dict):
        raise ValueError(f"a {type(entry).__name__}, not a decision")
    if "trunk" in entry and not all(isinstance(entry.get(k), str | None) and k in entry for k in ("trunk_before", "trunk_after")):
        raise ValueError("a move of the trunk without trunk_before and trunk_after")
    return entry


_PARSERS: dict[str, Callable[[str], dict]] = {RECORDS: _parse_record, DECISIONS: _parse_decision}


def _lines(path: Path) -> list[str]:
    return [line for line in path.read_text(encoding="utf-8").splitlines() if line.strip()] if path.is_file() else []


def read_state(path: Path) -> list[dict]:
    """Every line of the records or of the journal. A bad line is named with its number and the way out, and refuses the
    move that asked."""
    out = []
    for n, line in enumerate(_lines(path), start=1):
        try:
            out.append(_PARSERS[path.name](line))
        except ValueError as e:
            raise GateError(f"{path}: line {n} is not what this file holds ({e}). `python tools/review_gate.py repair` sets "
                            f"such lines aside in {REJECTED[path.name]} and keeps the rest; the file is outside every tree, "
                            "so mending it lands nothing.") from e
    return out


def _replace_text(path: Path, text: str) -> None:
    """The whole new text to a temp file, then moved over the target: a reader never sees half a file."""
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(text, encoding="utf-8", newline="\n")
    os.replace(tmp, path)


def _take_lock(lock: Path) -> None:
    """Create the lock file exclusively. A lock older than LOCK_STALE_S was left by a process that died (a leftover lock
    cost eleven seconds and then refused every move of the trunk, 16 Nov 2026): it is broken, and `locks.log` says so."""
    deadline = time.monotonic() + LOCK_WAIT_S
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, PermissionError) as e:      # Windows answers PermissionError while the holder removes it
            if _broke_stale(lock):
                continue
            if time.monotonic() > deadline:
                raise GateError(f"{lock} has been held for {LOCK_WAIT_S} s: it is broken by itself once it is {LOCK_STALE_S} s "
                                "old, or delete it if no review_gate.py is running") from e
            time.sleep(0.02)
        else:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(f"pid {os.getpid()} since {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            return


def _broke_stale(lock: Path) -> bool:
    try:
        age = time.time() - lock.stat().st_mtime
        if age <= LOCK_STALE_S:
            return False
        holder = lock.read_text(encoding="utf-8").strip() or "nobody on record"
        lock.unlink()
    except FileNotFoundError:
        return True                              # released or broken by another process meanwhile: try again
    except OSError:
        return False                             # its holder is at work on it: wait as for any held lock
    note = f"{time.strftime('%Y-%m-%d %H:%M:%S')} broke {lock.name}, {age:.0f} s old, left by {holder}"
    with lock.with_name("locks.log").open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(note + "\n")
    print(f"review gate: {note}", file=sys.stderr)
    return True


def _append_line(path: Path, line: str) -> None:
    """One line at the end of a file that several processes write (eight parallel `record` calls lost two lines to a
    read-modify-write, 16 Nov 2026): whoever holds the lock file appends."""
    path.parent.mkdir(parents=True, exist_ok=True)
    lock = path.with_name(path.name + ".lock")
    _take_lock(lock)
    try:
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(line + "\n")
    finally:
        lock.unlink(missing_ok=True)


def _set_aside(path: Path) -> tuple[int, int]:
    """Move the lines a state file cannot hold to its rejected file; (kept, set aside)."""
    good, bad = [], []
    for line in _lines(path):
        try:
            _PARSERS[path.name](line)
        except ValueError:
            bad.append(line)
        else:
            good.append(line)
    if bad:                                      # the rejected file first: a crash between the two writes loses nothing
        rejected = path.with_name(REJECTED[path.name])
        _replace_text(rejected, "".join(line + "\n" for line in [*_lines(rejected), *bad]))
        _replace_text(path, "".join(line + "\n" for line in good))
    return len(good), len(bad)


def _unreviewed(landing: Landing) -> str:
    shown = ", ".join(landing.paths[:SHOWN_PATHS]) + (", ..." if len(landing.paths) > SHOWN_PATHS else "")
    read = f"`git diff {landing.base} {landing.tree}`" if landing.base else f"everything in {landing.tree}"
    return (f"{landing.what} changes {len(landing.paths)} reviewed path(s) ({shown}) and has no review on record "
            f"(key {landing.key}).\n"
            f"  Have a fresh reviewer read {read} over those paths (`review_gate.py status {landing.selector}` lists them), "
            "answer the findings, then:\n"
            f"  python tools/review_gate.py record {landing.selector} --key {landing.key} --reviewer <id> --findings <n> "
            "--verdict <one line>\n"
            "  and repeat the command. The user, 14 and 16 Nov 2026: code and tests are reviewed before they join the trunk.")


def _put_back(new: str) -> str:
    """What to do about the index and working tree git built before the hook refused; `git reset --hard` would also take
    uncommitted work of the user's (16 Nov 2026: the real checkout had five such files)."""
    return ("\n  If this was a fast-forward merge or a pull, git has already put the refused content into the index and the "
            f"working tree: `git read-tree -m -u {new} HEAD` takes it out again and keeps your uncommitted edits. Not after "
            "a refused commit (the staged change is your work and is still staged); a merge commit, rebase, cherry-pick or am "
            "has its own --abort.")


# ---------------------------------------------------------------- the gate

@dataclass(frozen=True)
class Gate:
    """The decision, for the repository git finds from `cwd` (None: the process's own directory and git environment)."""

    config: GateConfig
    cwd: Path | None = None

    # ------------------------------------------------------------ reading the repository

    def git(self, *args: str, ok: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess[str]:
        return run_git(self.cwd, *args, ok=ok)

    @functools.cached_property
    def state_dir(self) -> Path:
        return common_dir(self.cwd) / STATE_DIR

    @functools.cached_property
    def journal(self) -> list[tuple[str | None, str | None, bool]]:
        """The journal's lines for this trunk (read_journal); read once per call."""
        return read_journal(self.cwd, self.config.trunk)

    def held(self, commit: str) -> bool:
        """Did the gate let the trunk onto this commit? Where the trunk merely was found is not enough: a commit that
        arrived unseen would be laundered by one move back and forth (16 Nov 2026, the third review)."""
        return any(after == commit and held for _, after, held in self.journal)

    def commit_of(self, rev: str) -> str | None:
        """The commit a revision names, None when it names nothing."""
        return commit_at(self.cwd, rev)

    def named_commit(self, ref: str) -> str:
        commit = self.commit_of(ref)
        if commit is None:
            raise GateError(f"'{ref}' names no commit in this repository")
        return commit

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

    def changed_reviewed_paths(self, base: str | None, tree: str) -> tuple[str, ...]:
        """The reviewed paths that differ between two trees. One cheap diff: most landings change none, and need no more."""
        if base is None:
            return tuple(sorted(self.reviewed_entries(tree)))
        names = self.git("diff-tree", "-r", "-z", "--no-renames", "--name-only", base, tree).stdout.split("\0")
        return tuple(sorted(p for p in names if p and self.config.reviewed_class(p)))

    # ------------------------------------------------------------ what would land

    def landing(self, base: str | None, tree: str, what: str, selector: str) -> Landing:
        paths = self.changed_reviewed_paths(base, tree)
        key = f"{code_id(self.reviewed_entries(base))}..{code_id(self.reviewed_entries(tree))}" if paths else None
        return Landing(what, selector, base, tree, paths, key)

    def staged(self) -> Landing | None:
        """A commit of the index while HEAD is the trunk; None when HEAD is elsewhere and a commit lands nothing."""
        if self.git("symbolic-ref", "--quiet", "HEAD", ok=(0, 1)).stdout.strip() != self.config.trunk:
            return None
        tree = self.git("write-tree").stdout.strip()
        return self.landing(self.commit_of(self.config.trunk), tree, f"the staged index, committed on {self.config.trunk}",
                            "--staged")

    def merged(self, ref: str) -> Landing:
        """A merge or a pull of `ref` into the trunk: its tip when the trunk can fast-forward, the merged tree otherwise.
        Ancestry only chooses which tree to show here; the hook judges the tree that really arrives."""
        trunk, tip = self.commit_of(self.config.trunk), self.named_commit(ref)
        if trunk is None or self.git("merge-base", "--is-ancestor", trunk, tip, ok=(0, 1)).returncode == 0:
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
        return next((r for r in reversed(read_state(self.state_dir / RECORDS)) if r["key"] == key), None)

    def judge_landing(self, landing: Landing) -> Verdict:
        if landing.key is None:
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
        if self.held(new):
            return Verdict(True, f"{trunk} moves from {_short(old)} to {_short(new)}, a commit the journal lists as one the "
                                 "trunk held: nothing lands that was not there")
        return self.judge_landing(self.landing(old, new, f"{trunk} moving {_short(old)} -> {_short(new)}",
                                               selector or f"--tip {new}"))

    def judge_push(self, new: str | None, remote_old: str | None) -> Verdict:
        """A push to a remote's trunk: free for the local trunk and for what it held, a landing like any other for the rest."""
        if new is not None and new == self.commit_of(self.config.trunk):
            return Verdict(True, f"push of {_short(new)} to a remote's {self.config.trunk}: it is the local trunk, where the "
                                 "gate read it")
        if remote_old and self.commit_of(remote_old) is None:
            return Verdict(False, f"push to a remote's {self.config.trunk}: its present commit {_short(remote_old)} is not in "
                                  "this repository, so what the push would change cannot be read. Fetch first.")
        return self.judge_move(remote_old, new)

    # ------------------------------------------------------------ a move no hook saw

    def unseen_move(self, now: str | None) -> tuple[str | None, str | None] | None:
        """(the commit the gate last knew, the trunk now) when the trunk is not where the journal's last line left it."""
        if not self.journal or now == self.journal[-1][1]:       # not the line's before: the trunk left that commit
            return None
        return last_known(self.journal), now

    def unseen(self) -> Landing | None:
        """The unseen move as a landing, for the command line; None when there is none."""
        move = self.unseen_move(self.commit_of(self.config.trunk))
        if move is None:
            return None
        if move[1] is None:
            raise GateError(f"{self.config.trunk} was deleted without this hook: there is no trunk to judge")
        return self.landing(move[0], move[1], f"{self.config.trunk} moved {_short(move[0])} -> {_short(move[1])} unseen",
                            "--unseen")

    def judge_unseen(self, now: str | None) -> Verdict | None:
        """The verdict on a move of the trunk no hook saw; None when the trunk is where the gate left it. A pass is a move
        the gate lets stand, and is journalled as one."""
        move = self.unseen_move(now)
        if move is None:
            return None
        inner = self.judge_move(move[0], move[1], "--unseen")
        lead = (f"{self.config.trunk} was moved {_short(move[0])} -> {_short(move[1])} without this hook (a branch copied or "
                "renamed over it, hooks switched off, an edit under .git), and that move is judged before any other. ")
        return replace(inner, reason=lead + inner.reason, move=move if inner.allowed else None, happened=True)

    def after_unseen(self, now: str | None, judge: Callable[[str | None], list[Verdict]]) -> list[Verdict]:
        """The verdicts of `judge`, behind the one on an unseen move - alone when the gate refuses that one. `judge` is
        given the commit its journal lines start from: the trunk, or the last commit the gate knew when the trunk's own
        was not let stand."""
        unseen = self.judge_unseen(now)
        if unseen is None:
            return judge(now)
        if not unseen.allowed and not self.config.log_only:
            return [unseen]
        return [unseen, *judge(now if unseen.allowed else last_known(self.journal))]

    def baseline(self, hook: str) -> bool:
        """Take the trunk where it stands as a commit it may return to; whether a line was written. That is so for an empty
        journal, and for a trunk the journal left on a commit it does not hold - one that landed only because of log_only,
        the commit that switched log_only off among them: without it a reviewed commit on top could not be undone
        (16 Nov 2026, the final review). A trunk that was moved unseen is not baselined: that move is judged."""
        now = self.commit_of(self.config.trunk)
        if self.journal and (self.journal[-1][1] != now or self.journal[-1][2]):
            return False
        self.log(hook, Verdict(True, f"baseline: the gate takes {self.config.trunk} as it stands, at {_short(now)}",
                               move=(now, now)), lands=True, held=True)
        return True

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
        if not moves:                            # the trunk stays where it is: putting a working tree back must always work
            return []

        def judged(before: str | None) -> list[Verdict]:
            return [self._governed(old, new, before) for new in moves]

        unseen = self.unseen_move(old)
        if unseen and all(new is not None and self.held(new) for new in moves):
            return judged(unseen[0])             # back to where the gate let the trunk: also the way out of an unseen move
        return self.after_unseen(old, judged)

    def _governed(self, old: str | None, new: str | None, before: str | None) -> Verdict:
        """The verdict on one move of this repository's trunk from `old`, with the way back after a refusal and what the
        journal needs: `before` is the commit the gate knew the trunk at, which is `old` unless that arrived unseen."""
        verdict = self.judge_move(old, new)
        after = self.commit_of(new.removeprefix("ref:")) if new and new.startswith("ref:") else new
        advice = "" if verdict.allowed or new is None or new.startswith("ref:") else _put_back(new)
        return replace(verdict, reason=verdict.reason + advice, move=(before, after))

    def on_pre_push(self, updates: str) -> list[Verdict]:
        """One verdict per pushed ref that lands on a remote's trunk: `<local ref> <local oid> <remote ref> <remote oid>`."""
        pushes = [(_oid(parts[1]), _oid(parts[3])) for line in updates.splitlines()
                  if len(parts := line.split(" ")) == 4 and parts[2] == self.config.trunk]
        if not pushes:
            return []
        now = self.commit_of(self.config.trunk)
        return self.after_unseen(now, lambda _before: [self.judge_push(new, remote_old) for new, remote_old in pushes])

    def log(self, hook: str, verdict: Verdict, *, lands: bool, held: bool) -> None:
        """One line of the journal. A governed move also says where it leaves the trunk - at the new commit when the
        transaction goes on (`lands`), at the old one when the gate refuses it - and whether the gate let it there (`held`):
        under log_only a move lands that the gate would refuse, and that commit is not one to return to freely."""
        entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "hook": hook, "allowed": verdict.allowed,
                 "refused": not verdict.allowed and not self.config.log_only, "key": verdict.key,
                 "reason": verdict.reason.splitlines()[0]}
        if verdict.move:
            entry.update(trunk=self.config.trunk, trunk_before=verdict.move[0],
                         trunk_after=verdict.move[1] if lands else verdict.move[0], held=held and lands)
        _append_line(self.state_dir / DECISIONS, json.dumps(entry, sort_keys=True))

    def settle(self, hook: str, verdicts: list[Verdict]) -> int:
        """Log every verdict, print the refusals, and give the hook's exit code: REFUSED only when the gate acts."""
        refused = [v for v in verdicts if not v.allowed]
        acts = bool(refused) and not self.config.log_only
        for verdict in verdicts:             # an unseen move has happened already, whatever becomes of this transaction
            self.log(hook, verdict, lands=verdict.happened or not acts,
                     held=verdict.allowed if verdict.happened else not refused)
        prefix = "review gate (log only, nothing is refused): " if self.config.log_only else "review gate: "
        for verdict in refused:
            print(prefix + verdict.reason, file=sys.stderr)
        return REFUSED if acts else 0

    # ------------------------------------------------------------ the records

    def record(self, landing: Landing, review: Review) -> dict:
        if landing.key is None:
            raise GateError(f"{landing.what}: no reviewed path changes, so there is nothing to record a review of")
        path = self.state_dir / RECORDS
        read_state(path)                         # a malformed file is mended first, never appended to
        entry = {"key": landing.key, "date": time.strftime("%Y-%m-%d %H:%M"), "reviewer": review.reviewer,
                 "findings": review.findings, "verdict": review.verdict, "paths": list(landing.paths), "lands": landing.what}
        if review.note:
            entry["note"] = review.note
        _append_line(path, json.dumps(entry, sort_keys=True))
        return entry

    def export(self, target: Path) -> int:
        """Add the records the tracked log does not hold yet; the number added."""
        path = self.state_dir / RECORDS
        read_state(path)
        have = _lines(target)
        new = [line for line in _lines(path) if line not in have]
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
        return REFUSED if acting else 0


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
    """The verdict the hook would give: an unseen move first, and a --tip as the bare move of the trunk it is, so a move back
    passes there as it does at the hook."""
    unseen = gate.judge_unseen(gate.commit_of(gate.config.trunk))
    if unseen is not None and (a.unseen or not unseen.allowed):
        return unseen
    return gate.judge_move(landing.base, landing.tree) if a.tip else gate.judge_landing(landing)


def _status(gate: Gate, a: argparse.Namespace, landing: Landing) -> int:
    verdict = _judged(gate, a, landing)
    print(f"review gate: {landing.what}")
    print(f"  trunk     {gate.config.trunk} at {_short(landing.base)}")
    print(f"  key       {landing.key or 'none: no reviewed path changes'}")
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
    hook.add_argument("--trunk", required=True, help="the trunk ref the shim was installed for")
    hook.add_argument("--config-path", help="the configuration's path inside the repository, as the shim was installed with")
    hook.add_argument("rest", nargs="*", help="reference-transaction: the state; pre-push: the remote's name and URL")
    sub.add_parser("repair", help="set the malformed lines of the records and of the journal aside")
    export = sub.add_parser("export", help="add the records to the tracked log, for later readers")
    export.add_argument("--to", type=Path, default=TRACKED_LOG, help="the tracked log (default: %(default)s)")
    return ap


def repair(cwd: Path | None = None) -> dict[str, tuple[int, int]]:
    """Set aside the malformed lines of the records and of the journal; file name -> (kept, set aside). It opens no gate:
    a journal that cannot be read is what it is for."""
    return {name: _set_aside(common_dir(cwd) / STATE_DIR / name) for name in _PARSERS}


def _dispatch(gate: Gate, a: argparse.Namespace) -> int:
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
    is_hook = a.what == "hook"
    try:
        if a.what == "repair":
            for name, (kept, aside) in repair().items():
                print(f"review gate: {name}: {kept} line(s) kept, {aside} malformed line(s) moved to {REJECTED[name]}")
            return 0
        if is_hook:
            gate = open_gate(trunk=a.trunk, config_path=a.config_path)
            state = a.rest[0] if a.hook == "reference-transaction" and a.rest else None
            return run_hook(gate, a.hook, state, sys.stdin.read())
        return _dispatch(open_gate(), a)
    except GateError as e:
        print(f"review gate: {e}", file=sys.stderr)
        return BROKEN if is_hook else 1


if __name__ == "__main__":
    sys.exit(main())
