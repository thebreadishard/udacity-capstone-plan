"""probes/low_mode_threshold_read.py on synthetic records with the regime's edge cases (TASKS 218; CLAUDE.md: a registration's read
script runs on synthetic records before the registration is committed).

Every record is a water-sized molecule whose label and patched Hessians are built on one fixed vibrational basis with chosen
frequencies, so the change the read must recover is known exactly. numpy only; everything is written under tmp_path.
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
import low_mode_threshold_read as R  # noqa: E402
import vibrations as V  # noqa: E402
from constants import HARTREE2CM  # noqa: E402

MASSES = np.array([15.99491461956, 1.00782503207, 1.00782503207])
COORDS = np.array([[0.0, 0.0, 0.0], [0.0, -1.4305, 1.1093], [0.0, 1.4305, 1.1093]])
BASIS = V.vibrational_modes(np.diag(np.arange(1.0, 10.0)), MASSES, COORDS).vectors   # a fixed orthonormal basis of the vibrations
STIFF = [1600.0, 3700.0]


def hessian(omega_cm: list[float], basis: np.ndarray = BASIS) -> np.ndarray:
    """A Cartesian Hessian whose vibrational frequencies are the ones given (cm⁻¹, negative = imaginary), one per basis vector."""
    w = np.asarray(omega_cm, float)
    sm = V.mass_weights(MASSES)
    return (basis @ np.diag(np.sign(w) * (w / HARTREE2CM) ** 2) @ basis.T) * np.outer(sm, sm)


def write_molecule(root: Path, mol_id: str, label: dict[str, list[float]], patched: dict[str, list[float]], **patch: object) -> None:
    """One molecule's geometry, labels and patch record under root/{molecules,labels,patches}; `directions` defaults to the first basis
    vector, the lowest mode's own."""
    U = np.asarray(patch.get("directions", BASIS[:, :1]), float)
    for folder in ("molecules", "labels", "patches"):
        (root / folder / mol_id).mkdir(parents=True, exist_ok=True)
    (root / "molecules" / mol_id / "geometry.json").write_text(json.dumps({"masses_amu": MASSES.tolist(), "coords_bohr": COORDS.tolist()}),
                                                              encoding="utf-8")
    for tag in V.LABEL_TAGS:
        H = hessian(label[tag])
        np.savez(root / "labels" / mol_id / f"hessian_{tag}_analytic.npz", H_raw=H, **patch.get("label_extra", {}))
        np.savez(root / "patches" / mol_id / f"hessian_{tag}_analytic_grfpatch.npz", H_raw=hessian(patched[tag]), directions=U,
                 columns=np.zeros_like(U), freq_label_vib_cm=np.sort(np.asarray(patch.get("recorded_label", label)[tag], float)),
                 freq_patched_vib_cm=np.sort(patched[tag]), below_cm=60.0, step_bohr=patch.get("step", 0.01))
    (root / "patches" / mol_id / "report.json").write_text(json.dumps({"id": mol_id, "directions": int(U.shape[1])}), encoding="utf-8")


def both(omega: list[float]) -> dict[str, list[float]]:
    return dict.fromkeys(V.LABEL_TAGS, omega)


def config(root: Path, **changes: object) -> R.ReadConfig:
    settings = {"sources": (R.Source(root / "patches", root / "labels"),), "step_checks": (), "molecules": root / "molecules",
                "out": root / "out", "exploratory": None} | changes
    return R.ReadConfig(**settings)


def read_points(root: Path) -> list[R.Point]:
    return R.source_points(config(root).sources, root / "molecules")


def point(label_cm: float, change_cm: float, k_cart: float = 1e-3, **changes: object) -> R.Point:
    """A constructed point of the registered population."""
    settings = {"mol_id": "X", "tag": R.DECISION_TAG, "mode": 0, "atoms": 3, "label_cm": label_cm, "patched_cm": label_cm + change_cm,
                "coverage": 1.0, "overlap_patched": 1.0, "k_cart": k_cart, "sample": R.UNBIASED, "below_cm": 60.0, "step_bohr": 0.01} | changes
    return R.Point(**settings)


