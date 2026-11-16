"""Install the review gate's two git hooks, which git does not version (the user, 16 November 2026: the check moves into git's hooks).

    python tools/install_git_hooks.py install   [--repo <dir>]    write the shims, or say they are current
    python tools/install_git_hooks.py check     [--repo <dir>]    exit 1 unless both shims are installed and current
    python tools/install_git_hooks.py uninstall [--repo <dir>]    remove the shims this installer wrote

Each hook is a small `sh` shim that calls `tools/review_gate.py hook ...`, the one implementation of the decision. git runs
`reference-transaction` for every ref update in the repository, several times each, fetches included, so the shim returns before
it starts python unless the update is a prepared one that names the trunk. `pre-push` returns at once unless a remote's trunk is
pushed to.

The shim holds three things fixed at install time: the trunk from `review_gate.json`, the python that ran the installer, and the
path of `review_gate.py` beside this file. `check` compares the installed text with what `install` would write now, so a changed
trunk or a moved checkout shows as stale. The hooks directory is shared by every worktree, so the installer refuses to run from
a linked worktree: the shim would point at a checkout that goes away.

`install` also writes the first line of the gate's journal when it has none for this trunk, so that a move of the trunk
past the hooks is told from where the gate started (review_gate.py, "What no hook sees").

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
_HEAD = """#!/bin/sh
{marker}
{filter}
gate='{gate}'
if [ ! -f "$gate" ]; then
    echo "review gate: $gate is missing, so this move of {trunk} cannot be judged and is refused." >&2
    echo "  Restore that file, or remove the hook: python tools/install_git_hooks.py uninstall" >&2
    exit 1
fi
printf '%s\\n' "$updates" | '{python}' "$gate" hook {hook} "$@"
"""
# git runs reference-transaction for every ref update, in several states; only a prepared update of the trunk costs a python start
_FILTERS = {
    "reference-transaction": """[ "$1" = prepared ] || exit 0
updates=$(cat)
case "$updates" in
*" {trunk}"*) ;;
*) exit 0 ;;
esac""",
    "pre-push": """updates=$(cat)
case "$updates" in
*" {trunk} "*) ;;
*) exit 0 ;;
esac""",
}
HOOKS = tuple(_FILTERS)


def _sh_path(path: Path | str) -> str:
    """A path for a single-quoted sh word, forward slashes."""
    text = str(path).replace("\\", "/")
    if "'" in text:
        raise GateError(f"{text}: a path with a single quote cannot be written into the hook")
    return text


def shim(hook: str, trunk: str) -> str:
    """The text of one hook as it would be installed now."""
    return _HEAD.format(marker=MARKER, filter=_FILTERS[hook].format(trunk=trunk), gate=_sh_path(GATE), trunk=trunk,
                        python=_sh_path(sys.executable), hook=hook)


def _refuse_linked_worktree(config: review_gate.GateConfig) -> None:
    """The shim points at this checkout's review_gate.py; a linked worktree is removed one day, and the hooks are shared."""
    found = review_gate.Gate(config, GATE.parent).git("rev-parse", "--path-format=absolute", "--git-dir", "--git-common-dir", ok=(0, 128))
    dirs = found.stdout.split("\n")
    if found.returncode == 0 and Path(dirs[0]) != Path(dirs[1]):
        raise GateError(f"{GATE.parent} is in a linked worktree; install from the main checkout, whose files stay")


def hooks_dir(gate: review_gate.Gate) -> Path:
    return Path(gate.git("rev-parse", "--path-format=absolute", "--git-path", "hooks").stdout.strip())


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
    directory = hooks_dir(gate)
    wanted = {directory / hook: shim(hook, gate.config.trunk) for hook in HOOKS}
    return {path: (state_of(path, text), text) for path, text in wanted.items()}


def install(gate: review_gate.Gate) -> int:
    _refuse_linked_worktree(gate.config)
    if gate.commit_of(gate.config.trunk) is None:
        raise GateError(f"the trunk {gate.config.trunk} of review_gate.json does not exist in this repository")
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


def uninstall(gate: review_gate.Gate) -> int:
    for path, (state, _) in _states(gate).items():
        if state in ("current", "stale"):
            path.unlink()
            print(f"{path}: removed")
        else:
            print(f"{path}: {state}, left alone")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("what", choices=("install", "check", "uninstall"))
    ap.add_argument("--repo", type=Path, default=GATE.parent,
                    help="a directory inside the repository to act on (default: the checkout this file is in)")
    a = ap.parse_args(argv)
    try:
        gate = review_gate.Gate(review_gate.load_config(), a.repo)
        return {"install": install, "check": check, "uninstall": uninstall}[a.what](gate)
    except GateError as e:
        print(f"install_git_hooks: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
