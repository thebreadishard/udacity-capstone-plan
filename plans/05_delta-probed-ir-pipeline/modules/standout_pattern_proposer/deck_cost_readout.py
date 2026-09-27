"""Deck cost read-out (27 September 2026): what the band deck and the all-pairs candidate set cost and buy, from the merged simulation JSONs of E1 (band pool)
and E2 (all pairs). Per evaluation split, medians over molecules:

  whole-deck energies     — n_energies at the last checkpoint of P0 (the whole pool consumed), band and all pairs;
  whole-deck rho_off      — P0's final held-out rho_off on each pool;
  energies to rho_off 0.3 — K_off(0.3) beyond the single block on the all-pairs pool for P0, P12 (seed 0), the oracle; and as a fraction of the whole band deck.

Every number of the deck-design note of 27 September comes from here.

    python deck_cost_readout.py out/sim/band_p2_merged.json out/sim/all_p2_merged.json out/sim/deck_cost_2026-09-27.md"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

if hasattr(sys.stdout, "reconfigure"):   # not inside a notebook kernel
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def main() -> int:
    band = json.load(open(sys.argv[1], encoding="utf-8"))
    wide = json.load(open(sys.argv[2], encoding="utf-8"))
    out_md = Path(sys.argv[3]) if len(sys.argv) > 3 else None
    lines = [f"# Deck cost read-out — {Path(sys.argv[1]).name} (band) against {Path(sys.argv[2]).name} (all pairs); medians over molecules", ""]
    res = {}
    for split in ("eval_parents", "eval"):
        B = {i: m for i, m in band["per_molecule"].items() if m["split"] == split}
        W = {i: m for i, m in wide["per_molecule"].items() if m["split"] == split}
        common = sorted(set(B) & set(W))
        med = lambda xs: float(np.median(xs)) if len(xs) else None  # noqa: E731
        r = dict(n_molecules=len(common), median_M=med([W[i]["M"] for i in common]),
                 band_deck_energies=med([B[i]["P0"]["curve"][-1][0] for i in common]),
                 wide_pool_energies=med([W[i]["P0"]["curve"][-1][0] for i in common]),
                 band_deck_final_rho_off=med([B[i]["P0"]["curve"][-1][2] for i in common]),
                 wide_pool_final_rho_off=med([W[i]["P0"]["curve"][-1][2] for i in common]),
                 band_P0_reaches_0p3=int(sum(B[i]["P0"]["K_off_0p3"] is not None for i in common)),
                 wide_P0_reaches_0p3=int(sum(W[i]["P0"]["K_off_0p3"] is not None for i in common)))
        for name, key in (("P0", "P0"), ("P12", "P12_seed0"), ("P1", "P1_seed0"), ("oracle", "P3_oracle")):
            ks = [W[i][key]["K_off_0p3"] for i in common if W[i][key]["K_off_0p3"] is not None]
            r[f"wide_K_off_0p3_{name}"] = med(ks)
            r[f"wide_K_off_0p3_{name}_n"] = len(ks)
            r[f"wide_K_off_0p3_{name}_over_band_deck"] = (med(ks) / r["band_deck_energies"]) if ks else None
        res[split] = r
        lines += [f"## {split}: {r['n_molecules']} molecules, median M {r['median_M']:.0f}", "",
                  "| quantity | band deck | all-pairs candidate set |", "|---|---|---|",
                  f"| whole deck, energies (median) | {r['band_deck_energies']:.0f} | {r['wide_pool_energies']:.0f} ({r['wide_pool_energies'] / r['band_deck_energies']:.1f}×) |",
                  f"| whole deck, final held-out ρ_off (median) | {r['band_deck_final_rho_off']:.3f} | {r['wide_pool_final_rho_off']:.3f} |",
                  f"| molecules reaching ρ_off ≤ 0.3 with the hashed order | {r['band_P0_reaches_0p3']} | {r['wide_P0_reaches_0p3']} |", "",
                  "| energies beyond the single block to ρ_off 0.3, all-pairs set | median | n | as a multiple of the whole band deck |", "|---|---|---|---|"]
        for name in ("P0", "P1", "P12", "oracle"):
            k = r[f"wide_K_off_0p3_{name}"]
            lines.append(f"| {name} | {k:.0f} | {r[f'wide_K_off_0p3_{name}_n']} | {r[f'wide_K_off_0p3_{name}_over_band_deck']:.2f} |" if k is not None else f"| {name} | — | 0 | — |")
        lines.append("")
    text = "\n".join(lines)
    print(text)
    if out_md:
        out_md.write_text(text + "\n", encoding="utf-8")
        json.dump(res, open(str(out_md).replace(".md", ".json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
