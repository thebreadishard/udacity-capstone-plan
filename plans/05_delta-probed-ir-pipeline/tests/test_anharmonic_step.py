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
    return {"config": config, "bar_cm": bar, "bar_one_to_one_cm": bar, "bar_refit_cm": bar,
            "n_training_modes": table["family"].count(family), "n_training_modes_one_to_one": table["family"].count(family),
            "n_target_rows": 9, "per_target_rms_cm": {"t1": bar - 1.0, "t2": bar + 1.0}}


def _probes(name: str, window: dict, per_family: int = 4) -> list[dict]:
    """Probe rows as the fit writes them: training rows of each modelled family with the shift the read's model gives them."""
    table = {k: np.asarray(window["table"][k], str if k == "family" else float) for k in A.TABLE_KEYS}
    rows = []
    for fa, model in window["families"].items():
        at = np.flatnonzero(table["family"] == fa)[:per_family]
        test = {k: table[k][at] for k in A.TABLE_KEYS}
        shift = S3.predictors(model["config"])["x2*"](table, test)
        rows += [{"window": name, **{k: test[k][j].item() for k in A.TABLE_KEYS}, "shift_cm": float(shift[j])} for j in range(len(at))]
    return rows


def _record() -> dict:
    """A small artefact of two windows: 'mid' with ring-ip and other, 'ch' with the CH stretches."""
    mid, ch = _table(["ring-ip", "other"], 40, 560.0, 1990.0, 1), _table(["CH-stretch"], 12, 3000.0, 3200.0, 2)
    src = {"marked_policy": "exclude", "route_rule": "rule.json", "s2b_read": "s2b.json", "s3_read": "s3.json"}
    windows = {"mid": {**src, "window": [550.0, 2000.0], "table": mid,
                       "families": {"ring-ip": _family(CONFIG, mid, "ring-ip", 3.37), "other": _family(CONFIG, mid, "other", 3.84)}},
               "ch": {**src, "window": [2800.0, None], "table": ch, "families": {"CH-stretch": _family(CONFIG, ch, "CH-stretch", 6.21)}}}
    return {"format": A.FORMAT, "model": A.MODEL, "commit": "abc", "registration": "reg.md", "decisions": "report.md",
            "scope": "no-large-amplitude", "training_molecules": ["m1", "m2", "m3"],
            "molecules": {"m1": "c1ccccc1", "m2": "c1ccncc1", "m3": "c1ccc2ccccc2c1"}, "targets": {"t1": "c1ccc2cc3ccccc3cc2c1"},
            "elements": ["C", "H", "N"], "compositions": {"C,H": 2, "C,H,N": 1}, "target_composition": {"t1": "C,H"},
            "probes": [row for name, w in windows.items() for row in _probes(name, w)], "windows": windows}


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
    r["format"] = A.FORMAT + 1


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


def _other_shift(r: dict) -> None:
    r["probes"][3]["shift_cm"] += 0.01


def _other_feature(r: dict) -> None:
    r["windows"]["mid"]["table"]["h"][0] += 0.2          # a training row that is not the fit's: every 'mid' probe moves


def _few_probes(r: dict) -> None:
    del r["probes"][2:]


def _family_without_probe(r: dict) -> None:
    r["probes"] = [p for p in r["probes"] if p["family"] != "other"]


def _no_elements(r: dict) -> None:
    del r["elements"]


@pytest.mark.parametrize(("spoil", "match"), [
    (_other_format, "this code reads format"), (_no_commit, "cannot be traced"), (_no_read, "cannot be traced"),
    (_no_molecules, "cannot be traced"), (_short_column, "differ in length"), (_unknown_config, "not one of the read's"),
    (_wrong_count, "the record says"), (_family_twice, "the record says|two windows"),
    # review finding 3: the probe rows are the equivalence with the fit that needs no force field, checked at every load
    (_other_shift, "this code or its libraries are not the fit's"), (_other_feature, "not the fit's"),
    (_few_probes, "at least 10, over every modelled family"), (_family_without_probe, "over every modelled family"),
    (_no_elements, "cannot be traced")])
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
    record["probes"] = [row for name, w in record["windows"].items() for row in _probes(name, w)]
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
    # review finding 7: the flagged mode 4 has a step and no bar — the family's 3.84 was not measured for its kind of mode
    assert [s.bar_cm for s in steps] == [None, 3.37, None, None, None, 3.84, None, 6.21, None]
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
    return A.ModeStep(i, 1000.0 + i, "ring-ip", 0.1, 0.0, 0.9, delta, reason, None if delta is None or flag else 3.37, flag, "mid")


