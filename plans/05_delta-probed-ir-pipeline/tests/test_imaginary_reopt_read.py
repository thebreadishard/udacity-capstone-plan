"""probes/imaginary_reopt_read.py on synthetic records (TASKS 215): the acceptance rule's every branch, damaged and cut-off folders,
and the lane logs' markers, from folders and logs written here.

The molecule is a bent triatomic held by three pair springs, so its Hessian has exactly three vibrational modes and six rigid
motions at zero; a negative spring gives one imaginary mode. Numpy only."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import imaginary_reopt_read as R  # noqa: E402  the probes folder is put on the path above

SYMBOLS = ["O", "H", "H"]
MASSES = [15.995, 1.008, 1.008]
COORDS = np.array([[0.0, 0.0, 0.22], [0.0, 1.43, -0.89], [0.0, -1.43, -0.89]])   # bohr; both O-H bonded, H-H not
BOTH = dict.fromkeys(R.LABEL_TAGS, 0)
NOT_PENDING = dict.fromkeys(R.LABEL_TAGS, False)
APT_FIELDS = {"passed": {"passed": True}, "failed": {"passed": False}, "unmarked": {}, "text": {"passed": "True"}}
STAMP = "2026-11-20 23:{:02d}:00"


def spring_hessian(coords: np.ndarray, k_hh: float = 0.1) -> np.ndarray:
    """Pair springs O-H, O-H (0.5 hartree/bohr²) and H-H (k_hh): positive vibrations, or one imaginary mode when k_hh is negative enough."""
    H = np.zeros((9, 9))
    for i, j, k in ((0, 1, 0.5), (0, 2, 0.5), (1, 2, k_hh)):
        u = (coords[i] - coords[j]) / np.linalg.norm(coords[i] - coords[j])
        b = np.zeros(9)
        b[3 * i:3 * i + 3], b[3 * j:3 * j + 3] = u, -u
        H += k * np.outer(b, b)
    return H


def write_folder(folder: Path, coords: np.ndarray = COORDS, *, k_hh: float = 0.1,  # noqa: PLR0913  one switch per branch of the rule
                 counts: dict | None = None, apt: str = "passed",
                 pending: tuple[str, ...] = (), symbols: list[str] | None = None) -> Path:
    """A folder as the lane leaves it. `apt`: a key of APT_FIELDS (the file as analytic_hessians.write_apt marks it), or 'absent'."""
    folder.mkdir(parents=True)
    geometry = {"symbols": symbols or SYMBOLS, "masses_amu": MASSES, "coords_bohr": coords.tolist()}
    (folder / "geometry.json").write_text(json.dumps(geometry), encoding="utf-8")
    (folder / "result.json").write_text(json.dumps({f"n_imaginary_{t}": n for t, n in (BOTH if counts is None else counts).items()}),
                                        encoding="utf-8")
    for tag in R.LABEL_TAGS:
        extra = {"low_mode_pending": True} if tag in pending else {}
        np.savez(folder / f"hessian_{tag}_analytic.npz", H_raw=spring_hessian(coords, k_hh), **extra)
    if apt != "absent":
        np.savez_compressed(folder / R.APT_FILE, apt=np.zeros(1), **APT_FIELDS[apt])
    return folder


def write_log(path: Path, lines: list[str]) -> Path:
    """A lane log: a line starting with '@' becomes the lane's marker for molecule M with the next minute's stamp, any other line is output."""
    text = [f"=== (IRL) M: {line[1:]} {STAMP.format(n)}" if line.startswith("@") else line for n, line in enumerate(lines)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(["=== (IRL) lane start: 1 molecules from ids.txt, 8 threads 2026-11-20 22:00:00", *text]) + "\n", encoding="utf-8")
    return path


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """A corpus folder whose label carries one imaginary mode."""
    write_folder(tmp_path / "corpus" / "M", k_hh=-0.4)
    return tmp_path / "corpus"


def read(corpus: Path, tmp_path: Path, **kwargs) -> R.Verdict:
    write_folder(tmp_path / "new" / "M", **kwargs)
    return R.read_molecule("M", corpus, tmp_path / "new")


def read_with_log(corpus: Path, tmp_path: Path, lines: list[str]) -> R.Verdict:
    events = R.lane_events([write_log(tmp_path / "logs" / "lane0.log", lines)])
    return R.read_molecule("M", corpus, tmp_path / "new", events)


def test_the_synthetic_corpus_label_is_imaginary_and_the_repaired_one_is_not(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path)
    assert all(v.lowest_before_cm[t] < 0 for t in R.LABEL_TAGS)
    assert all(v.lowest_after_cm[t] > 0 for t in R.LABEL_TAGS)
    assert v.accepted and v.state == R.ACCEPTED and v.reason == "" and v.changed_bonds == [] and not v.conformer_flag
    assert v.rms_bohr == pytest.approx(0.0, abs=1e-12)


def test_a_rotated_and_shifted_copy_is_the_same_geometry(corpus: Path, tmp_path: Path) -> None:
    c, s = np.cos(0.7), np.sin(0.7)
    moved = COORDS @ np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) + np.array([1.0, -2.0, 0.5])
    v = read(corpus, tmp_path, coords=moved)
    assert v.accepted and v.rms_bohr == pytest.approx(0.0, abs=1e-10)


def test_no_geometry_without_the_lane_logs_says_that_they_were_not_given(corpus: Path, tmp_path: Path) -> None:
    (tmp_path / "new" / "M").mkdir(parents=True)
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.state == R.INCOMPLETE and v.rms_bohr is None
    assert v.reason == f"{R.NO_GEOMETRY}; {R.NO_LOGS_NOTE}"


def test_a_folder_the_lane_never_made_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = R.read_molecule("M", corpus, tmp_path / "absent")
    assert not v.accepted and v.state == R.INCOMPLETE and v.reason.startswith(R.NO_GEOMETRY)


def test_still_imaginary_stays_out_with_its_frequency(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, k_hh=-0.4, counts=dict.fromkeys(R.LABEL_TAGS, 1))
    assert not v.accepted and v.state == R.REFUSED and v.reason.startswith("still imaginary: lowest mode b3lyp -")


def test_a_lowest_mode_of_exactly_zero_is_not_accepted() -> None:
    new = R.Reoptimised(SYMBOLS, COORDS, {"b3lyp": 0.0, "wb97x": 5.0}, NOT_PENDING, dict(BOTH))
    assert R.refusal(SYMBOLS, new, []).reason.startswith("still imaginary: lowest mode b3lyp 0.00")


def test_a_frequency_that_is_not_a_number_is_refused_by_name() -> None:
    new = R.Reoptimised(SYMBOLS, COORDS, {"b3lyp": 30.0, "wb97x": float("nan")}, NOT_PENDING, dict(BOTH))
    assert R.refusal(SYMBOLS, new, []) == R.Refusal("the lowest mode of wb97x is not a finite number")


def test_a_pending_label_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, pending=("wb97x",))
    assert not v.accepted and "wb97x is marked low_mode_pending" in v.reason


def test_a_missing_label_file_stays_out(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "hessian_wb97x_analytic.npz").rename(folder / "elsewhere.npz")
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.state == R.INCOMPLETE and v.reason == f"no label file for wb97x; {R.NO_LOGS_NOTE}"


def test_a_missing_apt_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, apt="absent")
    assert not v.accepted and v.reason.startswith(f"no {R.APT_FILE}")


def test_an_apt_that_failed_its_checks_stays_out(corpus: Path, tmp_path: Path) -> None:
    """analytic_hessians.write_apt writes the file with passed=False and then raises: the file's existence is not the check."""
    v = read(corpus, tmp_path, apt="failed")
    assert not v.accepted and v.state == R.REFUSED
    assert v.reason == f"{R.APT_FILE} is marked passed=False: the APT failed its sum rule or its CPHF residual"


