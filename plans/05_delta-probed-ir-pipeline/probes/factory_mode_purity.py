"""Irrep purity of the modes in an existing results_dryrun/<molecule>/stageA (2026-09-15).

Rotates the stage-A geometry and mode vectors into the principal frame, detects the point-group operations the
geometry satisfies (symmetrise_geometry.permutation) and projects every mode onto the irreps
(dryrun_dft_delta_recovery.project_modes_on_irreps). Prints per mode the label, 1 − purity (the squared admixture of
other irreps) and the size of the change the projection makes; nothing is written back — this is the measurement
behind decision 37's prerequisite (a non-totally-symmetric pattern with an Ag admixture ε carries a force term
odd(q) ∝ ε·q, seen at naphthalene mode 12 as −34 µE_h at q = 1 in the composite).

Usage: python factory_mode_purity.py --molecule naphthalene [--modes 11,12,22,31]
"""
import argparse
import json
import os
import sys
from collections import Counter

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dryrun_dft_delta_recovery import project_modes_on_irreps  # noqa: E402
from symmetrise_geometry import principal_frame  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--molecule", required=True)
    ap.add_argument("--modes", default="", help="comma-separated mode indices to list (default: all)")
    args = ap.parse_args()
    d = os.path.join(HERE, "results_dryrun", args.molecule)
    a = json.load(open(os.path.join(d, "stageA.json")))
    z = np.load(os.path.join(d, "stageA_hessians.npz"))
    L, coords, symbols = z["L"], z["coords"], a["symbols"]
    m = np.array(a["masses_amu"], float)
    x, _ = principal_frame(coords, m)
    com = (m[:, None] * coords).sum(0) / m.sum()
    V = np.linalg.lstsq(coords - com, x, rcond=None)[0]           # the rotation into the principal frame
    if np.abs(V.T @ V - np.eye(3)).max() > 1e-8:                     # degenerate moments (a symmetric top such as benzene)
        print("principal frame ill-defined (degenerate moments): keeping the stage-A frame; only the operations diagonal in it are found")
        x, V = coords - com, np.eye(3)
    Lr = np.einsum("kai,ab->kbi", L.reshape(-1, 3, L.shape[1]), V).reshape(L.shape)
    labels, purity, note, Lp = project_modes_on_irreps(Lr, x, symbols)
    print(f"{args.molecule}: {note}")
    if labels is None:
        return
    fam, fr = a["families"], a["freq_low_cm"]
    sel = [int(t) for t in args.modes.split(",")] if args.modes else range(len(labels))
    print("| mode | ω (cm⁻¹) | family | irrep | 1 − purity | admixture amplitude √(1−purity) | max change of a component |")
    print("|---|---|---|---|---|---|---|")
    for i in sel:
        print(f"| {i} | {fr[i]:.1f} | {fam[i]} | {labels[i]} | {1-purity[i]:.2e} | {np.sqrt(max(1-purity[i],0)):.1e} | "
              f"{np.abs(Lp[:, i]-Lr[:, i]).max():.1e} |")
    print("\nirrep counts:", ", ".join(f"{k} {v}" for k, v in sorted(Counter(labels).items())))
    w = int(np.argmax([1 - p for p in purity]))
    print(f"least pure mode: {w} ({fr[w]:.1f} cm⁻¹, {fam[w]}, {labels[w]}), 1 − purity {1-purity[w]:.2e}")


if __name__ == "__main__":
    main()
