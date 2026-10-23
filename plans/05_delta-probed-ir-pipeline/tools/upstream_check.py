"""Checks before and after a contribution to an upstream project (TASKS 101; the user, 23 Oct 2026: 'hoe kunnen we zeker stellen dat de code
die we schrijven bestaande conventies respecteert en ... goed aansluit bij het pyscf project en voldoet aan best practices?').

  lint <checkout> <base>              the project's own lint commands — every `run:` line of its .github/workflows/lint.yml that
                                      calls ruff, flake8 or pycodestyle — on the files the commits <base>..HEAD change under each
                                      command's target, with the config's excludes applied as the project's CI applies them; the
                                      change's scope (lines per file); every OpenMP parallel region of a changed C file without
                                      default(none)
  backport <owner/repo> <pr> <author> the commits on a merged pull request by anyone but <author>: maintainer changes our local copy must take
                                      over (pyscf#3470's 5b2633172 reached our kernel only 17 days later, TASKS 100)

Exit 1 when anything is found. Then read the project's own review guide against the diff (pyscf: agent-recipes/skills/
pyscf-pr-review.template.md, and its AI_POLICY.md: disclose AI use; the contributor submits and speaks in their own words).
ruff runs from this Python; flake8 and pycodestyle from tools/upstream_lint/.venv (versions in tools/upstream_lint/requirements.txt).
"""
from __future__ import annotations

import argparse
import configparser
import fnmatch
import json
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

LINT_PYTHON = Path(__file__).resolve().parent / "upstream_lint" / ".venv" / "Scripts" / "python.exe"
LINTERS = ("ruff", "flake8", "pycodestyle")
RUN_LINE = re.compile(r"^\s*run:\s*((?:ruff|flake8|pycodestyle)\b.*)$")
PARALLEL = re.compile(r"#pragma\s+omp\s+parallel\b[^\n]*")


def git(checkout: Path, *args: str) -> str:
    """git in a checkout that may sit on another filesystem (WSL): safe.directory for this call only, never written to a config."""
    res = subprocess.run(["git", "-c", "safe.directory=*", "-C", str(checkout), *args], capture_output=True, encoding="utf-8", check=False)
    if res.returncode:
        raise SystemExit(f"git {' '.join(args)} failed in {checkout}: {res.stderr.strip()}")
    return res.stdout


def lint_commands(checkout: Path) -> list[list[str]]:
    """The lint workflow's ruff / flake8 / pycodestyle commands as argument lists; refuses a project without them."""
    workflow = checkout / ".github" / "workflows" / "lint.yml"
    if not workflow.exists():
        raise SystemExit(f"no {workflow}: name this project's lint commands before checking against it")
    cmds = [shlex.split(m[1]) for line in workflow.read_text(encoding="utf-8").splitlines() if (m := RUN_LINE.match(line))]
    if not cmds:
        raise SystemExit(f"{workflow} has no ruff, flake8 or pycodestyle run line")
    return cmds


def executable(tool: str) -> list[str]:
    if tool == "ruff":
        return [sys.executable, "-m", "ruff"]
    if not LINT_PYTHON.exists():
        raise SystemExit(f"{tool} needs {LINT_PYTHON} (python -m venv tools/upstream_lint/.venv; pip install -r tools/upstream_lint/requirements.txt)")
    return [str(LINT_PYTHON), "-m", tool]


def on_changed(cmd: list[str], changed: list[str]) -> list[str]:
    """The changed .py files under the command's final argument, its target package directory."""
    target = cmd[-1].rstrip("/")
    return [f for f in changed if f.endswith(".py") and (f == target or f.startswith(target + "/"))]


def flake8_excluded(checkout: Path, cmd: list[str]) -> list[str]:
    """The exclude patterns of the flake8 config the command names (flake8 lints a named file even when they exclude it)."""
    if cmd[0] != "flake8" or "--config" not in cmd:
        return []
    cfg = configparser.ConfigParser()
    cfg.read(checkout / cmd[cmd.index("--config") + 1], encoding="utf-8")
    return [p.strip() for p in cfg.get("flake8", "exclude", fallback="").split(",") if p.strip()]


