"""TASKS 255: are modes refused by the one-to-one match to the xtb force field for their basis, not for their physics?

    python degenerate_match.py

Read-only. Every molecule of labels_domain_2026-11-13 (S2, S2b, S3's two targets) is loaded through the reads' own loaders. Per G
mode: its one-to-one xtb partner (`s2_xtb_read.match_modes`, the match of training and step), its near-degenerate set on the G side
(modes chained by gaps of at most a tolerance in ω), the xtb set (the xtb clusters, same tolerance, of the one-to-one partners of the
G set's members) and the subspace overlap: the sum over the xtb set of the squared overlaps of the G mode, which is the squared norm
of its projection on the xtb set's span. A mode refused one to one (< 0.5) whose subspace overlap passes is refused for its basis.

Then the first real run of the step on benzene from its saved files, and x2*'s four registered bars refitted with the rows a
set-wise match would add (`s2_xtb_read.attach_xtb` replaced in memory for the call; no file of the repository is changed).
Writes degenerate_match.json and degenerate_match.txt beside itself.
"""
from __future__ import annotations

import contextlib
import json
import os
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DESIGN = os.path.join(PLAN, "probes", "results_m1", "anharmonic_design_questions_2026-11-16")
for folder in (DESIGN, os.path.join(PLAN, "src"), os.path.join(PLAN, "probes")):
    sys.path.insert(0, folder)
import s2_xtb_read  # noqa: E402
from anharmonic_step import Modes  # noqa: E402
from refit import ROUTE_RULES, SETS, TARGETS, refit_window  # noqa: E402
from s1_anharmonic_level import harmonic_modes  # noqa: E402
from s2_read import FAMILIES, WINDOWS, XTB_KEY, in_window, write_atomic  # noqa: E402
from s2_xtb_read import MIN_OVERLAP, load_modes, match_modes  # noqa: E402
from s2b_read import load_set, merge, read_sets  # noqa: E402
from s3_read import label_notes  # noqa: E402

TOLERANCES_CM = (0.5, 1.0, 3.0)
REFIT_TOLERANCE_CM = 1.0        # the tolerance TASKS 255 names for the set-wise match
STRICT_OVERLAP = 0.8
FIRST_RUN = "probes/results_m1/pipeline_benzene_anharmonic_first_run/benzene"
STORED_DEMO = "probes/results_m1/anharmonic_step_2026-11-16/stored_field_demo/benzene/anharmonic.json"
NAMES = {"A_8448043181": "benzene"}
REGISTERED = {"ring-ip": 3.37, "other": 3.84, "CH-oop": 8.38, "CH-stretch": 6.21}


def clusters(omega: np.ndarray, tolerance: float) -> np.ndarray:
    """Per mode the number of its near-degenerate set: modes chained by gaps of at most `tolerance` in ω."""
    order = np.argsort(omega)
    label = np.empty(len(omega), int)
    label[order] = np.concatenate([[0], np.cumsum(np.diff(omega[order]) > tolerance)])
    return label


@dataclass(frozen=True)
class SetMatch:
    """One molecule's set-wise reading at one tolerance, per G mode."""
    g_size: np.ndarray          # members of the mode's G set
    x_size: np.ndarray          # members of the xtb set it is projected on
    subspace: np.ndarray        # squared norm of the mode's projection on the xtb set's span
    set_mean: np.ndarray        # the mean of `subspace` over the mode's G set
    weights: np.ndarray         # M_G × M_X: the squared overlaps inside the xtb set, zero outside

    def xtb_value(self, per_xtb_mode: np.ndarray) -> np.ndarray:
        """A per-xtb-mode quantity carried to each G mode as the overlap-weighted mean over its xtb set."""
        return self.weights @ np.asarray(per_xtb_mode, float) / self.subspace

    def xtb_spread(self, per_xtb_mode: np.ndarray) -> np.ndarray:
        """Largest minus smallest value of a per-xtb-mode quantity inside each G mode's xtb set."""
        inside = self.weights > 0
        v = np.asarray(per_xtb_mode, float)[None, :]
        return np.where(inside, v, -np.inf).max(axis=1) - np.where(inside, v, np.inf).min(axis=1)

    def xtb_any(self, per_xtb_mode: np.ndarray) -> np.ndarray:
        """Whether any member of each G mode's xtb set carries a flag."""
        return ((self.weights > 0) & np.asarray(per_xtb_mode, bool)[None, :]).any(axis=1)


