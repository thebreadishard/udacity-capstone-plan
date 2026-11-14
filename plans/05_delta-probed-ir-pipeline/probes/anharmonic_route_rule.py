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
from s2_read import LINE_LICENSE, WINDOWS, window_record, write_atomic  # noqa: E402
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


def window_of(s2b_read: dict[str, Any]) -> tuple[list[float | None], str]:
    """The window a read worked in, and its name, as a record may state them.

    A read written before 14 November 2026 records neither, because the window was a module constant then - the 550-2000 cm-1 one,
    for every read there was. That is said here rather than left as a null for a later reader to guess at.
    """
    if "window" in s2b_read:
        return window_record(tuple(s2b_read["window"])), s2b_read.get("window_name") or "not named by that read"
    return list(WINDOWS["mid"]), "mid (not recorded: that read predates the setting, when 550-2000 was the only window)"


def printed_for_family(s2b_verdict: dict[str, Any] | None, s3_entry: dict[str, Any] | None,
                       harmonic_cm: float | None) -> dict[str, Any]:
    """What the pipeline prints for one family, and why (PreRegistration_2026-11-14_Printed_Band_Position.md).

    The printed estimate is the family's S2b verdict model with its measured target rms as the stated bar - not as a licence, which
    is `route_for_family`'s question and a stricter one. A family the targets cannot judge at size gets no step, as rule 4 of the
    route rule says; and a step that does not beat the harmonic position is not printed, because printing a worse estimate than the
    one we would otherwise print is the one thing the registration forbids.
    """
    if s3_entry is None or s3_entry["n"] < MIN_MODES:
        n = 0 if s3_entry is None else s3_entry["n"]
        return {"model": None, "bar_cm": None, "reason": f"not checked at size: {n} target mode(s) < {MIN_MODES}"}
    if s2b_verdict is None:
        return {"model": None, "bar_cm": None, "reason": "no S2b verdict for this family"}
    model = s2b_verdict["best_curve_model"]
    bar = s3_entry["rms"].get(model, math.nan)
    if math.isnan(bar):
        return {"model": None, "bar_cm": None,
                "reason": f"the verdict model {model} gave no prediction on the targets, so there is nothing to print"}
    if harmonic_cm is None or not bar < harmonic_cm:
        return {"model": None, "bar_cm": None,
                "reason": f"the step does not beat the harmonic position: {model} {bar:.2f} against {harmonic_cm:.2f}"
                          if harmonic_cm is not None else "the harmonic position's own error is not known for this family"}
    return {"model": model, "bar_cm": bar, "harmonic_cm": harmonic_cm, "beats_harmonic_by_cm": harmonic_cm - bar,
            "reason": f"{model} {bar:.2f} against the harmonic position's {harmonic_cm:.2f} cm-1, "
                      f"{harmonic_cm / bar:.1f} times better; no licence is claimed"}


