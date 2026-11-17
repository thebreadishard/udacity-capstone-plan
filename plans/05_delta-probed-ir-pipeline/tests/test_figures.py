"""The readers' figures and the record-to-TensorBoard converter (`probes/figures/`): on the trainer pin's record (`tests/data/
rungC_train_golden.json`, a real record of 3 epochs), on the same record in the format of before 17 Nov 2026, and on synthetic eval
records. No corpus, no training."""
import csv
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
from pin_tools import DATA, M05, event_scalars

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes" / "figures"))
sys.path.insert(0, str(M05))
import history_to_tensorboard as H2T
import per_seed_molecule as PSM
import rungC_history as RH
import training_curves as TC

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
NEW_KEYS = ("val_main", "lr")


def _record() -> dict:
    return json.loads((DATA / "rungC_train_golden.json").read_text(encoding="utf-8"))["carried"]["record"]


def _old_format(record: dict) -> dict:
    """The record as the trainer wrote it before 17 Nov 2026: no `val_main`, no `lr`, no `inner_val_main`."""
    for row in record["curve"].values():
        for seed in row["per_seed"]:
            del seed["inner_val_main"]
            seed["train_history"] = [{k: v for k, v in h.items() if k not in NEW_KEYS} for h in seed["train_history"]]
    return record


def _write(tmp_path: Path, name: str, record: dict) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


def _history(record: dict) -> list[dict]:
    return record["curve"]["5"]["per_seed"][0]["train_history"]


def test_the_converter_writes_a_records_history_as_events(tmp_path, capsys):
    pytest.importorskip("tensorboard")
    record = _record()
    path = _write(tmp_path, "E7_rungC_pin", record)
    assert H2T.main([str(path), "--out", str(tmp_path / "tb")]) == 0
    run_dir = tmp_path / "tb" / "E7_rungC_pin" / "n5_seed0"
    scalars = event_scalars(run_dir)
    assert all([step for step, _ in scalars[tag]] == [1, 2, 3] for tag in RH.SCALAR_TAGS.values())
    assert [v for _, v in scalars["loss/val_main"]] == pytest.approx([h["val_main"] for h in _history(record)], rel=1e-6)
    best = record["curve"]["5"]["per_seed"][0]["best_epoch"]
    assert scalars[RH.BEST_EPOCH_TAG] == [(best, float(best))] and scalars["hparam/epochs_run"] == [(0, 3.0)]
    out = capsys.readouterr().out
    assert "3 epochs" in out and "left out" not in out


def test_the_converter_says_what_an_old_record_lacks(tmp_path, capsys):
    pytest.importorskip("tensorboard")
    path = _write(tmp_path, "E7_rungC_old", _old_format(_record()))
    assert H2T.main([str(path), "--out", str(tmp_path / "tb")]) == 0
    scalars = event_scalars(tmp_path / "tb" / "E7_rungC_old" / "n5_seed0")
    assert {"loss/train_main", "loss/train_aux", "loss/val_aux"} <= set(scalars) and not {"loss/val_main", "lr", "hparam/inner_val_main"} & set(scalars)
    out = capsys.readouterr().out
    assert "left out: val_main: not recorded before 17 Nov 2026; lr: not recorded before 17 Nov 2026" in out


def test_the_converter_refuses_what_is_no_trainer_record(tmp_path):
    pytest.importorskip("tensorboard")
    with pytest.raises(ValueError, match=r"not a record of m05/rungC_train\.py"):
        H2T.convert(_write(tmp_path, "eval", {"a8": {}}), tmp_path / "tb")
    twin = tmp_path / "elsewhere"
    twin.mkdir()
    with pytest.raises(SystemExit):
        H2T.main([str(_write(tmp_path, "same", _record())), str(_write(twin, "same", _record())), "--out", str(tmp_path / "tb")])
    assert not (tmp_path / "tb").exists()


@pytest.mark.parametrize("old", [False, True])
def test_training_curves_writes_the_figure_and_its_numbers(tmp_path, capsys, old):
    record = _old_format(_record()) if old else _record()
    path = _write(tmp_path, "E7_rungC_pin", record)
    out = tmp_path / "figures"
    assert TC.main([str(path), "--out", str(out)]) == 0
    png, table = out / "E7_rungC_pin_training_curves.png", out / "E7_rungC_pin_training_curves.csv"
    first = png.read_bytes()
    assert first.startswith(PNG_MAGIC) and not list(out.glob("*.tmp"))
    with table.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    history = _history(record)
    assert [float(r["aux"]) for r in rows] == [h["aux"] for h in history] and [float(r["val_aux"]) for r in rows] == [h["val_aux"] for h in history]
    assert [r["val_main"] for r in rows] == ([""] * 3 if old else [repr(h["val_main"]) for h in history])
    assert {(r["n"], r["seed"], r["epoch_cap"], r["stopped_early"]) for r in rows} == {("5", "0", "3", "False")}
    assert "| `E7_rungC_pin_training_curves.png` (`E7_rungC_pin_training_curves.csv`) | `probes/figures/training_curves.py` |" in capsys.readouterr().out
    assert TC.main([str(path), "--out", str(out)]) == 0 and png.read_bytes() == first          # the same record gives the same bytes


