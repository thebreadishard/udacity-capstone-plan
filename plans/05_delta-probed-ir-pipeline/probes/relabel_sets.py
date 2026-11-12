"""GVPT2 labels of every molecule in a sets file, again, with degeneracy from the point group (TASKS 53, 12 Nov 2026: a 0.5 cm⁻¹ gap had
paired accidental neighbours of asymmetric tops, averaging their quartic constants and skipping their resonances).

    PYTHONPATH=~/pyvpt2-wt-polyad python relabel_sets.py <sets.json> <out dir>

Per set, G labels into <out>/<set name>/gvpt2 and X labels into <out>/<set name>/gvpt2_x (probes/gvpt2_labels.py's write_labels, the
force fields and selections unchanged), then <out>/<sets file name> names the new label folders; every other field is copied. The old
labels stay where they are. Runs in WSL's 'vpt2' env (pyVPT2 imports psi4).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gvpt2_labels import write_labels
from s2_read import ReadOptions, write_atomic


def folder_name(set_name: str) -> str:
    """A set's name as a folder name ('S3 targets' -> 'S3_targets')."""
    return "".join(c if c.isalnum() else "_" for c in set_name)


def relabel(sets_path: str, out_dir: str) -> str:
    """Write both sides' labels of every set and the new sets file; returns its path."""
    with open(sets_path, encoding="utf-8") as fh:
        sets = json.load(fh)
    new_sets = []
    for s in sets:
        base = os.path.join(out_dir, folder_name(s["name"]))
        g_dir, x_dir = os.path.join(base, "gvpt2"), os.path.join(base, "gvpt2_x")
        print(f"== {s['name']}: G", flush=True)
        write_labels(s["root"], s["selection"], ReadOptions(setting="G", extra=s.get("extra", {})), g_dir)
        print(f"== {s['name']}: X", flush=True)
        write_labels(s["xtb_root"], s["selection"], ReadOptions(setting="X"), x_dir)
        new_sets.append({**s, "gvpt2_dir": g_dir, "xtb_gvpt2_dir": x_dir})
    path = os.path.join(out_dir, os.path.basename(sets_path))
    write_atomic(path, json.dumps(new_sets, indent=1) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("sets")
    ap.add_argument("out")
    a = ap.parse_args()
    print(f"relabel_sets: {relabel(a.sets, a.out)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
