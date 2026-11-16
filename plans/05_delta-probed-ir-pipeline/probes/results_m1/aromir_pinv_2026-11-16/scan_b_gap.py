"""The gap between the last real and the first null singular value of the Wilson B, for every corpus molecule (TASKS 236).

Read-only on the corpus. For each molecule folder with a `geometry.json`: B as aromir builds it under the bundled release's
primitive settings, its float64 singular values by the SVD with vectors (the route `np.linalg.pinv` takes) and by the
values-only route, and from them the 3N-6-th value (the last real one), the next (the first null one), their ratio, and how
many values numpy's default pinv cutoff (1e-15 times the largest) keeps. A molecule whose kept count is not 3N-6 is one where
`np.linalg.pinv(B)` returns a wrong pseudo-inverse on this build.

    python scan_b_gap.py <plan folder> <out.tsv> <summary.json> [--limit N]

One row per molecule is written as it is computed (flushed), the summary at the end through a temp file.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import time
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from aromir import release as aromir_release
from aromir.molecule import Geometry
from aromir.network import primitives

DEFAULT_RCOND = 1e-15      # np.linalg.pinv's default, relative to the largest singular value
PROGRESS_EVERY = 50
COLUMNS = ("id", "n_atoms", "n_primitives", "rank", "s_max", "s_last_real", "s_first_null", "null_over_real",
           "null_over_max", "real_over_max", "kept_by_default", "s_first_null_values_only", "kept_by_default_values_only")


@dataclass(frozen=True)
class Row:
    """One molecule's read; the names are the table's columns."""

    id: str
    n_atoms: int
    n_primitives: int
    rank: int
    s_max: float
    s_last_real: float
    s_first_null: float
    null_over_real: float
    null_over_max: float
    real_over_max: float
    kept_by_default: int
    s_first_null_values_only: float
    kept_by_default_values_only: int


def read_molecule(folder: Path, settings: primitives.PrimitiveSettings) -> Row:
    """Build one molecule's B and read its singular values around the rank 3N-6."""
    stored = json.loads((folder / "geometry.json").read_text(encoding="utf-8"))
    symbols = tuple(s[0].upper() + s[1:].lower() for s in stored["symbols"])
    geometry = Geometry(symbols, np.array(stored["coords_bohr"], float))
    b = primitives.build(geometry, settings).wilson_b
    rank = 3 * geometry.n_atoms - 6
    if min(b.shape) <= rank:
        raise ValueError(f"B {b.shape} has no singular value past 3N-6 = {rank}")
    s = np.linalg.svd(b, full_matrices=False)[1]
    values_only = np.linalg.svd(b, compute_uv=False)
    return Row(id=folder.name, n_atoms=geometry.n_atoms, n_primitives=b.shape[0], rank=rank, s_max=float(s[0]),
               s_last_real=float(s[rank - 1]), s_first_null=float(s[rank]), null_over_real=float(s[rank] / s[rank - 1]),
               null_over_max=float(s[rank] / s[0]), real_over_max=float(s[rank - 1] / s[0]),
               kept_by_default=int((s > DEFAULT_RCOND * s[0]).sum()),
               s_first_null_values_only=float(values_only[rank]),
               kept_by_default_values_only=int((values_only > DEFAULT_RCOND * values_only[0]).sum()))


def summarise(rows: list[Row], failed: dict[str, str], seconds: float) -> dict:
    """The scan's extremes: the smallest real value, the largest null one, and the molecules the default cutoff misreads."""
    smallest_real = min(rows, key=lambda r: r.real_over_max)
    largest_null = max(rows, key=lambda r: r.null_over_max)
    narrowest = max(rows, key=lambda r: r.null_over_real)
    wrong = [r.id for r in rows if r.kept_by_default != r.rank]
    wrong_values_only = [r.id for r in rows if r.kept_by_default_values_only != r.rank]
    return {"platform": platform.system(), "python": platform.python_version(), "numpy": np.__version__,
            "threads": os.environ.get("OMP_NUM_THREADS"), "n_molecules": len(rows), "n_failed": len(failed), "failed": failed,
            "seconds": round(seconds, 1),
            "smallest_real_over_max": asdict(smallest_real), "largest_null_over_max": asdict(largest_null),
            "narrowest_gap_null_over_real": asdict(narrowest),
            "default_cutoff_keeps_wrong_count": {"n": len(wrong), "ids": wrong},
            "default_cutoff_keeps_wrong_count_values_only": {"n": len(wrong_values_only), "ids": wrong_values_only}}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan", type=Path)
    ap.add_argument("table", type=Path)
    ap.add_argument("summary", type=Path)
    ap.add_argument("--limit", type=int, default=None, help="read only the first N molecules (a smoke test)")
    a = ap.parse_args()
    corpus = a.plan.resolve() / "modules" / "05_support_predictor" / "corpus" / "molecules"
    folders = sorted(f for f in corpus.iterdir() if (f / "geometry.json").is_file())[:a.limit]
    settings = aromir_release.load(aromir_release.bundled()).recipes[0].inputs.primitives
    print(f"scan: {len(folders)} molecules with a geometry, primitive settings {settings!r}, {platform.system()} "
          f"numpy {np.__version__}", flush=True)
    rows: list[Row] = []
    failed: dict[str, str] = {}
    start = time.monotonic()
    with a.table.open("w", encoding="utf-8", newline="\n") as table:
        table.write("\t".join(COLUMNS) + "\n")
        for count, folder in enumerate(folders, 1):
            try:
                row = read_molecule(folder, settings)
            except Exception as error:  # noqa: BLE001  every failure is counted and named in the summary
                failed[folder.name] = f"{type(error).__name__}: {error}"[:300]
            else:
                rows.append(row)
                table.write("\t".join(f"{v:.6e}" if isinstance(v, float) else str(v) for v in asdict(row).values()) + "\n")
                table.flush()
            if count % PROGRESS_EVERY == 0:
                print(f"scan: {count} of {len(folders)} read, {len(failed)} failed, {time.monotonic() - start:.0f} s", flush=True)
    summary = summarise(rows, failed, time.monotonic() - start)
    tmp = a.summary.with_name(a.summary.name + ".tmp")
    tmp.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, a.summary)
    print(f"scan done: {len(rows)} molecules read, {len(failed)} failed; smallest real/max "
          f"{summary['smallest_real_over_max']['real_over_max']:.3e} ({summary['smallest_real_over_max']['id']}), largest null/max "
          f"{summary['largest_null_over_max']['null_over_max']:.3e} ({summary['largest_null_over_max']['id']}), the default cutoff "
          f"keeps a wrong count for {summary['default_cutoff_keeps_wrong_count']['n']}", flush=True)


if __name__ == "__main__":
    main()
