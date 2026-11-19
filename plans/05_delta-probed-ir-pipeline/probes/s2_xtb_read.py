"""S2 amendment 4's reads (registered 18 Oct 2026, 14:5x, before any xtb number): GFN2-xTB's own anharmonic shift as an input for the
B3LYP (G) GVPT2 labels.

    python s2_xtb_read.py <s2_root> --selection <selection.json> [--extra ID=DIR ...] --gvpt2-dir <G labels> \
        --xtb-root <xtb root> --xtb-gvpt2-dir <X labels> --out <dir>

Per molecule the xtb normal modes are matched to the G modes by squared eigenvector overlap (Hungarian, as S1's comparison); a G mode
whose matched overlap is below MIN_OVERLAP is read against its near-degenerate set (`match_sets`, TASKS 255) and, when that overlap is
below the line too, has no xtb partner and leaves the xtb reads (counted). A molecule without an xtb force field,
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
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import json_records  # noqa: E402
from s2_read import (  # noqa: E402
    FAMILIES,
    LINE_LICENSE,
    WINDOW,
    WINDOWS,
    XTB_KEY,
    ReadOptions,
    add_window_argument,
    apply_scope,
    curve,
    fit_predict,
    in_window,
    load_selection,
    rms,
    verdict,
    window_record,
    write_atomic,
)
from s2_search import KRR_ALPHA, KRR_GAMMA, XTB_FEATURES, Config, nested  # noqa: E402
from s2_search import fit_predict as search_fit_predict  # noqa: E402

MIN_OVERLAP = 0.5           # amendment 4: a G mode whose matched xtb mode overlaps less has no partner
SET_TOLERANCE_CM = 1.0      # modes chained by gaps in ω of at most this form one near-degenerate set (`match_sets` says why this value)
SET_MIN_OVERLAP = 0.8       # a mode read as a set must lie this far in the span of the set's partners (`match_sets`, rule 3)
SET_MAX_MODES = 4           # a chained set of more modes is no degenerate level and is not read as a set (the table's largest: 3)
MATCH_RULES = {"sets": SET_TOLERANCE_CM, "single": None}    # 'single': the one-to-one match of the registered reads (amendment 4)
DEFAULT_RULE = "sets"
READ_SCOPES = ("all", "no-large-amplitude")
X1 = Config("ridge", XTB_FEATURES)
X2_GRID = [Config("krr", XTB_FEATURES, a, g) for a in KRR_ALPHA for g in KRR_GAMMA]


def match_modes(q_g: np.ndarray, q_x: np.ndarray, min_overlap: float = MIN_OVERLAP) -> tuple[np.ndarray, np.ndarray]:
    """Per G mode (columns of q_g, mass-weighted 3N × M), the index of its xtb partner among q_x's columns (−1 when the matched squared
    overlap is below min_overlap) and that overlap. q_g may hold fewer modes than q_x (the pipeline's listed bands against all
    B3LYP modes), never more: every mode of q_g must get a partner of its own."""
    if q_g.shape[0] != q_x.shape[0] or q_g.shape[1] > q_x.shape[1]:
        raise ValueError(f"mode arrays do not match: {q_g.shape} against {q_x.shape}")
    ov = (q_g.T @ q_x) ** 2
    rows, cols = linear_sum_assignment(-ov)
    partner = np.full(q_g.shape[1], -1)
    best = np.zeros(q_g.shape[1])
    best[rows] = ov[rows, cols]
    partner[rows] = np.where(ov[rows, cols] >= min_overlap, cols, -1)
    return partner, best


def mode_sets(omega: np.ndarray, tolerance: float | None) -> np.ndarray:
    """Per mode the number of its near-degenerate set: neighbours in ω chained while the gap is at most `tolerance` cm⁻¹. With
    None every mode is its own set."""
    omega = np.asarray(omega, float)
    if tolerance is None or not len(omega):
        return np.arange(len(omega))
    order = np.argsort(omega, kind="stable")
    label = np.empty(len(omega), int)
    label[order] = np.concatenate([[0], np.cumsum(np.diff(omega[order]) > tolerance)])
    return label


@dataclass(frozen=True)
class SetMatch:
    """`match_sets`' answer, per mode of the first side."""
    partner: np.ndarray     # the one-to-one partner on the other side; −1 without a match
    overlap: np.ndarray     # the squared overlap the match was read on: with the partner, or with the set's span for a mode read as a set
    set_wise: np.ndarray    # matched as a set after the one-to-one overlap fell below the line
    oversized: np.ndarray   # under the one-to-one line and not read as a set, because its set holds more than SET_MAX_MODES modes
    weights: np.ndarray     # M × M_other, each matched mode's row summing to 1: 1 at the partner, or the set's squared overlaps

    def carry(self, values: np.ndarray) -> np.ndarray:
        """A quantity of the other side's modes carried to every matched mode (nan without a match): the partner's own value, and
        for a mode matched as a set the mean over the set weighted by squared overlap."""
        v = np.asarray(values, float)
        out = np.full(len(self.partner), np.nan)
        one = (self.partner >= 0) & ~self.set_wise
        out[one] = v[self.partner[one]]
        for i in np.flatnonzero(self.set_wise):
            members = np.flatnonzero(self.weights[i])
            out[i] = self.weights[i, members] @ v[members]
        return out

    def flagged(self, flags: np.ndarray) -> np.ndarray:
        """Whether a matched mode's partner carries a flag; for a mode matched as a set, whether any member it overlaps at all
        does. A flagged member's value is not bounded, so no share of it is small: at 4 % of the weight a marked shift of +180
        moved a mean of −10 to −2.4 (the review of 17 Nov 2026)."""
        return ((self.weights > 0) & np.asarray(flags, bool)[None, :]).any(axis=1)


