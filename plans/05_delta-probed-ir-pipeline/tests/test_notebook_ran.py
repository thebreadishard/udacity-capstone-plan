"""tools/notebook_ran.py: an executed notebook counts as run only with every code cell executed and no error output."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import notebook_ran


def _notebook(tmp_path: Path, cells: list[dict]) -> Path:
    path = tmp_path / "nb.ipynb"
    path.write_text(json.dumps({"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}), encoding="utf-8")
    return path


def _code(source: str, count: int | None, outputs: list[dict] | None = None) -> dict:
    return {"cell_type": "code", "source": [source], "execution_count": count, "outputs": outputs or [], "metadata": {}}


def test_a_fully_executed_notebook_passes(tmp_path):
    path = _notebook(tmp_path, [{"cell_type": "markdown", "source": ["# t"], "metadata": {}}, _code("x = 1", 1), _code("   ", None)])
    assert notebook_ran.check(path) == []
    assert notebook_ran.main([str(path)]) == 0


def test_an_unexecuted_cell_fails_even_without_errors(tmp_path):
    path = _notebook(tmp_path, [_code("x = 1", 1), _code("y = 2", None)])
    assert notebook_ran.check(path) == ["cell 1 not executed"]
    assert notebook_ran.main([str(path)]) == 1


def test_an_error_output_fails(tmp_path):
    error = {"output_type": "error", "ename": "FileNotFoundError", "evalue": "../out/x.csv", "traceback": []}
    path = _notebook(tmp_path, [_code("open('../out/x.csv')", 1, [error])])
    assert notebook_ran.check(path) == ["cell 0: FileNotFoundError: ../out/x.csv"]


def test_wrong_usage_is_refused():
    assert notebook_ran.main([]) == 2
