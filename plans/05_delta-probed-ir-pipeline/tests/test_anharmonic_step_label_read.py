"""probes/anharmonic_step_label_read.py on synthetic records with the regime's edge cases (CLAUDE.md, 'Evidence': a
registration's read script runs on them before the registration is committed), and the pin that its per-family rms is the
arithmetic of the printed bars: coronene's and tetracene's registered numbers from the stored rows, by the same function.
Nothing here computes a force field.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import anharmonic_step_label_read as R  # noqa: E402
from s1_anharmonic_level import harmonic_modes  # noqa: E402

RESULTS = PLAN / "probes" / "results_m1"
BENZENE_REF = RESULTS / "routea_2026-11-02" / "gate" / "benzene" / "G" / "ref.json"      # tracked: a real B3LYP record to build labels on
BARS = {"CH-oop": 8.38, "other": 3.84, "ring-ip": 3.37, "CH-stretch": 6.21}
# Per molecule, x2* against the label, as the reads behind the printed bars state them: route_rule.md (the three mid families,
# also PreRegistration_2026-11-14_Printed_Band_Position.md section 3) and route_rule_ch.md (CH-stretch 6.94 / 5.68, pooled
# 6.2143, the printed 6.21). Amendment 1's "6.92 / 5.67" is the format-3 refit of 17 Nov (acceptance.md, pooled 6.1994), whose
# rows are not stored: it cannot be reproduced from a record, and the printed bar is not that number.
REGISTERED = {
    "s3_read_exclude": {"coronene": {"ring-ip": 4.25, "other": 5.69, "CH-oop": 11.91}, "tetracene": {"ring-ip": 2.35, "other": 1.09, "CH-oop": 4.55}},
    "s3_read_ch": {"coronene": {"CH-stretch": 6.94}, "tetracene": {"CH-stretch": 5.68}},
}


def row(family: str, error: float | None, omega: float = 1000.0, **over: object) -> dict:
    """One compared band: a step of −10 and a label `error` below it; None leaves the band without a step."""
    stepped = error is not None
    base = {"omega_cm": omega, "family": family, "step_delta_cm": -10.0 if stepped else None, "bar_cm": BARS[family] if stepped else None,
            "step_reason": None if stepped else "unmeasured", "label_omega_cm": omega, "label_family": family,
            "label_delta_cm": -10.0 - (error or 0.0), "label_marked": False, "label_overlap": 1.0, "error_cm": error,
            "not_counted": None if stepped else "no step: unmeasured"}
    return {**base, **over}


def rows_of(errors: dict[str, list[float]]) -> list[dict]:
    return [row(fa, e) for fa, es in errors.items() for e in es]


def test_the_line_by_n_is_the_chi_square_quantile_of_an_rms() -> None:
    """√(χ²₀.₉₅(n)/n) on the tabulated quantiles 9.488, 11.070, 12.592, 21.026, and the review's figures for the expected counts."""
    table = {4: 9.488, 5: 11.070, 6: 12.592, 12: 21.026}
    assert {n: round(R.line_factor(n) ** 2 * n, 3) for n in table} == table
    assert [round(R.line_factor(n), 2) for n in (12, 6, 5)] == [1.32, 1.45, 1.49]
    assert (R.line_cm(12, 3.37), R.line_cm(6, 8.38), R.line_cm(5, 6.21)) == (4.46, 12.14, 9.24)
    assert R.line_factor(1000) < 1.04 < R.line_factor(100)          # more bands, a narrower line
    with pytest.raises(ValueError, match="at least one"):
        R.line_factor(0)


def test_every_family_within_its_bar_is_no_family_beyond() -> None:
    families = R.judge(rows_of({"ring-ip": [3.0, -3.0, 2.0, -2.0], "CH-oop": [8.0] * 5, "other": [1.0] * 4, "CH-stretch": [6.0] * 4}), BARS)
    assert {fa: f["statement"] for fa, f in families.items()} == dict.fromkeys(BARS, R.WITHIN)
    assert R.outcome(families) == R.NONE_BEYOND and families["ring-ip"]["n"] == 4 and families["ring-ip"]["line_cm"] == R.line_cm(4, 3.37)


