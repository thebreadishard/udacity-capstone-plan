"""Which corpus folders the pipeline can reuse (TASKS 150, `m08/reuse.py`), and why the others are computed: every done manifest row through
`reuse.assess` with the pipeline's settings and its own start. The start-to-start fit distances set `reuse.SAME_START_ANGSTROM`.

    python probes/pipeline_reuse_survey.py --corpus <module 05's corpus folder> --out <folder>
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "08_industry_synthesis"))
from m08 import pipeline as P  # noqa: E402
from m08 import reuse as R  # noqa: E402

UNLIMITED = 1e9


def reason_class(why: str) -> str:
    """A refusal without the folder's name and numbers, so that equal reasons count together."""
    return re.sub(r"\d[\d.e+-]*", "#", re.sub(r"^[A-Za-z0-9_]+:? ", "", why))[:110]


def survey(corpus: Path) -> list[dict]:
    with (corpus / "manifest.csv").open(encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.DictReader(fh) if r["status"] == "done"]
    out = []
    for r in rows:
        if r["layer"] == "C":
            out.append({"id": r["id"], "reused": False, "why": ["layer C: the QM9 geometry, not a SMILES start"]})
            continue
        canonical = P.canonical_smiles(r["smiles"])
        xyz, _ = P.RC.start_geometry({"layer": "A", "smiles": canonical})
        start = R.Start(np.asarray([row[1:] for row in xyz], float), P.RC.opt_options_for({"smiles": canonical}))
        rec = R.assess(canonical, start, corpus, P.REUSE_SETTINGS)
        out.append({"id": r["id"], "layer": r["layer"], "smiles": r["smiles"], "canonical_written": canonical == r["smiles"]} | rec)
    return out


def summary(recs: list[dict]) -> dict:
    reasons = collections.Counter(reason_class(r["why"][-1]) for r in recs if not r["reused"])
    fits = sorted((r["start_rmsd_angstrom"], r["id"]) for r in recs if "start_rmsd_angstrom" in r)
    d = np.array([f for f, _ in fits])
    reordered = sum(1 for r in recs if r["reused"] and r["order"] != sorted(r["order"]))
    return {"rows": len(recs), "reused": sum(r["reused"] for r in recs), "reused_with_atoms_reordered": reordered,
            "first_refusal_reasons": dict(reasons.most_common()),
            "start_rmsd_angstrom": {"n": len(d), "median": float(np.median(d)), "p95": float(np.quantile(d, 0.95)),
                                    "p99": float(np.quantile(d, 0.99)), "max": float(d.max()), "largest": fits[-10:]} if len(d) else None,
            "limit_angstrom": R.SAME_START_ANGSTROM}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args(argv)
    R.SAME_START_ANGSTROM = UNLIMITED         # the survey measures the spread the limit is set from
    t = time.time()
    recs = survey(a.corpus)
    s = summary(recs) | {"seconds": round(time.time() - t, 1), "corpus": str(a.corpus)}
    s["limit_angstrom"] = "unlimited in the survey"
    a.out.mkdir(parents=True, exist_ok=True)
    for name, obj in (("pipeline_reuse_survey.json", {"summary": s, "molecules": recs}),):
        tmp = a.out / (name + ".tmp")
        tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, a.out / name)
    print(json.dumps(s, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
