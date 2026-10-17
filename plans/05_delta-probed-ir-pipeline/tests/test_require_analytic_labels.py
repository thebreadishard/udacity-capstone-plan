"""probes/require_analytic_labels.py: counts only molecules with both analytic Hessians inside the size bound, refuses below the minimum."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import require_analytic_labels as ral


def _mol(corpus: Path, name: str, atoms: int, labels: tuple[str, ...]) -> None:
    d = corpus / name
    d.mkdir(parents=True)
    (d / "geometry.json").write_text(json.dumps({"symbols": ["C"] * atoms}), encoding="utf-8")
    for label in labels:
        (d / label).write_bytes(b"x")


def test_counts_both_labels_within_the_bound_and_refuses_below_the_minimum(tmp_path, capsys):
    _mol(tmp_path, "small_both", 12, ral.LABELS)
    _mol(tmp_path, "small_one", 12, ral.LABELS[:1])
    _mol(tmp_path, "large_both", 30, ral.LABELS)
    _mol(tmp_path, "edge_both", 22, ral.LABELS)
    assert ral.count_labelled(tmp_path, 22) == 2
    assert ral.main(["--min", "2", "--max-atoms", "22", "--corpus", str(tmp_path)]) == 0
    assert ral.main(["--min", "3", "--max-atoms", "22", "--corpus", str(tmp_path)]) == 1
    assert "REFUSED: 2 molecules" in capsys.readouterr().out
