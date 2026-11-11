"""probes/butterfly_scan.py (TASKS 49): the registered verdict on synthetic energy curves (planar, double well, flat, mirror noise), the
settings refused before any geometry is read, the plane split, and a bent trans-glyoxal scanned at two small grids, whose verdict must be
PLANAR. Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
pytest.importorskip("pyscf")
BFS = pytest.importorskip("butterfly_scan")
AH = pytest.importorskip("analytic_hessians")

COARSE, FINE = (50, 194), (75, 302)
ANGSTROM = 1.8897261246
# trans-glyoxal (planar at its minimum), each atom lifted out of the plane in a butterfly pattern
GLYOXAL_XY = [("C", 0.0, 0.762), ("C", 0.0, -0.762), ("O", 1.04, 1.40), ("O", -1.04, -1.40), ("H", -0.95, 1.32), ("H", 0.95, -1.32)]
LIFT_BOHR = [0.0, 0.0, 0.15, 0.15, -0.15, -0.15]
MASSES = {"C": 12.0, "O": 15.99491461956, "H": 1.00782503207}


def _curve(fn) -> dict[float, float]:
    return {s: fn(s) for s in BFS.SCALES}


def test_verdict_planar_double_well_and_undecided():
    planar = _curve(lambda s: 1e-6 * s**2)
    well = _curve(lambda s: -2e-6 * s**2 + 1e-6 * s**4)              # minimum at s = 1, below planar by 1e-6
    flat = _curve(lambda s: 1e-12 * s**2)
    assert BFS.verdict({COARSE: planar, FINE: planar})[0] == "PLANAR"
    assert BFS.verdict({COARSE: well, FINE: well})[0] == "DOUBLE WELL"
    assert BFS.verdict({COARSE: well, FINE: planar})[0] == "UNDECIDED"  # the grids disagree on the sign
    noisy = dict(flat)
    noisy[-1.0] += 1e-9                                                    # mirror images apart by more than the curve's own depth
    call, noise = BFS.verdict({COARSE: noisy, FINE: noisy})
    assert call == "UNDECIDED"
    assert noise == pytest.approx(1e-9, rel=1e-3)


def test_settings_refused_before_reading(tmp_path: Path):
    base = {"molecule": tmp_path / "absent", "out": tmp_path / "out", "threads": 1, "max_memory_mb": 1000, "dry_run": False}
    with pytest.raises(ValueError, match="functional"):
        BFS.ScanConfig(xc_tag="pbe", grids=(COARSE, FINE), **base)
    with pytest.raises(ValueError, match="two distinct grids"):
        BFS.ScanConfig(xc_tag="b3lyp", grids=(COARSE,), **base)
    with pytest.raises(ValueError, match="two distinct grids"):
        BFS.ScanConfig(xc_tag="b3lyp", grids=(COARSE, COARSE), **base)


def _glyoxal() -> dict:
    coords = [[x * ANGSTROM, y * ANGSTROM, lift] for (_s, x, y), lift in zip(GLYOXAL_XY, LIFT_BOHR, strict=True)]
    symbols = [s for s, _x, _y in GLYOXAL_XY]
    return {"symbols": symbols, "coords_bohr": coords, "masses_amu": [MASSES[s] for s in symbols], "charge": 0, "multiplicity": 1}


def test_plane_split_removes_the_heights():
    g = _glyoxal()
    coords = np.array(g["coords_bohr"])
    heavy = np.array([s != "H" for s in g["symbols"]])
    planar, out = BFS.plane_split(coords, heavy)
    np.testing.assert_allclose(planar + out, coords, atol=1e-12)
    centre = planar[heavy].mean(axis=0)
    assert np.abs(np.linalg.svd(planar - centre)[1][2]) < 1e-10      # the planar geometry has no third dimension


def test_glyoxal_scan_is_planar(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    d = tmp_path / "G_glyoxal"
    d.mkdir()
    (d / "geometry.json").write_text(json.dumps(_glyoxal()))
    (d / "job.json").write_text(json.dumps({"id": "G_glyoxal", "layer": "D"}))
    (d / "result.json").write_text(json.dumps({"id": "G_glyoxal", "status": "done", "labels": "analytic_only", "peak_rss_gb": 1.0}))
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", str(d), "--threads", "1", "--grid", "50,194", "--functionals", "b3lyp",
                                      "--no-apt"])
    AH.main()
    out = tmp_path / "scan"
    BFS.main([str(d), str(out), "--grids", "50,194", "75,302", "--threads", "1", "--max-memory", "2000"])
    record = json.loads((out / "scan.json").read_text(encoding="utf-8"))
    assert record["verdict"] == "PLANAR"
    assert len(list(out.glob("point_*.json"))) == 2 * len(BFS.SCALES)
    BFS.main([str(d), str(out), "--grids", "50,194", "75,302", "--threads", "1", "--max-memory", "2000"])   # a resume keeps every point
    assert json.loads((out / "scan.json").read_text(encoding="utf-8"))["dE_cm"] == record["dE_cm"]
