"""tools/archive_psi4_logs.py on a synthetic plan: only the files the mirror excludes by name are collected, and only under sources that
exclude them; the archive holds them with the sha256 list and reads back equal; a changed or missing member is refused; the archive may not
be written inside the plan."""
import io
import sys
import tarfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
A = pytest.importorskip("archive_psi4_logs")
NAMES = frozenset({"psi4.out", "worker_stdout.txt"})


@pytest.fixture
def plan(tmp_path):
    files = {"corpus/molecules/A_1/psi4.out": "gradient 1\n" * 50, "corpus/molecules/A_1/hessian.npz": "npz",
             "corpus/molecules/A_2/worker_stdout.txt": "worker", "results/run/psi4.out": "gradient 2\n" * 50,
             "out/psi4.out": "a log under a source that keeps it"}
    for rel, text in files.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    sources = [("corpus/molecules", NAMES), ("results", NAMES), ("out", set()), ("absent", NAMES)]
    return tmp_path, sources


def test_collect_takes_the_excluded_names_under_excluding_sources_only(plan):
    root, sources = plan
    assert A.collect(root, sources, NAMES) == ["corpus/molecules/A_1/psi4.out", "corpus/molecules/A_2/worker_stdout.txt", "results/run/psi4.out"]


def test_the_archive_reads_back_equal_and_carries_its_list(plan, tmp_path):
    root, sources = plan
    files = A.collect(root, sources, NAMES)
    manifest = A.manifest_text(root, files)
    archive = tmp_path / "logs.tar.xz"
    A.build(root, files, manifest, archive)
    assert A.verify(archive, manifest) == 3
    with tarfile.open(archive, "r:xz") as tar:
        assert tar.extractfile("SHA256SUMS.tsv").read().decode("utf-8") == manifest


def test_a_changed_or_missing_member_is_refused(plan, tmp_path):
    root, sources = plan
    files = A.collect(root, sources, NAMES)
    manifest = A.manifest_text(root, files)
    archive = tmp_path / "logs.tar.xz"
    with tarfile.open(archive, "w:xz") as tar:
        data = b"tampered"
        info = tarfile.TarInfo(files[0])
        info.size = len(data)
        tar.addfile(info, io.BytesIO(data))
    with pytest.raises(SystemExit, match="does not match"):
        A.verify(archive, manifest)


def test_the_archive_may_not_land_inside_the_plan():
    with pytest.raises(SystemExit, match="inside the plan"):
        A.main(["--out", str(A.PLAN / "probes" / "results_m1")])
