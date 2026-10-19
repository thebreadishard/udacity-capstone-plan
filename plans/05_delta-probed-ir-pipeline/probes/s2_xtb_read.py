"""S2 amendment 4's reads (registered 18 Oct 2026, 14:5x, before any xtb number): GFN2-xTB's own anharmonic shift as an input for the
B3LYP (G) GVPT2 labels.

    python s2_xtb_read.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] --gvpt2-dir <G labels> \
        --xtb-root <xtb root> --xtb-gvpt2-dir <X labels> --out <dir>

Per molecule the xtb normal modes are matched to the G modes by squared eigenvector overlap (Hungarian, as S1's comparison); a G mode
whose matched overlap is below MIN_OVERLAP has no xtb partner and leaves the xtb reads (counted). A molecule without an xtb force field,
or a NOISY one, leaves them too (counted). Both scopes are read ('all', 'no-large-amplitude'), both reported:
  (x0) Δ_xtb itself as the prediction, no fit; with the per-family Pearson r between Δ_xtb and Δ_G (the registered prediction: r ≥ 0.7 in
       ring-ip and CH-oop) and route (c) on the same modes for comparison;
  (x1) ridge in route (b)'s form plus per-family slopes on Δ_xtb (s2_search feature set FX), with amendment 1's learning curve and
       verdict rules (the 'b' slot of s2_read.curve);
  (x2) kernel ridge on F1 + Δ_xtb over the search's grid, chosen per family on inner folds (s2_search.nested).
Line 2: ≤ 3.0 cm⁻¹ per family. The labels are GVPT2 on both sides (probes/gvpt2_labels.py, Martin K 1, the same solver).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import (  # noqa: E402
    FAMILIES,
    LINE_LICENSE,
    WINDOW,
    XTB_KEY,
    ReadOptions,
    apply_scope,
    curve,
    fit_predict,
    load_selection,
    rms,
    verdict,
    write_atomic,
)
from s2_search import KRR_ALPHA, KRR_GAMMA, XTB_FEATURES, Config, nested  # noqa: E402
from s2_search import fit_predict as search_fit_predict  # noqa: E402

MIN_OVERLAP = 0.5           # amendment 4: a G mode whose matched xtb mode overlaps less has no partner
READ_SCOPES = ("all", "no-large-amplitude")
X1 = Config("ridge", XTB_FEATURES)
X2_GRID = [Config("krr", XTB_FEATURES, a, g) for a in KRR_ALPHA for g in KRR_GAMMA]


def match_modes(q_g: np.ndarray, q_x: np.ndarray, min_overlap: float = MIN_OVERLAP) -> tuple[np.ndarray, np.ndarray]:
    """Per G mode (columns of q_g, mass-weighted 3N × M), the index of its xtb partner among q_x's columns (−1 when the matched squared
    overlap is below min_overlap) and that overlap."""
    if q_g.shape != q_x.shape:
        raise ValueError(f"mode arrays differ in shape: {q_g.shape} against {q_x.shape}")
    ov = (q_g.T @ q_x) ** 2
    rows, cols = linear_sum_assignment(-ov)
    partner = np.full(q_g.shape[1], -1)
    best = np.zeros(q_g.shape[1])
    best[rows] = ov[rows, cols]
    partner[rows] = np.where(ov[rows, cols] >= min_overlap, cols, -1)
    return partner, best


def attach_xtb(rec_g: dict, rec_x: dict, q_g: np.ndarray, q_x: np.ndarray) -> dict:
    """The G molecule with its per-mode Δ_xtb (nan where no partner) and the boolean 'no_xtb'."""
    partner, overlap = match_modes(q_g, q_x)
    xtb = np.where(partner >= 0, np.asarray(rec_x["delta"])[np.maximum(partner, 0)], np.nan)
    return {**rec_g, XTB_KEY: xtb, "no_xtb": partner < 0, "xtb_overlap": overlap}


def window(rec: dict) -> np.ndarray:
    return (rec["omega"] >= WINDOW[0]) & (rec["omega"] <= WINDOW[1])


def predict_x1(train: dict, test: dict) -> tuple[np.ndarray, np.ndarray, int]:
    """x1 in s2_read.curve's 'b' slot: the FX ridge; route (c) and the unseen-family count as route (b) has them (an unseen family's
    modes get the training mean, as route (b) does)."""
    _, pc, unseen = fit_predict(train, test)
    p, _ = search_fit_predict(X1, train, test, None)
    seen = np.isin(test["family"], np.unique(train["family"]))
    p[~seen] = train["delta"].mean()
    return p, pc, unseen


def x0_read(by_scaf: dict) -> dict:
    """Δ_xtb as the prediction, per family over the window modes: rms, Pearson r, and route (c)'s leave-one-scaffold-out rms on the same modes."""
    from s2_read import loso
    t, _, c, f, _ = loso(by_scaf)
    mols = [m for ms in by_scaf.values() for m in ms]
    truth = np.concatenate([m["delta"][window(m)] for m in mols])
    pred = np.concatenate([m[XTB_KEY][window(m)] for m in mols])
    fam = np.concatenate([m["family"][window(m)] for m in mols])
    out = {}
    for fa in FAMILIES:
        sel = fam == fa
        if not sel.any():
            continue
        r = float(np.corrcoef(pred[sel], truth[sel])[0, 1]) if sel.sum() > 2 and np.std(pred[sel]) > 0 and np.std(truth[sel]) > 0 else float("nan")
        out[fa] = {"n": int(sel.sum()), "rms": rms(pred[sel] - truth[sel]), "pearson_r": r, "c_rms": rms((c - t)[f == fa]),
                   "licensed": bool(rms(pred[sel] - truth[sel]) <= LINE_LICENSE)}
    return out


