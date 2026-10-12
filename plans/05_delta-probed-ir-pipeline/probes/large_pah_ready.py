"""Chain 42's wait condition (12 Oct 2026): exit 0 when the ten large-PAH folders (the frozen id lists in module 05's corpus/) are complete in
corpus/molecules. Complete means: geometry.json, both analytic Hessians, a passed dipole_b3lyp_cphf.npz, and a result.json that says
labels "analytic_only" with n_imaginary_b3lyp/wb97x present and zero.

A molecule with an imaginary mode keeps the run waiting and is named here; the registration's rule is one pyscf re-optimisation at the label
settings. One status line to stdout; exit 1 while incomplete.

    python probes/large_pah_ready.py [--molecules modules/05_support_predictor/corpus/molecules]
"""
import argparse
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus")
LISTS = ("large_pah_test_ids_2026-10-12.txt", "large_pah_train_ids_2026-10-12.txt")


def ids():
    out = []
    for name in LISTS:
        out += [s.strip() for s in open(os.path.join(CORPUS, name), encoding="utf-8") if s.strip() and not s.startswith("#")]
    return out


def state(d):
    """'ready', or what is missing or wrong."""
    for f in ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz", "dipole_b3lyp_cphf.npz", "result.json"):
        if not os.path.exists(os.path.join(d, f)):
            return f"no {f}"
    r = json.load(open(os.path.join(d, "result.json"), encoding="utf-8"))
    if r.get("labels") != "analytic_only":
        return "result.json not analytic_only"
    if "n_imaginary_b3lyp" not in r or "n_imaginary_wb97x" not in r:
        return "no n_imaginary in result.json"
    if r["n_imaginary_b3lyp"] or r["n_imaginary_wb97x"]:
        return f"IMAGINARY ({r['n_imaginary_b3lyp']}, {r['n_imaginary_wb97x']}): re-optimise at the label settings"
    if not bool(np.load(os.path.join(d, "dipole_b3lyp_cphf.npz"))["passed"]):
        return "APT not passed"
    return "ready"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--molecules", default=os.path.join(CORPUS, "molecules"))
    a = ap.parse_args()
    st = {i: state(os.path.join(a.molecules, i)) for i in ids()}
    waiting = {i: s for i, s in st.items() if s != "ready"}
    print(f"large PAHs ready {len(st) - len(waiting)}/{len(st)}" + ("" if not waiting else "; " + "; ".join(f"{i}: {s}" for i, s in waiting.items())))
    sys.exit(0 if not waiting else 1)


if __name__ == "__main__":
    main()
