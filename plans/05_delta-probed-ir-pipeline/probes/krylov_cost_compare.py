"""TASKS 133: the reference gradients of two krylov_cost_check.py runs (pyscf 2.14.0 and master) compared — the largest |Δg|, each run's
CPHF residuals, and the verdict against TASKS 133's threshold: beyond 1e-6 a.u. the anchors' Hessians are re-checked through their
energy route. Writes krylov_compare.json.

    python probes/krylov_cost_compare.py <run dir 2.14.0> <run dir master> <out.json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import e8_cc_hessian_fd as E8
import numpy as np

THRESHOLD = 1e-6        # a.u.; TASKS 133


def read_run(run: Path) -> tuple[np.ndarray, dict]:
    for name in ("reference.npz", "krylov_residuals.json"):
        if not (run / name).exists():
            raise SystemExit(f"{run / name} is missing: the run did not finish")
    with np.load(run / "reference.npz") as ref:
        g = np.array(ref["gradient"])
    return g, json.loads((run / "krylov_residuals.json").read_text(encoding="utf-8"))


def compare(released: Path, master: Path) -> dict:
    g0, r0 = read_run(released)
    g1, r1 = read_run(master)
    if g0.shape != g1.shape:
        raise SystemExit(f"the gradients differ in shape: {g0.shape} and {g1.shape}")
    if r0["solve_nos1_passes_lindep"] or not r1["solve_nos1_passes_lindep"]:
        raise SystemExit("the first run must be the release without lindep, the second master with it")
    dg = float(np.abs(g0 - g1).max())
    return {"max_abs_dg": dg, "threshold": THRESHOLD, "beyond_threshold": dg > THRESHOLD, "max_abs_g": float(np.abs(g1).max()),
            "residuals_released": [s["residual"] for s in r0["solves"]], "residuals_master": [s["residual"] for s in r1["solves"]],
            "runs": [str(released), str(master)]}


def main(args: list[str]) -> None:
    if len(args) != 3:
        raise SystemExit(__doc__)
    record = compare(Path(args[0]), Path(args[1]))
    E8.write_json(args[2], record)
    print(f"=== (KC) compare: max |Δg| {record['max_abs_dg']:.2e} a.u. (threshold {THRESHOLD:.0e}: "
          f"{'BEYOND — re-check the anchors through their energy route' if record['beyond_threshold'] else 'within'}); residuals 2.14.0 "
          f"{record['residuals_released']}, master {record['residuals_master']}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
