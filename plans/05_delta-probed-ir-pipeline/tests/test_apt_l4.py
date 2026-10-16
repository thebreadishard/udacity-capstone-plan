"""probes/apt_l4.py (TASKS 44's L4, 16 Oct 2026), run on synthetic files before the selection and the field runs: the registered selection
(two largest changes, then first / middle / last of the rest, deterministic on ties), the line read on the no-grid-response route only, and
a missing field file stopping the read."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import apt_l4 as L4  # noqa: E402


def write_apt(folder: Path, P: np.ndarray) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    np.savez(folder / L4.APT_FILE, apt=P)


def test_the_registered_selection():
    change = {"B_a": 1e-6, "B_b": 5e-4, "B_c": 2e-6, "B_d": 5e-4, "B_e": 3e-6, "B_f": 9e-5, "B_g": 1e-7}
    picks = L4.select(change)
    assert [i for i, _ in picks] == ["B_b", "B_d", "B_a", "B_e", "B_g"]          # tie broken by id; rest a, c, e, f, g → first, middle, last
    assert picks[0][1].startswith("largest change") and picks[3][1] == "middle of the rest"
    with pytest.raises(SystemExit, match="at least 5"):
        L4.select({"x": 1.0, "y": 2.0})


def test_changes_and_the_read(tmp_path):
    P = np.arange(18.0).reshape(3, 6) * 1e-2
    for i, shift in (("m1", 0.0), ("m2", 3e-4)):
        write_apt(tmp_path / "refined" / i, P)
        write_apt(tmp_path / "unrefined" / i, P + shift)
        np.savez(tmp_path / f"{i}_field.npz", apt_no_grid_response=P + (5e-5 if i == "m1" else 2e-4), apt_grid_response=P + 1e-3)
    assert L4.changes(tmp_path / "refined", tmp_path / "unrefined") == {"m1": 0.0, "m2": pytest.approx(3e-4)}
    res = L4.read(["m1", "m2"], tmp_path / "refined", tmp_path)
    assert res["molecules"]["m1"]["meets_line"] and not res["molecules"]["m2"]["meets_line"]
    assert res["verdict"] == "L4 fails on m2"
    assert res["molecules"]["m1"]["max_diff_grid_response_e"] == pytest.approx(1e-3)      # beside, never the line
    with pytest.raises(FileNotFoundError):
        L4.read(["m3"], tmp_path / "refined", tmp_path)