def match_sets(omega_g: np.ndarray, q_g: np.ndarray, q_x: np.ndarray, min_overlap: float = MIN_OVERLAP,
               tolerance: float | None = SET_TOLERANCE_CM, set_overlap: float = SET_MIN_OVERLAP) -> SetMatch:
    """The match of training and step (TASKS 255): `match_modes`, and for a mode it refuses the same question asked of sets.

    Why sets. The two eigenvectors of a degenerate pair are an arbitrary basis of a plane. Where both sides have the pair, the
    overlap of one vector with one vector is anything between 0 and 1 while the planes coincide: benzene's pair at 1655 cm⁻¹
    overlapped a fresh xtb field at 0.498 and 0.487 (sum 0.985) and lost its step for its basis (17 Nov 2026).

    The rule, per mode i of the first side:
    1. `match_modes` gives i its one-to-one partner p(i). At a squared overlap of `min_overlap` or more that is the match, and the
       mode carries its partner's values — exactly what the one-to-one match gave, so no match that held before changes.
    2. Otherwise i is read as a member of a set. Its own set S holds the modes chained to it by gaps in ω of at most `tolerance`
       (`omega_g`, cm⁻¹); the other side's set is T = p(S), the partners of S and nothing else. No window in ω is laid on the other
       side: it would let unrelated modes in, and T may only hold modes the assignment itself gave to S. The overlap read is the
       squared norm of i's projection on the span of T, Σ_{j∈T} (q_i·q_j)².
    3. At `set_overlap` or more i is matched as a set and carries the mean over T weighted by squared overlap,
       Σ_j (q_i·q_j)² v_j / Σ_j (q_i·q_j)²; below it, i has no match. The line is 0.8, not the single-mode 0.5: at 0.5 on a span,
       40 % and more of the mode lies outside everything that carries its input, which is the case the single-mode line was
       written to refuse; a pair refused for its basis lies almost wholly in its partners' plane (benzene's at 0.985).
    4. A set of more than SET_MAX_MODES modes is not read as a set at all: a chain that long is a crowded stretch of the
       spectrum, not a degenerate level (`SetMatch.oversized` names the modes this refused).
    5. A mode matched as a set is flagged when any member of T it overlaps is (`SetMatch.flagged`).

    A mode alone in its set whose partner is alone in its set is read exactly as `match_modes` reads it, to the bit.

    Rotation. Turning the two vectors of a degenerate pair, on either side, leaves the plane, hence T and the projection of the
    pair on it, as they were; for a symmetry pair every vector of the plane has the same projection (the measured pairs: 0.985 and
    0.985). The carried value is the same in every basis when the pair on the other side carries one value, which is what
    degenerate means. Stored labels of a pair differ by numerical noise (GFN2-xTB shifts of benzene's and coronene's symmetry pairs:
    0.025 cm⁻¹ at most, results_m1/degenerate_match_2026-11-17), and the carried value then lies between the two.

    The tolerance. It has to cover the numerical splitting of an exact degeneracy and nothing more, because only an exact
    degeneracy leaves the basis arbitrary. Stored Hessians split benzene's pairs by up to 0.62 cm⁻¹ (621.24 and 621.86 in S1's
    record), so 0.5 misses a real pair; 3 chains unrelated neighbours in the CH stretches of every larger molecule (482 modes in a
    set of two or more against 253; results_m1/anharmonic_step_2026-11-17/table_diff.txt has the counts at each).

    Accidental neighbours. Within 1 cm⁻¹ a large molecule has unrelated modes, and coronene has symmetry pairs with a third mode
    beside them. They cost nothing where the one-to-one match holds (rule 1 never looks at the set), and a refused mode gains from
    a neighbour's partner only the overlap it really has with it: a mode that does not lie in the span of its neighbours'
    partners stays refused. On the 39 molecules of the training table 76 modes are under the one-to-one line and one of them is
    matched as a set: a C–H stretch at 3183.24 cm⁻¹ that the two methods mix with its neighbour, 0.934 of it in the two partners.
    It is not a symmetry pair — on the stored fields no symmetry pair is under the line — and two more neighbours of this kind,
    at 0.561 and 0.617, stay refused under rule 3.

    `tolerance` None is the one-to-one match of the registered reads. q_g may hold fewer modes than q_x, never more.
    """
    omega_g = np.asarray(omega_g, float)
    if omega_g.shape != (q_g.shape[1],):
        raise ValueError(f"{omega_g.shape} frequencies for modes {q_g.shape}")
    partner, best = match_modes(q_g, q_x, 0.0)
    ov = (q_g.T @ q_x) ** 2
    set_g = mode_sets(omega_g, tolerance)
    overlap, weights = best.copy(), np.zeros_like(ov)
    single = best >= min_overlap
    set_wise, oversized = np.zeros(len(omega_g), bool), np.zeros(len(omega_g), bool)
    weights[single, partner[single]] = 1.0
    for i in np.flatnonzero(~single):
        partners = partner[set_g == set_g[i]]
        if len(partners) == 1:
            continue
        if len(partners) > SET_MAX_MODES:
            oversized[i] = True
            continue
        overlap[i] = ov[i, partners].sum()
        if overlap[i] >= set_overlap:
            weights[i, partners] = ov[i, partners] / overlap[i]
            set_wise[i] = True
    return SetMatch(np.where(single | set_wise, partner, -1), overlap, set_wise, oversized, weights)


