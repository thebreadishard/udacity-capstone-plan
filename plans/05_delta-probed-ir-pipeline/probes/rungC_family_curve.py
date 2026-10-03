"""Per-family learning curve from existing rung-C records (3 Oct 2026, decision 53): which mode families still learn with data and which stand still.

Reads the hold-out (a) and (b) per-family corrected-ω rms (`diag_rms`) per seed from the records of one recipe at several pool sizes and prints, per
family and size, the mean and the seed range; then the fall per step. Nothing is trained; the records are the chains already read (and recorded in
the pre-registration). A record whose recipe differs is passed with a flag in its label and read beside the series, never inside it.

    python probes/rungC_family_curve.py out/<prefix> 175=out/E7_rungC_carried_mixed175_2026-10-01.json 449=out/E7_rungC_carried_449_2026-10-01.json ...
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np

FAMILIES = ("ring-ip", "CH-stretch", "CH-oop", "other")


def read(path: Path) -> dict:
    d = json.load(open(path, encoding="utf-8"))
    out = {}
    for n, blk in d["curve"].items():
        for split in ("a", "b"):
            vals = {f: [ps[split]["diag_rms"][f] for ps in blk["per_seed"] if f in ps[split]["diag_rms"]] for f in FAMILIES}
            omega = [ps[split]["corrected_freq_rms"] for ps in blk["per_seed"]]
            ratio = [ps[split]["coupling_ratio"] for ps in blk["per_seed"]]
            out[(int(n), split)] = {"fam": vals, "omega": omega, "ratio": ratio}
    return out


def fmt(v: list) -> str:
    return f"{np.mean(v):.2f} ({min(v):.2f}–{max(v):.2f})" if v else "—"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("out_prefix")
    ap.add_argument("records", nargs="+", help="label=path; a label with a suffix in brackets, e.g. '750[+kdiag]', is read beside the series")
    a = ap.parse_args()
    series, beside = [], []
    for item in a.records:
        label, path = item.split("=", 1)
        data = read(Path(path))
        n = int(label.split("[")[0])
        key = next(k for k in data if k[0] == n and k[1] == "a")
        entry = {"label": label, "n": n, "path": path, "a": data[(n, "a")], "b": data[(n, "b")]}
        (beside if "[" in label else series).append(entry)
    series.sort(key=lambda e: e["n"])
    lines = [f"# Per-family learning curve from existing records — {datetime.now():%Y-%m-%d %H:%M}", "",
             "Series (one recipe): " + ", ".join(f"{e['label']} (`{Path(e['path']).name}`)" for e in series) + ". Beside: " + (", ".join(f"{e['label']} (`{Path(e['path']).name}`)" for e in beside) or "none") + ".", ""]
    res = {"date": datetime.now().strftime("%Y-%m-%d %H:%M"), "series": [], "beside": []}
    for split in ("a", "b"):
        lines += [f"## Hold-out ({split}) — corrected-ω rms per family (cm⁻¹), mean over seeds (seed range)", "",
                  "| n | " + " | ".join(FAMILIES) + " | all-mode ω | ratio |", "|---|" + "---|" * (len(FAMILIES) + 2)]
        for e in series + beside:
            r = e[split]
            lines.append(f"| {e['label']} | " + " | ".join(fmt(r["fam"][f]) for f in FAMILIES) + f" | {fmt(r['omega'])} | {fmt(r['ratio'])} |")
        lines.append("")
        if len(series) >= 2:
            lines += ["Fall per step (mean, cm⁻¹; positive = the family improved with more molecules):", ""]
            for lo, hi in zip(series, series[1:], strict=False):
                falls = {f: float(np.mean(lo[split]["fam"][f]) - np.mean(hi[split]["fam"][f])) for f in FAMILIES if lo[split]["fam"][f] and hi[split]["fam"][f]}
                lines.append(f"- {lo['label']} → {hi['label']}: " + ", ".join(f"{f} {v:+.2f}" for f, v in falls.items()))
                res.setdefault(f"falls_{split}", []).append({"from": lo["n"], "to": hi["n"], **falls})
            lines.append("")
    for e in series:
        res["series"].append({"label": e["label"], "n": e["n"], "path": e["path"], "a": {f: e["a"]["fam"][f] for f in FAMILIES}, "b": {f: e["b"]["fam"][f] for f in FAMILIES}})
    for e in beside:
        res["beside"].append({"label": e["label"], "n": e["n"], "path": e["path"], "a": {f: e["a"]["fam"][f] for f in FAMILIES}, "b": {f: e["b"]["fam"][f] for f in FAMILIES}})
    Path(a.out_prefix + ".md").write_text("\n".join(lines), encoding="utf-8")
    Path(a.out_prefix + ".json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
