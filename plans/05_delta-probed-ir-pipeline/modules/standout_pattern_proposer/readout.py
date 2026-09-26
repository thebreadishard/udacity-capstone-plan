"""Read-out of a (merged) simulation JSON against the pre-registration of 26 September 2026, including the fallback read-outs registered at 12:0x for the
case that ρ_off ≤ 0.3 is not reached under P0 on most molecules (the band finding made that likely):

  n_half   — energies (beyond the 2M single block) at which an ordering first reaches the midpoint between ρ_off after the single block alone and P0's
             final ρ_off (the whole deck); the target is P0's, so every ordering chases the same number on a molecule;
  auc      — the mean ρ_off over the common n grid (linear interpolation on P0's checkpoints), i.e. the area under the curve; lower is better;
  n_half in-band Frobenius — the same construction on the in-band Frobenius error column.

Ratios are per molecule against P0, summarised by the median and the fraction improved, per evaluation set. Also prints how many molecules reach the
registered levels, so the primary read-out is reported whenever it exists.

    python readout.py out/sim/band_merged.json [out/sim/band_readout.md]"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def first_n_at(curve, col, level, M):
    for row in curve:
        if row[col] <= level:
            return int(row[0] - 2 * M)
    return None


def interp_at(curve, col, grid):
    n = np.array([r[0] for r in curve], float)
    v = np.array([r[col] for r in curve], float)
    return np.interp(grid, n, v)


def per_molecule(m: dict, names: list[str]) -> dict:
    M = m["M"]
    p0 = m["P0"]["curve"]
    out = {}
    for col, tag in ((2, "rho_off"), (5, "frob_inband")):
        start, final = p0[0][col], p0[-1][col]
        mid = 0.5 * (start + final)
        grid = np.array([r[0] for r in p0], float)
        base_auc = float(np.mean(interp_at(p0, col, grid)))
        base_half = first_n_at(p0, col, mid, M)
        for name in names:
            c = m[name]["curve"]
            n_half = first_n_at(c, col, mid, M)
            auc = float(np.mean(interp_at(c, col, grid)))
            out[(name, tag)] = dict(n_half=n_half, base_half=base_half, auc_ratio=auc / base_auc if base_auc > 0 else None,
                                    half_ratio=(n_half / max(base_half, 1)) if (n_half is not None and base_half is not None) else None)
        out[("P0", tag)] = dict(start=start, final=final)
    return out


def summarise(res: dict, names: list[str]) -> dict:
    summary = {}
    for split in ("eval_parents", "eval"):
        mols = {i: m for i, m in res["per_molecule"].items() if m["split"] == split}
        if not mols:
            continue
        tab = {"n_molecules": len(mols)}
        for key in ("K_off_0p3", "K_off_0p1", "n10_inband"):
            tab[f"P0_reaches_{key}"] = int(sum(m["P0"][key] is not None for m in mols.values()))
        pm = {i: per_molecule(m, names) for i, m in mols.items()}
        for tag in ("rho_off", "frob_inband"):
            tab[tag] = {}
            for name in names:
                hr = [v[(name, tag)]["half_ratio"] for v in pm.values() if v[(name, tag)]["half_ratio"] is not None]
                ar = [v[(name, tag)]["auc_ratio"] for v in pm.values() if v[(name, tag)]["auc_ratio"] is not None]
                tab[tag][name] = dict(n_half=len(hr),
                                      median_half_ratio=float(np.median(hr)) if hr else None,
                                      frac_half_improved=float(np.mean([h < 1 for h in hr])) if hr else None,
                                      median_auc_ratio=float(np.median(ar)) if ar else None,
                                      frac_auc_improved=float(np.mean([r < 1 for r in ar])) if ar else None)
            tab[tag]["P0_start_median"] = float(np.median([v[("P0", tag)]["start"] for v in pm.values()]))
            tab[tag]["P0_final_median"] = float(np.median([v[("P0", tag)]["final"] for v in pm.values()]))
        summary[split] = tab
    return summary


def main() -> int:
    src = Path(sys.argv[1])
    res = json.load(open(src, encoding="utf-8"))
    names = sorted({n for m in res["per_molecule"].values() for n in m if n.startswith(("P1", "P2", "P3"))})
    summary = summarise(res, names)
    lines = [f"# Read-out — {src.name} (pool {res['pool']}, {res.get('date', '')})", ""]
    for split, tab in summary.items():
        lines += [f"## {split}: {tab['n_molecules']} molecules; P0 reaches ρ_off ≤ 0.3 on {tab['P0_reaches_K_off_0p3']}, "
                  f"≤ 0.1 on {tab['P0_reaches_K_off_0p1']}, in-band Frobenius ≤ 10 % on {tab['P0_reaches_n10_inband']}", ""]
        for tag in ("rho_off", "frob_inband"):
            t = tab[tag]
            lines += [f"### {tag}: P0 median start {t['P0_start_median']:.3f} → final {t['P0_final_median']:.3f}", "",
                      "| ordering | n | median n_half ratio vs P0 | half improved | median AUC ratio vs P0 | AUC improved |", "|---|---|---|---|---|---|"]
            for name in names:
                v = t[name]
                f = lambda x, pct=False: "—" if x is None else (f"{100 * x:.0f} %" if pct else f"{x:.2f}")  # noqa: E731
                lines.append(f"| {name} | {v['n_half']} | {f(v['median_half_ratio'])} | {f(v['frac_half_improved'], True)} | "
                             f"{f(v['median_auc_ratio'])} | {f(v['frac_auc_improved'], True)} |")
            lines.append("")
    text = "\n".join(lines)
    print(text)
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(text, encoding="utf-8")
        json.dump(summary, open(str(Path(sys.argv[2])).replace(".md", ".json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