def check_rule(rule: str) -> float | None:
    """A match rule's tolerance; an unknown rule is refused."""
    if rule not in MATCH_RULES:
        raise ValueError(f"match rule {rule!r}: one of {sorted(MATCH_RULES)}")
    return MATCH_RULES[rule]


def attach_xtb(rec_g: dict, rec_x: dict, q_g: np.ndarray, q_x: np.ndarray, rule: str = DEFAULT_RULE) -> dict:
    """The G molecule with its per-mode Δ_xtb (nan where no partner) and the boolean 'no_xtb', by `match_sets` under `rule`. A mode
    whose xtb partner is outside VPT2's domain is marked on the G side too (TASKS 207): its Δ_xtb feature would be a number the
    theory could not state."""
    tolerance = check_rule(rule)
    match = match_sets(rec_g["omega"], q_g, q_x, tolerance=tolerance)
    return {**rec_g, XTB_KEY: match.carry(rec_x["delta"]), "no_xtb": match.partner < 0, "xtb_overlap": match.overlap,
            "xtb_set_wise": match.set_wise, "xtb_set_oversized": match.oversized,
            "vpt2_marked": rec_g["vpt2_marked"] | match.flagged(rec_x["vpt2_marked"]),
            "vpt2_checked": bool(rec_g["vpt2_checked"] and rec_x["vpt2_checked"])}


def config_predictor(cfg: Config) -> Callable[[dict, dict], tuple[np.ndarray, np.ndarray, int]]:
    """One search configuration in s2_read.curve's 'b' slot; route (c) and the unseen-family count as route (b) has them (an unseen family's
    modes get the training mean, as route (b) does)."""
    def predict(train: dict, test: dict) -> tuple[np.ndarray, np.ndarray, int]:
        _, pc, unseen = fit_predict(train, test)
        p, _ = search_fit_predict(cfg, train, test, None)
        seen = np.isin(test["family"], np.unique(train["family"]))
        p[~seen] = train["delta"].mean()
        return p, pc, unseen
    return predict


predict_x1 = config_predictor(X1)      # x1: the FX ridge


