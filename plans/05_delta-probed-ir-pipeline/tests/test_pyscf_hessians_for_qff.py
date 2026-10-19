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