def test_an_apt_without_the_passed_mark_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, apt="unmarked")
    assert not v.accepted and v.state == R.REFUSED and v.reason.startswith(f"{R.APT_FILE} carries no 'passed' mark")


def test_a_passed_mark_that_is_not_a_boolean_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, apt="text")
    assert not v.accepted and "'passed' mark is not one true/false value" in v.reason


def test_a_cut_off_apt_file_is_unreadable_by_name(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / R.APT_FILE).write_bytes((folder / R.APT_FILE).read_bytes()[:60])
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.reason.startswith(f"label file unreadable: {R.APT_FILE}: ")


def test_a_cut_off_label_file_is_unreadable_by_name(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    label = folder / "hessian_wb97x_analytic.npz"
    label.write_bytes(label.read_bytes()[:100])
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.state == R.INCOMPLETE
    assert v.reason.startswith("label file unreadable: hessian_wb97x_analytic.npz: BadZipFile")
    assert v.lowest_after_cm["wb97x"] is None and v.lowest_after_cm["b3lyp"] > 0


def test_an_empty_label_file_and_one_without_the_hessian_are_unreadable(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "hessian_b3lyp_analytic.npz").write_bytes(b"")
    assert R.read_molecule("M", corpus, tmp_path / "new").reason.startswith("label file unreadable: hessian_b3lyp_analytic.npz: EOFError")
    np.savez(folder / "hessian_b3lyp_analytic.npz", other=np.zeros(1))
    assert R.read_molecule("M", corpus, tmp_path / "new").reason.startswith("label file unreadable: hessian_b3lyp_analytic.npz: KeyError")


def test_a_label_with_a_non_finite_value_stays_out(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    H = spring_hessian(COORDS)
    H[0, 0] = np.nan
    np.savez(folder / "hessian_b3lyp_analytic.npz", H_raw=H)
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.state == R.REFUSED and v.reason == "label holds a non-finite value: hessian_b3lyp_analytic.npz"


def test_a_missing_result_json_stays_out(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "result.json").unlink()
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.state == R.INCOMPLETE and v.reason.startswith("result.json missing")


def test_a_cut_off_json_file_is_unreadable_by_name(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "result.json").write_text('{"n_imaginary_b3lyp": 0, "n_im', encoding="utf-8")
    assert R.read_molecule("M", corpus, tmp_path / "new").reason.startswith("label file unreadable: result.json: JSONDecodeError")
    (folder / "geometry.json").write_text('{"symbols": ["O", "H", "H"]}', encoding="utf-8")
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert v.reason.startswith("label file unreadable: geometry.json: no masses_amu, coords_bohr") and v.rms_bohr is None


def test_an_error_that_is_not_a_damaged_file_still_raises(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    np.savez(folder / "hessian_b3lyp_analytic.npz", H_raw=np.zeros((6, 6)))        # a Hessian of another molecule: not a cut-off file
    with pytest.raises(Exception, match=r".") as caught:
        R.read_molecule("M", corpus, tmp_path / "new")
    assert not isinstance(caught.value, (OSError, EOFError, KeyError))


def test_one_damaged_folder_does_not_stop_the_read_of_the_others(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "corpus" / "N", k_hh=-0.4)
    damaged = write_folder(tmp_path / "new" / "M")
    (damaged / "hessian_b3lyp_analytic.npz").write_bytes(b"PK\x03\x04 cut off")
    write_folder(tmp_path / "new" / "N")
    ids = tmp_path / "ids.txt"
    ids.write_text("M\nN\n", encoding="utf-8")
    R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])
    record = json.loads((tmp_path / "read" / "record.json").read_text(encoding="utf-8"))
    assert [(r["mol_id"], r["accepted"]) for r in record] == [("M", False), ("N", True)]
    assert record[0]["reason"].startswith("label file unreadable: hessian_b3lyp_analytic.npz: ")


def test_the_routes_own_count_must_agree(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, counts={"b3lyp": 0, "wb97x": 1})
    assert not v.accepted and v.reason.endswith("(wb97x 1)")
    v_none = R.refusal(SYMBOLS, R.Reoptimised(SYMBOLS, COORDS, {"b3lyp": 9.0, "wb97x": 9.0}, NOT_PENDING, {"b3lyp": None, "wb97x": 0}), [])
    assert "b3lyp None" in v_none.reason and not v_none.incomplete


def test_a_broken_bond_stays_out_and_is_named(corpus: Path, tmp_path: Path) -> None:
    far = COORDS.copy()
    far[2] += np.array([0.0, -3.0, 0.0])        # the second hydrogen leaves
    v = read(corpus, tmp_path, coords=far)
    assert not v.accepted and v.changed_bonds == ["O0-H2 broken"] and "bond graph changed" in v.reason


def test_a_made_bond_is_named() -> None:
    near = COORDS.copy()
    near[1], near[2] = [0.0, 0.6, -1.6], [0.0, -0.6, -1.6]      # the hydrogens 1.2 bohr apart
    assert "H1-H2 made" in R.bond_changes(SYMBOLS, COORDS, near)


def test_another_atom_order_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, symbols=["H", "O", "H"])
    assert not v.accepted and v.reason.startswith("the atoms or their order differ") and v.rms_bohr is None


