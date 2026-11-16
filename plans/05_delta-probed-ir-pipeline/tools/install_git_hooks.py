"""Install the review gate's two git hooks, which git does not version (the user, 16 November 2026: the check moves into git's hooks).

    python tools/install_git_hooks.py install      write the shims, or say they are current
    python tools/install_git_hooks.py check        exit 1 unless both shims are installed and current
    python tools/install_git_hooks.py uninstall    remove the shims this installer wrote

It acts on the repository this file is checked out in, and on no other. Each hook is a small `sh` shim that calls
`tools/review_gate.py hook ...`, the one implementation of the decision.

**What the shim costs.** git runs `reference-transaction` for every ref update in the repository, in several states, fetches
and stashes included, so each start of `sh` is paid on every commit anywhere. Before its early exit the shim therefore uses
shell builtins only - no `cat`, `grep` or `$(...)`: it leaves at once unless the state is `prepared`, reads stdin with `read`,
and leaves unless a line names the trunk. `pre-push` leaves unless a remote's trunk is pushed to.

**A broken installation.** The shim holds four things fixed at install time: the trunk, the python that ran the installer, the
path of `review_gate.py` beside this file, and the configuration's path inside the repository. When that python or that file
is missing (git run from WSL sees neither under a `C:/` path) or the gate ends with anything but its two exit codes, the shim
decides alone (a gate that ran and could not judge has said why, and the shim says only that), on moves of the trunk only
(an update that leaves it where it is passes), and by the one switch: it reads `log_only` from the trunk's own
`review_gate.json` with git and passes the move when it says true; otherwise it refuses with one line that names the repair.
`check` compares the installed text with what `install` would write now, so a moved checkout or another python shows as
stale.

The hooks directory is shared by every worktree, so the installer refuses to run from a linked worktree: the shim would point
at a checkout that goes away. It refuses a trunk that does not hold the gate's configuration: the hook reads the reviewed set
from the trunk, never from the working tree. `install` also writes the first line of the gate's journal when it has none for
this trunk, so that a move of the trunk past the hooks is told from where the gate started (review_gate.py, "What no hook
sees").

It never touches a hook it did not write. The pre-commit framework owns `pre-commit`, a different file, and stays as it is; a
`reference-transaction` or `pre-push` hook without this installer's marker is foreign, and install refuses rather than overwrite
it - chain the two by hand.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import review_gate
from review_gate import GateError

MARKER = "# review-gate shim - written by tools/install_git_hooks.py; reinstall instead of editing"
GATE = Path(review_gate.__file__).resolve()
# builtins only up to the last `exit 0` of each filter: this part runs for every ref update of the repository
_FILTERS = {
    "reference-transaction": """[ "$1" = prepared ] || exit 0
updates=
hit=
while read -r old new ref; do
    [ "$ref" = '@TRUNK@' ] && hit=$new
    updates="$updates$old $new $ref
"
done
[ -n "$hit" ] || exit 0""",
    "pre-push": """updates=
hit=
while read -r local_ref local_oid remote_ref remote_oid; do
    [ "$remote_ref" = '@TRUNK@' ] && hit=push
    updates="$updates$local_ref $local_oid $remote_ref $remote_oid
"
done
[ -n "$hit" ] || exit 0""",
}
_SHIM = """#!/bin/sh
@MARKER@
@FILTER@
python='@PYTHON@'
gate='@GATE@'
if [ -x "$python" ] && [ -f "$gate" ]; then
    printf '%s' "$updates" | "$python" -I -S "$gate" hook @HOOK@ --trunk '@TRUNK@' --config-path '@CONFIG@' "$@"
    status=$?
    [ "$status" = 0 ] && exit 0
    [ "$status" = @REFUSED@ ] && exit 1
    [ "$status" = @BROKEN@ ] && why="the gate could not judge it, for the reason it gave above."
fi
# The gate could not run. An update that leaves the trunk where it is passes: putting a working tree back must always work.
[ "$hit" = "$(git rev-parse --quiet --verify '@TRUNK@')" ] && exit 0
# The one switch is still the trunk's own configuration, read here as the gate reads it.
if git cat-file blob '@TRUNK@:@CONFIG@' 2>/dev/null | grep -q '"log_only"[[:space:]]*:[[:space:]]*true'; then
    echo "review gate (log only, nothing is refused): ${why:-the gate could not run. @REPAIR@}" >&2
    exit 0
