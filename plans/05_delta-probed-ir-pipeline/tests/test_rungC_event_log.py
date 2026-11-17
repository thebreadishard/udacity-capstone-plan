"""The trainer's TensorBoard event log (`m05/rungC_history.EventLog`, the `event_log` setting): it holds the history's numbers and nothing
else, it leaves the training unchanged to the bit, it is refused up front without a writer — on synthetic water only."""
import contextlib
import sys

import numpy as np
import pytest

torch = pytest.importorskip("torch")
pytest.importorskip("tensorboard")
from pin_tools import M05, event_scalars  # noqa: E402
from test_rungC_train_switches import VAL_CFG, _water_tensors  # noqa: E402

sys.path.insert(0, str(M05))
import rungC_config as RC_CONFIG  # noqa: E402
import rungC_history as RH  # noqa: E402
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig  # noqa: E402

torch.set_num_threads(1)
COSINE = {**VAL_CFG, "lr_schedule": "cosine", "epochs": 30}          # stops early at 6 of 30 and restores epoch 4's weights


def _train(cfg: TrainConfig, on_epoch=RT._no_report) -> RT.Trained:
    tensors = _water_tensors(4)
    ids = list(tensors)
    return RT.train_fold(RT.Fold(tensors, ids[:2], ids[2:]), 0, cfg, RT.Progress(lambda s: None, on_epoch))


def _as_stored(value: float) -> float:
    return float(np.float32(value))


def test_the_event_log_holds_the_history_and_nothing_else(tmp_path):
    run_dir = RH.event_log_dir(tmp_path / "run", 2, 0)
    assert run_dir == tmp_path / "run_tb" / "n00002_seed0"
    assert sorted(RH.run_name(n, 0) for n in (100, 45, 1082)) == ["n00045_seed0", "n00100_seed0", "n01082_seed0"]
    cfg = TrainConfig(**COSINE)
    with RH.EventLog(run_dir) as events:
        trained = _train(cfg, events.epoch)
        events.finish(trained.best_epoch, RH.hparams({**cfg.model_dump(), "aux_mode": cfg.aux}, 2, 0),
                      {"inner_val_aux": 0.5, "inner_val_main": None, "epochs_run": len(trained.history)})
    scalars = event_scalars(run_dir)
    for key, tag in RH.SCALAR_TAGS.items():
        assert scalars.pop(tag) == [(h["epoch"], _as_stored(h[key])) for h in trained.history], tag
    assert scalars.pop(RH.BEST_EPOCH_TAG) == [(4, 4.0)] and trained.best_epoch == 4
    assert scalars == {"hparam/inner_val_aux": [(0, 0.5)], "hparam/epochs_run": [(0, 6.0)], "hparam/best_epoch": [(0, 4.0)]}


def test_the_history_records_the_rate_of_each_epoch():
    trained = _train(TrainConfig(**COSINE))
    assert [h["lr"] for h in trained.history] == [RC_CONFIG.learning_rate(1e-3, "cosine", ep, 30) for ep in range(len(trained.history))]


@pytest.mark.parametrize("settings", [VAL_CFG, COSINE])
def test_the_event_log_leaves_the_training_unchanged(tmp_path, settings):
    cfg = TrainConfig(**settings)
    plain = _train(cfg)
    with RH.EventLog(tmp_path / "log") as events:
        logged = _train(cfg, events.epoch)
    plain_state, logged_state = plain.model.state_dict(), logged.model.state_dict()
    assert list(plain_state) == list(logged_state) and all(torch.equal(plain_state[k], logged_state[k]) for k in plain_state)
    assert (plain.history, plain.best_epoch) == (logged.history, logged.best_epoch)
    assert list((tmp_path / "log").glob(RH.EVENT_FILES))


def test_a_log_that_is_off_writes_nothing(tmp_path):
    with RH.EventLog(None) as events:
        events.epoch(dict(epoch=1, main=1.0, aux=1.0))
        events.finish(1, {"n": 1}, {"inner_val_aux": 1.0})
    assert events.run_dir is None and list(tmp_path.iterdir()) == []


def test_a_run_folder_shows_one_training(tmp_path):
    """A second training with the same prefix replaces the first one's events, as its record replaces the first record."""
    for main in (2.0, 3.0):
        RH.write_event_log(tmp_path, [dict(epoch=1, main=main, aux=1.0)], None, {"n": 1}, {})
    assert event_scalars(tmp_path) == {"loss/train_main": [(1, 3.0)], "loss/train_aux": [(1, 1.0)]}


def test_the_switch_is_on_by_default_and_can_be_switched_off():
    assert RC_CONFIG.config_from_argv(["molecules", "prefix"]).event_log is True
    assert RC_CONFIG.config_from_argv(["molecules", "prefix", "--no-event-log"]).event_log is False


