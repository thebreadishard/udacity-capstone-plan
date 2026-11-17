"""The per-epoch history of a rung-C training (`train_history` in a record's per-seed entry, written by `rungC_train._fit`): what each
number is, how to read one series from it, and the TensorBoard event log written from it. No torch at import: a plot or a table can
import this alone; only opening an event log loads torch's writer.

Every loss number is a mean over molecules of the molecule's own term, each molecule counting once whatever its size; the molecule's term
is itself a mean over its entries (`rungC_train._terms`): `main` over the 3N × 3N entries of the mass-weighted Cartesian ΔH error
(× LOSS_SCALE, squared), `aux` over what the record's `aux` mode names in internal coordinates.

The two sides of a train-against-validation curve are not taken at the same weights. `main` and `aux` are running means over the epoch:
each fit molecule's term is taken in the forward pass of its own optimiser step, in train mode, so the first molecule of the epoch sees
the weights the previous epoch ended with and the last one the weights after all the other steps. `val_main` and `val_aux` are taken once
at the epoch's end, in eval mode, at the weights the epoch ends with, from one forward pass per validation molecule. Early in a training,
where one epoch moves the weights a lot, the training side therefore reads higher than it would at the epoch's end.

Early stopping reads `val_aux` only. `val_main` and `lr` are recorded since 17 Nov 2026; a record without an inner-validation set has
neither validation series.

The event log (`EventLog`) holds the same numbers and nothing else: every scalar is a history entry's value under the tag of
`SCALAR_TAGS`, at the step of its epoch, written once that entry is final. The record stays the source; a log can be made again from a
record (`probes/figures/history_to_tensorboard.py`). TensorBoard stores a scalar as a 32-bit float.

The log is a view and never stops a training: when the folder, a write or the close fails (any exception — a full disk, a file another
process holds, an error inside tensorboard), `EventLog` says so in one line, writes no more for that run and keeps the reason in `incomplete`, which the trainer
puts in the record as `event_log_incomplete`. On Windows a TensorBoard that reads the folder does not make a write fail (measured
17 Nov 2026, tensorboard 2.21.0: an append while the event file is held open for reading succeeds); only removing an earlier
run's file fails while a reader has it open, and that ends the log of the new run, not the training."""
from __future__ import annotations

import contextlib
from collections.abc import Callable
from pathlib import Path

RECORDED_SINCE = {"val_main": "17 Nov 2026", "lr": "17 Nov 2026"}
CAPTION = ("Training values are running means over the epoch, each molecule's term taken at its own step while the weights change; "
           "validation values are taken at the epoch's end. Each is a mean over molecules of the molecule's own mean.")
HISTORY_KEYS = {
    "epoch": "the epoch, counted from 1",
    "lr": "the learning rate of the epoch's steps",
    "main": "main term, running mean over the fit molecules during the epoch",
    "aux": "auxiliary term, running mean over the fit molecules during the epoch",
    "val_main": "main term, mean over the inner-validation molecules at the epoch's end",
    "val_aux": "auxiliary term, mean over the inner-validation molecules at the epoch's end (early stopping reads this one)",
}
SCALAR_TAGS = {"main": "loss/train_main", "val_main": "loss/val_main", "aux": "loss/train_aux", "val_aux": "loss/val_aux", "lr": "lr"}
BEST_EPOCH_TAG = "early_stopping/best_epoch"
EVENT_FILES = "events.out.tfevents.*"
CONVERTER = "probes/figures/history_to_tensorboard.py"
N_DIGITS = 5                                # run names sort by pool size: n00045 before n00100
# the settings TensorBoard's HParams tab compares, under the names a record's header gives them
HPARAM_KEYS = ("lr", "lr_schedule", "weight_decay", "epochs", "patience", "inner_val", "loss", "scale", "aux_mode", "aux_weight",
               "aux_target", "kring_weight", "kdiag_weight", "kdiag_mode", "head", "pattern", "hybrid_hidden", "body_blocks", "body_width",
               "aggregation", "pool_layers", "holdout_twins")


def missing_reason(history: list[dict], key: str) -> str | None:
    """Why `history` does not hold the series `key` in every epoch; None when it does."""
    if key not in HISTORY_KEYS:
        return f"train_history has no series {key!r}: {', '.join(HISTORY_KEYS)}"
    if all(key in h for h in history):
        return None
    if key in ("val_main", "val_aux") and not any("val_aux" in h for h in history):
        return f"{key}: this training had no inner-validation set"
    if key in RECORDED_SINCE and not any(key in h for h in history):
        return f"{key}: not recorded before {RECORDED_SINCE[key]}"
    return f"{key}: missing in epochs {[h.get('epoch') for h in history if key not in h]}"


def history_series(history: list[dict], key: str) -> list[float]:
    """The values of `key` over the epochs of one `train_history`; a record that does not hold the series is refused with the reason."""
    if reason := missing_reason(history, key):
        raise ValueError(reason)
    return [h[key] for h in history]


def run_name(n: int, seed: int) -> str:
    """One training's run folder: the pool size, zero-padded so that the runs sort by it, and the seed."""
    return f"n{n:0{N_DIGITS}d}_seed{seed}"


def event_log_root(out_prefix: str | Path) -> Path:
    """The folder of a record's event logs: `<prefix>_tb/` beside the record."""
    prefix = Path(out_prefix)
    return prefix.with_name(prefix.name + "_tb")


def event_log_dir(out_prefix: str | Path, n: int, seed: int) -> Path:
    """Where the training of `n` molecules with `seed` writes its event log: `<prefix>_tb/n<n, five digits>_seed<seed>/`."""
    return event_log_root(out_prefix) / run_name(n, seed)


