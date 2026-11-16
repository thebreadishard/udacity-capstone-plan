"""The selection eval on Linux with the rank-based B⁺ against the trainer's own Windows numbers, per molecule (TASKS 236).

Counterpart: `out/v14/E7_rungC_v14s1a_c00_control.json`, `curve.913.per_seed[0].sel.per_molecule` — what the training on Windows
recorded for its selection set. Read: the record `trainer_eval_with_fix.py` wrote in WSL. Third column: the WSL smoke of 16 Nov
without the fix (`v14_seleval_smoke_2026-11-16/wsl_eval/`).

    python compare_trainer_eval.py <plan folder> <out.json>
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NAME = "E7_rungC_v14s1a_c00_control"
KEY = "corrected_freq_rms"


def main() -> None:
    plan, target = Path(sys.argv[1]).resolve(), Path(sys.argv[2])
    trainer = json.loads((plan / "modules" / "05_support_predictor" / "out" / "v14" / f"{NAME}.json").read_text(encoding="utf-8"))
    trainer_sel = trainer["curve"]["913"]["per_seed"][0]["sel"]
    fixed = json.loads((HERE / "trainer_eval_fixed" / f"{NAME}_seleval_seed0.json").read_text(encoding="utf-8"))["selall"]
    smoke = json.loads((plan / "probes" / "results_m1" / "v14_seleval_smoke_2026-11-16" / "wsl_eval"
                        / f"{NAME}_seleval_seed0.json").read_text(encoding="utf-8"))["selall"]
    eighteen = (HERE / "ids_seleval18.txt").read_text(encoding="utf-8").split()
    if set(fixed["per_molecule"]) != set(trainer_sel["per_molecule"]):
        raise SystemExit("the eval and the trainer's record do not hold the same selection molecules")
    rows = [{"id": mol, "trainer_windows_cm": trainer_sel["per_molecule"][mol][KEY], "linux_fixed_cm": read[KEY],
             "linux_before_cm": smoke["per_molecule"][mol][KEY],
             "difference_cm": abs(read[KEY] - trainer_sel["per_molecule"][mol][KEY]), "one_of_the_18": mol in eighteen}
            for mol, read in fixed["per_molecule"].items()]
    worst18 = max((r for r in rows if r["one_of_the_18"]), key=lambda r: r["difference_cm"])
    worst = max(rows, key=lambda r: r["difference_cm"])
    record = {"checkpoint": f"{NAME}_model_n913_seed0.pt", "n_molecules": len(rows),
              "set_rms_trainer_windows_cm": trainer_sel[KEY], "set_rms_linux_fixed_cm": fixed[KEY], "set_rms_linux_before_cm": smoke[KEY],
              "largest_difference_of_the_18": worst18, "largest_difference_of_all": worst, "molecules": rows}
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(json.dumps(record, indent=1) + "\n", encoding="utf-8")
    os.replace(tmp, target)
    print(f"{NAME} seed 0, selection set of {len(rows)}: error of the corrected frequencies, cm-1")
    print(f"  {'molecule':<16}{'trainer (Windows)':>18}{'Linux, rank B+':>16}{'difference':>12}{'Linux before':>14}")
    for r in sorted((r for r in rows if r["one_of_the_18"]), key=lambda r: r["id"]):
        print(f"  {r['id']:<16}{r['trainer_windows_cm']:>18.6f}{r['linux_fixed_cm']:>16.6f}{r['difference_cm']:>12.1e}{r['linux_before_cm']:>14.3g}")
    print(f"  largest difference among the 18: {worst18['difference_cm']:.2e} cm-1 ({worst18['id']}); among all {len(rows)}: "
          f"{worst['difference_cm']:.2e} cm-1 ({worst['id']})")
    print(f"  the set's rms: trainer {trainer_sel[KEY]:.6f}, Linux with the rank-based B+ {fixed[KEY]:.6f}, Linux before {smoke[KEY]:.4g}")


if __name__ == "__main__":
    main()