APART = 1500.0 + 10.0 * np.arange(8)          # band positions 10 cm⁻¹ apart: no band has a near-degenerate neighbour


def test_a_step_is_withheld_where_a_second_family_rule_disagrees():
    """Review finding 8: two implementations of the family rule; a mode they name differently gets no step, with the reason."""
    steps = [_step(0, -10.0), _step(1, -20.0, flag=True), _step(2, None, A.NO_XTB_PARTNER)]
    assert A.agree_on_family(steps, ["ring-ip"] * 3) == steps
    out = A.agree_on_family(steps, ["ring-ip", "other", "CH-oop"])
    assert out[0] == steps[0] and out[2] == steps[2]                        # a mode without a step keeps its own reason
    assert (out[1].delta_anh_cm, out[1].reason, out[1].bar_cm, out[1].error_not_measured) == (None, A.FAMILY_MISMATCH, None, False)
    with pytest.raises(ValueError, match="2 families for 3 steps"):
        A.agree_on_family(steps, ["ring-ip"] * 2)


def test_the_artefact_says_what_its_table_holds(artefact: A.Artefact):
    """Review findings 5 and 6: the training molecules by SMILES, the targets, the elements and how many molecules of each composition."""
    assert A.elements(artefact) == frozenset({"C", "H", "N"})
    assert A.seen(artefact, "c1ccncc1") == {"role": "training", "id": "m2"} and A.seen(artefact, "c1ccc2cc3ccccc3cc2c1")["role"] == "target"
    assert A.seen(artefact, "c1ccoc1") == {"role": "unseen", "id": None} and A.seen(artefact, None) == {"role": "unknown", "id": None}
    assert A.composition(artefact, ["C", "H", "H", "N"]) == {"elements": "C,H,N", "training_molecules": 1, "of": 3, "few": True,
                                                             "targets": {"t1": "C,H"}}
    assert A.composition(artefact, ["C", "O"])["training_molecules"] == 0


def test_steps_are_carried_by_overlap_not_by_rank():
    """Four B3LYP modes; the corrected bands are the same shapes in another order, and one band that is no mode's own."""
    q = np.eye(6)[:, :4]
    steps = [_step(0, -10.0), _step(1, -20.0, flag=True), _step(2, None, A.NO_XTB_PARTNER), _step(3, -40.0)]
    mixed = (q[:, 2] + q[:, 3] + np.eye(6)[:, 4]) / np.sqrt(3.0)              # a third of each: under the line
    bands = A.carry_to_bands(APART[:3], np.stack([q[:, 1], q[:, 0], mixed], axis=1), q, steps)
    assert [b.mode for b in bands] == [1, 0, None]                             # rank would have given 0, 1, 2
    assert [b.delta_anh_cm for b in bands] == [-20.0, -10.0, None]
    assert bands[0].error_not_measured and bands[0].bar_cm is None and bands[1].bar_cm == 3.37 and not bands[1].error_not_measured
    assert bands[2].reason == A.MIXED_BAND and bands[2].overlap == pytest.approx(1 / 3) and bands[2].bar_cm is None
    assert not any(b.set_wise for b in bands)
    refused = A.carry_to_bands(APART[:1], q[:, [2]], q, steps)[0]             # the partner's own refusal comes along
    assert (refused.mode, refused.reason, refused.delta_anh_cm) == (2, A.NO_XTB_PARTNER, None)


