"""Regression pin of `probes/e8_cc_locality.py` (E8's locality read, 20 Oct 2026), written before its clean-code refactor: its main on real
inputs — benzene's CC/TZ anchor and pyridine's composite against their corpus B3LYP and ωB97X analytic Hessians — through
tests/locality_pin_runner.py (stored DFT Hessians in place of pyscf). That runs every helper other probes import from it (normal_modes,
bond_graph, rings, mode_shares, families, internals, readout). The json and md are compared without the date and the seconds.

E8_PROBES=<folder> selects the folder whose script is tested (default: this checkout's probes; a worktree's for a refactor).

    python tests/test_e8_cc_locality_regression.py --write-golden      # with the script as it is before a change
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from pin_tools import DATA, PLAN, environment, require_pinning_environment, single_thread_env

GOLDEN = DATA / "e8_cc_locality_golden.json"
RUNNER = Path(__file__).with_name("locality_pin_runner.py")
MOLS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
R = PLAN / "probes" / "results_m1"
OUT = PLAN / "modules" / "05_support_predictor" / "out"
CASES = {"benzene": ("A_8448043181", R / "e8_benzene_ccpvtz_oop_2026-10-03" / "hessian_ccsd_t.npz"),
         "pyridine": ("A_6e858b26e5", OUT / "composite_full_pyridine_2026-10-07.npz")}


def probes() -> Path:
    return Path(os.environ.get("E8_PROBES", PLAN / "probes")).resolve()


def run_case(case: str, work: Path, folder: Path) -> dict:
    mol_id, cc = CASES[case]
    d = MOLS / mol_id
    prefix = work / case
    argv = [str(folder / "e8_cc_locality.py"), str(d / "hessian_b3lyp_analytic.npz"), str(d / "hessian_wb97x_analytic.npz"),
            str(d / "geometry.json"), str(cc), str(prefix), "--threads", "1"]
    subprocess.run([sys.executable, str(RUNNER), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True, capture_output=True)
    rec = {k: v for k, v in json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8")).items() if k not in ("date", "seconds")}
    md = Path(f"{prefix}.md").read_text(encoding="utf-8")
    md = re.sub(r"Total \d+ s\.", "Total <s> s.", re.sub(r"\(\d{4}-\d\d-\d\d \d\d:\d\d\)", "(<date>)", md))
    return {"json": json.dumps(rec, sort_keys=True), "md": md}


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_read_is_unchanged(case, tmp_path):
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the script")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert run_case(case, tmp_path, probes()) == golden["cases"][case]


if __name__ == "__main__":
    import tempfile

    if sys.argv[1:] != ["--write-golden"]:
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "cases": {c: run_case(c, Path(tmp), probes()) for c in sorted(CASES)}}
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {len(CASES)} cases to {GOLDEN}")
