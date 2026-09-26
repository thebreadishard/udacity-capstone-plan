"""Merge the shards of run_simulation.py (same pool, same settings) into one results JSON + md: `python merge_shards.py <out_prefix_of_merged> <shard1.json> <shard2.json> ...`."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_simulation import ratio_summary  # noqa: E402


def main() -> int:
    out_prefix, files = sys.argv[1], sys.argv[2:]
    parts = [json.load(open(f)) for f in files]
    base = dict(parts[0])
    per_mol = {}
    for p in parts:
        per_mol.update(p["per_molecule"])
    summary = {}
    for split in ("eval_parents", "eval"):
        sub = {i: m for i, m in per_mol.items() if m["split"] == split}
        if not sub:
            continue
        names = [n for n in next(iter(sub.values())) if n.startswith(("P1", "P2", "P3"))]
        summary[split] = {key: {name: ratio_summary(sub, "P0", name, key) for name in names} for key in ("K_off_0p3", "K_off_0p1", "n10_inband", "n10_all")}
        summary[split]["n_molecules"] = len(sub)
        summary[split]["P0_reached_0p3"] = int(sum(m["P0"]["K_off_0p3"] is not None for m in sub.values()))
    base.update(per_molecule=per_mol, summary=summary, shards=files, seconds=float(np.sum([p["seconds"] for p in parts])))
    json.dump(base, open(out_prefix + ".json", "w"), indent=1)
    lines = [f"# Pattern-proposer simulation — pool {base['pool']}, merged {len(files)} shards", "",
             f"seeds {base['seeds']}, {base['checkpoints']} checkpoints per curve, λ {base['lam_grid']}, noise σ {base['noise_sigma']}; {len(per_mol)} evaluation molecules; "
             f"{base['seconds'] / 3600:.1f} CPU-hours.", ""]
    for split, tab in summary.items():
        lines += [f"## {split} (n {tab['n_molecules']}; P0 reaches ρ_off ≤ 0.3 on {tab['P0_reached_0p3']})", "", "| read-out | ordering | n | median ratio vs P0 | improved |", "|---|---|---|---|---|"]
        for key in ("K_off_0p3", "K_off_0p1", "n10_inband", "n10_all"):
            for name, v in tab[key].items():
                mr = "—" if v["median_ratio"] is None else f"{v['median_ratio']:.2f}"
                fi = "—" if v["frac_improved"] is None else f"{100 * v['frac_improved']:.0f} %"
                lines.append(f"| {key} | {name} | {v['n']} | {mr} | {fi} |")
        lines.append("")
    Path(out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    print(f"merged {len(per_mol)} molecules -> {out_prefix}.json/.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