def x0_read(by_scaf: dict, window: tuple[float, float] = WINDOW) -> dict:
    """Δ_xtb as the prediction, per family over the window modes: rms, Pearson r, and route (c)'s leave-one-scaffold-out rms on the same modes."""
    from s2_read import loso
    t, _, c, f, _ = loso(by_scaf, window=window)
    mols = [m for ms in by_scaf.values() for m in ms]
    keep = [in_window(m["omega"], window) for m in mols]
    truth = np.concatenate([m["delta"][w] for m, w in zip(mols, keep, strict=True)])
    pred = np.concatenate([m[XTB_KEY][w] for m, w in zip(mols, keep, strict=True)])
    fam = np.concatenate([m["family"][w] for m, w in zip(mols, keep, strict=True)])
    out = {}
    for fa in FAMILIES:
        sel = fam == fa
        if not sel.any():
            continue
        r = float(np.corrcoef(pred[sel], truth[sel])[0, 1]) if sel.sum() > 2 and np.std(pred[sel]) > 0 and np.std(truth[sel]) > 0 else float("nan")
        out[fa] = {"n": int(sel.sum()), "rms": rms(pred[sel] - truth[sel]), "pearson_r": r, "c_rms": rms((c - t)[f == fa]),
                   "licensed": bool(rms(pred[sel] - truth[sel]) <= LINE_LICENSE)}
    return out


def build(g_by_scaf: dict, x_by_id: dict, modes: dict, scope: str, window: tuple[float, float] = WINDOW,
          rule: str = DEFAULT_RULE) -> tuple[dict, dict]:
    """The scoped G molecules that have an xtb force field, with Δ_xtb; modes without an xtb partner dropped. Returns (by scaffold, counts)."""
    check_rule(rule)
    counts = {"molecules_without_xtb": [], "modes_without_partner": 0, "window_modes_without_partner": 0, "match_rule": rule,
              "window_modes_matched_as_a_set": 0}
    out = {}
    for scaf, mols in g_by_scaf.items():
        for m in mols:
            if m["id"] not in x_by_id:
                counts["molecules_without_xtb"].append(m["id"])
                continue
            q_g, q_x = modes[m["id"]]
            rec = attach_xtb(m, x_by_id[m["id"]], q_g, q_x, rule)
            if scope != "all":
                rec = apply_scope(rec, "large_amplitude")
            counts["modes_without_partner"] += int(rec["no_xtb"].sum())
            counts["window_modes_matched_as_a_set"] += int((rec["xtb_set_wise"] & in_window(rec["omega"], window)).sum())
            counts["window_modes_without_partner"] += int((rec["no_xtb"] & in_window(rec["omega"], window)).sum())
            rec = apply_scope(rec, "no_xtb")
            out.setdefault(scaf, []).append(rec)
    return out, counts


def read_scope(by_scaf: dict, window: tuple[float, float] = WINDOW) -> dict:
    """x0, x1 (curve and verdict) and x2 (nested) on one scope's molecules."""
    rows = curve(by_scaf, predict=predict_x1, window=window)
    x1_family = {fa: {**v, "licensed": bool(v["b"] <= LINE_LICENSE)} for fa, v in rows["all"]["per_family"].items()}
    return {"x0": x0_read(by_scaf, window), "x1": {"curve": rows, "verdict": verdict(rows), "per_family": x1_family},
            "x2": nested(by_scaf, X2_GRID, window=window)}


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
    add_window_argument(ap)
    a = ap.parse_args()
    extra, window = dict(e.split("=", 1) for e in a.extra), WINDOWS[a.window]
    g_by_scaf, used_g, excluded_g = load_selection(
        a.root, a.selection, ReadOptions(setting="G", extra=extra, gvpt2_dir=a.gvpt2_dir, window=window))
    x_by_scaf, _used_x, excluded_x = load_selection(
        a.xtb_root, a.selection, ReadOptions(setting="X", gvpt2_dir=a.xtb_gvpt2_dir, window=window))
    x_by_id = {m["id"]: m for ms in x_by_scaf.values() for m in ms}
    dirs = {m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id}
    modes = load_modes(dirs)
    res = {"registration": "PreRegistration_2026-10-14_S2_Anharmonic_Shift.md, amendment 4", "min_overlap": MIN_OVERLAP,
           "molecules_g": len(used_g), "excluded_g": excluded_g, "excluded_xtb": excluded_x, "window": window_record(window),
           "window_name": a.window, "scopes": {}}
    for scope in READ_SCOPES:
        by_scaf, counts = build(g_by_scaf, x_by_id, modes, scope, window)
        if len(by_scaf) < 2:
            raise SystemExit(f"scope {scope}: {len(by_scaf)} scaffold(s) with xtb partners — no leave-one-scaffold-out read")
        res["scopes"][scope] = {"counts": counts, "scaffolds": len(by_scaf), "read": read_scope(by_scaf, window)}
    os.makedirs(a.out, exist_ok=True)
    json_records.write(os.path.join(a.out, "s2_xtb_read.json"), res, default=float)
    lines = report(res)
    write_atomic(os.path.join(a.out, "s2_xtb_read.md"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