def test_the_carry_refuses_inputs_that_do_not_belong_together():
    q = np.eye(6)[:, :4]
    with pytest.raises(ValueError, match="3 steps for 4"):
        A.carry_to_bands(APART[:4], q, q, [_step(i, -1.0) for i in range(3)])
    with pytest.raises(ValueError, match="do not match"):                     # more bands than B3LYP modes
        A.carry_to_bands(APART[:5], np.eye(6)[:, :5], q, [_step(i, -1.0) for i in range(4)])
    with pytest.raises(ValueError, match="frequencies for modes"):            # positions that are not the bands'
        A.carry_to_bands(APART[:3], q, q, [_step(i, -1.0) for i in range(4)])


def test_match_modes_keeps_its_answer_on_square_input_and_takes_fewer_bands():
    rng = np.random.default_rng(3)
    q = np.linalg.qr(rng.normal(size=(9, 9)))[0][:, :5]
    partner, overlap = X.match_modes(q[:, [2, 0, 1, 4, 3]], q)
    assert partner.tolist() == [2, 0, 1, 4, 3] and np.allclose(overlap, 1.0)
    partner, overlap = X.match_modes(q[:, [4, 1]], q)
    assert partner.tolist() == [4, 1] and np.allclose(overlap, 1.0)


def test_the_committed_artefact_holds_the_registered_bars():
    """The artefact in git: the four registered bars, each reproduced under the registered match to the registration's
    0.01 cm⁻¹; the table it holds is matched set-wise (TASKS 255), three rows larger, its own bars within 0.05 of the registered."""
    art = A.load_artefact()
    models = {fa: m for w in art.windows for fa, m in w.families.items()}
    assert A.bars(art) == {"CH-oop": 8.38, "other": 3.84, "ring-ip": 3.37, "CH-stretch": 6.21}
    assert all(abs(m.bar_one_to_one_cm - m.bar_cm) <= 0.01 and abs(m.bar_refit_cm - m.bar_cm) <= 0.05 for m in models.values())
    assert {fa: round(m.bar_refit_cm, 3) for fa, m in models.items()} == {"CH-oop": 8.381, "other": 3.838, "ring-ip": 3.371, "CH-stretch": 6.199}
    assert {fa: m.n_training_modes - m.n_training_modes_one_to_one for fa, m in models.items()} == {"CH-oop": 0, "other": 1, "ring-ip": 1,
                                                                                                   "CH-stretch": 1}
    assert art.header["match"] == {"rule": "sets", "set_tolerance_cm": 1.0, "mark_share": 0.05, "registered_rule": "single",
                                   "change_limit_cm": 0.05}
    assert len(art.header["training_molecules"]) == 37 and art.header["commit"]
    assert sorted(A.elements(art)) == ["C", "H", "N", "O"]
    assert art.header["compositions"] == {"C,H": 14, "C,H,N": 18, "C,H,N,O": 2, "C,H,O": 3}
    assert art.header["target_composition"] == {"coronene": "C,H", "tetracene": "C,H"} and len(art.header["probes"]) == 12
    assert A.seen(art, "c1ccccc1") == {"role": "training", "id": "A_8448043181"} and A.composition(art, ["C", "H", "O"])["few"] is True
    assert {fa: m.n_target_rows for w in art.windows for fa, m in w.families.items()} == {"CH-oop": 22, "other": 23, "ring-ip": 56,
                                                                                         "CH-stretch": 20}
    assert all(m.per_target_rms_cm["coronene"] > m.per_target_rms_cm["tetracene"] for w in art.windows for m in w.families.values())


