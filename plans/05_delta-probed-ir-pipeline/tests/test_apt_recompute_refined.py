"""probes/apt_recompute_refined.py (TASKS 44 (b), 12 Oct 2026): the refined APT of a labels molecule whose file came from route C before the
refinement, without the Hessian; the input folder is not touched, a refined file is not recomputed, and a file of another route is refused.
Water at a small grid; needs pyscf, so it runs in WSL and is skipped elsewhere."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import analytic_hessians as AH  # noqa: E402
import apt_recompute_refined as R  # noqa: E402

WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.995, 1.008, 1.008]}
GRID = (50, 194)


@pytest.fixture(scope="module")
def fetched(tmp_path_factory):
    """A labels folder as the server leaves it before the install: both Hessians and an APT file marked as unrefined route C."""
    d = tmp_path_factory.mktemp("labels") / "W_water"
    d.mkdir()
    (d / "geometry.json").write_text(json.dumps(WATER))
    mp = pytest.MonkeyPatch()
    mp.setattr(sys, "argv", ["analytic_hessians.py", str(d), "--threads", "1", "--grid", ",".join(map(str, GRID))])
    AH.main()
    mp.undo()
    z = dict(np.load(d / AH.APT_FILE))
    z["route"] = np.array("hessian_response")
    z["apt"] = z["apt"] + 1e-4                       # the old file's APT, off as pyscf's early-stopped response leaves it
    np.savez_compressed(d / AH.APT_FILE, **z)
    return d


def test_the_recompute_writes_a_refined_file_elsewhere_and_reports_the_change(fetched, tmp_path):
    before = (fetched / AH.APT_FILE).read_bytes()
    row = R.recompute(str(fetched), str(tmp_path / "W_water"), grid=GRID)
    new = np.load(tmp_path / "W_water" / AH.APT_FILE)
    assert row["passed"] and str(new["route"]) == "hessian_response_refined" and row["residual_after"] <= AH.CPHF_BOUND
    assert abs(row["apt_change_max"] - 1e-4) < 1e-6 and row["id"] == "W_water"
    assert (fetched / AH.APT_FILE).read_bytes() == before


def test_a_file_of_another_route_is_refused(fetched, tmp_path):
    z = dict(np.load(fetched / AH.APT_FILE))
    other = tmp_path / "other"
    other.mkdir()
    (other / "geometry.json").write_text(json.dumps(WATER))
    (other / "hessian_b3lyp_analytic.npz").write_bytes((fetched / "hessian_b3lyp_analytic.npz").read_bytes())
    z["route"] = np.array("hessian_response_refined")
    np.savez_compressed(other / AH.APT_FILE, **z)
    with pytest.raises(ValueError, match="not the unrefined route C"):
        R.recompute(str(other), str(tmp_path / "out"), grid=GRID)


def test_height_change_is_relative_to_the_strongest_old_band():
    assert R.height_change([100.0, 10.0], [99.0, 10.5]) == pytest.approx(0.01)
