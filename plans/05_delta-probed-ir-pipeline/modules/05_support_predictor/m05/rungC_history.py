"""The per-epoch history of a rung-C training (`train_history` in a record's per-seed entry, written by `rungC_train._fit`) and how to read
one series from it. No torch: a plot or a table can import this alone.

Every number is a mean over molecules of the molecule's own term, each molecule counting once whatever its size; the molecule's term is
itself a mean over its entries (`rungC_train._terms`): `main` over the 3N × 3N entries of the mass-weighted Cartesian ΔH error
(× LOSS_SCALE, squared), `aux` over what the record's `aux` mode names in internal coordinates.

The two sides of a train-against-validation curve are not taken at the same weights. `main` and `aux` are running means over the epoch:
each fit molecule's term is taken in the forward pass of its own optimiser step, in train mode, so the first molecule of the epoch sees
the weights the previous epoch ended with and the last one the weights after all the other steps. `val_main` and `val_aux` are taken once
at the epoch's end, in eval mode, at the weights the epoch ends with, from one forward pass per validation molecule. Early in a training,
where one epoch moves the weights a lot, the training side therefore reads higher than it would at the epoch's end.

Early stopping reads `val_aux` only. `val_main` is recorded since 17 Nov 2026; a record without an inner-validation set has neither."""
from __future__ import annotations

VAL_MAIN_SINCE = "17 Nov 2026"
HISTORY_KEYS = {
    "epoch": "the epoch, counted from 1",
    "main": "main term, running mean over the fit molecules during the epoch",
    "aux": "auxiliary term, running mean over the fit molecules during the epoch",
    "val_main": "main term, mean over the inner-validation molecules at the epoch's end",
    "val_aux": "auxiliary term, mean over the inner-validation molecules at the epoch's end (early stopping reads this one)",
}


def history_series(history: list[dict], key: str) -> list[float]:
    """The values of `key` over the epochs of one `train_history`; a record that does not hold the series is refused with the reason."""
    if key not in HISTORY_KEYS:
        raise ValueError(f"train_history has no series {key!r}: {', '.join(HISTORY_KEYS)}")
    if all(key in h for h in history):
        return [h[key] for h in history]
    if key == "val_main" and all("val_aux" in h for h in history):
        raise ValueError(f"val_main: not recorded before {VAL_MAIN_SINCE} (this record holds val_aux only)")
    if key in ("val_main", "val_aux") and not any(key in h for h in history):
        raise ValueError(f"{key}: this training had no inner-validation set")
    raise ValueError(f"{key}: missing in epochs {[h.get('epoch') for h in history if key not in h]}")
