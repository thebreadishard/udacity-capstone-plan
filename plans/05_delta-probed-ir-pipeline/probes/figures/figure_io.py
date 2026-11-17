"""What every readers' figure shares (`reports/figures/`, one script per figure in this folder): a PNG and the CSV of its numbers are
written to a temp file and moved over the target, the PNG carries no date and no software version (the same inputs give the same bytes),
and each script prints the row for `reports/figures/INDEX.md`."""
from __future__ import annotations

import csv
import json
import os
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")                      # no display: the scripts run in a shell and in the tests
import matplotlib.pyplot as plt  # after the backend is chosen

PLAN = Path(__file__).resolve().parents[2]
FIGURES = PLAN / "reports" / "figures"
DPI = 150


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_png(fig: plt.Figure, path: Path) -> None:
    """The figure as a PNG without a software or date entry, moved into place; the figure is closed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    fig.savefig(tmp, format="png", dpi=DPI, metadata={"Software": None})
    plt.close(fig)
    os.replace(tmp, path)


def save_csv(path: Path, columns: list[str], rows: list[dict]) -> None:
    """The figure's numbers, one row per point, a missing value as an empty cell; floats in full precision, as the record holds them."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({c: "" if row.get(c) is None else repr(row[c]) if isinstance(row[c], float) else row[c] for c in columns})
    os.replace(tmp, path)


def index_row(png: Path, script: str, records: list[Path]) -> str:
    """The line for `reports/figures/INDEX.md`: the figure with its CSV, its script, the records it reads, today's date."""
    return (f"| `{png.name}` (`{png.with_suffix('.csv').name}`) | `probes/figures/{script}` | "
            f"{', '.join(f'`{r.as_posix()}`' for r in records)} | {date.today().isoformat()} |")