def test_uppercase_symbols_are_the_same_atoms(tmp_path: Path) -> None:
    write_folder(tmp_path / "corpus" / "M", k_hh=-0.4, symbols=["O", "H", "H"])
    write_folder(tmp_path / "new" / "M", symbols=["o", "h", "h"])
    assert R.read_molecule("M", tmp_path / "corpus", tmp_path / "new").accepted


def test_another_conformer_is_flagged_and_not_refused() -> None:
    """A four-carbon chain turned from trans to cis: every bond kept, the heavy atoms far from where they were."""
    symbols = ["C", "C", "C", "C"]
    trans = np.array([[0.0, 0.0, 0.0], [2.9, 0.0, 0.0], [3.9, 2.7, 0.0], [6.8, 2.7, 0.0]])
    cis = np.array([[0.0, 0.0, 0.0], [2.9, 0.0, 0.0], [3.9, 2.7, 0.0], [1.4, 4.4, 0.0]])
    new = R.Reoptimised(symbols, cis, {"b3lyp": 30.0, "wb97x": 31.0}, NOT_PENDING, dict(BOTH))
    geometry = {"symbols": symbols, "coords_bohr": trans.tolist()}
    v = R.verdict("chain", geometry, {"b3lyp": -40.0, "wb97x": 20.0}, new)
    assert v.accepted and v.conformer_flag and v.rms_heavy_bohr > R.CONFORMER_RMS_BOHR and v.changed_bonds == []


