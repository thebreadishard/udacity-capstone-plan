"""probes/anharmonic_step.py (TASKS 211): the artefact's refusals, every route a mode can take, the carry to the corrected bands,
and — on the force fields on disk, which git does not hold — that a training molecule fed through the step gets exactly the shift
the registered read's own path gives it.

The data tests read under DPIR_DATA_ROOT (default: this checkout's plan folder) and skip where the force fields are absent. They
do not turn into failures under DPIR_REQUIRE_DATA, which is for data that is committed: these 165 MB are not."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import anharmonic_step as A  # noqa: E402
import s2_xtb_read as X  # noqa: E402
import s3_read as S3  # noqa: E402
from s2_read import concat  # noqa: E402

DATA = Path(os.environ.get("DPIR_DATA_ROOT", PLAN))
SETS = "probes/results_m1/labels_domain_2026-11-13/sets.json"
TRAINING_PAIR = ("B_0603418c5b", "A_541c53d1a5")          # one of S2 (it has a marked, large-amplitude mode) and one of S2b
RANK_MOLECULE = "B_78f8233b4c"                            # 13 of its 54 modes change rank under the ωB97X Hessian (modes.json, 16 Nov)
CONFIG = X.X2_GRID[0].name


def _table(families: list[str], n: int, lo: float, hi: float, seed: int) -> dict[str, list]:
    rng = np.random.default_rng(seed)
    fam = [families[i % len(families)] for i in range(n)]
    xtb = rng.normal(-10.0, 4.0, n)
    return {"omega": np.linspace(lo, hi, n).tolist(), "delta": (xtb + rng.normal(0.0, 1.0, n)).tolist(), "family": fam,
            "h": rng.uniform(0, 1, n).tolist(), "o": rng.uniform(0, 1, n).tolist(), "xtb": xtb.tolist()}


def _family(config: str, table: dict, family: str, bar: float) -> dict:
    return {"config": config, "bar_cm": bar, "bar_refit_cm": bar, "n_training_modes": table["family"].count(family), "n_target_rows": 9}


def _record() -> dict:
    """A small artefact of two windows: 'mid' with ring-ip and other, 'ch' with the CH stretches."""
    mid, ch = _table(["ring-ip", "other"], 40, 560.0, 1990.0, 1), _table(["CH-stretch"], 12, 3000.0, 3200.0, 2)
    src = {"marked_policy": "exclude", "route_rule": "rule.json", "s2b_read": "s2b.json", "s3_read": "s3.json"}
    return {"format": A.FORMAT, "model": A.MODEL, "commit": "abc", "registration": "reg.md", "decisions": "report.md",
            "scope": "no-large-amplitude", "training_molecules": ["m1", "m2"],
            "windows": {"mid": {**src, "window": [550.0, 2000.0], "table": mid,
                                "families": {"ring-ip": _family(CONFIG, mid, "ring-ip", 3.37), "other": _family(CONFIG, mid, "other", 3.84)}},
                        "ch": {**src, "window": [2800.0, None], "table": ch,
                               "families": {"CH-stretch": _family(CONFIG, ch, "CH-stretch", 6.21)}}}}


def _write(tmp_path: Path, record: dict) -> str:
    path = tmp_path / "artefact.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return str(path)


@pytest.fixture
def artefact(tmp_path: Path) -> A.Artefact:
    return A.load_artefact(_write(tmp_path, _record()))


def test_the_artefact_loads_with_an_open_window_and_its_bars(artefact: A.Artefact):
    assert [w.name for w in artefact.windows] == ["mid", "ch"] and artefact.windows[1].bounds == (2800.0, np.inf)
    assert A.bars(artefact) == {"ring-ip": 3.37, "other": 3.84, "CH-stretch": 6.21}
    assert artefact.header["window_sources"]["mid"]["s3_read"] == "s3.json" and "table" not in artefact.header["window_sources"]["mid"]


def _other_format(r: dict) -> None:
    r["format"] = 2


def _no_commit(r: dict) -> None:
    r["commit"] = None


def _no_read(r: dict) -> None:
    del r["windows"]["ch"]["s3_read"]


def _no_molecules(r: dict) -> None:
    r["training_molecules"] = []


def _short_column(r: dict) -> None:
    r["windows"]["mid"]["table"]["xtb"].pop()


def _unknown_config(r: dict) -> None:
    r["windows"]["mid"]["families"]["other"]["config"] = "krr-FX α=7 γ=7"


def _wrong_count(r: dict) -> None:
    r["windows"]["mid"]["families"]["other"]["n_training_modes"] += 1


def _family_twice(r: dict) -> None:
    r["windows"]["ch"]["families"]["other"] = dict(r["windows"]["mid"]["families"]["other"], n_training_modes=0)


@pytest.mark.parametrize(("spoil", "match"), [
    (_other_format, "this code reads format"), (_no_commit, "cannot be traced"), (_no_read, "cannot be traced"),
    (_no_molecules, "cannot be traced"), (_short_column, "differ in length"), (_unknown_config, "not one of the read's"),
    (_wrong_count, "the record says"), (_family_twice, "the record says|two windows")])
def test_an_artefact_that_cannot_be_trusted_is_refused(tmp_path: Path, spoil, match: str):
    record = _record()
    spoil(record)
    with pytest.raises(ValueError, match=match):
        A.load_artefact(_write(tmp_path, record))


def test_a_family_modelled_in_two_windows_is_refused(tmp_path: Path):
    record = _record()
    record["windows"]["ch"]["table"] = _table(["CH-stretch", "other"], 12, 3000.0, 3200.0, 2)
    table = record["windows"]["ch"]["table"]
    record["windows"]["ch"]["families"] = {f: _family(CONFIG, table, f, 5.0) for f in ("CH-stretch", "other")}
    with pytest.raises(ValueError, match="two windows"):
        A.load_artefact(_write(tmp_path, record))


#          mode:     0          1          2          3          4            5        6          7             8
ROUTES = {"omega": [300.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0, 3050.0, 3100.0],
          "family": ["other", "ring-ip", "ring-ip", "ring-ip", "other", "other", "CH-oop", "CH-stretch", "other"],
          "o": [0.9, 0.0, 0.0, 0.0, 0.85, 0.79, 1.0, 0.0, 0.0],
          "large_amplitude": [0, 0, 1, 0, 0, 0, 0, 0, 0], "no_xtb": [0, 0, 0, 1, 0, 0, 0, 0, 0], "vpt2_marked": [0, 0, 1, 1, 0, 0, 0, 0, 0]}
EXPECTED = [A.UNMEASURED, None, A.LARGE_AMPLITUDE, A.NO_XTB_PARTNER, None, None, A.UNMEASURED, None, A.UNMEASURED]


def _synthetic_rec(marked_instead: int | None = None) -> dict[str, np.ndarray]:
    n = len(ROUTES["omega"])
    rec = {"omega": np.array(ROUTES["omega"]), "family": np.array(ROUTES["family"]), "o": np.array(ROUTES["o"]), "h": np.full(n, 0.3),
           "delta": np.zeros(n), "xtb": np.linspace(-14.0, -6.0, n), "xtb_overlap": np.full(n, 0.9),
           **{k: np.array(ROUTES[k], bool) for k in ("large_amplitude", "no_xtb", "vpt2_marked")}}
    if marked_instead is not None:
        rec["vpt2_marked"] = np.arange(n) == marked_instead
    return rec


def test_every_route_a_mode_can_take(artefact: A.Artefact, monkeypatch: pytest.MonkeyPatch):
    """Below both windows, a family without a model in its window, the three label-free refusals in their order (mode 2 is
    large-amplitude and marked: the first reason asked is the one given), and a step with its family's bar."""
    monkeypatch.setattr(A, "describe", lambda modes, xtb: _synthetic_rec())
    steps = A.mode_steps(A.Modes((), np.zeros((0, 3)), np.array(ROUTES["omega"]), np.zeros((0, 9))), None, artefact)
    assert [s.reason for s in steps] == EXPECTED
    assert [s.bar_cm for s in steps] == [None, 3.37, None, None, 3.84, 3.84, None, 6.21, None]
    assert [s.window for s in steps] == [None, "mid", None, None, "mid", "mid", None, "ch", None]
    assert all((s.delta_anh_cm is None) == (s.reason is not None) for s in steps)
    assert all(np.isfinite(s.delta_anh_cm) for s in steps if s.reason is None)
    # family 'other' at o 0.85 keeps its step and loses the bar's claim; at 0.79 it does not; a refused mode never carries the flag
    assert [s.error_not_measured for s in steps] == [False, False, False, False, True, False, False, False, False]


