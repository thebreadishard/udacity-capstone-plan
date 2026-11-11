"""probes/reoptimise_at_label_settings.py (TASKS 49): the lowest mode by two routes, the push only along a negative mode, the settings refused
before any SCF, the dry run writes nothing, and a water re-optimisation at a small grid writes a folder analytic_hessians.py labels with no
imaginary mode. Needs pyscf and geomeTRIC, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
pytest.importorskip("geometric")
RLS = pytest.importorskip("reoptimise_at_label_settings")
AH = pytest.importorskip("analytic_hessians")

# water slightly off its B3LYP/6-31G* minimum, so the optimisation has work to do
WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.25], [0.0, 1.50, -0.90], [0.0, -1.40, -0.88]],
         "masses_amu": [15.995, 1.008, 1.008], "charge": 0, "multiplicity": 1, "optimised_at": "B3LYP"}
SMALL_GRID = "50,194"


def _source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    d = tmp_path / "src" / "W_water"
    d.mkdir(parents=True)
    (d / "geometry.json").write_text(json.dumps(WATER))
    (d / "job.json").write_text(json.dumps({"id": "W_water", "layer": "D"}))
    (d / "result.json").write_text(json.dumps({"id": "W_water", "status": "done", "labels": "analytic_only", "n_imaginary_b3lyp": 0,
                                               "peak_rss_gb": 1.0}))
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", str(d), "--threads", "1", "--grid", SMALL_GRID, "--functionals", "b3lyp",
                                      "--no-apt"])
    AH.main()
    return d


def _hessian_with_lowest(freq_cm: float) -> tuple[np.ndarray, np.ndarray]:
    """A projected Hessian of a 3-atom molecule whose mass-weighted spectrum is six zeros and three chosen frequencies."""
    masses = np.array([15.995, 1.008, 1.008])
    rng = np.random.default_rng(0)
    Q, _ = np.linalg.qr(rng.normal(size=(9, 9)))
    freqs = np.array([0.0] * 6 + [freq_cm, 1600.0, 3700.0])
    w = np.sign(freqs) * (freqs / RLS.AU2CM) ** 2 * RLS.AMU2AU
    sm = np.sqrt(np.repeat(masses, 3))
    return (Q @ np.diag(w) @ Q.T) * np.outer(sm, sm), masses


def test_lowest_mode_agrees_with_the_corpus_route_and_is_scaled_to_one_bohr():
    H, masses = _hessian_with_lowest(-7.5)
    freq, mode = RLS.lowest_mode(H, masses)
    assert freq == pytest.approx(-7.5, abs=1e-6)
    assert np.linalg.norm(mode, axis=1).max() == pytest.approx(1.0)


def test_the_push_follows_only_a_negative_mode():
    for freq, moved in ((-7.5, True), (12.0, False)):
        H, _ = _hessian_with_lowest(freq)
        start, push = RLS.start_geometry(WATER, H, 0.05)
        shift = np.abs(np.array(start["coords_bohr"]) - np.array(WATER["coords_bohr"])).max()
        assert bool(shift > 0) == moved
        assert push["push_bohr_largest_atom"] == (0.05 if moved else 0.0)


def test_settings_are_refused_before_any_scf(tmp_path, monkeypatch):
    src = _source(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="source"):
        RLS.parse_args([str(src), str(src)])
    with pytest.raises(ValueError, match="push"):
        RLS.parse_args([str(src), str(tmp_path / "out"), "--push-bohr", "-1"])
    done = tmp_path / "done"
    done.mkdir()
    (done / "geometry.json").write_text("{}")
    with pytest.raises(ValueError, match="already holds"):
        RLS.parse_args([str(src), str(done)])
    with pytest.raises(ValueError, match="has no"):
        RLS.parse_args([str(tmp_path), str(tmp_path / "out")])


def test_the_dry_run_writes_nothing(tmp_path, monkeypatch, capsys):
    src = _source(tmp_path, monkeypatch)
    out = tmp_path / "out" / "W_water"
    RLS.main([str(src), str(out), "--threads", "1", "--grid", SMALL_GRID, "--dry-run"])
    assert "basis functions" in capsys.readouterr().out
    assert not out.exists()


def test_water_reoptimised_and_labelled_has_no_imaginary_mode(tmp_path, monkeypatch):
    src = _source(tmp_path, monkeypatch)
    before = (src / "geometry.json").read_text()
    out = tmp_path / "out" / "W_water"
    RLS.main([str(src), str(out), "--threads", "1", "--grid", SMALL_GRID])
    assert (src / "geometry.json").read_text() == before
    result = json.loads((out / "result.json").read_text())
    assert result["labels"] == "analytic_only" and "n_imaginary_b3lyp" not in result and "peak_rss_gb" not in result
    assert result["reoptimised_at_label_settings"]["steps"] >= 2
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", str(out), "--threads", "1", "--grid", SMALL_GRID, "--functionals", "b3lyp",
                                      "--no-apt"])
    AH.main()
    assert json.loads((out / "result.json").read_text())["n_imaginary_b3lyp"] == 0
    with pytest.raises(ValueError, match="already holds"):
        RLS.parse_args([str(src), str(out)])
