"""tools/deploy_closure.py: a deploy list that lacks a file one of its files needs is refused (imports at any depth, relative imports, a
package's submodule, shell references and `-m` modules), comments and third-party imports need nothing, and the plan's real deploy lists
(deploy_s2.sh, deploy_s1tz.sh via --list-files) are closed — the check that would have caught deploy_s2.sh without scf_converge.py
(19 Oct 2026)."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import deploy_closure as D  # noqa: E402

BASH = shutil.which("bash")


def write(root: Path, rel: str, text: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


@pytest.fixture
def plan(tmp_path):
    write(tmp_path, "probes/runner.sh", '# probes/never.py is only named in a comment\nPY=python\n"$PY" "$HERE/main.py" x  # probes/never.py\n'
                                       "python -m pkg.tool --flag\n")
    write(tmp_path, "probes/main.py", "import json\nimport numpy as np\nfrom helper import f\n\n\ndef late():\n    import lazy\n")
    write(tmp_path, "probes/helper.py", "def f():\n    return 1\n")
    write(tmp_path, "probes/lazy.py", "")
    write(tmp_path, "probes/never.py", "")
    write(tmp_path, "src/pkg/__init__.py", "")
    write(tmp_path, "src/pkg/tool.py", "from .util import g\nfrom pkg import extra\n")
    write(tmp_path, "src/pkg/util.py", "def g():\n    return 2\n")
    write(tmp_path, "src/pkg/extra.py", "")
    return tmp_path


FULL = ["probes/runner.sh", "probes/main.py", "probes/helper.py", "probes/lazy.py", "src/pkg/__init__.py", "src/pkg/tool.py", "src/pkg/util.py",
        "src/pkg/extra.py"]


def test_a_closed_list_passes_and_comments_and_third_party_need_nothing(plan):
    assert D.missing(FULL, plan) == []


@pytest.mark.parametrize(("dropped", "needed_by"), [
    ("probes/main.py", "probes/runner.sh"),        # $HERE/ reference in a shell script
    ("src/pkg/tool.py", "probes/runner.sh"),       # python -m pkg.tool
    ("probes/helper.py", "probes/main.py"),        # a sibling import
    ("probes/lazy.py", "probes/main.py"),          # an import inside a function
    ("src/pkg/util.py", "src/pkg/tool.py"),        # a relative import
    ("src/pkg/extra.py", "src/pkg/tool.py"),       # from pkg import extra: a submodule
])
def test_every_kind_of_need_is_found(plan, dropped, needed_by):
    assert (dropped, needed_by) in D.missing([f for f in FULL if f != dropped], plan)


def test_a_listed_path_that_is_no_file_is_refused(plan):
    with pytest.raises(SystemExit, match="not a file"):
        D.missing([*FULL, "probes/nowhere.py"], plan)


@pytest.mark.skipif(BASH is None, reason="needs bash")
@pytest.mark.parametrize("script", ["deploy_s2.sh", "deploy_s1tz.sh"])
def test_the_plans_deploy_lists_are_closed(script):
    out = subprocess.run([BASH, (PLAN / "probes" / script).as_posix(), "--list-files"], capture_output=True, text=True, encoding="utf-8",
                         timeout=60, check=True).stdout
    files = [line.strip() for line in out.splitlines() if line.strip()]
    assert "probes/scf_converge.py" in files and D.missing(files, PLAN) == []