def test_a_marked_xtb_partner_alone_refuses_the_step(artefact: A.Artefact, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(A, "describe", lambda modes, xtb: _synthetic_rec(marked_instead=1))
    steps = A.mode_steps(A.Modes((), np.zeros((0, 3)), np.array(ROUTES["omega"]), np.zeros((0, 9))), None, artefact)
    assert steps[1].reason == A.XTB_PARTNER_MARKED and steps[1].delta_anh_cm is None and steps[1].bar_cm is None
    assert steps[4].reason is None


def test_a_step_is_the_reads_own_prediction(artefact: A.Artefact, monkeypatch: pytest.MonkeyPatch):
    """The shift of a stepped mode is s3_read's x2* on the window table, whatever other modes the molecule has."""
    rec = _synthetic_rec()
    monkeypatch.setattr(A, "describe", lambda modes, xtb: rec)
    steps = A.mode_steps(A.Modes((), np.zeros((0, 3)), rec["omega"], np.zeros((0, 9))), None, artefact)
    mid = artefact.windows[0]
    one = {k: rec[k][[4]] for k in A.TABLE_KEYS}
    assert steps[4].delta_anh_cm == pytest.approx(float(S3.predictors(mid.families["other"].config)["x2*"](mid.table, one)[0]), abs=1e-9)


def _step(i: int, delta: float | None, reason: str | None = None, flag: bool = False) -> A.ModeStep:
    return A.ModeStep(i, 1000.0 + i, "ring-ip", 0.1, 0.0, 0.9, delta, reason, None if delta is None else 3.37, flag, "mid")


def test_steps_are_carried_by_overlap_not_by_rank():
    """Four B3LYP modes; the corrected bands are the same shapes in another order, and one band that is no mode's own."""
    q = np.eye(6)[:, :4]
    steps = [_step(0, -10.0), _step(1, -20.0, flag=True), _step(2, None, A.NO_XTB_PARTNER), _step(3, -40.0)]
    mixed = (q[:, 2] + q[:, 3] + np.eye(6)[:, 4]) / np.sqrt(3.0)              # a third of each: under the line
    bands = A.carry_to_bands(np.stack([q[:, 1], q[:, 0], mixed], axis=1), q, steps)
    assert [b.mode for b in bands] == [1, 0, None]                             # rank would have given 0, 1, 2
    assert [b.delta_anh_cm for b in bands] == [-20.0, -10.0, None]
    assert bands[0].error_not_measured and bands[0].bar_cm == 3.37 and not bands[1].error_not_measured
    assert bands[2].reason == A.MIXED_BAND and bands[2].overlap == pytest.approx(1 / 3) and bands[2].bar_cm is None
    refused = A.carry_to_bands(q[:, [2]], q, steps)[0]                        # the partner's own refusal comes along
    assert (refused.mode, refused.reason, refused.delta_anh_cm) == (2, A.NO_XTB_PARTNER, None)


def test_the_carry_refuses_inputs_that_do_not_belong_together():
    q = np.eye(6)[:, :4]
    with pytest.raises(ValueError, match="3 steps for 4"):
        A.carry_to_bands(q, q, [_step(i, -1.0) for i in range(3)])
    with pytest.raises(ValueError, match="do not match"):                     # more bands than B3LYP modes
        A.carry_to_bands(np.eye(6)[:, :5], q, [_step(i, -1.0) for i in range(4)])


def test_match_modes_keeps_its_answer_on_square_input_and_takes_fewer_bands():
    rng = np.random.default_rng(3)
    q = np.linalg.qr(rng.normal(size=(9, 9)))[0][:, :5]
    partner, overlap = X.match_modes(q[:, [2, 0, 1, 4, 3]], q)
    assert partner.tolist() == [2, 0, 1, 4, 3] and np.allclose(overlap, 1.0)
    partner, overlap = X.match_modes(q[:, [4, 1]], q)
    assert partner.tolist() == [4, 1] and np.allclose(overlap, 1.0)


def test_the_committed_artefact_holds_the_registered_bars():
    """The artefact in git: the four registered bars, each reproduced by its own refit to the registration's 0.01 cm⁻¹."""
    art = A.load_artefact()
    assert A.bars(art) == {"CH-oop": 8.38, "other": 3.84, "ring-ip": 3.37, "CH-stretch": 6.21}
    assert all(abs(m.bar_refit_cm - m.bar_cm) <= 0.01 for w in art.windows for m in w.families.values())
    assert len(art.header["training_molecules"]) == 37 and art.header["commit"]


def _data(*parts: str) -> Path:
    path = DATA.joinpath(*parts)
    if not path.exists():
        pytest.skip(f"force fields not on this machine: {path}")
    return path


@pytest.mark.data
def test_a_training_molecule_gets_exactly_the_training_paths_shift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Two training molecules from their stored files: through `mode_steps`, and through the registered read's own loader
    (`s3_read.load_scope` on a sets file cut down to the two) and predictor. The same shift to 1e-9 cm⁻¹ on every mode the read
    scores, and the read scores no mode the step refuses."""
    _data("probes", "results_m1", "s2_xtb_2026-10-18", "xtb", TRAINING_PAIR[0], "X", "qff_report.npz")
    monkeypatch.chdir(DATA)
    sets = json.loads(Path(SETS).read_text(encoding="utf-8"))
    for s in sets:
        selected = json.loads(Path(s["selection"]).read_text(encoding="utf-8"))["selected"]
        cut = tmp_path / f"{s['name']}_selection.json"
        cut.write_text(json.dumps({"selected": [m for m in selected if m["id"] in TRAINING_PAIR]}), encoding="utf-8")
        s["selection"] = str(cut)
        s["extra"] = {i: d for i, d in s["extra"].items() if i in TRAINING_PAIR}
    cut_sets = tmp_path / "sets.json"
    cut_sets.write_text(json.dumps(sets), encoding="utf-8")
    art, compared = A.load_artefact(), 0
    for w in art.windows:
        by_scaf, *_ = S3.load_scope(str(cut_sets), art.header["window_sources"][w.name]["marked_policy"], w.bounds)
        mols = [m for ms in by_scaf.values() for m in ms]
        assert sorted(m["id"] for m in mols) == sorted(TRAINING_PAIR)
        for m in mols:
            x_dir = next(str(Path(s["xtb_root"]) / m["id"] / "X") for s in sets if (Path(s["xtb_root"]) / m["id"]).is_dir())
            x_label = next(str(Path(s["xtb_gvpt2_dir"]) / f"{m['id']}.json") for s in sets if (Path(s["xtb_root"]) / m["id"]).is_dir())
            steps = A.mode_steps(A.Modes.from_ref(os.path.join(m["dir"], "ref.json")), A.XtbField.from_folder(x_dir, x_label), art)
            mine = {s.omega_cm: s for s in steps}
            test = concat([m], w.bounds)
            for fa, model in w.families.items():
                sel = test["family"] == fa
                reference = S3.predictors(model.config)["x2*"](w.table, test)[sel]
                for omega, ref in zip(test["omega"][sel], reference, strict=True):
                    assert mine[float(omega)].delta_anh_cm == pytest.approx(float(ref), abs=1e-9)
                    assert mine[float(omega)].family == fa and mine[float(omega)].bar_cm == model.bar_cm
                    compared += 1
    assert compared > 60


@pytest.mark.data
def test_on_a_stored_molecule_rank_and_overlap_disagree_and_the_carry_follows_overlap():
    """B_78f8233b4c's B3LYP and ωB97X analytic Hessians (the corrected modes of a perfect ΔH): several bands' partners are not the
    B3LYP mode of the same rank, each carried step is its partner's, and a band under the overlap line gets none."""
    folder = _data("modules", "05_support_predictor", "corpus", "molecules", RANK_MOLECULE)
    geometry = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    modes = {}
    for key, name in (("B", "hessian_b3lyp_analytic.npz"), ("W", "hessian_wb97x_analytic.npz")):
        with np.load(_data("modules", "05_support_predictor", "corpus", "molecules", RANK_MOLECULE, name)) as z:
            modes[key] = A.Modes.from_hessian(z["H_projected"], geometry["symbols"], np.asarray(geometry["coords_bohr"], float))
    n = len(modes["B"].omega)
    steps = [_step(i, -float(i)) for i in range(n)]                            # each mode's step names the mode
    bands = A.carry_to_bands(modes["W"].q, modes["B"].q, steps)
    moved = [j for j, b in enumerate(bands) if b.mode is not None and b.mode != j]
    assert len(moved) >= 5
    assert all(b.delta_anh_cm == -float(b.mode) for b in bands if b.mode is not None)
    assert all(b.overlap >= X.MIN_OVERLAP for b in bands if b.mode is not None)
    lost = [b for b in bands if b.mode is None]
    assert lost and all(b.reason == A.MIXED_BAND and b.overlap < X.MIN_OVERLAP for b in lost)
    assert len({b.mode for b in bands if b.mode is not None}) == n - len(lost)   # one B3LYP mode per band
