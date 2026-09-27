"""Pick the winner of a rung C search stage (pre-registration of 25 September 2026, amendment of 27 September 20:0x): the cell with the lowest
seed-mean inner-validation internal term. Reads the cells' JSON records written by `rungC_train.py --inner-val`, prints one table and the
winning cell's command-line flags, and writes both beside the records.

    python m05/rungC_stage_pick.py 'out/E7_rungC_s1_{label}_2026-09-27' i: ii:'--aux-weight 1.0' iii:'--loss internal' iv:'--loss internal --scale class'

Each argument after the prefix is `label:flags`; the record read is the prefix with `{label}` substituted plus `.json` (a prefix without the
placeholder gets `_<label>` appended); the pick is written with the label `pick`. The hold-out read-outs are printed for information only;
the choice is by the inner term, as registered."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np


def cell_summary(record: Path) -> dict:
    r = json.load(open(record, encoding="utf-8"))
    row = next(iter(r["curve"].values()))
    seeds = row["per_seed"]
    inner = [s["inner_val_aux"] for s in seeds if s.get("inner_val_aux") is not None]
    out = {"n": row["n"], "inner_mean": float(np.mean(inner)) if inner else float("nan"), "inner_per_seed": inner, "seconds": r.get("seconds")}
    for h in ("a", "b"):
        vals = [s[h] for s in seeds if h in s]
        if vals:
            out[f"ratio_{h}"] = float(np.mean([v["coupling_ratio"] for v in vals]))
            out[f"omega_{h}"] = float(np.mean([v["corrected_freq_rms"] for v in vals]))
    return out


def record_path(prefix: str, label: str) -> str:
    """`out/E7_rungC_s1_{label}_2026-09-27` → the label substituted; a prefix without the placeholder gets `_<label>` appended."""
    return prefix.format(label=label) if "{label}" in prefix else f"{prefix}_{label}"


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    prefix, cells = argv[1], [c.split(":", 1) for c in argv[2:]]
    table = {}
    for label, flags in cells:
        record = Path(record_path(prefix, label) + ".json")
        if not record.exists():
            print(f"missing: {record}")
            continue
        table[label] = dict(flags=flags, **cell_summary(record))
    if not table:
        return 1
    winner = min(table, key=lambda k: table[k]["inner_mean"] if np.isfinite(table[k]["inner_mean"]) else float("inf"))   # a diverged cell (NaN) never wins
    lines = [f"# Stage pick — {prefix}", "", "| cell | flags | n | inner term (seed mean) | per seed | (a) ratio | (a) ω | (b) ratio | (b) ω |",
             "|---|---|---|---|---|---|---|---|---|"]
    for label, t in table.items():
        mark = " **winner**" if label == winner else ""
        lines.append(f"| {label}{mark} | `{t['flags'] or '(registered)'}` | {t['n']} | {t['inner_mean']:.4f} | "
                     f"{', '.join(f'{v:.4f}' for v in t['inner_per_seed'])} | {t.get('ratio_a', float('nan')):.2f} | {t.get('omega_a', float('nan')):.2f} | "
                     f"{t.get('ratio_b', float('nan')):.2f} | {t.get('omega_b', float('nan')):.2f} |")
    lines += ["", f"winner: {winner} → flags `{table[winner]['flags']}` (chosen by the inner term alone, as registered)", ""]
    text = "\n".join(lines)
    print(text)
    Path(record_path(prefix, "pick") + ".md").write_text(text, encoding="utf-8")
    pick = {"winner": winner, "flags": table[winner]["flags"], "table": table}
    Path(record_path(prefix, "pick") + ".json").write_text(json.dumps(pick, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