def test_training_curves_marks_an_early_stop_and_asks_for_a_size():
    record = {"epochs": 10, "curve": {
        "5": {"n": 5, "per_seed": [{"seed": 1, "best_epoch": 2, "train_history": [dict(epoch=e, main=1.0, aux=1.0, val_aux=1.0) for e in (1, 2, 3)]}]},
        "9": {"n": 9, "per_seed": []}}}
    with pytest.raises(ValueError, match=r"pool sizes \[5, 9\]: choose one with --n"):
        TC.pool_row(record, None)
    with pytest.raises(ValueError, match="no pool size 7"):
        TC.pool_row(record, 7)
    rows = TC.curve_rows(record, TC.pool_row(record, 5))
    assert [(r["epoch"], r["best_epoch"], r["stopped_early"]) for r in rows] == [(1, 2, True), (2, 2, True), (3, 2, True)]
    fig = TC.figure(rows, "early stop")
    main_panel, aux_panel = fig.axes
    assert "val_main: not recorded before 17 Nov 2026" in main_panel.get_title() and len(main_panel.lines) == 1
    assert [line.get_marker() for line in aux_panel.lines] == ["None", "None", "o", "x"]         # training, validation, best epoch, early stop
    TC.plt.close(fig)


def _eval_records(tmp_path: Path) -> list[str]:
    values = {"new": [5.0, 1.5, 1.25], "carried": [1.0, 1.125, 0.75]}
    for label, per_seed in values.items():
        for seed, value in enumerate(per_seed):
            record = {"a8": {"corrected_freq_rms": 2.0, "per_molecule": {"A_benzene": {"corrected_freq_rms": value, "n_modes": 30},
                                                                        "A_other": {"corrected_freq_rms": 9.0}}}}
            _write(tmp_path, f"eval_{label}_seed{seed}", record)
    return ["--arm", f"v1.4={tmp_path.as_posix()}/eval_new_seed{{seed}}.json", "--arm", f"carried={tmp_path.as_posix()}/eval_carried_seed{{seed}}.json"]


def test_per_seed_molecule_reads_one_molecule_from_two_arms(tmp_path, capsys):
    arms = _eval_records(tmp_path)
    out = tmp_path / "figures"
    argv = ["--molecule", "A_benzene", "--name", "benzene_per_seed", "--seeds", "0,1,2", *arms, "--out", str(out)]
    assert PSM.main(argv) == 0
    first = (out / "benzene_per_seed.png").read_bytes()
    with (out / "benzene_per_seed.csv").open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert [(r["arm"], r["seed"], r["value"]) for r in rows] == [("v1.4", "0", "5.0"), ("v1.4", "1", "1.5"), ("v1.4", "2", "1.25"),
                                                                 ("carried", "0", "1.0"), ("carried", "1", "1.125"), ("carried", "2", "0.75")]
    assert all(Path(r["record"]).is_file() for r in rows) and first.startswith(PNG_MAGIC)
    assert "`probes/figures/per_seed_molecule.py`" in capsys.readouterr().out
    assert PSM.main(argv) == 0 and (out / "benzene_per_seed.png").read_bytes() == first


@pytest.mark.parametrize(("change", "reason"), [
    (["--molecule", "A_absent"], "molecule 'A_absent' is not on hold-out 'a8'"),
    (["--holdout", "b"], "no per-molecule read-outs on hold-out 'b'"),
    (["--metric", "coupling_rms"], "no 'coupling_rms' for A_benzene"),
    (["--seeds", "0,3"], "seed 3"),
    (["--arm", "third=x{seed}.json"], "2 arms with different labels"),
    (["--arm", "no-seed=x.json"], "'label=path' with {seed} in the path"),
])
def test_per_seed_molecule_refuses_with_the_reason(tmp_path, capsys, change, reason):
    argv = ["--molecule", "A_benzene", "--name", "x", "--seeds", "0,1,2", *_eval_records(tmp_path), "--out", str(tmp_path / "figures"), *change]
    with pytest.raises(SystemExit):
        PSM.main(argv)
    assert reason in capsys.readouterr().err and not (tmp_path / "figures").exists()
