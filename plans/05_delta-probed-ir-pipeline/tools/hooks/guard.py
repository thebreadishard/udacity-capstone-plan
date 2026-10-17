"""guard — Claude Code hooks for the rules that were broken by hand (TASKS 64; the user, 15 Oct 2026: 'Alle acht, gecommit, eerst een dag loggen';
17 Oct 2026, after the log review: 'Akkoord' — command words only, inline_code for heredoc_backslash, enforce, clean code logged).

Registered in .claude/settings.json at the repository root: `guard.py pre` before every Bash, PowerShell, Edit and Write call, `guard.py post`
after every Edit and Write. Reads the hook's JSON on stdin. Each rule is a function of the tool call that returns a reason or None, and
carries its decision and the incident it comes from:
  deny  the call is refused (exit 2; the reason goes back to Claude)
  ask   the user confirms in the app (permissionDecision 'ask')
  post  the call already ran; its problem goes back to Claude (exit 2)
A rule marked log_only is recorded and never acts, whatever the mode (a new rule's first days).
A shell command with a comment line of its own '# hook-exempt: <reason>' (outside any string) passes the deny rules; the exemption is logged.

Shell commands are read as command words (`commands`): quoted text, commit messages and file names are arguments, never commands — the log of
15–17 Oct had five false alarms from words inside strings or paths. Scripts handed to `bash -c`, `ssh` or `host_ssh` are read the same way.

Mode (tools/hooks/guard_config.json): 'log' records what would have happened and lets everything pass; 'enforce' acts. Every hit is a JSON line
in probes/watch_state/hooks.log (git-ignored) in both modes. A crash of the guard exits 1, which Claude Code shows the user and does not block:
a broken guard must never stop the work, and tests/test_hooks_guard.py keeps it from breaking.
Overridable for tests: GUARD_CONFIG, GUARD_LOG, GUARD_NOW (ISO time).
"""
from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

PLAN = Path(__file__).resolve().parents[2]
CONFIG = Path(os.environ.get("GUARD_CONFIG", Path(__file__).with_name("guard_config.json")))
LOG = Path(os.environ.get("GUARD_LOG", PLAN / "probes" / "watch_state" / "hooks.log"))
SHELLS = ("Bash", "PowerShell")
EDITS = ("Edit", "Write")
EXEMPT = re.compile(r"^[ \t]*#[ \t]*hook-exempt:[ \t]*([^<\s].*)$", re.M)   # a comment line of its own; '<reason>' is the placeholder
CLEAN_CODE_RUFF = ["--isolated", "--select", "E,F,W,B,SIM,UP,C90,PLR,RUF", "--ignore", "E741,RUF001,RUF002,RUF003,PLR2004,PLR0917",
                   "--line-length", "160", "--config", "lint.pylint.max-args = 6"]                 # CLAUDE.md, 'Python code'


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
    log_only: bool = False


# ---------------------------------------------------------------- reading a shell command

_HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
_QUOTED = re.compile(r"'[^']*'|\"(?:\\.|[^\"\\])*\"", re.S)
_SEPARATORS = {";", "&&", "||", "|", "&", "(", ")", "|&", ";;"}
_PREFIXES = {"env", "time", "exec", "command", "nice", "sudo"}
_ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")


def _heredoc_operators(line: str, quote: str | None) -> tuple[list[re.Match], str | None]:
    """The heredoc operators of one line that stand outside strings and comments, and the quote still open at its end."""
    found, j = [], 0
    while j < len(line):
        ch = line[j]
        if quote:
            if ch == quote:
                quote = None
            elif ch == "\\" and quote == '"':
                j += 1
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (j == 0 or line[j - 1].isspace()):
            break
        elif line.startswith("<<", j) and not line.startswith("<<<", j) and (m := _HEREDOC.match(line, j)):
            found.append(m)
            j = m.end()
            continue
        j += 1
    return found, quote


def split_heredocs(command: str) -> tuple[str, list[str]]:
    """The command without its heredoc bodies, and the bodies (up to the delimiter line, or the end when it is missing). An operator
    inside a string ('… <<EOF …' in a commit message) or a comment is not one."""
    lines, code, bodies, i, quote = command.split("\n"), [], [], 0, None
    while i < len(lines):
        code.append(lines[i])
        operators, quote = _heredoc_operators(lines[i], quote)
        for m in operators:
            end, strip, body = m.group(3), m.group(1) == "-", []
            i += 1
            while i < len(lines) and (lines[i].lstrip("\t") if strip else lines[i]) != end:
                body.append(lines[i])
                i += 1
            bodies.append("\n".join(body))
        i += 1
    return "\n".join(code), bodies