def population(n: int, moved: int) -> list[R.Point]:
    """n points in the decision window, `moved` of them beyond the line."""
    return [point(21.0 + 38.0 * i / n, 1.0 if i < moved else 0.1) for i in range(n)]


def test_an_exact_eigenmode_gives_back_its_change(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    points = read_points(tmp_path)
    assert [p.tag for p in points] == list(V.LABEL_TAGS)
    for p in points:
        assert p.label_cm == pytest.approx(35.0, abs=1e-6) and p.change_cm == pytest.approx(2.5, abs=1e-6)
        assert p.coverage == pytest.approx(1.0) and p.overlap_patched == pytest.approx(1.0)
        assert p.sample == R.UNBIASED and not p.flags and p.k_cart > 0


def test_a_direction_that_is_no_single_mode_is_flagged_and_left_out_of_the_statistics(tmp_path: Path) -> None:
    mixed = BASIS[:, 0] + 0.6 * BASIS[:, 1]
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]), directions=(mixed / np.linalg.norm(mixed))[:, None])
    points = read_points(tmp_path)
    assert all(p.flags == ("overlap",) and p.coverage == pytest.approx(1 / 1.36) for p in points)
    record = R.summarise(points)
    assert record["points"] == 2 and record["flagged_overlap"] == 2
    assert all(g["n"] == 0 for g in record["groups"])
    assert "M_1" in R.points_csv(points)


def test_a_mode_that_turns_imaginary_is_a_signed_move_and_is_counted(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([25.0, *STIFF]), both([-10.0, *STIFF]))
    points = read_points(tmp_path)
    assert all(p.turned_imaginary and p.change_cm == pytest.approx(-35.0, abs=1e-6) and not p.flags for p in points)
    record = R.summarise(points)
    assert record["turned_imaginary"] == ["M_1 b3lyp", "M_1 wb97x"]
    assert next(g for g in record["groups"] if g["tag"] == "b3lyp")["bands"][0]["moved"] == 1


def test_two_directions_give_one_point_per_mode_whatever_their_rotation(tmp_path: Path) -> None:
    c, s = np.cos(0.5), np.sin(0.5)
    rotated = np.stack([c * BASIS[:, 0] + s * BASIS[:, 1], -s * BASIS[:, 0] + c * BASIS[:, 1]], axis=1)
    write_molecule(tmp_path, "M_1", both([35.0, 45.0, 3700.0]), both([36.0, 44.2, 3700.0]), directions=rotated)
    b3lyp = [p for p in read_points(tmp_path) if p.tag == "b3lyp"]
    assert [p.mode for p in b3lyp] == [0, 1]
    assert [p.change_cm for p in b3lyp] == pytest.approx([1.0, -0.8], abs=1e-6)
    assert all(p.coverage == pytest.approx(1.0) and not p.flags for p in b3lyp)


