"""The step's two real runs again, offline, with the set-wise match (TASKS 255): nothing is computed and nothing is written into a run's folder.

    python replay_runs.py [--data-root <plan folder holding the runs' saved files>]

Per run (benzene, 17 Nov 2026: a degenerate pair lost to 'no-xtb-partner'; benzonitrile: four bands without a partner) the saved
files are read — the geometry, the B3LYP Hessian, the correction ΔH, the run's own GFN2-xTB force field with its GVPT2 label, the
recorded sticks — and the step's own functions are called in the order `m08.anharmonic.step` calls them, with the committed
artefact: `mode_steps`, `agree_on_family`, `carry_to_bands`. Beside every band's step the run's saved record (`anharmonic.json`,
made with the one-to-one match and format 2 of the artefact) and, for every mode the one-to-one match refuses, its near-degenerate
set and the overlap with the set's partners: refused for its basis, or mixed for real.

Writes replay_runs.json and replay_runs.txt beside itself.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

HERE = Path(__file__).resolve().parent
PLAN = HERE.parents[2]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import anharmonic as AN  # noqa: E402
from m08 import pipeline as P  # noqa: E402

# isort: split
import anharmonic_step as AS  # noqa: E402  probes/, on the path through m08.pipeline
import s2_xtb_read as X  # noqa: E402

RUNS = {"benzene": "probes/results_m1/pipeline_benzene_anharmonic_first_run/benzene",
        "benzonitrile": "probes/results_m1/pipeline_benzonitrile_anharmonic_second_run/benzonitrile"}
FRAGILE_BENZENE_CM = (621.9, 1068.8, 1207.7, 1531.1, 1655.3)      # B3LYP positions of the pairs TASKS 255 names (1655 is the lost one)


def write_atomic(path: Path, text: str) -> None:
    """The text into a temp file, moved over the target."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def refused_modes(modes: AS.Modes, xtb: AS.XtbField) -> list[dict[str, Any]]:
    """Every B3LYP mode the one-to-one match refuses: its overlap, its near-degenerate set and what the set-wise match reads."""
    _, single = X.match_modes(modes.q, xtb.q, 0.0)
    match = X.match_sets(modes.omega, modes.q, xtb.q)
    sets = X.mode_sets(modes.omega, X.SET_TOLERANCE_CM)
    out = []
    for i in np.flatnonzero(single < X.MIN_OVERLAP):
        members = np.flatnonzero(sets == sets[i])
        out.append({"mode": int(i), "omega_cm": float(modes.omega[i]), "one_to_one": float(single[i]),
                    "set_omega_cm": [float(modes.omega[k]) for k in members], "set_overlap": float(match.overlap[i]),
                    "verdict": "refused for its basis: matched as a set" if match.set_wise[i] else
                               ("alone in its set: mixed for real" if len(members) == 1 else "in a set, and its partners do not hold it")})
    return out


