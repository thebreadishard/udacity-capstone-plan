"""guard — Claude Code hooks for the rules that were broken by hand (TASKS 64; the user, 15 Oct 2026: 'Alle acht, gecommit, eerst een dag loggen').

Registered in .claude/settings.json at the repository root: `guard.py pre` before every Bash, PowerShell, Edit and Write call, `guard.py post`
after every Edit and Write. Reads the hook's JSON on stdin. Each rule is a function of the tool call that returns a reason or None, and
carries its decision and the incident it comes from:
  deny  the call is refused (exit 2; the reason goes back to Claude)
  ask   the user confirms in the app (permissionDecision 'ask')
  post  the call already ran; its problem goes back to Claude (exit 2)
A Bash or PowerShell command with a line of its own '# hook-exempt: <reason>' passes the deny rules; the exemption is logged.

Mode (tools/hooks/guard_config.json): 'log' records what would have happened and lets everything pass — the first day, to find false alarms;
'enforce' acts. Every hit is a JSON line in probes/watch_state/hooks.log (git-ignored) in both modes. A crash of the guard exits 1, which
Claude Code shows the user and does not block: a broken guard must never stop the work, and tests/test_hooks_guard.py keeps it from breaking.
Overridable for tests: GUARD_CONFIG, GUARD_LOG, GUARD_NOW (ISO time).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2]
CONFIG = Path(os.environ.get("GUARD_CONFIG", Path(__file__).with_name("guard_config.json")))
LOG = Path(os.environ.get("GUARD_LOG", PLAN / "probes" / "watch_state" / "hooks.log"))
SHELLS = ("Bash", "PowerShell")
EDITS = ("Edit", "Write")
EXEMPT = re.compile(r"^[ \t]*#[ \t]*hook-exempt:[ \t]*(\S.*)$", re.M)   # a line of its own, not a mention in a message


@dataclass(frozen=True)
class Call:
    tool: str
    input: dict

    @property
    def command(self) -> str:
        return self.input.get("command", "") if self.tool in SHELLS else ""

    @property
    def path(self) -> str:
        return self.input.get("file_path", "").replace("\\", "/") if self.tool in EDITS else ""

    @property
    def new_text(self) -> str:
        return self.input.get("content", "") if self.tool == "Write" else self.input.get("new_string", "")


@dataclass(frozen=True)
class Rule:
    name: str
    event: str            # pre | post
    tools: tuple[str, ...]
    decision: str         # deny | ask | post
    incident: str
    check: Callable[[Call], str | None]


# ---------------------------------------------------------------- 1. a heredoc that carries a backslash

_HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")


def heredoc_bodies(command: str) -> list[str]:
    """The bodies of the command's heredocs (up to the delimiter line, or the end when it is missing)."""
    bodies, lines = [], command.split("\n")
    for i, line in enumerate(lines):
        for m in _HEREDOC.finditer(line):
            end, strip = m.group(3), m.group(1) == "-"
            body = []
            for later in lines[i + 1:]:
                if (later.lstrip("\t") if strip else later) == end:
                    break
                body.append(later)
            bodies.append("\n".join(body))
    return bodies


def heredoc_backslash(c: Call) -> str | None:
    if any("\\" in body for body in heredoc_bodies(c.command)):
        return ("a heredoc that carries a backslash: escapes are mangled on the way (watch.sh and a run spec on 15 Oct, three patches on "
                "3-4 Oct). Write the script or file with the Write tool and run it.")
    return None


# ---------------------------------------------------------------- 2. git add -A / commit -a

_ADD_ALL = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?add\b[^;&|\n]*?\s(?:-A|--all|\.)(?=\s|$|[;&|])")
_COMMIT_ALL = re.compile(r"\bgit\s+(?:-C\s+\S+\s+)?commit\b[^;&|\n]*?\s(?:-[A-Za-z]*a[A-Za-z]*|--all)(?=\s|$)")


def git_add_all(c: Call) -> str | None:
    cmd = re.sub(r"(['\"]).*?\1", "''", c.command, flags=re.S)          # a commit message may say anything
    if _ADD_ALL.search(cmd) or _COMMIT_ALL.search(cmd):
        return "git add -A / . / commit -a: name the paths (run directories are written live; psi4 scratch is 75 MB). CLAUDE.md, Committing."
    return None


# ---------------------------------------------------------------- 3. a long job past tools/runspec.py

