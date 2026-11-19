"""TASKS 226: where pyscf cannot repair a soft mode (older than 2.15.0, or without the helpers grid_response_blocked imports), the label
route refuses a molecule with one by name before the repair imports grid_response_blocked -- its soft modes, the reason, the interpreter,
the lane and the remedy -- the other folders go on, and the exit status is EXIT_SOFT_MODE_DEFERRED (3 when an APT failed, naming the
deferral too). --reuse-existing reads a pending file and the same check decides again. No quantum chemistry: the version, the helpers'
module, the modes and the per-molecule work are monkeypatched. Imports pyscf, so it runs in WSL (qc05 and qc215)."""
import json
import sys
import types
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
pyscf = pytest.importorskip("pyscf")
AH = pytest.importorskip("analytic_hessians")

WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.995, 1.008, 1.008]}
HESSIANS = {"b3lyp": np.eye(9), "wb97x": np.eye(9)}       # every mode far above 20 cm-1
SOFT_CM = 12.34


def _run(**changes) -> "AH.LabelsRun":
    settings = dict(grid=(50, 194), charge=0, spin=0, compare_only=False, apt=False, stamp={}, lane="labels_lane.sh 2")
    return AH.LabelsRun(**(settings | changes))


def _environment(monkeypatch, version: str, helpers: bool) -> None:
    """pyscf's version, and whether the repair's module imports (None in sys.modules makes an import raise ImportError)."""
    monkeypatch.setattr(pyscf, "__version__", version)
    monkeypatch.setitem(sys.modules, AH.REPAIR_MODULE, types.ModuleType(AH.REPAIR_MODULE) if helpers else None)


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


@pytest.mark.parametrize(("version", "helpers", "reason"), [
    ("2.14.0", True, "pyscf 2.14.0 is older than 2.15.0"),
    ("2.15.0.dev0", False, "pyscf 2.15.0.dev0 lacks what grid_response_blocked needs"),   # a development build without the helpers
    ("2.15.0", True, ""),
])
def test_the_blocker_names_the_version_or_the_missing_helpers(monkeypatch, version, helpers, reason):
    _environment(monkeypatch, version, helpers)
    blocker = AH.repair_blocker()
    assert blocker.startswith(reason) and bool(blocker) == bool(reason)


def test_the_real_environment_can_repair_exactly_from_2_15():
    assert (AH.repair_blocker() == "") == (AH.parse_version(pyscf.__version__) >= AH.REPAIR_MIN_PYSCF)


def test_a_soft_mode_on_2_14_is_refused_with_molecule_modes_environment_lane_and_remedy(monkeypatch):
    _environment(monkeypatch, "2.14.0", helpers=False)
    _modes(monkeypatch, soft=True)
    message = AH.soft_mode_refusal("molecules/B_2804096c51", WATER, HESSIANS, _run())
    for part in ("molecules/B_2804096c51", "SOFT MODE DEFERRED", "1 direction(s) below 20 cm-1", f"b3lyp {SOFT_CM:.2f}",
                 f"wb97x {SOFT_CM:.2f}", "pyscf 2.14.0 is older than 2.15.0", sys.executable, "labels_lane.sh 2",
                 "2 analytic Hessian(s) (b3lyp, wb97x)", "qc215", "--reuse-existing"):
        assert part in message, part


def test_the_refusal_counts_the_hessians_it_leaves(monkeypatch):
    _environment(monkeypatch, "2.14.0", helpers=False)
    _modes(monkeypatch, soft=True)
    assert "1 analytic Hessian(s) (b3lyp) are on disk" in AH.soft_mode_refusal("d", WATER, {"b3lyp": np.eye(9)}, _run())


def test_an_unnamed_lane_says_how_to_name_it(monkeypatch):
    _environment(monkeypatch, "2.14.0", helpers=False)
    _modes(monkeypatch, soft=True)
    assert "not named: pass --lane" in AH.soft_mode_refusal("d", WATER, HESSIANS, _run(lane=None))


@pytest.mark.parametrize(("version", "helpers", "soft"), [("2.14.0", False, False), ("2.15.0", True, True)])
def test_no_refusal_without_a_soft_mode_or_with_the_repair_available(monkeypatch, version, helpers, soft):
    _environment(monkeypatch, version, helpers)
    _modes(monkeypatch, soft=soft)
    assert AH.soft_mode_refusal("d", WATER, HESSIANS, _run()) == ""


def test_an_empty_lane_is_refused_before_any_molecule():
    with pytest.raises(ValueError, match="--lane is empty"):
        _run(lane=" ")


def _folder(tmp_path) -> Path:
    d = tmp_path / "B_2804096c51"
    d.mkdir()
    (d / "geometry.json").write_text(json.dumps(WATER), encoding="utf-8")
    return d


