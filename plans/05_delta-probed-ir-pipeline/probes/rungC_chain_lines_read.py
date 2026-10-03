"""Read a rung-C chain record against its registered per-family lines (written 4 Oct 2026 00:2x for chain 34; the read is a script, not a model pass).

    python probes/rungC_chain_lines_read.py out/<prefix> <record.json> [--against <record.json>] [--line other<=3 --line ring-ip<=3 --line ratio<=0.25]
                                            [--cap 200]

Per hold-out (a) and (b): the seed mean and range of the corrected-ω rms per family, the coupling ratio, the all-mode ω and the ΔH residual ratio;
the best epochs against the cap (decision 51: a best epoch within 10 % of the cap means a re-run); every registered line as met / not met on hold-out
(a) with the number beside it; the same numbers for the record it is read against (the carried recipe) with the difference. Writes <prefix>.md and
<prefix>.json. Nothing here decides a model's registry status — that stays a reviewed entry in MODELS_STATUS.json.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")
STATS = {"ratio": "coupling_ratio", "omega": "corrected_freq_rms", "dH": "dH_residual_ratio"}


def summarise(path: Path) -> dict:
    rec = json.load(open(path, encoding="utf-8"))
    n = next(iter(rec["curve"]))
    ps = rec["curve"][n]["per_seed"]
    out = {"path": str(path), "n": int(n), "seeds": [s["seed"] for s in ps], "best_epoch": [s.get("best_epoch") for s in ps], "date": rec.get("date"),
           "model": rec.get("model"), "kdiag_mode": (rec.get("model") or {}).get("kdiag_mode") if isinstance(rec.get("model"), dict) else None}
    for h in ("a", "b"):
        blk = {}
        for f in FAMILIES:
            v = [s[h]["diag_rms"][f] for s in ps if f in s[h]["diag_rms"]]
            blk[f] = {"mean": float(np.mean(v)), "min": float(min(v)), "max": float(max(v))} if v else None
        for k, key in STATS.items():
            v = [s[h][key] for s in ps if key in s[h]]
            blk[k] = {"mean": float(np.mean(v)), "min": float(min(v)), "max": float(max(v))} if v else None
        out[h] = blk
    return out


def value(summary: dict, hold: str, name: str) -> float | None:
    e = summary[hold].get(name)
    return None if e is None else e["mean"]


def fmt(e) -> str:
    return "—" if e is None else f"{e['mean']:.2f} ({e['min']:.2f}–{e['max']:.2f})"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("record")
    ap.add_argument("--against", default=None, help="the record the chain is read against (the carried recipe)")
    ap.add_argument("--line", action="append", default=[], help="registered line, e.g. 'other<=3', 'ratio<=0.25' (hold-out (a))")
    ap.add_argument("--cap", type=int, default=200)
    a = ap.parse_args()
    s = summarise(Path(a.record))
    g = summarise(Path(a.against)) if a.against else None
    lines = []
    for spec in a.line:
        m = re.fullmatch(r"\s*([A-Za-z\-]+)\s*(<=|<|>=|>)\s*([0-9.]+)\s*", spec)
        if not m:
            raise SystemExit(f"line not understood: {spec!r}")
        name, op, lim = m.group(1), m.group(2), float(m.group(3))
        v = value(s, "a", name)
        ok = None if v is None else {"<=": v <= lim, "<": v < lim, ">=": v >= lim, ">": v > lim}[op]
        lines.append({"line": spec.strip(), "value": v, "met": ok})
    near_cap = [b for b in s["best_epoch"] if b is not None and b >= 0.9 * a.cap]
    md = [f"# Chain read against its lines — {datetime.now():%Y-%m-%d %H:%M}", "",
          f"Record: `{Path(a.record).name}` (run {s['date']}, n = {s['n']}, seeds {s['seeds']}, best epochs {s['best_epoch']} of {a.cap}"
          + (f", kdiag_mode `{s['kdiag_mode']}`" if s.get("kdiag_mode") else "") + ")."
          + (f" Against: `{Path(a.against).name}` (best epochs {g['best_epoch']})." if g else ""), ""]
    if near_cap:
        md.append(f"**Decision 51: best epoch within 10 % of the cap for seeds {near_cap} — a re-run with a higher cap is due before the read counts.**")
        md.append("")
    md += ["## Registered lines (hold-out (a))", ""]
    for ln in lines:
        md.append(f"- {ln['line']}: {'—' if ln['value'] is None else f'{ln['value']:.3f}'} → **{'met' if ln['met'] else 'not met' if ln['met'] is not None else 'no value'}**")
    md.append("")
    md.append(f"**All lines met: {'yes' if lines and all(ln['met'] for ln in lines) else 'no'}.**" if lines else "(no lines given)")
    md.append("")
    for h in ("a", "b"):
        md += [f"## Hold-out ({h}) — seed mean (seed range)", "", "| quantity | " + Path(a.record).stem[:40] + (" | against | difference |" if g else " |"),
               "|---|---|" + ("---|---|" if g else "")]
        for name in list(FAMILIES) + ["omega", "ratio", "dH"]:
            e = s[h].get(name); row = f"| {name} | {fmt(e)} |"
            if g:
                e2 = g[h].get(name)
                d = (e["mean"] - e2["mean"]) if (e and e2) else None
                row += f" {fmt(e2)} | {'—' if d is None else f'{d:+.2f}'} |"
            md.append(row)
        md.append("")
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "record": s, "against": g, "lines": lines, "all_met": bool(lines) and all(ln["met"] for ln in lines),
           "near_cap_seeds": near_cap, "cap": a.cap}
    Path(a.out_prefix + ".md").write_text("\n".join(md), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main())
