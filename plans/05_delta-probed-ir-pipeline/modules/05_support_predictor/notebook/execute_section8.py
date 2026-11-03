"""Append-only execution of the notebook's new follow-up cells (24 September 2026).

The cells already in the executed notebook keep their saved outputs: the module shows what was learned in dated follow-up sections, and a
top-to-bottom run would replace the earlier outputs. A fresh kernel executes the cheap setup cells (imports, data load, split, config), the
*definitions* of the two heavy cells (functions only, no training), and then the new cells, whose outputs are stored. The generator can still
execute everything top to bottom (`make_notebook.py`); this script is the path when only new cells were added. What it did is written into the
notebook's metadata and printed for PROVENANCE.

Usage: python execute_section8.py --from-cell N [--setup 3,5,9,11] [--defs 13,18] [--refresh-new-markdown]

`--refresh-new-markdown` (28 Sep 2026, section 11) rebuilds the cell list once more after the execution, with the result files the new cells
wrote, and copies the *markdown* cells of the new section from that rebuild, so a reading the builder derives from a result file lands in the
executed notebook instead of its placeholder. The cell list is built by `make_notebook.py --draft-to` in the module's own folder: the builder
reads the module's result files (since section 12), so a scratch copy of it cannot build.
"""
import argparse
import datetime as dt
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import nbformat
from nbclient import NotebookClient

HERE = Path(__file__).resolve().parent
NOTEBOOK = HERE / "deep_learning.ipynb"


def defs_only(source: str) -> str:
    """The leading part of a cell that consists of imports and def/class blocks — everything before the first top-level statement that computes."""
    out = []
    for line in source.split("\n"):
        top = line and not line.startswith((" ", "\t", "#", ")", "]", "}"))
        if top and not line.startswith(("def ", "class ", "import ", "from ", "@")):
            break
        out.append(line)
    return "\n".join(out)


def cell_list(text: str) -> list[int]:
    """'3,5,9' -> [3, 5, 9]; an empty string is no cells."""
    return [int(x) for x in text.split(",") if x.strip()]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="execute only the notebook's new cells, keeping the stored outputs of the others")
    ap.add_argument("--from-cell", type=int, required=True, help="the first new cell = the number of cells in the executed notebook")
    ap.add_argument("--setup", type=cell_list, default=[3, 5, 9, 11], help="setup cells rerun in the kernel (imports, data, split, config)")
    ap.add_argument("--defs", type=cell_list, default=[13, 18], help="heavy cells whose definitions only are rerun (training, evaluation)")
    ap.add_argument("--refresh-new-markdown", action="store_true")
    return ap.parse_args(argv)


def release_env(stored: nbformat.NotebookNode) -> dict[str, str]:
    """The environment for the builder, with the executed run's release so the regenerated data cell matches the stored one."""
    for cell in stored.cells[:8]:
        found = re.search(r'corpus_release" / "([^"]+)\.npz"', cell.source)
        if found:
            return dict(os.environ, M05_RELEASE=found.group(1))
    return dict(os.environ)


def build_draft(env: dict[str, str], scratch: Path) -> nbformat.NotebookNode:
    """The builder's current cell list, unexecuted, written to a scratch file so the executed notebook is not touched."""
    draft = scratch / "deep_learning.draft.ipynb"
    subprocess.run([sys.executable, str(HERE / "make_notebook.py"), "--draft-to", str(draft)], cwd=HERE, check=True,
                   capture_output=True, env=env)
    return nbformat.read(draft, as_version=4)


def merge_stored(stored: nbformat.NotebookNode, new: nbformat.NotebookNode, from_cell: int) -> None:
    """Puts the stored cells, outputs included, in front of the new ones; refuses when a stored code cell's source has changed."""
    n_old = len(stored.cells)
    if len(new.cells) <= n_old:
        raise SystemExit(f"no new cells: the builder makes {len(new.cells)}, the executed notebook has {n_old}")
    if from_cell != n_old:
        raise SystemExit(f"--from-cell should be {n_old}, the number of cells in the executed notebook")
    for i in range(n_old):
        if new.cells[i].cell_type == "code" and new.cells[i].source != stored.cells[i].source:
            raise SystemExit(f"code cell {i} changed since the executed run: run the full generator instead")
        new.cells[i] = stored.cells[i]