def blank_quotes(text: str) -> str:
    """Quoted text replaced by '' — what is left is the shell's own words and comments."""
    return _QUOTED.sub("''", text)


def _tokens(code: str) -> list[str]:
    lexer = shlex.shlex(code.replace("\n", " ;\n"), posix=True, punctuation_chars=True)    # a newline ends a command and a comment
    lexer.whitespace_split = True
    try:
        return list(lexer)
    except ValueError:                                  # an unbalanced quote: fall back to plain words
        return code.split()


def _nested_scripts(words: list[str]) -> Iterator[str]:
    """Scripts a command hands on: `bash -c S` (also inside `wsl -e bash -c S`), and the remote command of ssh / host_ssh."""
    for k, w in enumerate(words[:-1]):
        if Path(w).name in ("bash", "sh") and words[k + 1] == "-c" and k + 2 < len(words):
            yield words[k + 2]
    if words and words[0] in ("ssh", "host_ssh"):
        yield from (w for w in words[1:] if " " in w or ";" in w)


def commands(command: str, depth: int = 0) -> list[list[str]]:
    """The simple commands of a shell command as word lists, command word first (assignments and prefixes like env/time dropped);
    heredoc bodies and comments are not commands; scripts handed to bash -c / ssh / host_ssh are read too (two levels)."""
    code, _ = split_heredocs(command)
    out, words = [], []
    for tok in [*_tokens(code), ";"]:
        if tok not in _SEPARATORS and not set(tok) <= set(";&|()"):
            words.append(tok)
            continue
        while words and (_ASSIGNMENT.match(words[0]) or words[0] in _PREFIXES):
            words = words[1:]
        if words:
            out.append(words)
            if depth < 2:
                for script in _nested_scripts(words):
                    out.extend(commands(script, depth + 1))
        words = []
    return out


def _name(word: str) -> str:
    return Path(word.replace("\\", "/")).name.lower()


# ---------------------------------------------------------------- 1. code inside a shell command

_INTERPRETERS = ("python", "python3", "python.exe", "py", "node", "perl", "ruby", "rscript")


def inline_code(c: Call) -> str | None:
    if split_heredocs(c.command)[1]:
        return ("a heredoc: file content or code inside a shell command loses its backslashes in every quoting form (tested 15 Oct; watch.sh "
                "and a run spec on 15 Oct, three patches on 3-4 Oct). Write the file with the Write tool and run it.")
    for words in commands(c.command):
        if _name(words[0]) in _INTERPRETERS and any(w in ("-c", "-e", "-") for w in words[1:3]):
            return (f"inline code ('{words[0]} {words[1]}'): code inside a shell command loses its backslashes (15 Oct). Write the script with "
                    "the Write tool (the scratchpad for a one-off) and run the file.")
    return None


# ---------------------------------------------------------------- 2. git add -A / commit -a

def git_add_all(c: Call) -> str | None:
    for words in commands(c.command):
        args = words[3:] if words[:2] == ["git", "-C"] else words[1:]
        if words[0] != "git" or not args:
            continue
        if (args[0] == "add" and any(a in ("-A", "--all", ".") for a in args[1:])) or (
                args[0] == "commit" and any(a == "--all" or re.fullmatch(r"-[A-Za-z]*a[A-Za-z]*", a) for a in args[1:])):
            return "git add -A / . / commit -a: name the paths (run directories are written live; psi4 scratch is 75 MB). CLAUDE.md, Committing."
    return None


# ---------------------------------------------------------------- 3. a long job past tools/runspec.py

_WRAPPERS = ("remote_launch.sh", "launch_outside_app.sh")
_COMPUTE = ("python", "python3", "python.exe", "psi4", "wsl", "wsl.exe")


