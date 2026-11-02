"""Route A's benzene gate, read (S3 registration, 'Gate before the targets'): the fetched G setting with the ± saving and four lanes against
S1's directly computed G set, by `s1_anharmonic_level.compare`. The line, S1 amendment 2's: Δ_anh rms ≤ RMS_LINE and max ≤ MAX_LINE over
the window modes, and the gate's own force field not NOISY. Writes compare.json and gate.json beside the fetched setting.

    python probes/routea_gate_read.py        (from the plan folder; probes/routea_gate_read.sh fetches first)
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from s1_anharmonic_level import compare  # noqa: E402

DIRECT = os.path.join(HERE, "results_m1", "s1_anharmonic_benzene_2026-10-13", "s1_benzene", "G")
GATE_ROOT = os.path.join(HERE, "results_m1", "routea_2026-11-02", "gate2")   # the rerun (S3 amendment 2)
RMS_LINE, MAX_LINE = 0.2, 0.5    # cm⁻¹, S1 amendment 2


def main() -> int:
    res = compare(DIRECT, [os.path.join(GATE_ROOT, "benzene", "G")], (550.0, 2000.0))
    t = next(iter(res["tests"].values()))
    passed = (not t["noisy"]) and t["rms_window"] <= RMS_LINE and t["max_window"] <= MAX_LINE
    with open(os.path.join(GATE_ROOT, "benzene", "G", "images.json"), encoding="utf-8") as fh:
        images = json.load(fh)["summary"]
    gate = {"rms_window": t["rms_window"], "max_window": t["max_window"], "n_window": t["n_window"], "noisy": t["noisy"],
            "min_overlap": t["min_overlap"], "line": {"rms": RMS_LINE, "max": MAX_LINE}, "passed": passed, "images": images}
    for name, obj in (("compare.json", res), ("gate.json", gate)):
        with open(os.path.join(GATE_ROOT, name + ".tmp"), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=1)
        os.replace(os.path.join(GATE_ROOT, name + ".tmp"), os.path.join(GATE_ROOT, name))
    print(f"gate: Δ_anh rms {t['rms_window']:.3f}, max {t['max_window']:.3f} cm⁻¹ over {t['n_window']} window modes (min overlap "
          f"{t['min_overlap']:.3f}; {images['images']} image Hessians, {images['grid_compatible']} grid-compatible) → "
          f"{'PASS' if passed else 'FAIL'}")
    return 0 if passed else 3


if __name__ == "__main__":
    sys.exit(main())