def test_the_pipelines_modes_are_the_training_paths_modes():
    """Review finding 3: the pipeline builds its B3LYP modes with `Modes.from_hessian`, the training with `Modes.from_ref`. On a
    reference record that git holds (route A's gate benzene) the two give the same modes, and so the same steps."""
    ref = PLAN / "probes" / "results_m1" / "routea_2026-11-02" / "gate" / "benzene" / "G" / "ref.json"
    stored = json.loads(ref.read_text(encoding="utf-8"))
    n = len(stored["molecule"]["symbols"])
    a = A.Modes.from_ref(str(ref))
    b = A.Modes.from_hessian(np.array(stored["return_result"], float).reshape(3 * n, 3 * n), stored["molecule"]["symbols"],
                             np.array(stored["molecule"]["geometry"], float))
    assert np.array_equal(a.omega, b.omega) and np.array_equal(a.q, b.q) and a.symbols == b.symbols
    art = A.load_artefact()
    field = A.XtbField(-0.01 * a.omega, np.zeros(len(a.omega), bool), a.q)
    assert A.mode_steps(a, field, art) == A.mode_steps(b, field, art)


def test_the_superseded_artefact_is_refused_with_its_reason():
    """Format 2 in git (the table of the one-to-one match) names why it is not read any more; an unknown format is refused too."""
    with pytest.raises(ValueError, match=r"format 2 is superseded .* one-to-one match .* refit with probes/anharmonic_step_fit\.py"):
        A.load_artefact(str(PLAN / "probes" / "anharmonic_step" / "x2star_v2.json"))
    assert A.FORMAT == 3 and A.ARTEFACT.endswith("x2star_v3.json")


def test_the_table_holds_every_row_of_the_one_to_one_table_unchanged_and_three_more():
    """Against master's output on the stored molecules: format 2 in git is the table master's one-to-one match built. Every
    one of its rows is in the new table in the same order with the same six numbers, to the bit; the new table has three rows
    between them and no other difference."""
    old = json.loads((PLAN / "probes" / "anharmonic_step" / "x2star_v2.json").read_text(encoding="utf-8"))["windows"]
    new = json.loads(Path(A.ARTEFACT).read_text(encoding="utf-8"))["windows"]
    added = {}
    for name, w in old.items():
        before = list(zip(*(w["table"][k] for k in A.TABLE_KEYS), strict=True))
        after = list(zip(*(new[name]["table"][k] for k in A.TABLE_KEYS), strict=True))
        rest = iter(after)
        assert all(row in rest for row in before)                             # every old row, in order, exactly
        extra = list(after)
        for row in before:
            extra.remove(row)
        added[name] = [(row[2], round(row[0], 2)) for row in extra]
    assert added == {"mid": [("ring-ip", 1276.74), ("other", 580.28)], "ch": [("CH-stretch", 3183.24)]}


def _symmetric_benzene() -> A.Modes:
    """Route A's gate benzene (in git) with its geometry and Hessian averaged over the sixfold axis, so that its degenerate
    pairs are degenerate to round-off and every vector of a pair's plane has the same hydrogen and out-of-plane share."""
    stored = json.loads((PLAN / "probes" / "results_m1" / "routea_2026-11-02" / "gate" / "benzene" / "G" / "ref.json").read_text(encoding="utf-8"))
    symbols = stored["molecule"]["symbols"]
    n = len(symbols)
    x = np.array(stored["molecule"]["geometry"], float).reshape(n, 3)
    x = x - x.mean(axis=0)
    axis = np.linalg.svd(x)[2][2]
    k = np.array([[0.0, -axis[2], axis[1]], [axis[2], 0.0, -axis[0]], [-axis[1], axis[0], 0.0]])
    turn = np.eye(3) + np.sin(np.pi / 3) * k + (1.0 - np.cos(np.pi / 3)) * (k @ k)
    op = np.zeros((3 * n, 3 * n))
    for i in range(n):
        j = int(np.argmin(np.linalg.norm(x - turn @ x[i], axis=1)))
        assert symbols[j] == symbols[i] and np.linalg.norm(x[j] - turn @ x[i]) < 0.05
        op[3 * j:3 * j + 3, 3 * i:3 * i + 3] = turn
    powers = [np.linalg.matrix_power(op, p) for p in range(6)]
    hessian = np.array(stored["return_result"], float).reshape(3 * n, 3 * n)
    hessian = 0.5 * (hessian + hessian.T)                  # the solver reads one triangle: the average must be symmetric itself
    return A.Modes.from_hessian(sum(p @ hessian @ p.T for p in powers) / 6.0, symbols,
                                (sum(p @ x.reshape(-1) for p in powers) / 6.0).reshape(n, 3))


