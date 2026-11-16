"""Q2 of TASKS 211: does the mark of the xtb force field alone catch what the mark of the B3LYP (G) label catches?

    python marks.py

Every molecule of labels_domain_2026-11-13 (S2, S2b and S3's two targets) is loaded through the reads' own loader. Per G mode:
the G mark (the label's vpt2_domain), the xtb mark (the matched xtb mode's vpt2_domain, as s2_xtb_read.attach_xtb carries it), the
strain and the partner share on both sides, and x2*'s prediction when the step is applied whatever the marks say (fitted on the
other scaffolds' unmarked modes; for a target, on all training molecules, as S3 does). Writes marks.json beside itself.

The partner share printed for unmarked modes comes from qff_report.npz's chi_sym (dpir.qff's DVPT2), not from the GVPT2 call the
label was marked with; `share_check` says how often the two agree on the mark.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "src"))
from s2_read import FAMILIES, WINDOWS, apply_marked_policy, apply_scope, concat, in_window, rms, write_atomic  # noqa: E402
from s2_xtb_read import attach_xtb, load_modes, match_modes  # noqa: E402
from s2b_read import load_set, merge, read_sets  # noqa: E402
from s3_read import MAIN_SCOPE, predictors  # noqa: E402

from dpir.vpt2_domain import PARTNER_MAX, STRAIN_MAX  # noqa: E402

LABELS = "probes/results_m1/labels_domain_2026-11-13"
SETS, TARGETS = f"{LABELS}/sets.json", f"{LABELS}/S3_targets/targets.json"
S2B_READS = {"mid": "probes/results_m1/labels_symmetry_2026-11-12/s2b_read/s2b_read.json"}
ROUTE_RULE_CH = f"{LABELS}/route_rule/route_rule_ch.json"
CELLS = ("both", "G only", "xtb only", "neither")
THRESHOLDS = (0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02)
PER_MODE = ("omega", "delta", "family", "h", "o", "xtb", "g_mark", "x_mark", "g_strain", "g_share", "x_strain", "x_share",
            "xtb_overlap", "mode", "large_amplitude", "no_xtb", "vpt2_marked")


def diagnostics(directory: str, nu_minus_omega: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """A force field's per-mode strain (from the label's shift) and partner share (from its report's chi_sym)."""
    with np.load(os.path.join(directory, "qff_report.npz")) as z:
        omega, chi = np.asarray(z["omega_cm"], float), np.asarray(z["chi_sym"], float)
    off = np.abs(chi - np.diag(np.diag(chi)))
    return np.abs(nu_minus_omega) / omega, off.max(axis=1) / omega


def molecule_table(g: dict, x: dict, q_g: np.ndarray, q_x: np.ndarray) -> dict:
    """One molecule's G modes with both marks and both sides' diagnostics, before any scope or window is applied."""
    partner, _ = match_modes(q_g, q_x)
    has, at = partner >= 0, np.maximum(partner, 0)
    rec = attach_xtb(g, x, q_g, q_x)
    g_strain, g_share = diagnostics(g["dir"], g["delta"])
    x_strain, x_share = diagnostics(x["dir"], x["delta"])
    rec.update({"g_mark": g["vpt2_marked"].copy(), "x_mark": has & x["vpt2_marked"][at], "g_strain": g_strain, "g_share": g_share,
                "x_strain": np.where(has, x_strain[at], np.nan), "x_share": np.where(has, x_share[at], np.nan),
                "x_own_mark": x["vpt2_marked"], "x_own_strain": x_strain, "x_own_share": x_share,
                "x_own_delta": x["delta"], "x_dir": x["dir"],
                "mode": np.arange(len(g["omega"]))})
    return rec


def load_tables(sets_path: str) -> dict[str, list[dict]]:
    """Every molecule of a sets file, by scaffold, as `molecule_table` builds it."""
    parts = {s.name: load_set(s) for s in read_sets(sets_path)}
    g_by_scaf, x_by_id = merge(parts)
    dirs = {m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id}
    modes = load_modes(dirs)
    return {scaf: [molecule_table(m, x_by_id[m["id"]], *modes[m["id"]]) for m in ms if m["id"] in x_by_id]
            for scaf, ms in g_by_scaf.items()}


def scoped(rec: dict) -> dict:
    """The molecule in the reads' main scope with only the modes that have an xtb partner, as s2_xtb_read.build leaves it."""
    if MAIN_SCOPE != "all":
        rec = apply_scope(rec, "large_amplitude")
    return apply_scope(rec, "no_xtb")


def x2_choices() -> dict[str, dict[str, str]]:
    """Per window, S2b's x2 configuration per family, from the reads the route rule names."""
    with open(ROUTE_RULE_CH, encoding="utf-8") as fh:
        reads = {**S2B_READS, "ch": json.load(fh)["s2b_read"]}
    out = {}
    for name, path in reads.items():
        with open(path, encoding="utf-8") as fh:
            out[name] = json.load(fh)["scopes"][MAIN_SCOPE]["read"]["x2_choice"]
    return out


def predict_kept(train_mols: list[dict], test: dict, choice: dict[str, str], window: tuple[float, float]) -> np.ndarray:
    """x2*'s shift for every window mode of `test` (marked ones too), fitted on the unmarked window modes of `train_mols`."""
    train = concat([apply_marked_policy(m, "exclude", m["id"])[0] for m in train_mols], window)
    table = concat([test], window)
    pred = np.full(len(table["omega"]), np.nan)
    for fa in FAMILIES:
        sel = table["family"] == fa
        if sel.any() and fa in choice and (train["family"] == fa).any():
            pred[sel] = predictors(choice[fa])["x2*"](train, table)[sel]
    return pred


def window_rows(rec: dict, pred: np.ndarray, window: tuple[float, float], window_name: str) -> list[dict]:
    """One row per window mode of a scoped molecule: its marks, diagnostics, label shift and the model's shift."""
    w = in_window(rec["omega"], window)
    cols = {k: rec[k][w] for k in PER_MODE}
    return [{"id": rec["id"], "window": window_name, "pred": float(pred[i]),
             **{k: (v[i].item() if hasattr(v[i], "item") else v[i]) for k, v in cols.items()}} for i in range(int(w.sum()))]


def all_rows(train: dict[str, list[dict]], targets: dict[str, list[dict]]) -> list[dict]:
    """Every window mode of every molecule with the step applied whatever its marks: leave one scaffold out, targets on all."""
    choices, rows = x2_choices(), []
    everything = [scoped(m) for ms in train.values() for m in ms]
    for name, choice in choices.items():
        window = WINDOWS[name]
        for scaf, mols in train.items():
            others = [scoped(m) for s, ms in train.items() if s != scaf for m in ms]
            for m in mols:
                rows += window_rows(scoped(m), predict_kept(others, scoped(m), choice, window), window, name)
        for mols in targets.values():
            for m in mols:
                rows += window_rows(scoped(m), predict_kept(everything, scoped(m), choice, window), window, name)
    return rows


def cell(g_mark: bool, x_mark: bool) -> str:
    """The confusion cell of one mode."""
    return CELLS[(0 if x_mark else 1) if g_mark else (2 if x_mark else 3)]


def confusion(recs: list[dict]) -> dict[str, dict[str, int]]:
    """All G modes of all molecules, unscoped and unwindowed, per family and in all: the four cells and the modes without a partner."""
    out = {fa: dict.fromkeys((*CELLS, "G marked, no xtb partner", "no xtb partner"), 0) for fa in (*FAMILIES, "all")}
    for r in recs:
        for fa, g, x, lone in zip(r["family"], r["g_mark"], r["x_mark"], r["no_xtb"], strict=True):
            for key in (fa, "all"):
                out[key][cell(bool(g), bool(x))] += 1
                out[key]["no xtb partner"] += int(lone)
                out[key]["G marked, no xtb partner"] += int(lone and g)
    return out


def costs(rows: list[dict]) -> dict[str, dict]:
    """Per window family and cell: n, the rms of the label's shift (the harmonic position's error against the label) and the rms of
    model minus label (the step's error against the label) on the same modes."""
    out: dict[str, dict] = {}
    for fa in (*FAMILIES, "all"):
        for c in CELLS:
            sel = [r for r in rows if (fa == "all" or r["family"] == fa) and cell(r["g_mark"], r["x_mark"]) == c
                   and np.isfinite(r["pred"])]
            if sel:
                d, p = np.array([r["delta"] for r in sel]), np.array([r["pred"] for r in sel])
                out.setdefault(fa, {})[c] = {"n": len(sel), "harmonic_rms": rms(d), "step_rms": rms(p - d),
                                             "mean_label_shift": float(d.mean()), "mean_model_shift": float(p.mean())}
    return out


def threshold_scan(recs: list[dict]) -> list[dict]:
    """An xtb-only rule at lower thresholds: of the G-marked modes with a partner how many it catches, and how many unmarked it marks."""
    g = np.concatenate([r["g_mark"][~r["no_xtb"]] for r in recs])
    strain = np.concatenate([r["x_strain"][~r["no_xtb"]] for r in recs])
    share = np.concatenate([r["x_share"][~r["no_xtb"]] for r in recs])
    out = []
    for t in THRESHOLDS:
        flag = (strain > t) | (share > t)
        out.append({"threshold": t, "g_marked": int(g.sum()), "caught": int((flag & g).sum()),
                    "false_marks": int((flag & ~g).sum()), "unmarked": int((~g).sum())})
    return out


def share_check(recs: list[dict]) -> dict[str, int]:
    """How well strain and the report's chi_sym reproduce the stored marks, per side (the stored marks used the GVPT2 call's chi)."""
    out = {}
    for side, mark, strain, share in (("G", "g_mark", "g_strain", "g_share"), ("xtb", "x_own_mark", "x_own_strain", "x_own_share")):
        stored = np.concatenate([r[mark] for r in recs])
        mine = np.concatenate([(r[strain] > STRAIN_MAX) | (r[share] > PARTNER_MAX) for r in recs])
        out[side] = {"stored": int(stored.sum()), "recomputed": int(mine.sum()), "agree_marked": int((stored & mine).sum())}
    return out


def marked_list(recs: list[dict]) -> list[dict]:
    """Every mode either side marks, with both sides' numbers."""
    keys = ("mode", "omega", "family", "o", "delta", "xtb", "g_mark", "x_mark", "g_strain", "g_share", "x_strain", "x_share",
            "xtb_overlap", "large_amplitude", "no_xtb")
    out = []
    for r in recs:
        for i in np.flatnonzero(r["g_mark"] | r["x_mark"]):
            out.append({"id": r["id"], **{k: (r[k][i].item() if hasattr(r[k][i], "item") else r[k][i]) for k in keys}})
    return out


def main() -> int:
    """Run the read and print its tables."""
    os.chdir(PLAN)
    train, targets = load_tables(SETS), load_tables(TARGETS)
    recs = [m for ms in (*train.values(), *targets.values()) for m in ms]
    rows = all_rows(train, targets)
    res = {"molecules": len(recs), "modes": int(sum(len(r["omega"]) for r in recs)), "confusion_all_modes": confusion(recs),
           "share_check": share_check(recs), "threshold_scan": threshold_scan(recs), "marked_modes": marked_list(recs),
           "costs_window_modes": costs(rows), "rows": rows}
    write_atomic(os.path.join(HERE, "marks.json"), json.dumps(res, indent=1, default=float))
    print(res["molecules"], "molecules", res["modes"], "modes;", "share check", res["share_check"])
    for fa, c in res["confusion_all_modes"].items():
        print("confusion", fa, c)
    for t in res["threshold_scan"]:
        print("scan", t)
    for m in res["marked_modes"]:
        print("marked", {k: (round(v, 3) if isinstance(v, float) else v) for k, v in m.items()})
    for fa, c in res["costs_window_modes"].items():
        for name, v in c.items():
            print("cost", fa, name, {k: (round(x, 2) if isinstance(x, float) else x) for k, x in v.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
