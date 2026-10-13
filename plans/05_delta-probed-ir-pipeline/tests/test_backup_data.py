"""tools/backup_data.py (13 Oct 2026, after the 03:30 run failed): psi4 scratch files are not mirrored, and a file that vanishes while the
plan is made is skipped and counted instead of ending the backup."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import backup_data as B  # noqa: E402


def test_psi4_scratch_names_are_excluded():
    assert B.PSI4_SCRATCH.match("psi.14148.clean") and B.PSI4_SCRATCH.match("psi.8.clean")
    assert not B.PSI4_SCRATCH.match("psi4_worker.py") and not B.PSI4_SCRATCH.match("psi4.out")


def test_a_file_that_vanishes_during_the_plan_is_skipped(tmp_path, monkeypatch):
    src = tmp_path / "plan" / "data"
    src.mkdir(parents=True)
    (src / "keep.json").write_text("{}")
    gone = src / "gone.json"
    gone.write_text("{}")
    monkeypatch.setattr(B, "PLAN", tmp_path / "plan")
    monkeypatch.setattr(B, "SOURCES", [("data", set())])
    monkeypatch.setattr(B, "SINGLE_FILES", [])
    real_stat = Path.stat

    def stat(self, *a, **k):
        if self.name == "gone.json":
            raise FileNotFoundError(self)
        return real_stat(self, *a, **k)
    monkeypatch.setattr(Path, "stat", stat)
    pairs, n, _ = B.plan_copies(tmp_path / "mirror")
    assert n == 1 and B.plan_copies.vanished == 1 and [p.name for p, _ in pairs] == ["keep.json"]
