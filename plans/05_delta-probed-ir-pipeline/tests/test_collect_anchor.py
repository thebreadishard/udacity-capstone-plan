"""`probes/collect_anchor.sh` against a stand-in server (a folder and an ssh that runs the command here): what each stage waits for,
the fetch with its sha256 comparison and its record, a changed file, a second run; and the registry name helper. Linux only: the
stand-in needs /etc/machine-id, which tools/hosts.sh pins a server by."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import collect_anchor_name as N  # noqa: E402  (after the sys.path insert)

BASH = shutil.which("bash")
linux = pytest.mark.skipif(BASH is None or not Path("/etc/machine-id").exists(), reason="needs bash and /etc/machine-id (Linux)")
FAKE_SSH = """#!/usr/bin/env bash
# stands in for `ssh root@ip "command"`: the command runs here
shift; exec bash -c "$1"
"""
ID = "T_0000000001"


@pytest.fixture
def server(tmp_path):
    """A stand-in server with one molecule whose CC run is done; its roots, the environment for the script and the output folder."""
    cc, mp2, corpus = tmp_path / "dpir", tmp_path / "mp2b", tmp_path / "corpus"
    run = cc / "probes" / "results" / f"{ID}_ccpvdz"
    run.mkdir(parents=True)
    for name in ("hessian_ccsd_t.npz", "apt_ccsd_t_field.npz", "grad_00_p.npy", "e8_fd.log"):
        (run / name).write_text(f"content of {name}\n")
    (cc / "geoms" / ID).mkdir(parents=True)
    (cc / "geoms" / ID / "geometry.json").write_text('{"symbols": ["H"]}')
    (corpus / ID).mkdir(parents=True)
    (corpus / ID / "geometry.json").write_text('{"symbols": ["H"]}')
    (cc / "COMMIT").write_text("abc\n")
    (cc / "anchors.log").write_text(f"=== (AS3) {ID} hessian DONE 2026-11-22\n=== (AS3) {ID} apt PASS {{}}\n")
    ssh = tmp_path / "fakessh"
    ssh.write_text(FAKE_SSH, newline="\n")
    ssh.chmod(0o755)
    hosts = tmp_path / "hosts.tsv"
    hosts.write_text(f"srv\t127.0.0.1\t{Path('/etc/machine-id').read_text().strip()}\ta stand-in\n")
    out = f"probes/results_m1/_test_collect_{os.getpid()}"
    env = {**os.environ, "HOSTS_FILE": str(hosts), "HOSTS_SSH": str(ssh), "CC_ROOT": str(cc), "MP2_ROOT": str(mp2),
           "CORPUS_MOLECULES": str(corpus), "COLLECT_OUT": out}
    yield {"cc": cc, "mp2": mp2, "run": run, "env": env, "out": PLAN / out / ID, "corpus": corpus}
    shutil.rmtree(PLAN / out, ignore_errors=True)


def collect(server, mol_id=ID):
    return subprocess.run([BASH, str(PLAN / "probes" / "collect_anchor.sh"), "srv", mol_id], capture_output=True, text=True,
                          env=server["env"], check=False, timeout=120)


def finish_mp2(server):
    rows = server["mp2"] / "rows" / ID
    rows.mkdir(parents=True)
    for b in ("ccpvdz", "ccpvtz"):
        (rows / f"dfmp2_rows_{b}.npz").write_text(b)
        (rows / f"rows_{b}.log").write_text("=== DF ROWS DONE x (3 rows)\n")


@linux
def test_the_cc_folder_comes_home_checked_and_the_run_waits_for_the_mp2_rows(server):
    done = collect(server)
    assert done.returncode == 2, done.stdout + done.stderr
    assert f"FETCHED {ID} cc 4 files" in done.stdout and "MP2 rows of both bases are not finished yet" in done.stdout
    assert (server["out"] / "cc" / "hessian_ccsd_t.npz").read_text() == "content of hessian_ccsd_t.npz\n"
    assert (server["out"] / "server" / "geometry.json").exists() and "apt PASS" in (server["out"] / "server" / "anchors_log_at_fetch.txt").read_text()
    assert f"FETCHED {ID} cc 4 files" in (server["cc"] / "fetched.log").read_text()
    again = collect(server)
    assert again.returncode == 2 and "cc: verified again (4 files, sha256 equal)" in again.stdout
    assert (server["out"] / "FETCHED.txt").read_text().count("FETCHED") == 1          # the record is written once


@linux
def test_nothing_is_fetched_before_the_wave_log_says_done_and_pass(server):
    (server["cc"] / "anchors.log").write_text(f"=== (AS3) {ID} hessian DONE 2026-11-22\n")
    done = collect(server)
    assert done.returncode == 2 and "nothing fetched" in done.stdout and not server["out"].exists()


@linux
def test_a_file_that_differs_from_the_server_s_stops_the_run(server):
    assert collect(server).returncode == 2
    (server["out"] / "cc" / "e8_fd.log").write_text("edited here\n")
    done = collect(server)
    assert done.returncode == 1 and "sha256 MISMATCH" in done.stdout


@linux
def test_a_server_geometry_that_is_not_the_corpus_s_is_refused(server):
    (server["corpus"] / ID / "geometry.json").write_text('{"symbols": ["He"]}')
    done = collect(server)
    assert done.returncode == 1 and "is not the corpus geometry file" in done.stdout


@linux
def test_a_molecule_without_a_corpus_geometry_is_refused_before_the_server_is_asked(server):
    done = collect(server, "T_0000000002")
    assert done.returncode == 1 and "has no corpus geometry" in done.stdout


@linux
def test_with_finished_mp2_rows_they_come_home_and_the_composite_is_attempted(server):
    finish_mp2(server)
    done = collect(server)
    assert f"FETCHED {ID} mp2 4 files" in done.stdout and (server["out"] / "mp2" / "dfmp2_rows_ccpvtz.npz").read_text() == "ccpvtz"
    assert done.returncode == 1 and "COMPOSITE BUILD FAILED" in done.stdout     # the stand-in files are not Hessians; real ones build
    assert not (server["out"] / f"composite_{ID}.npz").exists()


@linux
def test_unfinished_mp2_rows_of_one_basis_keep_the_composite_waiting(server):
    finish_mp2(server)
    (server["mp2"] / "rows" / ID / "rows_ccpvtz.log").write_text("still running\n")
    done = collect(server)
    assert done.returncode == 2 and "not finished yet" in done.stdout and not (server["out"] / "mp2").exists()


def test_the_registry_name_is_the_manifest_s(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text('id,layer,name,smiles\nB_1,B,"2-fluoro, 4-chloropyridine",x\nB_2,B,,y\nB_3,B,a,z\nB_3,B,b,z\n', encoding="utf-8")
    assert N.name_of("B_1", manifest) == "2-fluoro, 4-chloropyridine"
    for bad in ("B_2", "B_3", "B_9"):
        with pytest.raises(SystemExit, match="manifest rows with a name"):
            N.name_of(bad, manifest)
