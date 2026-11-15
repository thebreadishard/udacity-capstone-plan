"""probes/labels_merge_checked.py on synthetic folders: the copy, its refusals (all or nothing), a copy that fails half way and the
run after it, and that the record keeps a sha256 for every label file."""
import json
import shutil
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import labels_merge_checked as M  # noqa: E402

N_LABELS = len(M.LABEL_FILES)


def molecule(root: Path, name: str, geometry: str = "g", files: dict[str, bytes] | None = None) -> Path:
    folder = root / name
    folder.mkdir(parents=True)
    (folder / M.GEOMETRY).write_text(geometry, encoding="utf-8")
    for file_name, content in (files or {}).items():
        (folder / file_name).write_bytes(content)
    return folder


def source_files(tag: bytes) -> dict[str, bytes]:
    """A server folder: the four label files, and the finite-difference labels and a log that must not be copied."""
    return {name: tag + name.encode() for name in M.LABEL_FILES} | {"hessian_b3lyp.npz": b"the server's fd", "pyscf.log": b"log"}


@pytest.fixture
def folders(tmp_path):
    source, corpus = tmp_path / "source", tmp_path / "corpus"
    for name in ("A_1", "B_2"):
        molecule(source, name, files=source_files(name.encode()))
        molecule(corpus, name, files={"hessian_b3lyp.npz": b"fd"})
    return source, corpus


def test_only_the_label_files_are_copied_and_the_fd_labels_stay(folders):
    source, corpus = folders
    record = M.merge(source, corpus, 2, dry_run=False)
    assert (record["source_molecules"], record["to_copy"], record["identical"], record["refusals"], record["error"]) == (2, 8, {}, [], None)
    assert len(record["copied"]) == 2 * N_LABELS
    for name in ("A_1", "B_2"):
        for file_name in M.LABEL_FILES:
            assert (corpus / name / file_name).read_bytes() == (source / name / file_name).read_bytes()
            assert record["copied"][f"{name}/{file_name}"] == M.sha256(source / name / file_name)
        assert (corpus / name / "hessian_b3lyp.npz").read_bytes() == b"fd"          # the corpus's own, not the server's
        assert sorted(p.name for p in (corpus / name).iterdir()) == sorted([M.GEOMETRY, "hessian_b3lyp.npz", *M.LABEL_FILES])


def test_a_dry_run_copies_nothing(folders):
    source, corpus = folders
    record = M.merge(source, corpus, 2, dry_run=True)
    assert record["to_copy"] == 2 * N_LABELS and record["copied"] == {}
    assert not (corpus / "A_1" / M.LABEL_FILES[0]).exists()


def test_a_second_run_finds_everything_identical_with_its_sha256(folders):
    source, corpus = folders
    first = M.merge(source, corpus, 2, dry_run=False)
    second = M.merge(source, corpus, 2, dry_run=False)
    assert (second["to_copy"], second["copied"]) == (0, {})
    assert second["identical"] == first["copied"]


def test_a_part_already_there_is_kept_and_the_rest_copied(folders):
    source, corpus = folders
    shutil.copyfile(source / "A_1" / M.LABEL_FILES[0], corpus / "A_1" / M.LABEL_FILES[0])
    record = M.merge(source, corpus, 2, dry_run=False)
    assert list(record["identical"]) == [f"A_1/{M.LABEL_FILES[0]}"] and len(record["copied"]) == 2 * N_LABELS - 1


@pytest.mark.parametrize(("spoil", "reason"), [
    (lambda s, c: (c / "B_2" / M.GEOMETRY).write_text("other", encoding="utf-8"), "geometry.json differs"),
    (lambda s, c: (c / "B_2" / M.LABEL_FILES[1]).write_bytes(b"another label"), "already holds another"),
    (lambda s, c: (s / "B_2" / M.LABEL_FILES[2]).unlink(), "the source has no"),
    (lambda s, c: (c / "B_2" / M.GEOMETRY).unlink(), "missing in the source or the corpus"),
    (lambda s, c: (c / "B_2" / (M.LABEL_FILES[3] + M.TMP_SUFFIX)).write_bytes(b"half"), "leftover"),
])
def test_one_bad_molecule_refuses_the_whole_merge(folders, spoil, reason):
    source, corpus = folders
    spoil(source, corpus)
    record = M.merge(source, corpus, 2, dry_run=False)
    assert len(record["refusals"]) == 1 and reason in record["refusals"][0]
    assert record["copied"] == {} and not (corpus / "A_1" / M.LABEL_FILES[0]).exists()     # the good molecule is not copied either