def test_a_family_above_its_bar_and_under_its_line_is_consistent_and_changes_nothing() -> None:
    families = R.judge(rows_of({"ring-ip": [4.0] * 12, "CH-oop": [1.0] * 4}), BARS)
    assert families["ring-ip"]["statement"] == R.CONSISTENT and R.outcome(families) == R.NONE_BEYOND
    assert "may go to a reviewed change" in R.CONSEQUENCE[R.NONE_BEYOND]


def test_one_family_beyond_its_line_makes_the_molecule_beyond() -> None:
    families = R.judge(rows_of({"ring-ip": [3.0] * 6, "CH-stretch": [12.0, -12.0, 12.0, -12.0], "CH-oop": [9.0] * 4}), BARS)
    assert families["CH-stretch"]["statement"] == R.BEYOND and families["ring-ip"]["statement"] == R.WITHIN
    assert families["CH-oop"]["statement"] == R.CONSISTENT
    assert families["CH-stretch"]["rms_cm"] == pytest.approx(12.0) and R.outcome(families) == R.BEYOND
    assert "default does not change" in R.CONSEQUENCE[R.BEYOND]


@pytest.mark.parametrize(("family", "n"), [("ring-ip", 12), ("CH-oop", 6), ("CH-stretch", 5), ("other", 4)])
def test_both_boundaries_of_every_family_at_its_expected_count(family: str, n: int) -> None:
    """At the bar: within. One hundredth above: consistent. At the line: consistent. One hundredth above the line: beyond."""
    bar, line = BARS[family], R.line_cm(n, BARS[family])
    said = [R.statement(n, value, bar) for value in (bar, bar + 0.01, line, line + 0.01)]
    assert said == [R.WITHIN, R.CONSISTENT, R.CONSISTENT, R.BEYOND]
    assert R.statement(n - 1 if n == 4 else 3, 99.0, bar) == R.NO_STATEMENT


def test_a_family_with_fewer_than_four_bands_is_reported_without_a_statement() -> None:
    families = R.judge(rows_of({"other": [9.0, 9.0, 9.0], "ring-ip": [1.0] * 4}), BARS)
    assert families["other"] == {"n": 3, "rms_cm": pytest.approx(9.0), "bar_cm": 3.84, "line_cm": None, "statement": R.NO_STATEMENT,
                                 "n_every_stepped_band": 3, "rms_every_stepped_band_cm": pytest.approx(9.0)}
    assert R.outcome(families) == R.NONE_BEYOND       # the three bands at 9 decide nothing: the family is not judged by this molecule
    assert families["CH-oop"]["n"] == 0 and families["CH-oop"]["rms_cm"] is None and families["CH-oop"]["statement"] == R.NO_STATEMENT


def test_no_family_with_four_bands_is_no_statement_at_all() -> None:
    families = R.judge(rows_of({"other": [9.0] * 3, "ring-ip": [9.0] * 3}), BARS)
    assert R.outcome(families) == R.NO_STATEMENT and "default does not change" in R.CONSEQUENCE[R.NO_STATEMENT]


@pytest.mark.parametrize(("error", "said"), [(3.37, R.WITHIN), (3.374, R.WITHIN), (3.376, R.CONSISTENT), (5.19, R.CONSISTENT),
                                             (5.194, R.CONSISTENT), (5.196, R.BEYOND)])
def test_an_rms_exactly_at_the_bar_or_the_line_is_on_the_mild_side_and_is_compared_as_printed(error: float, said: str) -> None:
    families = R.judge(rows_of({"ring-ip": [error, -error, error, -error]}), BARS)
    assert families["ring-ip"]["statement"] == said