def test_the_refusal_comes_before_the_repair_and_keeps_the_apt_errors(monkeypatch, tmp_path):
    _environment(monkeypatch, "2.14.0", helpers=False)
    _modes(monkeypatch, soft=True)
    d = _folder(tmp_path)

    def label(d, mol, tag, xc, run, g, errors):  # noqa: PLR0913  analytic_label's own signature, which it stands in for
        if tag == "b3lyp":
            errors.append(f"{d}: APT sum rule too large")
        return HESSIANS[tag], -76.0, 1.0, False

    monkeypatch.setattr(AH, "labels_mol", lambda *args: None)
    monkeypatch.setattr(AH, "analytic_label", label)
    for name in ("repair_low_modes", "write_labels"):
        monkeypatch.setattr(AH, name, lambda *args, _n=name: pytest.fail(f"{_n} reached after the refusal"))
    with pytest.raises(AH.SoftModeNeedsNewerPyscf, match="SOFT MODE DEFERRED") as caught:
        AH.process_molecule(str(d), _run(), None)
    assert caught.value.apt_errors == [f"{d}: APT sum rule too large"]


def _main(monkeypatch, tmp_path, outcomes: dict) -> tuple[int, list[str]]:
    """main over the folders of `outcomes` ({name: 'deferred' | 'deferred_apt' | 'apt' | 'ok'}); its exit status and the folders done."""
    done = []

    def molecule(d, run, lib_log):
        kind = outcomes[Path(d).name]
        if kind.startswith("deferred"):
            raise AH.SoftModeNeedsNewerPyscf(f"{d}: SOFT MODE DEFERRED TO PYSCF 2.15", ["APT failed"] if kind == "deferred_apt" else [])
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


@pytest.mark.parametrize("outcomes", [{"A_soft": "deferred", "B_apt": "apt"}, {"A_soft": "deferred_apt"}])
def test_a_failed_apt_outranks_a_deferral_and_names_it(monkeypatch, tmp_path, capsys, outcomes):
    assert _main(monkeypatch, tmp_path, outcomes)[0] == 3
    assert "exit 3 for a failed APT; also SOFT MODE DEFERRED TO PYSCF 2.15: " in capsys.readouterr().out


def test_a_clean_call_exits_zero(monkeypatch, tmp_path):
    assert _main(monkeypatch, tmp_path, {"A": "ok", "B": "ok"}) == (0, ["A", "B"])


def _pending_files(d: Path) -> None:
    for tag, H in HESSIANS.items():
        AH.save_hessian(str(d), tag, H, H, np.zeros(9), -76.0, _run(), pending=True)


@pytest.mark.parametrize(("version", "helpers"), [("2.14.0", False), ("2.15.0", True)])
def test_reuse_reads_a_pending_file_on_any_pyscf(monkeypatch, tmp_path, capsys, version, helpers):
    _environment(monkeypatch, version, helpers)
    d = _folder(tmp_path)
    _pending_files(d)
    Hc, e, _seconds, repaired_already = AH.analytic_label(str(d), None, "b3lyp", "b3lyp", _run(reuse_existing=True), WATER, [])
    assert np.array_equal(Hc, HESSIANS["b3lyp"]) and e == -76.0 and not repaired_already
    assert "(its low-mode repair follows)" in capsys.readouterr().out


def test_compare_only_refuses_a_pending_file(monkeypatch, tmp_path):
    _environment(monkeypatch, "2.15.0", helpers=True)
    d = _folder(tmp_path)
    _pending_files(d)
    with pytest.raises(RuntimeError, match="--compare-only reads finished labels only"):
        AH.analytic_label(str(d), None, "b3lyp", "b3lyp", _run(compare_only=True), WATER, [])


def test_a_pending_folder_without_a_soft_mode_finishes_on_2_14(monkeypatch, tmp_path):
    """A crash between the pending save and the label files: 2.14 finishes it, and the repair's module is never imported."""
    _environment(monkeypatch, "2.14.0", helpers=False)
    monkeypatch.setattr(AH, "labels_mol", lambda *args: None)
    d = _folder(tmp_path)
    _pending_files(d)
    assert AH.process_molecule(str(d), _run(reuse_existing=True), None) == []
    for tag in HESSIANS:
        with np.load(d / f"hessian_{tag}_analytic.npz") as z:
            assert "low_mode_pending" not in z.files and "low_mode_patch" not in z.files
    assert set(json.loads((d / "analytic_check.json").read_text(encoding="utf-8"))) == set(HESSIANS)


def test_a_pending_folder_with_a_soft_mode_is_deferred_on_2_14(monkeypatch, tmp_path):
    _environment(monkeypatch, "2.14.0", helpers=False)
    _modes(monkeypatch, soft=True)
    d = _folder(tmp_path)
    _pending_files(d)
    monkeypatch.setattr(AH, "labels_mol", lambda *args: None)
    monkeypatch.setattr(sys, "argv", ["analytic_hessians.py", str(d), "--threads", "1", "--reuse-existing"])
    with pytest.raises(SystemExit) as stop:
        AH.main()
    assert stop.value.code == AH.EXIT_SOFT_MODE_DEFERRED
    with np.load(d / "hessian_b3lyp_analytic.npz") as z:
        assert "low_mode_pending" in z.files                     # kept for the 2.15 rerun


@pytest.mark.parametrize("script", ["labels_lane.sh", "labels_batch_ccx53.sh"])
def test_the_lane_scripts_read_the_same_exit_code(script):
    text = (PLAN / "probes" / script).read_text(encoding="utf-8")
    assert f"DEFERRED_RC={AH.EXIT_SOFT_MODE_DEFERRED} " in text and "--lane " in text