# --- the lane logs: not run, unfinished and failed told apart (the registration's section 6) ---

def test_no_folder_and_no_marker_is_not_run(corpus: Path, tmp_path: Path) -> None:
    v = read_with_log(corpus, tmp_path, [])
    assert not v.accepted and v.state == R.NOT_RUN and v.reason.startswith("not run: ") and v.reason.endswith(f"on disk: {R.NO_GEOMETRY}")
    (tmp_path / "new" / "M").mkdir(parents=True)        # an empty folder is no sign of a start either
    assert read_with_log(corpus, tmp_path, []).state == R.NOT_RUN


def test_started_and_cut_off_in_the_optimisation_is_unfinished(corpus: Path, tmp_path: Path) -> None:
    (tmp_path / "new" / "M").mkdir(parents=True)
    (tmp_path / "new" / "M" / "pyscf.log").write_text("SCF cycle 3\n", encoding="utf-8")
    v = read_with_log(corpus, tmp_path, ["@start", "(RLS) step 4 E -76.4 gmax 2.1e-03"])
    assert v.state == R.UNFINISHED and v.reason == f"unfinished: started and cut off in the optimisation; on disk: {R.NO_GEOMETRY}"


def test_files_without_any_marker_are_unfinished(corpus: Path, tmp_path: Path) -> None:
    (tmp_path / "new" / "M").mkdir(parents=True)
    (tmp_path / "new" / "M" / "pyscf.log").write_text("SCF cycle 3\n", encoding="utf-8")
    v = read_with_log(corpus, tmp_path, [])
    assert v.state == R.UNFINISHED and "the lane logs hold no marker for it" in v.reason