def test_a_band_without_a_step_is_listed_with_the_labels_shift_and_stays_out_of_the_rms() -> None:
    rows = [*rows_of({"other": [1.0] * 4}), row("other", None, omega=167.5, label_delta_cm=-3.2)]
    families = R.judge(rows, BARS)
    assert families["other"]["n"] == 4 and families["other"]["rms_cm"] == pytest.approx(1.0)
    text = "\n".join(R.report({"run": "r", "label": "l", "geometry_rms_bohr": 0.0, "outcome": R.outcome(families), "families": families,
                               "bands": rows}))
    assert "| 167.5 | unmeasured | -3.2 | no |" in text


def test_a_band_stepped_without_the_bars_claim_is_outside_the_statement_and_inside_the_second_column() -> None:
    unbarred = row("other", 20.0, bar_cm=None, not_counted=R.not_counted(-10.0, None, -30.0, False, None))
    families = R.judge([*rows_of({"other": [1.0] * 4}), unbarred], BARS)
    assert unbarred["not_counted"].startswith("stepped without the family's bar")
    assert families["other"]["n"] == 4 and families["other"]["statement"] == R.WITHIN
    assert families["other"]["n_every_stepped_band"] == 5 and families["other"]["rms_every_stepped_band_cm"] > 8.0


def test_a_band_whose_label_mode_is_outside_vpt2s_domain_is_in_neither() -> None:
    marked = row("ring-ip", 150.0, label_marked=True, not_counted=R.not_counted(-10.0, 3.37, -160.0, True, None))
    families = R.judge([*rows_of({"ring-ip": [1.0] * 4}), marked], BARS)
    assert families["ring-ip"]["n"] == 4 and families["ring-ip"]["n_every_stepped_band"] == 4


def test_a_band_printed_in_another_family_than_its_label_modes_is_listed() -> None:
    rows = [*rows_of({"ring-ip": [1.0] * 4}), row("ring-ip", 2.5, omega=1307.2, label_family="other")]
    text = "\n".join(R.mismatch_lines(rows))
    assert "| 1307.2 | ring-ip | other | 2.5 |" in text and "printed family's bar" in text
    assert R.judge(rows, BARS)["ring-ip"]["n"] == 5                     # judged in the printed family
    assert R.mismatch_lines(rows_of({"ring-ip": [1.0] * 4}))[-1] == "None."


def test_why_a_band_is_not_counted_in_the_order_the_read_asks() -> None:
    assert R.not_counted(None, None, -3.0, False, "unmeasured") == "no step: unmeasured"
    assert R.not_counted(-10.0, 3.37, None, False, None) == "no label mode matches the band"
    assert R.not_counted(-10.0, 3.37, -9.0, True, None) == "the label's mode is outside VPT2's domain"
    assert R.not_counted(-10.0, 3.37, -9.0, False, None) is None


# --- the label and the run it is read against ---------------------------------------------------------------------------------


def label_folder(tmp_path: Path, marked: tuple[int, ...] = (), pairs: tuple[tuple[int, int], ...] = (), shift: float = -12.0) -> tuple[Path, Path]:
    """A G folder and its GVPT2 file on the tracked benzene record: every mode shifted by `shift`."""
    g = tmp_path / "g" / "benzene" / "G"
    g.mkdir(parents=True)
    shutil.copy2(BENZENE_REF, g / "ref.json")
    omega, _ = harmonic_modes(str(g / "ref.json"))
    np.savez(g / "qff_report.npz", omega_cm=omega)
    label = tmp_path / "gvpt2_g" / "benzene.json"
    label.parent.mkdir()
    label.write_text(json.dumps({"id": "benzene", "omega": omega.tolist(), "nu_gvpt2": (omega + shift).tolist(),
                                 "degenerate_pairs": [list(p) for p in pairs], "vpt2_domain": {"marked": list(marked)}}), encoding="utf-8")
    return g, label


