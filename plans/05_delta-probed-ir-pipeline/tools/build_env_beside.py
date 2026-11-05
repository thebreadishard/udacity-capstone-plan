"""Build a WSL virtual environment beside an existing one: the same interpreter and the same pinned packages, with named changes.

Used for an upstream release (the software ledger's upgrade checklist, step 2): the running jobs keep the old environment, the new one differs from
it only in the packages named here, so a difference in the checks that follow belongs to those packages.

    python tools/build_env_beside.py --source qc05 --target qc215 --set pyscf==2.15.0 --drop pyscf-forge --import pyscf --dry-run
    python tools/build_env_beside.py --source qc05 --target qc215 --set pyscf==2.15.0 --drop pyscf-forge --import pyscf
    python tools/build_env_beside.py --source qc05 --target qc215 --set pyscf==2.15.0 --drop pyscf-forge --import pyscf --verify

Environments are directories in the WSL home. The source is read live (`pip freeze`), never from a possibly stale listing, and never written. The
target must not exist; its packages are installed exactly as pinned with `--no-deps`, then `pip check` must pass, its own `pip freeze` must equal
the plan and each `--import` module must import. The pin list stays in the target as `build-requirements.txt`. A failure after the target was
created leaves it in place for inspection; nothing is deleted here. `--verify` runs the three checks again on an existing target.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from freeze_environments import WSL, locals_of, normalise

ENV_NAME = re.compile(r"[A-Za-z0-9_.-]+")
MODULE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*")
PIN = re.compile(r"(?P<name>[A-Za-z0-9][A-Za-z0-9_.-]*)==(?P<version>[A-Za-z0-9_.+!-]+)")
REQUIREMENTS = "build-requirements.txt"
INSTALL_TIMEOUT_S = 3600
Shell = Callable[..., str]


class BuildError(RuntimeError):
    """A refused plan or a failed build step; the message says which and why."""


def canonical(name: str) -> str:
    """PEP 503 normalised project name: pip treats pyscf_forge and pyscf-forge as one project."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_pin(line: str) -> tuple[str, str]:
    m = PIN.fullmatch(line.strip())
    if m is None:
        raise BuildError(f"not an exact pin 'name==version': {line!r}")
    return m["name"], m["version"]


def pins_of(freeze_text: str) -> dict[str, tuple[str, str]]:
    """{canonical name: (name as written, version)} of a `pip freeze`; a local or editable install cannot be rebuilt from a pin, so it is refused."""
    local = locals_of(freeze_text)
    if local:
        raise BuildError("the source has local or editable installs, which a pin list cannot rebuild: " + "; ".join(local))
    pins = {}
    for line in normalise(freeze_text):
        name, version = parse_pin(line)
        pins[canonical(name)] = (name, version)
    return pins


@dataclass(frozen=True)
class BuildPlan:
    source: str
    target: str
    set_pins: tuple[tuple[str, str], ...] = ()
    drop: tuple[str, ...] = ()
    imports: tuple[str, ...] = ()
    dry_run: bool = False
    verify_only: bool = False

    def __post_init__(self) -> None:
        for env in (self.source, self.target):
            if not ENV_NAME.fullmatch(env):
                raise BuildError(f"an environment is a directory name in the WSL home (letters, digits, '_', '.', '-'): {env!r}")
        if self.source == self.target:
            raise BuildError("source and target are the same environment")
        if self.dry_run and self.verify_only:
            raise BuildError("--dry-run creates nothing and --verify checks an existing target: one or the other")
        both = {canonical(n) for n, _ in self.set_pins} & {canonical(n) for n in self.drop}
        if both:
            raise BuildError(f"set and dropped at once: {sorted(both)}")
        bad = [m for m in self.imports if not MODULE.fullmatch(m)]
        if bad:
            raise BuildError(f"not a module name: {bad}")


def home_path(env: str) -> str:
    """The shell form of an environment's directory; safe unquoted inside double quotes because BuildPlan admits only ENV_NAME."""
    return f'"$HOME/{env}"'


def planned_pins(source: dict[str, tuple[str, str]], plan: BuildPlan) -> list[str]:
    """The source's pins with the plan's changes; a change to a package the source does not have is refused (a typo would otherwise pass)."""
    pins = dict(source)
    for name, version in plan.set_pins:
        if canonical(name) not in pins:
            raise BuildError(f"--set {name}: the source has no such package")
        pins[canonical(name)] = (pins[canonical(name)][0], version)
    for name in plan.drop:
        if canonical(name) not in pins:
            raise BuildError(f"--drop {name}: the source has no such package")
        del pins[canonical(name)]
    return sorted((f"{n}=={v}" for n, v in pins.values()), key=str.lower)