def long_job_past_the_door(c: Call) -> str | None:
    door = "launch it through `python tools/runspec.py launch probes/runspecs/<name>.json` (TASKS 63)"
    cmds = commands(c.command)
    for words in cmds:
        run = words[1:] if words[0] in ("bash", "sh") and len(words) > 1 else words
        if words[0] in ("nohup", "setsid", "disown") or _name(run[0]) in _WRAPPERS:
            return f"a detached job or a direct launch wrapper: {door}. The #2702 repro ran 37 h without a progress line, started by hand."
    background_compute = any(_name(w[0]) in _COMPUTE for w in cmds)
    harmless = any("watch.sh" in " ".join(w) or "pytest" in w for w in cmds)
    if c.input.get("run_in_background") and background_compute and not harmless:
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

_GH_WRITES = {"pr": {"comment", "create", "review", "merge", "close", "edit", "reopen"}, "issue": {"comment", "create", "close", "edit", "reopen"},
              "release": {"create", "delete", "edit"}, "repo": {"create", "delete", "edit"}, "gist": {"create", "delete", "edit"}}


def github_post(c: Call) -> str | None:
    for words in commands(c.command):
        if _name(words[0]) not in ("gh", "gh.exe") or len(words) < 3:
            continue
        api_write = words[1] == "api" and any(
            w in ("-f", "-F", "--field", "--raw-field") or (w in ("-X", "--method") and k + 1 < len(words) and words[k + 1].upper() != "GET")
            or re.fullmatch(r"(?:-X|--method=)(?:POST|PATCH|PUT|DELETE)", w) for k, w in enumerate(words))
        if words[2] in _GH_WRITES.get(words[1], ()) or api_write:
            return "a post or change on GitHub: only on the user's word (22 Sep 2026)."
    return None


# ---------------------------------------------------------------- 6. deleting or overwriting what cannot come back

def _rm_recursive_force(words: list[str]) -> bool:
    flags = "".join(w[1:] for w in words[1:] if w.startswith("-") and not w.startswith("--"))
    return words[0] == "rm" and "r" in flags.lower() and "f" in flags


def destructive(c: Call) -> str | None:
    reason = "a deletion on a server or a history rewrite: only on the user's word."
    for words in commands(c.command):
        if words[0] in ("ssh", "host_ssh") and any(_rm_recursive_force(w) for s in _nested_scripts(words) for w in commands(s)):
            return reason
        if words[0] in ("ssh", "host_ssh") and "rm" in words and _rm_recursive_force(words[words.index("rm"):]):
            return reason
        if words[:3] == ["hcloud", "server", "delete"]:
            return reason
        if words[0] == "git" and len(words) > 1 and (
                (words[1] == "push" and any(w in ("--force", "--force-with-lease", "-f") for w in words[2:]))
                or (words[1] == "reset" and "--hard" in words) or (words[1] == "clean" and any(re.fullmatch(r"-[a-zA-Z]*f[a-zA-Z]*", w) for w in words))):
            return reason
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


def _in_repository(p: Path) -> bool:
    root = Path(os.environ.get("CLAUDE_PROJECT_DIR", PLAN.parents[1]))
    return p.is_file() and root.resolve() in p.resolve().parents        # scratch files are run at once; their errors show there


def _run(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, timeout=50, check=False, cwd=cwd)


def lint_after_edit(c: Call) -> str | None:
    p = Path(c.input.get("file_path", ""))
    if not _in_repository(p):
        return None
    if p.suffix == ".py":
        r = _run([sys.executable, "-m", "ruff", "check", "--quiet", str(p)], p.parent)
        if r.returncode not in (0, 2) and r.stdout.strip():   # 2: ruff not installed or no config — not the file's fault
            return f"ruff on {p.name}:\n{_first_lines(r.stdout)}"
        try:
            compile(p.read_bytes(), str(p), "exec")
        except SyntaxError as e:
            return f"{p.name} does not compile: line {e.lineno}: {e.msg}"
    elif p.suffix == ".sh":
        r = _run([sys.executable, str(PLAN / "tools" / "check_shell.py"), str(p)], p.parent)
        if r.returncode != 0:
            return f"{p.name}: {_first_lines(r.stdout + r.stderr)}"
    elif p.suffix == ".json" and p.parent.name == "runspecs":
        r = _run([sys.executable, str(PLAN / "tools" / "runspec.py"), "validate", str(p)], p.parent)
        if r.returncode != 0:
            return f"run spec {p.name}:\n{_first_lines(r.stdout)}"
    return None


# ---------------------------------------------------------------- 9. after an edit: the clean-code set on the lines just written

