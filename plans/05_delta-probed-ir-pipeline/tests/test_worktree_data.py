"""tools/worktree_data.py (TASKS 222) on a throwaway repository in tmp_path: never the real repository's data."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import worktree_data as WD

REPO = Path(__file__).resolve().parents[3]
DATA = "data/run1"
EXCLUDED = f"{WD.EXCLUDED_DIRS[0][0]}/out"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, check=True, text=True, env=WD.git_env()).stdout


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> WD.Checkouts:
    """A main checkout with ignored data, a cache and an excluded module folder, and a linked worktree without any of it."""
    main = tmp_path / "main"
    main.mkdir()
    _git(main, "init", "-q", "-b", "master")
    for key, value in (("user.email", "t@example.invalid"), ("user.name", "t"), ("commit.gpgsign", "false")):
        _git(main, "config", key, value)
    _write(main / ".gitignore", "data/\n__pycache__/\n**/out/\n")
    _write(main / "tracked.txt", "tracked\n")
    _git(main, "add", ".gitignore", "tracked.txt")
    _git(main, "commit", "-q", "-m", "init")
    _write(main / DATA / "a.json", "A")
    _write(main / DATA / "deep" / "b.npz", "B")
    _write(main / DATA / "__pycache__" / "c.pyc", "C")
    _write(main / EXCLUDED / "page.html", "written by tests")
    worktree = tmp_path / "wt"
    _git(main, "worktree", "add", "-q", "-b", "side", str(worktree))
    return WD.Checkouts(main=main.resolve(), worktree=worktree.resolve())


def _found(repo: WD.Checkouts) -> WD.Checkouts:
    return WD.find_checkouts(repo.worktree, WD.repository_of(repo.main))


def _folder_link(link: Path, target: Path) -> None:
    """A junction on Windows (what a user's mklink /J makes, and what os.walk enters), a symlink elsewhere."""
    if sys.platform == "win32":
        subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True, check=True)
    else:
        os.symlink(target, link, target_is_directory=True)


def test_find_checkouts_reads_the_main_checkout_from_git(repo):
    assert _found(repo) == repo


def test_link_counts_and_skip_rules(repo):
    report = WD.link(_found(repo), ("data",))
    assert (report.linked, report.already, report.skipped, report.refused, report.not_ignored) == (2, 0, 1, [], [])   # the cache is skipped
    assert (repo.worktree / DATA / "deep" / "b.npz").read_text(encoding="utf-8") == "B"
    assert not (repo.worktree / DATA / "__pycache__").exists()


def test_excluded_folder_is_skipped_inside_a_requested_parent(repo):
    report = WD.link(_found(repo), ("plans",))
    assert (report.linked, report.skipped) == (0, 1)
    assert not (repo.worktree / EXCLUDED).exists()


def test_link_is_idempotent(repo):
    checkouts = _found(repo)
    WD.link(checkouts, ("data",))
    again = WD.link(checkouts, ("data",))
    assert (again.linked, again.already, again.refused) == (0, 2, [])


def test_a_different_existing_file_is_refused_not_overwritten(repo):
    _write(repo.worktree / DATA / "a.json", "the worktree's own")
    report = WD.link(_found(repo), ("data",))
    assert report.refused == [f"{DATA}/a.json"]
    assert report.linked == 1
    assert not report.clean
    assert (repo.worktree / DATA / "a.json").read_text(encoding="utf-8") == "the worktree's own"
    assert (repo.main / DATA / "a.json").read_text(encoding="utf-8") == "A"


def test_a_file_the_branch_does_not_ignore_is_not_linked(repo):
    _write(repo.worktree / ".gitignore", "__pycache__/\n**/out/\n")             # the branch no longer ignores data/
    report = WD.link(_found(repo), ("data",))
    assert report.not_ignored == [f"{DATA}/a.json", f"{DATA}/deep/b.npz"]
    assert report.linked == 0
    assert not report.clean
    assert not (repo.worktree / DATA).exists()


def test_a_failure_partway_reports_what_was_linked(repo, monkeypatch):
    real_link, calls = os.link, []

    def fail_second(src, dst):
        calls.append(dst)
        if len(calls) == 2:
            raise OSError("too many links")
        real_link(src, dst)

    monkeypatch.setattr(WD.os, "link", fail_second)
    with pytest.raises(WD.LinkStopped, match="too many links") as stopped:
        WD.link(_found(repo), ("data",))
    assert stopped.value.report.linked == 1


def test_the_main_checkout_is_refused(repo):
    with pytest.raises(WD.WorktreeDataError, match="main checkout itself"):
        WD.find_checkouts(repo.main, WD.repository_of(repo.main))


def test_a_subfolder_of_the_worktree_is_refused(repo):
    (repo.worktree / "sub").mkdir()
    with pytest.raises(WD.WorktreeDataError, match="not its top level"):
        WD.find_checkouts(repo.worktree / "sub", WD.repository_of(repo.main))


def test_a_worktree_of_another_repository_is_refused(repo, tmp_path):
    other = tmp_path / "other"
    other.mkdir()
    _git(other, "init", "-q")
    with pytest.raises(WD.WorktreeDataError, match="belongs to the repository"):
        WD.find_checkouts(repo.worktree, WD.repository_of(other))


