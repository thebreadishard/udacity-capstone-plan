"""P3-2 cation gate (decision 54, 3 Oct 2026): probes/rungC_family_floor_ceiling.py --dirs reads row directories outside the corpus. A complete row
(four Hessians) yields a per-family floor through the corpus labeller; a row without the FD ωB97X file is reported as incomplete with what can still be
read (B3LYP frequencies FD vs analytic), never skipped silently; the gate verdict follows the registered line (median floor per family ≤ limit)."""
import shutil
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
CORPUS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
BENZENE = CORPUS / "A_8448043181"
sys.path.insert(0, str(PLAN / "probes"))
pytestmark = pytest.mark.skipif(not (BENZENE / "hessian_wb97x_analytic.npz").exists(), reason="corpus benzene row with analytic Hessians not present")
FC = pytest.importorskip("rungC_family_floor_ceiling")


def test_complete_and_incomplete_rows(tmp_path):
    full = tmp_path / "C_full"
    shutil.copytree(BENZENE, full, ignore=shutil.ignore_patterns("psi4.out", "*.txt", "dipole_*"))
    part = tmp_path / "C_part"
    shutil.copytree(full, part)
    (part / "hessian_wb97x.npz").unlink()                                   # the benzene⁺ situation of 3 Oct: no FD ωB97X
    rows, partial = FC.rows_from_dirs([full, part], log=lambda *a: None)
    assert [r["id"] for r in rows] == ["C_full"] and set(rows[0]["fd_vs_analytic"]) >= {"ring-ip", "CH-stretch", "CH-oop"}
    assert rows[0]["fd_vs_analytic"]["ring-ip"] > 10                        # benzene's known FD artefact (29 Sep): the floor reads it
    assert len(partial) == 1 and partial[0]["id"] == "C_part" and partial[0]["incomplete"] is True
    assert partial[0]["files"]["wb97x"] is False and 0 < partial[0]["b3lyp_freq_fd_vs_analytic_rms"] < 5


def test_gate_verdict_follows_the_line():
    rows = [{"fd_vs_analytic": {"ring-ip": 1.2, "CH-oop": 1.4}}, {"fd_vs_analytic": {"ring-ip": 1.0, "CH-oop": 1.6}}]
    v = FC.gate_verdict(rows, 1.5)
    assert v["pass"] is True and v["median_floor"]["CH-oop"] == 1.5
    assert FC.gate_verdict(rows, 1.4)["pass"] is False
    assert FC.gate_verdict([], 1.5)["pass"] is False                        # no complete row: nothing is licensed
