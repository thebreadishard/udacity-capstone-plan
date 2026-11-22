"""`corpus/check_results.py` on a stand-in corpus: a done row with analytic labels only is counted, not read for the frequency lists
it does not have; a row with the lists is still checked."""
import csv
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "corpus"))
import check_results as C

FIELDS = ["id", "layer", "name", "n_atoms", "status", "note"]


def corpus(tmp_path: Path, results: dict[str, dict]) -> None:
    with (tmp_path / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for mol_id in results:
            w.writerow({"id": mol_id, "layer": "B", "name": mol_id, "n_atoms": 3, "status": "done", "note": ""})
    for mol_id, result in results.items():
        (tmp_path / "molecules" / mol_id).mkdir(parents=True)
        (tmp_path / "molecules" / mol_id / "result.json").write_text(json.dumps(result))


def run(tmp_path: Path, monkeypatch) -> int:
    monkeypatch.setattr(C, "HERE", tmp_path)
    monkeypatch.setattr(sys, "argv", ["check_results.py"])
    with pytest.raises(SystemExit) as e:
        C.main()
    return e.value.code


def lists(n: int) -> dict:
    freq = [0.0] * 6 + [1600.0, 3700.0, 3800.0][: n - 6]
    return {"freq_b3lyp_cm": freq, "freq_wb97x_cm": freq, "timings_s": {"total": 3600.0}}


def test_an_analytic_only_row_is_counted_and_a_full_row_is_checked(tmp_path, monkeypatch, capsys):
    corpus(tmp_path, {"B_full": lists(9), "B_analytic": {"status": "done", "labels": "analytic_only"}})
    assert run(tmp_path, monkeypatch) == 0
    assert "layer B: done 2, failed 0" in (out := capsys.readouterr().out) and "analytic labels only 1 (not checked here)" in out


def test_a_full_row_with_a_wrong_list_length_still_fails(tmp_path, monkeypatch, capsys):
    corpus(tmp_path, {"B_short": lists(8)})
    assert run(tmp_path, monkeypatch) == 1
    assert "WRONG LENGTH: B_short" in capsys.readouterr().out
