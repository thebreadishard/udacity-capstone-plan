"""Module 05's append-only executor: the stored cells keep their outputs, a changed stored code cell is refused, and only the leading
imports and definitions of a heavy cell are rerun."""
import importlib.util
from pathlib import Path

import nbformat
import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "notebook" / "execute_section8.py"
spec = importlib.util.spec_from_file_location("execute_section8", SCRIPT)
ex = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ex)


def notebook(sources: list[str]) -> nbformat.NotebookNode:
    return nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(s) for s in sources])


def test_merge_keeps_stored_outputs():
    stored = notebook(["a = 1", "b = 2"])
    stored.cells[0].outputs = [nbformat.v4.new_output("stream", text="kept")]
    new = notebook(["a = 1", "b = 2", "c = 3"])
    ex.merge_stored(stored, new, from_cell=2)
    assert new.cells[0].outputs[0]["text"] == "kept"
    assert new.cells[2].source == "c = 3"


def test_merge_refuses_a_changed_code_cell():
    with pytest.raises(SystemExit, match="code cell 1 changed"):
        ex.merge_stored(notebook(["a = 1", "b = 2"]), notebook(["a = 1", "b = 5", "c = 3"]), from_cell=2)


def test_merge_refuses_a_wrong_from_cell():
    with pytest.raises(SystemExit, match="--from-cell should be 2"):
        ex.merge_stored(notebook(["a = 1", "b = 2"]), notebook(["a = 1", "b = 2", "c = 3"]), from_cell=1)


def test_defs_only_stops_at_the_first_computation():
    source = "import os\ndef f(x):\n    return x\nresult = f(1)\ndef g():\n    pass"
    assert ex.defs_only(source) == "import os\ndef f(x):\n    return x"


def test_cell_lists():
    assert ex.parse_args(["--from-cell", "85"]).setup == [3, 5, 9, 11]
    assert ex.parse_args(["--from-cell", "85", "--defs", ""]).defs == []
