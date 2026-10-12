"""The registered lines of the CC field-route APT (lever 6, 12 Oct 2026; `probes/results_m1/cc_apt_field_2026-10-12/REGISTRATION.md`), as a
step of the run: exit 0 when the APT passes, 1 when it fails (the chain runner stops there), one JSON line to stdout either way.

    python probes/cc_apt_field_check.py <field apt.npz> [--ref <E8 apt_ccsd_t.npz> --line 1e-3] [--sum-rule 1e-6] [--low <dipole_b3lyp npz>]
"""
import argparse
import json
import sys

import numpy as np


def check(new, ref=None, line=1e-3, sum_rule_line=1e-6, low=None):
    z = np.load(new)
    P = z["apt"]
    row = {"apt": new, "sum_rule": float(z["sum_rule_max"]), "seconds": int(z["seconds"]), "passed": float(z["sum_rule_max"]) <= sum_rule_line}
    if ref is not None:
        r = np.load(ref)
        dx = float(np.abs(np.asarray(r["coords_bohr"], float) - np.asarray(z["coords_bohr"], float)).max())
        if dx > 1e-8:
            raise SystemExit(f"{new} and {ref} are at different geometries (max |dx| {dx:.1e} bohr)")
        row.update(ref=ref, max_abs_diff=float(np.abs(P - r["apt"]).max()), line=line, ref_sum_rule=float(r["sum_rule_max"]))
        row["passed"] = row["passed"] and row["max_abs_diff"] <= line
    if low is not None:                                        # reported, not judged: how far the CC APT is from the low level's
        row["max_abs_diff_to_low_level"] = float(np.abs(P - np.load(low)["apt"]).max())
    return row


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("apt")
    ap.add_argument("--ref")
    ap.add_argument("--line", type=float, default=1e-3)
    ap.add_argument("--sum-rule", type=float, default=1e-6)
    ap.add_argument("--low")
    a = ap.parse_args()
    row = check(a.apt, a.ref, a.line, a.sum_rule, a.low)
    print(json.dumps(row), flush=True)
    sys.exit(0 if row["passed"] else 1)


if __name__ == "__main__":
    main()