def incomplete_line(where: Path, reason: str) -> str:
    """The one line a failed event log prints."""
    return (f"EVENT LOG INCOMPLETE in {where}: {reason} — the training goes on and its record holds every number; make the log again "
            f"from the record with {CONVERTER}")


def prepare_event_logs(out_prefix: str | Path, log: Callable[[str], None] = print) -> str | None:
    """Make `<prefix>_tb/` and write one probe file into it, before the corpus is loaded, so that a blocked folder is said at the start.
    A failure is a line and its reason returned, not a refusal: the trainings run, each without its log."""
    root = event_log_root(out_prefix)
    try:
        root.mkdir(parents=True, exist_ok=True)
        probe = root / ".writable"
        probe.write_text("", encoding="utf-8")
        probe.unlink()
    except OSError as e:
        reason = f"{type(e).__name__}: {e}"
        log(incomplete_line(root, reason))
        return reason
    return None


def summary_writer_class() -> type:
    """torch's `SummaryWriter`; without it the reason is raised, so that a run that asks for an event log stops before it trains."""
    try:
        from torch.utils.tensorboard import SummaryWriter
    except ImportError as e:
        raise RuntimeError(f"the event log needs torch with the tensorboard package ({e}): install tensorboard, or run with "
                           "--no-event-log") from e
    return SummaryWriter


def hparams(settings: dict, n: int, seed: int) -> dict:
    """One training's row for the HParams tab: the HPARAM_KEYS that `settings` (a record's header) holds, the pool size and the seed.
    A value TensorBoard cannot hold (None, a list) goes in as its text."""
    out: dict = {"n": n, "seed": seed}
    for key in HPARAM_KEYS:
        if key in settings:
            value = settings[key]
            out[key] = value if isinstance(value, bool | int | float | str) else str(value)
    return out


class EventLog:
    """One training's TensorBoard event log in `run_dir`; with `run_dir` None the setting is off and every call does nothing.

    It only writes what it is handed: nothing is read from the model and no random number is drawn. Event files an earlier run left in
    `run_dir` are removed first, as the record of the same prefix is overwritten, so that the folder shows one training.

    An exception at any point ends the log, never the training: one line to `log`, no further write, the reason in `incomplete`
    (None while the log is whole). A missing tensorboard package is a configuration fault and is raised, before anything is written."""

    def __init__(self, run_dir: Path | None, log: Callable[[str], None] = print) -> None:
        self.run_dir = run_dir
        self.incomplete: str | None = None
        self._log = log
        self._writer = None
        if run_dir is not None:
            self._guarded(self._open, summary_writer_class())

    def _open(self, writer_class: type) -> None:
        self.run_dir.mkdir(parents=True, exist_ok=True)
        for earlier in self.run_dir.glob(EVENT_FILES):
            try:
                earlier.unlink()
            except OSError as e:
                raise OSError(f"an earlier run's events remain in the folder and are not this training's ({type(e).__name__}: {e})") from e
        self._writer = writer_class(log_dir=str(self.run_dir))

    def _guarded(self, write: Callable[..., None], *args: object) -> None:
        """Run one step of the log; whatever it raises ends the log with its line and is not passed on."""
        try:
            write(*args)
        except Exception as e:  # noqa: BLE001  a view must not stop a training whose record is written only after every seed
            self.incomplete = f"{type(e).__name__}: {e}"
            writer, self._writer = self._writer, None
            self._log(incomplete_line(self.run_dir, self.incomplete))
            if writer is not None:
                with contextlib.suppress(Exception):             # the writer that just failed may fail again while it closes
                    writer.close()

    def __enter__(self) -> EventLog:
        return self

    def __exit__(self, *exc: object) -> None:
        if self._writer is not None:
            self._guarded(self._writer.close)
            self._writer = None

    def epoch(self, entry: dict) -> None:
        """One final history entry: a scalar per series it holds, at the step of its epoch."""
        if self._writer is not None:
            self._guarded(self._write_epoch, entry)

    def _write_epoch(self, entry: dict) -> None:
        for key, tag in SCALAR_TAGS.items():
            if key in entry:
                self._writer.add_scalar(tag, entry[key], entry["epoch"])
        self._writer.flush()

    def finish(self, best_epoch: int | None, settings: dict, final: dict) -> None:
        """The end of the training: the best epoch and, for the HParams tab, the settings (`hparams`) with the final numbers `final`
        (a None among them is left out). `add_hparams(..., run_name=".")` keeps them in this run's folder: torch's
        `utils/tensorboard/writer.py` joins `run_name` to the log folder and, without one, opens a sub-run named by the clock."""
        if self._writer is not None:
            self._guarded(self._write_end, best_epoch, settings, final)

    def _write_end(self, best_epoch: int | None, settings: dict, final: dict) -> None:
        metrics = {f"hparam/{key}": value for key, value in final.items() if value is not None}
        if best_epoch is not None:
            self._writer.add_scalar(BEST_EPOCH_TAG, best_epoch, best_epoch)
            metrics["hparam/best_epoch"] = best_epoch
        self._writer.add_hparams(settings, metrics, run_name=".")
        self._writer.flush()


def write_event_log(run_dir: Path, history: list[dict], best_epoch: int | None, settings: dict, final: dict) -> list[str]:
    """A whole stored training as an event log; the tags of the series it wrote. Here the log is the product: a failure is raised."""
    with EventLog(run_dir, log=lambda line: None) as events:
        for entry in history:
            events.epoch(entry)
        events.finish(best_epoch, settings, final)
    if events.incomplete:
        raise OSError(f"{run_dir}: {events.incomplete}")
    return [tag for key, tag in SCALAR_TAGS.items() if any(key in entry for entry in history)]
