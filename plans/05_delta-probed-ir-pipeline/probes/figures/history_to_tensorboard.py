"""Turn the training histories of stored trainer records into TensorBoard event logs — the trainings made before the trainer wrote its own
(`m05/rungC_train.py --event-log`, 17 Nov 2026). The same writer (`m05/rungC_history.EventLog`), fed from each record's `train_history`;
the record stays the source of every number.

    python probes/figures/history_to_tensorboard.py out/E7_rungC_<a>.json out/v14/E7_rungC_<b>.json … --out out/tensorboard
    tensorboard --logdir out/tensorboard

One run folder per record, size and seed: `<out>/<record's file name without .json>/n<n>_seed<seed>/`, so the runs sort as the records'
names do. A record made before 17 Nov 2026 has no `val_main` and no `lr`: those series are left out and named in the output."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "modules" / "05_support_predictor" / "m05"))
import rungC_history as RH


def trainings(record: dict, path: Path) -> list[tuple[int, dict]]:
    """(pool size, per-seed entry) of every training in a trainer record; a file that is no such record is refused."""
    if not isinstance(record.get("curve"), dict):
        raise ValueError(f"{path}: no 'curve' — not a record of m05/rungC_train.py")
    found = [(row["n"], entry) for row in record["curve"].values() for entry in row["per_seed"]]
    if without := [f"n={n} seed {entry.get('seed')}" for n, entry in found if not entry.get("train_history")]:
        raise ValueError(f"{path}: no train_history for {without}")
    return found


def convert(path: Path, out: Path) -> list[str]:
    """Write one record's trainings as event logs under `out`; one line per run saying what was written and what the record lacks."""
    with path.open(encoding="utf-8") as fh:
        record = json.load(fh)
    lines = []
    for n, entry in trainings(record, path):
        history, seed = entry["train_history"], entry["seed"]
        run_dir = out / path.stem / f"n{n}_seed{seed}"
        final = {"inner_val_aux": entry.get("inner_val_aux"), "inner_val_main": entry.get("inner_val_main"), "epochs_run": len(history)}
        tags = RH.write_event_log(run_dir, history, entry.get("best_epoch"), RH.hparams(record, n, seed), final)
        lacks = [reason for key in RH.SCALAR_TAGS if (reason := RH.missing_reason(history, key))]
        lines.append(f"{run_dir.as_posix()}: {len(history)} epochs, {', '.join(tags)}" + (f" — left out: {'; '.join(lacks)}" if lacks else ""))
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("records", nargs="+", type=Path, help="trainer records (JSON)")
    ap.add_argument("--out", required=True, type=Path, help="the folder TensorBoard will read (--logdir)")
    args = ap.parse_args(argv)
    stems = [p.stem for p in args.records]
    if twice := sorted({s for s in stems if stems.count(s) > 1}):
        ap.error(f"records with the same file name would share a run folder: {twice}")
    if missing := [str(p) for p in args.records if not p.is_file()]:
        ap.error(f"not found: {missing}")
    RH.summary_writer_class()
    for path in args.records:
        for line in convert(path, args.out):
            print(line, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
