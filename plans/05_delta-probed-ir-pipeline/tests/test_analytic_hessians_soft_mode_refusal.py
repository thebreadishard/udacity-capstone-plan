"""TASKS 226: on a pyscf older than 2.15.0 the label route cannot repair a soft mode. A molecule with one is refused by name before the
repair imports grid_response_blocked -- its soft modes, the pyscf version, the interpreter, the lane and the remedy -- the other folders
go on, the exit status is EXIT_SOFT_MODE_DEFERRED, and --reuse-existing on 2.15.0 finishes the pending Hessians. No quantum chemistry:
the version, the modes and the per-molecule work are monkeypatched. Imports pyscf, so it runs in WSL (qc05 or qc215)."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
pyscf = pytest.importorskip("pyscf")
AH = pytest.importorskip("analytic_hessians")

WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.995, 1.008, 1.008]}
HESSIANS = {"b3lyp": np.eye(9), "wb97x": np.eye(9)}
SOFT_CM = 12.34


def _run(**changes) -> "AH.LabelsRun":
    settings = dict(grid=(50, 194), charge=0, spin=0, compare_only=False, apt=False, stamp={}, lane="labels_lane.sh 2")
    return AH.LabelsRun(**(settings | changes))


def _modes(monkeypatch, soft: bool) -> None:
    """Every label gets one mode at SOFT_CM (or none below the threshold) and the directions follow."""
    omega = np.array([SOFT_CM if soft else 150.0, 1600.0, 3700.0])
    monkeypatch.setattr(AH, "vibrational_modes", lambda H, m, x: AH.Modes(omega_cm=omega, vectors=np.eye(9)[:, :3]))
    monkeypatch.setattr(AH, "low_mode_directions", lambda sets, below: np.eye(9)[:, :1] if soft else np.zeros((9, 0)))


@pytest.mark.parametrize(("text", "expected"), [("2.14.0", (2, 14, 0)), ("2.15.0", (2, 15, 0)), ("2.15", (2, 15, 0)),
                                                ("2.15.0.dev0", (2, 15, 0)), ("3.0.1+git", (3, 0, 1))])
def test_versions_parse(text, expected):
    assert AH.parse_version(text) == expected


def test_a_version_without_major_and_minor_is_refused():
    with pytest.raises(ValueError, match=r"major\.minor"):
        AH.parse_version("unknown")


@pytest.mark.parametrize(("version", "available"), [("2.14.0", False), ("2.15.0", True), ("2.16.1", True)])
def test_the_repair_is_available_from_2_15(monkeypatch, version, available):
    monkeypatch.setattr(pyscf, "__version__", version)
    assert AH.repair_available() is available


def test_a_soft_mode_on_2_14_is_refused_with_molecule_modes_environment_lane_and_remedy(monkeypatch):
    monkeypatch.setattr(pyscf, "__version__", "2.14.0")
    _modes(monkeypatch, soft=True)
    with pytest.raises(AH.SoftModeNeedsNewerPyscf) as caught:
        AH.refuse_without_repair("molecules/B_2804096c51", WATER, HESSIANS, _run())
    message = str(caught.value)
    for part in ("molecules/B_2804096c51", "1 direction(s) below 20 cm-1", f"b3lyp {SOFT_CM:.2f}", f"wb97x {SOFT_CM:.2f}",
                 "pyscf >= 2.15.0", "runs pyscf 2.14.0", sys.executable, "labels_lane.sh 2", "qc215", "--reuse-existing"):
        assert part in message, part


def test_an_unnamed_lane_says_how_to_name_it(monkeypatch):
    monkeypatch.setattr(pyscf, "__version__", "2.14.0")
    _modes(monkeypatch, soft=True)
    with pytest.raises(AH.SoftModeNeedsNewerPyscf, match="not named: pass --lane"):
        AH.refuse_without_repair("d", WATER, HESSIANS, _run(lane=None))


@pytest.mark.parametrize(("version", "soft"), [("2.14.0", False), ("2.15.0", True)])
def test_no_refusal_without_a_soft_mode_or_with_the_repair_available(monkeypatch, version, soft):
    monkeypatch.setattr(pyscf, "__version__", version)
    _modes(monkeypatch, soft=soft)
    AH.refuse_without_repair("d", WATER, HESSIANS, _run())


def test_an_empty_lane_is_refused_before_any_molecule():
    with pytest.raises(ValueError, match="--lane is empty"):
        _run(lane=" ")


def _labels_on_disk(monkeypatch, tmp_path) -> Path:
    """A molecule folder whose two analytic labels 'compute' instantly; the repair and the label writer must not be reached."""
    d = tmp_path / "B_2804096c51"
    d.mkdir()
    (d / "geometry.json").write_text(json.dumps(WATER), encoding="utf-8")
    monkeypatch.setattr(AH, "labels_mol", lambda *args: None)
    monkeypatch.setattr(AH, "analytic_label", lambda d, mol, tag, xc, run, g, errors: (HESSIANS[tag], -76.0, 1.0, False))
    for name in ("repair_low_modes", "write_labels"):
        monkeypatch.setattr(AH, name, lambda *args, _n=name: pytest.fail(f"{_n} reached after the refusal"))
    return d


def test_the_refusal_comes_before_the_repair_and_its_import(monkeypatch, tmp_path):
    monkeypatch.setattr(pyscf, "__version__", "2.14.0")
    monkeypatch.setitem(sys.modules, "grid_response_blocked", None)      # an import of it would raise ImportError
    _modes(monkeypatch, soft=True)
    d = _labels_on_disk(monkeypatch, tmp_path)
    with pytest.raises(AH.SoftModeNeedsNewerPyscf, match="SOFT MODE DEFERRED"):
        AH.process_molecule(str(d), _run(), None)


def _main(monkeypatch, tmp_path, outcomes: dict) -> tuple[int, list[str]]:
    """main over the folders of `outcomes` ({name: 'deferred' | 'apt' | 'ok'}); returns its exit status and the folders it finished."""
    done = []

    def molecule(d, run, lib_log):
        kind = outcomes[Path(d).name]
        if kind == "deferred":
            raise AH.SoftModeNeedsNewerPyscf(f"{d}: SOFT MODE DEFERRED TO PYSCF 2.15")
        done.append(Path(d).name)
        return ["APT failed"] if kind == "apt" else []

    dirs = []
    for name in outcomes:
        (tmp_path / name).mkdir()
        dirs.append(str(tmp_path / name))
    monkeypatch.setattr(AH, "process_molecule", molecule)
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", *dirs, "--threads", "1", "--lane", "test 0"])
    try:
        AH.main()
    except SystemExit as stop:
        return int(stop.code), done
    return 0, done


def test_a_deferred_molecule_exits_with_its_own_code_and_the_others_go_on(monkeypatch, tmp_path, capsys):
    status, done = _main(monkeypatch, tmp_path, {"A_soft": "deferred", "B_fine": "ok"})
    assert status == AH.EXIT_SOFT_MODE_DEFERRED == 4 and done == ["B_fine"]
    assert "A_soft: SOFT MODE DEFERRED" in capsys.readouterr().out


def test_a_failed_apt_outranks_a_deferral(monkeypatch, tmp_path):
    assert _main(monkeypatch, tmp_path, {"A_soft": "deferred", "B_apt": "apt"})[0] == 3


def test_a_clean_call_exits_zero(monkeypatch, tmp_path):
    assert _main(monkeypatch, tmp_path, {"A": "ok", "B": "ok"}) == (0, ["A", "B"])


def _pending_file(tmp_path) -> Path:
    d = tmp_path / "mol"
    d.mkdir()
    H = np.arange(81, dtype=float).reshape(9, 9)
    AH.save_hessian(str(d), "b3lyp", H, H, np.zeros(9), -76.0, _run(), pending=True)
    return d


def test_reuse_on_2_15_finishes_a_pending_file(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(pyscf, "__version__", "2.15.0")
    d = _pending_file(tmp_path)
    Hc, e, _seconds, repaired_already = AH.analytic_label(str(d), None, "b3lyp", "b3lyp", _run(reuse_existing=True), WATER, [])
    assert np.array_equal(Hc, np.arange(81, dtype=float).reshape(9, 9)) and e == -76.0 and not repaired_already
    assert "(its low-mode repair follows)" in capsys.readouterr().out


@pytest.mark.parametrize(("version", "changes", "reason"), [
    ("2.14.0", {"reuse_existing": True}, "this is 2.14.0"),
    ("2.15.0", {"compare_only": True}, "--compare-only reads finished labels only"),
])
def test_a_pending_file_is_refused_where_the_repair_cannot_follow(monkeypatch, tmp_path, version, changes, reason):
    monkeypatch.setattr(pyscf, "__version__", version)
    d = _pending_file(tmp_path)
    with pytest.raises(RuntimeError, match="written before its low-mode repair") as caught:
        AH.analytic_label(str(d), None, "b3lyp", "b3lyp", _run(**changes), WATER, [])
    assert reason in str(caught.value)


@pytest.mark.parametrize("script", ["labels_lane.sh", "labels_batch_ccx53.sh"])
def test_the_lane_scripts_read_the_same_exit_code(script):
    text = (PLAN / "probes" / script).read_text(encoding="utf-8")
    assert f"DEFERRED_RC={AH.EXIT_SOFT_MODE_DEFERRED} " in text and "--lane " in text
