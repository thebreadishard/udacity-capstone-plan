"""tools/hooks/guard.py (TASKS 64, 15 Oct 2026): each of the eight rules refuses what its incident was and lets the everyday neighbour pass;
the hook answers Claude Code in the documented shapes (exit 2 + stderr to deny, permissionDecision 'ask' as JSON, exit 1 when it breaks);
'log' mode lets everything pass and records it."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools" / "hooks"))
import guard as G  # noqa: E402

GUARD = PLAN / "tools" / "hooks" / "guard.py"


def bash(command: str, **extra) -> G.Call:
    return G.Call("Bash", {"command": command, **extra})


def names(call: G.Call, event: str = "pre") -> set[str]:
    return {r.name for r, _ in G.evaluate(event, call)}


# ---------------------------------------------------------------- the rules: incident refused, neighbour allowed

@pytest.mark.parametrize("command, hit", [
    ("python - <<'EOF'\nprint('a\\nb')\nEOF", True),                      # the 15 Oct watch.sh patch
    ("cat > spec.json <<EOF\n{\"r\": \"^=== \\\\(SM\\\\) \"}\nEOF", True),  # the 15 Oct smoke spec
    ("cat <<-END\n\tx \\ y\n\tEND\necho done", True),
    ("python - <<'EOF'\nprint('plain')\nEOF\necho 'a\\b'", False),         # a backslash outside the heredoc
    ("echo $((1 << 3))", False),
])
def test_heredoc_backslash(command, hit):
    assert ("heredoc_backslash" in names(bash(command))) is hit


@pytest.mark.parametrize("command, hit", [
    ("git add -A", True), ("git add --all && git commit -m x", True), ("cd x; git add . ; git commit -m y", True),
    ("git commit -am 'msg'", True), ("git -C repo add -A", True),
    ("git add plans/a.py plans/b.py && git commit -q -m 'add -A is banned; see .'", False),
    ("git add .gitignore", False), ("git commit --amend --no-edit", False), ("git status -s .", False),
])
def test_git_add_all(command, hit):
    assert ("git_add_all" in names(bash(command))) is hit


@pytest.mark.parametrize("call, hit", [
    (bash("wsl -e bash -c 'nohup python repro_2702.py --large > l.log 2>&1 &'"), True),       # the #2702 repro
    (bash("bash tools/remote_launch.sh root@1.2.3.4 /root/x n -- 'bash run.sh'"), True),
    (bash("tools/launch_outside_app.sh n . 'python x.py'"), True),
    (bash("python probes/s2_read.py", run_in_background=True), True),
    (bash("python tools/runspec.py launch probes/runspecs/s3.json"), False),
    (bash("bash probes/watch.sh; echo rc=$?", run_in_background=True), False),
    (bash("until grep -q done x.log; do sleep 120; done; cut -c1-80 x.log", run_in_background=True), False),
    (bash("python -m pytest -q tests", run_in_background=True), False),
    (bash("python probes/s2_read.py"), False),                                                 # foreground: bounded by the tool's timeout
])
def test_long_job_past_the_door(call, hit):
    assert ("long_job_past_the_door" in names(call)) is hit


def test_watch_while_running_only_when_a_watch_runs():
    edit = G.Call("Edit", {"file_path": "C:\\Users\\x\\plans\\05\\probes\\watch.sh", "old_string": "a", "new_string": "b"})
    patch = bash("python /c/tmp/scratchpad/patch_watch_cr.py")
    other = G.Call("Edit", {"file_path": "C:/x/probes/watch_jobs.tsv", "old_string": "a", "new_string": "b"})
    assert G.watch_while_running(edit, lambda: True) and G.watch_while_running(patch, lambda: True)
    assert G.watch_while_running(edit, lambda: False) is None and G.watch_while_running(other, lambda: True) is None
    assert G.watch_while_running(bash("bash probes/watch.sh; echo rc=$?"), lambda: True) is None   # re-arming is not editing


@pytest.mark.parametrize("command, hit", [
    ("gh issue comment 2702 -R pyscf/pyscf --body-file reply.md", True), ("gh pr create --fill", True),
    ("gh api repos/o/r/issues/1/comments -f body=hi", True), ("gh api -X DELETE repos/o/r/git/refs/heads/x", True),
    ("gh release create v1", True),
    ("gh run list -R o/r --limit 1", False), ("gh api repos/pyscf/pyscf/issues/2702/comments --jq '.[].body'", False),
    ("gh pr view 3469 --json state", False),
])
def test_github_post_asks(command, hit):
    assert ("github_post" in names(bash(command))) is hit


@pytest.mark.parametrize("command, hit", [
    (". tools/hosts.sh; host_ssh s1 'rm -rf /root/runspec_smoke'", True), ("ssh root@1.2.3.4 'rm -fr /root/labels'", True),
    ("hcloud server delete hel1-6", True), ("git push --force origin master", True), ("git push -f", True),
    ("git reset --hard HEAD~1", True), ("git clean -fdx", True),
    ("rm -rf /c/Users/x/scratchpad/runspec_smoke/state", False),                  # local scratch
    ("git push -q && git log --oneline -1", False), ("git reset HEAD file", False),
])
def test_destructive_asks(command, hit):
    assert ("destructive" in names(bash(command))) is hit


def test_stamp_ahead_of_the_clock(monkeypatch):
    monkeypatch.setenv("GUARD_NOW", "2026-10-15T18:42:00")
    write = lambda text, path="C:/x/TASKS.md": G.Call("Write", {"file_path": path, "content": text})  # noqa: E731
    edit = G.Call("Edit", {"file_path": "C:/x/TASKS.md", "old_string": "a", "new_string": "**15 Oct 19:0x:** done"})
    assert G.stamp_ahead(edit) and G.stamp_ahead(write("(15 Oct 18:5x; the user)"))
    assert G.stamp_ahead(write("(15 Oct 18:4x)")) is None                         # the current ten minutes
    assert G.stamp_ahead(write("(14 Oct 23:5x) and deadline 16 Oct 09:00")) is None   # another day; not a stamp
    assert G.stamp_ahead(write("15 Oct 19:0x", path="C:/x/probe.py")) is None       # only documents


@pytest.mark.parametrize("name, text, problem", [
    ("good.py", "import os\n\nprint(os.sep)\n", None),
    ("unused.py", "import os\n", "F401"),
    ("broken.py", "def f(:\n", "broken.py"),
    ("ok.sh", "#!/bin/bash\nset -euo pipefail\necho hi\n", None),
    ("nofail.sh", "#!/bin/bash\necho hi\n", "nofail.sh"),
])
def test_lint_after_edit(tmp_path, monkeypatch, name, text, problem):
    if name.endswith(".py"):
        pytest.importorskip("ruff")
    if name.endswith(".sh") and shutil.which("bash") is None:
        pytest.skip("bash not available")
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    f = tmp_path / name
    f.write_text(text, encoding="utf-8", newline="\n")
    reason = G.lint_after_edit(G.Call("Write", {"file_path": str(f), "content": text}))
    assert (reason is None) if problem is None else (problem in reason)


def test_lint_skips_files_outside_the_repository(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path / "repo"))
    f = tmp_path / "scratch.py"
    f.write_text("def f(:\n", encoding="utf-8")
    assert G.lint_after_edit(G.Call("Write", {"file_path": str(f), "content": ""})) is None


def test_every_rule_names_its_incident_and_a_known_decision():
    assert len(G.RULES) == 8 and len({r.name for r in G.RULES}) == 8
    assert all(r.incident and r.decision in ("deny", "ask", "post") and r.event in ("pre", "post") for r in G.RULES)


# ---------------------------------------------------------------- the hook end to end

def hook(tmp_path: Path, payload, mode: str, event: str = "pre") -> subprocess.CompletedProcess:
    cfg = tmp_path / "cfg.json"
    cfg.write_text(json.dumps({"mode": mode}), encoding="utf-8")
    env = dict(os.environ, GUARD_CONFIG=str(cfg), GUARD_LOG=str(tmp_path / "hooks.log"))
    data = payload if isinstance(payload, str) else json.dumps(payload)
    return subprocess.run([sys.executable, str(GUARD), event], input=data, env=env, capture_output=True, text=True, timeout=60, check=False)


def logged(tmp_path: Path) -> list[dict]:
    p = tmp_path / "hooks.log"
    return [json.loads(line) for line in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


def test_log_mode_passes_everything_and_records_it(tmp_path):
    r = hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "git add -A"}}, "log")
    assert r.returncode == 0 and r.stdout == "" and r.stderr == ""
    (entry,) = logged(tmp_path)
    assert entry["rule"] == "git_add_all" and entry["acted"] is False and entry["excerpt"] == "git add -A"


def test_enforce_denies_with_the_reason_on_stderr(tmp_path):
    r = hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "git add -A"}}, "enforce")
    assert r.returncode == 2 and "name the paths" in r.stderr


def test_enforce_asks_in_the_documented_shape(tmp_path):
    r = hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "gh pr create --fill"}}, "enforce")
    out = json.loads(r.stdout)["hookSpecificOutput"]
    assert r.returncode == 0 and out["hookEventName"] == "PreToolUse" and out["permissionDecision"] == "ask"


def test_an_exemption_passes_a_deny_rule_and_is_logged(tmp_path):
    cmd = "# hook-exempt: a one-off listener the user asked for\nnohup bash x.sh &"
    r = hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": cmd}}, "enforce")
    assert r.returncode == 0 and logged(tmp_path)[0]["exempt"].startswith("a one-off listener")


def test_a_mention_of_the_exemption_is_not_one(tmp_path):
    """15 Oct 2026: a commit message describing '# hook-exempt: <reason>' was logged as an exemption."""
    cmd = "git add -A && git commit -m \"'# hook-exempt: <reason>' passes a deny rule\""
    r = hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": cmd}}, "enforce")
    assert r.returncode == 2 and logged(tmp_path)[0]["exempt"] is None


def test_a_quiet_call_is_not_logged_and_a_broken_payload_never_blocks(tmp_path):
    assert hook(tmp_path, {"tool_name": "Bash", "tool_input": {"command": "ls"}}, "enforce").returncode == 0 and logged(tmp_path) == []
    r = hook(tmp_path, "{not json", "enforce")
    assert r.returncode == 1 and "guard.py failed" in r.stderr
