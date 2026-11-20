"""probes/low_mode_threshold_read.py on synthetic records with the regime's edge cases (TASKS 218; CLAUDE.md: a registration's read
script runs on synthetic records before the registration is committed).

Every record is a water-sized molecule whose label and patched Hessians are built on one fixed vibrational basis with chosen
frequencies, so the change the read must recover is known exactly. numpy only; everything is written under tmp_path.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
import low_mode_step_analysis as A  # noqa: E402
import low_mode_threshold_read as R  # noqa: E402
import vibrations as V  # noqa: E402
from constants import AMU2AU, HARTREE2CM  # noqa: E402

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


def coupled_patch(root: Path, mol_id: str, label: list[float], block_cm2: list[list[float]]) -> None:
    """A two-direction molecule whose patched Hessian replaces the 2×2 block of its two lowest modes (cm⁻², in the label's mode basis)."""
    write_molecule(root, mol_id, both(label), both(label), directions=BASIS[:, :2])
    curvature = np.diag((np.asarray(label, float) / HARTREE2CM) ** 2)
    curvature[:2, :2] = np.asarray(block_cm2, float) / HARTREE2CM ** 2
    sm = V.mass_weights(MASSES)
    for tag in V.LABEL_TAGS:
        path = root / "patches" / mol_id / f"hessian_{tag}_analytic_grfpatch.npz"
        with np.load(path) as z:
            fields = {k: z[k] for k in z.files}
        np.savez(path, **(fields | {"H_raw": (BASIS @ curvature @ BASIS.T) * np.outer(sm, sm)}))


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
    assert rows[0] == {"group": "20–30", "n": 0, "median_abs_cm": None, "max_abs_cm": None, "moved": 0, "fraction": None, "se": None,
                       "median_noise_cm": None}
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
              + [point(40.0, 3.0, step_check_cm=0.4)])
    decision = R.summarise(registered + others)["decision"]
    assert (decision["n"], decision["moved"], decision["outcome"]) == (20, 2, R.OUTCOME_SOUND)
    assert decision["bounds"] == {"flagged": 31, "n": 51, "as_moved": {"moved": 33, "outcome": R.OUTCOME_MAJORITY},
                                  "as_unmoved": {"moved": 2, "outcome": R.OUTCOME_SOUND}}
    assert len(decision["points"]) == 51


def test_what_orders_the_moves_is_described_with_signs_and_never_named_a_trigger() -> None:
    """Frequency and force constant rise together here, so both correlations are −1 and the two cannot be told apart; a positive
    correlation is printed with its sign and is no trigger either (review finding 3)."""
    falling = [point(21.0 + 1.9 * i, 3.0 / (i + 1), k_cart=1e-4 * (i + 1)) for i in range(20)]
    c = R.correlations(falling)
    assert (c["rho_frequency"], c["rho_log_k"], c["rho_frequency_log_k"]) == pytest.approx((-1.0, -1.0, 1.0))
    sentence = R.ordering_sentence(falling)
    assert "frequency: -1.00 (n = 20)" in sentence and "log k: -1.00 (n = 20)" in sentence and "same points: +1.00" in sentence
    rising = R.ordering_sentence([point(21.0 + 1.9 * i, 0.1 * (i + 1), k_cart=1e-4 * (20 - i)) for i in range(20)])
    assert "frequency: +1.00" in rising and "log k: -1.00" in rising
    for text in (sentence, rising, R.apply_rule([point(30.0, 2.0) for _ in range(20)]).statement):
        assert "trigger to change" not in text and "orders the moves better" not in text
    assert "the read names none" in sentence
    assert "undefined" in R.ordering_sentence([point(30.0, 1.0) for _ in range(20)])


def test_the_outcome_sentences_speak_of_the_sampled_population_and_of_no_cause() -> None:
    strata = R.Strata({"X": "20–30"}, {"20–30": 41}, 25)
    assert strata.population == "molecules whose lowest b3lyp mode lies in 20–60 cm⁻¹, with at most 25 atoms, each band weighted equally"
    sound = R.apply_rule(population(20, 2), strata.population).statement
    assert f"Outcome 1, for {strata.population}:" in sound and "threshold stays" not in sound
    wrong = R.apply_rule(population(20, 15), strata.population).statement
    assert f"Outcome 2, for {strata.population}:" in wrong and "label and patch disagree, not why" in wrong and "CPHF" in wrong


def test_the_noise_per_unit_of_gradient_noise_follows_the_patchs_own_arithmetic() -> None:
    """Two atoms of 1 amu moving against each other: |d| = 1/√m, q = step·√(2m), so σ_λ = σ / (2·step·m) and σ_ω = σ_λ / (2ω)."""
    masses = np.array([1.0, 1.0])
    mode = np.array([1.0, 0.0, 0.0, -1.0, 0.0, 0.0]) / np.sqrt(2)
    expected = R.GRADIENT_NOISE_UNIT / (2 * 0.01 * AMU2AU) * HARTREE2CM ** 2 / (2 * 30.0)
    assert R.noise_sensitivity_cm(mode, 30.0, masses, 0.01) == pytest.approx(expected, rel=1e-12)
    assert R.noise_sensitivity_cm(mode, 60.0, masses, 0.01) == pytest.approx(expected / 2)
    assert R.noise_sensitivity_cm(mode, 30.0, masses, 0.02) == pytest.approx(expected / 2)
    assert R.noise_sensitivity_cm(mode, -30.0, masses, 0.01) == pytest.approx(expected) and R.noise_sensitivity_cm(mode, 0.0, masses, 0.01) == np.inf
    # the same number from the repair's own column: the curvature is linear in the two gradients, one coefficient per component
    v = BASIS[:, 0]
    _, q = V.displacement(v, MASSES, 0.01)
    coefficients = np.array([v @ V.column(unit, np.zeros(9), q, MASSES) for unit in np.eye(9)])
    by_column = R.GRADIENT_NOISE_UNIT * np.sqrt(2 * (coefficients ** 2).sum()) * HARTREE2CM ** 2 / (2 * 35.0)
    assert R.noise_sensitivity_cm(v, 35.0, MASSES, 0.01) == pytest.approx(by_column, rel=1e-10)


def test_a_light_rotor_is_noisier_than_a_heavy_frame_mode_and_the_point_carries_it(tmp_path: Path) -> None:
    heavy = np.array([1.0, 0.0, 0.0, -1.0, 0.0, 0.0]) / np.sqrt(2)
    assert R.noise_sensitivity_cm(heavy, 30.0, np.array([1.0, 1.0]), 0.01) > 10 * R.noise_sensitivity_cm(heavy, 30.0, np.array([12.0, 12.0]), 0.01)
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    p = read_points(tmp_path)[0]
    assert p.noise_cm == pytest.approx(R.noise_sensitivity_cm(BASIS[:, 0], 35.0, MASSES, 0.01), rel=1e-6)
    assert "noise_cm_per_1e-7_hartree_bohr" in R.points_csv([p]).splitlines()[0]


