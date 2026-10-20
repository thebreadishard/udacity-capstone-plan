"""Regression pin of `probes/cc_composite_full_check.py` (20 Oct 2026), written before its clean-code refactor: every subcommand that runs on
the laptop, on real inputs, must give the same files to the bit — `build` in the corpus frame (quinoline, set three) and in the plane frame
(anthracene, the 7 Oct composite), `read` (benzene, test 2), `repair-oop` (anthracene, test 3), `planeframe` and `merge` (anthracene's
lane files). `compute` needs pyscf and is pinned in WSL (`test_cc_composite_compute_regression.py`).

Each run goes through `tests/cc_full_pin_runner.py`, which points the script's data root at this checkout, so a refactored copy in a worktree
is tested on the same inputs: CC_FULL_SCRIPT=<path> selects the script under test (default: this checkout's).

    python tests/test_cc_composite_full_check_regression.py --write-golden      # with the script as it is before a change
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from pin_tools import (
    DATA,
    PLAN,
    digest,
    environment,
    first_difference,
    require_free_memory,
    require_pinning_environment,
    single_thread_env,
    stable,
)

SCRIPT = PLAN / "probes" / "cc_composite_full_check.py"
RUNNER = Path(__file__).with_name("cc_full_pin_runner.py")
GOLDEN = DATA / "cc_composite_full_check_golden.json"
R = PLAN / "probes" / "results_m1"
ANTHRACENE = "A_a1e6ec1862"
A_PARTIAL = R / "e8_anthracene_ccpvdz_2026-10-06_partial"
A_OOP = R / "ccx53_full_2026-10-07_anthracene" / "e8" / "composite"
DFA = R / "dfmp2_anchors_2026-10-20"
VOLATILE = frozenset({"date"})
CASES = {
    "build_quinoline": ["build", R / "e8_quinoline_ccpvdz_2026-10-18" / "hessian_ccsd_t.npz", "A_ff98e1160d",
                        DFA / "dfmp2_rows_quinoline_ccpvdz.npz", DFA / "dfmp2_rows_quinoline_ccpvtz.npz", "{out}"],
    "build_anthracene_planeframe": ["build", A_PARTIAL / "hessian_ccsd_t_IMAGINARY.npz", ANTHRACENE,
                                    R / "composite_rows_2026-10-07" / "mp2_rows_anthracene_ccpvdz.npz",
                                    R / "composite_rows_2026-10-07" / "mp2_rows_anthracene_ccpvtz.npz", "{out}",
                                    "--planeframe", A_PARTIAL / "geometry_planeframe.json"],
    "read_benzene": ["read", R / "e8_benzene_ccpvdz_dip_2026-10-03", R / "e8_benzene_ccpvtz_oop_2026-10-03", "A_8448043181",
                     R / "composite_mp2_rows_benzene_ccpvdz_2026-10-04.npz", R / "composite_mp2_rows_benzene_ccpvtz_2026-10-04.npz", "{out}"],
    "repair_oop_anthracene": ["repair-oop", A_PARTIAL, ANTHRACENE, A_PARTIAL / "geometry_planeframe.json",
                              A_OOP / "mp2_rows_anthracene_oop_ccpvdz.npz", A_OOP / "mp2_rows_anthracene_oop_ccpvtz.npz", "{out}"],
    "planeframe_anthracene": ["planeframe", PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules" / ANTHRACENE / "geometry.json",
                              "{out}.json"],
    "merge_anthracene_lanes": ["merge", "{out}.npz", A_OOP / "mp2_rows_anthracene_oop_ccpvtz_a.npz", A_OOP / "mp2_rows_anthracene_oop_ccpvtz_b.npz"],
}


def script_under_test() -> Path:
    return Path(os.environ.get("CC_FULL_SCRIPT", SCRIPT)).resolve()


def inputs(case: str) -> list[Path]:
    return [x for x in CASES[case] if isinstance(x, Path)]


def anonymised(text: str, work: Path) -> str:
    for spelling in (json.dumps(str(work))[1:-1], str(work), work.as_posix()):
        text = text.replace(spelling, "<work>")
    return text


def npz_summary(path: Path, work: Path) -> dict:
    """A digest per numeric array, every other field (paths, status, labels) as its value."""
    with np.load(path) as z:
        return {k: digest(z[k]) if z[k].dtype.kind in "fiub" and z[k].ndim else anonymised(json.dumps(z[k].tolist()), work) for k in z.files}


def outputs(work: Path) -> dict:
    out = {}
    for p in sorted(work.iterdir()):
        if p.suffix == ".npz":
            out[p.name] = npz_summary(p, work)
        elif p.suffix == ".json":
            out[p.name] = stable(json.loads(anonymised(p.read_text(encoding="utf-8"), work)), VOLATILE)
        elif p.suffix == ".md":
            out[p.name] = re.sub(r"\d{4}-\d\d-\d\d \d\d:\d\d", "<date>", anonymised(p.read_text(encoding="utf-8"), work))
    return out


def run_case(case: str, work: Path, script: Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    argv = [str(x).replace("{out}", str(work / case)) if isinstance(x, str) else str(x) for x in CASES[case]]
    subprocess.run([sys.executable, str(RUNNER), str(script), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True,
                   capture_output=True)
    return outputs(work)


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_outputs_are_unchanged(case, tmp_path):
    pytest.importorskip("torch")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the script")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    if case == "read_benzene":
        require_free_memory()                                               # test 2's read loads the corpus
    missing = [str(p) for p in inputs(case) if not p.exists()]
    assert not missing, f"pin inputs missing: {missing}"
    assert (diff := first_difference(golden["cases"][case], run_case(case, tmp_path, script_under_test()))) is None, diff


def test_every_case_writes_something():
    """The pin covers a subcommand only if its golden holds files."""
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    cases = json.loads(GOLDEN.read_text(encoding="utf-8"))["cases"]
    assert sorted(cases) == sorted(CASES) and all(cases[c] for c in CASES)


if __name__ == "__main__":
    import tempfile

    if sys.argv[1:] != ["--write-golden"]:
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "script": SCRIPT.name,
               "cases": {c: run_case(c, Path(tmp) / c, SCRIPT) for c in sorted(CASES)}}
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {len(CASES)} cases to {GOLDEN}: " + ", ".join(f"{c} ({len(v)} files)" for c, v in pin["cases"].items()))
