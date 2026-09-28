#!/usr/bin/env python
"""W1 / W2 of the wide-deck pre-registration (27 Sep 2026, amendment 28 Sep): the stop rule applied to recorded recovery curves.

    python stop_rule_readout.py <wide sim json> <band sim json> <out_prefix> [--tau 0.3] [--bmax-factor 2] [--orders P0,P12,P3_oracle]
                                [--seeds 0,1,2] [--false-stop 0.4] [--label "..."]

Per molecule: the whole band deck = the band record's P0 curve total energies (single block included); B_max = factor × that, spent beyond the block;
the stop rule (`pp.core.stop_rule`: two consecutive checkpoints with held-out ρ_off ≤ τ, or the budget) on every requested ordering; for a seeded
ordering (P12) the seed median of the cost over the seeds that stopped, defined when at least two of three did. W1: stopped within B_max on ≥ 90 % of
molecules and median cost ≤ 1.5 × the whole band deck (ratio of medians, as `deck_cost_readout.py`). W2: false stops (truth-based frob_off > 0.4 at the
stop) on ≤ 5 % of the stopped molecules. Judged on all evaluation molecules; the two splits are shown beside."""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PLAN / "src"))
from pp import core as C  # noqa: E402

from dpir.provenance import provenance  # noqa: E402

W1_FRAC, W1_RATIO, W2_FRAC = 0.90, 1.5, 0.05


def molecule_stops(m: dict, band_deck: int, tau: float, bmax_factor: float, orders: list[str], seeds: list[int], false_stop: float) -> dict:
    """The stop-rule read of one molecule's record `m` (per_molecule entry: split, M, <ordering>: {curve, ...})."""
    M = m["M"]
    b_max = int(round(bmax_factor * band_deck))
    out = dict(M=M, band_deck=band_deck, b_max=b_max, orderings={})
    for name in orders:
        keys = [f"{name}_seed{s}" for s in seeds if f"{name}_seed{s}" in m] or ([name] if name in m else [])
        if not keys:
            continue
        per_seed = {k: C.stop_rule(m[k]["curve"], tau=tau, b_max=b_max, M=M) for k in keys}
        stopped = [r for r in per_seed.values() if r["stopped"]]
        defined = len(stopped) >= (2 if len(keys) >= 3 else 1)
        cost = statistics.median([r["cost"] for r in stopped]) if defined else None
        frob = statistics.median([r["frob_off"] for r in stopped]) if defined else None
        first = [C.k_off_at(m[k]["curve"], tau, M) for k in keys]
        first = [f for f in first if f is not None]
        out["orderings"][name] = dict(stopped=defined, cost=cost, cost_over_band_deck=(cost / band_deck) if cost is not None else None,
                                      frob_off_at_stop=frob, false_stop=(frob is not None and frob > false_stop),
                                      hysteresis=(cost - statistics.median(first)) if (cost is not None and first) else None,
                                      seeds={k: dict(stopped=r["stopped"], reason=r["reason"], cost=r["cost"], frob_off=round(r["frob_off"], 4)) for k, r in per_seed.items()})
    return out


def read(wide: dict, band: dict, tau: float, bmax_factor: float, orders: list[str], seeds: list[int], false_stop: float) -> dict:
    W, B = wide["per_molecule"], band["per_molecule"]
    common = sorted(set(W) & set(B))
    per_mol = {i: dict(split=W[i]["split"], **molecule_stops(W[i], int(B[i]["P0"]["curve"][-1][0]), tau, bmax_factor, orders, seeds, false_stop)) for i in common}
    summary = {}
    for split in ("all", "eval_parents", "eval"):
        ids = [i for i in common if split == "all" or per_mol[i]["split"] == split]
        if not ids:
            continue
        med_band = statistics.median([per_mol[i]["band_deck"] for i in ids])
        tab = dict(n_molecules=len(ids), median_band_deck=med_band, median_M=statistics.median([per_mol[i]["M"] for i in ids]))
        for name in orders:
            rs = [per_mol[i]["orderings"][name] for i in ids if name in per_mol[i]["orderings"]]
            st = [r for r in rs if r["stopped"]]
            costs = [r["cost"] for r in st]
            med_cost = statistics.median(costs) if costs else None
            tab[name] = dict(n=len(rs), n_stopped=len(st), frac_stopped=(len(st) / len(rs)) if rs else None, median_cost=med_cost,
                             cost_ratio_of_medians=(med_cost / med_band) if med_cost is not None else None,
                             median_per_molecule_ratio=statistics.median([r["cost_over_band_deck"] for r in st]) if st else None,
                             n_false_stops=sum(r["false_stop"] for r in st), frac_false_stops=(sum(r["false_stop"] for r in st) / len(st)) if st else None,
                             median_hysteresis=statistics.median([r["hysteresis"] for r in st if r["hysteresis"] is not None]) if any(r["hysteresis"] is not None for r in st) else None)
        summary[split] = tab
    return dict(per_molecule=per_mol, summary=summary)


