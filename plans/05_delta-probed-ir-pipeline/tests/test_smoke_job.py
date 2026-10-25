"""probes/smoke_job.py: lever 5's psi4 job for a smoke geometry — optimise, no FD Hessians, coordinates in ångström, written to and named
after its folder."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
from smoke_job import BOHR, DECK, smoke_job  # noqa: E402

WATER = PLAN / "probes" / "results_m1" / "water_dipole_fd_2026-10-02" / "geometry.json"


def test_the_job_asks_what_lever_5_asks():
    geometry = json.loads(WATER.read_text(encoding="utf-8"))
    deck = json.loads(Path(DECK).read_text(encoding="utf-8"))
    j = smoke_job(geometry, "/root/x_smoke/water_plus/molecules/water_plus", deck)
    assert j["id"] == "water_plus" and j["out_dir"] == "/root/x_smoke/water_plus/molecules/water_plus"
    assert j["optimise"] is True and j["hessians"] is False and j["grid_check"] is False
    assert j["deck"]["basis"] == deck["basis"] and j["deck"]["threads"] == 2
    assert [row[0] for row in j["xyz_angstrom"]] == geometry["symbols"]
    assert j["xyz_angstrom"][0][1:] == pytest.approx([c * BOHR for c in geometry["coords_bohr"][0]])


def test_the_command_writes_job_json_into_the_folder(tmp_path):
    out = tmp_path / "water_plus"
    subprocess.run([sys.executable, str(PLAN / "probes" / "smoke_job.py"), str(WATER), str(out)], check=True)
    j = json.loads((out / "job.json").read_text(encoding="utf-8"))
    assert j["id"] == "water_plus" and Path(j["out_dir"]) == out.resolve()


def test_a_server_path_is_kept_as_given_with_a_separate_job_file(tmp_path):
    job_file = tmp_path / "staging" / "job.json"
    subprocess.run([sys.executable, str(PLAN / "probes" / "smoke_job.py"), str(WATER), "/root/labels/psi4_smoke/water_smoke",
                    "--job-file", str(job_file)], check=True)
    j = json.loads(job_file.read_text(encoding="utf-8"))
    assert j["out_dir"] == "/root/labels/psi4_smoke/water_smoke" and j["id"] == "water_smoke"


def test_a_relative_out_dir_is_refused(tmp_path):
    res = subprocess.run([sys.executable, str(PLAN / "probes" / "smoke_job.py"), str(WATER), "water_plus"], cwd=tmp_path,
                         capture_output=True, text=True, check=False)
    assert res.returncode != 0 and "out_dir must be absolute" in res.stderr