def test_two_failed_step_checks_make_the_outcome_undecided_and_one_only_drops_its_point() -> None:
    registered = population(20, 2)
    one = R.summarise([*registered, point(40.0, 3.0, mol_id="F_1", step_check_cm=0.4)])["decision"]
    assert one["outcome"] == R.OUTCOME_SOUND and one["n"] == 20
    two = R.summarise([*registered, point(40.0, 3.0, mol_id="F_1", step_check_cm=0.4),
                       point(45.0, 0.1, mol_id="F_2", step_check_cm=-0.2)])["decision"]
    assert two["outcome"] == R.OUTCOME_UNDECIDED and "F_1 mode 0, F_2 mode 0" in two["statement"]
    assert "extended to every sampled molecule" in two["statement"] and two["n"] == 20
    elsewhere = R.summarise([*registered, point(40.0, 3.0, tag="wb97x", step_check_cm=0.4), point(70.0, 3.0, step_check_cm=0.4),
                             point(45.0, 3.0, sample=R.BIASED, step_check_cm=0.4)])["decision"]
    assert elsewhere["outcome"] == R.OUTCOME_SOUND


@pytest.mark.parametrize(("change", "check", "outcome"), [
    (0.6, None, R.OUTCOME_NOT_STATED),     # near the line and unchecked: held back
    (-0.3, None, R.OUTCOME_NOT_STATED),
    (0.6, 0.05, R.OUTCOME_SOUND),          # checked and agreeing: read
    (0.25, None, R.OUTCOME_SOUND),         # the band's edges are outside it
    (1.0, None, R.OUTCOME_SOUND),
    (3.0, None, R.OUTCOME_SOUND),
])
def test_a_move_near_the_line_without_a_step_check_holds_the_outcome_back(change: float, check: float | None, outcome: str) -> None:
    decision = R.summarise([*population(20, 2), point(40.0, change, mol_id="N_1", step_check_cm=check)])["decision"]
    assert decision["outcome"] == outcome and decision["n"] == 21
    if outcome == R.OUTCOME_NOT_STATED:
        assert "No outcome is stated" in decision["statement"] and f"N_1 mode 0 {change:+.2f}" in decision["statement"]


def test_flagged_points_bound_the_outcome_from_both_sides(tmp_path: Path) -> None:
    """The review's case: label modes at 30.0 and 30.3 cm⁻¹ and a patch that only couples them by 60 cm⁻². Neither label mode has one
    counterpart afterwards, so both points are flagged; the read says what counting them either way would give."""
    coupled_patch(tmp_path, "M_1", [30.0, 30.3, 3700.0], [[30.0 ** 2, 60.0], [60.0, 30.3 ** 2]])
    cfg = config(tmp_path)
    record = R.run(cfg)
    b3lyp = [p for p in read_points(tmp_path) if p.tag == "b3lyp"]
    assert [p.flags for p in b3lyp] == [("overlap",), ("overlap",)] and all(p.coverage == pytest.approx(1.0) for p in b3lyp)
    assert record["decision"]["n"] == 0
    assert record["decision"]["bounds"] == {"flagged": 2, "n": 2, "as_moved": {"moved": 2, "outcome": R.OUTCOME_UNDECIDED},
                                            "as_unmoved": {"moved": 0, "outcome": R.OUTCOME_UNDECIDED}}
    assert "Counted as moved: 2 of 2" in (cfg.out / "RESULT.md").read_text(encoding="utf-8")
    bounds = R.flagged_bounds(population(18, 3), [point(30.0, 0.0, coverage=0.5) for _ in range(12)])
    assert (bounds["as_moved"], bounds["as_unmoved"]) == ({"moved": 15, "outcome": R.OUTCOME_MAJORITY}, {"moved": 3, "outcome": R.OUTCOME_SOUND})


def test_the_fraction_per_band_and_weighted_by_the_bands_sizes() -> None:
    strata = R.Strata({"A": "20–30", "B": "50–60"}, {"20–30": 41, "50–60": 146}, 25)
    points = [point(22.0, 2.0, mol_id="A"), point(24.0, 2.0, mol_id="A"), point(55.0, 2.0, mol_id="B"), *(point(56.0, 0.0, mol_id="B") for _ in range(3))]
    rows = R.stratum_rows(points, strata)
    assert rows == [{"band": "20–30", "eligible": 41, "n": 2, "moved": 2, "fraction": 1.0},
                    {"band": "50–60", "eligible": 146, "n": 4, "moved": 1, "fraction": 0.25}]
    assert R.weighted_fraction(rows) == pytest.approx((41 * 1.0 + 146 * 0.25) / 187)
    assert R.weighted_fraction(R.stratum_rows(points[:2], strata)) is None
    with pytest.raises(ValueError, match="not in the sample record"):
        R.stratum_rows([point(22.0, 2.0, mol_id="Z")], strata)
    decision = R.registered_decision(points, strata)
    assert decision["weighted_fraction"] == pytest.approx(0.4144, abs=1e-4) and decision["p"] == pytest.approx(0.5)
    text = "\n".join(R.decision_lines(decision))
    assert "20–30: 2 of 2; 50–60: 1 of 4" in text and "(41/146): 0.41 (descriptive" in text


