"""tools/deploy_closure.py <file>… (paths relative to the plan folder, run from it) — refuses a deploy list that lacks a file one of its own
files needs. 19 Oct 2026: probes/deploy_s2.sh shipped a runner without library_log.py and scf_converge.py, which the runner imports since that
morning, so S2b's first molecule would have failed on import; the list had been kept by hand beside deploy_s1tz.sh's.

What a file needs, when that file exists in the plan:
  .py — every import (also inside a function) that names a sibling module of the file or a module under src/ (relative imports included;
        `from pkg import name` also needs pkg/name.py when it exists);
  .sh — outside comments: $HERE/<file>, probes/<file>.(sh|py), and `-m <package.module>` under src/.
Prints each missing file with the file that needs it and exits 1; prints the number of files checked and exits 0 when the list is closed.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

SHELL_HERE = re.compile(r"\$\{?HERE\}?/([\w.-]+\.(?:sh|py))")
SHELL_PROBES = re.compile(r"(?<![\w/])(probes/[\w./-]+\.(?:sh|py))")
SHELL_MODULE = re.compile(r"-m\s+([A-Za-z_]\w*(?:\.\w+)+)")
TRAILING_COMMENT = re.compile(r"\s#.*$")


def module_files(dotted: str, roots: list[Path]) -> list[Path]:
    """The files a dotted module name can be, under each root: a.b → a/b.py or a/b/__init__.py."""
    rel = Path(*dotted.split("."))
    return [p for root in roots for p in (root / rel.with_suffix(".py"), root / rel / "__init__.py")]


def python_needs(path: Path, plan: Path) -> set[Path]:
    """The plan's files that a Python file imports."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots = [path.parent, plan / "src"]
    names: list[tuple[str, list[Path]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names += [(alias.name, roots) for alias in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = path.parent
            for _ in range(max(node.level - 1, 0)):
                base = base.parent
            where = [base] if node.level else roots
            module = node.module or ""
            if module:
                names.append((module, where))
            names += [(f"{module}.{alias.name}" if module else alias.name, where) for alias in node.names]
    return {f for dotted, where in names for f in module_files(dotted, where) if f.is_file()}


def shell_needs(path: Path, plan: Path) -> set[Path]:
    """The plan's files a shell script runs or sources, outside its comments."""
    out: set[Path] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("#"):
            continue
        code = TRAILING_COMMENT.sub("", line)
        out |= {path.parent / m for m in SHELL_HERE.findall(code)}
        out |= {plan / m for m in SHELL_PROBES.findall(code)}
        out |= {f for m in SHELL_MODULE.findall(code) for f in module_files(m, [plan / "src"])}
    return {f for f in out if f.is_file()}


def missing(files: list[str], plan: Path) -> list[tuple[str, str]]:
    """(needed file, needing file) for every file the list needs and lacks, both relative to the plan."""
    shipped = {(plan / f).resolve() for f in files}
    out = []
    for f in files:
        path = plan / f
        if not path.is_file():
            raise SystemExit(f"{f}: not a file of the plan")
        needs = python_needs(path, plan) if path.suffix == ".py" else shell_needs(path, plan) if path.suffix == ".sh" else set()
        out += [(n.resolve().relative_to(plan.resolve()).as_posix(), f) for n in sorted(needs) if n.resolve() not in shipped]
    return sorted(set(out))


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit(__doc__.splitlines()[0])
    gaps = missing(argv, Path.cwd())
    for needed, by in gaps:
        print(f"MISSING {needed} (needed by {by})")
    if not gaps:
        print(f"deploy list closed: {len(argv)} files")
    return 1 if gaps else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
