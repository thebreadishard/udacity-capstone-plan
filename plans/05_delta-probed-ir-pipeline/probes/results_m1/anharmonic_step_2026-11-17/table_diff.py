"""What the set-wise match changes on the stored molecules (TASKS 255): every mode under both rules, and the two artefacts' tables.

    python table_diff.py [--data-root <plan folder holding the force fields>]

Every molecule of labels_domain_2026-11-13 (S2, S2b, S3's two targets: 39 molecules) is loaded as the reads load it and matched
to its xtb field twice by `s2_xtb_read.attach_xtb`: under 'single' (the one-to-one match of the registered reads) and under
'sets'. Counted: the modes whose partner held under 'single' and whose shift, mark or overlap is not the same number to the bit
under 'sets' (must be none), the modes 'sets' adds, and the same at the tolerances 0.5 and 3 cm⁻¹ beside the carried 1. Then
format 2 of the artefact (the table master's match built) against format 3: rows added, rows missing, rows changed.

Writes table_diff.json and table_diff.txt beside itself.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import s2_xtb_read as X  # noqa: E402
from anharmonic_step import ARTEFACT, TABLE_KEYS  # noqa: E402
from anharmonic_step_fit import SETS, TARGETS  # noqa: E402
from s2_read import WINDOWS, XTB_KEY, in_window  # noqa: E402
from s2b_read import load_set, merge, read_sets  # noqa: E402

TOLERANCES_CM = (0.5, 1.0, 3.0)
OLD_ARTEFACT = PLAN / "probes" / "anharmonic_step" / "x2star_v2.json"


def write_atomic(path: Path, text: str) -> None:
    """The text into a temp file, moved over the target."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def molecules(sets_path: str) -> list[tuple[dict, dict, np.ndarray, np.ndarray]]:
    """Every molecule of a sets file with both force fields: its G record, its xtb record and both mode sets."""
    parts = {s.name: load_set(s) for s in read_sets(sets_path)}
    g_by_scaf, x_by_id = merge(parts)
    mols = [m for ms in g_by_scaf.values() for m in ms if m["id"] in x_by_id]
    modes = X.load_modes({m["id"]: (m["dir"], x_by_id[m["id"]]["dir"]) for m in mols})
    return [(m, x_by_id[m["id"]], *modes[m["id"]]) for m in mols]


def window_of(omega: float) -> str | None:
    """The reading window a frequency falls in."""
    return next((name for name, w in WINDOWS.items() if in_window(np.array([omega]), w)[0]), None)


def compare(g: dict, x: dict, q_g: np.ndarray, q_x: np.ndarray) -> dict[str, Any]:
    """One molecule under both rules: the modes that held and differ in any number, and the modes the set-wise match adds."""
    single, sets = X.attach_xtb(g, x, q_g, q_x, "single"), X.attach_xtb(g, x, q_g, q_x, "sets")
    held = ~single["no_xtb"]
    differ = held & ~((single[XTB_KEY] == sets[XTB_KEY]) & (single["vpt2_marked"] == sets["vpt2_marked"])
                      & (single["xtb_overlap"] == sets["xtb_overlap"]) & ~sets["no_xtb"] & ~sets["xtb_set_wise"])
    match = X.match_sets(g["omega"], q_g, q_x)
    added = []
    for i in np.flatnonzero(sets["xtb_set_wise"]):
        members = np.flatnonzero(match.weights[i])
        added.append({"id": g["id"], "mode": int(i), "omega_cm": float(g["omega"][i]), "family": str(g["family"][i]),
                      "window": window_of(float(g["omega"][i])), "large_amplitude": bool(g["large_amplitude"][i]),
                      "marked": bool(sets["vpt2_marked"][i]), "one_to_one": float(single["xtb_overlap"][i]),
                      "set_overlap": float(sets["xtb_overlap"][i]), "xtb_shift_cm": float(sets[XTB_KEY][i]),
                      "partners": [{"xtb_omega_cm": float(x["omega"][j]), "weight": float(match.weights[i, j]),
                                    "xtb_shift_cm": float(x["delta"][j])} for j in members]})
    refused_unchanged = single["no_xtb"] & sets["no_xtb"] & (np.asarray(single["xtb_overlap"]) == np.asarray(sets["xtb_overlap"]))
    return {"modes": len(held), "held_one_to_one": int(held.sum()), "held_and_differ": int(differ.sum()),
            "refused_one_to_one": int(single["no_xtb"].sum()), "refused_both_same_overlap": int(refused_unchanged.sum()), "added": added}


