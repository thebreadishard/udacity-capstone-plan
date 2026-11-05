"""tools/build_env_beside.py: the plan's refusals, the pin changes, and the build steps against a recorded fake shell (nothing runs in WSL)."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import build_env_beside as B  # noqa: E402

SOURCE_FREEZE = "numpy==2.5.2\npyscf==2.14.0\npyscf_forge==1.1.1\nscipy==1.18.1\n"
INTERPRETER = "/home/u/.local/share/uv/python/cpython-3.12.14-linux-x86_64-gnu/bin/python3.12"


class FakeShell:
    """Answers the source reads and the target's freeze; records every script and refuses to create a target that 'exists'."""

    def __init__(self, target_freeze: str | None = None, target_exists: bool = False) -> None:
        self.scripts: list[str] = []
        self.stdin: list[str | None] = []
        self.target_freeze = target_freeze
        self.target_exists = target_exists

    def __call__(self, script: str, stdin: str | None = None, timeout: int = 300) -> str:
        self.scripts.append(script)
        self.stdin.append(stdin)
        if script.startswith("readlink -f"):
            return INTERPRETER + "\n"
        if script.startswith("test ! -e") and self.target_exists:
            raise B.BuildError("the target exists")
        if script.endswith("-m pip freeze"):
            return SOURCE_FREEZE if '"$HOME/qc05"' in script else (self.target_freeze or "")
        return ""


def plan(**kw) -> B.BuildPlan:
    base = dict(source="qc05", target="qc215", set_pins=(("pyscf", "2.15.0"),), drop=("pyscf-forge",), imports=("pyscf",))
    return B.BuildPlan(**{**base, **kw})


EXPECTED = ["numpy==2.5.2", "pyscf==2.15.0", "scipy==1.18.1"]


def test_canonical_names_match_pip():
    assert B.canonical("pyscf_forge") == B.canonical("PySCF-Forge") == B.canonical("pyscf.forge") == "pyscf-forge"


def test_set_and_drop_change_only_the_named_packages():
    assert B.planned_pins(B.pins_of(SOURCE_FREEZE), plan()) == EXPECTED
    assert B.changes(B.pins_of(SOURCE_FREEZE), EXPECTED) == ["pyscf 2.14.0 -> 2.15.0", "pyscf_forge 1.1.1 dropped"]


@pytest.mark.parametrize("kw", [dict(set_pins=(("pyscff", "2.15.0"),)), dict(drop=("pyscf-forj",))])
def test_a_change_to_an_absent_package_is_refused(kw):
    with pytest.raises(B.BuildError, match="no such package"):
        B.planned_pins(B.pins_of(SOURCE_FREEZE), plan(**kw))


@pytest.mark.parametrize("kw, reason", [
    (dict(target="qc05"), "same environment"),
    (dict(target="~/qc215"), "directory name"),
    (dict(target="qc 215"), "directory name"),
    (dict(drop=("pyscf",)), "set and dropped"),
    (dict(imports=("pyscf; rm",)), "not a module name"),
    (dict(dry_run=True, verify_only=True), "one or the other"),
])
def test_the_plan_refuses_unsafe_or_contradictory_settings(kw, reason):
    with pytest.raises(B.BuildError, match=reason):
        plan(**kw)


def test_local_installs_in_the_source_are_refused():
    with pytest.raises(B.BuildError, match="local or editable"):
        B.pins_of("numpy==2.5.2\n-e git+https://x/pyscf.git@t3#egg=pyscf\n")


def test_a_pin_must_be_exact():
    with pytest.raises(B.BuildError, match="exact pin"):
        B.parse_pin("pyscf>=2.15")
    assert B.parse_pin("pyscf==2.15.0") == ("pyscf", "2.15.0")


def test_dry_run_reads_the_source_and_creates_nothing():
    sh = FakeShell()
    report = B.build(plan(dry_run=True), sh)
    assert report[-1] == "dry run: qc215 not created"
    assert all(s.startswith(("readlink", '"$HOME/qc05"')) for s in sh.scripts)


def test_build_uses_the_source_interpreter_installs_the_plan_and_checks_it():
    sh = FakeShell(target_freeze="\n".join(EXPECTED) + "\n")
    report = B.build(plan(), sh)
    assert f"'{INTERPRETER}' -m venv \"$HOME/qc215\"" in sh.scripts
    assert sh.stdin[sh.scripts.index('cat > "$HOME/qc215"/build-requirements.txt')] == "\n".join(EXPECTED) + "\n"
    install = next(s for s in sh.scripts if "pip install" in s)
    assert "--no-deps" in install
    assert any(s.endswith("-m pip check") for s in sh.scripts)
    assert sh.scripts[-1].endswith(" pyscf")
    assert report[-1].startswith("built ~/qc215")


def test_an_existing_target_is_never_built_over():
    sh = FakeShell(target_exists=True)
    with pytest.raises(B.BuildError, match="exists"):
        B.build(plan(), sh)
    assert not any("-m venv" in s for s in sh.scripts)


def test_a_target_whose_pins_differ_from_the_plan_fails():
    sh = FakeShell(target_freeze="numpy==2.5.2\npyscf==2.14.0\nscipy==1.18.1\n")
    with pytest.raises(B.BuildError, match=r"missing \['pyscf==2.15.0'\], extra \['pyscf==2.14.0'\]"):
        B.build(plan(), sh)


def test_no_imports_means_no_import_step():
    sh = FakeShell(target_freeze="\n".join(EXPECTED) + "\n")
    B.build(plan(imports=()), sh)
    assert not any("importlib" in s for s in sh.scripts)


def test_verify_checks_an_existing_target_and_creates_nothing():
    sh = FakeShell(target_freeze="\n".join(EXPECTED) + "\n", target_exists=True)
    report = B.build(plan(verify_only=True), sh)
    assert report[-1].startswith("verified ~/qc215")
    assert not any(s.startswith("test ! -e") or "-m venv" in s or "pip install" in s for s in sh.scripts)
    assert any(s.endswith("-m pip check") for s in sh.scripts)


def test_the_command_line_builds_the_same_plan():
    argv = ["--source", "qc05", "--target", "qc215", "--set", "pyscf==2.15.0", "--drop", "pyscf-forge", "--import", "pyscf", "--dry-run"]
    assert B.plan_from_args(argv) == plan(dry_run=True)
    assert B.plan_from_args([*argv[:-1], "--verify"]) == plan(verify_only=True)


def test_main_reports_a_refusal_with_exit_1(capsys):
    assert B.main(["--source", "qc05", "--target", "qc05"]) == 1
    assert "same environment" in capsys.readouterr().err
