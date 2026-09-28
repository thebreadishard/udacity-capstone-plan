"""Append-only execution of the notebook's new follow-up cells (24 September 2026).

The cells of sections 1–7 ran on 23 September and their results do not change, so they are not rerun: their saved outputs are kept. A fresh kernel
executes the cheap setup cells (imports, data load, split, config), the *definitions* of the two heavy cells (functions only, no training), and then
the new cells (section 8), whose outputs are stored. The generator can still execute everything top to bottom (`make_notebook.py`); this script is the
economical path when only new cells were added. What it did is written into the notebook's metadata and printed for PROVENANCE.

Usage: python execute_section8.py [--from-cell 27] [--setup 2,4,8,10] [--defs 12,17] [--refresh-new-markdown]

28 Sep 2026 (section 11): `--refresh-new-markdown` rebuilds the cell list once more after the execution, with the result files the new cells
wrote beside the generator, and copies the *markdown* cells of the new section from that rebuild — so a reading the builder derives from a
result file (the pattern of section 6) lands in the executed notebook instead of its "not yet executed" placeholder.
"""
import argparse
import datetime as dt
import os
import re
import shutil
import subprocess
import sys
import tempfile

import nbformat
from nbclient import NotebookClient

HERE = os.path.dirname(os.path.abspath(__file__))


def defs_only(source):
    """The leading part of a cell that consists of imports and def/class blocks — everything before the first top-level statement that computes."""
    out = []
    for line in source.split("\n"):
        top = line and not line.startswith((" ", "\t", "#", ")", "]", "}"))
        if top and not line.startswith(("def ", "class ", "import ", "from ", "@")):
            break
        out.append(line)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--from-cell", type=int, default=27); ap.add_argument("--setup", default="2,4,8,10"); ap.add_argument("--defs", default="12,17")
    ap.add_argument("--refresh-new-markdown", action="store_true")
    a = ap.parse_args()
    old_path = os.path.join(HERE, "deep_learning.ipynb"); old = nbformat.read(old_path, as_version=4)
    # build the new cell list with the generator, in a scratch copy so the executed notebook is not overwritten
    scratch = tempfile.mkdtemp(prefix="m05_nb_"); shutil.copy(os.path.join(HERE, "make_notebook.py"), scratch)
    rel = re.search(r'corpus_release" / "([^"]+)\.npz"', old.cells[2].source)   # the executed run's release, so the regenerated cell 2 matches it
    env = dict(os.environ, M05_RELEASE=rel.group(1)) if rel else dict(os.environ)
    subprocess.run([sys.executable, "make_notebook.py", "--no-execute"], cwd=scratch, check=True, capture_output=True, env=env)
    new = nbformat.read(os.path.join(scratch, "deep_learning.ipynb"), as_version=4)
    n_old = len(old.cells); assert len(new.cells) > n_old, "no new cells"
    for i in range(n_old):
        if new.cells[i].cell_type == "code":
            assert new.cells[i].source == old.cells[i].source, f"code cell {i} changed since the executed run — run the full generator instead"
        # markdown cells are kept as run: the section-6 summary text is generated from results.json at generation time and may lag the final numbers
    for i in range(n_old):
        new.cells[i] = old.cells[i]                          # keep the saved outputs and execution metadata of the run of 23 September
    assert a.from_cell == n_old, f"--from-cell should be {n_old}"
    setup = [int(x) for x in a.setup.split(",")]; defs = [int(x) for x in a.defs.split(",")]
    client = NotebookClient(new, timeout=7200, kernel_name="python3", resources={"metadata": {"path": HERE}})
    t0 = dt.datetime.now(dt.UTC)
    with client.setup_kernel():
        for i in setup:
            print(f"setup cell {i}", flush=True); keep = new.cells[i]; client.execute_cell(nbformat.v4.new_code_cell(new.cells[i].source), i, store_history=False); new.cells[i] = keep
        for i in defs:
            # 25 Sep 2026: nbclient stores the executed cell object at nb.cells[i]; without `keep` the temporary copy replaced the real cell (sources truncated, outputs lost on 24 Sep)
            print(f"definitions of cell {i}", flush=True); keep = new.cells[i]; client.execute_cell(nbformat.v4.new_code_cell(defs_only(new.cells[i].source)), i, store_history=False); new.cells[i] = keep
        for i in range(n_old, len(new.cells)):
            if new.cells[i].cell_type == "code":
                print(f"new cell {i}: {new.cells[i].source.split(chr(10))[0][:60]}", flush=True); client.execute_cell(new.cells[i], i)
    if a.refresh_new_markdown:
        scratch2 = tempfile.mkdtemp(prefix="m05_nb_"); shutil.copy(os.path.join(HERE, "make_notebook.py"), scratch2)
        for f in os.listdir(HERE):
            if f.startswith("results") and f.endswith(".json"): shutil.copy(os.path.join(HERE, f), scratch2)
        subprocess.run([sys.executable, "make_notebook.py", "--no-execute"], cwd=scratch2, check=True, capture_output=True, env=env)
        rebuilt = nbformat.read(os.path.join(scratch2, "deep_learning.ipynb"), as_version=4); assert len(rebuilt.cells) == len(new.cells)
        for i in range(n_old, len(new.cells)):
            if new.cells[i].cell_type == "markdown" and rebuilt.cells[i].source != new.cells[i].source:
                print(f"markdown cell {i} refreshed from the result files", flush=True); new.cells[i].source = rebuilt.cells[i].source
        shutil.rmtree(scratch2, ignore_errors=True)
    note = dict(method="append-only", date_utc=t0.strftime("%Y-%m-%dT%H:%M:%SZ"), executed_new_cells=list(range(n_old, len(new.cells))), setup_cells_rerun=setup,
                definition_cells_rerun=defs, sections_1_to_7_outputs_from=old.metadata.get("executed_utc", "the run of 23 September 2026"),
                previous_append_only_execution=old.metadata.get("append_only_execution"))
    new.metadata["append_only_execution"] = note
    nbformat.write(new, old_path); shutil.rmtree(scratch, ignore_errors=True)
    print("written", old_path, note)


if __name__ == "__main__":
    main()