def bands_on_the_label(g: Path, keep: slice = slice(None), stretch: float = 1.0) -> R.Bands:
    """A run whose bands are the label's own modes: every band stepped −10 in 'ring-ip' under its bar, the first unmeasured."""
    molecule = json.loads((g / "ref.json").read_text(encoding="utf-8"))["molecule"]
    omega, q = harmonic_modes(str(g / "ref.json"))
    omega, q = omega[keep], q[:, keep]
    sticks = [{"omega_cm": round(float(w), 1), "nu_cm": round(float(w) - 10.0, 1),
               "anharmonic": {"delta_anh_cm": -10.0, "bar_cm": 3.37, "reason": None, "family": "ring-ip"}} for w in omega]
    sticks[0]["anharmonic"] = {"delta_anh_cm": None, "bar_cm": None, "reason": "unmeasured", "family": "other"}
    coords = np.asarray(molecule["geometry"], float).reshape(-1, 3) * stretch
    return R.Bands(list(molecule["symbols"]), coords, omega, q, sticks, dict(BARS))


def test_a_label_of_the_runs_own_molecule_is_read_band_by_band(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path, marked=(5,))
    bands = bands_on_the_label(g)
    label = R.load_label(g, label_file, bands)
    rows = R.compare(bands, label)
    assert label.geometry_rms_bohr < 1e-9 and len(rows) == 30
    assert rows[0]["not_counted"] == "no step: unmeasured" and rows[0]["label_delta_cm"] == pytest.approx(-12.0)
    flagged = [r for r in rows if r["label_marked"]]
    assert len(flagged) >= 1 and all(r["not_counted"] == "the label's mode is outside VPT2's domain" for r in flagged)
    counted = [r for r in rows if r["not_counted"] is None]
    assert all(r["error_cm"] == pytest.approx(2.0) for r in counted)
    families = R.judge(rows, bands.bars)
    assert families["ring-ip"]["n"] == len(counted) and families["ring-ip"]["rms_cm"] == pytest.approx(2.0)


def test_a_label_at_another_geometry_is_refused(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path)
    with pytest.raises(ValueError, match="another geometry"):
        R.load_label(g, label_file, bands_on_the_label(g, stretch=1.05))


def test_a_label_of_other_atoms_or_another_order_is_refused(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path)
    bands = bands_on_the_label(g)
    swapped = R.Bands([*bands.symbols[1:], bands.symbols[0]], bands.coords, bands.omega, bands.q, bands.sticks, bands.bars)
    if swapped.symbols == bands.symbols:
        pytest.fail("the fixture's atoms are all one element: the swap changes nothing")
    with pytest.raises(ValueError, match="in the result's order"):
        R.load_label(g, label_file, swapped)


def test_a_label_with_another_number_of_modes_than_the_run_has_bands_is_refused(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path)
    with pytest.raises(ValueError, match="30 modes and the run 29 bands"):
        R.load_label(g, label_file, bands_on_the_label(g, keep=slice(1, None)))


def test_a_noisy_force_field_is_not_read_and_says_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    g, label_file = label_folder(tmp_path)
    (g / "NOISY").touch()
    with pytest.raises(R.NotReadError, match="NOISY"):
        R.load_label(g, label_file, bands_on_the_label(g))
    run = tmp_path / "run"
    run.mkdir()
    for name in ("pipeline.json", "geometry.json"):
        (run / name).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(R, "load_bands", lambda folder: bands_on_the_label(g))
    out = tmp_path / "read"
    assert R.main(["read", "--run", str(run), "--g-dir", str(g), "--label", str(label_file), "--out", str(out)]) == 3
    record = json.loads((out / "label_read.json").read_text(encoding="utf-8"))
    assert record["read"] is False and "NOISY" in record["reason"] and "families" not in record
    assert "not read" in (out / "RESULT.md").read_text(encoding="utf-8")