_DETACH = re.compile(r"\b(?:nohup|setsid|disown)\b")
_WRAPPER = re.compile(r"(?:^|[\s;&|(])(?:bash\s+|sh\s+)?\S*(?:remote_launch|launch_outside_app)\.sh\b", re.M)
_COMPUTE = re.compile(r"\b(?:python3?|psi4|wsl)\b")


def long_job_past_the_door(c: Call) -> str | None:
    cmd = c.command
    door = "launch it through `python tools/runspec.py launch probes/runspecs/<name>.json` (TASKS 63)"
    if _DETACH.search(cmd) or _WRAPPER.search(cmd):
        return f"a detached job or a direct launch wrapper: {door}. The #2702 repro ran 37 h without a progress line, started by hand."
    if c.input.get("run_in_background") and _COMPUTE.search(cmd) and "watch.sh" not in cmd and "pytest" not in cmd:
        return f"a computation in the background of this session: {door}."
    return None


# ---------------------------------------------------------------- 4. watch.sh while a watch runs

def _watch_running() -> bool:
    r = subprocess.run(["bash", "-c", "ps -ef | grep -c '[w]atch\\.sh'"], capture_output=True, text=True, timeout=10, check=False)
    return r.stdout.strip() not in ("", "0")


def watch_while_running(c: Call, running: Callable[[], bool] = _watch_running) -> str | None:
    touches = c.path.endswith("probes/watch.sh") or "patch_watch" in c.command or ("watch.sh" in c.command and "sed -i" in c.command)
    if touches and running():
        return "a running watch holds probes/watch.sh (Windows lock, 15 Oct): stop the watch by pid first, then patch, then re-arm."
    return None


# ---------------------------------------------------------------- 5. a post on GitHub

_GH_POST = re.compile(r"\bgh\s+(?:(?:pr|issue)\s+(?:comment|create|review|merge|close|edit|reopen)|(?:release|repo|gist)\s+(?:create|delete|edit))\b")
_GH_API_WRITE = re.compile(r"\bgh\s+api\b[^\n]*?(?:-X\s*|--method[\s=]+)(?:POST|PATCH|PUT|DELETE)\b|\bgh\s+api\b[^\n]*?\s(?:-f|-F|--field|--raw-field)\s")


def github_post(c: Call) -> str | None:
    if _GH_POST.search(c.command) or _GH_API_WRITE.search(c.command):
        return "a post or change on GitHub: only on the user's word (22 Sep 2026)."
    return None


# ---------------------------------------------------------------- 6. deleting or overwriting what cannot come back

_RM_RF = re.compile(r"\brm\s+-(?:[a-zA-Z]*r[a-zA-Z]*f|[a-zA-Z]*f[a-zA-Z]*r)[a-zA-Z]*\b")
_REMOTE = re.compile(r"\b(?:ssh|host_ssh|scp)\b")
_GIT_LOSS = re.compile(r"\bgit\s+(?:push\b[^;&|\n]*\s(?:--force(?:-with-lease)?|-f)(?=\s|$)|reset\s+--hard|clean\s+-[a-zA-Z]*f)")


def destructive(c: Call) -> str | None:
    cmd = c.command
    if (_RM_RF.search(cmd) and _REMOTE.search(cmd)) or re.search(r"\bhcloud\s+server\s+delete\b", cmd) or _GIT_LOSS.search(cmd):
        return "a deletion on a server or a history rewrite: only on the user's word."
    return None


# ---------------------------------------------------------------- 7. a stamp ahead of the clock

_STAMP = re.compile(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{2}):(\d)x\b")


def now() -> datetime:
    return datetime.fromisoformat(os.environ["GUARD_NOW"]) if "GUARD_NOW" in os.environ else datetime.now()


