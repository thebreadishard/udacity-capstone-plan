"""Run a script of this repository with aromir's rank-based B⁺ in place of `np.linalg.pinv(B)` (TASKS 236).

Module 05's code is not changed (a live chain imports it): inside this process only, a call of `np.linalg.pinv` without a cutoff
— how module 05 inverts the Wilson B — goes to `aromir.network.primitives.pseudo_inverse`, which refuses anything that is not a
Wilson B of a non-linear molecule; a call that names its cutoff goes to numpy unchanged.

    python run_with_rank_pinv.py <script> [its arguments]

Prints how many calls went each way, so a run with zero replaced calls is not mistaken for a test of the fix.
"""
from __future__ import annotations

import runpy
import sys
from collections import Counter

import numpy as np
from aromir.network.primitives import pseudo_inverse

calls: Counter[str] = Counter()
numpy_pinv = np.linalg.pinv


def rank_based_pinv(matrix, *args, **kwargs):   # numpy's own signature
    """`np.linalg.pinv` for this process: a call without a cutoff is a Wilson B and gets the rank 3N-6."""
    if args or kwargs:
        calls["cutoff named: numpy"] += 1
        return numpy_pinv(matrix, *args, **kwargs)
    calls["no cutoff: aromir's pseudo_inverse"] += 1
    return pseudo_inverse(np.asarray(matrix, dtype=float))


def main() -> int:
    script = sys.argv[1]
    sys.argv = sys.argv[1:]
    np.linalg.pinv = rank_based_pinv
    code = 0
    try:
        runpy.run_path(script, run_name="__main__")
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
        if code != 0:
            print(f"(RANKPINV) the script stopped: {stop.code}", flush=True)
    print(f"(RANKPINV) pinv calls: {dict(calls)}; exit {code}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
