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
