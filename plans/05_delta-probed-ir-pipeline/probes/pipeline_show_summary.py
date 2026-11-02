"""The runs the Atlas pipeline show links to, summarised for a written account (the blog post of 2 Nov 2026, TASKS 167).

Per run: the network's role towards the molecule (held out in (a) or (b), or in the catalogue only), its size, its error against the
ωB97X truth (rms of the positions paired by rank, spectrum overlap) and the corpus's time for steps 3–4; per role the median and the
largest error. Every value is read from the runs' own `certificate.json` and `pipeline.json`.

    python probes/pipeline_show_summary.py [--show website/export/out/pipeline_show.json] [--out <record.md>]
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
REPO = PLAN.parents[1]
RESULTS = PLAN / "probes" / "results_m1"
SHOW = REPO / "website" / "export" / "out" / "pipeline_show.json"


def run_row(mid: str, folder: Path) -> dict:
    """One show run's role, size, truth error and corpus time from its records."""
    cert = json.loads((folder / "certificate.json").read_text(encoding="utf-8"))
    rec = json.loads((folder / "pipeline.json").read_text(encoding="utf-8"))
    mol = cert["molecule"]
    if "truth" not in mol:
        raise ValueError(f"{mid}: the certificate has no ωB97X truth to measure against")
    return {"id": mid, "formula": mol["formula"], "atoms": mol["n_atoms"], "role": mol["seen"]["role"],
            "rms_cm": mol["truth"]["rms_by_rank_cm"], "overlap": mol["truth"]["overlap"],
            "version": rec["pipeline_version"],
            "corpus_s": rec["optimisation"]["timings_s"]["optimise"] + rec["low_level"]["b3lyp"]["seconds"],
            "laptop_s": sum(rec["seconds"].values())}


def role_line(role: str, rows: list[dict]) -> str:
    """Median and largest error of one role's runs."""
    rms = [r["rms_cm"] for r in rows]
    return (f"| {role} | {len(rows)} | {min(r['atoms'] for r in rows)}–{max(r['atoms'] for r in rows)} | {statistics.median(rms):.2f} | "
            f"{max(rms):.2f} | {statistics.median(r['overlap'] for r in rows):.3f} |")


def report(rows: list[dict]) -> str:
    """The record: one line per role, then the times and versions."""
    roles = sorted({r["role"] for r in rows})
    corpus = sorted(r["corpus_s"] for r in rows)
    lines = ["# The Atlas pipeline show's runs", "",
             "| role | runs | atoms | median rms (cm⁻¹) | largest rms (cm⁻¹) | median overlap |", "|---|---|---|---|---|---|"]
    lines += [role_line(role, [r for r in rows if r["role"] == role]) for role in roles]
    lines += ["", f"runs {len(rows)}; pipeline versions {sorted({r['version'] for r in rows})}",
              f"laptop seconds per run: {min(r['laptop_s'] for r in rows):.1f}–{max(r['laptop_s'] for r in rows):.1f}",
              f"corpus seconds for steps 3–4: {corpus[0]:.0f}–{corpus[-1]:.0f}, median {statistics.median(corpus):.0f}", "",
              "| id | formula | atoms | role | rms (cm⁻¹) | overlap |", "|---|---|---|---|---|---|"]
    lines += [f"| {r['id']} | {r['formula']} | {r['atoms']} | {r['role']} | {r['rms_cm']:.2f} | {r['overlap']:.3f} |"
              for r in sorted(rows, key=lambda r: (r["role"], r["id"]))]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--show", type=Path, default=SHOW)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    show = json.loads(args.show.read_text(encoding="utf-8"))
    text = report([run_row(mid, RESULTS / rel) for mid, rel in show["molecules"].items()])
    if args.out:
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, args.out)
    print(text, end="")


if __name__ == "__main__":
    main()
