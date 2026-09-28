"""tools/check_shell.py (28 Sep 2026): fail-fast or a stated reason, and a parse check, for every shell script under plan 05."""
import subprocess
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import check_shell as CS  # noqa: E402


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8", newline="\n")
    return p


def test_set_e_variants_pass_and_missing_fails(tmp_path):
    assert CS.check(_write(tmp_path, "a.sh", "#!/bin/bash\nset -euo pipefail\necho ok\n"), None) == []
    assert CS.check(_write(tmp_path, "b.sh", "#!/bin/bash\nset -e\necho ok\n"), None) == []
    polling = "#!/bin/bash\n# no-set-e: polling loop, an empty pgrep is normal\nset -u\nwhile true; do sleep 1; done\n"
    assert CS.check(_write(tmp_path, "c.sh", polling), None) == []
    bad = CS.check(_write(tmp_path, "d.sh", "#!/bin/bash\nset -u\necho ok\n"), None)
    assert len(bad) == 1 and "no `set -e`" in bad[0]


def test_parse_error_is_reported_when_bash_exists(tmp_path):
    bash = CS.shutil.which("bash")
    if not bash:
        return
    bad = CS.check(_write(tmp_path, "e.sh", "#!/bin/bash\nset -e\nif [ 1 ]; then\n"), bash)
    assert any("bash -n failed" in b for b in bad)


def test_cli_exit_codes(tmp_path):
    good = _write(tmp_path, "g.sh", "#!/bin/bash\nset -e\n")
    bad = _write(tmp_path, "h.sh", "#!/bin/bash\necho\n")
    assert subprocess.run([sys.executable, str(PLAN / "tools" / "check_shell.py"), str(good)], capture_output=True, text=True, check=False).returncode == 0
    r = subprocess.run([sys.executable, str(PLAN / "tools" / "check_shell.py"), str(bad)], capture_output=True, text=True, check=False)
    assert r.returncode == 1 and "h.sh" in r.stdout


def test_repo_shell_scripts_conform():
    """Every committed .sh under the plan (outside run directories) passes — the hook's promise, checked here too."""
    scripts = [p for p in PLAN.rglob("*.sh") if "results_" not in str(p) and "node_modules" not in str(p)]
    problems = [x for p in scripts for x in CS.check(p, None)]
    assert not problems, problems