def replay(name: str, folder: Path, artefact: AS.Artefact) -> dict[str, Any]:
    """One run's bands through the step's functions, beside the run's saved record."""
    symbols, coords, masses = AN.geometry(folder)
    H_low = AN.low_hessian(folder)
    with np.load(folder / P.CORRECTION) as z:
        dH = np.asarray(z["dH"], float)
    sticks = json.loads((folder / "pipeline.json").read_text(encoding="utf-8"))["spectra"]["network"]["sticks"]
    saved = json.loads((folder / AN.RECORD).read_text(encoding="utf-8"))
    modes = AN.b3lyp_modes(symbols, coords, H_low, artefact)
    xtb = AS.XtbField.from_folder(str(folder / AN.FOLDER / "xtb" / name / "X"), str(folder / AN.FOLDER / "gvpt2_x" / f"{name}.json"))
    steps = AS.agree_on_family(AS.mode_steps(modes, xtb, artefact), AN.certificate_families(folder, H_low, modes.omega))
    bands = AS.carry_to_bands(*AN.corrected_modes(H_low + dH, masses, sticks), modes.q, steps)
    rows = []
    for stick, band, old in zip(sticks, bands, saved["bands"], strict=True):
        mode = None if band.mode is None else steps[band.mode]
        rows.append({"omega_cm": stick["omega_cm"], "b3lyp_mode": band.mode, "b3lyp_omega_cm": None if mode is None else mode.omega_cm,
                     "xtb_overlap": None if mode is None else mode.xtb_overlap, "band_overlap": band.overlap,
                     "band_set_wise": band.set_wise, "delta_anh_cm": band.delta_anh_cm, "reason": band.reason,
                     "saved_delta_anh_cm": old["delta_anh_cm"], "saved_reason": old["reason"]})
    both = [abs(r["delta_anh_cm"] - r["saved_delta_anh_cm"]) for r in rows if r["delta_anh_cm"] is not None and r["saved_delta_anh_cm"] is not None]
    return {"folder": RUNS[name], "bands": len(rows), "stepped_saved": saved["summary"]["bands"]["stepped"],
            "stepped_now": AN.counts(bands)["stepped"], "no_step_saved": saved["summary"]["bands"]["no_step"],
            "no_step_now": AN.counts(bands)["no_step"],
            "gained": [r for r in rows if r["saved_delta_anh_cm"] is None and r["delta_anh_cm"] is not None],
            "lost": [r for r in rows if r["saved_delta_anh_cm"] is not None and r["delta_anh_cm"] is None],
            "largest_change_of_a_step_both_have_cm": max(both, default=0.0),
            "modes_refused_one_to_one": refused_modes(modes, xtb), "rows": rows}


def lines_of(name: str, r: dict[str, Any]) -> list[str]:
    """One run's part of the text record."""
    out = [f"## {name} ({r['folder']})", "",
           f"bands stepped: {r['stepped_saved']} of {r['bands']} in the run's record -> {r['stepped_now']} of {r['bands']} now; "
           f"without a step: {r['no_step_saved']} -> {r['no_step_now']}",
           f"bands that gained a step: {[(x['omega_cm'], round(x['delta_anh_cm'], 2)) for x in r['gained']]}; that lost one: "
           f"{[x['omega_cm'] for x in r['lost']]}",
           f"largest change of a step both records have: {r['largest_change_of_a_step_both_have_cm']:.3f} cm-1 (format 3 of the "
           "artefact against format 2: one more training row)", "", "modes the one-to-one match refuses:"]
    out += [f"  mode {m['mode']} at {m['omega_cm']:.2f}: one to one {m['one_to_one']:.3f}; set {[round(w, 2) for w in m['set_omega_cm']]}, "
            f"overlap with the set's partners {m['set_overlap']:.3f} - {m['verdict']}" for m in r["modes_refused_one_to_one"]]
    if name == "benzene":
        out += ["", "the pairs TASKS 255 names (B3LYP position; overlap of the match; step now; step in the run's record):"]
        for x in r["rows"]:
            if x["b3lyp_omega_cm"] is not None and min(abs(x["b3lyp_omega_cm"] - w) for w in FRAGILE_BENZENE_CM) < 0.5:
                was = "none" if x["saved_delta_anh_cm"] is None else f"{x['saved_delta_anh_cm']:.2f}"
                out.append(f"  band {x['omega_cm']} <- mode at {x['b3lyp_omega_cm']:.2f}: {x['xtb_overlap']:.3f}; {x['delta_anh_cm']:.2f}; "
                           f"{was} ({x['saved_reason'] or 'stepped'})")
    return [*out, ""]


def main() -> int:
    """Replay both runs, write the two records and print the text."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data-root", type=Path, default=PLAN, help="the plan folder whose probes/results_m1 holds the runs' saved files")
    a = ap.parse_args()
    artefact = AS.load_artefact()
    res = {"artefact": Path(AS.ARTEFACT).name, "match": artefact.header["match"],
           "runs": {name: replay(name, a.data_root / rel, artefact) for name, rel in RUNS.items()}}
    write_atomic(HERE / "replay_runs.json", json.dumps(res, indent=1, ensure_ascii=False))
    text = [f"# The two real runs replayed offline with the set-wise match ({res['artefact']}, {res['match']})", ""]
    for name, r in res["runs"].items():
        text += lines_of(name, r)
    write_atomic(HERE / "replay_runs.txt", "\n".join(text) + "\n")
    print("\n".join(text), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
