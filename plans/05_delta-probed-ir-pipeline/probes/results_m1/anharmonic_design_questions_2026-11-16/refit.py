"""Refit x2* from the force fields on disk with the repository's own read, and set the result beside the registered bars.

    python refit.py

For each window (mid, ch) it takes the S2b read and the S3 read that route_rule*.json names, reloads the training molecules and the
targets through probes/s3_read.load_scope with the marked policy of the registered read, calls probes/s3_read.read_targets, and
compares every family's verdict-model rms with the stored read. Writes refit.json beside itself.
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "src"))
from s2_read import WINDOWS, window_size, write_atomic  # noqa: E402
from s3_read import MAIN_SCOPE, label_notes, load_scope, read_targets  # noqa: E402

LABELS = "probes/results_m1/labels_domain_2026-11-13"
ROUTE_RULES = {"mid": f"{LABELS}/route_rule/route_rule.json", "ch": f"{LABELS}/route_rule/route_rule_ch.json"}
SETS, TARGETS = f"{LABELS}/sets.json", f"{LABELS}/S3_targets/targets.json"


def refit_window(name: str) -> dict:
    """One window's refit: sizes, and per family the reproduced and the stored rms of the verdict model."""
    with open(ROUTE_RULES[name], encoding="utf-8") as fh:
        rule = json.load(fh)
    with open(rule["s2b_read"], encoding="utf-8") as fh:
        s2b = json.load(fh)
    with open(rule["s3_read"], encoding="utf-8") as fh:
        stored = json.load(fh)
    window, policy = WINDOWS[name], stored["marked_policy"]
    train, _, excluded_train, _ = load_scope(SETS, policy, window)
    targets, _, excluded_targets, _ = load_scope(TARGETS, policy, window)
    read = read_targets(train, targets, s2b["scopes"][MAIN_SCOPE]["read"], label_notes(TARGETS), window)
    families = {}
    for fa, entry in read["families"].items():
        model = entry.get("verdict_model")
        if model is None:
            continue
        old = stored["read"]["families"][fa]
        families[fa] = {"model": model, "x2_config": s2b["scopes"][MAIN_SCOPE]["read"].get("x2_choice", {}).get(fa),
                        "n": entry["n"], "n_stored": old["n"], "rms_refit": entry["rms"][model], "rms_stored": old["rms"][model],
                        "printed_bar": rule["printed"][fa]["bar_cm"],
                        "per_molecule_refit": {t: v[model] for t, v in entry["per_molecule"].items()}}
    return {"s2b_read": rule["s2b_read"], "s3_read": rule["s3_read"], "marked_policy": policy,
            "train": window_size(train, window), "targets": window_size(targets, window),
            "excluded": {**excluded_train, **excluded_targets}, "families": families}


def main() -> int:
    """Refit both windows from the plan folder and print the comparison."""
    os.chdir(PLAN)
    out = {name: refit_window(name) for name in ROUTE_RULES}
    write_atomic(os.path.join(HERE, "refit.json"), json.dumps(out, indent=1, default=float))
    for name, res in out.items():
        print(f"{name}: train {res['train']['molecules']} force fields, {res['train']['per_family']}; "
              f"targets {res['targets']['per_family']}; excluded {res['excluded']}")
        for fa, f in res["families"].items():
            print(f"  {fa}: {f['model']} ({f['x2_config']}) n {f['n']} refit {f['rms_refit']:.4f} stored {f['rms_stored']:.4f} "
                  f"printed {f['printed_bar']} diff {abs(f['rms_refit'] - f['rms_stored']):.2e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
