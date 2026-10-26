"""probes/ids_have_labels.py: analytic labels by default; '--labels any' also takes a complete FD pair; a half pair or no geometry is missing."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "probes"))
import ids_have_labels as ihl


def _mol(root: Path, name: str, files: tuple[str, ...]) -> None:
    (root / name).mkdir(parents=True)
    for f in files:
        (root / name / f).write_bytes(b"x")


def test_analytic_by_default_and_any_takes_a_complete_fd_pair(tmp_path, capsys):
    g = ihl.GEOMETRY
    _mol(tmp_path, "analytic", (g, "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"))
    _mol(tmp_path, "fd", (g, "hessian_b3lyp.npz", "hessian_wb97x.npz"))
    _mol(tmp_path, "half", (g, "hessian_b3lyp.npz"))
    _mol(tmp_path, "nogeom", ("hessian_b3lyp.npz", "hessian_wb97x.npz"))
    ids = tmp_path / "ids.txt"
    ids.write_text("# a comment\nanalytic\nfd\n", encoding="utf-8")
    assert set(ihl.missing(["analytic", "fd"], tmp_path)) == {"fd"}
    assert ihl.missing(["analytic", "fd"], tmp_path, "any") == {}
    assert set(ihl.missing(["half", "nogeom"], tmp_path, "any")) == {"half", "nogeom"}
    assert ihl.main([str(ids), "--labels", "any", "--molecules", str(tmp_path)]) == 0
    assert ihl.main([str(ids), "--molecules", str(tmp_path)]) == 1
    assert "labelled (analytic) 1/2; missing fd" in capsys.readouterr().out


def test_max_missing_admits_named_gaps_and_refuses_beyond(tmp_path, capsys):
    ids = tmp_path / "ids.txt"
    ids.write_text("a\nb\nc\n", encoding="utf-8")
    for name in ("a", "b"):
        folder = tmp_path / "mol" / name
        folder.mkdir(parents=True)
        (folder / ihl.GEOMETRY).write_text("{}", encoding="utf-8")
        for f in ihl.LABEL_SETS["analytic"][0]:
            (folder / f).write_bytes(b"x")
    args = [str(ids), "--molecules", str(tmp_path / "mol")]
    assert ihl.main(args) == 1
    assert ihl.main([*args, "--max-missing", "1"]) == 0
    assert "labelled (analytic) 2/3; missing c (geometry.json/" in capsys.readouterr().out
    with pytest.raises(SystemExit):
        ihl.main([*args, "--max-missing", "-1"])
