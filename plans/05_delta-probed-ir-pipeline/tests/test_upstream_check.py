"""tools/upstream_check.py (TASKS 101): lint runs the project's own workflow commands on the changed files only, a C change with a bare
OpenMP region is reported, and backport lists exactly the merged pull request's commits by others."""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import upstream_check as uc

WORKFLOW = """jobs:
  ruff:
    steps:
    - name: Check style
      run: ruff check --config .ruff.toml pkg
  flake:
    steps:
    - name: Static analysis
      run: flake8 --config .flake8 pkg
    - name: unrelated
      run: pip install flake8
"""


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)


@pytest.fixture
def checkout(tmp_path):
    """A project with a lint workflow, one commit as the base, then a changed .py inside the target, one outside, and a C file."""
    repo = tmp_path / "proj"
    (repo / ".github" / "workflows").mkdir(parents=True)
    (repo / ".github" / "workflows" / "lint.yml").write_text(WORKFLOW, encoding="utf-8")
    (repo / "pkg").mkdir()
    (repo / "pkg" / "a.py").write_text("x = 1\n", encoding="utf-8")
    (repo / ".flake8").write_text("[flake8]\nexclude = test, .git\n", encoding="utf-8")
    _git(repo, "init", "-q")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "base")
    (repo / "pkg" / "a.py").write_text("import os\nx = 1\n", encoding="utf-8")
    (repo / "outside.py").write_text("import sys\n", encoding="utf-8")
    (repo / "pkg" / "test").mkdir()
    (repo / "pkg" / "test" / "t.py").write_text("import json\n", encoding="utf-8")   # excluded by .flake8
    (repo / "pkg" / "k.c").write_text("#pragma omp parallel shared(n)\n{ }\n#pragma omp parallel default(none) shared(n)\n{ }\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "-m", "change")
    (repo / "pkg" / "uncommitted.py").write_text("import re\n", encoding="utf-8")       # not part of the change
    return repo


def test_lint_commands_are_the_workflows_own(checkout):
    assert uc.lint_commands(checkout) == [["ruff", "check", "--config", ".ruff.toml", "pkg"], ["flake8", "--config", ".flake8", "pkg"]]


def test_lint_runs_each_command_on_the_changed_files_under_its_target(checkout, monkeypatch, capsys):
    monkeypatch.setattr(uc, "LINT_PYTHON", Path(sys.executable))
    calls = []

    def fake_run(argv, **_kw):
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 1 if "flake8" in argv else 0, stdout="pkg/a.py:1:1: F401 'os' imported but unused")

    assert uc.lint(checkout, "HEAD~1", run=fake_run) == 1
    assert len(calls) == 2 and all("pkg/a.py" in c and "outside.py" not in c for c in calls)
    assert "pkg/test/t.py" in calls[0] and "pkg/test/t.py" not in calls[1]      # ruff decides with --force-exclude; flake8 is filtered here
    assert "--force-exclude" in calls[0] and "--force-exclude" not in calls[1]
    out = capsys.readouterr().out
    assert "F401" in out and "1 OpenMP parallel region(s) without default(none)" in out


def test_a_project_without_a_lint_workflow_is_refused(tmp_path):
    with pytest.raises(SystemExit, match="lint commands"):
        uc.lint_commands(tmp_path)


def test_backport_lists_the_commits_of_others(capsys):
    pages = {
        "repos/o/r/pulls/7": {"merged_at": "2026-10-06T20:05:34Z"},
        "repos/o/r/pulls/7/commits": [{"sha": "aaaaaaaaaa", "author": {"login": "me"}, "commit": {"message": "ours"}},
                                      {"sha": "bbbbbbbbbb", "author": {"login": "maintainer"}, "commit": {"message": "Declare i, j, k\n\nbody"}}],
        "repos/o/r/commits/bbbbbbbbbb": {"files": [{"filename": "k.c", "patch": "-int a;\n+int a, i;"}]},
    }
    assert uc.backport("o/r", 7, "me", api=pages.__getitem__) == 1
    out = capsys.readouterr().out
    assert "1 commit(s) by others than me" in out and "bbbbbbbbb maintainer: Declare i, j, k" in out and "+int a, i;" in out


def test_backport_refuses_an_unmerged_pull_request():
    with pytest.raises(SystemExit, match="not merged"):
        uc.backport("o/r", 8, "me", api={"repos/o/r/pulls/8": {"merged_at": None}}.__getitem__)
