"""probes/anharmonic_second_field.py and probes/frame_match.py (TASKS 211, part A of the measurement on a substituted
molecule): the start record of a second force field, the frame two geometries share, and the reference built on a stored
field — which, on benzene's inputs, must be the reference of 19 Nov 2026 that the first-run checks read. No force field
is computed: the stored ones are read.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anharmonic_second_field as SF  # noqa: E402
import frame_match as FM  # noqa: E402

RESULTS = PLAN / "probes" / "results_m1"
SYMBOLS = ["N", "C", "C", "H"]
COORDS = np.array([[0.0, 0.0, 0.0], [2.2, 0.0, 0.0], [3.5, 2.1, 0.0], [5.4, 2.0, 0.3]])


TURN = np.array([[np.cos(0.7), -np.sin(0.7), 0.0], [np.sin(0.7), np.cos(0.7), 0.0], [0.0, 0.0, 1.0]])


def turned(coords: np.ndarray) -> np.ndarray:
    return coords @ TURN + np.array([1.0, -2.0, 0.5])


def test_a_turned_and_shifted_copy_lies_on_the_original_and_its_modes_come_back() -> None:
    frame = FM.frame_onto((SYMBOLS, turned(COORDS)), (SYMBOLS, COORDS), "the copy")
    assert frame.rms_bohr < 1e-12
    q = np.random.default_rng(0).normal(size=(12, 5))
    q_turned = np.einsum("nim,ij->njm", q.reshape(4, 3, 5), TURN).reshape(12, 5)      # a displacement turns with the atoms and does not shift
    assert np.allclose(frame.modes(q_turned), q, atol=1e-12)


def test_another_order_and_a_far_geometry_are_refused() -> None:
    with pytest.raises(ValueError, match="in the result's order"):
        FM.frame_onto((SYMBOLS[::-1], COORDS[::-1]), (SYMBOLS, COORDS), "reversed")
    far = COORDS + np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.6, 0.0]])
    with pytest.raises(ValueError, match="another geometry"):
        FM.frame_onto((SYMBOLS, far), (SYMBOLS, COORDS), "moved")
    assert FM.frame_onto((["n", "c", "c", "h"], COORDS), (SYMBOLS, COORDS), "lower case").rms_bohr < 1e-12


def geometry_file(path: Path, coords: np.ndarray) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"symbols": SYMBOLS, "coords_bohr": coords.tolist(), "masses_amu": [14.0, 12.0, 12.0, 1.0]}), encoding="utf-8")
    return path


def test_the_start_is_the_candidate_farthest_from_the_runs_minimum(tmp_path: Path) -> None:
    run = geometry_file(tmp_path / "run" / "geometry.json", COORDS).parent
    near = geometry_file(tmp_path / "near" / "geometry.json", turned(COORDS + np.array([[0.0, 0.0, 0.0]] * 3 + [[0.001, 0.0, 0.0]])))
    far = geometry_file(tmp_path / "far" / "geometry.json", COORDS + np.array([[0.0, 0.0, 0.0]] * 3 + [[0.0, 0.004, 0.0]]))
    record = SF.start(run, [near, far], tmp_path / "second" / "G")
    distances = record["rms_bohr_from_the_run"]
    assert record["chosen"] == far.as_posix() and distances[far.as_posix()] > distances[near.as_posix()] > 0.0
    ref = json.loads((tmp_path / "second" / "G" / "ref.json").read_text(encoding="utf-8"))
    assert ref["molecule"]["symbols"] == SYMBOLS and np.allclose(np.reshape(ref["molecule"]["geometry"], (4, 3)), np.reshape(
        json.loads(far.read_text(encoding="utf-8"))["coords_bohr"], (4, 3)))
    assert "return_result" not in ref and json.loads((tmp_path / "second" / "G" / "start.json").read_text(encoding="utf-8")) == record
    with pytest.raises(ValueError, match="never overwritten"):
        SF.start(run, [near, far], tmp_path / "second" / "G")


def test_the_committed_start_of_benzonitrile_is_corpus_a_at_its_recorded_distance() -> None:
    folder = RESULTS / "anharmonic_step_substituted_2026-11-20" / "second_minimum" / "G"
    record = json.loads((folder / "start.json").read_text(encoding="utf-8"))
    assert record["chosen"].endswith("A_3100da3761/geometry.json")
    assert sorted(round(v, 5) for v in record["rms_bohr_from_the_run"].values()) == [0.00037, 0.00057]
    assert len(json.loads((folder / "ref.json").read_text(encoding="utf-8"))["molecule"]["symbols"]) == 13


def test_the_stand_in_field_is_taken_back_also_after_an_error() -> None:
    real = SF.AN.force_field
    with SF.stand_in_field("a field", {"source": "stored"}):
        assert SF.AN.force_field("name", Path(), None) == ("a field", {"source": "stored"})
    assert SF.AN.force_field is real
    with pytest.raises(RuntimeError, match="inside"), SF.stand_in_field("a field", {}):
        raise RuntimeError("inside")
    assert SF.AN.force_field is real


def test_a_reference_needs_the_runs_files_and_a_field_that_is_not_noisy(tmp_path: Path) -> None:
    run, x_dir, label = tmp_path / "run", tmp_path / "X", tmp_path / "label.json"
    run.mkdir()
    x_dir.mkdir()
    for path in (*(run / name for name in SF.COPIED), x_dir / "ref.json", x_dir / "qff_report.npz"):
        path.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match=r"label\.json is missing"):
        SF.ReferenceConfig(run, x_dir, label, tmp_path / "out")
    label.write_text("{}", encoding="utf-8")
    SF.ReferenceConfig(run, x_dir, label, tmp_path / "out")
    (x_dir / "NOISY").touch()
    with pytest.raises(ValueError, match="NOISY"):
        SF.ReferenceConfig(run, x_dir, label, tmp_path / "out")


def test_on_benzenes_inputs_the_reference_is_the_one_of_19_november(tmp_path: Path) -> None:
    """The benzene reference the first-run checks read was built by the 16 Nov demo script on the run's steps 1-5; this tool on
    the same run and the same stored field must give every band the same position, step, bar and reason."""
    cfg_paths = (RESULTS / "pipeline_benzene_anharmonic_v3_2026-11-19" / "benzene", RESULTS / "s2_xtb_2026-10-18" / "xtb" / "A_8448043181" / "X",
                 RESULTS / "labels_domain_2026-11-13" / "S2" / "gvpt2_x" / "A_8448043181.json")
    stored = RESULTS / "anharmonic_reference_v14release_v3_2026-11-19" / "benzene" / "pipeline.json"
    for path in (*cfg_paths, stored):
        if not path.exists():
            pytest.skip(f"data not present: {path}")
    built = SF.build(SF.ReferenceConfig(*cfg_paths, tmp_path / "reference"))
    assert built == (tmp_path / "reference" / "benzene").resolve()
    mine = json.loads((built / "pipeline.json").read_text(encoding="utf-8"))["spectra"]
    theirs = json.loads(stored.read_text(encoding="utf-8"))["spectra"]
    assert mine["network"]["sticks"] == theirs["network"]["sticks"] and len(mine["network"]["sticks"]) == 30
    assert mine["anharmonic"]["bands"] == theirs["anharmonic"]["bands"] and mine["anharmonic"]["artefact"] == theirs["anharmonic"]["artefact"]
    with pytest.raises(ValueError, match="never overwritten"):
        SF.build(SF.ReferenceConfig(*cfg_paths, tmp_path / "reference"))
