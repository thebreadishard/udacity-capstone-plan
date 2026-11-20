"""probes/low_mode_threshold_sample.py on a synthetic corpus (TASKS 218): the draw is the same every time and a larger one contains the
smaller, a band with too few molecules refuses it, repaired molecules and repair candidates stay out, and the price counts the
directions the runner would patch. Water-sized molecules on one fixed vibrational basis; everything is written under tmp_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import low_mode_threshold_sample as S  # noqa: E402
import vibrations as V  # noqa: E402
from constants import HARTREE2CM  # noqa: E402

MASSES = np.array([15.99491461956, 1.00782503207, 1.00782503207])
COORDS = np.array([[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]])
BASIS = V.vibrational_modes(np.diag(np.arange(1.0, 10.0)), MASSES, COORDS).vectors
BAND_LOWS = (22.0, 33.0, 44.0, 55.0)       # one lowest B3LYP mode inside each band


def hessian(omega_cm: list[float]) -> np.ndarray:
    w = np.asarray(omega_cm, float)
    sm = V.mass_weights(MASSES)
    return (BASIS @ np.diag(np.sign(w) * (w / HARTREE2CM) ** 2) @ BASIS.T) * np.outer(sm, sm)


def write_molecule(molecules: Path, mol_id: str, b3lyp: list[float], wb97x: list[float] | None = None, repaired: bool = False) -> None:
    folder = molecules / mol_id
    folder.mkdir(parents=True)
    (folder / "geometry.json").write_text(json.dumps({"masses_amu": MASSES.tolist(), "coords_bohr": COORDS.tolist()}), encoding="utf-8")
    extra = {"low_mode_patch": "{}"} if repaired else {}
    for tag, omega in zip(V.LABEL_TAGS, (b3lyp, wb97x or b3lyp), strict=True):
        np.savez(folder / f"hessian_{tag}_analytic.npz", H_raw=hessian(omega), **extra)


def write_corpus(root: Path, per_band: int = 4, second: float = 1600.0) -> Path:
    """`per_band` molecules in each band, and one earlier repair whose point files give the gradient times."""
    molecules = root / "molecules"
    for b, low in enumerate(BAND_LOWS):
        for i in range(per_band):
            write_molecule(molecules, f"M_{b}{i}", [low + 0.5 * i, second, 3700.0])
    write_molecule(molecules, "T_0", [12.0, 1600.0, 3700.0], repaired=True)
    for tag, seconds in zip(V.LABEL_TAGS, (30.0, 50.0), strict=True):
        (root / "timing" / "T_0" / tag).mkdir(parents=True)
        for sign in ("plus", "minus"):
            (root / "timing" / "T_0" / tag / f"dir_0_{sign}.json").write_text(json.dumps({"seconds": seconds}), encoding="utf-8")
    return molecules


def config(root: Path, **changes: object) -> S.SampleConfig:
    settings = {"molecules": root / "molecules", "out": root / "out", "timing": (root / "timing",), "per_band": 2, "max_atoms": 25,
                "seed": 218} | changes
    return S.SampleConfig(**settings)


def drawn(record: dict) -> list[str]:
    return [m["id"] for m in record["molecules"]]


def test_the_draw_is_the_same_every_time_and_a_larger_one_contains_it(tmp_path: Path) -> None:
    write_corpus(tmp_path)
    first = S.run(config(tmp_path))
    again = S.run(config(tmp_path, out=tmp_path / "again"))
    larger = S.run(config(tmp_path, out=tmp_path / "larger", per_band=3))
    assert drawn(first) == drawn(again) and len(drawn(first)) == 8
    assert set(drawn(first)) < set(drawn(larger)) and len(drawn(larger)) == 12
    assert drawn(S.run(config(tmp_path, out=tmp_path / "other", seed=7))) != drawn(first)
    assert [m["band"] for m in first["molecules"]] == ["20–30"] * 2 + ["30–40"] * 2 + ["40–50"] * 2 + ["50–60"] * 2


def test_the_files_are_written_into_the_output_folder_and_the_runner_can_read_the_ids(tmp_path: Path) -> None:
    write_corpus(tmp_path)
    record = S.run(config(tmp_path))
    assert sorted(p.name for p in (tmp_path / "out").iterdir()) == ["SAMPLE.md", "ids_sample.txt", "ids_step02.txt", "sample.json"]
    lines = (tmp_path / "out" / "ids_sample.txt").read_text(encoding="utf-8").splitlines()
    assert [line.split()[0] for line in lines if not line.startswith("#")] == drawn(record)
    step = (tmp_path / "out" / "ids_step02.txt").read_text(encoding="utf-8").splitlines()
    assert [line.split()[0] for line in step if not line.startswith("#")] == record["step_check_ids"] == list(record["step_check"])
    assert set(record["step_check_ids"]) <= set(drawn(record)) and len(record["step_check_ids"]) >= 4
    assert all(m["registered_points"][0]["noise_cm"] > 0 and m["registered_points"][0]["mode"] == 0 for m in record["molecules"])
    assert json.loads((tmp_path / "out" / "sample.json").read_text(encoding="utf-8")) == json.loads(json.dumps(record))


def test_a_band_with_fewer_molecules_than_asked_refuses_the_draw(tmp_path: Path) -> None:
    write_corpus(tmp_path, per_band=2)
    with pytest.raises(ValueError, match="fewer than the 3 asked for"):
        S.run(config(tmp_path, per_band=3))
    assert not (tmp_path / "out").exists()


def test_repaired_molecules_repair_candidates_and_large_molecules_stay_out(tmp_path: Path) -> None:
    molecules = write_corpus(tmp_path, per_band=2)
    write_molecule(molecules, "R_0", [22.0, 1600.0, 3700.0], repaired=True)
    write_molecule(molecules, "C_0", [22.0, 1600.0, 3700.0], wb97x=[12.0, 1600.0, 3700.0])
    write_molecule(molecules, "I_0", [22.0, 1600.0, 3700.0], wb97x=[-40.0, 1600.0, 3700.0])
    record = S.run(config(tmp_path))
    assert not {"R_0", "C_0", "I_0"} & set(drawn(record))
    assert record["population"][0] == {"band": "20–30", "unrepaired": 4, "within_atom_limit": 4, "eligible": 2}
    with pytest.raises(ValueError, match="between 3 and 25"):
        config(tmp_path, max_atoms=26)


def test_the_price_counts_the_runners_directions_at_each_threshold(tmp_path: Path) -> None:
    write_corpus(tmp_path, per_band=1, second=80.0)       # one mode in the band and one at 80 cm⁻¹: 1 direction below 60, 2 below 100
    record = S.run(config(tmp_path, per_band=1))
    pair_s = 2 * 30.0 + 2 * 50.0                           # ± one step in both functionals at the recorded medians
    for m in record["molecules"]:
        assert m["modes_cm"]["b3lyp"][1] == 80.0 and m["atoms"] == 3
        assert m["below"]["60"] == {"directions": 1, "gradients": 4, "seconds": pytest.approx((1 + S.REFERENCE_SHARE) * pair_s)}
        assert m["below"]["100"] == {"directions": 2, "gradients": 8, "seconds": pytest.approx((2 + S.REFERENCE_SHARE) * pair_s)}
    total = record["totals"]["100"]
    assert (total["directions"], total["gradients"], total["reference_scfs"]) == (8, 32, 8)
    assert total["hours_8_threads"] == pytest.approx(4 * (2 + S.REFERENCE_SHARE) * pair_s / 3600)
    assert (total["hours_low"], total["hours_high"]) == pytest.approx((total["hours_8_threads"], 2 * total["hours_8_threads"]))
    assert record["gradient_seconds"] == {"0 b3lyp": {"median_s": 30.0, "points": 2}, "0 wb97x": {"median_s": 50.0, "points": 2}}
    text = (tmp_path / "out" / "SAMPLE.md").read_text(encoding="utf-8")
    assert "The sample at `--below 60`: 4 directions, 16 gradients and 8 reference SCFs" in text and "nan" not in text.lower()
    assert record["step_check_totals"]["60"]["directions"] == len(record["step_check_ids"]) and "The step check at `--below 60`" in text


def test_a_size_without_a_recorded_gradient_time_refuses_the_price(tmp_path: Path) -> None:
    write_corpus(tmp_path, per_band=1)
    (tmp_path / "empty").mkdir()
    with pytest.raises(ValueError, match="no recorded gradient time"):
        S.run(config(tmp_path, per_band=1, timing=(tmp_path / "empty",)))
    with pytest.raises(ValueError, match="no timing folder"):
        config(tmp_path, timing=())
    with pytest.raises(ValueError, match="folder of its own"):
        config(tmp_path, out=tmp_path / "molecules" / "sample")


def test_a_molecule_past_the_atom_limit_is_never_drawn(tmp_path: Path) -> None:
    write_corpus(tmp_path, per_band=1)
    modes = {tag: np.array([low]) for tag, low in zip(V.LABEL_TAGS, (25.0, 70.0), strict=True)}
    population = [S.Candidate(f"S_{b}{i}", 10, {t: np.array([low]) for t in V.LABEL_TAGS}) for b, low in enumerate(BAND_LOWS) for i in range(2)]
    population.append(S.Candidate("L_0", 26, modes))
    chosen = S.draw(population, config(tmp_path))
    assert "L_0" not in {c.mol_id for picked in chosen.values() for c in picked}
    with pytest.raises(ValueError, match="20–30 cm⁻¹ holds 2 eligible molecules"):
        S.draw(population, config(tmp_path, per_band=3))
    assert S.population_rows(population, 25)[0] == {"band": "20–30", "unrepaired": 3, "within_atom_limit": 2, "eligible": 2}


def test_the_step_check_list_is_the_smallest_of_each_band_and_every_noisy_registered_point() -> None:
    """Review finding 1: a rule, not a typed list. A quiet large molecule stays off; a noisy one goes on whatever its size; a tie in size
    goes to the first id."""
    def row(mol_id: str, band: str, atoms: int, *noise: float) -> dict:
        return {"id": mol_id, "band": band, "atoms": atoms, "registered_points": [{"mode": i, "label_cm": 25.0, "noise_cm": n} for i, n in enumerate(noise)]}

    rows = [row("A_big_quiet", "20–30", 25, 0.2), row("A_small", "20–30", 15, 0.1), row("A_noisy", "20–30", 23, 0.2, 0.71),
            row("B_tie_1", "30–40", 16, 0.1), row("B_tie_2", "30–40", 16, 0.5), row("B_both", "30–40", 12, 1.09)]
    assert S.step_check_ids(rows) == {"A_small": "smallest of its band", "A_noisy": "a registered point above the noise line",
                                      "B_both": "smallest of its band and a registered point above the noise line"}
    assert S.step_check_ids(rows[3:5]) == {"B_tie_1": "smallest of its band"}      # 0.5 is not above the line


def test_the_registered_points_of_a_molecule_are_its_modes_in_the_window(tmp_path: Path) -> None:
    molecules = tmp_path / "molecules"
    write_molecule(molecules, "M_1", [23.7, 30.3, 3700.0])
    write_molecule(molecules, "M_2", [45.0, 80.0, 3700.0])
    two = S.registered_points(molecules / "M_1")
    assert [(p["mode"], round(p["label_cm"], 4)) for p in two] == [(0, 23.7), (1, 30.3)]
    assert [p["mode"] for p in S.registered_points(molecules / "M_2")] == [0]
