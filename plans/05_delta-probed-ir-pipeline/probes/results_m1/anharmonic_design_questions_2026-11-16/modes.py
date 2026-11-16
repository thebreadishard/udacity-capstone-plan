"""Q1 of TASKS 211: which modes carry x2*'s inputs for a new molecule - the B3LYP modes or the corrected ones?

    python modes.py

For every molecule of labels_domain_2026-11-13 that also has the corpus's analytic B3LYP and wB97X Hessians (the correction's
target: wB97X modes are what a perfect dH gives), three mode sets are compared in the corpus frame:

    G  the training's modes (pyscf B3LYP/6-31G* at its own minimum, ref.json), rotated onto the corpus geometry
    B  the pipeline's B3LYP modes (hessian_b3lyp_analytic.npz)
    W  the corrected modes (hessian_wb97x_analytic.npz)

and x2* is asked for a shift twice per band: with the inputs taken on the B mode (family, omega, h, o, the xtb partner's shift)
and carried to its W partner, and with the inputs taken on the W mode itself. Both are scored against the label of the G mode the
B mode matches; the fit leaves the molecule's scaffold out (coronene, a target, is fitted on all training molecules).
Writes modes.json beside itself.
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "src"))
from e8_cc_locality import families, mode_shares  # noqa: E402
from marks import SETS, TARGETS, load_tables, predict_kept, scoped, x2_choices  # noqa: E402
from s1_anharmonic_level import harmonic_modes  # noqa: E402
from s2_read import FAMILIES, WINDOWS, in_window, rms, write_atomic  # noqa: E402
from s2_xtb_read import MIN_OVERLAP, match_modes  # noqa: E402

from dpir.qff import MASS, harmonic  # noqa: E402

CORPUS = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules")
CORPUS_ID = {"coronene": "T_94b3a9d13a"}     # the targets' corpus rows (manifest.csv); tetracene has no computed row
LOW, HIGH = "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz"
FRAME_TOLERANCE_BOHR = 0.2                   # a larger rms distance after the rotation means the atoms are not the same atoms


def kabsch(moving: np.ndarray, fixed: np.ndarray) -> tuple[np.ndarray, float]:
    """The rotation R with (moving - centroid) @ R closest to (fixed - centroid), and the rms distance left."""
    a, b = moving - moving.mean(axis=0), fixed - fixed.mean(axis=0)
    u, _, vt = np.linalg.svd(a.T @ b)
    d = np.sign(np.linalg.det(u @ vt))
    r = u @ np.diag([1.0, 1.0, d]) @ vt
    return r, float(np.sqrt(((a @ r - b) ** 2).sum(axis=1).mean()))


def rotate_modes(q: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Mass-weighted modes (3N x M) with every atom's displacement rotated by r."""
    n = q.shape[0] // 3
    return np.einsum("nim,ij->njm", q.reshape(n, 3, -1), r).reshape(3 * n, -1)


def corpus_modes(folder: str, symbols: list[str]) -> dict:
    """The corpus geometry with the B and W modes of its two analytic Hessians."""
    with open(os.path.join(folder, "geometry.json"), encoding="utf-8") as fh:
        geo = json.load(fh)
    if list(geo["symbols"]) != list(symbols):
        raise ValueError("the corpus atom order differs from the force field's")
    x = np.asarray(geo["coords_bohr"], float)
    out = {"x": x}
    for key, name in (("B", LOW), ("W", HIGH)):
        with np.load(os.path.join(folder, name)) as z:
            h = harmonic(np.asarray(z["H_projected"], float), symbols, x)
        out[key] = (np.asarray(h.omega_cm), np.asarray(h.q))
    return out