def test_a_molecule_with_a_label_mode_below_the_threshold_is_the_biased_sample(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", {"b3lyp": [12.0, *STIFF], "wb97x": [55.0, *STIFF]}, {"b3lyp": [15.0, *STIFF], "wb97x": [57.0, *STIFF]})
    assert {p.sample for p in read_points(tmp_path)} == {R.BIASED}


def test_an_empty_band_is_a_row_with_n_zero() -> None:
    rows = R.band_rows([point(35.0, 0.7)])
    assert [r["n"] for r in rows] == [0, 1, 0, 0, 0, 0]
    assert rows[0] == {"group": "20–30", "n": 0, "median_abs_cm": None, "max_abs_cm": None, "moved": 0, "fraction": None, "se": None}
    assert rows[1]["fraction"] == 1.0 and rows[1]["se"] == 0.0
    assert R.quartile_rows([point(35.0, 0.7)]) == []


def test_all_moves_zero_leave_the_correlation_undefined_and_no_nan_in_the_text(tmp_path: Path) -> None:
    for i, omega in enumerate([25.0, 35.0, 45.0, 55.0]):
        write_molecule(tmp_path, f"M_{i}", both([omega, *STIFF]), both([omega, *STIFF]))
    cfg = config(tmp_path)
    record = R.run(cfg)
    group = next(g for g in record["groups"] if g["registered"])
    assert group["n"] == 4 and group["correlations"]["rho_frequency"] is None and group["correlations"]["rho_log_k"] is None
    text = (cfg.out / "RESULT.md").read_text(encoding="utf-8")
    assert "undefined" in text and "nan" not in text.lower()
    assert sorted(p.name for p in cfg.out.iterdir()) == ["RESULT.md", "points.csv", "record.json"]
    assert json.loads((cfg.out / "record.json").read_text(encoding="utf-8"))["decision"]["outcome"] == R.OUTCOME_UNDECIDED


@pytest.mark.parametrize(("n", "moved", "outcome"), [
    (25, 5, R.OUTCOME_SOUND),          # p = 0.20 exactly, p + SE = 0.28
    (25, 6, R.OUTCOME_UNDECIDED),      # p = 0.24
    (25, 12, R.OUTCOME_UNDECIDED),     # p = 0.48
    (25, 13, R.OUTCOME_MAJORITY),      # p = 0.52, p − SE = 0.42
    (20, 10, R.OUTCOME_UNDECIDED),     # p = 0.50 but p − SE = 0.39
    (100, 50, R.OUTCOME_MAJORITY),     # p = 0.50 exactly, p − SE = 0.45
    (100, 20, R.OUTCOME_SOUND),
    (16, 0, R.OUTCOME_SOUND),          # the fewest points the rule reads
    (15, 0, R.OUTCOME_UNDECIDED),      # one fewer: nothing is read from them, although p = 0 and SE = 0
    (15, 15, R.OUTCOME_UNDECIDED),
    (0, 0, R.OUTCOME_UNDECIDED),
])
def test_the_registered_rule_and_its_boundaries(n: int, moved: int, outcome: str) -> None:
    rule = R.apply_rule(population(n, moved))
    assert (rule.n, rule.moved, rule.outcome) == (n, moved, outcome)
    assert f"n = {n}" in rule.statement and "nan" not in rule.statement.lower()


def test_the_decision_reads_only_unflagged_b3lyp_points_of_the_unbiased_sample_in_the_window() -> None:
    registered = population(20, 2)
    others = ([point(40.0, 3.0, tag="wb97x") for _ in range(30)] + [point(40.0, 3.0, sample=R.BIASED) for _ in range(30)]
              + [point(40.0, 3.0, coverage=0.5) for _ in range(30)] + [point(70.0, 3.0) for _ in range(30)]
              + [point(40.0, 3.0, step_check_cm=0.4) for _ in range(30)])
    decision = R.summarise(registered + others)["decision"]
    assert (decision["n"], decision["moved"], decision["outcome"]) == (20, 2, R.OUTCOME_SOUND)


def test_outcome_two_names_the_quantity_that_orders_the_moves_or_none() -> None:
    by_stiffness = [point(21.0 + (7 * i) % 38, 0.6 + 3.0 / (i + 1), k_cart=1e-4 * (i + 1)) for i in range(20)]
    assert "the force constant (log k) orders the moves better" in R.apply_rule(by_stiffness).statement
    by_frequency = [point(21.0 + 1.9 * i, 0.6 + 3.0 / (i + 1), k_cart=1e-4 * (1 + (7 * i) % 20)) for i in range(20)]
    assert "the label frequency orders the moves better" in R.apply_rule(by_frequency).statement
    unordered = [point(30.0, 1.0) for _ in range(20)]
    assert "no trigger is named" in R.apply_rule(unordered).statement


def test_a_step_check_flags_a_point_whose_two_steps_disagree(tmp_path: Path) -> None:
    main, check = tmp_path / "main", tmp_path / "check"
    write_molecule(main, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    write_molecule(main, "M_2", both([45.0, *STIFF]), both([46.0, *STIFF]))
    write_molecule(check, "M_1", both([35.0, *STIFF]), {"b3lyp": [37.9, *STIFF], "wb97x": [37.6, *STIFF]}, step=0.02)
    cfg = config(main, step_checks=(R.Source(check / "patches", main / "labels"),))
    record = R.run(cfg)
    flagged = {(p.mol_id, p.tag): p.flags for p in R.with_step_check(read_points(main), R.source_points(cfg.step_checks, cfg.molecules))}
    assert flagged == {("M_1", "b3lyp"): ("step",), ("M_1", "wb97x"): (), ("M_2", "b3lyp"): (), ("M_2", "wb97x"): ()}
    assert record["flagged_step"] == 1 and record["step_checked"] == 2


def test_a_step_check_at_the_same_step_is_refused(tmp_path: Path) -> None:
    main, check = tmp_path / "main", tmp_path / "check"
    write_molecule(main, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    write_molecule(check, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    with pytest.raises(ValueError, match="same step"):
        R.run(config(main, step_checks=(R.Source(check / "patches", main / "labels"),)))


def test_a_repaired_label_is_refused_as_the_original(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]), label_extra={"low_mode_patch": "{}"})
    with pytest.raises(ValueError, match="carries a low-mode repair"):
        read_points(tmp_path)


def test_a_label_the_patch_was_not_made_from_is_refused(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]), recorded_label=both([33.0, *STIFF]))
    with pytest.raises(ValueError, match="not the label this patch was made from"):
        read_points(tmp_path)