def test_another_number_of_molecules_than_expected_is_refused(folders):
    source, corpus = folders
    molecule(source, "C_3", files=source_files(b"c"))
    molecule(corpus, "C_3")
    record = M.merge(source, corpus, 2, dry_run=False)
    assert "3 molecule folders, 2 expected" in record["refusals"][0] and record["copied"] == {}
    (tmp := source.parent / "empty").mkdir()
    assert "0 molecule folders, 2 expected" in M.merge(tmp, corpus, 2, dry_run=False)["refusals"][0]
    molecule(source, "D_4", files=source_files(b"d"))                                   # in the source, not in the corpus
    assert any("D_4: no such folder in the corpus" in r for r in M.merge(source, corpus, 4, dry_run=False)["refusals"])


def test_a_copy_that_differs_is_never_put_in_place(folders, monkeypatch):
    source, corpus = folders
    target = corpus / "A_1" / M.LABEL_FILES[0]

    def torn_copy(src, dst):
        Path(dst).write_bytes(b"torn")

    monkeypatch.setattr(M.shutil, "copyfile", torn_copy)
    with pytest.raises(RuntimeError, match="the copy differs"):
        M.copy_checked(source / "A_1" / M.LABEL_FILES[0], target)
    assert not target.exists() and not target.with_name(target.name + M.TMP_SUFFIX).exists()


def test_a_target_that_appeared_after_planning_is_left_alone(folders):
    source, corpus = folders
    target = corpus / "A_1" / M.LABEL_FILES[0]
    target.write_bytes(b"someone else's")
    with pytest.raises(RuntimeError, match="appeared after the merge was planned"):
        M.copy_checked(source / "A_1" / M.LABEL_FILES[0], target)
    assert target.read_bytes() == b"someone else's" and not target.with_name(target.name + M.TMP_SUFFIX).exists()


def test_a_failed_copy_stops_with_a_record_and_the_next_run_finishes(folders, monkeypatch):
    source, corpus = folders
    real_copy, calls = M.copy_checked, []

    def failing_third(src, dst):
        calls.append(dst)
        if len(calls) == 3:
            raise PermissionError("held by another process")
        return real_copy(src, dst)

    monkeypatch.setattr(M, "copy_checked", failing_third)
    first = M.merge(source, corpus, 2, dry_run=False)
    assert len(first["copied"]) == 2 and "PermissionError" in first["error"] and len(calls) == 3      # stopped at the failure
    monkeypatch.setattr(M, "copy_checked", real_copy)
    second = M.merge(source, corpus, 2, dry_run=False)
    assert second["error"] is None and second["identical"] == first["copied"] and len(second["copied"]) == 2 * N_LABELS - 2


def run_main(monkeypatch, *args: str) -> None:
    monkeypatch.setattr(sys, "argv", ["labels_merge_checked.py", *args])
    M.main()


def test_the_command_copies_records_and_refuses(folders, tmp_path, monkeypatch, capsys):
    source, corpus = folders
    dry, real = tmp_path / "dry.json", tmp_path / "real.json"
    run_main(monkeypatch, str(source), str(corpus), str(dry), "--expect-molecules", "2", "--dry-run")
    assert json.loads(dry.read_text(encoding="utf-8"))["dry_run"] is True and "DRY RUN" in capsys.readouterr().out
    with pytest.raises(SystemExit, match="is not overwritten"):
        run_main(monkeypatch, str(source), str(corpus), str(dry), "--expect-molecules", "2")
    run_main(monkeypatch, str(source), str(corpus), str(real), "--expect-molecules", "2")
    assert len(json.loads(real.read_text(encoding="utf-8"))["copied"]) == 2 * N_LABELS and "8 copied" in capsys.readouterr().out
    (corpus / "A_1" / M.GEOMETRY).write_text("moved", encoding="utf-8")
    with pytest.raises(SystemExit, match="REFUSED, nothing copied"):
        run_main(monkeypatch, str(source), str(corpus), str(tmp_path / "refused.json"), "--expect-molecules", "2")
    assert json.loads((tmp_path / "refused.json").read_text(encoding="utf-8"))["refusals"]
    with pytest.raises(SystemExit, match="no such folder"):
        run_main(monkeypatch, str(tmp_path / "nowhere"), str(corpus), str(tmp_path / "x.json"), "--expect-molecules", "2")


def test_the_command_stops_with_the_record_when_a_copy_fails(folders, tmp_path, monkeypatch):
    source, corpus = folders

    def refuse_all(src, dst):
        raise PermissionError("held")

    monkeypatch.setattr(M, "copy_checked", refuse_all)
    with pytest.raises(SystemExit, match="STOPPED after 0 copies"):
        run_main(monkeypatch, str(source), str(corpus), str(tmp_path / "stopped.json"), "--expect-molecules", "2")
    assert "PermissionError" in json.loads((tmp_path / "stopped.json").read_text(encoding="utf-8"))["error"]
