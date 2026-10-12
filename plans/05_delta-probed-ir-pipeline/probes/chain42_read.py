"""Chain 42's registered read (12 Oct 2026; GoalGathering/notes/PreRegistration_2026-10-12_Large_PAH_Size_Test.md). From the per-seed
rungC_eval_saved records of arm 0 and arm D (each read with `--eval-ids-file T=…`), the seed means of the ring-coupling ratio r:

- line 1: q_T = r₀(T) / r₀(a). At most 1.3 carries, at least 1.8 is steep, between is noted.
- line 2: g = r_D(T) / r₀(T). At most 0.85 the lever works. At least 0.95 six are too few to judge, so a second point (≈ 20) follows. Between
  is noted.

Reported beside, without lines: corrected ω rms per molecule of T, and (a)/(b) of both arms. Writes out/read_chain42.{json,md} under module
05; exit 0 (a read, not a gate).

    python probes/chain42_read.py <arm0 eval json> [...] --arm-d <armD eval json> [...]
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np

PLAN = Path(__file__).resolve().parents[1]
OUT = PLAN / "modules" / "05_support_predictor" / "out" / "read_chain42"


def mean_of(records: list, hold: str, key: str = "coupling_ratio") -> float:
    return float(np.mean([r[hold][key] for r in records]))


def verdicts(q_t: float, g: float) -> dict:
    line1 = "carries (≤ 1.3)" if q_t <= 1.3 else "steep (≥ 1.8)" if q_t >= 1.8 else "between: noted"
    line2 = ("the lever works (≤ 0.85)" if g <= 0.85 else "six are too few to judge (≥ 0.95): a second point (≈ 20) before any conclusion"
             if g >= 0.95 else "between: noted")
    return {"line_1": line1, "line_2": line2}


def read(arm0: list, arm_d: list) -> dict:
    r0t, r0a, rdt = mean_of(arm0, "T"), mean_of(arm0, "a"), mean_of(arm_d, "T")
    res = {"r0_T": r0t, "r0_a": r0a, "rD_T": rdt, "q_T": r0t / r0a, "g": rdt / r0t, "n_seeds": [len(arm0), len(arm_d)]}
    res.update(verdicts(res["q_T"], res["g"]))
    res["beside"] = {arm: {h: {"coupling_ratio": mean_of(recs, h), "corrected_freq_rms": mean_of(recs, h, "corrected_freq_rms")}
                           for h in ("a", "b", "T")} for arm, recs in (("arm 0", arm0), ("arm D", arm_d))}
    ids = list(arm0[0]["T"]["per_molecule"])
    res["T_per_molecule_freq_rms"] = {i: {arm: float(np.mean([r["T"]["per_molecule"][i]["corrected_freq_rms"] for r in recs]))
                                          for arm, recs in (("arm 0", arm0), ("arm D", arm_d))} for i in ids}
    return res


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arm0", nargs="+")
    ap.add_argument("--arm-d", nargs="+", required=True)
    a = ap.parse_args()
    load = lambda paths: [json.loads(Path(p).read_text(encoding="utf-8")) for p in paths]  # noqa: E731
    res = read(load(a.arm0), load(a.arm_d))
    res["files"] = {"arm 0": a.arm0, "arm D": a.arm_d}
    lines = ["# Chain 42 — the four shape molecules as a size test (registered read)", "",
             f"q_T = r₀(T)/r₀(a) = {res['r0_T']:.3f}/{res['r0_a']:.3f} = **{res['q_T']:.2f}** → {res['line_1']}",
             f"g = r_D(T)/r₀(T) = {res['rD_T']:.3f}/{res['r0_T']:.3f} = **{res['g']:.2f}** → {res['line_2']}", "",
             "| molecule | ω rms arm 0 (cm⁻¹) | ω rms arm D |", "|---|---|---|"]
    lines += [f"| {i} | {v['arm 0']:.2f} | {v['arm D']:.2f} |" for i, v in res["T_per_molecule_freq_rms"].items()]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{OUT}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    Path(f"{OUT}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