def test_a_failed_optimisation_carries_the_logs_reason_line(corpus: Path, tmp_path: Path) -> None:
    v = read_with_log(corpus, tmp_path, ["@start", "Traceback (most recent call last):", "RuntimeError: geomeTRIC did not converge in 300 steps",
                                         "", "@FAILED in the optimisation (not converged or an error; no geometry.json is written)"])
    assert v.state == R.FAILED
    assert v.reason == f"failed in the optimisation: RuntimeError: geomeTRIC did not converge in 300 steps; on disk: {R.NO_GEOMETRY}"


def test_a_failed_optimisation_without_an_output_line_says_so(corpus: Path, tmp_path: Path) -> None:
    v = read_with_log(corpus, tmp_path, ["@start", "@FAILED in the optimisation (not converged or an error; no geometry.json is written)"])
    assert v.state == R.FAILED and v.reason.startswith("failed in the optimisation: the log holds no line before the marker")


def test_a_later_pass_replaces_an_earlier_failure(corpus: Path, tmp_path: Path) -> None:
    v = read_with_log(corpus, tmp_path, ["@start", "Killed", "@FAILED in the optimisation (not converged or an error; no geometry.json is written)",
                                         "@start"])
    assert v.state == R.UNFINISHED


def test_failed_in_the_labels_carries_the_exit_code(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M", apt="absent")
    (folder / "hessian_wb97x_analytic.npz").unlink()
    v = read_with_log(corpus, tmp_path, ["@start", "@optimisation done in 900 s", "MemoryError", "@FAILED in the labels (exit 1)"])
    assert v.state == R.FAILED and v.reason == "failed in the labels (exit 1); on disk: no label file for wb97x"


def test_cut_off_in_the_labels_is_unfinished(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "result.json").unlink()
    v = read_with_log(corpus, tmp_path, ["@start", "@optimisation done in 900 s"])
    assert v.state == R.UNFINISHED and v.reason == "unfinished: started and cut off in the labels; on disk: result.json missing"


def test_a_molecule_the_lane_finished_is_judged_by_the_rule_alone(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "new" / "M", apt="failed")
    v = read_with_log(corpus, tmp_path, ["@start", "@optimisation done in 900 s", "@labels done, APT FAILED its checks (the Hessians are written)",
                                         "@no imaginary mode \"n_imaginary_b3lyp\": 0 \"n_imaginary_wb97x\": 0 (1500 s)"])
    assert v.state == R.REFUSED and v.reason.startswith(f"{R.APT_FILE} is marked passed=False")
    (tmp_path / "new" / "M" / R.APT_FILE).unlink()      # finished by the lane's own word, a file gone since: refused, not unfinished
    v = read_with_log(corpus, tmp_path, ["@start", "@labels done", "@no imaginary mode (1500 s)"])
    assert v.state == R.REFUSED and v.reason == f"no {R.APT_FILE}: the APT was not written"


def test_the_lane_logs_never_turn_an_accepted_molecule_away(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "new" / "M")
    assert read_with_log(corpus, tmp_path, ["@start", "@FAILED in the labels (exit 1)"]).accepted


def test_lane_logs_come_from_a_folder_or_a_glob_and_must_hold_markers(tmp_path: Path) -> None:
    write_log(tmp_path / "logs" / "lane0.log", ["@start"])
    (tmp_path / "logs" / "notes.txt").write_text("not a log\n", encoding="utf-8")
    assert R.lane_log_paths(str(tmp_path / "logs")) == [tmp_path / "logs" / "lane0.log"]
    assert R.lane_log_paths(str(tmp_path / "logs" / "lane*.log")) == [tmp_path / "logs" / "lane0.log"]
    with pytest.raises(FileNotFoundError, match="no log file there"):
        R.lane_log_paths(str(tmp_path / "logs" / "other*.log"))
    (tmp_path / "logs" / "pyscf.log").write_text("SCF cycle 3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="these are not the lane logs"):
        R.lane_events([tmp_path / "logs" / "pyscf.log"])


def test_the_last_marker_is_the_latest_across_the_logs(tmp_path: Path) -> None:
    first = write_log(tmp_path / "logs" / "a.log", ["@start", "Killed", "@FAILED in the labels (exit 137)"])
    second = tmp_path / "logs" / "b.log"
    second.write_text("=== (IRL) M: start 2026-11-21 01:00:00\n=== (IRL) N: start 2026-11-21 01:10:00\n", encoding="utf-8")
    for order in ([first, second], [second, first]):
        events = R.lane_events(order)
        assert events["M"] == R.LaneEvent("start", "") and events["N"].text == "start"


# --- the corpus folder, the id list and the files the read writes ---

def test_a_corpus_folder_without_a_label_is_a_named_reason(corpus: Path, tmp_path: Path) -> None:
    (corpus / "M" / "hessian_wb97x_analytic.npz").unlink()
    v = read(corpus, tmp_path)
    assert not v.accepted and v.state == R.SOURCE_PROBLEM and v.reason == "the corpus folder has no analytic label for wb97x"
    assert v.lowest_before_cm["wb97x"] is None and v.lowest_before_cm["b3lyp"] < 0
    assert "| M | " in R.result_text([v])


def test_a_corpus_folder_without_a_readable_geometry_is_a_named_reason(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "new" / "M")
    assert R.read_molecule("absent", corpus, tmp_path / "new").reason == "the corpus folder has no geometry.json"
    (corpus / "M" / "hessian_b3lyp_analytic.npz").write_bytes(b"")
    assert R.read_molecule("M", corpus, tmp_path / "new").reason == "the corpus folder's label file unreadable: hessian_b3lyp_analytic.npz: EOFError"


def test_the_read_writes_a_row_per_molecule(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "corpus" / "N", k_hh=-0.4)
    write_folder(tmp_path / "new" / "M")
    ids = tmp_path / "ids.txt"
    ids.write_text("# two molecules\nM 3\nN 3\n", encoding="utf-8")
    R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])
    record = json.loads((tmp_path / "read" / "record.json").read_text(encoding="utf-8"))
    assert [(r["mol_id"], r["accepted"], r["state"]) for r in record] == [("M", True, R.ACCEPTED), ("N", False, R.INCOMPLETE)]
    text = (tmp_path / "read" / "RESULT.md").read_text(encoding="utf-8")
    assert f"2 molecules read, 1 accepted, 1 stay out (1 {R.INCOMPLETE})" in text and "| N |" in text and "stays out: no geometry.json" in text


