"""The acceptance test of the anharmonic step's first stage (TASKS 211), on the force fields on disk and nothing else.

    python anharmonic_step_accept.py --out <dir> [--data-root <plan folder holding the force fields>] [--artefact <json>]

Every molecule goes through `anharmonic_step.mode_steps` alone — its B3LYP reference record, its GFN2-xTB force field with that
field's GVPT2 label, and the artefact; the molecule's own B3LYP label is read afterwards, as the truth and as the mark the
label-free rule is compared with. Three checks, each of which must pass or the script exits 1:

1. the route-A targets: per family the rms of step minus label over the registered rows (the modes the registered read scored:
   those the B3LYP label marks left out, a symmetry pair counted once) equals the artefact's own bar — the rms its fit measured
   with the table it holds — to TOLERANCE_CM, on the registered number of rows. The registered bar is printed beside it and is
   not the pass line: since TASKS 255 the table is matched to the xtb field set-wise and holds rows the registered read did
   not, so the model that runs is measured against itself, and its distance from the registered number is reported and bounded
   by CHANGE_LIMIT_CM (`anharmonic_step_fit.py` says why; the fit also reproduces the registered bar with the registered match);
2. coronene's modes 24 and 36 (marked by the B3LYP label only) come out with a step and the 'error not measured' flag;
3. the label-free rule over all molecules of both sets: of the modes a B3LYP label marks, how many get no step (REPORT.md of
   16 Nov: 4 of 6), and how many modes no label marks lose their step to an xtb partner's mark (0).

Reported beside the checks, not a check: the largest difference between the two GFN2-xTB labels of a symmetry pair over all
molecules. The set-wise match gives a pair one shift in every basis when the pair's two labels are one number; where they
differ, the carried shift lies between them, so this difference bounds how far a basis can move it.

Writes acceptance.json and acceptance.md into --out.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections import Counter
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(PLAN, "src"))
from anharmonic_step import ARTEFACT, MODE_REASONS, XTB_PARTNER_MARKED, Artefact, Modes, ModeStep, XtbField, load_artefact, mode_steps  # noqa: E402
from anharmonic_step_fit import CHANGE_LIMIT_CM, SETS, TARGETS, TOLERANCE_CM  # noqa: E402
from s2_read import gvpt2_delta, marked_mask, rms, write_atomic  # noqa: E402
from s2b_read import read_sets  # noqa: E402
from s3_read import label_notes, pair_groups  # noqa: E402

from dpir.provenance import git_state  # noqa: E402

EXPECTED_MARKS = {"label_marked": 6, "caught": 4, "sound_lost": 0}      # REPORT.md, 'Rules compared', first row
FLAGGED = {"coronene": (24, 36)}                                         # REPORT.md, Q2: the two modes the xtb mark misses


def molecules(sets_path: str) -> tuple[list[dict[str, str]], list[str]]:
    """Every selected molecule of a sets file with its four inputs — the G folder and label, the X folder and label — and the ids
    of the selected molecules that lack one of them (a force field that stopped or failed: the reads exclude those too)."""
    out, absent = [], []
    for s in read_sets(sets_path):
        with open(s.selection, encoding="utf-8") as fh:
            selected = json.load(fh)["selected"]
        for m in selected:
            i = m["id"]
            mol = {"id": i, "set": s.name, "g_dir": s.extra.get(i, os.path.join(s.root, i, "G")),
                   "g_label": os.path.join(s.gvpt2_dir, f"{i}.json"), "x_dir": os.path.join(s.xtb_root, i, "X"),
                   "x_label": os.path.join(s.xtb_gvpt2_dir, f"{i}.json")}
            needed = (mol["g_label"], mol["x_label"], *(os.path.join(mol[d], "qff_report.npz") for d in ("g_dir", "x_dir")))
            if all(os.path.isfile(p) for p in needed):
                out.append(mol)
            else:
                absent.append(i)
    return out, absent


def through_step(mol: dict[str, str], artefact: Artefact) -> dict[str, Any]:
    """One molecule through `mode_steps`, then its B3LYP label beside the result: the label's shift and the label's marks."""
    modes = Modes.from_ref(os.path.join(mol["g_dir"], "ref.json"))
    steps = mode_steps(modes, XtbField.from_folder(mol["x_dir"], mol["x_label"]), artefact)
    truth, marked = gvpt2_delta(mol["g_label"], modes.omega)
    if marked is None:
        raise ValueError(f"{mol['g_label']}: the label predates the VPT2-domain check")
    return {"id": mol["id"], "omega": modes.omega, "steps": steps, "truth": truth, "label_marked": marked_mask(marked, len(truth))}


def registered_rows(res: dict[str, Any], pair_omega: list[list[float]]) -> list[dict[str, Any]]:
    """The rows the registered read scored for one target: per window the stepped modes no B3LYP label marks, a symmetry pair as
    the mean of its two members (`s3_read.pair_groups`)."""
    steps: list[ModeStep] = res["steps"]
    rows = []
    for window in sorted({s.window for s in steps if s.window}):
        kept = np.array([i for i, s in enumerate(steps) if s.window == window and not res["label_marked"][i]])
        for g in pair_groups(res["omega"][kept], pair_omega):
            members = [steps[int(k)] for k in kept[g]]
            if len({s.family for s in members}) != 1:
                raise ValueError(f"{res['id']}: a symmetry pair spans families")
            rows.append({"id": res["id"], "family": members[0].family, "modes": [s.mode for s in members],
                         "omega": float(res["omega"][kept[g]].mean()), "truth": float(res["truth"][kept[g]].mean()),
                         "step": float(np.mean([s.delta_anh_cm for s in members]))})
    return rows


def check_targets(results: list[dict[str, Any]], artefact: Artefact) -> dict[str, Any]:
    """Check 1: per family the rms over the targets' registered rows against the artefact's own bar and the registered row
    count; the registered bar, its reproduction under the registered match and the rows the set-wise match added beside it."""
    notes = label_notes(TARGETS)
    rows = [r for res in results for r in registered_rows(res, notes[res["id"]]["pair_omega"])]
    out = {}
    for w in artefact.windows:
        for fa, model in w.families.items():
            mine = [r for r in rows if r["family"] == fa]
            got = rms(np.array([r["step"] - r["truth"] for r in mine]))
            out[fa] = {"rows": len(mine), "rows_registered": model.n_target_rows, "rms_cm": got, "bar_cm": model.bar_cm,
                       "bar_refit_cm": model.bar_refit_cm, "bar_one_to_one_cm": model.bar_one_to_one_cm,
                       "from_registered_cm": got - model.bar_cm,
                       "training_rows_added_by_the_set_wise_match": model.n_training_modes - model.n_training_modes_one_to_one,
                       "harmonic_rms_cm": rms(np.array([r["truth"] for r in mine])),
                       "per_molecule": {i: rms(np.array([r["step"] - r["truth"] for r in mine if r["id"] == i]))
                                        for i in sorted({r["id"] for r in mine})},
                       "passed": bool(abs(got - model.bar_refit_cm) <= TOLERANCE_CM and abs(got - model.bar_cm) <= CHANGE_LIMIT_CM
                                      and len(mine) == model.n_target_rows)}
    return out


def check_flagged(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Check 2: the modes only a B3LYP label marks keep their step and carry the 'error not measured' flag."""
    by_id = {r["id"]: r for r in results}
    out = {}
    for mol, modes in FLAGGED.items():
        for k in modes:
            s: ModeStep = by_id[mol]["steps"][k]
            out[f"{mol} mode {k}"] = {**s.as_record(), "label_marked": bool(by_id[mol]["label_marked"][k]),
                                      "label_shift_cm": float(by_id[mol]["truth"][k]),
                                      "passed": bool(s.delta_anh_cm is not None and s.error_not_measured and by_id[mol]["label_marked"][k])}
    return out


