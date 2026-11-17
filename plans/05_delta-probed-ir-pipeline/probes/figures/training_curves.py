"""Readers' figure: the curves of one trainer record — per seed the training and the validation value of each loss term against the
epoch, the best epoch and an early stop marked. One panel per term, logarithmic y-axis.

    python probes/figures/training_curves.py out/E7_rungC_<name>.json [--n 1082] [--title "…"] [--out reports/figures]

Writes `<record's name>_training_curves.png` and, beside it, the same numbers as `.csv` (one row per seed and epoch), and prints the row
for `reports/figures/INDEX.md`. What the numbers are is `m05/rungC_history.py`'s description; its caption goes under the figure. A record
made before 17 Nov 2026 has no validation value of the main term: that panel then shows the training side only and says so."""
from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "modules" / "05_support_predictor" / "m05"))
import figure_io as FIO
import rungC_history as RH
from figure_io import plt

TERMS = (("main", "val_main", "main term (mass-weighted Cartesian ΔH)"), ("aux", "val_aux", "auxiliary term (internal coordinates)"))
COLUMNS = ["n", "seed", "epoch", "lr", "main", "val_main", "aux", "val_aux", "best_epoch", "epoch_cap", "stopped_early"]


def pool_row(record: dict, n: int | None) -> dict:
    """The record's row of pool size `n`; without `n` the record must hold one size."""
    if not isinstance(record.get("curve"), dict) or "epochs" not in record:
        raise ValueError("the file has no 'curve' or no 'epochs': not a record of m05/rungC_train.py")
    rows = {row["n"]: row for row in record["curve"].values()}
    if n is None and len(rows) != 1:
        raise ValueError(f"the record holds the pool sizes {sorted(rows)}: choose one with --n")
    if n is not None and n not in rows:
        raise ValueError(f"no pool size {n} in the record: {sorted(rows)}")
    return rows[n] if n is not None else next(iter(rows.values()))


def curve_rows(record: dict, row: dict) -> list[dict]:
    """One row per seed and epoch: the history entry with the seed's best epoch, the epoch cap and whether the seed stopped before it."""
    cap = record["epochs"]
    return [{**entry, "n": row["n"], "seed": seed["seed"], "best_epoch": seed.get("best_epoch"), "epoch_cap": cap,
             "stopped_early": len(seed["train_history"]) < cap}
            for seed in row["per_seed"] for entry in seed["train_history"]]


def draw_term(ax: plt.Axes, rows: list[dict], train: str, validation: str, label: str) -> None:
    """One term's panel: per seed the training curve (solid) and the validation curve (dashed), a circle at the best epoch and a cross
    where an early stop ended the training."""
    notes = []
    for k, seed in enumerate(sorted({r["seed"] for r in rows})):
        mine = [r for r in rows if r["seed"] == seed]
        colour = f"C{k}"
        ax.plot([r["epoch"] for r in mine], [r[train] for r in mine], color=colour, linestyle="-", label=f"seed {seed}, training")
        if reason := RH.missing_reason(mine, validation):
            notes.append(reason)
            continue
        ax.plot([r["epoch"] for r in mine], [r[validation] for r in mine], color=colour, linestyle="--", label=f"seed {seed}, validation")
        if best := [r for r in mine if r["epoch"] == r["best_epoch"]]:
            ax.plot(best[0]["epoch"], best[0][validation], marker="o", color=colour, markerfacecolor="none", markersize=9)
        if mine[-1]["stopped_early"]:
            ax.plot(mine[-1]["epoch"], mine[-1][validation], marker="x", color=colour, markersize=9)
    ax.set_yscale("log")
    ax.set_xlabel("epoch")
    ax.set_title(label + "".join(f"\n({note})" for note in sorted(set(notes))), fontsize=10)
    ax.legend(fontsize=7)


def figure(rows: list[dict], title: str) -> plt.Figure:
    fig, axes = plt.subplots(1, len(TERMS), figsize=(11.0, 5.4))
    for ax, (train, validation, label) in zip(axes, TERMS, strict=True):
        draw_term(ax, rows, train, validation, label)
    fig.suptitle(title, fontsize=11)
    caption = "Circle: the best epoch on the validation auxiliary term, whose weights are kept. Cross: early stop. " + RH.CAPTION
    fig.text(0.02, 0.01, textwrap.fill(caption, 170), fontsize=7, va="bottom")
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    return fig


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("record", type=Path, help="a record of m05/rungC_train.py")
    ap.add_argument("--n", type=int, default=None, help="the pool size, when the record holds several")
    ap.add_argument("--title", default=None)
    ap.add_argument("--out", type=Path, default=FIO.FIGURES)
    args = ap.parse_args(argv)
    try:
        record = FIO.read_json(args.record)
        row = pool_row(record, args.n)
    except ValueError as e:
        ap.error(str(e))
    rows = curve_rows(record, row)
    png = args.out / f"{args.record.stem}_training_curves.png"
    FIO.save_csv(png.with_suffix(".csv"), COLUMNS, rows)
    FIO.save_png(figure(rows, args.title or f"{args.record.stem}: {row['n']} pool molecules, {len(row['per_seed'])} seed(s)"), png)
    print(FIO.index_row(png, Path(__file__).name, [args.record]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
