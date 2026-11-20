"""probes/imaginary_reopt_read.py on synthetic records (TASKS 215): the acceptance rule's every branch, from folders written here.

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
                 counts: dict | None = None, apt: bool = True,
                 pending: tuple[str, ...] = (), symbols: list[str] | None = None) -> Path:
    folder.mkdir(parents=True)
    geometry = {"symbols": symbols or SYMBOLS, "masses_amu": MASSES, "coords_bohr": coords.tolist()}
    (folder / "geometry.json").write_text(json.dumps(geometry), encoding="utf-8")
    (folder / "result.json").write_text(json.dumps({f"n_imaginary_{t}": n for t, n in (BOTH if counts is None else counts).items()}),
                                        encoding="utf-8")
    for tag in R.LABEL_TAGS:
        extra = {"low_mode_pending": True} if tag in pending else {}
        np.savez(folder / f"hessian_{tag}_analytic.npz", H_raw=spring_hessian(coords, k_hh), **extra)
    if apt:
        np.savez(folder / R.APT_FILE, apt=np.zeros(1))
    return folder


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    """A corpus folder whose label carries one imaginary mode."""
    write_folder(tmp_path / "corpus" / "M", k_hh=-0.4)
    return tmp_path / "corpus"


def read(corpus: Path, tmp_path: Path, **kwargs) -> R.Verdict:
    write_folder(tmp_path / "new" / "M", **kwargs)
    return R.read_molecule("M", corpus, tmp_path / "new")


def test_the_synthetic_corpus_label_is_imaginary_and_the_repaired_one_is_not(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path)
    assert all(v.lowest_before_cm[t] < 0 for t in R.LABEL_TAGS)
    assert all(v.lowest_after_cm[t] > 0 for t in R.LABEL_TAGS)
    assert v.accepted and v.reason == "" and v.changed_bonds == [] and not v.conformer_flag
    assert v.rms_bohr == pytest.approx(0.0, abs=1e-12)


def test_a_rotated_and_shifted_copy_is_the_same_geometry(corpus: Path, tmp_path: Path) -> None:
    c, s = np.cos(0.7), np.sin(0.7)
    moved = COORDS @ np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]]) + np.array([1.0, -2.0, 0.5])
    v = read(corpus, tmp_path, coords=moved)
    assert v.accepted and v.rms_bohr == pytest.approx(0.0, abs=1e-10)


def test_no_geometry_means_the_optimisation_did_not_finish(corpus: Path, tmp_path: Path) -> None:
    (tmp_path / "new" / "M").mkdir(parents=True)
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.reason.startswith("no geometry.json") and v.rms_bohr is None


def test_a_folder_the_lane_never_made_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = R.read_molecule("M", corpus, tmp_path / "absent")
    assert not v.accepted and v.reason.startswith("no geometry.json")


def test_still_imaginary_stays_out_with_its_frequency(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, k_hh=-0.4, counts=dict.fromkeys(R.LABEL_TAGS, 1))
    assert not v.accepted and v.reason.startswith("still imaginary: lowest mode b3lyp -")


def test_a_lowest_mode_of_exactly_zero_is_not_accepted() -> None:
    new = R.Reoptimised(SYMBOLS, COORDS, {"b3lyp": 0.0, "wb97x": 5.0}, dict.fromkeys(R.LABEL_TAGS, False), dict(BOTH), True)
    assert R.refusal(SYMBOLS, new, []).startswith("still imaginary: lowest mode b3lyp 0.00")


def test_a_pending_label_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, pending=("wb97x",))
    assert not v.accepted and "wb97x is marked low_mode_pending" in v.reason


def test_a_missing_label_file_stays_out(corpus: Path, tmp_path: Path) -> None:
    folder = write_folder(tmp_path / "new" / "M")
    (folder / "hessian_wb97x_analytic.npz").rename(folder / "elsewhere.npz")
    v = R.read_molecule("M", corpus, tmp_path / "new")
    assert not v.accepted and v.reason == "no label file for wb97x"


def test_a_missing_apt_stays_out(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, apt=False)
    assert not v.accepted and v.reason.startswith(f"no {R.APT_FILE}")


def test_the_routes_own_count_must_agree(corpus: Path, tmp_path: Path) -> None:
    v = read(corpus, tmp_path, counts={"b3lyp": 0, "wb97x": 1})
    assert not v.accepted and v.reason.endswith("(wb97x 1)")
    v_none = R.refusal(SYMBOLS, R.Reoptimised(SYMBOLS, COORDS, {"b3lyp": 9.0, "wb97x": 9.0}, dict.fromkeys(R.LABEL_TAGS, False),
                                              {"b3lyp": None, "wb97x": 0}, True), [])
    assert "b3lyp None" in v_none


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
    new = R.Reoptimised(symbols, cis, {"b3lyp": 30.0, "wb97x": 31.0}, dict.fromkeys(R.LABEL_TAGS, False), dict(BOTH), True)
    geometry = {"symbols": symbols, "coords_bohr": trans.tolist()}
    v = R.verdict("chain", geometry, {"b3lyp": -40.0, "wb97x": 20.0}, new)
    assert v.accepted and v.conformer_flag and v.rms_heavy_bohr > R.CONFORMER_RMS_BOHR and v.changed_bonds == []


def test_the_read_writes_a_row_per_molecule(corpus: Path, tmp_path: Path) -> None:
    write_folder(tmp_path / "corpus" / "N", k_hh=-0.4)
    write_folder(tmp_path / "new" / "M")
    ids = tmp_path / "ids.txt"
    ids.write_text("# two molecules\nM 3\nN 3\n", encoding="utf-8")
    R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])
    record = json.loads((tmp_path / "read" / "record.json").read_text(encoding="utf-8"))
    assert [(r["mol_id"], r["accepted"]) for r in record] == [("M", True), ("N", False)]
    text = (tmp_path / "read" / "RESULT.md").read_text(encoding="utf-8")
    assert "2 molecules read, 1 accepted, 1 stay out" in text and "| N |" in text and "stays out: no geometry.json" in text


def test_a_repeated_id_is_refused(corpus: Path, tmp_path: Path) -> None:
    ids = tmp_path / "ids.txt"
    ids.write_text("M\nM\n", encoding="utf-8")
    with pytest.raises(ValueError, match="repeats an id"):
        R.main([str(corpus), str(tmp_path / "new"), "--ids", str(ids), "--out", str(tmp_path / "read")])
