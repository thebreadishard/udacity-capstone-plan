"""Chain 42's wait condition (12 Oct 2026): exit 0 when the ten large-PAH folders (the frozen id lists in module 05's corpus/) are complete in
corpus/molecules. Complete means: geometry.json, both analytic Hessians, a dipole_b3lyp_cphf.npz, a result.json that says
labels "analytic_only", and no imaginary mode in either analytic Hessian, counted as the trainer counts it: `n_imaginary` of m05's
`learning_curve_layerA` on the npz's `freq_cm`, the array `e7_rungB_reread_analytic.substitute` reads. result.json's n_imaginary_* are not
read: `corpus/analytic_hessians.py` wrote them at a -10 cm-1 threshold until 8 Nov 2026, so a -7.48 cm-1 mode passed here and was dropped at
load (TASKS 198).

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
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "m05"))
from learning_curve_layerA import n_imaginary  # noqa: E402  the trainer's count (TASKS 198)

FUNCTIONALS = ("b3lyp", "wb97x")
LISTS = ("large_pah_test_ids_2026-10-12.txt", "large_pah_train_ids_2026-10-12.txt")


def ids() -> list[str]:
    out = []
    for name in LISTS:
        lines = Path(CORPUS, name).read_text(encoding="utf-8").splitlines()
        out += [s.strip() for s in lines if s.strip() and not s.startswith("#")]
    return out


def imaginary_counts(d: str | Path) -> dict[str, int]:
    """Imaginary modes of each analytic Hessian in folder d, by the trainer's count on the frequencies its loader reads."""
    counts = {}
    for tag in FUNCTIONALS:
        with np.load(os.path.join(d, f"hessian_{tag}_analytic.npz")) as z:
            counts[tag] = n_imaginary(z["freq_cm"])
    return counts


def state(d: str | Path) -> str:
    """'ready', or what is missing or wrong."""
    for f in ("geometry.json", "hessian_b3lyp_analytic.npz", "hessian_wb97x_analytic.npz", "dipole_b3lyp_cphf.npz", "result.json"):
        if not os.path.exists(os.path.join(d, f)):
            return f"no {f}"
    r = json.loads(Path(d, "result.json").read_text(encoding="utf-8"))
    if r.get("labels") != "analytic_only":
        return "result.json not analytic_only"
    counts = imaginary_counts(d)
    if any(counts.values()):
        return f"IMAGINARY ({counts['b3lyp']}, {counts['wb97x']}): re-optimise at the label settings"
    return "ready"


def apt_passed(d: str | Path) -> bool:
    """Whether the labels route's APT passed its sum rule and response checks (the file is written either way)."""
    with np.load(os.path.join(d, "dipole_b3lyp_cphf.npz")) as z:
        return bool(z["passed"])


def main() -> None:
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
