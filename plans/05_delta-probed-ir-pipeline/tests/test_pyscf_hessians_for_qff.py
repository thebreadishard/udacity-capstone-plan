"""probes/pyscf_hessians_for_qff.py --guess-from-previous (19 Oct 2026): each displaced SCF starts from the previous Hessian's converged
density. On two displaced water geometries the Hessians and energies equal those from pyscf's default guess to the SCF's own tolerance.
Needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
SCRIPT = Path(__file__).resolve().parents[1] / "probes" / "pyscf_hessians_for_qff.py"
WATER = np.array([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]])


def _stubs(d: Path):
    d.mkdir()
    for k, shift in enumerate((0.05, -0.05)):
        x = WATER.copy()
        x[0, 2] += shift
        (d / f"w{k}.json").write_text(json.dumps({"driver": "hessian", "molecule": {"symbols": ["O", "H", "H"], "geometry": x.ravel().tolist()}}))


def _run(stubs: Path, out: Path, *extra: str) -> dict:
    subprocess.run([sys.executable, str(SCRIPT), str(stubs), str(out), "--basis", "6-31g*", "--grid", "50,194", "--threads", "1", *extra],
                   check=True, capture_output=True, text=True)
    return {p.name: json.loads(p.read_text()) for p in sorted(out.glob("w*.json"))}


def test_a_start_from_the_previous_density_gives_the_same_hessians(tmp_path):
    _stubs(tmp_path / "stubs")
    plain = _run(tmp_path / "stubs", tmp_path / "plain")
    reused = _run(tmp_path / "stubs", tmp_path / "reused", "--guess-from-previous")
    assert plain.keys() == reused.keys() == {"w0.json", "w1.json"}
    for name in plain:
        assert abs(plain[name]["properties"]["return_energy"] - reused[name]["properties"]["return_energy"]) < 1e-9
        assert np.abs(np.array(plain[name]["return_result"]) - np.array(reused[name]["return_result"])).max() < 1e-6


def _stubs3(d: Path) -> None:
    d.mkdir()
    for k, shift in enumerate((0.05, 0.0, -0.05)):
        x = WATER.copy()
        x[0, 2] += shift
        (d / f"w{k}.json").write_text(json.dumps({"driver": "hessian", "molecule": {"symbols": ["O", "H", "H"], "geometry": x.ravel().tolist()}}))
    (d / "notes.json").write_text(json.dumps({"driver": "energy"}))          # not a Hessian request: never a start


def test_resume_start_is_the_geometry_before_the_first_missing_one(tmp_path):
    sys.path.insert(0, str(SCRIPT.parent))
    import pyscf_hessians_for_qff as Q
    stubs, out = tmp_path / "stubs", tmp_path / "out"
    _stubs3(stubs)
    out.mkdir()
    files = sorted(str(p) for p in stubs.glob("*.json"))
    assert Q.resume_start(files, str(out)) is None                          # fresh: nothing to resume from
    (out / "w0.json").write_text("{}")
    assert Path(Q.resume_start(files, str(out))).name == "w0.json"
    (out / "w1.json").write_text("{}")
    (out / "w2.json").write_text("{}")
    assert Q.resume_start(files, str(out)) is None                          # finished


def test_a_resumed_run_starts_from_the_neighbour_and_equals_a_fresh_one(tmp_path):
    _stubs3(tmp_path / "stubs")
    fresh = _run(tmp_path / "stubs", tmp_path / "fresh", "--guess-from-previous")
    resumed_dir = tmp_path / "resumed"
    resumed_dir.mkdir()
    (resumed_dir / "w0.json").write_text(json.dumps(fresh["w0.json"]))    # a call that stopped after its first geometry
    p = subprocess.run([sys.executable, str(SCRIPT), str(tmp_path / "stubs"), str(resumed_dir), "--basis", "6-31g*", "--grid", "50,194",
                        "--threads", "1", "--guess-from-previous"], check=True, capture_output=True, text=True)
    assert "resumed: the start density from an SCF at w0.json" in p.stdout
    resumed = {q.name: json.loads(q.read_text()) for q in sorted(resumed_dir.glob("w*.json"))}
    for name in ("w1.json", "w2.json"):
        assert abs(fresh[name]["properties"]["return_energy"] - resumed[name]["properties"]["return_energy"]) < 1e-9
        assert np.abs(np.array(fresh[name]["return_result"]) - np.array(resumed[name]["return_result"])).max() < 1e-6