def edited_lines(c: Call, text: str) -> range:
    """The file's lines the call wrote: all of them for Write, the new_string's span for Edit (its first occurrence)."""
    n_lines = text.count("\n") + 1
    if c.tool == "Write" or not c.new_text or c.new_text not in text:
        return range(1, n_lines + 1)
    start = text[: text.index(c.new_text)].count("\n") + 1
    return range(start, start + c.new_text.count("\n") + 1)


def clean_code_after_edit(c: Call) -> str | None:
    p = Path(c.input.get("file_path", ""))
    if p.suffix != ".py" or not _in_repository(p):
        return None
    r = _run([sys.executable, "-m", "ruff", "check", *CLEAN_CODE_RUFF, "--output-format", "concise", str(p)], p.parent)
    span = edited_lines(c, p.read_text(encoding="utf-8", errors="replace"))
    found = [line for line in r.stdout.splitlines() if (m := re.match(r".*?:(\d+):\d+: ", line)) and int(m.group(1)) in span]
    return f"clean-code check on the lines just written in {p.name}:\n" + "\n".join(found[:6]) if found else None


RULES = (
    Rule("inline_code", "pre", SHELLS, "deny", "3-4 Oct (3x), 15 Oct (2x): backslashes lost from code inside shell commands", inline_code),
    Rule("git_add_all", "pre", SHELLS, "deny", "CLAUDE.md: live run directories, 75 MB psi4 scratch", git_add_all),
    Rule("long_job_past_the_door", "pre", SHELLS, "deny", "15 Oct: #2702 repro 37 h without a progress line", long_job_past_the_door),
    Rule("watch_while_running", "pre", SHELLS + EDITS, "deny", "15 Oct: WinError 5 on watch.sh", watch_while_running),
    Rule("github_post", "pre", SHELLS, "ask", "22 Sep: GitHub replies need the user's word", github_post),
    Rule("destructive", "pre", SHELLS, "ask", "standing rule: deletions need the user's word", destructive),
    Rule("stamp_ahead", "pre", EDITS, "deny", "20 and 22 Sep: stamps ahead of the clock", stamp_ahead),
    Rule("lint_after_edit", "post", EDITS, "post", "errors found only at the commit", lint_after_edit),
    Rule("clean_code_after_edit", "post", EDITS, "post", "16 Oct: the user's clean-code rule (CLAUDE.md 'Python code')", clean_code_after_edit,
         log_only=True),
)


# ---------------------------------------------------------------- the hook

def evaluate(event: str, call: Call) -> list[tuple[Rule, str]]:
    return [(r, reason) for r in RULES if r.event == event and call.tool in r.tools and (reason := r.check(call))]


def mode() -> str:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8")).get("mode", "log")
    except (OSError, ValueError):
        return "log"


def exemption(command: str) -> str | None:
    """The reason of a '# hook-exempt:' comment line outside strings and heredocs, or None."""
    m = EXEMPT.search(blank_quotes(split_heredocs(command)[0]))
    return m.group(1).strip() if m else None


def log(entry: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def respond(call: Call, hits: list[tuple[Rule, str]], acting: bool) -> tuple[int, str, str]:
    """(exit code, stdout, stderr) for Claude Code. Deny outranks ask; an exempted command passes the deny rules; log_only rules never act."""
    exempt = exemption(call.command)
    live = [(r, reason) for r, reason in hits if not r.log_only]
    deny = [reason for r, reason in live if r.decision in ("deny", "post") and not (exempt and r.decision == "deny")]
    ask = [reason for r, reason in live if r.decision == "ask"]
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
    exempt = exemption(call.command)
    for rule, reason in hits:
        log({"time": now().isoformat(timespec="seconds"), "rule": rule.name, "decision": rule.decision, "acted": acting and not rule.log_only,
             "exempt": exempt[:120] if exempt and rule.decision == "deny" else None, "tool": call.tool,
             "excerpt": (call.command or call.path)[:1000], "reason": reason[:300]})
    code, out, err = respond(call, hits, acting)
    if out:
        print(out)
    if err:
        print(err, file=sys.stderr)
    return code


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as e:  # noqa: BLE001, RUF100 — a broken guard reports itself and never blocks; BLE001 is pyproject's, unknown to the clean set
        print(f"tools/hooks/guard.py failed: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
