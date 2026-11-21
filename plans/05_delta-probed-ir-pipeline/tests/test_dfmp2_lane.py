"""The MP2 basis step's lane (`probes/dfmp2_lane.sh`) with stand-ins for psi4, the cap and the OOM check: order, resumption, the
molecules it refuses, a failing and a killed molecule, the wait and its stop, the refusals before the wait; and the deploy's file list
is closed and tracked."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
needs_bash = pytest.mark.skipif(BASH is None, reason="needs bash")
needs_time = pytest.mark.skipif(BASH is None or not Path("/usr/bin/time").exists(), reason="needs bash and /usr/bin/time (Linux)")

FAKE_QC = """#!/usr/bin/env bash
# stands in for the psi4 python: `-c …` prints a version; `dfmp2_rows.py rows --geometry G --basis B --out O …` writes O and the end
# line — unless the geometry's folder is 'bad' (fails) or 'big' (writes a partial file and dies, as a kill at the cap leaves it)
if [ "$1" = -c ]; then echo 1.11; exit 0; fi
while [ $# -gt 0 ]; do case "$1" in --geometry) g=$2 ;; --basis) b=$2 ;; --out) o=$2 ;; esac; shift; done
case "$g" in */bad/*) echo "psi4 failed"; exit 3 ;; */big/*) echo partial > "$o"; exit 137 ;; esac
echo "$b" > "$o"; echo "=== DF ROWS DONE $o (1 rows)"
"""
FAKE_CAPPED = """#!/usr/bin/env bash
# stands in for wsl_capped.sh: <cap> -- command …
shift 2; exec "$@"
"""
FAKE_OOM = """#!/usr/bin/env bash
# stands in for cation_oom_check.sh <id>: only 'big' was killed at the cap
[ "$1" = big ]
"""
DONE = '{"status": "done", "n_imaginary_b3lyp": 0, "n_imaginary_wb97x": 0}'


@pytest.fixture
def batch(tmp_path):
    for name, text in (("qc", FAKE_QC), ("capped.sh", FAKE_CAPPED), ("oom.sh", FAKE_OOM)):
        (tmp_path / name).write_text(text, newline="\n")
        (tmp_path / name).chmod(0o755)
    for mol in ("m1", "m2", "bad", "big"):
        (tmp_path / "geoms" / mol).mkdir(parents=True)
        (tmp_path / "geoms" / mol / "geometry.json").write_text('{"symbols": ["H"]}')
    (tmp_path / "ready.log").write_text("READY\n")
    return tmp_path


def run(batch, lines, *extra, env=None, wait_log="ready.log"):
    (batch / "list.txt").write_text("".join(line + "\n" for line in lines), newline="\n")
    full = {**os.environ, "QC": str(batch / "qc"), "CAPPED": str(batch / "capped.sh"), "OOM_CHECK": str(batch / "oom.sh"),
            "PSI_SCRATCH": str(batch / "scratch"), "WAIT_S": "1", **(env or {})}
    return subprocess.run([BASH, str(PLAN / "probes" / "dfmp2_lane.sh"), str(batch), "MP", str(batch / wait_log), "READY", *extra],
                          capture_output=True, text=True, env=full, check=False, timeout=60)


def geom(batch, mol, record=None):
    line = f"{mol}|{(batch / 'geoms' / mol / 'geometry.json').as_posix()}"
    return line if record is None else f"{line}|{Path(record).as_posix()}"


@needs_time
def test_the_lane_computes_both_bases_per_molecule_in_list_order_and_resumes(batch):
    done = run(batch, [geom(batch, "m2"), geom(batch, "m1")])
    assert done.returncode == 0, done.stdout + done.stderr
    lines = [line.split(" rows done")[0].strip() for line in done.stdout.splitlines() if "rows done" in line]
    assert lines == ["m2 ccpvdz", "m2 ccpvtz", "m1 ccpvdz", "m1 ccpvtz"]
    assert (batch / "rows" / "m1" / "dfmp2_rows_ccpvtz.npz").read_text().strip() == "cc-pvtz"
    assert "=== (MP) all done: 0 failures or skips" in done.stdout
    again = run(batch, [geom(batch, "m2"), geom(batch, "m1")])
    assert again.returncode == 0 and again.stdout.count("rows found") == 4 and "rows done" not in again.stdout
    (batch / "rows" / "m1" / "dfmp2_rows_ccpvdz.npz").unlink()                 # a row file removed: its old end line does not vouch for it
    third = run(batch, [geom(batch, "m2"), geom(batch, "m1")])
    assert third.stdout.count("rows found") == 3 and "m1 ccpvdz rows done" in third.stdout


@needs_time
def test_a_failing_and_a_killed_molecule_are_named_and_counted_and_the_rest_runs(batch):
    done = run(batch, [geom(batch, "bad"), geom(batch, "big"), geom(batch, "m1")])
    assert done.returncode == 1
    assert done.stdout.count("bad cc") == 2 and done.stdout.count("ROWS FAILED") == 2
    assert done.stdout.count("big cc") == 2 and done.stdout.count("KILLED at the cap of 8192 MB") == 2
    assert "m1 ccpvtz rows done" in done.stdout and "all done: 4 failures or skips" in done.stdout
    assert (batch / "status_MP.log").read_text().splitlines() == ["bad ccpvdz failed", "bad ccpvtz failed", "big ccpvdz killed at the cap",
                                                                  "big ccpvtz killed at the cap"]
    again = run(batch, [geom(batch, "big")])                                    # the partial file of the kill is not taken for a finished one
    assert again.stdout.count("KILLED at the cap") == 2 and "rows found" not in again.stdout


@needs_time
@pytest.mark.parametrize(("geometry", "record", "why"), [
    (None, None, "no geometry at"),
    ('{"charge": 1, "multiplicity": 2}', None, "names a charge other than 0"),
    ('{"charge": 0, "multiplicity": 3}', None, "names a multiplicity other than 1"),
    ('{"charge": 0, "multiplicity": 1}', "missing", "no DFT record at"),
    ('{"charge": 0, "multiplicity": 1}', '{"status": "failed"}', "its DFT record is not done"),
    ('{"charge": 0, "multiplicity": 1}', '{"status": "done", "n_imaginary_b3lyp": 1, "n_imaginary_wb97x": 0}', "no imaginary mode"),
    ('{"charge": 0, "multiplicity": 1}', '{"status": "done", "labels": "analytic_only"}', "no imaginary mode"),   # optimised, never labelled
])
def test_a_molecule_that_must_not_get_rows_is_skipped_by_name(batch, geometry, record, why):
    g = batch / "geoms" / "x" / "geometry.json"
    g.parent.mkdir()
    if geometry is not None:
        g.write_text(geometry)
    rec = None
    if record is not None:
        rec = batch / "geoms" / "x" / "result.json"
        if record != "missing":
            rec.write_text(record)
    done = run(batch, [geom(batch, "x", rec), geom(batch, "m1")])
    assert done.returncode == 1 and "x SKIPPED (" in done.stdout and why in done.stdout and "m1 ccpvtz rows done" in done.stdout
    assert not (batch / "rows" / "x").exists() and "all done: 1 failures or skips" in done.stdout


@needs_time
def test_a_dft_molecule_done_without_imaginary_modes_gets_its_rows(batch):
    rec = batch / "geoms" / "m1" / "result.json"
    rec.write_text(DONE)
    (batch / "geoms" / "m1" / "geometry.json").write_text('{"charge": 0, "multiplicity": 1}')
    done = run(batch, [geom(batch, "m1", rec)])
    assert done.returncode == 0 and "m1 ccpvtz rows done" in done.stdout


@needs_time
def test_the_dry_run_arms_and_runs_nothing(batch):
    done = run(batch, [geom(batch, "m1")], "--dry-run")
    assert done.returncode == 0 and "armed: 1 molecules, 2 of 2 row files to compute" in done.stdout
    assert "dry run: wait condition met" in done.stdout and not (batch / "rows").exists()


@needs_time
def test_the_wait_stops_by_name_when_what_it_waits_for_is_gone(batch):
    done = run(batch, [geom(batch, "m1")], env={"WAIT_PGREP": "no_such_process_dfmp2_lane_test"}, wait_log="never.log")
    assert done.returncode == 1 and "STOPPED: the wait condition is unmet and no process matches" in done.stdout
    assert "start:" not in done.stdout and not (batch / "rows").exists()


@needs_time
def test_the_wait_says_waiting_and_starts_when_the_condition_is_met(batch):
    lane = subprocess.Popen([BASH, "-c", f'sleep 3; echo READY > "{(batch / "later.log").as_posix()}"'])
    done = run(batch, [geom(batch, "m1")], wait_log="later.log")
    lane.wait()
    assert done.returncode == 0 and "=== (MP) waiting" in done.stdout and "m1 ccpvtz rows done" in done.stdout


@needs_bash
@pytest.mark.parametrize(("lines", "env", "says"), [
    ([], {}, "list.txt names no molecule"),
    (["m1|relative/geometry.json"], {}, "not 'id|/absolute/geometry.json"),
    (["m1|/x/geometry.json|/x/r.json|more"], {}, "not 'id|/absolute/geometry.json"),
    (["m1|/x/geometry.json"], {"THREADS": "0"}, "THREADS must be a positive integer"),
    (["m1|/x/geometry.json"], {"MEMORY_GB": "8", "CAP_MB": "8192"}, "does not fit under the cap"),
])
def test_the_lane_refuses_before_the_wait(batch, lines, env, says):
    done = run(batch, lines, env=env)
    assert done.returncode == 1 and says in done.stdout and "start:" not in done.stdout


@needs_bash
def test_the_deploy_list_is_closed_and_tracked():
    listed = subprocess.run([BASH, "probes/deploy_dfmp2_lane.sh", "--list-files"], cwd=PLAN, capture_output=True, text=True, check=True)
    files = listed.stdout.split()
    assert "probes/dfmp2_lane.sh" in files and "probes/dfmp2_rows.py" in files
    closure = subprocess.run([sys.executable, "tools/deploy_closure.py", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert closure.returncode == 0, closure.stdout + closure.stderr
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert tracked.returncode == 0, tracked.stderr