fi
echo "review gate: this move of @TRUNK@ is refused: ${why:-the gate could not run ($python $gate). @REPAIR@}" >&2
exit 1
"""
_REPAIR = "Repair: python tools/install_git_hooks.py install - or uninstall, to work without the gate."
HOOKS = tuple(_FILTERS)


def _sh_word(value: Path | str) -> str:
    """A value for a single-quoted sh word; a path with forward slashes."""
    text = str(value).replace("\\", "/")
    if "'" in text:
        raise GateError(f"{text}: a single quote cannot be written into the hook")
    return text


def shim(hook: str, trunk: str, config_path: str) -> str:
    """The text of one hook as it would be installed now."""
    values = {"@MARKER@": MARKER, "@FILTER@": _FILTERS[hook], "@PYTHON@": _sh_word(sys.executable), "@GATE@": _sh_word(GATE),
              "@HOOK@": hook, "@TRUNK@": trunk, "@CONFIG@": _sh_word(config_path), "@REFUSED@": str(review_gate.REFUSED), "@REPAIR@": _REPAIR,
              "@BROKEN@": str(review_gate.BROKEN)}
    text = _SHIM
    for name, value in values.items():
        text = text.replace(name, value)
    return text


def _refuse_linked_worktree() -> None:
    """The shim points at this checkout's review_gate.py; a linked worktree is removed one day, and the hooks are shared."""
    found = review_gate.run_git(GATE.parent, "rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir")
    git_dir, common = found.stdout.split("\n")[:2]
    if Path(git_dir) != Path(common):
        raise GateError(f"{GATE.parent} is in a linked worktree; install from the main checkout, whose files stay")


def hooks_dir() -> Path:
    return Path(review_gate.run_git(GATE.parent, "rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip())


def state_of(path: Path, wanted: str) -> str:
    """missing | current | stale | foreign"""
    if not path.is_file():
        return "missing"
    text = path.read_text(encoding="utf-8", errors="replace")
    if MARKER not in text:
        return "foreign"
    return "current" if text == wanted else "stale"


def _states(gate: review_gate.Gate) -> dict[Path, tuple[str, str]]:
    """hook file -> (its state, the text install would write)"""
    directory, config_path = hooks_dir(), review_gate.tracked_config_path()
    wanted = {directory / hook: shim(hook, gate.config.trunk, config_path) for hook in HOOKS}
    return {path: (state_of(path, text), text) for path, text in wanted.items()}


def install(gate: review_gate.Gate) -> int:
    trunk = gate.commit_of(gate.config.trunk)
    if trunk is None:
        raise GateError(f"the trunk {gate.config.trunk} of review_gate.json does not exist in this repository")
    if review_gate.config_on(gate.cwd, trunk, review_gate.tracked_config_path()) is None:
        raise GateError(f"{gate.config.trunk} does not hold {review_gate.tracked_config_path()}: land the gate on the "
                        "trunk first, the hook reads its configuration there")
    states = _states(gate)
    foreign = [str(path) for path, (state, _) in states.items() if state == "foreign"]
    if foreign:
        raise GateError(f"{', '.join(foreign)}: a hook this installer did not write. Nothing was installed; chain the two by "
                        "hand, or move the other hook away.")
    for path, (state, text) in states.items():
        if state != "current":
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_name(path.name + ".tmp")
            tmp.write_text(text, encoding="utf-8", newline="\n")
            tmp.chmod(0o755)
            os.replace(tmp, path)
        print(f"{path}: {'already current' if state == 'current' else 'installed'}")
    if gate.baseline("install"):
        print(f"the gate starts from {gate.config.trunk} as it is; what moves it past the hooks from here on is judged later")
    return 0


def check(gate: review_gate.Gate) -> int:
    states = _states(gate)
    for path, (state, _) in states.items():
        print(f"{path}: {state}")
    if all(state == "current" for state, _ in states.values()):
        return 0
    print("the review gate's hooks are not all in place: python tools/install_git_hooks.py install", file=sys.stderr)
    return 1


def uninstall() -> int:
    """Remove the shims by their marker alone: this is the way out of a broken gate, so it reads no configuration."""
    for path in (hooks_dir() / hook for hook in HOOKS):
        state = state_of(path, wanted="")
        if state == "stale":
            path.unlink()
            print(f"{path}: removed")
        else:
            print(f"{path}: {state}, left alone")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=("install", "check", "uninstall"))
    a = ap.parse_args(argv)
    try:
        if a.what == "uninstall":
            return uninstall()
        _refuse_linked_worktree()
        return {"install": install, "check": check}[a.what](review_gate.open_gate(GATE.parent))
    except GateError as e:
        print(f"install_git_hooks: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
