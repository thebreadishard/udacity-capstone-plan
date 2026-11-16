"""The trainer's saved-model evaluator with aromir's rank-based B⁺ in place of `np.linalg.pinv(B)` (TASKS 236).

Module 05's code is not changed (a live chain imports it): inside this process only, a call of `np.linalg.pinv` without a cutoff
— how `rungC_train.py` inverts the Wilson B — goes to `aromir.network.primitives.pseudo_inverse`, which refuses anything that is
not a Wilson B of a non-linear molecule; a call that names its cutoff goes to numpy unchanged. Then `probes/rungC_eval_saved.py`
runs as `v14_search.py seleval` runs it, with its records under the output prefix given here instead of module 05's `out/`.

    cd modules/05_support_predictor && python <this file> <model, relative to module 05> <absolute output prefix>

Prints how many calls went each way, so that a read with zero replaced calls is not mistaken for a test of the fix.
"""
from __future__ import annotations

import runpy
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from aromir.network.primitives import pseudo_inverse

PLAN = Path(__file__).resolve().parents[3]
EVALUATOR = PLAN / "probes" / "rungC_eval_saved.py"
HOLDOUT_B = "corpus/holdout_b_frozen_2026-10-08.txt"     # chain_runner.HOLDOUT_B
SETS = {"selall": "out/v14/selection_selall.ids", "selscored": "out/v14/selection_selscored.ids"}   # v14_search.ids_file
THREADS = "8"

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
    model, out_prefix = sys.argv[1], Path(sys.argv[2])
    if not out_prefix.is_absolute():
        raise SystemExit("the output prefix must be absolute: the evaluator runs from module 05")
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    np.linalg.pinv = rank_based_pinv
    sys.argv = [str(EVALUATOR), model, str(out_prefix), "--use-analytic", "--threads", THREADS, "--allow-any-model",
                "--holdout-b-file", HOLDOUT_B]
    for name, file in SETS.items():
        sys.argv += ["--eval-ids-file", f"{name}={file}"]
    try:
        runpy.run_path(str(EVALUATOR), run_name="__main__")
    except SystemExit as stop:
        code = stop.code if isinstance(stop.code, int) else (0 if stop.code is None else 1)
        if code != 0:
            print(f"(FIXEVAL) the evaluator stopped: {stop.code}", flush=True)
    else:
        code = 0
    print(f"(FIXEVAL) pinv calls: {dict(calls)}", flush=True)
    print(f"(FIXEVAL) evaluator exit {code}", flush=True)
    return code


if __name__ == "__main__":
    sys.exit(main())
