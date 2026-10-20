"""Regression pin of `probes/e8_cc_hessian_fd.py`, the CCSD(T) FD Hessian of every anchor (20 Oct 2026), written before its clean-code
refactor; runs in WSL (qc05, one thread) on water at cc-pVDZ: with and without symmetry, with the (T) C kernels, the two-route check deferred
and then run ('separate', 'only'), a partial run followed by the energy route, the UHF path (H2O+), and the two refusals (a frozen core
that differs from the elements', a C kernel on the UHF path). Every file of the run folder is compared (arrays by sha256, the log and the
check file without times), with each step's exit code. Gate 1 is replaced by tests/e8_pin_runner.py: the pin tests the computation.

E8_PROBES=<folder> selects the folder whose script is tested (default: this checkout's probes; a worktree's for a refactor).

    ~/qc05/bin/python tests/test_e8_cc_hessian_fd_regression.py --write-golden      # in WSL, with the script as it is before a change
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
GOLDEN = PLAN / "tests" / "data" / "e8_cc_hessian_fd_golden.json"
RUNNER = Path(__file__).with_name("e8_pin_runner.py")
WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.994915, 1.007825, 1.007825]}
COMMON = ["--threads", "1", "--max-memory", "2000"]
CASES = {
    "symmetry": [["--symmetry"]],
    "plain": [[]],
    "fast_kernels": [["--symmetry", "--fast-t-density", "--fast-t-lambda"]],
    "separate_then_only": [["--two-route-check", "separate", "--only-reference"], ["--two-route-check", "only"], ["--symmetry"]],
    "partial_then_energy": [["--symmetry", "--ks", "0:2"], ["--symmetry", "--two-route-check", "energy"]],
    "uhf_cation": [["--symmetry", "--charge", "1", "--spin", "1"]],
    "refuse_frozen": [["--frozen", "3"]],
    "refuse_fast_uhf": [["--fast-t-density", "--charge", "1", "--spin", "1"]],
}
TIME = re.compile(r"\[\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\] ")
SECONDS = re.compile(r"\b\d+ s\b")


def probes() -> Path:
    return Path(os.environ.get("E8_PROBES", PLAN / "probes")).resolve()


def environment() -> dict:
    import pyscf
    return {"system": platform.system(), "python": platform.python_version(), "pyscf": pyscf.__version__, "numpy": np.__version__}


def digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def file_summary(p: Path):
    if p.suffix == ".npy":
        return digest(np.load(p))
    if p.suffix == ".npz":
        with np.load(p) as z:
            return {k: digest(z[k]) if z[k].dtype.kind in "fiub" and z[k].ndim else json.dumps(z[k].tolist()) for k in z.files}
    if p.suffix == ".json":
        rec = {k: v for k, v in json.loads(p.read_text(encoding="utf-8")).items() if k not in ("date", "seconds")}
        return json.dumps(rec, sort_keys=True)                    # text, so a NaN compares equal to itself
    if p.suffix == ".log":
        return SECONDS.sub("<s> s", TIME.sub("", p.read_text(encoding="utf-8")))
    return f"<{p.suffix} file>"


def run_case(case: str, work: Path, folder: Path) -> dict:
    work.mkdir(parents=True, exist_ok=True)
    geometry = work / "water.json"
    geometry.write_text(json.dumps(WATER), encoding="utf-8")
    out = work / "run"
    env = {**os.environ, "OMP_NUM_THREADS": "1"}
    steps = []
    for args in CASES[case]:
        r = subprocess.run([sys.executable, str(RUNNER), str(folder / "e8_cc_hessian_fd.py"), str(geometry), str(out), *COMMON, *args],
                           env=env, cwd=folder, capture_output=True, text=True, check=False)
        last = (r.stderr.strip().splitlines() or [""])[-1]
        steps.append({"rc": r.returncode, "last_stderr_line": last if r.returncode not in (0,) else ""})
    files = {p.name: file_summary(p) for p in sorted(out.iterdir())} if out.exists() else {}
    return {"steps": steps, "files": files}


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_run_is_unchanged(case, tmp_path):
    pytest.importorskip("pyscf")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it in WSL with --write-golden before changing the script")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if golden["environment"] != environment():
        pytest.skip(f"bit-identity holds in the pinning environment only: {golden['environment']} vs {environment()}")
    assert run_case(case, tmp_path, probes()) == golden["cases"][case]


if __name__ == "__main__":
    import tempfile

    if sys.argv[1:] != ["--write-golden"]:
        sys.exit(__doc__)
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "cases": {c: run_case(c, Path(tmp) / c, probes()) for c in sorted(CASES)}}
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {len(CASES)} cases to {GOLDEN}: " + ", ".join(f"{c} (rc {[s['rc'] for s in v['steps']]}, {len(v['files'])} files)"
                                                                 for c, v in pin["cases"].items()))
