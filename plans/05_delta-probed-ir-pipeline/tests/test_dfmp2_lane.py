"""The MP2 basis step's lane (`probes/dfmp2_lane.sh`) with stand-ins for psi4 and the cap: order, resumption, a missing geometry, a
failing molecule, the refusals; and the deploy's file list is closed and tracked."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None or not Path("/usr/bin/time").exists(), reason="needs bash and /usr/bin/time")

FAKE_QC = """#!/usr/bin/env bash
# stands in for the psi4 python: `-c …` prints a version; `dfmp2_rows.py rows --geometry G --basis B --out O …` writes O and the end
# line, unless the geometry's folder is named 'bad'
if [ "$1" = -c ]; then echo 1.11; exit 0; fi
while [ $# -gt 0 ]; do case "$1" in --geometry) g=$2 ;; --basis) b=$2 ;; --out) o=$2 ;; esac; shift; done
case "$g" in */bad/*) echo "psi4 failed"; exit 3 ;; esac
echo "$b" > "$o"; echo "=== DF ROWS DONE $o (1 rows)"
"""
FAKE_CAPPED = """#!/usr/bin/env bash
# stands in for wsl_capped.sh: <cap> -- command …
shift 2; exec "$@"
"""
FAKE_OOM = "#!/usr/bin/env bash\nexit 1\n"


@pytest.fixture
def batch(tmp_path):
    for name, text in (("qc", FAKE_QC), ("capped.sh", FAKE_CAPPED), ("oom.sh", FAKE_OOM)):
        (tmp_path / name).write_text(text, newline="\n")
        (tmp_path / name).chmod(0o755)
    for mol in ("m1", "m2", "bad"):
        (tmp_path / "geoms" / mol).mkdir(parents=True)
        (tmp_path / "geoms" / mol / "geometry.json").write_text("{}")
    (tmp_path / "ready.log").write_text("READY\n")
    return tmp_path


def run(batch, lines, *extra, env=None):
    (batch / "list.txt").write_text("".join(line + "\n" for line in lines), newline="\n")
    full = {**os.environ, "QC": str(batch / "qc"), "CAPPED": str(batch / "capped.sh"), "OOM_CHECK": str(batch / "oom.sh"),
            "PSI_SCRATCH": str(batch / "scratch"), "WAIT_S": "1", **(env or {})}
    return subprocess.run([BASH, str(PLAN / "probes" / "dfmp2_lane.sh"), str(batch), "MP", str(batch / "ready.log"), "READY", *extra],
                          capture_output=True, text=True, env=full, check=False)


def geom(batch, mol):
    return f"{mol}|{(batch / 'geoms' / mol / 'geometry.json').as_posix()}"


def test_the_lane_computes_both_bases_per_molecule_in_list_order_and_resumes(batch):
    done = run(batch, [geom(batch, "m2"), geom(batch, "m1")])
    assert done.returncode == 0, done.stdout + done.stderr
    lines = [line.split(" rows done")[0].strip() for line in done.stdout.splitlines() if "rows done" in line]
    assert lines == ["m2 ccpvdz", "m2 ccpvtz", "m1 ccpvdz", "m1 ccpvtz"]
    assert (batch / "rows" / "m1" / "dfmp2_rows_ccpvtz.npz").read_text().strip() == "cc-pvtz"
    assert "=== (MP) all done: 0 failures or skips" in done.stdout
    again = run(batch, [geom(batch, "m2"), geom(batch, "m1")])
    assert again.returncode == 0 and again.stdout.count("rows found") == 4 and "rows done" not in again.stdout


def test_a_missing_geometry_and_a_failing_molecule_are_named_and_counted_and_the_rest_runs(batch):
    done = run(batch, [f"gone|{(batch / 'nowhere.json').as_posix()}", geom(batch, "bad"), geom(batch, "m1")])
    assert done.returncode == 1
    assert "gone SKIPPED (no geometry" in done.stdout and done.stdout.count("bad cc") == 2 and "ROWS FAILED" in done.stdout
    assert "m1 ccpvtz rows done" in done.stdout and "all done: 3 failures or skips" in done.stdout
    assert (batch / "status_MP.log").read_text().splitlines() == ["gone skipped: no geometry", "bad ccpvdz failed", "bad ccpvtz failed"]


def test_the_dry_run_arms_and_runs_nothing(batch):
    done = run(batch, [geom(batch, "m1")], "--dry-run")
    assert done.returncode == 0 and "armed: 1 molecules, 2 of 2 row files to compute" in done.stdout
    assert "dry run: wait condition met" in done.stdout and not (batch / "rows").exists()


@pytest.mark.parametrize(("lines", "env", "says"), [
    ([], {}, "list.txt names no molecule"),
    (["m1|relative/geometry.json"], {}, "not 'id|/absolute/geometry.json'"),
    (["m1|/x/geometry.json"], {"THREADS": "0"}, "THREADS must be a positive integer"),
    (["m1|/x/geometry.json"], {"MEMORY_GB": "8", "CAP_MB": "8192"}, "does not fit under the cap"),
])
def test_the_lane_refuses_before_the_wait(batch, lines, env, says):
    done = run(batch, lines, env=env)
    assert done.returncode == 1 and says in done.stdout and "start:" not in done.stdout


def test_the_deploy_list_is_closed_and_tracked():
    listed = subprocess.run([BASH, "probes/deploy_dfmp2_lane.sh", "--list-files"], cwd=PLAN, capture_output=True, text=True, check=True)
    files = listed.stdout.split()
    assert "probes/dfmp2_lane.sh" in files and "probes/dfmp2_rows.py" in files
    closure = subprocess.run([sys.executable, "tools/deploy_closure.py", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert closure.returncode == 0, closure.stdout + closure.stderr
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", *files], cwd=PLAN, capture_output=True, text=True, check=False)
    assert tracked.returncode == 0, tracked.stderr