def set_match(omega_g: np.ndarray, omega_x: np.ndarray, q_g: np.ndarray, q_x: np.ndarray, tolerance: float) -> SetMatch:
    """The set-wise reading of one molecule at one tolerance."""
    ov = (q_g.T @ q_x) ** 2
    partner, _ = match_modes(q_g, q_x, 0.0)
    lab_g, lab_x = clusters(omega_g, tolerance), clusters(omega_x, tolerance)
    n = len(omega_g)
    weights, g_size, x_size = np.zeros_like(ov), np.zeros(n, int), np.zeros(n, int)
    for c in np.unique(lab_g):
        members = np.flatnonzero(lab_g == c)
        x_set = np.isin(lab_x, lab_x[partner[members]])
        weights[np.ix_(members, np.flatnonzero(x_set))] = ov[np.ix_(members, np.flatnonzero(x_set))]
        g_size[members], x_size[members] = len(members), int(x_set.sum())
    subspace = weights.sum(axis=1)
    set_mean = np.array([subspace[lab_g == lab_g[i]].mean() for i in range(n)])
    return SetMatch(g_size, x_size, subspace, set_mean, weights)


def load_molecules(sets_path: str, role: str) -> list[dict[str, Any]]:
    """Every molecule of a sets file that has both force fields: the G and xtb records of the reads and both mode sets."""
    parts = {s.name: load_set(s) for s in read_sets(sets_path)}
    g_by_scaf, x_by_id = merge(parts)
    mols = [m for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id]
    modes = load_modes({m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for m in mols})
    pairs = label_notes(sets_path)
    return [{"id": m["id"], "role": role, "g": m, "x": x_by_id[m["id"]], "q_g": modes[m["id"]][0], "q_x": modes[m["id"]][1],
             "symmetry_pairs": len(pairs[m["id"]]["degenerate_pairs"])} for m in mols]


def window_name(omega: float) -> str | None:
    """The read window a harmonic frequency falls in, or None."""
    for name, window in WINDOWS.items():
        if in_window(np.array([omega]), window)[0]:
            return name
    return None


def mode_rows(mol: dict[str, Any]) -> list[dict[str, Any]]:
    """One row per G mode of a molecule: the one-to-one match and the set-wise reading at every tolerance."""
    g, x = mol["g"], mol["x"]
    partner, best = match_modes(mol["q_g"], mol["q_x"], 0.0)
    sets = {tol: set_match(g["omega"], x["omega"], mol["q_g"], mol["q_x"], tol) for tol in TOLERANCES_CM}
    rows = []
    for i in range(len(g["omega"])):
        row = {"id": mol["id"], "name": NAMES.get(mol["id"], mol["id"]), "role": mol["role"], "mode": i,
               "omega_cm": float(g["omega"][i]), "family": str(g["family"][i]), "window": window_name(float(g["omega"][i])),
               "large_amplitude": bool(g["large_amplitude"][i]), "g_marked": bool(g["vpt2_marked"][i]),
               "overlap": float(best[i]), "refused": bool(best[i] < MIN_OVERLAP),
               "xtb_partner_omega_cm": float(x["omega"][partner[i]]), "symmetry_pairs": mol["symmetry_pairs"], "sets": {}}
        row["table_row"] = bool(row["window"] and not row["large_amplitude"] and not row["g_marked"])
        for tol, s in sets.items():
            row["sets"][str(tol)] = {"g_size": int(s.g_size[i]), "x_size": int(s.x_size[i]), "subspace": float(s.subspace[i]),
                                     "set_mean": float(s.set_mean[i]), "xtb_delta_cm": float(s.xtb_value(x["delta"])[i]),
                                     "xtb_delta_spread_cm": float(s.xtb_spread(x["delta"])[i]),
                                     "xtb_marked": bool(s.xtb_any(x["vpt2_marked"])[i])}
        rows.append(row)
    return rows


