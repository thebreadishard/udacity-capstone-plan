"""A deploy script copies every module its copied modules import (14 November 2026).

The labels bootstrap copies the corpus's `analytic_hessians.py` and its own helpers into one flat folder on the server. When that
module gained two imports this morning — `constants` and `vibrations`, from the extraction of TASKS 216 — the script still copied the
old set, so the next server would have died at import with nothing to say for itself. The deployed runs were safe only because they
started from an older copy.

This test reads the imports that resolve inside the plan rather than to a package, and checks that the script's copy line names each
one. It is a static check: no server, no network, nothing to run nightly.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus"
BOOTSTRAP = PLAN / "probes" / "bootstrap_labels_ccx53.sh"
LOCAL_FOLDERS = (CORPUS, PLAN / "probes")


def local_imports(module: Path) -> set[str]:
    """The module names `module` imports that are files in the corpus folder or in probes/ — the ones a flat server folder needs."""
    tree = ast.parse(module.read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module.split(".")[0])
    return {name for name in names if any((folder / f"{name}.py").is_file() for folder in LOCAL_FOLDERS)}


def copied_files(script: Path) -> set[str]:
    """The file names the script's scp lines carry (basenames, as they land in the server's flat folder)."""
    text = script.read_text(encoding="utf-8")
    return {Path(m).name for m in re.findall(r'"\$[CP]/([^"]+\.py)"', text)}


def missing_modules(script: Path) -> list[str]:
    """The module files the script's copied modules import and the script does not copy."""
    copied = copied_files(script)
    needed: set[str] = set()
    for name in sorted(copied):
        for folder in LOCAL_FOLDERS:
            if (folder / name).is_file():
                needed |= local_imports(folder / name)
    return sorted(f"{name}.py" for name in needed if f"{name}.py" not in copied)


def test_the_labels_bootstrap_copies_every_module_it_needs() -> None:
    assert "analytic_hessians.py" in copied_files(BOOTSTRAP), "the bootstrap no longer copies the label route; rewrite this test"
    assert not missing_modules(BOOTSTRAP), f"{BOOTSTRAP.name} does not copy {missing_modules(BOOTSTRAP)}"


def test_the_reader_finds_the_imports_it_is_meant_to() -> None:
    found = local_imports(CORPUS / "analytic_hessians.py")
    assert {"apt", "constants", "vibrations", "library_log"} <= found
    assert "numpy" not in found and "pyscf" not in found        # packages are the server's own problem, not the copy line's


def test_the_reader_finds_a_function_level_import() -> None:
    """`grid_response_blocked` is imported inside a function, because it needs a newer pyscf than the route itself."""
    assert "grid_response_blocked" in local_imports(CORPUS / "analytic_hessians.py")


def test_a_script_that_copies_too_little_is_caught(tmp_path: Path) -> None:
    script = tmp_path / "deploy.sh"
    script.write_text('scp "$C/analytic_hessians.py" root@host:/root/\n', encoding="utf-8")
    assert copied_files(script) == {"analytic_hessians.py"}
    assert "vibrations.py" in missing_modules(script)      # the check fires on the set that broke this morning