def test_the_cli_refuses_a_worktree_outside_its_own_repository(repo, capsys):
    assert WD.main(["status", str(repo.worktree)]) == 2
    assert "belongs to the repository" in capsys.readouterr().err


@pytest.mark.parametrize("bad", ["/abs/data", "../data", ".", "C:/data", f"{WD.EXCLUDED_DIRS[0][0]}/out"])
def test_bad_folders_are_refused_up_front(bad):
    with pytest.raises(WD.WorktreeDataError):
        WD.validate_dirs([bad])


def test_folders_are_normalised():
    assert WD.validate_dirs(["website\\export\\out", "data/"]) == ("website/export/out", "data")


def test_default_folders_are_distinct_reasoned_and_where_the_repository_has_them():
    """Each default is already normal, has a reason, neither nests in another nor touches an excluded folder, and its parent is a folder
    of this repository (the layout only; no data is read), so a renamed module shows here instead of as a silent zero-file link."""
    names = [d for d, _ in WD.DEFAULT_DIRS]
    assert WD.validate_dirs(names) == tuple(names)
    assert all(reason.strip() for _, reason in WD.DEFAULT_DIRS)
    for a in names:
        assert not any(a != b and PurePosixPath(a).is_relative_to(b) for b in names), a
        assert not any(PurePosixPath(excluded).is_relative_to(a) for excluded, _ in WD.EXCLUDED_DIRS), a
        assert (REPO / a).parent.is_dir(), a


def test_status_counts_only_links_to_the_main_checkout(repo):
    checkouts = _found(repo)
    WD.link(checkouts, ("data",))
    _write(repo.worktree / "data" / "own.txt", "not a link")
    assert WD.status(checkouts) == {"(other folders)": 2}


def test_unlink_removes_only_links_and_keeps_the_originals(repo):
    checkouts = _found(repo)
    WD.link(checkouts, ("data",))
    _write(repo.worktree / "data" / "own.txt", "not a link")
    assert WD.unlink(checkouts) == 2
    assert (repo.worktree / "data" / "own.txt").read_text(encoding="utf-8") == "not a link"
    assert (repo.worktree / "tracked.txt").exists()
    assert not (repo.worktree / DATA).exists()                                 # folders left empty are pruned
    assert (repo.main / DATA / "a.json").read_text(encoding="utf-8") == "A"   # one name removed, the data stays
    assert (repo.main / DATA / "deep" / "b.npz").read_text(encoding="utf-8") == "B"
    assert os.stat(repo.main / DATA / "a.json").st_nlink == 1
    assert WD.status(checkouts) == {}


def test_a_same_named_file_that_is_not_the_link_survives_unlink(repo):
    checkouts = _found(repo)
    _write(repo.worktree / DATA / "a.json", "A")                               # same name and content, a different file
    assert WD.unlink(checkouts) == 0
    assert (repo.worktree / DATA / "a.json").exists()


def test_a_folder_junction_into_the_main_checkout_is_never_entered(repo):
    """A worktree folder that is a junction to the main's folder: unlink must not delete the main's names, link must not create there."""
    checkouts = _found(repo)
    _folder_link(repo.worktree / "data", repo.main / "data")
    try:
        assert WD.status(checkouts) == {}
        assert WD.unlink(checkouts) == 0
        assert (repo.main / DATA / "a.json").read_text(encoding="utf-8") == "A"
        assert (repo.main / DATA / "deep").is_dir()
        with pytest.raises(WD.LinkStopped, match="resolves outside the worktree"):
            WD.link(checkouts, ("data",))
        assert sorted(p.name for p in (repo.main / DATA).iterdir()) == ["__pycache__", "a.json", "deep"]
    finally:
        if sys.platform == "win32":
            os.rmdir(repo.worktree / "data")                                   # removes the junction, not the main's folder
        else:
            os.unlink(repo.worktree / "data")


def test_writing_into_a_link_writes_the_main_checkouts_original(repo):
    """The hazard the tool's summary warns about: an in-place write goes through; a replace only breaks the link."""
    checkouts = _found(repo)
    WD.link(checkouts, ("data",))
    with open(repo.worktree / DATA / "a.json", "w", encoding="utf-8") as f:
        f.write("changed in the worktree")
    assert (repo.main / DATA / "a.json").read_text(encoding="utf-8") == "changed in the worktree"
    tmp = repo.worktree / DATA / "deep" / "b.npz.tmp"
    tmp.write_text("replaced", encoding="utf-8")
    os.replace(tmp, repo.worktree / DATA / "deep" / "b.npz")
    assert (repo.main / DATA / "deep" / "b.npz").read_text(encoding="utf-8") == "B"


def test_worktree_remove_with_links_present_keeps_the_main_checkouts_data(repo):
    """git counts ignored files as clean, so `git worktree remove` needs no --force and no unlink first; it removes names, not data."""
    WD.link(_found(repo), ("data",))
    _git(repo.main, "worktree", "remove", str(repo.worktree))
    assert not repo.worktree.exists()
    assert (repo.main / DATA / "a.json").read_text(encoding="utf-8") == "A"
