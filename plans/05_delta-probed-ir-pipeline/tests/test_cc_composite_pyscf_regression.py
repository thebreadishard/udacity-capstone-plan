"""Regression pin of the pyscf side of the composite anchor tools (20 Oct 2026), written before their clean-code refactor; runs in WSL (qc05):
`cc_composite_basis_check.py` in its smoke mode (water, B3LYP and MP2, both bases, the analytic second route) and with an out-of-plane check
file (the Δ_CC branch), and `cc_composite_full_check.py compute` (the MP2 rows of the 7 Oct anchors) on water. One thread, so the rows are
reproducible to the bit; every output file is compared (arrays by sha256, md and json without the date and the seconds).

CC_PYSCF_PROBES=<folder> selects the folder whose two scripts are tested (default: this checkout's probes; a worktree's for a refactor).

    ~/qc05/bin/python tests/test_cc_composite_pyscf_regression.py --write-golden      # in WSL, with the scripts as they are before a change
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
GOLDEN = PLAN / "tests" / "data" / "cc_composite_pyscf_golden.json"
VOLATILE = ("date", "seconds")
WATER = {"symbols": ["O", "H", "H"], "coords_bohr": [[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]],
         "masses_amu": [15.994915, 1.007825, 1.007825]}
OOP_CHECK = {"rows": [{"k": 0, "H_cc_tz": 0.51, "H_cc_dz": 0.50, "oop_fraction": 1.0, "atom": "O", "xyz": "x"},
                      {"k": 4, "H_cc_tz": 0.43, "H_cc_dz": 0.45, "oop_fraction": 0.0, "atom": "H", "xyz": "y"}]}
CASES = {
    "basis_smoke": ["cc_composite_basis_check.py", "--smoke", "{out}/smoke", "--threads", "1"],
    "basis_oop_check": ["cc_composite_basis_check.py", "{work}/geom/water.json", "{out}/oop", "--oop-check", "{work}/oop_check.json", "--levels", "mp2",
                        "--threads", "1"],
    "full_compute": ["cc_composite_full_check.py", "compute", "{work}/geom/water.json", "{out}/rows.npz", "--basis", "cc-pvdz", "--ks", "0,4",
                     "--threads", "1", "--max-memory", "2000"],
}


def probes() -> Path:
    return Path(os.environ.get("CC_PYSCF_PROBES", PLAN / "probes")).resolve()


def environment() -> dict:
    import pyscf
    return {"system": platform.system(), "python": platform.python_version(), "pyscf": pyscf.__version__, "numpy": np.__version__}


def digest(a: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(a).tobytes()).hexdigest()


def outputs(out: Path, work: Path) -> dict:
    res = {}
    for p in sorted(out.iterdir()):
        if p.suffix == ".npz":
            with np.load(p) as z:
                res[p.name] = {k: digest(z[k]) if z[k].dtype.kind in "fiub" and z[k].ndim else json.dumps(z[k].tolist()) for k in z.files}
        elif p.suffix == ".json":
            text = p.read_text(encoding="utf-8").replace(work.as_posix(), "<work>")
            res[p.name] = {k: v for k, v in json.loads(text).items() if k not in VOLATILE}
        elif p.suffix == ".md":
            text = re.sub(r"\d{4}-\d\d-\d\d \d\d:\d\d", "<date>", p.read_text(encoding="utf-8"))
            res[p.name] = re.sub(r"\d+ s at", "<s> s at", text)
    return res


def run_case(case: str, work: Path, folder: Path) -> dict:
    out = work / case
    out.mkdir(parents=True)
    (work / "geom").mkdir(exist_ok=True)
    (work / "geom" / "water.json").write_text(json.dumps(WATER), encoding="utf-8")
    (work / "oop_check.json").write_text(json.dumps(OOP_CHECK), encoding="utf-8")
    script, *args = CASES[case]
    argv = [a.replace("{out}", out.as_posix()).replace("{work}", work.as_posix()) for a in args]
    env = {**os.environ, "OMP_NUM_THREADS": "1"}
    r = subprocess.run([sys.executable, str(folder / script), *argv], env=env, cwd=folder, capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    return outputs(out, work)


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_outputs_are_unchanged(case, tmp_path):
    pytest.importorskip("pyscf")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it in WSL with --write-golden before changing the scripts")
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
    print(f"pinned {len(CASES)} cases to {GOLDEN}: " + ", ".join(f"{c} ({len(v)} files)" for c, v in pin["cases"].items()))