def build(g_by_scaf: dict, x_by_id: dict, modes: dict, scope: str) -> tuple[dict, dict]:
    """The scoped G molecules that have an xtb force field, with Δ_xtb; modes without an xtb partner dropped. Returns (by scaffold, counts)."""
    counts = {"molecules_without_xtb": [], "modes_without_partner": 0, "window_modes_without_partner": 0}
    out = {}
    for scaf, mols in g_by_scaf.items():
        for m in mols:
            if m["id"] not in x_by_id:
                counts["molecules_without_xtb"].append(m["id"])
                continue
            q_g, q_x = modes[m["id"]]
            rec = attach_xtb(m, x_by_id[m["id"]], q_g, q_x)
            if scope != "all":
                rec = apply_scope(rec, "large_amplitude")
            counts["modes_without_partner"] += int(rec["no_xtb"].sum())
            counts["window_modes_without_partner"] += int((rec["no_xtb"] & window(rec)).sum())
            rec = apply_scope(rec, "no_xtb")
            out.setdefault(scaf, []).append(rec)
    return out, counts


def read_scope(by_scaf: dict) -> dict:
    """x0, x1 (curve and verdict) and x2 (nested) on one scope's molecules."""
    rows = curve(by_scaf, predict=predict_x1)
    x1_family = {fa: {**v, "licensed": bool(v["b"] <= LINE_LICENSE)} for fa, v in rows["all"]["per_family"].items()}
    return {"x0": x0_read(by_scaf), "x1": {"curve": rows, "verdict": verdict(rows), "per_family": x1_family}, "x2": nested(by_scaf, X2_GRID)}


def load_modes(ids_dirs: dict) -> dict:
    """Mass-weighted normal modes of each molecule's ref.json (dpir.qff's own order), per id: (q_G, q_X)."""
    from s1_anharmonic_level import harmonic_modes
    return {i: (harmonic_modes(os.path.join(g, "ref.json"))[1], harmonic_modes(os.path.join(x, "ref.json"))[1]) for i, (g, x) in ids_dirs.items()}


def report(res: dict) -> list[str]:
    lines = [f"# S2 amendment 4 — GFN2-xTB as input ({res['molecules_g']} G molecules; GVPT2 labels both sides; line 2 ≤ {LINE_LICENSE} cm⁻¹)", ""]
    for scope, r in res["scopes"].items():
        c = r["counts"]
        lines += [f"## Scope {scope}", "", f"Without an xtb force field: {len(c['molecules_without_xtb'])}; G window modes without an xtb partner "
                  f"(overlap < {MIN_OVERLAP}): {c['window_modes_without_partner']}.", "",
                  "| family | modes | (x0) Δ_xtb rms | Pearson r | (c) rms | (x1) rms | (x2) nested rms | licensed (x0/x1/x2) |",
                  "|---|---|---|---|---|---|---|---|"]
        for fa in FAMILIES:
            x0, x1, x2 = r["read"]["x0"].get(fa), r["read"]["x1"]["per_family"].get(fa), r["read"]["x2"].get(fa)
            if x0 is None:
                continue
            lic = "/".join("yes" if v and v.get("licensed") else "no" for v in (x0, x1, x2))
            x2_cell = f"{x2['rms']:.2f}" if x2 else "—"
            lines.append(f"| {fa} | {x0['n']} | {x0['rms']:.2f} | {x0['pearson_r']:.2f} | {x0['c_rms']:.2f} | {x1['b']:.2f} | {x2_cell} | {lic} |")
        lines += ["", f"(x1) curve verdict: {r['read']['x1']['verdict']['reading']}", ""]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("root")
    ap.add_argument("--selection", required=True)
    ap.add_argument("--extra", nargs="*", default=[])
    ap.add_argument("--gvpt2-dir", required=True)
    ap.add_argument("--xtb-root", required=True)
    ap.add_argument("--xtb-gvpt2-dir", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    extra = dict(e.split("=", 1) for e in a.extra)
    g_by_scaf, used_g, excluded_g = load_selection(a.root, a.selection, ReadOptions(setting="G", extra=extra, gvpt2_dir=a.gvpt2_dir))
    x_by_scaf, _used_x, excluded_x = load_selection(a.xtb_root, a.selection, ReadOptions(setting="X", gvpt2_dir=a.xtb_gvpt2_dir))
    x_by_id = {m["id"]: m for ms in x_by_scaf.values() for m in ms}
    dirs = {m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id}
    modes = load_modes(dirs)
    res = {"registration": "PreRegistration_2026-10-14_S2_Anharmonic_Shift.md, amendment 4", "min_overlap": MIN_OVERLAP,
           "molecules_g": len(used_g), "excluded_g": excluded_g, "excluded_xtb": excluded_x, "scopes": {}}
    for scope in READ_SCOPES:
        by_scaf, counts = build(g_by_scaf, x_by_id, modes, scope)
        if len(by_scaf) < 2:
            raise SystemExit(f"scope {scope}: {len(by_scaf)} scaffold(s) with xtb partners — no leave-one-scaffold-out read")
        res["scopes"][scope] = {"counts": counts, "scaffolds": len(by_scaf), "read": read_scope(by_scaf)}
    os.makedirs(a.out, exist_ok=True)
    write_atomic(os.path.join(a.out, "s2_xtb_read.json"), json.dumps(res, indent=1, default=float))
    lines = report(res)
    write_atomic(os.path.join(a.out, "s2_xtb_read.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