def drop_excluded(files: list[str], patterns: list[str]) -> list[str]:
    return [f for f in files if not any(fnmatch.fnmatch(part, p) for part in Path(f).parts for p in patterns)]


def command(cmd: list[str], files: list[str]) -> list[str]:
    """The workflow's command on these files instead of its whole target."""
    extra = ["--force-exclude"] if cmd[0] == "ruff" else []      # ruff lints a named file even when the config excludes it
    return [*executable(cmd[0]), *cmd[1:-1], *extra, *files]


def openmp_without_default_none(text: str) -> list[str]:
    return [p for p in PARALLEL.findall(text) if "default(none)" not in p]


def lint(checkout: Path, base: str, run: Callable = subprocess.run) -> int:
    changed = git(checkout, "diff", "--name-only", base, "HEAD").split()      # commits only: a WSL tree read from Windows shows
    numstat = [line.split("\t") for line in git(checkout, "diff", "--numstat", base, "HEAD").splitlines()]   # every file as changed
    found = 0
    print(f"{len(changed)} files changed in {base}..HEAD:")
    for added, removed, name in numstat:
        print(f"  +{added} -{removed}  {name}")
    for cmd in lint_commands(checkout):
        files = drop_excluded(on_changed(cmd, changed), flake8_excluded(checkout, cmd))
        if not files:
            continue
        res = run(command(cmd, files), cwd=checkout, capture_output=True, encoding="utf-8", errors="replace", check=False)
        print(f"$ {' '.join(cmd[:-1])} <{len(files)} changed files>: {'clean' if res.returncode == 0 else 'FINDINGS'}")
        if res.returncode:
            found += 1
            print(res.stdout.strip() or res.stderr.strip())
    for name in (f for f in changed if f.endswith(".c") and (checkout / f).exists()):
        bare = openmp_without_default_none((checkout / name).read_text(encoding="utf-8", errors="replace"))
        if bare:
            found += 1
            print(f"{name}: {len(bare)} OpenMP parallel region(s) without default(none): " + "; ".join(bare))
    return 1 if found else 0


def gh_json(*args: str) -> object:
    res = subprocess.run(["gh", "api", *args], capture_output=True, encoding="utf-8", check=False)
    if res.returncode:
        raise SystemExit(f"gh api {' '.join(args)} failed: {res.stderr.strip()}")
    return json.loads(res.stdout)


def backport(repo: str, pr: int, author: str, api: Callable = gh_json) -> int:
    info = api(f"repos/{repo}/pulls/{pr}")
    if not info.get("merged_at"):
        raise SystemExit(f"{repo}#{pr} is not merged")
    others = [c for c in api(f"repos/{repo}/pulls/{pr}/commits") if (c.get("author") or {}).get("login") != author]
    print(f"{repo}#{pr} (merged {info['merged_at'][:10]}): {len(others)} commit(s) by others than {author}")
    for c in others:
        detail = api(f"repos/{repo}/commits/{c['sha']}")
        print(f"\n{c['sha'][:9]} {(c.get('author') or {}).get('login')}: {c['commit']['message'].splitlines()[0]}")
        for f in detail.get("files", []):
            print(f"--- {f['filename']}\n{f.get('patch', '(no patch)')}")
    return 1 if others else 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="mode", required=True)
    lt = sub.add_parser("lint")
    lt.add_argument("checkout", type=Path)
    lt.add_argument("base")
    bp = sub.add_parser("backport")
    bp.add_argument("repo")
    bp.add_argument("pr", type=int)
    bp.add_argument("author")
    a = p.parse_args(argv)
    return lint(a.checkout, a.base) if a.mode == "lint" else backport(a.repo, a.pr, a.author)


if __name__ == "__main__":
    sys.exit(main())