def _leaning_field(modes: A.Modes, pair: tuple[int, int], share: float = 0.985) -> A.XtbField:
    """A force field with the molecule's own modes, one shift per degenerate level, the plane of one pair leaning out of the
    B3LYP pair's plane into the rotations and translations (every other overlap 1 or 0)."""
    spare = np.linalg.svd(modes.q)[0][:, modes.q.shape[1]:]
    q = modes.q.copy()
    for k, s in zip(pair, (0, 1), strict=True):
        q[:, k] = np.sqrt(share) * modes.q[:, k] + np.sqrt(1.0 - share) * spare[:, s]
    return A.XtbField(-0.01 * np.round(modes.omega), np.zeros(len(modes.omega), bool), q)


def _turned(q: np.ndarray, pair: tuple[int, int], angle: float) -> np.ndarray:
    out, (a, b) = q.copy(), pair
    out[:, a], out[:, b] = np.cos(angle) * q[:, a] + np.sin(angle) * q[:, b], -np.sin(angle) * q[:, a] + np.cos(angle) * q[:, b]
    return out


def _ring_pair(modes: A.Modes) -> tuple[int, int]:
    """Benzene's degenerate ring stretch near 1650 cm⁻¹: the pair the first real run lost."""
    a = int(np.argmin(np.abs(modes.omega - 1655.0)))
    b = a + 1 if a + 1 < len(modes.omega) and abs(modes.omega[a + 1] - modes.omega[a]) < 1e-6 else a - 1
    assert abs(modes.omega[a] - modes.omega[b]) < 1e-6
    return (min(a, b), max(a, b))


def test_a_pair_in_a_basis_45_degrees_from_the_fields_gets_its_step(artefact: A.Artefact):
    """The first real run's case (17 Nov 2026) on a symmetric benzene: the field's pair turned by 45°, one-to-one 0.4925 and
    0.4925. Both modes are stepped, with the step they get in the basis where the one-to-one match holds."""
    modes = _symmetric_benzene()
    pair = _ring_pair(modes)
    field = _leaning_field(modes, pair)
    aligned = A.mode_steps(modes, field, artefact)
    turned = A.mode_steps(modes, A.XtbField(field.delta, field.marked, _turned(field.q, pair, np.pi / 4)), artefact)
    assert X.match_modes(modes.q, _turned(field.q, pair, np.pi / 4))[1][list(pair)] == pytest.approx([0.4925, 0.4925], abs=1e-9)
    for k in pair:
        assert aligned[k].reason is None and turned[k].reason is None and turned[k].family == "ring-ip" and turned[k].bar_cm == 3.37
        assert turned[k].delta_anh_cm == pytest.approx(aligned[k].delta_anh_cm, abs=1e-9)
        assert turned[k].xtb_overlap == pytest.approx(0.985, abs=1e-9) and aligned[k].xtb_overlap == pytest.approx(0.985, abs=1e-9)
    assert [s.reason for s in turned] == [s.reason for s in aligned]
    assert all(abs(s.delta_anh_cm - t.delta_anh_cm) <= 1e-9 for s, t in zip(turned, aligned, strict=True) if s.reason is None)


