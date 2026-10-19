"""S2b's registered read (GoalGathering/notes/PreRegistration_2026-10-19_S2b_Learning_Curve.md, 'Read'): does the learned anharmonic shift
reach line 2 (≤ 3.0 cm⁻¹ per family) once S2's scaffolds grow about four-fold, and if not, is it still learning?

    python s2b_read.py --sets <sets.json> --out <dir>

<sets.json> is a list of computed sets (S2, S2b), each {"name", "root", "selection", "gvpt2_dir", "xtb_root", "xtb_gvpt2_dir", "extra"}, read
as probes/s2_xtb_read.py reads one ("extra" maps an id to a G directory computed elsewhere: benzene's S1 G). The molecules of all sets are
read together, grouped by Murcko scaffold; an id in two sets is refused. A molecule without a report, a NOISY one, or one without an xtb force
field leaves the read and is named; a G mode without an xtb partner leaves it and is counted (S2 amendment 4).

Per scope ('no-large-amplitude' the main read, 'all' reported), on the same modes for every model:
  x0, x1, x2 as S2 amendment 4; the search's nested read over ridge, kernel ridge and the network on F1–F3 (s2_search.nested);
  the learning curve (s2_read.curve: k ∈ CURVE_KS and 'all', N_SUBSETS random subsets per k, the same subsets for every model) of (c), (b),
  x1 and x2* — kernel ridge on FX at the configuration the nested x2 read chose most often for the family (ties: the first in X2_GRID).
Per family: licensed when any read's rms at the full set (x0, (c), (b), x1 at 'all'; x2 and the search nested) is ≤ 3.0 cm⁻¹. Otherwise the
curve model with the lowest rms at 'all' is read: still learning when its rms at 'all' is below its rms at k = 16 by more than twice that
row's SE (with fewer than 17 training scaffolds, the largest k at most half of them is the reference, and named); then extrapolated
(a + b·k^(−c), s2_read.extrapolate) to the scaffolds needed. A fitted asymptote at or above the line, or a flat curve, reads 'flat: route A'.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from dataclasses import dataclass, field
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import FAMILIES, LINE_LICENSE, N_SUBSETS, ReadOptions, curve, extrapolate, fit_predict, load_selection, write_atomic  # noqa: E402
from s2_search import Config, configs, nested  # noqa: E402
from s2_xtb_read import MIN_OVERLAP, X2_GRID, build, config_predictor, load_modes, predict_x1, x0_read  # noqa: E402

CURVE_KS = (4, 6, 8, 12, 16, 24)
REF_K = 16
READ_SCOPES = ("no-large-amplitude", "all")
CURVE_MODELS = ("c", "b", "x1", "x2*")
SET_KEYS = ("name", "root", "selection", "gvpt2_dir", "xtb_root", "xtb_gvpt2_dir")


@dataclass(frozen=True)
class ComputedSet:
    """One computed set as s2_xtb_read.py reads it; every path is checked when the set is built."""
    name: str
    root: str
    selection: str
    gvpt2_dir: str
    xtb_root: str
    xtb_gvpt2_dir: str
    extra: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        missing = [p for p in (self.root, self.gvpt2_dir, self.xtb_root, self.xtb_gvpt2_dir, *self.extra.values()) if not os.path.isdir(p)]
        missing += [] if os.path.isfile(self.selection) else [self.selection]
        if missing:
            raise ValueError(f"set {self.name}: missing {missing}")


@dataclass(frozen=True)
class ReadPlan:
    """The registered read's settings; a test passes fewer subsets or a smaller search."""
    ks: tuple[int, ...] = CURVE_KS
    n_subsets: int = N_SUBSETS
    search_configs: tuple[Config, ...] = field(default_factory=lambda: tuple(configs()))

    def __post_init__(self) -> None:
        if REF_K not in self.ks or list(self.ks) != sorted(set(self.ks)):
            raise ValueError(f"ks {self.ks}: strictly increasing and containing the reference k = {REF_K}")


def read_sets(path: str) -> list[ComputedSet]:
    with open(path, encoding="utf-8") as fh:
        raw = json.load(fh)
    if not isinstance(raw, list) or not raw:
        raise ValueError(f"{path}: a non-empty list of sets")
    for entry in raw:
        unknown, absent = set(entry) - {*SET_KEYS, "extra"}, set(SET_KEYS) - set(entry)
        if unknown or absent:
            raise ValueError(f"{path}: set {entry.get('name')} has unknown keys {sorted(unknown)} and lacks {sorted(absent)}")
    sets = [ComputedSet(**entry) for entry in raw]
    names = [s.name for s in sets]
    if len(set(names)) != len(names):
        raise ValueError(f"{path}: set names repeat: {names}")
    return sets