def test_a_label_with_symmetry_pairs_or_without_the_domain_check_is_refused(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path, pairs=((3, 4),))
    with pytest.raises(ValueError, match="symmetry pairs"):
        R.load_label(g, label_file, bands_on_the_label(g))
    record = json.loads(label_file.read_text(encoding="utf-8"))
    del record["vpt2_domain"]
    label_file.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="predates the VPT2-domain check"):
        R.load_label(g, label_file, bands_on_the_label(g))


def test_the_command_writes_the_record_once_and_never_over_it(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    g, label_file = label_folder(tmp_path)
    run = tmp_path / "run"
    run.mkdir()
    for name in ("pipeline.json", "geometry.json"):
        (run / name).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(R, "load_bands", lambda folder: bands_on_the_label(g))
    args = ["read", "--run", str(run), "--g-dir", str(g), "--label", str(label_file), "--out", str(tmp_path / "read")]
    assert R.main(args) == 0
    record = json.loads((tmp_path / "read" / "label_read.json").read_text(encoding="utf-8"))      # strict JSON: no NaN in it
    assert record["read"] is True and record["outcome"] == R.NONE_BEYOND and record["families"]["ring-ip"]["n"] == 29
    assert record["families"]["CH-oop"]["rms_cm"] is None and not list((tmp_path / "read").glob("*.tmp"))
    text = (tmp_path / "read" / "RESULT.md").read_text(encoding="utf-8")
    assert f"**Outcome: {R.NONE_BEYOND}.**" in text and "## Bands whose printed family differs" in text and "one run in seven" in text
    with pytest.raises(ValueError, match="never overwritten"):
        R.main(args)


def test_a_run_without_the_step_or_without_its_files_is_refused(tmp_path: Path) -> None:
    g, label_file = label_folder(tmp_path)
    with pytest.raises(ValueError, match=r"pipeline\.json is missing"):
        R.ReadConfig(tmp_path / "no_run", g, label_file, tmp_path / "out")
    run = tmp_path / "run"
    run.mkdir()
    (run / "pipeline.json").write_text(json.dumps({"spectra": {"network": {"sticks": []}, "anharmonic": {"status": "not applied"}}}),
                                       encoding="utf-8")
    with pytest.raises(ValueError, match="was not applied"):
        R.load_bands(run)


def test_the_real_benzonitrile_record_reads_band_for_band_against_its_own_b3lyp_modes() -> None:
    """The real path, without a label: the run of 19 Nov with its own B3LYP modes standing in for the label's. All 33 bands find
    their mode, and no band's printed family differs from its mode's."""
    run = RESULTS / "pipeline_benzonitrile_anharmonic_v3_2026-11-19" / "benzonitrile"
    if not (run / "correction.npz").exists():
        pytest.skip(f"data not present: {run}")
    bands = R.load_bands(run)
    modes = R.AS.Modes.from_hessian(R.AN.low_hessian(run), bands.symbols, bands.coords)
    recorded = json.loads((run / "anharmonic.json").read_text(encoding="utf-8"))["modes"]
    stand_in = R.Label(modes.omega, np.zeros(len(modes.omega)), np.zeros(len(modes.omega), bool), np.array([m["family"] for m in recorded]),
                       modes.q, 0.0)
    rows = R.compare(bands, stand_in)
    assert len(rows) == 33 and bands.bars == BARS and all(r["label_omega_cm"] is not None for r in rows)
    assert R.mismatch_lines(rows)[-1] == "None." and all(r["family"] == r["label_family"] for r in rows)
    families = R.judge(rows, bands.bars)
    assert {fa: f["n"] for fa, f in families.items()} == {"CH-oop": 6, "other": 3, "ring-ip": 12, "CH-stretch": 5}
    assert families["other"]["n_every_stepped_band"] == 4 and sum(r["step_delta_cm"] is None for r in rows) == 6


# --- the same arithmetic as the printed bars --------------------------------------------------------------------------------------


@pytest.mark.parametrize("read", sorted(REGISTERED))
def test_the_reads_rms_is_the_arithmetic_of_the_printed_bars(read: str) -> None:
    """Coronene's and tetracene's registered per-molecule numbers come out of the stored rows by the function this read uses."""
    stored = RESULTS / "labels_domain_2026-11-13" / read / "s3_read.json"
    if not stored.exists():
        pytest.skip(f"record not present: {stored} (the CH window's read is not tracked)")
    rows = json.loads(stored.read_text(encoding="utf-8"))["read"]["rows"]
    for molecule, expected in REGISTERED[read].items():
        r = rows[molecule]
        got = R.family_errors(np.array(r["family"]), np.array(r["pred"]["x2*"], float), np.array(r["truth"], float))
        assert {fa: round(got[fa]["rms_cm"], 2) for fa in expected} == expected
    targets = [rows[m] for m in REGISTERED[read]]
    pooled = R.family_errors(np.concatenate([np.array(r["family"]) for r in targets]),
                             np.concatenate([np.array(r["pred"]["x2*"], float) for r in targets]),
                             np.concatenate([np.array(r["truth"], float) for r in targets]))
    families = list(REGISTERED[read]["coronene"])
    assert {fa: round(pooled[fa]["rms_cm"], 2) for fa in families} == {fa: BARS[fa] for fa in families}     # together: the printed bar itself


# --- the prior table --------------------------------------------------------------------------------------------------------------


def test_the_committed_prior_table_is_what_the_stored_read_gives() -> None:
    record = R.prior(RESULTS / "anharmonic_design_questions_2026-11-16" / "modes.json")
    assert list(record["molecules"]) == list(R.SUBSTITUTED) and record["bars_cm"] == BARS
    worst = record["molecules"]["B_78f8233b4c"]["families"]["CH-stretch"]
    assert (round(worst["rms_cm"], 2), worst["n"], worst["statement"]) == (17.98, 7, R.BEYOND)
    counts = {g: {fa: (v[fa]["above_the_bar"], v[fa]["beyond_the_line"], v[fa]["molecules_judged"]) for fa in BARS}
              for g, v in record["groups"].items()}
    assert counts == {"substituted": {"CH-oop": (1, 0, 3), "other": (2, 2, 6), "ring-ip": (5, 3, 7), "CH-stretch": (4, 4, 6)},
                      "unsubstituted": {"CH-oop": (3, 1, 28), "other": (4, 3, 30), "ring-ip": (6, 1, 31), "CH-stretch": (22, 7, 31)}}
    assert record["groups"]["unsubstituted"]["molecules"] == 31 and record["groups"]["unsubstituted"]["not_training_molecules"] == ["coronene"]
    assert round(record["groups"]["unsubstituted"]["CH-stretch"]["pooled_rms_cm"], 2) == 8.52
    few = record["molecules"]["B_052693bd01"]["families"]["CH-oop"]
    assert (few["n"], few["statement"]) == (2, R.NO_STATEMENT)
    committed = json.loads((RESULTS / "anharmonic_step_substituted_2026-11-20" / "prior" / "prior.json").read_text(encoding="utf-8"))
    assert committed["molecules"] == json.loads(json.dumps(record["molecules"])) and committed["groups"] == json.loads(json.dumps(record["groups"]))
    assert "| azulene+NH2 | B_78f8233b4c | — | **6.15 (10)** | **4.51 (15)** | **17.98 (7)** | 9.59 (32) |" in R.prior_report(record)


def test_the_prior_table_is_never_written_over(tmp_path: Path) -> None:
    (tmp_path / "prior.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="never overwritten"):
        R.main(["prior", "--modes-json", str(RESULTS / "anharmonic_design_questions_2026-11-16" / "modes.json"), "--out", str(tmp_path)])