def judge(summary: dict, order: str) -> dict:
    t = summary["all"][order]
    w1 = t["frac_stopped"] is not None and t["frac_stopped"] >= W1_FRAC and t["cost_ratio_of_medians"] is not None and t["cost_ratio_of_medians"] <= W1_RATIO
    w2 = t["frac_false_stops"] is not None and t["frac_false_stops"] <= W2_FRAC
    return dict(order=order, W1_pass=bool(w1), W2_pass=bool(w2), frac_stopped=t["frac_stopped"], cost_ratio_of_medians=t["cost_ratio_of_medians"], frac_false_stops=t["frac_false_stops"])


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("wide"); ap.add_argument("band"); ap.add_argument("out_prefix")
    ap.add_argument("--tau", type=float, default=0.3); ap.add_argument("--bmax-factor", type=float, default=2.0)
    ap.add_argument("--orders", default="P0,P12,P3_oracle"); ap.add_argument("--seeds", default="0,1,2"); ap.add_argument("--false-stop", type=float, default=0.4)
    ap.add_argument("--judge", default="P12", help="the ordering the W1/W2 lines are judged on")
    ap.add_argument("--label", default="", help="free text for the heading (e.g. the solver prior of the wide record)")
    a = ap.parse_args(argv)
    wide, band = json.load(open(a.wide, encoding="utf-8")), json.load(open(a.band, encoding="utf-8"))
    orders, seeds = a.orders.split(","), [int(s) for s in a.seeds.split(",")]
    res = read(wide, band, a.tau, a.bmax_factor, orders, seeds, a.false_stop)
    J = judge(res["summary"], a.judge)
    rec = dict(date=time.strftime("%Y-%m-%d %H:%M"), wide=str(a.wide), band=str(a.band), wide_w_cm=wide.get("w_cm", C.W_BAND_CM), wide_embed=wide.get("embed_prefix"),
               tau=a.tau, bmax_factor=a.bmax_factor, false_stop=a.false_stop, orders=orders, seeds=seeds, label=a.label, judged=J, summary=res["summary"],
               per_molecule=res["per_molecule"], provenance=provenance())
    out = Path(a.out_prefix); out.parent.mkdir(parents=True, exist_ok=True)
    json.dump(rec, open(str(out) + ".json", "w", encoding="utf-8"), indent=1)
    f2 = lambda x: "—" if x is None else f"{x:.2f}"  # noqa: E731
    pc = lambda x: "—" if x is None else f"{100 * x:.0f} %"  # noqa: E731
    L = [f"# Stop-rule read-out — {Path(a.wide).name} (solver prior w {rec['wide_w_cm']:g} cm⁻¹) against {Path(a.band).name}; {rec['date']}" + (f" — {a.label}" if a.label else ""), "",
         f"τ_stop {a.tau}, B_max = {a.bmax_factor:g} × whole band deck, false stop = frob_off > {a.false_stop} at the stop; seeds {seeds}; W1/W2 judged on {a.judge}.", ""]
    for split, tab in res["summary"].items():
        L += [f"## {split}: {tab['n_molecules']} molecules, median M {tab['median_M']:.0f}, median whole band deck {tab['median_band_deck']:.0f} energies", "",
              "| ordering | stopped within B_max | median cost beyond block | ratio of medians vs band deck | median per-molecule ratio | false stops | median hysteresis |",
              "|---|---|---|---|---|---|---|"]
        for name in orders:
            if name not in tab:
                continue
            t = tab[name]
            L.append(f"| {name} | {t['n_stopped']} / {t['n']} ({pc(t['frac_stopped'])}) | {'—' if t['median_cost'] is None else format(t['median_cost'], '.0f')} | "
                     f"{f2(t['cost_ratio_of_medians'])} | {f2(t['median_per_molecule_ratio'])} | {t['n_false_stops']} ({pc(t['frac_false_stops'])}) | "
                     f"{'—' if t['median_hysteresis'] is None else format(t['median_hysteresis'], '.0f')} |")
        L.append("")
    L += [f"**W1** ({a.judge}: stopped on ≥ {100 * W1_FRAC:.0f} % and ratio of medians ≤ {W1_RATIO}): {'pass' if J['W1_pass'] else 'FAIL'} "
          f"({pc(J['frac_stopped'])}, {f2(J['cost_ratio_of_medians'])}×). **W2** (false stops ≤ {100 * W2_FRAC:.0f} %): {'pass' if J['W2_pass'] else 'FAIL'} ({pc(J['frac_false_stops'])}).", ""]
    Path(str(out) + ".md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L)); print("written", str(out) + ".json / .md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
