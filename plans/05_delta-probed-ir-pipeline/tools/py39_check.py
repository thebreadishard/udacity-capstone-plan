"""Python 3.9 compatibility of the files a pyscf PR branch changes (pyscf's floor: requires-python >= 3.9, tested in its CI). Checks the 3.9
grammar (ast feature_version) and the 3.10+ run-time forms the grammar lets through: zip(strict=), itertools.pairwise, int.bit_count,
X | Y in an isinstance/issubclass argument, in an annotation without `from __future__ import annotations`, or in a module- or class-level
type alias, and dataclass(kw_only=/slots=/match_args=). There is no 3.9 interpreter on the laptop (installing one is a download), so this
script is the check (26 Oct 2026, the review of PR D).

    python tools/py39_check.py <worktree> <base commit>      (one line per finding; exit 1 when there is one)
"""
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

NEW_IN_310 = ("pairwise", "bit_count")
DATACLASS_310 = ("kw_only", "slots", "match_args")


def _has_bitor(node: ast.AST) -> bool:
    return any(isinstance(n, ast.BinOp) and isinstance(n.op, ast.BitOr) for n in ast.walk(node))


def _is_type_union(node: ast.AST) -> bool:
    """A | B whose sides look like types (names, attributes, subscripts, None), not integer or set arithmetic."""
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return all(_is_type_union(side) or _is_type_like(side) for side in (node.left, node.right))
    return False


def _is_type_like(node: ast.AST) -> bool:
    return isinstance(node, ast.Name | ast.Attribute | ast.Subscript) or (isinstance(node, ast.Constant) and node.value is None)


def _call_findings(n: ast.Call) -> list[str]:
    name = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", "")
    keywords = {k.arg for k in n.keywords}
    out = []
    if name == "zip" and "strict" in keywords:
        out.append("zip(strict=) is 3.10")
    if name in NEW_IN_310:
        out.append(f"{name} is 3.10")
    if name in ("isinstance", "issubclass") and len(n.args) == 2 and _has_bitor(n.args[1]):
        out.append(f"X | Y in {name} is 3.10")
    if name == "dataclass" and keywords & set(DATACLASS_310):
        out.append(f"dataclass({', '.join(sorted(keywords & set(DATACLASS_310)))}) is 3.10")
    return out


def _annotations(n: ast.AST) -> list[ast.AST]:
    if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef):
        args = [*n.args.posonlyargs, *n.args.args, *n.args.kwonlyargs, n.args.vararg, n.args.kwarg]
        return [a.annotation for a in args if a is not None and a.annotation is not None] + ([n.returns] if n.returns else [])
    if isinstance(n, ast.AnnAssign):
        return [n.annotation]
    return []


def _alias_findings(tree: ast.Module) -> list[tuple[int, str]]:
    scopes = [tree, *(c for c in ast.walk(tree) if isinstance(c, ast.ClassDef))]
    return [(n.lineno, "X | Y type alias evaluated at run time") for scope in scopes for n in scope.body
            if isinstance(n, ast.Assign) and _is_type_union(n.value)]


def findings(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), feature_version=(3, 9))
    except SyntaxError as e:
        return [f"{path}:{e.lineno}: not Python 3.9 grammar: {e.msg}"]
    postponed = any(isinstance(n, ast.ImportFrom) and n.module == "__future__" and any(a.name == "annotations" for a in n.names)
                    for n in tree.body)
    found: list[tuple[int, str]] = _alias_findings(tree)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            found += [(n.lineno, f) for f in _call_findings(n)]
        if not postponed and any(_has_bitor(a) and _is_type_union(a) for a in _annotations(n)):
            found.append((n.lineno, "X | Y in an annotation without postponed annotations"))
    return [f"{path}:{line}: {what}" for line, what in sorted(found)]


def main(worktree: str, base: str) -> int:
    root = Path(worktree)
    changed = subprocess.run(["git", "-C", worktree, "diff", "--name-only", base, "--", "*.py"], capture_output=True, text=True, check=True)
    files = [root / f for f in changed.stdout.split() if (root / f).exists()]
    problems = [p for f in files for p in findings(f)]
    print(f"{worktree}: {len(files)} changed .py files, {len(problems)} Python 3.9 findings")
    for p in problems:
        print("  " + p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