def check_marks(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Check 3: the label-free rule against the B3LYP labels' marks, over every mode of every molecule."""
    marked, reasons, flagged, lost = [], Counter(), 0, []
    for res in results:
        for s, m in zip(res["steps"], res["label_marked"], strict=True):
            reasons[s.reason or "step"] += 1
            flagged += int(s.error_not_measured)
            if m:
                marked.append({"id": res["id"], "mode": s.mode, "omega_cm": s.omega_cm, "family": s.family, "o": s.o, "reason": s.reason,
                               "error_not_measured": s.error_not_measured, "caught": s.reason in MODE_REASONS})
            elif s.reason == XTB_PARTNER_MARKED:
                lost.append({"id": res["id"], "mode": s.mode})
    counts = {"label_marked": len(marked), "caught": sum(m["caught"] for m in marked), "sound_lost": len(lost)}
    uncaught = [m for m in marked if not m["caught"]]
    return {"molecules": len(results), "modes": int(sum(len(r["steps"]) for r in results)), "counts": counts, "expected": EXPECTED_MARKS,
            "label_marked_modes": marked, "sound_modes_lost": lost, "modes_by_route": dict(reasons),
            "stepped_with_error_not_measured": flagged,
            "uncaught_all_flagged": all(m["error_not_measured"] for m in uncaught),
            "passed": counts == EXPECTED_MARKS and all(m["error_not_measured"] for m in uncaught)}


def pair_label_spread(mols: list[dict[str, str]]) -> dict[str, Any]:
    """Over the symmetry pairs the xtb labels name: how many, and the largest difference between a pair's two shifts."""
    pairs, worst = 0, {"difference_cm": 0.0}
    for mol in mols:
        with open(mol["x_label"], encoding="utf-8") as fh:
            label = json.load(fh)
        shift = np.asarray(label["nu_gvpt2"], float) - np.asarray(label["omega"], float)
        for i, j in label["degenerate_pairs"]:
            pairs += 1
            if abs(shift[i] - shift[j]) > worst["difference_cm"]:
                worst = {"difference_cm": float(abs(shift[i] - shift[j])), "id": mol["id"], "omega_cm": float(label["omega"][i]),
                         "shifts_cm": [float(shift[i]), float(shift[j])]}
    return {"pairs": pairs, "molecules_with_pairs": sum(bool(json.load(open(m["x_label"], encoding="utf-8"))["degenerate_pairs"]) for m in mols),
            "largest": worst}


def report(rec: dict[str, Any]) -> list[str]:
    """The record as the page beside it."""
    L = [f"# The anharmonic step, stage 1 — acceptance ({rec['date']}, TASKS 211)", "",
         f"Artefact `{rec['artefact']}` (written at commit {rec['artefact_commit'][:8]}); every molecule through "
         "`anharmonic_step.mode_steps` alone; this record by `probes/anharmonic_step_accept.py` at commit "
         f"{rec['commit'][:8]} (uncommitted changes: {rec['commit_dirty']}).", "",
         f"**{'PASSED' if rec['passed'] else 'FAILED'}**", "",
         "## 1. The route-A targets against the artefact's bars (cm⁻¹)", "",
         f"Pass: the step's rms within {rec['tolerance_cm']} of the artefact's own bar, within {rec['change_limit_cm']} of the "
         "registered bar, on the registered rows. The registered bar was read with one xtb mode per mode; the artefact's table "
         "is matched set-wise (TASKS 255).", "",
         "| family | rows | registered rows | rms of step − label | the artefact's bar | registered bar | registered match "
         "reproduced | from the registered | changed by the set-wise match | harmonic position | per molecule | |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for fa, t in rec["targets"].items():
        per = ", ".join(f"{i} {v:.2f}" for i, v in t["per_molecule"].items())
        L.append(f"| {fa} | {t['rows']} | {t['rows_registered']} | {t['rms_cm']:.4f} | {t['bar_refit_cm']:.4f} | {t['bar_cm']} | "
                 f"{t['bar_one_to_one_cm']:.4f} | {t['from_registered_cm']:+.4f} | "
                 f"{t['training_rows_added_by_the_set_wise_match']:+d} rows | "
                 f"{t['harmonic_rms_cm']:.2f} | {per} | {'pass' if t['passed'] else 'FAIL'} |")
    L += ["", "## 2. The modes only the B3LYP label marks", "",
          "| mode | ω (cm⁻¹) | family | o | step (cm⁻¹) | bar | error not measured | the label's shift | |", "|---|---|---|---|---|---|---|---|---|"]
    for name, f in rec["flagged"].items():
        step = "none" if f["delta_anh_cm"] is None else f"{f['delta_anh_cm']:.1f}"
        L.append(f"| {name} | {f['omega_cm']:.1f} | {f['family']} | {f['o']:.2f} | {step} | {f['bar_cm']} | "
                 f"{'yes' if f['error_not_measured'] else 'no'} | {f['label_shift_cm']:+.1f} | {'pass' if f['passed'] else 'FAIL'} |")
    m = rec["marks"]
    L += ["", f"## 3. The label-free rule over {m['molecules']} molecules, {m['modes']} modes", "",
          f"- modes a B3LYP label marks: {m['counts']['label_marked']}; of those without a step under the rule: {m['counts']['caught']} "
          f"(expected {m['expected']['caught']} of {m['expected']['label_marked']})",
          f"- modes no label marks that lose their step to an xtb partner's mark: {m['counts']['sound_lost']} "
          f"(expected {m['expected']['sound_lost']})",
          f"- the marked modes the rule misses all carry the 'error not measured' flag: {'yes' if m['uncaught_all_flagged'] else 'NO'}",
          f"- all modes by route: {m['modes_by_route']}; stepped modes with the flag: {m['stepped_with_error_not_measured']}", "",
          "| molecule | mode | ω | family | o | under the rule |", "|---|---|---|---|---|---|"]
    L += [f"| {x['id']} | {x['mode']} | {x['omega_cm']:.1f} | {x['family']} | {x['o']:.2f} | "
          f"{x['reason'] or ('step, error not measured' if x['error_not_measured'] else 'step')} |" for x in m["label_marked_modes"]]
    s, b = rec["xtb_pair_labels"], rec["bars"]
    L += [f"- **{'pass' if m['passed'] else 'FAIL'}**", "", "## 4. Stated, not checked", "",
          f"- **The printed bars.** {b['note']} Printed: {b['printed_cm']}; this table's own: {b['own_cm']}.",
          f"- **A degenerate pair in another basis.** The match gives the pair one shift in every basis when its two GFN2-xTB labels "
          f"are one number; where they differ the carried shift lies between them. Over {s['pairs']} symmetry pairs of "
          f"{s['molecules_with_pairs']} molecules the two labels differ by {s['largest']['difference_cm']:.3f} cm⁻¹ at most"
          + (f" ({s['largest']['id']} at {s['largest']['omega_cm']:.1f} cm⁻¹)." if s["pairs"] else "."), ""]
    return L


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--data-root", default=PLAN, help="the plan folder whose probes/results_m1 holds the force fields")
    ap.add_argument("--artefact", default=ARTEFACT)
    a = ap.parse_args()
    out, artefact_path = os.path.abspath(a.out), os.path.abspath(a.artefact)
    artefact = load_artefact(artefact_path)
    os.chdir(a.data_root)
    (target_mols, absent_targets), (training_mols, absent_training) = molecules(TARGETS), molecules(SETS)
    if absent_targets or sorted(m["id"] for m in training_mols) != artefact.header["training_molecules"]:
        raise SystemExit(f"the molecules on disk are not the artefact's: targets without a force field {absent_targets}, "
                         f"training molecules {len(training_mols)} against the artefact's {len(artefact.header['training_molecules'])}")
    targets = [through_step(m, artefact) for m in target_mols]
    training = [through_step(m, artefact) for m in training_mols]
    state = git_state(HERE)
    rec = {"date": time.strftime("%Y-%m-%d %H:%M"), "artefact": os.path.relpath(artefact_path, PLAN).replace(os.sep, "/"),
           "artefact_commit": artefact.header["commit"], "commit": state.get("commit", ""), "commit_dirty": state.get("dirty"),
           "tolerance_cm": TOLERANCE_CM, "change_limit_cm": CHANGE_LIMIT_CM, "selected_without_a_force_field": absent_training,
           "targets": check_targets(targets, artefact), "flagged": check_flagged(targets),
           "marks": check_marks([*training, *targets]), "bars": artefact.header["bars"],
           "xtb_pair_labels": pair_label_spread([*training_mols, *target_mols])}
    rec["passed"] = bool(all(t["passed"] for t in rec["targets"].values()) and all(f["passed"] for f in rec["flagged"].values())
                         and rec["marks"]["passed"])
    os.makedirs(out, exist_ok=True)
    write_atomic(os.path.join(out, "acceptance.json"), json.dumps(rec, indent=1, ensure_ascii=False))
    lines = report(rec)
    write_atomic(os.path.join(out, "acceptance.md"), "\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)
    return 0 if rec["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