def stamp_ahead(c: Call) -> str | None:
    if not c.path.endswith(".md"):
        return None
    t = now()
    for m in _STAMP.finditer(c.new_text):
        day, mon, hour, tens = int(m.group(1)), m.group(2), int(m.group(3)), int(m.group(4))
        if (day, mon) == (t.day, t.strftime("%b")) and (hour, tens) > (t.hour, t.minute // 10):
            return f"the stamp '{m.group(0)}' is ahead of the clock ({t:%H:%M}): take it from `python tools/stamp.py` (20 and 22 Sep 2026)."
    return None


# ---------------------------------------------------------------- 8. after an edit: does it still parse and lint

def _first_lines(text: str, n: int = 6) -> str:
    return "\n".join(text.strip().splitlines()[:n])


def lint_after_edit(c: Call) -> str | None:
    p = Path(c.input.get("file_path", ""))
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", PLAN.parents[1]))
    if not p.is_file() or root.resolve() not in p.resolve().parents:
        return None                                     # scratch files are run at once; their errors show there
    run = lambda args: subprocess.run(args, capture_output=True, text=True, timeout=50, check=False, cwd=p.parent)  # noqa: E731
    if p.suffix == ".py":
        r = run([sys.executable, "-m", "ruff", "check", "--quiet", str(p)])
        if r.returncode not in (0, 2) and r.stdout.strip():   # 2: ruff not installed or no config — not the file's fault
            return f"ruff on {p.name}:\n{_first_lines(r.stdout)}"
        try:
            compile(p.read_bytes(), str(p), "exec")
        except SyntaxError as e:
            return f"{p.name} does not compile: line {e.lineno}: {e.msg}"
    elif p.suffix == ".sh":
        r = run([sys.executable, str(PLAN / "tools" / "check_shell.py"), str(p)])
        if r.returncode != 0:
            return f"{p.name}: {_first_lines(r.stdout + r.stderr)}"
    elif p.suffix == ".json" and p.parent.name == "runspecs":
        r = run([sys.executable, str(PLAN / "tools" / "runspec.py"), "validate", str(p)])
        if r.returncode != 0:
            return f"run spec {p.name}:\n{_first_lines(r.stdout)}"
    return None


RULES = (
    Rule("heredoc_backslash", "pre", ("Bash",), "deny", "3-4 Oct (3x), 15 Oct (2x): escapes mangled in heredocs", heredoc_backslash),
    Rule("git_add_all", "pre", SHELLS, "deny", "CLAUDE.md: live run directories, 75 MB psi4 scratch", git_add_all),
    Rule("long_job_past_the_door", "pre", SHELLS, "deny", "15 Oct: #2702 repro 37 h without a progress line", long_job_past_the_door),
    Rule("watch_while_running", "pre", SHELLS + EDITS, "deny", "15 Oct: WinError 5 on watch.sh", watch_while_running),
    Rule("github_post", "pre", SHELLS, "ask", "22 Sep: GitHub replies need the user's word", github_post),
    Rule("destructive", "pre", SHELLS, "ask", "standing rule: deletions need the user's word", destructive),
    Rule("stamp_ahead", "pre", EDITS, "deny", "20 and 22 Sep: stamps ahead of the clock", stamp_ahead),
    Rule("lint_after_edit", "post", EDITS, "post", "errors found only at the commit", lint_after_edit),
)


# ---------------------------------------------------------------- the hook

def evaluate(event: str, call: Call) -> list[tuple[Rule, str]]:
    return [(r, reason) for r in RULES if r.event == event and call.tool in r.tools and (reason := r.check(call))]


def mode() -> str:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8")).get("mode", "log")
    except (OSError, ValueError):
        return "log"


def log(entry: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def respond(event: str, call: Call, hits: list[tuple[Rule, str]], acting: bool) -> tuple[int, str, str]:
    """(exit code, stdout, stderr) for Claude Code. Deny outranks ask; an exempted command passes the deny rules."""
    exempt = EXEMPT.search(call.command)
    deny = [reason for r, reason in hits if r.decision in ("deny", "post") and not exempt]
    ask = [reason for r, reason in hits if r.decision == "ask"]
    if not acting:
        return 0, "", ""
    if deny:
        return 2, "", "\n".join(deny)
    if ask:
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "ask", "permissionDecisionReason": " ".join(ask)}}
        return 0, json.dumps(out), ""
    return 0, "", ""


def main(argv: list[str]) -> int:
    event = argv[1] if len(argv) > 1 else "pre"
    payload = json.loads(sys.stdin.read() or "{}")
    call = Call(payload.get("tool_name", ""), payload.get("tool_input") or {})
    hits = evaluate(event, call)
    if not hits:
        return 0
    acting = mode() == "enforce"
    exempt = EXEMPT.search(call.command)
    for rule, reason in hits:
        log({"time": now().isoformat(timespec="seconds"), "rule": rule.name, "decision": rule.decision, "acted": acting,
             "exempt": exempt.group(1)[:120] if exempt and rule.decision == "deny" else None, "tool": call.tool,
             "excerpt": (call.command or call.path)[:1000], "reason": reason[:300]})
    code, out, err = respond(event, call, hits, acting)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # noqa: BLE001 — a broken guard reports itself and never blocks (exit 1 is shown to the user, not a block)
        print(f"tools/hooks/guard.py failed: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