def test_the_models_inputs_of_a_degenerate_pair_do_not_depend_on_either_basis(artefact: A.Artefact):
    """100 draws: the B3LYP pair and the field's pair turned by random angles. Family, ω, h, o and the xtb shift of every mode —
    the model's inputs — and the refusals are those of the unturned case to 1e-9; so are the steps, read on five of the draws."""
    modes = _symmetric_benzene()
    pair = _ring_pair(modes)
    field = _leaning_field(modes, pair, share=0.7)          # a quarter of the bases fall under the one-to-one line
    reference, steps = A.describe(modes, field), A.mode_steps(modes, field, artefact)
    rng, as_a_set = np.random.default_rng(21), 0
    for draw in range(100):
        a, b = rng.uniform(0.0, 2.0 * np.pi, 2)
        turned = A.Modes(modes.symbols, modes.coords_bohr, modes.omega, _turned(modes.q, pair, a))
        turned_field = A.XtbField(field.delta, field.marked, _turned(field.q, pair, b))
        rec = A.describe(turned, turned_field)
        assert all(np.abs(rec[k] - reference[k]).max() <= 1e-9 for k in ("omega", "h", "o", "xtb"))
        assert all(np.array_equal(rec[k], reference[k]) for k in ("family", "no_xtb", "large_amplitude", "vpt2_marked"))
        as_a_set += int(rec["xtb_set_wise"][list(pair)].all())
        if draw < 5:
            got = A.mode_steps(turned, turned_field, artefact)
            assert [s.reason for s in got] == [s.reason for s in steps]
            assert all(abs(s.delta_anh_cm - t.delta_anh_cm) <= 1e-9 for s, t in zip(got, steps, strict=True) if s.reason is None)
    assert 10 < as_a_set < 50


def test_a_band_that_lies_in_a_degenerate_pairs_plane_takes_the_pairs_step():
    """Corrected bands 0 and 1 are a degenerate pair turned 45° against B3LYP modes 0 and 1 and leaning a little out of their
    plane: one-to-one 0.49 each. As a set each band takes the pair's step; with a member that has no step, neither has one."""
    q = np.eye(8)[:, :4]
    lean = np.sqrt(0.98) * q[:, :2] + np.sqrt(0.02) * np.eye(8)[:, 4:6]
    bands_q = np.stack([(lean[:, 0] + lean[:, 1]) / np.sqrt(2.0), (lean[:, 0] - lean[:, 1]) / np.sqrt(2.0), q[:, 2], q[:, 3]], axis=1)
    omega = np.array([1500.0, 1500.02, 1600.0, 1700.0])
    steps = [_step(0, -10.0), _step(1, -10.0), _step(2, -30.0), _step(3, -40.0)]
    bands = A.carry_to_bands(omega, bands_q, q, steps)
    assert [b.set_wise for b in bands] == [True, True, False, False] and [b.delta_anh_cm for b in bands[2:]] == [-30.0, -40.0]
    assert all(b.delta_anh_cm == pytest.approx(-10.0, abs=1e-12) and b.overlap == pytest.approx(0.98) and b.bar_cm == 3.37 for b in bands[:2])
    assert sorted(b.mode for b in bands[:2]) == [0, 1] and all(b.reason is None and not b.error_not_measured for b in bands[:2])
    apart = A.carry_to_bands(np.array([1500.0, 1510.0, 1600.0, 1700.0]), bands_q, q, steps)      # not a set: 10 cm⁻¹ apart
    assert [b.reason for b in apart[:2]] == [A.MIXED_BAND, A.MIXED_BAND] and apart[0].overlap == pytest.approx(0.49)
    steps[1] = _step(1, None, A.NO_XTB_PARTNER)
    lost = A.carry_to_bands(omega, bands_q, q, steps)
    assert all(b.delta_anh_cm is None and b.reason == A.NO_XTB_PARTNER and b.bar_cm is None and b.set_wise for b in lost[:2])
    steps[1] = _step(1, -12.0, flag=True)
    flagged = A.carry_to_bands(omega, bands_q, q, steps)
    assert all(b.delta_anh_cm == pytest.approx(-11.0, abs=1e-12) and b.bar_cm is None and b.error_not_measured for b in flagged[:2])


def _data(*parts: str) -> Path:
    path = DATA.joinpath(*parts)
    if not path.exists():
        pytest.skip(f"force fields not on this machine: {path}")
    return path


