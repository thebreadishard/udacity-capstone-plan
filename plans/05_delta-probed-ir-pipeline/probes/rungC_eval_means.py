"""Seed means (and ranges) of saved-model reads (`probes/rungC_eval_saved.py` jsons) per hold-out and family, beside a chain record's own numbers
(the trainer's json, finite-difference targets) — the mechanical read of chain 34 step 3 (5 Oct 2026: analytic hold-out (a) targets) and of any later
re-read of carried models. Writes <out_prefix>.md and .json.

    python probes/rungC_eval_means.py <out_prefix> <eval json> [<eval json> ...] [--against <chain record json>] [--line "CH-oop<=3" ...]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
QUANT = {"ratio": "coupling_ratio", "omega": "corrected_freq_rms", "dH": "dH_residual_ratio"}


def eval_numbers(path: Path, hold: str) -> dict:
    j = json.loads(path.read_text(encoding="utf-8"))[hold]
    out = {f: float(j["diag_rms"][f]) for f in FAMILIES if f in j["diag_rms"]}
    out.update({k: float(j[v]) for k, v in QUANT.items() if v in j})
    return out


def record_numbers(path: Path, hold: str) -> dict:
    rec = json.loads(path.read_text(encoding="utf-8")); n = next(iter(rec["curve"])); ps = rec["curve"][n]["per_seed"]
    out = {f: float(np.mean([s[hold]["diag_rms"][f] for s in ps if f in s[hold]["diag_rms"]])) for f in FAMILIES}
    out.update({k: float(np.mean([s[hold][v] for s in ps if v in s[hold]])) for k, v in QUANT.items()})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("evals", nargs="+")
    ap.add_argument("--against", default=None, help="the chain record whose (finite-difference) hold-out numbers stand beside the re-read")
    ap.add_argument("--line", action="append", default=[], help="registered line on hold-out (a), e.g. 'CH-oop<=3'")
    a = ap.parse_args()
    evals = [Path(p) for p in a.evals]
    res = {}
    for hold in ("a", "b"):
        per_seed = [eval_numbers(p, hold) for p in evals]
        keys = [k for k in per_seed[0] if all(k in s for s in per_seed)]
        res[hold] = {k: dict(mean=float(np.mean([s[k] for s in per_seed])), lo=float(min(s[k] for s in per_seed)), hi=float(max(s[k] for s in per_seed))) for k in keys}
    against = {hold: record_numbers(Path(a.against), hold) for hold in ("a", "b")} if a.against else None
    lines = {}
    for ln in a.line:
        k, v = ln.split("<=")
        lines[ln] = dict(value=res["a"][k.strip()]["mean"], met=res["a"][k.strip()]["mean"] <= float(v))
    sub = json.loads(evals[0].read_text(encoding="utf-8")).get("substituted_analytic", [])
    md = [f"# Saved-model re-read, seed means — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Evals: {', '.join(p.name for p in evals)}; analytic targets substituted for {len(sub)} molecules" + (f"; against `{Path(a.against).name}` (its own targets)." if a.against else ".")]
    if lines:
        md += ["", "## Lines (hold-out a)", ""] + [f"- {ln}: {d['value']:.3f} → **{'met' if d['met'] else 'not met'}**" for ln, d in lines.items()]
    for hold in ("a", "b"):
        md += ["", f"## Hold-out ({hold}) — seed mean (seed range)" + (" and the record's number" if against else ""), "",
               "| quantity | re-read | " + ("record | difference |" if against else "") , "|---|---|" + ("---|---|" if against else "")]
        for k, d in res[hold].items():
            fmt = (lambda v: f"{v:.3f}") if k in ("ratio", "dH") else (lambda v: f"{v:.2f}")
            row = f"| {k} | {fmt(d['mean'])} ({fmt(d['lo'])}–{fmt(d['hi'])}) |"
            if against and k in against[hold]:
                row += f" {fmt(against[hold][k])} | {d['mean'] - against[hold][k]:+.2f} |"
            md.append(row)
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(dict(date=datetime.now().strftime("%Y-%m-%d %H:%M"), evals=[str(p) for p in evals], against=a.against,
                                                            substituted_analytic=sub, results=res, record=against, lines=lines), indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