def printed_rule(s2b_read: dict[str, Any], s3_read: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Every family's printed estimate, from the same two reads the licensing rule uses."""
    verdicts = s2b_read["scopes"][MAIN_SCOPE]["read"]["verdicts"]
    families = s3_read["read"]["families"]
    harmonic = no_shift_rms(s3_read)
    return {fa: printed_for_family(verdicts.get(fa), families.get(fa), harmonic.get(fa))
            for fa in sorted(set(verdicts) | set(families))}


def route_rule(s2b_read: dict[str, Any], s3_read: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Every family that S2b's main scope or S3's targets name."""
    verdicts = s2b_read["scopes"][MAIN_SCOPE]["read"]["verdicts"]
    families = s3_read["read"]["families"]
    return {fa: route_for_family(verdicts.get(fa), families.get(fa)) for fa in sorted(set(verdicts) | set(families))}


def no_shift_rms(s3_read: dict[str, Any]) -> dict[str, float]:
    """Per family, the rms of the true shift over the target modes the read kept: the error a harmonic position carries."""
    truths: dict[str, list[float]] = {}
    for rows in s3_read["read"]["rows"].values():
        for family, truth in zip(rows["family"], rows["truth"], strict=True):
            truths.setdefault(family, []).append(truth)
    return {fa: math.sqrt(math.fsum(t * t for t in ts) / len(ts)) for fa, ts in truths.items()}


def printed_lines(printed: dict[str, dict[str, Any]]) -> list[str]:
    """The printed table: what the pipeline puts on a band, and the bar it states (TASKS 211, registered 14 Nov 2026)."""
    lines = ["", "## What the pipeline prints", "",
             "Registration: `GoalGathering/notes/PreRegistration_2026-11-14_Printed_Band_Position.md`. A printed estimate states a "
             "measured bar; it claims no licence, which is the table above and a stricter question.", "",
             "| family | printed | bar (cm⁻¹) | harmonic position (cm⁻¹) | why |", "|---|---|---|---|---|"]
    for fa, p in sorted(printed.items()):
        bar = "—" if p["bar_cm"] is None else f"{p['bar_cm']:.2f}"
        plain = "—" if p.get("harmonic_cm") is None else f"{p['harmonic_cm']:.2f}"
        lines.append(f"| {fa} | {p['model'] or 'harmonic position'} | {bar} | {plain} | {p['reason']} |")
    return lines


def report(res: dict[str, dict[str, Any]], printed: dict[str, dict[str, Any]], s3_read: dict[str, Any]) -> list[str]:
    """The rule's reading: per family its route, error bar and reason, with the per-target numbers behind it, and what is printed."""
    families, targets = s3_read["read"]["families"], s3_read["targets"]
    lines = [f"# The anharmonic route per family (TASKS 178, step 1), line {LINE_LICENSE} cm⁻¹", "",
             "Rule: `GoalGathering/notes/PreRegistration_2026-11-04_Anharmonic_Route_Rule.md`, registered before either read.",
             f"S3's read: {s3_read['registration']}, marked-mode policy `{s3_read.get('marked_policy', '—')}`.", "",
             "| family | n | route | error bar | verdict model | " + " | ".join(targets) + " | harmonic position | reason |",
             "|---|---|---|---|---|" + "---|" * (len(targets) + 2)]
    harmonic = no_shift_rms(s3_read)
    for fa, r in res.items():
        entry = families.get(fa)
        model = (entry or {}).get("verdict_model", "—")
        per = [f"{entry['per_molecule'][t][model]:.2f}" if entry and model in entry.get("per_molecule", {}).get(t, {}) else "—"
               for t in targets]
        bar = "—" if r["error_bar_cm"] is None else f"{r['error_bar_cm']:.2f}"
        plain = f"{harmonic[fa]:.2f}" if fa in harmonic else "—"
        lines.append(f"| {fa} | {entry['n'] if entry else 0} | {r['route'] or 'no step'} | {bar} | {model} | "
                     + " | ".join(per) + f" | {plain} | {r['reason']} |")
    licensed = [fa for fa, r in res.items() if r["route"]]
    lines += ["", "Licensed, an anharmonic step in the pipeline: "
              + (", ".join(licensed) if licensed
                 else "no family. Every band keeps its harmonic position with the pipeline's HARMONIC_NOTE."),
              "", "The last column is the rms of the true shift over the same modes, the error a harmonic position carries. It is not "
              "part of the rule, which was registered on 4 November and reads as it reads; it is there so a reader can see what the "
              "rule's outcome costs per family."]
    return lines + printed_lines(printed)


def main(argv: list[str] | None = None) -> int:
    """Command line."""
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--s2b-read", required=True)
    ap.add_argument("--s3-read", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    with open(a.s2b_read, encoding="utf-8") as f2, open(a.s3_read, encoding="utf-8") as f3:
        s2b, s3 = json.load(f2), json.load(f3)
    licensed, printed = route_rule(s2b, s3), printed_rule(s2b, s3)
    # through window_of, never copied: a read written before it carries Infinity, which no JSON reader outside Python
    # accepts, or no window at all (14 Nov 2026, the independent review)
    window, window_name = window_of(s2b)
    record = {"licence_registration": "PreRegistration_2026-11-04_Anharmonic_Route_Rule.md",
              "printed_registration": "PreRegistration_2026-11-14_Printed_Band_Position.md",
              "s2b_read": a.s2b_read, "s3_read": a.s3_read,
              "window": window, "window_name": window_name,
              "licensed": licensed, "printed": printed}
    write_atomic(a.out, json.dumps(record, indent=1))
    write_atomic(os.path.splitext(a.out)[0] + ".md", "\n".join(report(licensed, printed, s3)) + "\n")
    for fa in sorted(set(licensed) | set(printed)):
        step = printed[fa]["model"] or "no step"
        print(f"{fa}: licensed {licensed[fa]['route'] or 'no'}, printed {step} — {printed[fa]['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
