"""Readers' figure: one hold-out molecule, one error per seed, for two arms — read from eval records
(`<hold-out>.per_molecule[<molecule>].<metric>`, as `out/v14/eval_data_seed*.json` hold it).

    python probes/figures/per_seed_molecule.py --molecule <id> --name benzene_per_seed --seeds 0,1,2 \\
        --arm "v1.4=out/v14/eval_data_seed{seed}.json" --arm "carried=out/v14/eval_carried_data_seed{seed}.json" \\
        [--holdout a8] [--metric corrected_freq_rms] [--ylabel "…"] [--title "…"] [--out reports/figures]

Each `--arm` is `label=path` with `{seed}` where the seed stands in the file name. Writes `<name>.png` and the same numbers as
`<name>.csv` (arm, seed, value, the record read), and prints the row for `reports/figures/INDEX.md`."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import figure_io as FIO
from figure_io import plt

COLUMNS = ["arm", "seed", "value", "record"]
N_ARMS = 2
BAR_WIDTH = 0.38


def arm(spec: str) -> tuple[str, str]:
    """`label=path with {seed}` as (label, path pattern)."""
    label, sep, pattern = spec.partition("=")
    if not sep or not label or "{seed}" not in pattern:
        raise argparse.ArgumentTypeError(f"--arm {spec!r}: 'label=path' with {{seed}} in the path")
    return label, pattern


def molecule_value(record: dict, path: Path, holdout: str, molecule: str, metric: str) -> float:
    """`record[holdout].per_molecule[molecule][metric]`, or the reason it is not there."""
    if holdout not in record or "per_molecule" not in record[holdout]:
        raise ValueError(f"{path}: no per-molecule read-outs on hold-out {holdout!r}")
    per_molecule = record[holdout]["per_molecule"]
    if molecule not in per_molecule:
        raise ValueError(f"{path}: molecule {molecule!r} is not on hold-out {holdout!r} ({len(per_molecule)} molecules)")
    if metric not in per_molecule[molecule]:
        raise ValueError(f"{path}: no {metric!r} for {molecule}: {sorted(per_molecule[molecule])}")
    return float(per_molecule[molecule][metric])


def read_rows(arms: list[tuple[str, str]], seeds: list[int], pick: tuple[str, str, str]) -> list[dict]:
    """One row per arm and seed; `pick` = (hold-out, molecule, metric)."""
    rows = []
    for label, pattern in arms:
        for seed in seeds:
            path = Path(pattern.format(seed=seed))
            rows.append({"arm": label, "seed": seed, "value": molecule_value(FIO.read_json(path), path, *pick), "record": path.as_posix()})
    return rows


def figure(rows: list[dict], title: str, ylabel: str) -> plt.Figure:
    seeds = sorted({r["seed"] for r in rows})
    labels = list(dict.fromkeys(r["arm"] for r in rows))
    fig, ax = plt.subplots(figsize=(1.6 + 1.5 * len(seeds), 4.2))
    for k, label in enumerate(labels):
        values = [next(r["value"] for r in rows if r["arm"] == label and r["seed"] == seed) for seed in seeds]
        bars = ax.bar([i + (k - (len(labels) - 1) / 2) * BAR_WIDTH for i in range(len(seeds))], values, BAR_WIDTH, label=label, color=f"C{k}")
        ax.bar_label(bars, fmt="%.2f", fontsize=8)
    ax.set_xticks(range(len(seeds)), [f"seed {s}" for s in seeds])
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    return fig


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--molecule", required=True, help="the molecule's id in the eval records")
    ap.add_argument("--name", required=True, help="the figure's file name without extension")
    ap.add_argument("--arm", action="append", type=arm, required=True, help="label=path with {seed}; give it twice")
    ap.add_argument("--seeds", required=True, help="comma list, e.g. 0,1,2")
    ap.add_argument("--holdout", default="a8")
    ap.add_argument("--metric", default="corrected_freq_rms")
    ap.add_argument("--ylabel", default=None)
    ap.add_argument("--title", default=None)
    ap.add_argument("--out", type=Path, default=FIO.FIGURES)
    args = ap.parse_args(argv)
    if len(args.arm) != N_ARMS or args.arm[0][0] == args.arm[1][0]:
        ap.error(f"{N_ARMS} arms with different labels, got {[label for label, _ in args.arm]}")
    if not all(s.isdigit() for s in args.seeds.split(",")):
        ap.error(f"--seeds {args.seeds!r}: comma-separated non-negative integers")
    try:
        rows = read_rows(args.arm, [int(s) for s in args.seeds.split(",")], (args.holdout, args.molecule, args.metric))
    except ValueError as e:
        ap.error(str(e))
    png = args.out / f"{args.name}.png"
    FIO.save_csv(png.with_suffix(".csv"), COLUMNS, rows)
    FIO.save_png(figure(rows, args.title or f"{args.molecule} on hold-out ({args.holdout}), per seed", args.ylabel or args.metric), png)
    print(FIO.index_row(png, Path(__file__).name, [Path(r["record"]) for r in rows]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
