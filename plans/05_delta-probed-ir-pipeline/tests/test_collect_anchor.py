"""`probes/collect_anchor.sh` against a stand-in server (a folder and an ssh that runs the command here): what each stage waits for,
the fetch with its sha256 comparison and its record, the failed runs that still come home, a changed file, a second run, a server that
does not answer, a list on stdin; and what it asks of the manifest and the registry. The stand-in needs /etc/machine-id (Linux), which
tools/hosts.sh pins a server by. Stages 3 and 4 need real Hessians: the build's refusal of the stand-in files is asserted here, their
success is each real anchor's own run."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import collect_anchor_registry as CR  # noqa: E402  (after the sys.path insert)

BASH = shutil.which("bash")
linux = pytest.mark.skipif(BASH is None or not Path("/etc/machine-id").exists(), reason="needs bash and /etc/machine-id (Linux)")
FAKE_SSH = """#!/usr/bin/env bash
# stands in for `ssh root@ip "command"`: the command runs here; it reads stdin as ssh does
shift; exec bash -c "$1"
"""
ID = "T_0000000001"
DONE = f"=== (AS3) {ID} hessian DONE 2026-11-22\n=== (AS3) {ID} apt PASS {{}}\n"


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
    (cc / "anchors.log").write_text(DONE)
    ssh = tmp_path / "fakessh"
    ssh.write_text(FAKE_SSH, newline="\n")
    ssh.chmod(0o755)
    hosts = tmp_path / "hosts.tsv"
    hosts.write_text(f"srv\t127.0.0.1\t{Path('/etc/machine-id').read_text().strip()}\ta stand-in\n")
    env = {**os.environ, "HOSTS_FILE": str(hosts), "HOSTS_SSH": str(ssh), "CC_ROOT": str(cc), "MP2_ROOT": str(mp2),
           "CORPUS_MOLECULES": str(corpus), "COLLECT_OUT": str(tmp_path / "home")}
    return {"cc": cc, "mp2": mp2, "run": run, "env": env, "out": tmp_path / "home" / ID, "corpus": corpus, "ssh": ssh}


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
def test_nothing_is_fetched_while_the_wave_log_has_no_end_for_the_molecule(server):
    (server["cc"] / "anchors.log").write_text(f"=== (AS3) {ID} hessian DONE 2026-11-22\n")
    done = collect(server)
    assert done.returncode == 2 and "nothing fetched" in done.stdout and not server["out"].exists()


@linux
@pytest.mark.parametrize(("line", "state"), [
    (f"=== (AS3) {ID} hessian IMAGINARY 2026-11-22\n", "IMAGINARY"),
    (f"=== (AS3) {ID} hessian FAILED (see x) 2026-11-22\n", "HESSIAN_FAILED"),
    (f"=== (AS3) {ID} hessian DONE 2026-11-22\n=== (AS3) {ID} apt FAIL {{}}\n", "APT_FAILED"),
])
def test_a_run_that_ended_in_a_failure_still_comes_home_and_ends_with_its_own_code(server, line, state):
    (server["cc"] / "anchors.log").write_text(line)
    done = collect(server)
    assert done.returncode == 3 and f"ended as {state}" in done.stdout and f"FETCHED {ID} cc 4 files" in done.stdout
    assert (server["out"] / "cc" / "grad_00_p.npy").exists() and not (server["out"] / "mp2").exists()


@linux
def test_the_user_s_accepted_apt_counts_as_an_end(server):
    (server["cc"] / "anchors.log").write_text(f"=== (AS3) {ID} hessian DONE 2026-11-22\n=== (AS3) {ID} apt ACCEPTED by the user\n")
    assert collect(server).returncode == 2                                           # fetched, then waits for the MP2 rows


@linux
def test_a_longer_id_with_the_same_start_is_not_this_molecule(server):
    (server["cc"] / "anchors.log").write_text(DONE.replace(ID, ID + "9"))
    done = collect(server)
    assert done.returncode == 2 and "nothing fetched" in done.stdout


@linux
def test_a_server_that_does_not_answer_is_an_error_not_a_wait(server):
    server["ssh"].write_text("#!/usr/bin/env bash\nexit 255\n", newline="\n")
    done = collect(server)
    assert done.returncode == 1 and "UNREACHABLE" in done.stdout


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


@linux
def test_the_script_leaves_a_list_on_stdin_to_the_loop_that_reads_it(server):
    loop = f'while read -r id; do bash "{PLAN / "probes" / "collect_anchor.sh"}" srv "$id" > /dev/null 2>&1; echo "$id $?"; done'
    done = subprocess.run([BASH, "-c", loop], input=f"{ID}\nT_0000000002\nT_0000000003\n", capture_output=True, text=True,
                          env=server["env"], check=False, timeout=120)
    assert done.stdout.split("\n")[:3] == [f"{ID} 2", "T_0000000002 1", "T_0000000003 1"]


def test_the_registry_name_is_the_manifest_s(tmp_path):
    manifest = tmp_path / "manifest.csv"
    manifest.write_text('id,layer,name,smiles\nB_1,B,"2-fluoro, 4-chloropyridine",x\nB_2,B,,y\nB_3,B,a,z\nB_3,B,b,z\n', encoding="utf-8")
    assert CR.name_of("B_1", manifest) == "2-fluoro, 4-chloropyridine"
    for bad in ("B_2", "B_3", "B_9"):
        with pytest.raises(SystemExit, match="manifest rows with a name"):
            CR.name_of(bad, manifest)


def test_the_registry_status_is_given_only_for_an_entry_that_passes_its_check(tmp_path):
    f = tmp_path / "p" / "composite_a.npz"
    f.parent.mkdir()
    np.savez(f, H_raw=np.eye(3), H_projected=np.eye(3), status="VALID")
    e = {"mol_id": "a", "name": "a", "path": "p/composite_a.npz", "level": "composite", "tier": "TZ", "kind": "composite",
         "status": "carried", "date": "2026-11-22", "sha16": CR.AR.sha16(f), "checks": "—", "note": ""}
    assert CR.status_of("p/composite_a.npz", [e], tmp_path) == "carried"
    assert CR.status_of("p/composite_a.npz", [{**e, "status": "experimental"}], tmp_path) == "experimental"
    with pytest.raises(SystemExit, match="0 registry entries"):
        CR.status_of("p/other.npz", [e], tmp_path)
    np.savez(f, H_raw=2 * np.eye(3), H_projected=2 * np.eye(3), status="VALID")
    with pytest.raises(SystemExit, match="changed since it was registered"):
        CR.status_of("p/composite_a.npz", [e], tmp_path)
