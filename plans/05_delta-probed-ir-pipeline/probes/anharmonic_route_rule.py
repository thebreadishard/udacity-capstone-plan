"""TASKS 178's route rule (GoalGathering/notes/PreRegistration_2026-11-04_Anharmonic_Route_Rule.md): per family, which anharmonic shift
model the pipeline carries, from S2b's read (the verdict model, chosen at 'all' by leave-one-scaffold-out) and S3's read (the check on
route A's targets).

    python anharmonic_route_rule.py --s2b-read <s2b_read.json> --s3-read <s3_read.json> --out <route_rule.json>

The reading is written beside the record, as `<out>` with a `.md` suffix.

A family gets S2b's verdict model when S3's transfer line holds for it; otherwise the family mean (c) when (c)'s own target rms meets the
same line; otherwise no anharmonic step (the band stays harmonic). A family S3 cannot judge (fewer than MIN_MODES target modes, or no S2b
verdict) gets no step. The error bar is the chosen model's rms on the targets.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s2_read import LINE_LICENSE, write_atomic  # noqa: E402
from s2b_read import READ_SCOPES  # noqa: E402
from s3_read import MIN_MODES, transfer_holds  # noqa: E402

MAIN_SCOPE = READ_SCOPES[0]


def route_for_family(s2b_verdict: dict[str, Any] | None, s3_entry: dict[str, Any] | None) -> dict[str, Any]:
    """The route, its error bar and the reason for one family."""
    if s3_entry is None or s3_entry["n"] < MIN_MODES:
        n = 0 if s3_entry is None else s3_entry["n"]
        return {"route": None, "error_bar_cm": None, "reason": f"not checked at size: {n} target mode(s) < {MIN_MODES}"}
    if s2b_verdict is None:
        return {"route": None, "error_bar_cm": None, "reason": "no S2b verdict for this family"}
    rms = s3_entry["rms"]
    model = s2b_verdict["best_curve_model"]
    r_model, r_c = rms.get(model, math.nan), rms["c"]
    if model != "c" and transfer_holds(r_model, r_c):
        return {"route": model, "error_bar_cm": r_model, "reason": f"S3's line holds: {model} {r_model:.2f} ≤ {LINE_LICENSE}, below (c) {r_c:.2f}"}
    if r_c <= LINE_LICENSE:
        return {"route": "c", "error_bar_cm": r_c,
                "reason": f"the verdict model {model} does not carry ({r_model:.2f}); (c) {r_c:.2f} ≤ {LINE_LICENSE} on the targets"}
    return {"route": None, "error_bar_cm": None,
            "reason": f"neither carries: {model} {r_model:.2f}, (c) {r_c:.2f} against {LINE_LICENSE}"}


def route_rule(s2b_read: dict[str, Any], s3_read: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Every family that S2b's main scope or S3's targets name."""
    verdicts = s2b_read["scopes"][MAIN_SCOPE]["read"]["verdicts"]
    families = s3_read["read"]["families"]
    return {fa: route_for_family(verdicts.get(fa), families.get(fa)) for fa in sorted(set(verdicts) | set(families))}


def report(res: dict[str, dict[str, Any]], s3_read: dict[str, Any]) -> list[str]:
    """The rule's reading: per family its route, error bar and reason, with the per-target numbers behind it."""
    families, targets = s3_read["read"]["families"], s3_read["targets"]
    lines = [f"# The anharmonic route per family (TASKS 178, step 1), line {LINE_LICENSE} cm⁻¹", "",
             "Rule: `GoalGathering/notes/PreRegistration_2026-11-04_Anharmonic_Route_Rule.md`, registered before either read.",
             f"S3's read: {s3_read['registration']}, marked-mode policy `{s3_read.get('marked_policy', '—')}`.", "",
             "| family | n | route | error bar | verdict model | " + " | ".join(targets) + " | reason |",
             "|---|---|---|---|---|" + "---|" * (len(targets) + 1)]
    for fa, r in res.items():
        entry = families.get(fa)
        model = (entry or {}).get("verdict_model", "—")
        per = [f"{entry['per_molecule'][t][model]:.2f}" if entry and model in entry.get("per_molecule", {}).get(t, {}) else "—"
               for t in targets]
        bar = "—" if r["error_bar_cm"] is None else f"{r['error_bar_cm']:.2f}"
        lines.append(f"| {fa} | {entry['n'] if entry else 0} | {r['route'] or 'no step'} | {bar} | {model} | "
                     + " | ".join(per) + f" | {r['reason']} |")
    licensed = [fa for fa, r in res.items() if r["route"]]
    lines += ["", "Licensed, an anharmonic step in the pipeline: "
              + (", ".join(licensed) if licensed
                 else "no family. Every band keeps its harmonic position with the pipeline's HARMONIC_NOTE.")]
    return lines


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--s2b-read", required=True)
    ap.add_argument("--s3-read", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(a.s2b_read, encoding="utf-8") as f2, open(a.s3_read, encoding="utf-8") as f3:
        s2b, s3 = json.load(f2), json.load(f3)
    res = route_rule(s2b, s3)
    write_atomic(a.out, json.dumps(res, indent=1))
    write_atomic(os.path.splitext(a.out)[0] + ".md", "\n".join(report(res, s3)) + "\n")
    for fa, r in res.items():
        print(f"{fa}: {r['route'] or 'no anharmonic step'} — {r['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
