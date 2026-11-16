"""Which force-field files the anharmonic reads need, per molecule: on disk, and tracked by git.

    python inventory.py

Reads the two sets files of labels_domain_2026-11-13 the way probes/s2b_read.py does and writes inventory.json beside itself.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
from s2_read import write_atomic  # noqa: E402

LABELS = os.path.join(PLAN, "probes", "results_m1", "labels_domain_2026-11-13")
SET_FILES = (os.path.join(LABELS, "sets.json"), os.path.join(LABELS, "S3_targets", "targets.json"))
NEEDED = ("ref.json", "qff_report.npz")


def tracked_files() -> set[str]:
    """Every path git tracks under the plan's probes folder, relative to the plan."""
    out = subprocess.run(["git", "-C", PLAN, "ls-files", "probes/results_m1"], check=True, capture_output=True, text=True).stdout
    return set(out.splitlines())


def molecule_dirs(entry: dict) -> dict[str, dict[str, str]]:
    """Per molecule id of one computed set: its G directory and its xtb directory, relative to the plan."""
    ids = sorted(n[:-5] for n in os.listdir(os.path.join(PLAN, entry["gvpt2_dir"])) if n.endswith(".json"))
    return {i: {"G": entry["extra"].get(i, f"{entry['root']}/{i}/G"), "X": f"{entry['xtb_root']}/{i}/X",
                "label_G": f"{entry['gvpt2_dir']}/{i}.json", "label_X": f"{entry['xtb_gvpt2_dir']}/{i}.json"} for i in ids}


def state(rel: str, tracked: set[str]) -> str:
    """'git', 'disk' (present but untracked) or 'absent' for one path relative to the plan."""
    if rel in tracked:
        return "git"
    return "disk" if os.path.exists(os.path.join(PLAN, rel)) else "absent"


def main() -> int:
    """Write the inventory and print its totals."""
    tracked = tracked_files()
    rows = {}
    for path in SET_FILES:
        with open(path, encoding="utf-8") as fh:
            for entry in json.load(fh):
                for i, d in molecule_dirs(entry).items():
                    row = {"set": entry["name"], **d}
                    for side in ("G", "X"):
                        for name in NEEDED:
                            row[f"{side}/{name}"] = state(f"{d[side]}/{name}", tracked)
                    for lab in ("label_G", "label_X"):
                        row[f"{lab}_state"] = state(d[lab], tracked)
                    rows[i] = row
    keys = [f"{s}/{n}" for s in ("G", "X") for n in NEEDED] + ["label_G_state", "label_X_state"]
    totals = {k: {v: sum(r[k] == v for r in rows.values()) for v in ("git", "disk", "absent")} for k in keys}
    write_atomic(os.path.join(HERE, "inventory.json"), json.dumps({"totals": totals, "molecules": rows}, indent=1))
    print(f"{len(rows)} molecules")
    for k, t in totals.items():
        print(f"{k}: {t}")
    for i, r in rows.items():
        print(i, r["set"], *(r[k] for k in keys), r["X"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
