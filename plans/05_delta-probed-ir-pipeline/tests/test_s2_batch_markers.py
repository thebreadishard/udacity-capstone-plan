"""probes/s2_batch.sh's markers (21 Oct 2026): a molecule is STOPPED only when the stop rule fired, FAILED with its first error line
otherwise (S1-TZ naphthalene's 'SCF not converged' was reported as a time-limit stop), and a resumed molecule's earlier log is kept. The
batch runs beside a stand-in for s1_anharmonic_level.sh that prints what the case needs."""
import shutil
import subprocess
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None, reason="needs bash")

STAND_IN = {
    "stop": "echo 'STOP: the first Hessian took 5000 s > 4200 s'; echo '=== (S1) T: STOPPED by the stop rule or a failure'; exit 1",
    "scf": "echo 'SCF not converged at stubs/mode33_p.json'; echo '=== (S1) T: STOPPED by the stop rule or a failure'; exit 1",
    "ok": "exit 0",
}


def run_batch(tmp_path: Path, case: str) -> str:
    here = tmp_path / "probes"
    here.mkdir(exist_ok=True)
    shutil.copy(PLAN / "probes" / "s2_batch.sh", here / "s2_batch.sh")
    (here / "s1_anharmonic_level.sh").write_text(f"#!/usr/bin/env bash\n{STAND_IN[case]}\n", encoding="utf-8", newline="\n")
    (tmp_path / "ids.tsv").write_text("A_x\tgeom.json\n", encoding="utf-8", newline="\n")
    p = subprocess.run([BASH, str(here / "s2_batch.sh"), str(tmp_path / "ids.tsv"), str(tmp_path / "out"), "1", "1", "T:def2-tzvp:75,302"],
                       capture_output=True, text=True, check=False, env={"MAX_FIRST": "4200", "PATH": str(Path(BASH).parent)})
    return p.stdout


def test_the_stop_rule_is_a_stop(tmp_path):
    assert "A_x: STOPPED (first displaced Hessian over 4200 s)" in run_batch(tmp_path, "stop")


def test_an_scf_failure_is_a_failure_with_its_reason(tmp_path):
    out = run_batch(tmp_path, "scf")
    assert "A_x: FAILED rc=1: SCF not converged at stubs/mode33_p.json" in out and "STOPPED" not in out


def test_a_resumed_molecule_keeps_its_earlier_log(tmp_path):
    run_batch(tmp_path, "scf")
    run_batch(tmp_path, "ok")
    logs = sorted(p.name for p in (tmp_path / "out").glob("A_x*.log"))
    assert len(logs) == 2 and "A_x.log" in logs
