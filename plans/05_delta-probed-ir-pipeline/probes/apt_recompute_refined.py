"""TASKS 44 (b), 12 Oct 2026 (the user: 'Ja, doe a, b en c zoals je adviseert'): the route-C APTs written on the labels server before the
residual-checked response was installed carry pyscf's early-stopped CPHF (pyscf #2702; ~4e-4 e on benzene, heights ≤ 0.6 %). This recomputes
their APT without the Hessian: the labels SCF, `solve_response` (pyscf's own CPHF, the one the Hessian solved) and the labels route's own writer
`write_apt`, which refines the response and checks its residual — with the Hessian taken from the molecule's `hessian_b3lyp_analytic.npz`.
One implementation: the molecule, the SCF and the writer are `analytic_hessians.py`'s.

    python probes/apt_recompute_refined.py <fetched molecule dir> [...] --out <dir> [--threads 4] [--max-memory MB] [--check-only]  (WSL, qc05)

Route B files (1 Nov 2026, the clean hold-out (a), TASKS 146): `probes/dipole_derivs_cphf.py` solved pyscf's Krylov CPHF without a residual
check as route C did, so its files ("cphf") are redone as well. --check-only runs the source checks on every folder and computes nothing;
--max-memory is pyscf's max_memory for a run under a cgroup cap (`probes/wsl_capped.sh`).

Per molecule, `<out>/<id>/dipole_b3lyp_cphf.npz` is written (the input folder is not touched), and one JSON line is appended to
`<out>/recompute.jsonl`: the residual before/after, the largest change of the APT and of a band height against the old file, and the seconds.
A molecule that already has an output file is skipped. The exit status is 3 when a molecule's APT fails (as the labels route's).
"""
import argparse
import json
import os
import sys
import time
from typing import Any

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus"))
import analytic_hessians as AH  # noqa: E402
from apt import solve_response  # noqa: E402
from pyscf import lib  # noqa: E402

LABELS_GRID = (99, 590)
REDO_ROUTES = ("hessian_response", "cphf")   # route C before the refinement, route B: both pyscf's Krylov CPHF without a residual check


def height_change(old, new):
    """The largest change of a band height (km/mol) relative to the strongest band of the old file: the scale a spectrum is read on."""
    old, new = np.asarray(old, dtype=float), np.asarray(new, dtype=float)
    return float(np.abs(new - old).max() / old.max())


def source_files(src: str, grid: tuple[int, int] = LABELS_GRID) -> tuple[Any, Any]:
    """The old APT file and the B3LYP Hessian file of one fetched molecule; raises unless the APT is one to redo and the Hessian is the
    labels route's closed-shell setting."""
    old = np.load(os.path.join(src, AH.APT_FILE))
    route = str(old["route"])
    failed_refined = route == "hessian_response_refined" and not bool(old["passed"])   # 13 Oct 2026: the guard's failures
    if route not in REDO_ROUTES and not failed_refined:                                 # (B_1194d7a42a, B_127dd8c4ed) redo
        raise ValueError(f"{src}: the APT file's route is {route} (passed {bool(old['passed'])}): neither an unrefined route "
                         f"({', '.join(REDO_ROUTES)}) nor a failed refined one")
    hz = np.load(os.path.join(src, "hessian_b3lyp_analytic.npz"))
    if "charge" not in hz.files or "spin" not in hz.files:
        raise ValueError(f"{src}: the Hessian file predates its charge and spin fields; its Hessian is computed again "
                         "(analytic_hessians.py), not only its APT")
    if tuple(hz["grid"]) != tuple(grid) or int(hz["spin"]) != 0:
        raise ValueError(f"{src}: Hessian grid {tuple(hz['grid'])} / spin {int(hz['spin'])} is not the labels route's closed-shell setting")
    return old, hz


def recompute(src, out_dir, grid=LABELS_GRID, stamp=None, max_memory=AH.MAX_MEMORY_MB):
    """The refined APT of one fetched labels molecule (closed shell); returns the summary row."""
    t0 = time.time()
    with open(os.path.join(src, "geometry.json"), encoding="utf-8") as fh:
        g = json.load(fh)
    old, hz = source_files(src, grid)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, AH.PYSCF_LOG_NAME), "a", encoding="utf-8") as lib_log:
        mol = AH.labels_mol(g, lib_log, int(hz["charge"]), 0, max_memory)
        mf, _ = AH.labels_scf(mol, "b3lyp", grid)
        hobj = mf.Hessian()
        response = solve_response(hobj)
        cause = None
        try:       # inside the log's block: the refinement's get_jk logs through hobj when the integrals are direct (A_428228e5a5)
            message, error = AH.write_apt(out_dir, hobj, response, hz["H_projected"], np.array(g["masses_amu"]), grid,
                                          stamp or AH.software()), ""
        except ValueError as exc:  # write_apt writes the file, marked failed, before it raises for a failed sum rule or residual
            message, error, cause = "", str(exc), exc
    apt_path = os.path.join(out_dir, AH.APT_FILE)
    if not os.path.exists(apt_path):
        raise RuntimeError(f"{src}: write_apt raised before writing {AH.APT_FILE}: {error}") from cause
    new = np.load(apt_path)
    return {"id": os.path.basename(os.path.normpath(src)), "passed": bool(new["passed"]), "error": error, "message": message,
            "residual_before": float(new["cphf_residual_before"]), "residual_after": float(new["cphf_residual_after"]),
            "rounds": int(new["cphf_refine_rounds"]), "apt_change_max": float(np.abs(new["apt"] - old["apt"]).max()),
            "height_change_max": height_change(old["intensity_km_mol"], new["intensity_km_mol"]),
            "sum_rule_old": float(old["sum_rule_max"]), "sum_rule_new": float(new["sum_rule_max"]), "seconds": round(time.time() - t0, 1)}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--max-memory", type=int, default=AH.MAX_MEMORY_MB, help="pyscf's max_memory in MB (below a run's cgroup cap)")
    ap.add_argument("--check-only", action="store_true", help="the source checks on every folder; nothing is computed or written")
    a = ap.parse_args()
    if a.check_only:
        for src in a.dirs:
            old, _ = source_files(src)
            print(f"{os.path.basename(os.path.normpath(src))}: route {old['route']!s}, to be refined", flush=True)
        return
    lib.num_threads(a.threads)
    stamp = AH.software()
    failed = 0
    for src in a.dirs:
        mid = os.path.basename(os.path.normpath(src))
        out_dir = os.path.join(a.out, mid)
        if os.path.exists(os.path.join(out_dir, AH.APT_FILE)):
            print(f"{mid}: done before, skipped", flush=True)
            continue
        row = recompute(src, out_dir, stamp=stamp, max_memory=a.max_memory)
        failed += not row["passed"]
        with open(os.path.join(a.out, "recompute.jsonl"), "a") as fh:
            fh.write(json.dumps(row) + "\n")
        print(json.dumps(row), flush=True)
    if failed:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
