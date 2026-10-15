"""Rung 4's registered read (TASKS 61; GoalGathering/notes/PreRegistration_2026-10-14_Rung4_Broad_Set.md), written 15 Oct 2026 before any
rung-4 label. Input: the per-seed rungC_eval_saved records of the four trainings k = 0, 10, 20, 30 (rows per training family), each read with
`--eval-ids-file tetracene=out/rung4_tetracene.txt`.

e(k) per band family = the record's per-family read-out on tetracene, `diag_rms[F]` (the predicted against the true diagonal of the correction
in the mode basis, cm⁻¹ — the per-family read-out of decision 53 and TASKS 58; the registration calls it the per-family corrected-ω rms), seed
mean with the standard error over seeds.
- line 1: rung 4 holds when e(30) ≤ 2.5 cm⁻¹ in every band family.
- a family that misses is 'still learning' when e(30) < e(10) − 2·√(SE₁₀² + SE₃₀²) and e(30) < e(20): not failed, data-limited — the
  registered next step is 60 rows per training family, priced and put to the user. A family that misses with a flat curve: no verdict at 30,
  the registered search first.
- beside, no line: e(0) per family (the transfer without rung-4 data), q₄ = ring-coupling ratio at k = 0 / at k = 30, the overall corrected-ω
  rms per k.
A record that dropped a registered tetracene molecule stops the read (a test set is read whole or not at all). Writes out/read_rung4.{json,md}
under module 05; exit 0 (a read, not a gate).

    python probes/rung4_read.py --k0 <seed jsons> --k10 <…> --k20 <…> --k30 <…>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
OUT = PLAN / "modules" / "05_support_predictor" / "out" / "read_rung4"
FAMILIES = ("CH-stretch", "CH-oop", "ring-ip", "other")
CURVE = (0, 10, 20, 30)
LINE = 2.5            # cm⁻¹, decision 39's go/no-go
HOLD = "tetracene"


def require_complete(records: list[dict]) -> None:
    for r in records:
        dropped = r[HOLD].get("dropped") or []
        if dropped:
            raise SystemExit(f"the tetracene set lost {len(dropped)} registered molecules at evaluation ({', '.join(dropped[:5])}) — not read")


def mean_se(values: list[float]) -> tuple[float, float]:
    v = np.asarray(values, dtype=float)
    return float(v.mean()), float(v.std(ddof=1) / np.sqrt(len(v))) if len(v) > 1 else float("nan")


def still_learning(e: dict[int, tuple[float, float]]) -> bool:
    (e10, se10), (e20, _), (e30, se30) = e[10], e[20], e[30]
    return bool(e30 < e10 - 2 * np.hypot(se10, se30) and e30 < e20)      # a Python bool: the result is written as JSON


def read(records: dict[int, list[dict]]) -> dict:
    if sorted(records) != list(CURVE) or any(len(v) < 2 for v in records.values()):
        raise SystemExit(f"need records for k = {CURVE}, at least two seeds each")
    for recs in records.values():
        require_complete(recs)
    fam = {F: {k: mean_se([r[HOLD]["diag_rms"][F] for r in records[k]]) for k in CURVE} for F in FAMILIES}
    families = {}
    for F, e in fam.items():
        meets = e[30][0] <= LINE
        families[F] = {"e": {str(k): {"mean": m, "se": s} for k, (m, s) in e.items()}, "meets_line": meets,
                       "still_learning": still_learning(e),
                       "status": "meets" if meets else "data-limited" if still_learning(e) else "flat miss"}
    statuses = {f["status"] for f in families.values()}
    verdict = ("rung 4 holds: step 2 (rung 5) may be proposed, priced and registered" if statuses == {"meets"}
               else "no verdict at 30: the registered search first (a family missed with a flat curve)" if "flat miss" in statuses
               else "data-limited: 60 rows per training family, priced and put to the user; the read repeated at k = 60")
    coupling = {k: mean_se([r[HOLD]["coupling_ratio"] for r in records[k]])[0] for k in CURVE}
    freq = {str(k): mean_se([r[HOLD]["corrected_freq_rms"] for r in records[k]]) for k in CURVE}
    return {"line_cm": LINE, "families": families, "verdict": verdict, "q4": coupling[0] / coupling[30],
            "coupling_ratio": {str(k): v for k, v in coupling.items()}, "corrected_freq_rms": freq,
            "n_seeds": {str(k): len(v) for k, v in records.items()}}


def report(res: dict) -> list[str]:
    lines = ["# Rung 4 — the tetracene family at k = 0, 10, 20, 30 rows per training family (registered read)", "",
             f"**{res['verdict']}**", "", "| family | " + " | ".join(f"e({k})" for k in CURVE) + " | line 1 (≤ 2.5) | still learning |",
             "|---|" + "---|" * (len(CURVE) + 2)]
    for F, f in res["families"].items():
        cells = " | ".join(f"{f['e'][str(k)]['mean']:.2f} ± {f['e'][str(k)]['se']:.2f}" for k in CURVE)
        lines.append(f"| {F} | {cells} | {'meets' if f['meets_line'] else 'misses'} | {'yes' if f['still_learning'] else 'no'} |")
    lines += ["", f"Beside, no line: q₄ = ring-coupling ratio at k = 0 / at k = 30 = {res['coupling_ratio']['0']:.3f} / "
                  f"{res['coupling_ratio']['30']:.3f} = **{res['q4']:.2f}**; overall corrected-ω rms per k: "
                  + ", ".join(f"{k}: {m:.2f}" for k, (m, _) in res["corrected_freq_rms"].items()) + " cm⁻¹."]
    return lines


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for k in CURVE:
        ap.add_argument(f"--k{k}", nargs="+", required=True)
    a = ap.parse_args()
    records = {k: [json.loads(Path(p).read_text(encoding="utf-8")) for p in getattr(a, f"k{k}")] for k in CURVE}
    res = read(records)
    res["files"] = {str(k): getattr(a, f"k{k}") for k in CURVE}
    lines = report(res)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{OUT}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    Path(f"{OUT}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