def load_set(s: ComputedSet) -> dict[str, Any]:
    """A set's G molecules by scaffold (with the search's features), its xtb molecules by id, and both exclusion lists."""
    g_by_scaf, used, excluded_g = load_selection(s.root, s.selection, ReadOptions(setting="G", extra=s.extra, gvpt2_dir=s.gvpt2_dir, features=True))
    x_by_scaf, _, excluded_x = load_selection(s.xtb_root, s.selection, ReadOptions(setting="X", gvpt2_dir=s.xtb_gvpt2_dir))
    return {"g": g_by_scaf, "x": {m["id"]: m for ms in x_by_scaf.values() for m in ms}, "used": used,
            "excluded_g": excluded_g, "excluded_x": excluded_x}


def merge(parts: dict[str, dict[str, Any]]) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    """All sets' G molecules by scaffold and xtb molecules by id; an id in two sets is refused."""
    g_by_scaf: dict[str, list[dict]] = {}
    x_by_id: dict[str, dict] = {}
    seen: dict[str, str] = {}
    for name, part in parts.items():
        for scaf, mols in part["g"].items():
            for m in mols:
                if m["id"] in seen:
                    raise ValueError(f"{m['id']} is in set {seen[m['id']]} and in set {name}")
                seen[m["id"]] = name
                g_by_scaf.setdefault(scaf, []).append(m)
        x_by_id.update(part["x"])
    return g_by_scaf, x_by_id


def x2_choice(x2: dict[str, dict]) -> dict[str, Config]:
    """Per family, the X2_GRID configuration the nested x2 read chose most often (ties: the first in X2_GRID)."""
    out = {}
    for fa, v in x2.items():
        counts = Counter(v["chosen"])
        top = max(counts.values())
        out[fa] = next(c for c in X2_GRID if counts.get(c.name, 0) == top)
    return out


def family_rows(rows: dict[str, dict], slot: str, family: str) -> dict[str, dict]:
    """One family's curve of one slot ('b' or 'c') in s2_read.extrapolate's form (route key 'r'); 'all' carries the training count k."""
    out = {k: {"r": v["per_family"][family][slot], "r_se": v["per_family"][family][f"{slot}_se"]} for k, v in rows.items() if k != "all"}
    out["all"] = {"r": rows["all"]["per_family"][family][slot], "r_se": 0.0, "k": rows["all"]["k"]}
    return out


def curves(by_scaf: dict[str, list[dict]], choice: dict[str, Config], plan: ReadPlan) -> dict[str, dict[str, dict]]:
    """Per family and curve model, its curve rows (the same subsets for every model: each curve draws from default_rng(0) in one order)."""
    def run(predict):
        return curve(by_scaf, ks=plan.ks, n_subsets=plan.n_subsets, predict=predict)
    bc, x1 = run(fit_predict), run(predict_x1)
    x2 = {cfg.name: run(config_predictor(cfg)) for cfg in {c.name: c for c in choice.values()}.values()}
    out = {}
    for fa in FAMILIES:
        if not np.isfinite(bc["all"]["per_family"][fa]["c"]):
            continue
        out[fa] = {"c": family_rows(bc, "c", fa), "b": family_rows(bc, "b", fa), "x1": family_rows(x1, "b", fa)}
        if fa in choice:
            out[fa]["x2*"] = family_rows(x2[choice[fa].name], "b", fa)
    return out


def reference_k(rows: dict[str, dict]) -> int:
    """k = 16 when the curve has it; else the largest k at most half the training scaffolds (a step of at least two-fold)."""
    if str(REF_K) in rows:
        return REF_K
    half = [int(k) for k in rows if k != "all" and int(k) <= rows["all"]["k"] / 2]
    if not half:
        raise ValueError(f"{rows['all']['k']} training scaffolds: no k at most half of them, the curve cannot be read")
    return max(half)


def family_verdict(model_rows: dict[str, dict], full_set: dict[str, float]) -> dict[str, Any]:
    """The registration's per-family reading from the curve models' rows and every read's rms at the full set."""
    licensed = [name for name, v in full_set.items() if np.isfinite(v) and v <= LINE_LICENSE]
    finite = {m: r for m, r in model_rows.items() if np.isfinite(r["all"]["r"])}
    best = min(finite, key=lambda m: finite[m]["all"]["r"])
    rows = finite[best]
    ref = reference_k(rows)
    at_ref, at_all = rows[str(ref)], rows["all"]
    out: dict[str, Any] = {"licensed_by": licensed, "best_curve_model": best, "reference_k": ref, "rms_at_ref": at_ref["r"],
                           "se_at_ref": at_ref["r_se"], "rms_at_all": at_all["r"], "training_scaffolds": at_all["k"]}
    out["still_learning"] = bool(at_all["r"] < at_ref["r"] - 2 * at_ref["r_se"])
    if licensed:
        out["reading"] = f"licensed by {', '.join(licensed)} (≤ {LINE_LICENSE} cm⁻¹ at the full set)"
        return out
    if not out["still_learning"]:
        out["reading"] = f"line 2 missed, {best} flat from k = {ref} to all: route A for the large targets"
        return out
    ex = extrapolate(rows, "r")
    out["extrapolation"] = ex
    if ex["fit"] is None:
        out["reading"] = f"line 2 missed, {best} still learning but the fit a + b·k^(−c) failed: no size, named"
    elif ex["scaffolds_needed"] is None:
        out["reading"] = f"line 2 missed, {best} still descending to an asymptote ≥ {LINE_LICENSE} cm⁻¹: read as flat — route A"
    else:
        out["reading"] = f"line 2 missed, {best} still learning: ≈ {ex['scaffolds_needed']:.0f} training scaffolds to the line — sizes S2c"
    return out