def _cut_sets(tmp_path: Path, ids: tuple[str, ...]) -> tuple[list[dict], Path]:
    """The registered sets file cut down to a few molecules (run from DATA): the sets, and the file that holds them."""
    sets = json.loads(Path(SETS).read_text(encoding="utf-8"))
    for s in sets:
        selected = json.loads(Path(s["selection"]).read_text(encoding="utf-8"))["selected"]
        cut = tmp_path / f"{s['name']}_selection.json"
        cut.write_text(json.dumps({"selected": [m for m in selected if m["id"] in ids]}), encoding="utf-8")
        s["selection"] = str(cut)
        s["extra"] = {i: d for i, d in s["extra"].items() if i in ids}
    path = tmp_path / "sets.json"
    path.write_text(json.dumps(sets), encoding="utf-8")
    return sets, path


@pytest.mark.data
def test_a_training_molecule_gets_exactly_the_training_paths_shift(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Two training molecules from their stored files: through `mode_steps`, and through the registered read's own loader
    (`s3_read.load_scope` on a sets file cut down to the two) and predictor. The same shift to 1e-9 cm⁻¹ on every mode the read
    scores, and the read scores no mode the step refuses."""
    _data("probes", "results_m1", "s2_xtb_2026-10-18", "xtb", TRAINING_PAIR[0], "X", "qff_report.npz")
    monkeypatch.chdir(DATA)
    sets, cut_sets = _cut_sets(tmp_path, TRAINING_PAIR)
    art, compared = A.load_artefact(), 0
    for w in art.windows:
        by_scaf, *_ = S3.load_scope(str(cut_sets), art.header["window_sources"][w.name]["marked_policy"], w.bounds)
        mols = [m for ms in by_scaf.values() for m in ms]
        assert sorted(m["id"] for m in mols) == sorted(TRAINING_PAIR)
        for m in mols:
            x_dir = next(str(Path(s["xtb_root"]) / m["id"] / "X") for s in sets if (Path(s["xtb_root"]) / m["id"]).is_dir())
            x_label = next(str(Path(s["xtb_gvpt2_dir"]) / f"{m['id']}.json") for s in sets if (Path(s["xtb_root"]) / m["id"]).is_dir())
            field = A.XtbField.from_folder(x_dir, x_label)
            steps = A.mode_steps(A.Modes.from_ref(os.path.join(m["dir"], "ref.json")), field, art)
            ref = json.loads(Path(m["dir"], "ref.json").read_text(encoding="utf-8"))          # and as the pipeline builds its modes
            n = len(ref["molecule"]["symbols"])
            assert steps == A.mode_steps(A.Modes.from_hessian(np.array(ref["return_result"], float).reshape(3 * n, 3 * n),
                                                              ref["molecule"]["symbols"], np.array(ref["molecule"]["geometry"], float)),
                                         field, art)
            mine = {s.omega_cm: s for s in steps}
            test = concat([m], w.bounds)
            for fa, model in w.families.items():
                sel = test["family"] == fa
                reference = S3.predictors(model.config)["x2*"](w.table, test)[sel]
                for omega, ref in zip(test["omega"][sel], reference, strict=True):
                    assert mine[float(omega)].delta_anh_cm == pytest.approx(float(ref), abs=1e-9)
                    step = mine[float(omega)]
                    assert step.family == fa and step.bar_cm == (None if step.error_not_measured else model.bar_cm)
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
    bands = A.carry_to_bands(modes["W"].omega, modes["W"].q, modes["B"].q, steps)
    moved = [j for j, b in enumerate(bands) if b.mode is not None and b.mode != j]
    assert len(moved) >= 5
    assert all(b.delta_anh_cm == -float(b.mode) for b in bands if b.mode is not None)
    assert all(b.overlap >= X.MIN_OVERLAP for b in bands if b.mode is not None)
    lost = [b for b in bands if b.mode is None]
    assert lost and all(b.reason == A.MIXED_BAND and b.overlap < X.MIN_OVERLAP for b in lost)
    assert len({b.mode for b in bands if b.mode is not None}) == n - len(lost)   # one B3LYP mode per band


SET_MOLECULES = ("P3_ff62f88395", "A_8448043181")          # one whose CH stretch at 3183.24 is matched as a set, and benzene


@pytest.mark.data
def test_the_match_rule_reaches_the_reads_loader_and_adds_one_row_there(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """`s3_read.load_scope` under both rules on two stored molecules: 'single' is the registered read's table; 'sets' holds the
    same rows with the same numbers and one more, the CH stretch the one-to-one match refused at 0.466 (0.934 as a set)."""
    _data("probes", "results_m1", "s2b_xtb_2026-11-02", "xtb", SET_MOLECULES[0], "X", "qff_report.npz")
    monkeypatch.chdir(DATA)
    _, cut_sets = _cut_sets(tmp_path, SET_MOLECULES)
    window = (2800.0, np.inf)
    tables = {}
    for rule in X.MATCH_RULES:
        by_scaf, counts, *_ = S3.load_scope(str(cut_sets), "exclude", window, rule)
        assert counts["match_rule"] == rule and counts["window_modes_matched_as_a_set"] == (1 if rule == "sets" else 0)
        table = concat([m for ms in by_scaf.values() for m in ms], window)
        tables[rule] = sorted(zip(*(table[k].tolist() for k in A.TABLE_KEYS), strict=True))
    extra = [row for row in tables["sets"] if row not in tables["single"]]
    assert all(row in tables["sets"] for row in tables["single"]) and len(tables["sets"]) == len(tables["single"]) + 1
    assert [(round(row[0], 2), row[2], round(row[5], 2)) for row in extra] == [(3183.24, "CH-stretch", -152.25)]
    with pytest.raises(ValueError, match="match rule 'pairs'"):
        S3.load_scope(str(cut_sets), "exclude", window, "pairs")


def _read(rms: float, n: int, modes: int) -> dict:
    return {"read": {"families": {"CH-stretch": {"rms": {"x2*": rms}, "n": n, "per_molecule": {"t1": {"x2*": rms}}}}},
            "size": {"per_family": {"CH-stretch": modes}}}


def test_the_fit_holds_the_registered_read_to_its_bar_and_the_set_wise_table_to_a_limit():
    """`anharmonic_step_fit.family_record`: the registered match must reproduce the registered bar to 0.01; the table that is
    saved may move the bar by 0.05 at most and must score the same target rows; the record keeps all three numbers."""
    import anharmonic_step_fit as F

    printed = {"model": "x2*", "bar_cm": 6.2143}
    rec = F.family_record("ch/CH-stretch", printed, "cfg", _read(6.2143, 20, 288), _read(6.1994, 20, 289))
    assert rec == {"config": "cfg", "bar_cm": 6.21, "bar_one_to_one_cm": 6.2143, "bar_refit_cm": 6.1994, "n_training_modes": 289,
                   "n_training_modes_one_to_one": 288, "n_target_rows": 20, "per_target_rms_cm": {"t1": 6.1994}}
    with pytest.raises(SystemExit, match=r"registered read's match gives 6\.2300"):
        F.family_record("ch/CH-stretch", printed, "cfg", _read(6.23, 20, 288), _read(6.1994, 20, 289))
    with pytest.raises(SystemExit, match="a new model, which needs its own registration"):
        F.family_record("ch/CH-stretch", printed, "cfg", _read(6.2143, 20, 288), _read(6.15, 20, 289))
    with pytest.raises(SystemExit, match=r"on 21 target rows against the registered 6\.2143 on 20"):
        F.family_record("ch/CH-stretch", printed, "cfg", _read(6.2143, 20, 288), _read(6.2143, 21, 289))
    with pytest.raises(SystemExit, match="printed with 'x1'"):
        F.family_record("ch/CH-stretch", {**printed, "model": "x1"}, "cfg", _read(6.2143, 20, 288), _read(6.1994, 20, 289))
    assert (F.TOLERANCE_CM, F.CHANGE_LIMIT_CM, F.REGISTERED_RULE) == (0.01, 0.05, "single")