def test_the_read_with_lane_logs_counts_the_states(corpus: Path, tmp_path: Path) -> None:
    for name in ("N", "P"):
        write_folder(tmp_path / "corpus" / name, k_hh=-0.4)
    write_folder(tmp_path / "new" / "M")
    logs = tmp_path / "logs"
    logs.mkdir()
    (logs / "lane0.log").write_text("=== (IRL) M: start 2026-11-20 23:00:00\n=== (IRL) M: labels done 2026-11-20 23:30:00\n"
                                    "=== (IRL) N: start 2026-11-20 23:31:00\nValueError: a | in the line\n"
                                    "=== (IRL) N: FAILED in the optimisation (not converged or an error; no geometry.json is written) "
                                    "2026-11-20 23:40:00\n", encoding="utf-8")
    ids = tmp_path / "ids.txt"
    ids.write_text("M\nN\nP\n", encoding="utf-8")
    R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read"), "--lane-logs", str(logs)])
    text = (tmp_path / "read" / "RESULT.md").read_text(encoding="utf-8")
    assert "3 molecules read, 1 accepted, 2 stay out (1 failed, 1 not run)" in text
    assert "stays out: failed in the optimisation: ValueError: a / in the line; on disk" in text and "stays out: not run: " in text
    assert all(line.count("|") == 6 for line in text.splitlines() if line.startswith("|"))


def test_a_repeated_id_is_refused(corpus: Path, tmp_path: Path) -> None:
    ids = tmp_path / "ids.txt"
    ids.write_text("M\nM\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"repeats an id \(M\)"):
        R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])


def test_an_empty_id_list_is_refused(corpus: Path, tmp_path: Path) -> None:
    ids = tmp_path / "ids.txt"
    ids.write_text("# nothing yet\n\n", encoding="utf-8")
    with pytest.raises(ValueError, match="names no molecule"):
        R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])
    assert not (tmp_path / "read").exists()