def assign(q_a: np.ndarray, q_b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Per column of q_a its partner among q_b's columns by the best one-to-one squared overlap, and that squared overlap."""
    ov = (q_a.T @ q_b) ** 2
    rows, cols = linear_sum_assignment(-ov)
    partner = np.empty(q_a.shape[1], int)
    partner[rows] = cols
    return partner, ov[np.arange(q_a.shape[1]), partner]


def mode_table(omega: np.ndarray, q: np.ndarray, symbols: list[str], x: np.ndarray, rec_x: dict, q_x: np.ndarray) -> dict:
    """x2*'s inputs taken on one mode set: family, omega, h, o and the matched xtb mode's shift (nan without a partner)."""
    m = np.array([MASS[s] for s in symbols])
    h, o, _ = mode_shares(q, symbols, m, x)
    partner, _ = match_modes(q, q_x)
    has = partner >= 0
    return {"omega": omega, "family": families(omega, q, symbols, m, x), "h": h, "o": o, "xtb_partner": partner,
            "xtb": np.where(has, np.asarray(rec_x["delta"])[np.maximum(partner, 0)], np.nan), "delta": np.zeros(len(omega))}


def predict_all(train: list[dict], table: dict, choices: dict[str, dict[str, str]]) -> np.ndarray:
    """x2*'s shift per mode of a table, each mode in the window its own omega falls in; nan outside both or without an xtb partner."""
    pred = np.full(len(table["omega"]), np.nan)
    usable = np.isfinite(table["xtb"])
    part = {k: v[usable] for k, v in table.items()}
    part["id"], part["vpt2_marked"], part["vpt2_checked"] = "table", np.zeros(int(usable.sum()), bool), True
    for name, choice in choices.items():
        w = in_window(part["omega"], WINDOWS[name])
        if w.any():
            pred[np.flatnonzero(usable)[w]] = predict_kept(train, part, choice, WINDOWS[name])
    return pred


def molecule(rec: dict, x_dir: str, train: list[dict], choices: dict[str, dict[str, str]]) -> dict:
    """One molecule's comparison: the three mode sets' overlaps, the inputs on B and on W, both predictions and the label."""
    with open(os.path.join(rec["dir"], "ref.json"), encoding="utf-8") as fh:
        ref = json.load(fh)["molecule"]
    symbols = ref["symbols"]
    corpus = corpus_modes(os.path.join(CORPUS, CORPUS_ID.get(rec["id"], rec["id"])), symbols)
    r, left = kabsch(np.asarray(ref["geometry"], float).reshape(-1, 3), corpus["x"])
    if left > FRAME_TOLERANCE_BOHR:
        raise ValueError(f"the force field's geometry is {left:.3f} bohr rms from the corpus's after rotation")
    q_g = rotate_modes(harmonic_modes(os.path.join(rec["dir"], "ref.json"))[1], r)
    q_x = rotate_modes(harmonic_modes(os.path.join(x_dir, "ref.json"))[1], r)
    (w_b, q_b), (w_w, q_w) = corpus["B"], corpus["W"]
    to_g, ov_bg = assign(q_b, q_g)
    to_w, ov_bw = assign(q_b, q_w)
    rec_x = {"delta": rec["x_own_delta"]}
    t_b, t_w = (mode_table(w, q, symbols, corpus["x"], rec_x, q_x) for w, q in ((w_b, q_b), (w_w, q_w)))
    return {"id": rec["id"], "geometry_rms_bohr": left, "omega_B": w_b, "omega_W_partner": w_w[to_w], "omega_G_partner": rec["omega"][to_g],
            "overlap2_BG": ov_bg, "overlap2_BW": ov_bw, "rank_kept_BW": to_w == np.arange(len(to_w)),
            "family_B": t_b["family"], "family_W": t_w["family"][to_w], "family_G": rec["family"][to_g],
            "h_B": t_b["h"], "h_W": t_w["h"][to_w], "o_B": t_b["o"], "o_W": t_w["o"][to_w],
            "xtb_partner_B": t_b["xtb_partner"], "xtb_partner_W": t_w["xtb_partner"][to_w],
            "pred_B": predict_all(train, t_b, choices), "pred_W": predict_all(train, t_w, choices)[to_w],
            "label": rec["delta"][to_g], "label_usable": ~(rec["vpt2_marked"] | rec["large_amplitude"])[to_g] & (ov_bg >= MIN_OVERLAP)}


def pooled(mols: list[dict]) -> dict:
    """The comparison over all molecules: the mode mixing, the inputs that move, and both choices' error against the label."""
    cat = {k: np.concatenate([m[k] for m in mols]) for k in mols[0] if isinstance(mols[0][k], np.ndarray)}
    abs_bw = np.sqrt(cat["overlap2_BW"])
    out = {"molecules": len(mols), "modes": len(abs_bw),
           "B_vs_G": {"overlap_abs_median": float(np.median(np.sqrt(cat["overlap2_BG"]))),
                      "overlap_abs_p10": float(np.percentile(np.sqrt(cat["overlap2_BG"]), 10)),
                      "omega_rms_cm": rms(cat["omega_B"] - cat["omega_G_partner"])},
           "B_vs_W": {"overlap_abs_median": float(np.median(abs_bw)), "overlap_abs_p10": float(np.percentile(abs_bw, 10)),
                      "overlap_abs_p01": float(np.percentile(abs_bw, 1)), "overlap_abs_min": float(abs_bw.min()),
                      "modes_below_match_line": int((cat["overlap2_BW"] < MIN_OVERLAP).sum()),
                      "rank_changed": int((~cat["rank_kept_BW"]).sum()), "omega_shift_rms_cm": rms(cat["omega_W_partner"] - cat["omega_B"]),
                      "family_changed": int((cat["family_B"] != cat["family_W"]).sum()),
                      "h_rms": rms(cat["h_W"] - cat["h_B"]), "o_rms": rms(cat["o_W"] - cat["o_B"]),
                      "xtb_partner_changed": int((cat["xtb_partner_B"] != cat["xtb_partner_W"]).sum()),
                      "xtb_partner_lost_on_W": int(((cat["xtb_partner_B"] >= 0) & (cat["xtb_partner_W"] < 0)).sum()),
                      "xtb_partner_lost_on_B": int(((cat["xtb_partner_B"] < 0) & (cat["xtb_partner_W"] >= 0)).sum())},
           "families": {}}
    both = cat["label_usable"] & np.isfinite(cat["pred_B"]) & np.isfinite(cat["pred_W"])
    for fa in (*FAMILIES, "all"):
        sel = both & ((cat["family_G"] == fa) | (fa == "all"))
        if sel.any():
            mixing = np.sqrt(cat["overlap2_BW"][sel])
            out["families"][fa] = {
                "n": int(sel.sum()), "overlap_abs_median": float(np.median(mixing)), "overlap_abs_p10": float(np.percentile(mixing, 10)),
                "rms_inputs_on_B": rms((cat["pred_B"] - cat["label"])[sel]), "rms_inputs_on_W": rms((cat["pred_W"] - cat["label"])[sel]),
                "rms_between": rms((cat["pred_W"] - cat["pred_B"])[sel]),
                "max_between": float(np.abs(cat["pred_W"] - cat["pred_B"])[sel].max())}
    out["only_one_predicts"] = {"B only": int((cat["label_usable"] & np.isfinite(cat["pred_B"]) & ~np.isfinite(cat["pred_W"])).sum()),
                                "W only": int((cat["label_usable"] & ~np.isfinite(cat["pred_B"]) & np.isfinite(cat["pred_W"])).sum())}
    return out


def main() -> int:
    """Run the comparison and print it."""
    os.chdir(PLAN)
    train, targets = load_tables(SETS), load_tables(TARGETS)
    choices = x2_choices()
    everything = [scoped(m) for ms in train.values() for m in ms]
    mols, skipped = [], {}
    for group, is_target in ((train, False), (targets, True)):
        for scaf, ms in group.items():
            fit_on = everything if is_target else [scoped(m) for s, others in train.items() if s != scaf for m in others]
            for m in ms:
                try:
                    mols.append(molecule(m, m["x_dir"], fit_on, choices))
                except (OSError, ValueError) as err:
                    skipped[m["id"]] = str(err)
    res = {"pooled": pooled(mols), "skipped": skipped, "per_molecule": {m["id"]: pooled([m]) for m in mols}}
    write_atomic(os.path.join(HERE, "modes.json"), json.dumps(res, indent=1, default=float))
    print(json.dumps(res["pooled"], indent=1, default=float))
    print("skipped", skipped)
    for i, p in res["per_molecule"].items():
        print(i, p["modes"], "B-W median", round(p["B_vs_W"]["overlap_abs_median"], 4), "p10", round(p["B_vs_W"]["overlap_abs_p10"], 3),
              "below line", p["B_vs_W"]["modes_below_match_line"], "all", p["families"].get("all"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