def read_scope(by_scaf: dict[str, list[dict]], plan: ReadPlan) -> dict[str, Any]:
    """Every read of one scope's molecules and the per-family verdicts."""
    x0 = x0_read(by_scaf)
    x2 = nested(by_scaf, X2_GRID)
    search = nested(by_scaf, list(plan.search_configs))
    choice = x2_choice(x2)
    fam_curves = curves(by_scaf, choice, plan)
    verdicts = {}
    for fa, model_rows in fam_curves.items():
        full_set = {"x0": x0.get(fa, {}).get("rms", np.nan), **{m: r["all"]["r"] for m, r in model_rows.items() if m != "x2*"},
                    "x2": x2.get(fa, {}).get("rms", np.nan), "search": search.get(fa, {}).get("rms", np.nan)}
        verdicts[fa] = {"full_set": full_set, **family_verdict(model_rows, full_set)}
    return {"x0": x0, "x2": x2, "search": search, "x2_choice": {fa: c.name for fa, c in choice.items()}, "curves": fam_curves,
            "verdicts": verdicts}


def report(res: dict[str, Any]) -> list[str]:
    lines = [f"# S2b read — {res['molecules']} molecules in {res['scaffolds']} scaffolds, line 2 ≤ {LINE_LICENSE} cm⁻¹ per family", ""]
    for scope, r in res["scopes"].items():
        lines += [f"## Scope {scope}{' (main read)' if scope == READ_SCOPES[0] else ''}", "",
                  f"Molecules without an xtb force field: {len(r['counts']['molecules_without_xtb'])}; G window modes without an xtb partner "
                  f"(overlap < {MIN_OVERLAP}): {r['counts']['window_modes_without_partner']}.", "",
                  "| family | x0 | (c) | (b) | x1 | x2 nested | search nested | best curve model: k → rms | reading |", "|---|---|---|---|---|---|---|---|---|"]
        for fa, v in r["read"]["verdicts"].items():
            fs = v["full_set"]
            rows = r["read"]["curves"][fa][v["best_curve_model"]]
            path = ", ".join(f"{k} {rows[k]['r']:.2f}" for k in rows if k != "all") + f", all ({rows['all']['k']}) {rows['all']['r']:.2f}"
            cells = " | ".join(f"{fs[m]:.2f}" if np.isfinite(fs[m]) else "—" for m in ("x0", "c", "b", "x1", "x2", "search"))
            lines.append(f"| {fa} | {cells} | {v['best_curve_model']}: {path} | {v['reading']} |")
        lines.append("")
    lines += [f"- excluded {i}: {w}" for i, w in res["excluded"].items()]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--sets", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    plan = ReadPlan()
    parts = {s.name: load_set(s) for s in read_sets(a.sets)}
    g_by_scaf, x_by_id = merge(parts)
    dirs = {m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id}
    modes = load_modes(dirs)
    excluded = {i: f"{name}: {w}" for name, p in parts.items() for i, w in {**p["excluded_g"], **p["excluded_x"]}.items()}
    res: dict[str, Any] = {"registration": "PreRegistration_2026-10-19_S2b_Learning_Curve.md", "sets": list(parts),
                           "molecules": sum(len(p["used"]) for p in parts.values()), "scaffolds": len(g_by_scaf), "excluded": excluded, "scopes": {}}
    for scope in READ_SCOPES:
        by_scaf, counts = build(g_by_scaf, x_by_id, modes, scope)
        if len(by_scaf) < 2:
            raise SystemExit(f"scope {scope}: {len(by_scaf)} scaffold(s) with xtb partners — no leave-one-scaffold-out read")
        res["scopes"][scope] = {"counts": counts, "scaffolds": len(by_scaf), "read": read_scope(by_scaf, plan)}
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s2b_read.json"), json.dumps(res, indent=1, default=float))
    lines = report(res)
    write_atomic(os.path.join(a.out, "s2b_read.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
