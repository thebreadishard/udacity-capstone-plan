"""tools/make_module_repo.sh: a module folder becomes its own repository with its own history — main from master, the development branch
kept — and an existing target is refused."""
import json
import shutil
import subprocess
import sys
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
    _git(mono, "config", "user.name", "t")          # the script reads the repository's identity; a CI runner has no global one
    _git(mono, "config", "user.email", "t@t")
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


# ---- SUBMISSION.txt: deliverables only, and the notebook runs in a fresh clone (18 Oct 2026)

def _notebook_reading(path: str, require_env: str = "") -> str:
    guard = (f"import os\nif os.environ.get({require_env!r}) != '1':\n    raise RuntimeError('variable not set')\n"
             if require_env else "")
    cell = {"cell_type": "code", "source": [guard + f"print(open({path!r}).read())"], "execution_count": None, "outputs": [],
            "metadata": {}}
    return json.dumps({"cells": [cell], "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
                       "nbformat": 4, "nbformat_minor": 5})


def _module_with_manifest(tmp_path: Path, manifest: str, notebook_reads: str = "data.txt", readme: str = "# m\n",
                          require_env: str = "") -> Path:
    mono = tmp_path / "mono"
    mono.mkdir()
    _git(mono, "init", "-q", "-b", "master")
    _git(mono, "config", "user.name", "t")
    _git(mono, "config", "user.email", "t@t")
    _commit(mono, "plans/outside.txt", "only in the plan repository", "outside the module")
    _commit(mono, "plans/m02/build.py", "print('builder')", "builder")
    _commit(mono, "plans/m02/nb/data.txt", "data", "data")
    _commit(mono, "plans/m02/nb/work.ipynb", _notebook_reading(notebook_reads, require_env), "notebook")
    _commit(mono, "plans/m02/README.md", readme, "readme")
    _commit(mono, "plans/m02/SUBMISSION.txt", manifest, "manifest")
    _git(mono, "branch", "module-02")
    return mono


def _make(mono: Path, target: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([BASH, SCRIPT.as_posix(), "plans/m02", "module-02", target.as_posix(), *extra], cwd=mono, capture_output=True,
                          text=True, timeout=300, check=False)


MANIFEST = "# deliverables\nREADME.md\nSUBMISSION.txt\nnb/\nrun: nb/work.ipynb\n"
needs_jupyter = pytest.mark.skipif(shutil.which("jupyter") is None, reason="needs jupyter nbconvert")


@needs_jupyter
def test_only_listed_files_kept_and_notebook_runs_standalone(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST)
    target = tmp_path / "repo"
    r = _make(mono, target)
    assert r.returncode == 0, r.stdout + r.stderr
    assert sorted(_git(target, "ls-files").split()) == ["README.md", "SUBMISSION.txt", "nb/data.txt", "nb/work.ipynb"]   # the builder is gone
    assert "build.py" in _git(target, "ls-tree", "-r", "--name-only", "main~1").split()   # ... from main's tip only; the history keeps it
    assert "1 notebook(s) executed" in r.stdout


@needs_jupyter
def test_notebook_reading_outside_the_module_fails(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST, notebook_reads="../../outside.txt")   # exists in the plan repository, not in the clone
    r = _make(mono, tmp_path / "repo")
    assert r.returncode == 1 and "fails in a fresh clone" in r.stderr


def test_no_run_skips_execution_but_not_the_file_checks(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST + "missing.csv\n")
    r = _make(mono, tmp_path / "repo", "--no-run")
    assert r.returncode == 1 and "missing.csv" in r.stderr


@needs_jupyter
def test_run_line_assignments_reach_the_notebook(tmp_path):
    manifest = MANIFEST.replace("run: nb/work.ipynb", "run: nb/work.ipynb QUICK_CHECK=1")
    mono = _module_with_manifest(tmp_path, manifest, require_env="QUICK_CHECK")   # the notebook fails without the variable
    r = _make(mono, tmp_path / "repo")
    assert r.returncode == 0, r.stdout + r.stderr


def test_run_line_word_that_is_no_assignment_is_refused(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST.replace("run: nb/work.ipynb", "run: nb/work.ipynb --quick"))
    r = _make(mono, tmp_path / "repo", "--no-run")
    assert r.returncode == 1 and "not a VAR=value assignment" in r.stderr


def test_a_module_without_a_development_branch_gets_main_only(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST)
    target = tmp_path / "repo"
    r = subprocess.run([BASH, SCRIPT.as_posix(), "plans/m02", "-", target.as_posix(), "--no-run"], cwd=mono, capture_output=True, text=True,
                       timeout=300, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert _git(target, "branch", "--format=%(refname:short)").split() == ["main"]


@needs_jupyter
def test_notebooks_run_in_the_interpreter_given(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST)
    exe = Path(sys.executable).as_posix()
    if len(exe) > 1 and exe[1] == ":":                        # pass it the way a Git Bash user types it: /c/Users/... (the 18 Oct failure)
        exe = "/" + exe[0].lower() + exe[2:]
    r = _make(mono, tmp_path / "repo", "--python", exe)
    assert r.returncode == 0, r.stdout + r.stderr
    bad = subprocess.run([BASH, SCRIPT.as_posix(), "plans/m02", "-", (tmp_path / "repo2").as_posix(), "--python", "/no/such/python"],
                         cwd=mono, capture_output=True, text=True, timeout=120, check=False)
    assert bad.returncode == 2 and "not an executable" in bad.stderr


def test_readme_link_outside_the_repository_fails(tmp_path):
    mono = _module_with_manifest(tmp_path, MANIFEST, readme="# m\nsee [the parser](../build.py)\n")
    r = _make(mono, tmp_path / "repo", "--no-run")
    assert r.returncode == 1 and "README links outside" in r.stderr
