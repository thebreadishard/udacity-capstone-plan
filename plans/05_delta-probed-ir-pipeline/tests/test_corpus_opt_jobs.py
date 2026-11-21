"""psi4 optimisation jobs for corpus rows and their per-host batches (`probes/corpus_opt_jobs.py`)."""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("rdkit")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import anchor_wave_lists as W
import corpus_opt_jobs as J

DECK = {"low_functional": "B3LYP", "threads": 4, "memory_gb": 8}
ROW = {"id": "B_x", "layer": "B", "name": "pyridine", "smiles": "c1ccncc1", "status": "pending"}


def test_opt_job_optimises_without_hessians_into_the_given_folder():
    job = J.opt_job(ROW, DECK, "/root/dft1/molecules/B_x", {"list": "needs_dft.txt"})
    assert (job["id"], job["layer"], job["out_dir"]) == ("B_x", "B", "/root/dft1/molecules/B_x")
    assert (job["optimise"], job["hessians"], job["grid_check"]) == (True, False, False)
    assert job["deck"] == DECK and job["source"] == {"list": "needs_dft.txt"}
    assert len(job["xyz_angstrom"]) == 11 and {a[0] for a in job["xyz_angstrom"]} == {"C", "H", "N"}


def test_opt_job_refuses_a_row_start_geometry_would_not_optimise(monkeypatch):
    import run_corpus
    monkeypatch.setattr(run_corpus, "start_geometry", lambda row: ([["H", 0.0, 0.0, 0.0]], False))
    with pytest.raises(ValueError, match="would not optimise"):
        J.opt_job(ROW, DECK, "/x", {})


def test_read_ids_skips_comments_and_blank_lines_and_refuses_repeats(tmp_path):
    f = tmp_path / "ids.txt"
    f.write_text("# header\nA\n\nB\n")
    assert J.read_ids(f) == ["A", "B"]
    f.write_text("A\nB\nA\n")
    with pytest.raises(SystemExit, match="twice"):
        J.read_ids(f)


def test_write_batches_writes_jobs_and_ids_cheapest_first(tmp_path):
    items = [W.Candidate("B_x", "batch", 11, 109, 5.0)]
    J.write_batches(tmp_path / "out", {"h1": items, "h2": []}, {"B_x": {k: v for k, v in ROW.items() if k != "id"}}, DECK,
                    "/root/dft1/molecules", "needs_dft.txt")
    job = json.loads((tmp_path / "out" / "h1" / "molecules" / "B_x" / "job.json").read_text())
    assert job["out_dir"] == "/root/dft1/molecules/B_x" and job["source"]["smiles"] == "c1ccncc1"
    assert (tmp_path / "out" / "h1" / "ids.txt").read_text().splitlines()[1:] == ["B_x"]
    assert (tmp_path / "out" / "h2" / "ids.txt").read_text().splitlines()[1:] == []


def test_write_batches_refuses_an_atom_count_that_does_not_match(tmp_path):
    items = [W.Candidate("B_x", "batch", 12, 109, 5.0)]
    with pytest.raises(ValueError, match="atoms embedded"):
        J.write_batches(tmp_path / "out", {"h1": items}, {"B_x": dict(ROW)}, DECK, "/r", "l")


@pytest.mark.parametrize(("extra", "message"), [
    (["--hosts", "h1,h1"], "named twice"), (["--server-root", "rel/path"], "absolute"), (["--threads", "0"], "positive")])
def test_main_refuses_bad_arguments(tmp_path, extra, message):
    ids = tmp_path / "ids.txt"
    ids.write_text("B_x\n")
    base = {"--ids": str(ids), "--hosts": "h1", "--server-root": "/root/dft1/molecules", "--out": str(tmp_path / "o"),
            "--threads": "4", "--memory-gb": "8"}
    base.update(dict(zip(extra[::2], extra[1::2], strict=True)))
    with pytest.raises(SystemExit, match=message):
        J.main([x for kv in base.items() for x in kv])


def test_main_refuses_an_existing_out_folder(tmp_path):
    ids = tmp_path / "ids.txt"
    ids.write_text("B_x\n")
    with pytest.raises(SystemExit, match="exists"):
        J.main(["--ids", str(ids), "--hosts", "h1", "--server-root", "/r", "--out", str(tmp_path), "--threads", "4", "--memory-gb", "8"])
