"""The pure helpers of probes/e8_cc_hessian_fd.py without importing it: the probe imports pyscf, which the laptop's python lacks, so its limits,
file helpers and checks (core_orbital_count, select_displacements, pair_consistency, …) are executed from its source — from the first limit to
the gradient section."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np

SRC = Path(__file__).resolve().parents[1] / "probes" / "e8_cc_hessian_fd.py"
START, END = "LAMBDA_TOL = ", "# ---- the CCSD(T) gradient"


def source() -> str:
    return SRC.read_text(encoding="utf-8")


def pure_helpers() -> dict:
    sys.path.insert(0, str(SRC.parent))
    from qc_common import CORE_ORBITALS
    text = source()
    ns = {"np": np, "os": os, "json": json, "time": time, "Path": Path, "CORE_ORBITALS": CORE_ORBITALS}
    exec(text[text.index(START): text.index(END)], ns)
    return ns