def changes(source: dict[str, tuple[str, str]], planned: list[str]) -> list[str]:
    """Readable difference between the source and the plan, for the dry run and the final report."""
    after = {canonical(n): (n, v) for n, v in map(parse_pin, planned)}
    out = [f"{n} {v} -> {after[k][1]}" for k, (n, v) in source.items() if k in after and after[k][1] != v]
    out += [f"{n} {v} dropped" for k, (n, v) in source.items() if k not in after]
    return sorted(out, key=str.lower)


def wsl_shell(script: str, stdin: str | None = None, timeout: int = 300) -> str:
    """Run one bash script in WSL; a non-zero exit raises with its stderr."""
    try:
        p = subprocess.run([*WSL, script], input=stdin, capture_output=True, text=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise BuildError(f"WSL did not run {script!r}: {exc}") from exc
    if p.returncode != 0:
        raise BuildError(f"exit {p.returncode} from {script!r}: {p.stderr.strip()[-2000:]}")
    return p.stdout


def read_source(plan: BuildPlan, shell: Shell) -> tuple[str, dict[str, tuple[str, str]]]:
    """(the source's real interpreter, its pins); the interpreter is the symlink target, so the target venv runs the very same Python."""
    src = home_path(plan.source)
    interpreter = shell(f"readlink -f {src}/bin/python").strip()
    if not interpreter or "'" in interpreter:
        raise BuildError(f"no usable interpreter behind {plan.source}/bin/python: {interpreter!r}")
    return interpreter, pins_of(shell(f"{src}/bin/python -m pip freeze"))


def create_target(plan: BuildPlan, interpreter: str, planned: list[str], shell: Shell) -> None:
    dst = home_path(plan.target)
    shell(f"test ! -e {dst} || {{ echo 'the target exists; it is never overwritten' >&2; exit 1; }}")
    shell(f"'{interpreter}' -m venv {dst}")
    shell(f"cat > {dst}/{REQUIREMENTS}", stdin="\n".join(planned) + "\n")
    shell(f"{dst}/bin/python -m pip install --no-input --no-deps -r {dst}/{REQUIREMENTS}", timeout=INSTALL_TIMEOUT_S)


def verify_target(plan: BuildPlan, planned: list[str], shell: Shell) -> None:
    """Three checks: pip's own dependency check, the installed pins against the plan, and the named imports."""
    py = f"{home_path(plan.target)}/bin/python"
    shell(f"{py} -m pip check")
    installed = sorted((f"{n}=={v}" for n, v in pins_of(shell(f"{py} -m pip freeze")).values()), key=str.lower)
    if installed != planned:
        missing, extra = sorted(set(planned) - set(installed)), sorted(set(installed) - set(planned))
        raise BuildError(f"the target's pins differ from the plan: missing {missing}, extra {extra}")
    if plan.imports:
        shell(f"{py} -c 'import importlib, sys; [importlib.import_module(m) for m in sys.argv[1:]]' " + " ".join(plan.imports))


def build(plan: BuildPlan, shell: Shell = wsl_shell) -> list[str]:
    """Build (or, on a dry run, only plan) the target; returns the report lines."""
    interpreter, source = read_source(plan, shell)
    planned = planned_pins(source, plan)
    report = [f"interpreter: {interpreter}", f"{len(planned)} packages; changes: " + ("; ".join(changes(source, planned)) or "none")]
    if plan.dry_run:
        return [*report, f"dry run: {plan.target} not created"]
    if not plan.verify_only:
        create_target(plan, interpreter, planned, shell)
    verify_target(plan, planned, shell)
    done = "verified" if plan.verify_only else "built"
    return [*report, f"{done} ~/{plan.target}: pip check passed, pins equal the plan, imports {list(plan.imports)} ok"]


def plan_from_args(argv: Sequence[str] | None) -> BuildPlan:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", required=True, help="existing environment, a directory in the WSL home")
    ap.add_argument("--target", required=True, help="new environment, a directory in the WSL home that must not exist")
    ap.add_argument("--set", action="append", default=[], metavar="NAME==VERSION", help="a package pinned to another version")
    ap.add_argument("--drop", action="append", default=[], metavar="NAME", help="a package left out")
    ap.add_argument("--import", dest="imports", action="append", default=[], metavar="MODULE", help="a module that must import in the target")
    ap.add_argument("--dry-run", action="store_true", help="read the source and print the plan; create nothing")
    ap.add_argument("--verify", action="store_true", help="run the checks on an existing target; build nothing")
    a = ap.parse_args(argv)
    return BuildPlan(a.source, a.target, tuple(parse_pin(s) for s in a.set), tuple(a.drop), tuple(a.imports), a.dry_run, a.verify)


def main(argv: Sequence[str] | None = None) -> int:
    try:
        plan = plan_from_args(argv)
        for line in build(plan):
            print(line, flush=True)
    except BuildError as exc:
        print(f"REFUSED or FAILED: {exc}", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