def at_tolerance(mols: list[tuple[dict, dict, np.ndarray, np.ndarray]], tolerance: float) -> dict[str, int]:
    """Over all molecules at one tolerance: the modes in a set of two or more, and the refused modes matched as a set."""
    in_a_set = rescued = 0
    for g, _, q_g, q_x in mols:
        sets = X.mode_sets(g["omega"], tolerance)
        in_a_set += int((np.bincount(sets)[sets] > 1).sum())
        rescued += int(X.match_sets(g["omega"], q_g, q_x, tolerance=tolerance).set_wise.sum())
    return {"modes_in_a_set": in_a_set, "matched_as_a_set": rescued}


def tables() -> dict[str, Any]:
    """Format 2's table against format 3's, per window: rows of the old table missing from the new, and the rows added."""
    old = json.loads(OLD_ARTEFACT.read_text(encoding="utf-8"))["windows"]
    new = json.loads(Path(ARTEFACT).read_text(encoding="utf-8"))["windows"]
    out = {}
    for name, w in old.items():
        before = list(zip(*(w["table"][k] for k in TABLE_KEYS), strict=True))
        after = list(zip(*(new[name]["table"][k] for k in TABLE_KEYS), strict=True))
        rest, missing = list(after), []
        for row in before:
            if row in rest:
                rest.remove(row)
            else:
                missing.append(dict(zip(TABLE_KEYS, row, strict=True)))
        walk = iter(after)
        out[name] = {"rows_before": len(before), "rows_after": len(after), "old_rows_missing_or_changed": missing,
                     "old_rows_in_their_order": all(row in walk for row in before),
                     "rows_added": [dict(zip(TABLE_KEYS, row, strict=True)) for row in rest]}
    return out


def report(res: dict[str, Any]) -> list[str]:
    """The text record."""
    t = res["totals"]
    lines = [f"# The set-wise match on the stored molecules ({res['molecules']} molecules, {t['modes']} modes)", "",
             f"partner held one to one: {t['held_one_to_one']}; of those with another shift, mark or overlap under the set-wise match "
             f"(to the bit): {t['held_and_differ']}",
             f"refused one to one: {t['refused_one_to_one']}; matched as a set: {len(res['added'])}; still refused: "
             f"{t['refused_one_to_one'] - len(res['added'])}, of which with the same overlap to the bit: {t['refused_both_same_overlap']} "
             "(the others are read against their set's partners and stay under the line)", "",
             "modes matched as a set (id, mode, omega, family, window; one to one -> set overlap; shift; partners as omega/weight/shift):"]
    lines += [f"  {a['id']} {a['mode']} {a['omega_cm']:.2f} {a['family']} {a['window']}{' large-amplitude' if a['large_amplitude'] else ''}"
              f"{' marked' if a['marked'] else ''}: {a['one_to_one']:.3f} -> {a['set_overlap']:.3f}; {a['xtb_shift_cm']:.2f}; "
              + ", ".join(f"{p['xtb_omega_cm']:.2f}/{p['weight']:.3f}/{p['xtb_shift_cm']:.2f}" for p in a["partners"]) for a in res["added"]]
    lines += ["", "by tolerance (cm-1): modes in a set of two or more; refused modes matched as a set"]
    lines += [f"  {tol}: {v['modes_in_a_set']}; {v['matched_as_a_set']}" for tol, v in res["by_tolerance"].items()]
    lines += ["", f"the artefact's table, format 2 ({OLD_ARTEFACT.name}) against format 3 ({Path(ARTEFACT).name}):"]
    for name, w in res["tables"].items():
        lines.append(f"  {name}: {w['rows_before']} -> {w['rows_after']} rows; old rows missing or changed: "
                     f"{len(w['old_rows_missing_or_changed'])}; old rows in their order: {w['old_rows_in_their_order']}; added: "
                     + "; ".join(f"{r['family']} at {r['omega']:.2f} (label {r['delta']:.2f}, xtb {r[XTB_KEY]:.2f})" for r in w["rows_added"]))
    return lines


def main() -> int:
    """Compare, write both records and print the text."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", default=str(PLAN), help="the plan folder whose probes/results_m1 holds the force fields")
    a = ap.parse_args()
    table_part = tables()
    os.chdir(a.data_root)
    mols = molecules(SETS) + molecules(TARGETS)
    per = {m[0]["id"]: compare(*m) for m in mols}
    keys = ("modes", "held_one_to_one", "held_and_differ", "refused_one_to_one", "refused_both_same_overlap")
    res = {"molecules": len(mols), "totals": {k: sum(p[k] for p in per.values()) for k in keys},
           "added": [x for p in per.values() for x in p["added"]],
           "by_tolerance": {str(tol): at_tolerance(mols, tol) for tol in TOLERANCES_CM}, "tables": table_part,
           "per_molecule": {i: {k: p[k] for k in keys} | {"added": len(p["added"])} for i, p in per.items()}}
    write_atomic(HERE / "table_diff.json", json.dumps(res, indent=1, ensure_ascii=False))
    lines = report(res)
    write_atomic(HERE / "table_diff.txt", "\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