def tally(rows: list[dict[str, Any]], tol: float) -> dict[str, int]:
    """The counts of one group of modes at one tolerance."""
    key = str(tol)
    refused = [r for r in rows if r["refused"]]
    in_set = [r for r in rows if not r["refused"] and r["sets"][key]["g_size"] > 1]
    lucky = [r for r in in_set if r["overlap"] < STRICT_OVERLAP]
    return {"modes": len(rows), "refused": len(refused),
            "refused_in_a_set": sum(r["sets"][key]["g_size"] > 1 or r["sets"][key]["x_size"] > 1 for r in refused),
            "refused_for_basis_0.5": sum(r["sets"][key]["subspace"] >= MIN_OVERLAP for r in refused),
            "refused_for_basis_0.8": sum(r["sets"][key]["subspace"] >= STRICT_OVERLAP for r in refused),
            "accepted_in_a_set": len(in_set), "accepted_in_a_set_0.5_to_0.8": len(lucky),
            "of_those_subspace_0.8": sum(r["sets"][key]["subspace"] >= STRICT_OVERLAP for r in lucky)}


def totals(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Per tolerance: all modes, the training table's rows, the symmetric molecules' share, per family and per molecule."""
    out = {}
    for tol in TOLERANCES_CM:
        table = [r for r in rows if r["table_row"]]
        out[str(tol)] = {
            "all_modes": tally(rows, tol), "table_rows": tally(table, tol),
            "symmetric_molecules": tally([r for r in rows if r["symmetry_pairs"] > 0], tol),
            "other_molecules": tally([r for r in rows if r["symmetry_pairs"] == 0], tol),
            "per_family": {fa: tally([r for r in rows if r["family"] == fa], tol) for fa in FAMILIES},
            "per_family_table_rows": {fa: tally([r for r in table if r["family"] == fa], tol) for fa in FAMILIES},
            "per_molecule": {i: {"symmetry_pairs": next(r["symmetry_pairs"] for r in rows if r["id"] == i),
                                 **tally([r for r in rows if r["id"] == i], tol)} for i in dict.fromkeys(r["id"] for r in rows)}}
    return out


def first_run() -> dict[str, Any]:
    """The step's first real run on benzene, from its saved files: every B3LYP mode against the run's own xtb field."""
    folder = os.path.join(PLAN, FIRST_RUN)
    with open(os.path.join(folder, "geometry.json"), encoding="utf-8") as fh:
        geo = json.load(fh)
    with np.load(os.path.join(folder, "hessian_b3lyp_analytic.npz")) as z:
        hessian = np.asarray(z["H_projected"], float)
    modes = Modes.from_hessian(hessian, [s.capitalize() for s in geo["symbols"]], np.asarray(geo["coords_bohr"], float))
    omega_x, q_x = harmonic_modes(os.path.join(folder, "anharmonic", "xtb", "benzene", "X", "ref.json"))
    partner, best = match_modes(modes.q, q_x, 0.0)
    sets = {tol: set_match(modes.omega, omega_x, modes.q, q_x, tol) for tol in TOLERANCES_CM}
    with open(os.path.join(folder, "anharmonic.json"), encoding="utf-8") as fh:
        saved = json.load(fh)["modes"]
    with open(os.path.join(PLAN, STORED_DEMO), encoding="utf-8") as fh:
        stored = json.load(fh)["modes"]
    rows = []
    for i, w in enumerate(modes.omega):
        rows.append({"mode": i, "omega_cm": float(w), "overlap": float(best[i]), "overlap_saved_by_the_run": saved[i]["xtb_overlap"],
                     "reason_saved_by_the_run": saved[i]["reason"], "overlap_stored_field_demo": stored[i]["xtb_overlap"],
                     "xtb_partner_omega_cm": float(omega_x[partner[i]]),
                     "overlap_with_each_xtb_mode_of_the_set": [[float(omega_x[j]), float(sets[1.0].weights[i, j])]
                                                               for j in np.flatnonzero(sets[1.0].weights[i] > 0)],
                     "sets": {str(tol): {"g_size": int(s.g_size[i]), "x_size": int(s.x_size[i]), "subspace": float(s.subspace[i])}
                              for tol, s in sets.items()}})
    return {"folder": FIRST_RUN, "modes": rows,
            "largest_difference_from_saved_overlap": float(max(abs(r["overlap"] - r["overlap_saved_by_the_run"]) for r in rows))}


def setwise_attach(original: Any) -> Any:
    """`s2_xtb_read.attach_xtb` with the set-wise match added: a mode refused one to one whose subspace overlap passes MIN_OVERLAP
    gets the overlap-weighted mean shift of its xtb set, and the set's mark."""
    def attach(rec_g: dict, rec_x: dict, q_g: np.ndarray, q_x: np.ndarray) -> dict:
        rec = original(rec_g, rec_x, q_g, q_x)
        s = set_match(rec_g["omega"], rec_x["omega"], q_g, q_x, REFIT_TOLERANCE_CM)
        rescued = rec["no_xtb"] & (s.subspace >= MIN_OVERLAP)
        xtb = np.where(rescued, s.xtb_value(rec_x["delta"]), rec[XTB_KEY])
        return {**rec, XTB_KEY: xtb, "no_xtb": rec["no_xtb"] & ~rescued,
                "vpt2_marked": rec["vpt2_marked"] | (rescued & s.xtb_any(rec_x["vpt2_marked"]))}
    return attach


@contextlib.contextmanager
def setwise_match_in_memory() -> Iterator[None]:
    """The reads' loader with the set-wise match, for the duration of the block only."""
    original = s2_xtb_read.attach_xtb
    s2_xtb_read.attach_xtb = setwise_attach(original)
    try:
        yield
    finally:
        s2_xtb_read.attach_xtb = original


def refit() -> dict[str, Any]:
    """The four registered bars with the table as it is and with the rows a set-wise match adds (S2b's configurations unchanged)."""
    out = {}
    for name in ROUTE_RULES:
        before = refit_window(name)
        with setwise_match_in_memory():
            after = refit_window(name)
        out[name] = {"train_rows": {"one_to_one": before["train"]["per_family"], "set_wise": after["train"]["per_family"]},
                     "target_modes": {"one_to_one": before["targets"]["per_family"], "set_wise": after["targets"]["per_family"]},
                     "families": {fa: {"config": f["x2_config"], "registered": f["rms_stored"], "one_to_one": f["rms_refit"],
                                       "set_wise": after["families"][fa]["rms_refit"], "n_one_to_one": f["n"],
                                       "n_set_wise": after["families"][fa]["n"],
                                       "per_target_one_to_one": f["per_molecule_refit"],
                                       "per_target_set_wise": after["families"][fa]["per_molecule_refit"]}
                                  for fa, f in before["families"].items()}}
    return out


def mode_line(r: dict[str, Any]) -> str:
    """One mode's row of the text tables."""
    cells = " ".join(f"| {r['sets'][str(t)]['g_size']}/{r['sets'][str(t)]['x_size']} {r['sets'][str(t)]['subspace']:.3f} "
                     f"{r['sets'][str(t)]['set_mean']:.3f}" for t in TOLERANCES_CM)
    flags = "".join(c for c, on in (("T", r["table_row"]), ("L", r["large_amplitude"]), ("M", r["g_marked"])) if on) or "-"
    return (f"{r['name']:<14} {r['mode']:>3} {r['omega_cm']:>8.2f} {r['family']:<10} {r['window'] or '-':<4} {flags:<3} "
            f"{r['overlap']:.3f} {r['xtb_partner_omega_cm']:>8.2f} {cells}")


def tally_line(label: str, t: dict[str, int]) -> str:
    """One group's counts as a line of the text tables."""
    return (f"{label:<26} modes {t['modes']:>4}  refused {t['refused']:>3}  in a set {t['refused_in_a_set']:>3}  basis>=0.5 "
            f"{t['refused_for_basis_0.5']:>3}  basis>=0.8 {t['refused_for_basis_0.8']:>3}  accepted in a set "
            f"{t['accepted_in_a_set']:>3}  of them 0.5-0.8 {t['accepted_in_a_set_0.5_to_0.8']:>3} (subspace>=0.8: {t['of_those_subspace_0.8']})")


def report(res: dict[str, Any]) -> list[str]:
    """The text tables."""
    rows = res["modes"]
    head = ("molecule      mode    omega family     win  flg 1-to-1 xtb omega " + " ".join(f"| tol {t}: sizes G/X, subspace, set mean"
                                                                                           for t in TOLERANCES_CM))
    lines = [f"Degenerate modes and the one-to-one match (TASKS 255): {len({r['id'] for r in rows})} molecules, {len(rows)} modes",
             "flags: T a training-table row (in a window, not large-amplitude, not marked), L large-amplitude, M marked on G", "",
             "REFUSED MODES (one-to-one squared overlap < 0.5)", head]
    lines += [mode_line(r) for r in rows if r["refused"]]
    lines += ["", "ACCEPTED MODES IN A NEAR-DEGENERATE G SET (1 cm-1) WITH ONE-TO-ONE OVERLAP 0.5-0.8", head]
    lines += [mode_line(r) for r in rows if not r["refused"] and r["sets"]["1.0"]["g_size"] > 1 and r["overlap"] < STRICT_OVERLAP]
    for tol in TOLERANCES_CM:
        t = res["totals"][str(tol)]
        lines += ["", f"TOTALS at {tol} cm-1", tally_line("all modes", t["all_modes"]), tally_line("training-table rows", t["table_rows"]),
                  tally_line("symmetric molecules", t["symmetric_molecules"]), tally_line("other molecules", t["other_molecules"])]
        lines += [tally_line(f"family {fa}", v) for fa, v in t["per_family"].items()]
        lines += [tally_line(f"table rows, {fa}", v) for fa, v in t["per_family_table_rows"].items()]
        lines += [tally_line(f"{NAMES.get(i, i)} (pairs {v['symmetry_pairs']})", v) for i, v in t["per_molecule"].items()]
    lines += ["", f"FIRST REAL RUN ON BENZENE ({res['first_run']['folder']}); largest difference from the overlaps the run saved: "
                  f"{res['first_run']['largest_difference_from_saved_overlap']:.2e}",
              "mode    omega 1-to-1 stored-field xtb omega  subspace(0.5/1/3)  overlaps inside the xtb set (1 cm-1)  reason saved"]
    for r in res["first_run"]["modes"]:
        sub = "/".join(f"{r['sets'][str(t)]['subspace']:.3f}" for t in TOLERANCES_CM)
        inside = ", ".join(f"{w:.3f}: {v:.3f}" for w, v in r["overlap_with_each_xtb_mode_of_the_set"])
        lines.append(f"{r['mode']:>4} {r['omega_cm']:>8.2f} {r['overlap']:.4f} {r['overlap_stored_field_demo']:.4f} "
                     f"{r['xtb_partner_omega_cm']:>8.2f}  {sub}  [{inside}]  {r['reason_saved_by_the_run']}")
    lines += ["", f"REFIT with the set-wise match at {REFIT_TOLERANCE_CM} cm-1 (S2b's configurations unchanged)"]
    for name, w in res["refit"].items():
        lines.append(f"{name}: training rows {w['train_rows']['one_to_one']} -> {w['train_rows']['set_wise']}; "
                     f"target modes {w['target_modes']['one_to_one']} -> {w['target_modes']['set_wise']}")
        lines += [f"  {fa}: printed {REGISTERED[fa]}, registered {f['registered']:.4f}, one-to-one refit {f['one_to_one']:.4f} "
                  f"(n {f['n_one_to_one']}), set-wise {f['set_wise']:.4f} (n {f['n_set_wise']}); per target "
                  f"{ {k: round(v, 2) for k, v in f['per_target_one_to_one'].items()} } -> "
                  f"{ {k: round(v, 2) for k, v in f['per_target_set_wise'].items()} }" for fa, f in w["families"].items()]
    return lines


def main() -> int:
    """Measure, write both files and print the text."""
    os.chdir(PLAN)
    mols = load_molecules(SETS, "training") + load_molecules(TARGETS, "target")
    rows = [r for m in mols for r in mode_rows(m)]
    res = {"min_overlap": MIN_OVERLAP, "strict_overlap": STRICT_OVERLAP, "tolerances_cm": TOLERANCES_CM,
           "molecules": len(mols), "totals": totals(rows), "first_run": first_run(), "refit": refit(), "modes": rows}
    write_atomic(os.path.join(HERE, "degenerate_match.json"), json.dumps(res, indent=1, default=float))
    lines = report(res)
    write_atomic(os.path.join(HERE, "degenerate_match.txt"), "\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