def test_the_sample_record_gives_the_read_its_bands(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    sample = tmp_path / "sample.json"
    sample.write_text(json.dumps({"settings": {"max_atoms": 25}, "molecules": [{"id": "M_1", "band": "30–40"}],
                                  "population": [{"band": "30–40", "eligible": 41}]}), encoding="utf-8")
    record = R.run(config(tmp_path, sample=sample))
    assert record["decision"]["strata"] == [{"band": "30–40", "eligible": 41, "n": 1, "moved": 1, "fraction": 1.0}]
    assert record["decision"]["weighted_fraction"] == 1.0 and record["decision"]["points"][0]["id"] == "M_1"
    with pytest.raises(FileNotFoundError):
        config(tmp_path, sample=tmp_path / "no_sample.json")


def test_the_rules_error_rates_at_the_expected_sample_size() -> None:
    """Registration section 7 quotes these: 21 points, each moved with the true probability given."""
    assert [R.rule_outcome(21, k) for k in (4, 5, 10, 11)] == [R.OUTCOME_SOUND, R.OUTCOME_UNDECIDED, R.OUTCOME_UNDECIDED, R.OUTCOME_MAJORITY]
    assert R.outcome_probabilities(21, 0.30)[R.OUTCOME_SOUND] == pytest.approx(0.20, abs=0.005)
    assert R.outcome_probabilities(21, 0.40)[R.OUTCOME_MAJORITY] == pytest.approx(0.17, abs=0.005)
    assert R.outcome_probabilities(21, 0.35)[R.OUTCOME_UNDECIDED] == pytest.approx(0.83, abs=0.005)
    assert sum(R.outcome_probabilities(21, 0.35).values()) == pytest.approx(1.0)


def test_a_step_check_flags_a_point_whose_two_steps_disagree(tmp_path: Path) -> None:
    main, check = tmp_path / "main", tmp_path / "check"
    write_molecule(main, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    write_molecule(main, "M_2", both([45.0, *STIFF]), both([46.0, *STIFF]))
    write_molecule(check, "M_1", both([35.0, *STIFF]), {"b3lyp": [37.9, *STIFF], "wb97x": [37.6, *STIFF]}, step=0.02)
    cfg = config(main, step_checks=(R.Source(check / "patches", main / "labels"),))
    record = R.run(cfg)
    checked, set_aside = R.with_step_check(read_points(main), R.source_points(cfg.step_checks, cfg.molecules))
    flagged = {(p.mol_id, p.tag): p.flags for p in checked}
    assert set_aside == [] and record["step_checks_set_aside"] == []
    assert flagged == {("M_1", "b3lyp"): ("step",), ("M_1", "wb97x"): (), ("M_2", "b3lyp"): (), ("M_2", "wb97x"): ()}
    assert record["flagged_step"] == 1 and record["step_checked"] == 2


def test_a_check_point_without_a_single_counterpart_checks_nothing(tmp_path: Path) -> None:
    main, check = tmp_path / "main", tmp_path / "check"
    write_molecule(main, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    mixed = BASIS[:, 0] + 0.6 * BASIS[:, 1]
    write_molecule(check, "M_1", both([35.0, *STIFF]), both([39.0, *STIFF]), step=0.02, directions=(mixed / np.linalg.norm(mixed))[:, None])
    checked, set_aside = R.with_step_check(read_points(main), read_points(check))
    assert all(p.step_check_cm is None and not p.flags for p in checked)
    assert set_aside == ["M_1 mode 0 b3lyp", "M_1 mode 0 wb97x"]


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


# --- the extrapolated read (amendment 3): two steps combined to step zero --------------------------------------------------------------

READ_FOLDER = PLAN / "probes" / "results_m1" / "low_mode_threshold_2026-11-20"
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
CM2 = 1.0 / HARTREE2CM ** 2   # one cm⁻² of curvature in atomic units
Q2_RECORD = {"record": "q2_test.json", "verdict": R.Q2_HOLDS, "interval": [4.0, 6.0],
             "ratios": [{"id": "T_1", "tag": "b3lyp", "direction": 0, "ratio": 5.02}]}
BOTH_STEPS_AND_Q2 = R.Extrapolation((), Q2_RECORD)   # nothing holds the extrapolated read back


def measured_columns(true_cm: list[float], U: np.ndarray, step: float, quartic_cm2: float = 0.0, sextic_cm2: float = 0.0) -> np.ndarray:
    """The columns the repair's own `column` makes of gradients at ± one step along each direction, for a potential with the given
    harmonic frequencies and, along every direction, a quartic and a sextic term. The two terms are named by the curvature error (cm⁻²)
    they cause at a step of 0.01 bohr: the central difference of g(x) = λx + c₄x³/6 + c₆x⁵/120 is λ + c₄q²/6 + c₆q⁴/120."""
    sm = V.mass_weights(MASSES)
    w = np.asarray(true_cm, float)
    Hmw = BASIS @ np.diag(np.sign(w) * (w / HARTREE2CM) ** 2) @ BASIS.T
    columns = []
    for u in U.T:
        _, q = V.displacement(u, MASSES, step)
        scale = step / 0.01
        along = q * (Hmw @ u) + q * (quartic_cm2 * scale ** 2 + sextic_cm2 * scale ** 4) * CM2 * u   # the mass-weighted gradient at +q
        columns.append(V.column(along * sm, -along * sm, q, MASSES))
    return np.stack(columns, axis=1)


def write_step(root: Path, folder: str, mol_id: str, label: list[float], columns: np.ndarray, **patch: object) -> None:
    """One molecule's patch record at one step, made from its columns as the runner makes it; both functionals alike."""
    U = np.asarray(patch.get("directions", BASIS[:, :1]), float)
    (root / folder / mol_id).mkdir(parents=True, exist_ok=True)
    H = V.patched_hessian(hessian(label), MASSES, U, columns)
    stored = V.vibrational_modes(H, MASSES, COORDS).omega_cm + float(patch.get("stored_shift", 0.0))
    for tag in V.LABEL_TAGS:
        np.savez(root / folder / mol_id / f"hessian_{tag}_analytic_grfpatch.npz", H_raw=H, directions=U, columns=columns,
                 freq_label_vib_cm=np.sort(label), freq_patched_vib_cm=stored, below_cm=float(patch.get("below", 60.0)),
                 step_bohr=float(patch.get("step", 0.01)))
    (root / folder / mol_id / "report.json").write_text(json.dumps({"id": mol_id, "directions": int(U.shape[1])}), encoding="utf-8")


def write_two_steps(root: Path, mol_id: str, label: list[float], true: list[float], quartic_cm2: float = 0.0, **patch: object) -> None:
    """A molecule with its geometry and labels, patched at 0.01 bohr into `patches` and, unless `second=False`, at the large step into
    `second` (optionally along other directions there)."""
    U = np.asarray(patch.get("directions", BASIS[:, :1]), float)
    write_molecule(root, mol_id, both(label), both(label))
    write_step(root, "patches", mol_id, label, measured_columns(true, U, 0.01, quartic_cm2), directions=U)
    if patch.get("second", True):
        U2, step = np.asarray(patch.get("large_directions", U), float), float(patch.get("large_step", 0.02))
        write_step(root, "second", mol_id, label, measured_columns(true, U2, step, quartic_cm2), directions=U2, step=step)


def extrapolated(root: Path, **changes: object) -> R.ReadConfig:
    return config(root, second_steps=(R.Source(root / "second", root / "labels"),), **changes)


def two_step_point(label_cm: float, change_cm: float, two_step_cm: float = 0.3, **changes: object) -> R.Point:
    """A constructed extrapolated point: the small step stands 0.1 cm⁻¹ above the extrapolated value, the large one two_step_cm above
    the small."""
    small = label_cm + change_cm + 0.1
    return point(label_cm, change_cm, small_step_cm=small, large_step_cm=small + two_step_cm, **changes)


def test_the_weights_are_richardsons_and_the_noise_factor_follows_from_them() -> None:
    assert pytest.approx(4 / 3, rel=1e-15) == R.WEIGHT_SMALL
    assert pytest.approx(-1 / 3, rel=1e-15) == R.WEIGHT_LARGE
    assert pytest.approx(math.sqrt(65) / 6, rel=1e-15) == R.EXTRAPOLATED_NOISE_FACTOR


def test_a_quartic_term_is_removed_exactly_and_each_single_step_is_off() -> None:
    u = BASIS[:, :1]
    truth = float(u[:, 0] @ measured_columns([37.5, *STIFF], u, 0.01)[:, 0])
    small, large = (measured_columns([37.5, *STIFF], u, step, quartic_cm2=7.0) for step in (0.01, 0.02))
    assert float(u[:, 0] @ small[:, 0]) - truth == pytest.approx(7.0 * CM2, rel=1e-9)        # the step error grows as q²:
    assert float(u[:, 0] @ large[:, 0]) - truth == pytest.approx(28.0 * CM2, rel=1e-9)       # four times it at twice the step
    assert np.abs(R.extrapolated_columns(small, large) - measured_columns([37.5, *STIFF], u, 0.01)).max() < 1e-12 * abs(truth)


def test_the_extrapolated_frequency_is_the_true_one_to_1e_8_where_neither_step_is(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    points, unread = R.extrapolated_points(extrapolated(tmp_path))
    assert unread == [] and len(points) == 2
    for p in points:
        assert p.patched_cm == pytest.approx(37.5, abs=1e-8) and p.change_cm == pytest.approx(2.5, abs=1e-8)
        assert p.small_step_cm == pytest.approx(math.sqrt(37.5 ** 2 + 7.0), abs=1e-8)
        assert p.large_step_cm == pytest.approx(math.sqrt(37.5 ** 2 + 28.0), abs=1e-8)
        assert p.small_step_change_cm == pytest.approx(p.small_step_cm - 35.0)
        assert p.bias_removed_cm == pytest.approx(p.small_step_cm - 37.5, abs=1e-8) and p.bias_removed_cm > 0.09
        assert p.two_step_cm == pytest.approx(p.large_step_cm - p.small_step_cm) and p.flags == ()


def test_a_sextic_term_leaves_a_known_residual() -> None:
    u = BASIS[:, :1]
    truth = float(u[:, 0] @ measured_columns([37.5, *STIFF], u, 0.01)[:, 0])
    small, large = (measured_columns([37.5, *STIFF], u, step, quartic_cm2=7.0, sextic_cm2=0.5) for step in (0.01, 0.02))
    left = float(u[:, 0] @ R.extrapolated_columns(small, large)[:, 0]) - truth
    assert left == pytest.approx(-R.STEP_RATIO ** 2 * 0.5 * CM2, rel=1e-9)     # −4·b·q⁴: the q² term is gone, the q⁴ term is not


def test_gradient_noise_reaches_the_extrapolated_curvature_with_the_stated_factor() -> None:
    """By propagation: the curvature along u is linear in the four gradients, so its noise is the root sum of squares of the
    coefficients, read off the repair's own `column` on unit gradients."""
    u = BASIS[:, 0]
    q = V.displacement(u, MASSES, 0.01)[1]
    unit, zero = np.eye(len(u)), np.zeros(len(u))
    small = np.array([u @ V.column(e, zero, q, MASSES) for e in unit])                   # d(uᵀC)/d(g₊) at the small step; g₋ mirrors it
    large = np.array([u @ V.column(e, zero, R.STEP_RATIO * q, MASSES) for e in unit])
    single = math.sqrt(2 * (small ** 2).sum())
    combined = math.sqrt(2 * ((R.WEIGHT_SMALL * small) ** 2).sum() + 2 * ((R.WEIGHT_LARGE * large) ** 2).sum())
    assert combined / single == pytest.approx(R.EXTRAPOLATED_NOISE_FACTOR, rel=1e-12)
    assert 1.34 < R.EXTRAPOLATED_NOISE_FACTOR < 1.35


def test_an_extrapolated_point_carries_the_small_steps_noise_times_the_factor(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    single = {p.tag: p.noise_cm for p in read_points(tmp_path)}
    points, _ = R.extrapolated_points(extrapolated(tmp_path))
    assert {p.tag: p.noise_cm for p in points} == {tag: pytest.approx(n * R.EXTRAPOLATED_NOISE_FACTOR) for tag, n in single.items()}


@pytest.mark.parametrize(("two_step", "flags"), [
    (1.0, ()),                              # at the limit exactly: read
    (-1.0, ()),
    (1.0 + 1e-9, (R.NOT_QUADRATIC,)),       # just beyond: left out
    (-1.0 - 1e-9, (R.NOT_QUADRATIC,)),
    (0.57, ()),                             # the largest difference of the seven checked molecules
])
def test_a_point_is_not_quadratic_beyond_one_wavenumber_between_the_steps(two_step: float, flags: tuple[str, ...]) -> None:
    p = point(30.0, 0.2, small_step_cm=30.0, large_step_cm=30.0 + two_step)
    assert p.flags == flags
    assert point(30.0, 0.2).flags == ()     # a point of the registered read has no two steps and no such flag


def test_a_molecule_without_its_second_step_has_no_point_and_holds_the_outcome_back(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    write_two_steps(tmp_path, "M_2", [45.0, *STIFF], [45.2, *STIFF], second=False)
    record = R.run(extrapolated(tmp_path))
    assert record["unread"] == [{"id": "M_2", "reason": "no second step"}]
    assert record["molecules"] == 1 and record["points"] == 2
    assert record["decision"]["outcome"] == R.OUTCOME_NOT_STATED
    assert "1 molecule(s) have no second step (M_2)" in record["decision"]["statement"]
    assert "no point here: M_2." in (tmp_path / "out" / "RESULT.md").read_text(encoding="utf-8")


def test_a_second_step_that_is_not_twice_the_first_or_patched_another_space_is_refused(tmp_path: Path) -> None:
    write_two_steps(tmp_path / "ratio", "M_1", [35.0, *STIFF], [37.5, *STIFF], large_step=0.03)
    with pytest.raises(ValueError, match=r"0\.01 and 0\.03 bohr"):
        R.extrapolated_points(extrapolated(tmp_path / "ratio"))
    root = tmp_path / "space"
    write_two_steps(root, "M_1", [35.0, *STIFF], [37.5, *STIFF])
    write_step(root, "second", "M_1", [35.0, *STIFF], measured_columns([37.5, *STIFF], BASIS[:, :1], 0.02), step=0.02, below=100.0)
    with pytest.raises(ValueError, match="not the same space"):
        R.extrapolated_points(extrapolated(root))


def test_stored_columns_that_do_not_rebuild_the_stored_patch_are_refused(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF])
    write_step(tmp_path, "second", "M_1", [35.0, *STIFF], measured_columns([37.5, *STIFF], BASIS[:, :1], 0.02), step=0.02,
               stored_shift=1e-5)
    with pytest.raises(ValueError, match="rebuilt from the stored columns"):
        R.extrapolated_points(extrapolated(tmp_path))


def test_second_step_folders_may_be_several_but_hold_each_molecule_once_and_no_stranger(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF])
    write_two_steps(tmp_path, "M_2", [45.0, *STIFF], [45.2, *STIFF], second=False)
    write_step(tmp_path, "extension", "M_2", [45.0, *STIFF], measured_columns([45.2, *STIFF], BASIS[:, :1], 0.02), step=0.02)
    labels = tmp_path / "labels"
    both_folders = (R.Source(tmp_path / "second", labels), R.Source(tmp_path / "extension", labels))
    points, unread = R.extrapolated_points(config(tmp_path, second_steps=both_folders))
    assert unread == [] and {p.mol_id for p in points} == {"M_1", "M_2"}
    write_step(tmp_path, "extension", "M_1", [35.0, *STIFF], measured_columns([37.5, *STIFF], BASIS[:, :1], 0.02), step=0.02)
    with pytest.raises(ValueError, match="M_1 is in more than one second-step folder"):
        R.extrapolated_points(config(tmp_path, second_steps=both_folders))
    write_step(tmp_path, "stranger", "M_9", [35.0, *STIFF], measured_columns([37.5, *STIFF], BASIS[:, :1], 0.02), step=0.02)
    with pytest.raises(ValueError, match="holds molecules the sources do not"):
        R.extrapolated_points(config(tmp_path, second_steps=(R.Source(tmp_path / "stranger", labels),)))


def test_a_step_check_and_a_second_step_do_not_combine(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF])
    second = (R.Source(tmp_path / "second", tmp_path / "labels"),)
    with pytest.raises(ValueError, match="give one of the two"):
        config(tmp_path, step_checks=second, second_steps=second)
    with pytest.raises(FileNotFoundError):
        config(tmp_path, second_steps=(R.Source(tmp_path / "absent", tmp_path / "labels"),))


@pytest.mark.parametrize(("n", "moved", "outcome"), [
    (20, 4, R.OUTCOME_SOUND),              # p = 0.20, p + 1 SE = 0.29
    (20, 5, R.OUTCOME_UNDECIDED),
    (20, 10, R.OUTCOME_UNDECIDED),         # p = 0.50 but p − 1 SE = 0.39
    (20, 12, R.OUTCOME_MAJORITY),
    (15, 0, R.OUTCOME_UNDECIDED),          # below the floor of 16 points
])
def test_the_rule_is_read_on_the_extrapolated_change_with_its_thresholds_unchanged(n: int, moved: int, outcome: str) -> None:
    points = [two_step_point(21.0 + 38.0 * i / n, 1.0 if i < moved else 0.1) for i in range(n)]
    decision = R.summarise(points, extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert decision["outcome"] == outcome and decision["n"] == n and decision["moved"] == moved
    listed = decision["points"][0]
    assert listed["small_step_change_cm"] == pytest.approx(listed["change_cm"] + 0.1) and listed["bias_removed_cm"] == pytest.approx(0.1)
    assert listed["two_step_cm"] == pytest.approx(0.3)


def test_the_small_steps_change_does_not_decide_an_extrapolated_point() -> None:
    """A point whose small step alone is beyond the line and whose extrapolated value is not counts as unmoved, and the reverse."""
    inside = point(30.0, 0.45, small_step_cm=30.6, large_step_cm=31.05)
    beyond = point(40.0, -0.55, small_step_cm=39.55, large_step_cm=39.85)
    rest = [two_step_point(21.0 + 2.0 * i, 0.1) for i in range(18)]
    decision = R.summarise([inside, beyond, *rest], extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert decision["n"] == 20 and decision["moved"] == 1


def test_two_points_not_quadratic_make_the_outcome_undecided_and_one_only_drops_its_point() -> None:
    registered = [two_step_point(21.0 + 1.9 * i, 1.0 if i < 2 else 0.1) for i in range(20)]
    one = R.summarise([*registered, two_step_point(40.0, 3.0, 1.2, mol_id="F_1")], extrapolation=BOTH_STEPS_AND_Q2)
    assert one["decision"]["outcome"] == R.OUTCOME_SOUND and one["decision"]["n"] == 20 and one["flagged_not_quadratic"] == 1
    two = R.summarise([*registered, two_step_point(40.0, 3.0, 1.2, mol_id="F_1"), two_step_point(45.0, 0.1, -1.5, mol_id="F_2")],
                      extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert two["outcome"] == R.OUTCOME_UNDECIDED and "F_1 mode 0, F_2 mode 0" in two["statement"] and two["n"] == 20
    assert "the step error is not quadratic there" in two["statement"]
    elsewhere = R.summarise([*registered, two_step_point(40.0, 3.0, 1.2, tag="wb97x"), two_step_point(70.0, 3.0, 1.2),
                             two_step_point(45.0, 3.0, 1.2, sample=R.BIASED)], extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert elsewhere["outcome"] == R.OUTCOME_SOUND


def test_a_move_near_the_line_holds_nothing_back_once_every_point_has_both_steps() -> None:
    registered = [two_step_point(21.0 + 1.9 * i, 1.0 if i < 2 else 0.1) for i in range(20)]
    decision = R.summarise([*registered, two_step_point(40.0, 0.6, mol_id="N_1")], extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert decision["outcome"] == R.OUTCOME_SOUND and decision["n"] == 21
    missing = R.Extrapolation(({"id": "W_1", "reason": "no second step"},), Q2_RECORD)
    waiting = R.summarise([*registered], extrapolation=missing)["decision"]
    assert waiting["outcome"] == R.OUTCOME_NOT_STATED and "W_1" in waiting["statement"]


def test_the_extrapolated_read_writes_its_three_numbers_and_says_what_it_is(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    record = R.run(extrapolated(tmp_path))
    out = tmp_path / "out"
    header, first = (out / "points.csv").read_text(encoding="utf-8").splitlines()[:2]
    assert header.endswith("flags,small_step_change_cm,bias_removed_cm,large_minus_small_step_cm")
    small, large = math.sqrt(37.5 ** 2 + 7.0), math.sqrt(37.5 ** 2 + 28.0)
    assert first.endswith(f",{small - 35.0:+.4f},{small - 37.5:.4f},{large - small:+.4f}")
    text = (out / "RESULT.md").read_text(encoding="utf-8")
    assert "**Extrapolated to step zero (amendment 3 of the registration).**" in text and "1.3333·C(small) -0.3333·C(large)" in text
    assert "| M_1 mode 0 | 35.00 | 37.50 | +2.50 | +2.59 | 0.09 | +0.28 |" in text
    assert record["constants"]["not_quadratic_cm"] == 1.0 and record["constants"]["extrapolated_noise_factor"] == R.EXTRAPOLATED_NOISE_FACTOR
    assert record["inputs"]["second_steps"] == [[(tmp_path / "second").resolve().as_posix(), (tmp_path / "labels").resolve().as_posix()]]
    assert record["flagged_not_quadratic"] == 0 and record["flagged_directions"] == 0 and record["unread"] == []
    assert record["q2_test"] is None and record["decision"]["outcome"] == R.OUTCOME_NOT_STATED


def test_the_registered_read_carries_nothing_of_the_extrapolation(tmp_path: Path) -> None:
    write_molecule(tmp_path, "M_1", both([35.0, *STIFF]), both([37.5, *STIFF]))
    record = R.run(config(tmp_path))
    assert not {"unread", "flagged_not_quadratic", "flagged_directions", "q2_test"} & set(record)
    assert "second_steps" not in record["inputs"]
    assert "not_quadratic_cm" not in record["constants"] and "two_step_cm" not in record["decision"]["points"][0]
    assert (tmp_path / "out" / "points.csv").read_text(encoding="utf-8").splitlines()[0].endswith("turned_imaginary,flags")


@pytest.mark.skipif(not (READ_FOLDER / "read" / "record.json").is_file() or not (READ_FOLDER / "patch_step02_below60").is_dir(),
                    reason="the registered read's records are not in this checkout")
def test_the_registered_read_of_20_november_is_reproduced_byte_for_byte(tmp_path: Path) -> None:
    """The unchanged path on the stored patches against the read that ran on 20 November: the three files, to the byte."""
    cfg = R.ReadConfig((R.Source(READ_FOLDER / "patch_below60", CORPUS),), (R.Source(READ_FOLDER / "patch_step02_below60", CORPUS),),
                       CORPUS, tmp_path / "out", None, READ_FOLDER / "sample" / "sample.json")
    R.run(cfg)
    for name in ("record.json", "points.csv", "RESULT.md"):
        assert (tmp_path / "out" / name).read_bytes() == (READ_FOLDER / "read" / name).read_bytes(), name


@pytest.mark.skipif(not (READ_FOLDER / "patch_below60" / "B_0c6c144a7f").is_dir(), reason="the stored patch is not in this checkout")
@pytest.mark.parametrize("tag", V.LABEL_TAGS)
def test_a_stored_patch_is_rebuilt_from_its_columns_to_1e_6(tag: str) -> None:
    """The label and the stored columns of step 0.01 through `vibrations.patched_hessian` give the frequencies the runner stored."""
    mol = R.Molecule.read("B_0c6c144a7f", CORPUS, CORPUS)
    step = R.patch_of(mol, tag, R.Source(READ_FOLDER / "patch_below60", CORPUS), R.read_step)
    rebuilt = V.vibrational_modes(V.patched_hessian(mol.labels[tag], mol.masses, step["U"], step["C"]), mol.masses, mol.coords).omega_cm
    assert np.abs(rebuilt - np.sort(step["patched_vib"])).max() < 1e-6
    assert np.array_equal(R.rebuilt_modes(mol, tag, step).omega_cm, rebuilt)     # the read's own check passes on it


def test_the_step_analysis_tells_a_one_signed_step_bias_from_its_noise(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    write_two_steps(tmp_path, "M_2", [45.0, *STIFF], [45.2, *STIFF], quartic_cm2=9.0)
    write_two_steps(tmp_path, "M_3", [50.0, *STIFF], [50.2, *STIFF], second=False)
    labels = tmp_path / "labels"
    cfg = A.AnalysisConfig(R.Source(tmp_path / "patches", labels), R.Source(tmp_path / "second", labels), tmp_path / "molecules",
                           tmp_path / "analysis")
    record = A.run(cfg)
    assert (record["n"], record["positive"], record["negative"]) == (4, 4, 0) and record["chance_one_sign"] == 0.125
    assert record["curvature_diff_cm2"]["min"] == pytest.approx(21.0, abs=1e-6) and record["curvature_diff_cm2"]["max"] == pytest.approx(27.0, abs=1e-6)
    assert [g["diffs_cm2"] for g in record["functional_gaps"]] == [pytest.approx([21.0, 21.0], abs=1e-6), pytest.approx([27.0, 27.0], abs=1e-6)]
    point_1 = A.step_points(cfg)[0]
    assert point_1.noise_of_diff_cm(2e-8) == pytest.approx(point_1.noise_cm * 0.2 * math.sqrt(1.25))
    assert "4 have the large step above the small one and 0 below" in (tmp_path / "analysis" / "STEP_ANALYSIS.md").read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="an analysis writes into a folder of its own"):
        A.AnalysisConfig(cfg.small, cfg.large, cfg.molecules, tmp_path / "second" / "out")


def test_steps_along_rotated_directions_are_flagged_left_out_and_never_combined(tmp_path: Path) -> None:
    turn = np.array([[np.cos(0.4), -np.sin(0.4)], [np.sin(0.4), np.cos(0.4)]])
    write_two_steps(tmp_path, "M_1", [35.0, 55.0, 3700.0], [37.5, 56.0, 3700.0], quartic_cm2=7.0, directions=BASIS[:, :2],
                    large_directions=BASIS[:, :2] @ turn)
    cfg = extrapolated(tmp_path)
    points, unread = R.extrapolated_points(cfg)
    single = {(p.tag, p.mode): p for p in read_points(tmp_path)}
    assert unread == [] and len(points) == 4
    for p in points:
        assert p.flags == (R.DIRECTIONS_DIFFER,) and p.bias_removed_cm is None
        assert p.patched_cm == p.small_step_cm == single[p.tag, p.mode].patched_cm     # nothing is extrapolated: the small step's value
        assert p.noise_cm == single[p.tag, p.mode].noise_cm and p.two_step_cm > 0.1    # both frequencies are still known
    record = R.run(cfg)
    assert record["flagged_directions"] == 4 and record["unread"] == []
    assert record["decision"]["n"] == 0 and record["decision"]["bounds"]["flagged"] == 2
    assert [p["bias_removed_cm"] for p in record["decision"]["points"]] == [None, None]
    text = (tmp_path / "out" / "RESULT.md").read_text(encoding="utf-8")
    assert "| M_1 mode 0 | 35.00 | none | none | +2.59 | none |" in text and "directions differ |" in text
    assert ",directions differ,+2.5932,,+0.2783" in (tmp_path / "out" / "points.csv").read_text(encoding="utf-8")
    mol = R.Molecule.read("M_1", tmp_path / "labels", tmp_path / "molecules")
    small, large = (R.patch_of(mol, "b3lyp", source, R.read_step) for source in (cfg.sources[0], cfg.second_steps[0]))
    with pytest.raises(ValueError, match="different directions"):
        R.extrapolated_tag_points(mol, "b3lyp", small, large)
    with pytest.raises(ValueError, match="differ in shape"):
        R.extrapolated_columns(small["C"], large["C"][:, :1])


def test_a_second_step_that_measured_another_space_is_refused_not_flagged(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, 55.0, 3700.0], [37.5, 56.0, 3700.0], directions=BASIS[:, :2],
                    large_directions=BASIS[:, [0, 2]])
    with pytest.raises(ValueError, match="did not re-measure the same space"):
        R.extrapolated_points(extrapolated(tmp_path))


def test_points_with_rotated_directions_leave_the_rule_to_the_rest_and_to_the_floor_of_sixteen() -> None:
    rotated = [two_step_point(23.7, 0.1, mol_id="D_1", directions_differ=True),
               two_step_point(30.3, -0.4, mol_id="D_1", mode=1, directions_differ=True)]
    nineteen = [two_step_point(21.0 + 2.0 * i, 1.0 if i < 2 else 0.1) for i in range(19)]
    decision = R.summarise([*nineteen, *rotated], extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert decision["outcome"] == R.OUTCOME_SOUND and decision["n"] == 19 and decision["bounds"]["flagged"] == 2
    assert [p["flags"] for p in decision["points"] if p["id"] == "D_1"] == [[R.DIRECTIONS_DIFFER]] * 2
    fifteen = R.summarise([*nineteen[:15], *rotated], extrapolation=BOTH_STEPS_AND_Q2)["decision"]
    assert fifteen["outcome"] == R.OUTCOME_UNDECIDED and "fewer than the 16 points" in fifteen["statement"]


def test_the_extrapolated_read_states_no_outcome_without_a_q2_test_that_holds() -> None:
    points = [two_step_point(21.0 + 1.9 * i, 1.0 if i < 2 else 0.1) for i in range(20)]
    none = R.summarise(points, extrapolation=R.Extrapolation())["decision"]
    assert none["outcome"] == R.OUTCOME_NOT_STATED and "no record of the q² test was given" in none["statement"]
    assert (none["n"], none["moved"]) == (20, 2)                           # the arithmetic is printed; the outcome is not
    failed_record = Q2_RECORD | {"verdict": R.Q2_FAILS, "ratios": [{"id": "T_1", "tag": "b3lyp", "direction": 0, "ratio": 8.158}]}
    failed = R.summarise(points, extrapolation=R.Extrapolation((), failed_record))["decision"]
    assert failed["outcome"] == R.OUTCOME_NOT_STATED and "the q² test fails" in failed["statement"]
    assert "R = T_1 b3lyp 8.16" in failed["statement"] and "the registered read's outcome 3 stands" in failed["statement"]
    assert R.summarise(points, extrapolation=BOTH_STEPS_AND_Q2)["decision"]["outcome"] == R.OUTCOME_SOUND


def test_the_q2_record_is_named_explicitly_and_checked_before_it_is_believed(tmp_path: Path) -> None:
    write_two_steps(tmp_path, "M_1", [35.0, *STIFF], [37.5, *STIFF], quartic_cm2=7.0)
    path = tmp_path / "q2_test.json"
    path.write_text(json.dumps({"verdict": R.Q2_HOLDS, "interval": [4.0, 6.0], "predicted": 5.0,
                                "ratios": [{"id": "T_1", "tag": "b3lyp", "direction": 0, "ratio": 5.02, "noise_sd": 0.2}]}), encoding="utf-8")
    record = R.run(extrapolated(tmp_path, q2_test=path))
    assert record["q2_test"]["verdict"] == R.Q2_HOLDS and record["q2_test"]["ratios"][0]["ratio"] == 5.02
    assert record["decision"]["outcome"] == R.OUTCOME_UNDECIDED and "fewer than the 16 points" in record["decision"]["statement"]
    assert "the q² test holds" in (tmp_path / "out" / "RESULT.md").read_text(encoding="utf-8")
    source = f"{tmp_path / 'patches'}={tmp_path / 'labels'}"
    parsed = R.parse_args(["--source", source, "--second-step", f"{tmp_path / 'second'}={tmp_path / 'labels'}", "--q2-test", str(path),
                           "--molecules", str(tmp_path / "molecules"), "--out", str(tmp_path / "out")])
    assert parsed.q2_test == path and len(parsed.second_steps) == 1
    path.write_text(json.dumps({"verdict": "fine", "interval": [4.0, 6.0], "ratios": [{"ratio": 5.0}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="is no q²-test record"):
        R.run(extrapolated(tmp_path, q2_test=path))
    with pytest.raises(ValueError, match="belongs to the extrapolated read"):
        config(tmp_path, q2_test=path)
    with pytest.raises(FileNotFoundError):
        extrapolated(tmp_path, q2_test=tmp_path / "absent.json")


# --- the q² test on a third step (amendment 3, point 7) ------------------------------------------------------------------------------

def three_steps(root: Path, mol_id: str, true: list[float], terms: list[tuple[float, float]], **patch: object) -> A.AnalysisConfig:
    """A molecule patched at 0.01, 0.02 and 0.04 bohr into `patches`, `second` and `third`. `terms` gives each step's quartic and
    sextic term: the same pair thrice is one potential, different pairs stand for errors that follow no law."""
    U = np.asarray(patch.get("directions", BASIS[:, :1]), float)
    label = [35.0, 55.0, 3700.0]
    write_molecule(root, mol_id, both(label), both(label))
    steps = zip(("patches", "second", "third"), (0.01, 0.02, float(patch.get("third_step", 0.04))), terms,
                (U, U, np.asarray(patch.get("third_directions", U), float)), strict=True)
    for folder, step, (quartic, sextic), directions in steps:
        write_step(root, folder, mol_id, label, measured_columns(true, directions, step, quartic, sextic), directions=directions, step=step)
    labels = root / "labels"
    return A.AnalysisConfig(R.Source(root / "patches", labels), R.Source(root / "second", labels), root / "molecules", root / "q2",
                            R.Source(root / "third", labels))


def test_an_error_that_grows_as_q2_gives_a_ratio_of_five_and_the_law_holds(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    cfg = three_steps(tmp_path, "T_1", [37.5, 56.0, 3700.0], [(7.0, 0.0)] * 3)
    A.main(["--small", f"{cfg.small.patches}={cfg.small.labels}", "--large", f"{cfg.large.patches}={cfg.large.labels}",
            "--third", f"{cfg.third.patches}={cfg.third.labels}", "--molecules", str(cfg.molecules), "--out", str(cfg.out)])
    assert "**The law holds.**" in capsys.readouterr().out
    record = json.loads((cfg.out / "q2_test.json").read_text(encoding="utf-8"))
    assert pytest.approx(5.0, rel=1e-15) == A.Q2_PREDICTED and record["verdict"] == R.Q2_HOLDS and record["interval"] == [4.0, 6.0]
    assert [(r["id"], r["tag"]) for r in record["ratios"]] == [("T_1", "b3lyp"), ("T_1", "wb97x")]
    for r in record["ratios"]:
        assert r["ratio"] == pytest.approx(5.0, abs=1e-6) and r["inside"] and r["noise_sd"] > 0
        assert r["curvature_cm2"] == pytest.approx([37.5 ** 2 + 7.0, 37.5 ** 2 + 28.0, 37.5 ** 2 + 112.0], abs=1e-6)
        assert r["zero_two_step_cm2"] == pytest.approx(37.5 ** 2, abs=1e-6) and r["zero_three_step_cm2"] == pytest.approx(37.5 ** 2, abs=1e-6)
    read = R.run(extrapolated(tmp_path, q2_test=cfg.out / "q2_test.json"))       # the read takes the record the test wrote
    assert read["q2_test"]["verdict"] == R.Q2_HOLDS and "No outcome is stated" not in read["decision"]["statement"]


def test_a_q4_term_beside_the_q2_term_moves_the_ratio_out_and_the_law_fails(tmp_path: Path) -> None:
    record = A.run_q2_test(three_steps(tmp_path, "T_1", [37.5, 56.0, 3700.0], [(7.0, 0.5)] * 3))
    assert record["verdict"] == R.Q2_FAILS
    for r in record["ratios"]:
        assert r["ratio"] == pytest.approx((112.0 + 128.0 - 7.5) / (28.0 + 8.0 - 7.5), abs=1e-6) and not r["inside"]     # 8.16
        assert r["zero_three_step_cm2"] == pytest.approx(37.5 ** 2, abs=1e-6)             # three points remove both terms,
        assert r["zero_two_step_cm2"] == pytest.approx(37.5 ** 2 - 4 * 0.5, abs=1e-6)     # two leave −4·b·q⁴


def test_differences_that_are_noise_give_no_ratio_of_five_and_the_law_fails(tmp_path: Path) -> None:
    """Offsets of +0.3, −0.2 and +0.1 cm⁻² at the three steps, as noise would leave them: R = (0.1 − 0.3) / (−0.2 − 0.3) = 0.4."""
    record = A.run_q2_test(three_steps(tmp_path, "T_1", [37.5, 56.0, 3700.0], [(0.3, 0.0), (-0.05, 0.0), (0.1 / 16, 0.0)]))
    assert record["verdict"] == R.Q2_FAILS and [r["ratio"] for r in record["ratios"]] == [pytest.approx(0.4, abs=1e-5)] * 2


def test_one_ratio_outside_fails_the_law_and_the_bounds_are_inside(tmp_path: Path) -> None:
    """A q⁴ term of 1.818 % of the q² term at the small step puts R on 6.0; just beyond it the law fails."""
    inside = A.run_q2_test(three_steps(tmp_path / "a", "T_1", [37.5, 56.0, 3700.0], [(7.0, 7.0 * 0.018)] * 3))
    beyond = A.run_q2_test(three_steps(tmp_path / "b", "T_1", [37.5, 56.0, 3700.0], [(7.0, 7.0 * 0.0185)] * 3))
    assert inside["verdict"] == R.Q2_HOLDS and 5.9 < inside["ratios"][0]["ratio"] < 6.0
    assert beyond["verdict"] == R.Q2_FAILS and 6.0 < beyond["ratios"][0]["ratio"] < 6.1


def test_the_ratios_noise_follows_from_the_three_curvatures_by_propagation() -> None:
    c, noise = [1204.3, 1233.4, 1349.9], 1.88
    eps = 1e-6
    slopes = [(A.q2_ratio([x + eps * (i == j) for j, x in enumerate(c)]) - A.q2_ratio(c)) / eps for i in range(3)]
    by_hand = math.sqrt(sum((slope * noise / R.STEP_RATIO ** i) ** 2 for i, slope in enumerate(slopes)))
    assert A.q2_ratio_noise(c, noise) == pytest.approx(by_hand, rel=1e-5)
    assert A.q2_ratio_noise([0.0, 30.0, 150.0], 1.88) == pytest.approx(1.88 / 30.0 * math.sqrt(16 + 6.25 + 0.0625))    # 0.296 at R = 5
    assert A.three_step_zero([3.0 + 2.0 + 0.5, 3.0 + 8.0 + 8.0, 3.0 + 32.0 + 128.0]) == pytest.approx(3.0)
    with pytest.raises(ValueError, match="the ratio is undefined"):
        A.q2_ratio([10.0, 10.0, 12.0])


def test_a_third_step_along_rotated_directions_or_not_twice_the_second_is_refused(tmp_path: Path) -> None:
    turn = np.array([[np.cos(0.4), -np.sin(0.4)], [np.sin(0.4), np.cos(0.4)]])
    rotated = three_steps(tmp_path / "rotated", "T_1", [37.5, 56.0, 3700.0], [(7.0, 0.0)] * 3, directions=BASIS[:, :2],
                          third_directions=BASIS[:, :2] @ turn)
    with pytest.raises(ValueError, match="different directions"):
        A.run_q2_test(rotated)
    with pytest.raises(ValueError, match=r"0\.02 and 0\.03 bohr"):
        A.run_q2_test(three_steps(tmp_path / "ratio", "T_1", [37.5, 56.0, 3700.0], [(7.0, 0.0)] * 3, third_step=0.03))
    with pytest.raises(ValueError, match="needs a third step"):
        A.q2_rows(A.AnalysisConfig(rotated.small, rotated.large, rotated.molecules, tmp_path / "out"))
