"""Regression pin of the read machinery `probes/s2_read.py` shares with S2b and S3 (concat → loso → curve) and of
`probes/s2_xtb_read.py`'s x0 read, written before the reading window became a setting instead of a module constant (TASKS 219, the
CH-stretch read). The window is threaded through concat, loso, curve, in_window, x0_read and build; this pin says that the reads inside
550-2000 cm-1, which are registered and already published, give the same numbers afterwards — to REL_TOL, not to the bit: the pin runs
on every machine, and GitHub's runner image of 11 Nov 2026 gave 0.05445599912157338 where every earlier machine gave …61214, on a
commit that had been green (15 Nov). The reads are published to 0.01 cm-1; 1e-9 relative is seven digits finer.

Synthetic molecules only (the generator of tests/test_s2_read.py, shared rather than copied), so the pin is fast and needs no run
output. What it does not cover is the loader and the file formats; tests/test_s2_read.py and tests/test_s2_xtb_read.py do.

    python tests/test_s2_read_regression.py --write-golden      # with the scripts as they are before the change
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import DATA, PLAN, first_difference

sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import s2_read as R

from test_s2_read import dataset, molecule

GOLDEN = DATA / "s2_read_golden.json"
REL_TOL = 1e-9
OUTSIDE = (300.0, 520.0, 2100.0, 2850.0, 3050.0)   # below, just below, above, and two CH-stretch positions: none inside 550-2000


def widened(rng: np.random.Generator) -> dict:
    """One synthetic molecule whose last modes are moved outside the registered window, so the window filter has something to drop."""
    mol = molecule(rng)
    mol["omega"] = np.concatenate([mol["omega"][: -len(OUTSIDE)], np.array(OUTSIDE, float)])
    return mol


def concat_case() -> dict:
    rng = np.random.default_rng(7)
    out = R.concat([widened(rng) for _ in range(3)])
    return {"n": len(out["omega"]), "omega_min": float(out["omega"].min()), "omega_max": float(out["omega"].max()),
            "per_family": {fa: int((out["family"] == fa).sum()) for fa in R.FAMILIES},
            "delta_sum": float(out["delta"].sum())}


def xtb_case() -> dict:
    """x0: Δ_xtb as the prediction, on molecules whose G label is a per-family multiple of it (as tests/test_s2_xtb_read.py builds them)."""
    X = pytest.importorskip("s2_xtb_read")
    rng = np.random.default_rng(3)
    by_scaf = {}
    for i in range(4):
        mols = []
        for _ in range(2):
            m = molecule(rng, noise=1.0)
            m[X.XTB_KEY] = m["delta"] * 0.9 - 1.5
            mols.append(m)
        by_scaf[f"s{i:02d}"] = mols
    return X.x0_read(by_scaf)


def record() -> dict:
    return {"curve_exact": R.curve(dataset(), n_subsets=5),
            "curve_noise2": R.curve(dataset(noise=2.0), n_subsets=5),
            "concat": concat_case(),
            "x0": xtb_case()}


def test_the_shared_read_machinery_is_unchanged():
    if not GOLDEN.is_file():
        pytest.skip(f"{GOLDEN.name} is missing: write it with --write-golden before the change it pins")
    difference = first_difference(json.loads(json.dumps(record(), default=float)),
                                  json.loads(GOLDEN.read_text(encoding="utf-8")), rel_tol=REL_TOL)
    assert difference is None, f"the read moved at {difference}"


def test_the_tolerance_passes_rounding_and_nothing_larger():
    assert first_difference({"a": [0.05445599912157338]}, {"a": [0.05445599912161214]}, rel_tol=REL_TOL) is None
    assert first_difference({"a": [0.05445599912157338]}, {"a": [0.05445599912161214]}) == "$.a[0]: 0.05445599912157338 vs 0.05445599912161214"
    assert first_difference({"a": 0.0544560}, {"a": 0.0544561}, rel_tol=REL_TOL) is not None      # the seventh digit: a change
    assert first_difference({"a": 1}, {"a": 2}, rel_tol=REL_TOL) is not None                      # integers stay exact
    assert first_difference({"a": 0.0}, {"a": 5e-10}, rel_tol=REL_TOL) is None                    # near zero: absolute


if __name__ == "__main__":
    if sys.argv[1:] != ["--write-golden"]:
        raise SystemExit(__doc__.strip().splitlines()[-1].strip())
    GOLDEN.write_text(json.dumps(record(), indent=1, default=float) + "\n", encoding="utf-8")
    print(f"wrote {GOLDEN}")