def test_an_unfinished_molecule_refuses_the_read_and_one_without_directions_is_skipped(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    (tmp_path / "patches" / "M_0").mkdir()
    (tmp_path / "patches" / "M_0" / "report.json").write_text(json.dumps({"id": "M_0", "directions": 0}), encoding="utf-8")
    assert {p.mol_id for p in read_points(tmp_path)} == {"M_1"}
    (tmp_path / "patches" / "M_2").mkdir()
    with pytest.raises(FileNotFoundError, match="has not finished"):
        read_points(tmp_path)


def test_the_configuration_is_refused_before_anything_is_read(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    with pytest.raises(ValueError, match="folder of its own"):
        config(tmp_path, out=tmp_path / "patches" / "read")
    with pytest.raises(FileNotFoundError):
        config(tmp_path, molecules=tmp_path / "nowhere")
    with pytest.raises(ValueError, match="no source"):
        config(tmp_path, sources=())
    with pytest.raises(ValueError, match="says why"):
        config(tmp_path, exploratory=" ")
    with pytest.raises(ValueError, match="<patch folder>=<label folder>"):
        R.Source.parse("only_one_folder")
    source = R.Source(tmp_path / "patches", tmp_path / "labels")
    with pytest.raises(ValueError, match="more than one source"):
        R.source_points((source, source), tmp_path / "molecules")


def test_the_force_constant_is_the_rayleigh_quotient_of_the_cartesian_hessian() -> None:
    direction = BASIS[:, 0]
    assert R.cartesian_force_constant(0.37 * np.eye(9), direction, MASSES) == pytest.approx(0.37)
    d = direction / V.mass_weights(MASSES)
    H = hessian([35.0, *STIFF])
    assert R.cartesian_force_constant(H, direction, MASSES) == pytest.approx(float(d @ H @ d / (d @ d)))


def test_an_exploratory_read_says_so_at_the_top(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    R.main(["--source", f"{tmp_path / 'patches'}={tmp_path / 'labels'}", "--molecules", str(tmp_path / "molecules"),
            "--out", str(tmp_path / "out"), "--exploratory", "the points were looked at before"])
    printed = capsys.readouterr().out
    assert "**Exploratory read; it decides nothing.** the points were looked at before" in printed
    assert "Outcome 3: undecided" in printed
