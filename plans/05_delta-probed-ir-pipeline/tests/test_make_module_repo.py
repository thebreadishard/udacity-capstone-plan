"""tools/make_module_repo.sh: a module folder becomes its own repository with its own history — main from master, the development branch
kept — and an existing target is refused."""
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "tools" / "make_module_repo.sh"
BASH = shutil.which("bash")
pytestmark = pytest.mark.skipif(BASH is None or shutil.which("git") is None, reason="needs bash and git")


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def _commit(repo: Path, path: str, text: str, msg: str) -> None:
    f = repo / path
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")
    _git(repo, "add", path)
    _git(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", msg)


def test_module_history_and_branches_carried_over(tmp_path):
    mono = tmp_path / "mono"
    mono.mkdir()
    _git(mono, "init", "-q", "-b", "master")
    _commit(mono, "other/x.txt", "x", "unrelated")
    _commit(mono, "plans/m02/a.txt", "a", "module first")
    _git(mono, "checkout", "-q", "-b", "module-02")
    _commit(mono, "plans/m02/b.txt", "b", "module on its branch")
    _git(mono, "checkout", "-q", "master")
    _git(mono, "-c", "user.name=t", "-c", "user.email=t@t", "merge", "-q", "--no-ff", "-m", "merge", "module-02")
    _commit(mono, "plans/m02/a.txt", "a2", "module after the merge")
    target = tmp_path / "out" / "ai-programming-foundations-project"
    r = subprocess.run([BASH, SCRIPT.as_posix(), "plans/m02", "module-02", target.as_posix()], cwd=mono, capture_output=True, text=True,
                       timeout=120, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert set(_git(target, "branch", "--format=%(refname:short)").split()) == {"main", "module-02"}
    assert sorted(_git(target, "ls-files").split()) == ["a.txt", "b.txt"]          # the module folder is the root; 'other' is gone
    assert int(_git(target, "rev-list", "--count", "main")) >= 3
    assert "unrelated" not in _git(target, "log", "--format=%s", "main")
    assert not [b for b in _git(mono, "branch", "--format=%(refname:short)").split() if b.startswith("split-")]   # temporary branches removed
    again = subprocess.run([BASH, SCRIPT.as_posix(), "plans/m02", "module-02", target.as_posix()], cwd=mono, capture_output=True, text=True,
                           timeout=120, check=False)
    assert again.returncode == 2 and "exists" in again.stderr
