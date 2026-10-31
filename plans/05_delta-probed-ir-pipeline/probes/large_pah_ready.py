"""Chain 42's wait condition (12 Oct 2026): exit 0 when the ten large-PAH folders (the frozen id lists in module 05's corpus/) are complete in
corpus/molecules. Complete means: geometry.json, both analytic Hessians, a dipole_b3lyp_cphf.npz, and a result.json that says
labels "analytic_only" with n_imaginary_b3lyp/wb97x present and zero.

An APT that failed its checks does not hold the run: chain 42's lines read the Hessians only, and its registration (risk 4) gives the
intensity read-out a second route for such a molecule (`probes/apt_field_route.py`) without moving the limit. The status line names
every APT that did not pass, for that read-out.

A molecule with an imaginary mode keeps the run waiting and is named here; the registration's rule is one pyscf re-optimisation at the label
settings. One status line to stdout; exit 1 while incomplete.

    python probes/large_pah_ready.py [--molecules modules/05_support_predictor/corpus/molecules]
"""
import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus")
LISTS = ("large_pah_test_ids_2026-10-12.txt", "large_pah_train_ids_2026-10-12.txt")


def ids():
    out = []
    for name in LISTS:
        lines = Path(CORPUS, name).read_text(encoding="utf-8").splitlines()
        out += [s.strip() for s in lines if s.strip() and not s.startswith("#")]
    return out


def state(d):
    """'ready', or what is missing or wrong."""
    for f in ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz", "dipole_b3lyp_cphf.npz", "result.json"):
        if not os.path.exists(os.path.join(d, f)):
            return f"no {f}"
    r = json.loads(Path(d, "result.json").read_text(encoding="utf-8"))
    if r.get("labels") != "analytic_only":
        return "result.json not analytic_only"
    if "n_imaginary_b3lyp" not in r or "n_imaginary_wb97x" not in r:
        return "no n_imaginary in result.json"
    if r["n_imaginary_b3lyp"] or r["n_imaginary_wb97x"]:
        return f"IMAGINARY ({r['n_imaginary_b3lyp']}, {r['n_imaginary_wb97x']}): re-optimise at the label settings"
    return "ready"


def apt_passed(d):
    """Whether the labels route's APT passed its sum rule and response checks (the file is written either way)."""
    with np.load(os.path.join(d, "dipole_b3lyp_cphf.npz")) as z:
        return bool(z["passed"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--molecules", default=os.path.join(CORPUS, "molecules"))
    a = ap.parse_args()
    st = {i: state(os.path.join(a.molecules, i)) for i in ids()}
    waiting = {i: s for i, s in st.items() if s != "ready"}
    failed_apt = [i for i, s in st.items() if s == "ready" and not apt_passed(os.path.join(a.molecules, i))]
    print(f"large PAHs ready {len(st) - len(waiting)}/{len(st)}" + ("" if not waiting else "; " + "; ".join(f"{i}: {s}" for i, s in waiting.items()))
          + ("" if not failed_apt else f"; APT not passed (field route for the intensity read): {', '.join(failed_apt)}"))
    sys.exit(0 if not waiting else 1)


if __name__ == "__main__":
    main()