def run_unstored(client: NotebookClient, nb: nbformat.NotebookNode, index: int, source: str) -> None:
    """Runs source in the kernel without keeping its output. nbclient stores the executed cell object at nb.cells[index], so the real
    cell is put back (25 Sep 2026: the temporary copy had replaced it, sources truncated and outputs lost)."""
    keep = nb.cells[index]
    client.execute_cell(nbformat.v4.new_code_cell(source), index, store_history=False)
    nb.cells[index] = keep


def execute_new(nb: nbformat.NotebookNode, n_old: int, setup: list[int], defs: list[int]) -> None:
    client = NotebookClient(nb, timeout=7200, kernel_name="python3", resources={"metadata": {"path": str(HERE)}})
    with client.setup_kernel():
        for i in setup:
            print(f"setup cell {i}", flush=True)
            run_unstored(client, nb, i, nb.cells[i].source)
        for i in defs:
            print(f"definitions of cell {i}", flush=True)
            run_unstored(client, nb, i, defs_only(nb.cells[i].source))
        for i in range(n_old, len(nb.cells)):
            if nb.cells[i].cell_type == "code":
                print(f"new cell {i}: {nb.cells[i].source.split(chr(10))[0][:60]}", flush=True)
                client.execute_cell(nb.cells[i], i)


def refresh_markdown(nb: nbformat.NotebookNode, n_old: int, env: dict[str, str], scratch: Path) -> None:
    rebuilt = build_draft(env, scratch)
    if len(rebuilt.cells) != len(nb.cells):
        raise SystemExit(f"the rebuild has {len(rebuilt.cells)} cells, the executed draft {len(nb.cells)}")
    for i in range(n_old, len(nb.cells)):
        if nb.cells[i].cell_type == "markdown" and rebuilt.cells[i].source != nb.cells[i].source:
            print(f"markdown cell {i} refreshed from the result files", flush=True)
            nb.cells[i].source = rebuilt.cells[i].source


def last_execution(stored: nbformat.NotebookNode) -> str | None:
    """The latest cell execution time recorded in the stored notebook: when its kept outputs were made."""
    stamps = [c.metadata.get("execution", {}).get("iopub.status.idle") for c in stored.cells if c.cell_type == "code"]
    stamps = [s for s in stamps if s]
    return max(stamps) if stamps else None


def write_atomically(nb: nbformat.NotebookNode, path: Path) -> None:
    tmp = path.with_suffix(".writing.ipynb")
    nbformat.write(nb, tmp)
    os.replace(tmp, path)


def main() -> None:
    a = parse_args()
    stored = nbformat.read(NOTEBOOK, as_version=4)
    n_old = len(stored.cells)
    env = release_env(stored)
    started = dt.datetime.now(dt.UTC)
    with tempfile.TemporaryDirectory(prefix="m05_nb_") as scratch_dir:
        scratch = Path(scratch_dir)
        new = build_draft(env, scratch)
        merge_stored(stored, new, a.from_cell)
        execute_new(new, n_old, a.setup, a.defs)
        if a.refresh_new_markdown:
            refresh_markdown(new, n_old, env, scratch)
    note = {"method": "append-only", "date_utc": started.strftime("%Y-%m-%dT%H:%M:%SZ"), "executed_new_cells": list(range(n_old, len(new.cells))),
            "setup_cells_rerun": a.setup, "definition_cells_rerun": a.defs, "kept_outputs_last_executed_utc": last_execution(stored),
            "previous_append_only_execution": stored.metadata.get("append_only_execution")}
    new.metadata["append_only_execution"] = note
    write_atomically(new, NOTEBOOK)
    print("written", NOTEBOOK, note)


if __name__ == "__main__":
    main()
