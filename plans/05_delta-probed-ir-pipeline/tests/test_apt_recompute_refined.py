"""probes/apt_recompute_refined.py (TASKS 44 (b), 12 Oct 2026): the refined APT of a labels molecule whose file came from route C before the
refinement, without the Hessian; the input folder is not touched, a refined file that passed is refused, and since 13 Oct 2026 (78293273) a
refined file that failed the guard is recomputed. Since 1 Nov 2026 route B files are redone, a Hessian without its charge and spin
fields is refused, --check-only computes nothing and --max-memory reaches pyscf.
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


def _refined_copy(fetched, folder, passed):
    """A copy of the fetched folder whose APT file is marked as the refined route, with the guard's verdict `passed`."""
    z = dict(np.load(fetched / AH.APT_FILE))
    folder.mkdir()
    (folder / "geometry.json").write_text(json.dumps(WATER))
    (folder / "hessian_b3lyp_analytic.npz").write_bytes((fetched / "hessian_b3lyp_analytic.npz").read_bytes())
    z["route"] = np.array("hessian_response_refined")
    z["passed"] = np.array(passed)
    np.savez_compressed(folder / AH.APT_FILE, **z)
    return folder


def test_a_refined_file_that_passed_is_refused(fetched, tmp_path):
    other = _refined_copy(fetched, tmp_path / "other", passed=True)
    with pytest.raises(ValueError, match="neither an unrefined route"):
        R.recompute(str(other), str(tmp_path / "out"), grid=GRID)


def test_a_refined_file_that_failed_the_guard_is_recomputed(fetched, tmp_path):
    failed = _refined_copy(fetched, tmp_path / "failed", passed=False)
    row = R.recompute(str(failed), str(tmp_path / "out"), grid=GRID)
    assert row["passed"] and row["residual_after"] <= AH.CPHF_BOUND


def _copy_with(fetched, folder, route=None, drop_hessian_fields=()):
    """A copy of the fetched folder with the APT file's route replaced and the named fields left out of the B3LYP Hessian file."""
    folder.mkdir()
    (folder / "geometry.json").write_text(json.dumps(WATER))
    z = dict(np.load(fetched / AH.APT_FILE))
    if route is not None:
        z["route"] = np.array(route)
    np.savez_compressed(folder / AH.APT_FILE, **z)
    h = {k: v for k, v in np.load(fetched / "hessian_b3lyp_analytic.npz").items() if k not in drop_hessian_fields}
    np.savez_compressed(folder / "hessian_b3lyp_analytic.npz", **h)
    return folder


def test_a_route_b_file_is_recomputed(fetched, tmp_path):
    route_b = _copy_with(fetched, tmp_path / "route_b", route="cphf")
    row = R.recompute(str(route_b), str(tmp_path / "out"), grid=GRID)
    assert row["passed"] and str(np.load(tmp_path / "out" / AH.APT_FILE)["route"]) == "hessian_response_refined"


def test_a_hessian_without_charge_and_spin_is_refused(fetched, tmp_path):
    old = _copy_with(fetched, tmp_path / "old_hessian", drop_hessian_fields=("charge", "spin"))
    with pytest.raises(ValueError, match="predates its charge and spin fields"):
        R.source_files(str(old), GRID)


def test_check_only_computes_nothing(fetched, tmp_path, monkeypatch, capsys):
    route_b = _copy_with(fetched, tmp_path / "route_b", route="cphf")
    monkeypatch.setattr(R, "source_files", lambda src, grid=GRID: (np.load(Path(src) / AH.APT_FILE), None))
    monkeypatch.setattr(R, "recompute", lambda *a, **k: pytest.fail("--check-only computed"))
    monkeypatch.setattr(sys, "argv", ["apt_recompute_refined.py", str(route_b), "--out", str(tmp_path / "out"), "--check-only"])
    R.main()
    assert "route_b: route cphf, to be refined" in capsys.readouterr().out and not (tmp_path / "out").exists()


def test_max_memory_reaches_pyscf(fetched, tmp_path, monkeypatch):
    seen = []
    labels_mol = AH.labels_mol

    def spy(g, log, charge, spin, max_memory):
        seen.append(max_memory)
        return labels_mol(g, log, charge, spin, max_memory)

    monkeypatch.setattr(AH, "labels_mol", spy)
    R.recompute(str(fetched), str(tmp_path / "out"), grid=GRID, max_memory=1234)
    assert seen == [1234]


def test_an_error_before_the_apt_file_is_written_is_raised_with_its_cause(fetched, tmp_path, monkeypatch):
    """1 Nov 2026: A_428228e5a5's step died on the missing file, and the error that kept write_apt from writing it was lost."""
    def broken(*args, **kwargs):
        raise ValueError("operands could not be broadcast")
    monkeypatch.setattr(AH, "write_apt", broken)
    with pytest.raises(RuntimeError, match=r"raised before writing .*operands could not be broadcast") as info:
        R.recompute(str(fetched), str(tmp_path / "W_water"), grid=GRID)
    assert isinstance(info.value.__cause__, ValueError)


def test_write_apt_may_log_through_the_hessian_object(fetched, tmp_path, monkeypatch):
    """2 Nov 2026: A_428228e5a5's refinement logged a direct-SCF timer line after the pyscf log was closed."""
    from pyscf.lib import logger
    real = AH.write_apt

    def logging(out_dir, hobj, *args):
        logger.info(hobj.base, "a line from inside write_apt")
        return real(out_dir, hobj, *args)
    monkeypatch.setattr(AH, "write_apt", logging)
    out = tmp_path / "W_water"
    R.recompute(str(fetched), str(out), grid=GRID)
    assert "a line from inside write_apt" in (out / AH.PYSCF_LOG_NAME).read_text(encoding="utf-8")


def test_height_change_is_relative_to_the_strongest_old_band():
    assert R.height_change([100.0, 10.0], [99.0, 10.5]) == pytest.approx(0.01)