def test_without_a_writer_the_run_is_refused_before_the_corpus_is_loaded(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "torch.utils.tensorboard", None)            # the import then fails as without the package
    with pytest.raises(RuntimeError, match="--no-event-log"):
        RH.summary_writer_class()

    def loaded(*args, **kwargs):
        raise AssertionError("the corpus was loaded")

    monkeypatch.setattr(RT, "select_corpus", loaded)
    with pytest.raises(RuntimeError, match="the event log needs torch with the tensorboard package"):
        RT.main(["nowhere", str(tmp_path / "run"), "--threads", "1"])
    with pytest.raises(AssertionError, match="the corpus was loaded"):           # switched off, the run goes on to its corpus
        RT.main(["nowhere", str(tmp_path / "run"), "--threads", "1", "--no-event-log"])
    assert list(tmp_path.iterdir()) == []


def test_hparams_take_the_records_names_and_plain_values():
    row = RH.hparams({"lr": 3e-4, "aux_mode": "both", "pretrained": None, "pool_layers": "A,A2", "holdout_twins": None, "sizes": [5]}, 5, 2)
    assert row == {"n": 5, "seed": 2, "lr": 3e-4, "aux_mode": "both", "pool_layers": "A,A2", "holdout_twins": "None"}


def _same_training(a: RT.Trained, b: RT.Trained) -> bool:
    state_a, state_b = a.model.state_dict(), b.model.state_dict()
    return (list(state_a) == list(state_b) and all(torch.equal(state_a[k], state_b[k]) for k in state_a)
            and (a.history, a.best_epoch) == (b.history, b.best_epoch))


def test_a_write_that_fails_ends_the_log_and_not_the_training(tmp_path, monkeypatch):
    """A full disk at epoch 3: the training finishes with the same weights, one line names the reason and the converter, the log stops."""
    cfg = TrainConfig(**COSINE)
    lines = []
    with RH.EventLog(tmp_path / "log", lines.append) as events:
        add_scalar = events._writer.add_scalar

        def full_disk(tag, value, step):
            if step == 3:
                raise OSError(28, "No space left on device")
            add_scalar(tag, value, step)

        monkeypatch.setattr(events._writer, "add_scalar", full_disk)
        logged = _train(cfg, events.epoch)
        events.finish(logged.best_epoch, {"n": 2}, {"inner_val_aux": 1.0})
    assert _same_training(logged, _train(cfg)) and len(logged.history) == 6
    assert events.incomplete == "OSError: [Errno 28] No space left on device"
    assert len(lines) == 1 and lines[0].startswith("EVENT LOG INCOMPLETE") and events.incomplete in lines[0] and RH.CONVERTER in lines[0]
    scalars = event_scalars(tmp_path / "log")
    assert [step for step, _ in scalars["loss/train_main"]] == [1, 2] and not [tag for tag in scalars if tag.startswith("hparam/")]


@pytest.mark.skipif(sys.platform != "win32", reason="only Windows refuses to remove a file that another handle holds open")
def test_an_earlier_event_file_held_open_ends_the_log_and_not_the_training(tmp_path):
    cfg = TrainConfig(**VAL_CFG)
    RH.write_event_log(tmp_path, [dict(epoch=1, main=2.0, aux=1.0)], None, {"n": 1}, {})
    lines = []
    with contextlib.ExitStack() as held:
        for earlier in tmp_path.glob(RH.EVENT_FILES):
            held.enter_context(earlier.open("rb"))
        with RH.EventLog(tmp_path, lines.append) as events:
            logged = _train(cfg, events.epoch)
            events.finish(logged.best_epoch, {"n": 2}, {})
    assert _same_training(logged, _train(cfg))
    assert events.incomplete.startswith("PermissionError") and len(lines) == 1 and "EVENT LOG INCOMPLETE" in lines[0]
    assert event_scalars(tmp_path)["loss/train_main"] == [(1, 2.0)]                 # the earlier run's log, untouched


def test_a_blocked_folder_is_said_before_the_corpus_and_stops_nothing(tmp_path):
    (tmp_path / "run_tb").write_text("a file where the logs' folder goes", encoding="utf-8")
    lines = []
    reason = RH.prepare_event_logs(tmp_path / "run", lines.append)
    assert reason and "Error" in reason and len(lines) == 1 and lines[0].startswith("EVENT LOG INCOMPLETE")
    with RH.EventLog(RH.event_log_dir(tmp_path / "run", 2, 0), lines.append) as events:
        logged = _train(TrainConfig(**VAL_CFG), events.epoch)
        events.finish(logged.best_epoch, {"n": 2}, {})
    assert events.incomplete and len(lines) == 2 and len(logged.history) == 4
    with pytest.raises(OSError, match="run_tb"):                                    # the converter's log is its product: there it is raised
        RH.write_event_log(RH.event_log_dir(tmp_path / "run", 2, 0), [dict(epoch=1, main=1.0, aux=1.0)], None, {"n": 1}, {})
    assert RH.prepare_event_logs(tmp_path / "free", lines.append) is None and list((tmp_path / "free_tb").iterdir()) == [] and len(lines) == 2


def test_the_trainer_makes_the_logs_folder_before_it_loads_the_corpus(monkeypatch, tmp_path):
    def loaded(*args, **kwargs):
        assert (tmp_path / "run_tb").is_dir()
        raise RuntimeError("the corpus is next")

    monkeypatch.setattr(RT, "select_corpus", loaded)
    with pytest.raises(RuntimeError, match="the corpus is next"):
        RT.main(["nowhere", str(tmp_path / "run"), "--threads", "1"])
