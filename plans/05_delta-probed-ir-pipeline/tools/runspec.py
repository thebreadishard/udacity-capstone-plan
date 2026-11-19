"""runspec — one door for long runs, each with a progress contract (15 Oct 2026, TASKS 63).

Why: the #2702 repro ran 37 h in a library fallback without one line in its log. The run rule said "a run longer than an hour prints a
progress line at least hourly"; the threshold needed an estimate, the estimate was wrong, and the job had been started by hand, past every
wrapper. Here a run cannot start without saying which log lines prove progress and how long they may stay away, whatever its expected length.

A run is a spec, probes/runspecs/<name>.json (committed: the launch record), and a state, probes/watch_state/runs/<name>.json (git-ignored).
  launch    refuses an invalid spec, a run already running, an unknown or re-used host, a source that does not compile or whose server copy
            differs (sha256), a laptop run without a measured peak memory, past the laptop's memory budget or whose log git tracks, and a
            failed dry run; then
            starts the command through the existing wrappers — tools/remote_launch.sh on a server, tools/launch_outside_app.sh on the laptop.
            Both leave <name>.log, <name>.pid and, when the command ends, <name>.exit in the workdir. Python's output is unbuffered
            (PYTHONUNBUFFERED=1), so a line printed is a line in the log.
  check     what probes/watch.sh runs every ten minutes. Per running run: marker lines, the exit file, the pid, the count of progress lines.
            One line per event on stdout — 'ANOMALY <text>' (a decision is needed), 'MARKER <text>' (news), a final 'QUIET <summary>'. The
            texts are stable while the situation lasts, so the watch's seen file reports each one once.
  resume    what tools/resume_laptop_jobs.sh runs every 30 minutes (the scheduled task CapstoneResumeJobs): a laptop run whose spec is
            `resumable` (its command skips finished work), neither ended nor alive in two looks 30 s apart, is relaunched with its log
            appended. The watch gives a resumable run RESUME_GRACE before it reports it gone, so a restart does not wake the session.
            With a fail_regex a run that left a non-zero exit file but neither its end nor its failure line counts as interrupted (a
            restart killed it after its wrapper wrote the exit file, TASKS 83) and is resumed the same way.
  stop      ends a running run's process tree and holds it (TASKS 251; on 16 Nov v14_stage1 was paused with taskkill by hand, which left it
            'running': counted against the memory budget and due for the resume task). Laptop: taskkill /T /F from the Windows process of
            the pid file's bash (the whole Windows tree, wsl.exe included), then every WSL process that carries the run's RUNSPEC_RUN tag,
            which the launch exports into WSL through WSLENV — a process group at a time where the group's leader carries it, TERM and
            then KILL. Server: the run's process group (remote_launch.sh starts it with setsid), TERM and then KILL. Only when nothing of
            the run is left does it append its stop line to the log and write 143 to the exit file. The state becomes 'stopped': resume
            leaves it, the check reports it once as 'MARKER run <name> stopped by hand' (a deliberate stop, never an ANOMALY), and only a
            fresh launch arms it again. A run that ended by itself is not stopped: its exit code stays the record. A stop that does not
            finish leaves the run 'stopping': held from resume, refused by launch, an ANOMALY in the check after STOP_STALE, and stop
            again tries again.

    python tools/runspec.py validate probes/runspecs/<name>.json
    python tools/runspec.py launch probes/runspecs/<name>.json
    python tools/runspec.py check [--peek]      (--peek: the same lines, the state not saved; for a look by hand — the watch owns the state)
    python tools/runspec.py resume [--dry-run]
    python tools/runspec.py stop probes/runspecs/<name>.json [--reason TEXT]
    python tools/runspec.py list

Regexes are POSIX ERE, matched by grep -E where the log lives; Python's \\d, \\s, \\w, \\b and (?...) are refused because grep -E does not
read them the same way. Overridable for tests: RUNSPEC_ROOT (the plan folder), RUNSPEC_DIR, RUNSPEC_STATE, HOSTS_FILE, HOSTS_SSH.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from pathlib import Path, PurePosixPath

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

ROOT = Path(os.environ.get("RUNSPEC_ROOT", Path(__file__).resolve().parents[1]))
SPEC_DIR = Path(os.environ.get("RUNSPEC_DIR", ROOT / "probes" / "runspecs"))
STATE_DIR = Path(os.environ.get("RUNSPEC_STATE", ROOT / "probes" / "watch_state" / "runs"))
TOOLS = Path(__file__).resolve().parent
LAPTOP = "laptop"
ESTIMATE_OVERRUN = 1.5          # elapsed / estimate at which the run is reported once: an overrun is the moment to read the log
MARKER_WIDTH = 110              # the width of the watch's other markers
DRY_RUN_TIMEOUT_S = 900
RESUME_GRACE = timedelta(minutes=40)   # longer than the resume task's 30 minutes: a resumable run gone for less is the resume's business
RESUME_SECOND_LOOK_S = 30              # a run is gone only when two looks this far apart both miss it (13 Oct: one ps snapshot missed a runner)
INTERRUPTED_MIN_LIFE_S = 120           # a run that died sooner is a start-up failure to read, not a restart to resume (TASKS 83)
# The laptop's memory for runs, GB. 19 Oct 2026 07:24: 11.0 of 31.3 GB free with one trainer at 3.2 GB, so Windows, the app and an idle WSL
# hold ≈ 16 GB; 2 GB stay free as margin. At 00:46 that night chain 41, two dxtb shards and a UKS cation together ran Windows out of memory.
LAPTOP_RUN_MEMORY_GB = 13.0
FREE_COMMIT_MARGIN_GB = 4.0     # a second laptop run must leave this much committable beside its peak (20-21 Oct: 3.5-3.7 GB was not enough)
RUN_ENV = "export PYTHONUNBUFFERED=1; "  # a print to a file is block-buffered otherwise: 18-19 Oct, an optimisation's lines sat in the buffer for hours
STOP_EXIT = 143                 # 128 + SIGTERM in the exit file of a stopped run; the state, not the code, says the stop was deliberate
STOP_WAIT_S = 15                # how long a run's processes may take to go after TERM before they get KILL
STOP_STALE = timedelta(minutes=15)   # a stop takes a minute or two; one still 'stopping' after this did not finish
RUN_TAG = "RUNSPEC_RUN"         # set to the run's name in every process of a laptop run, WSL ones included: how the stop finds them
_NOT_ERE = re.compile(r"\\[dDsSwWbB]|\(\?")


# ---------------------------------------------------------------- the spec

def _ere(value: str | None) -> str | None:
    if value is None:
        return None
    if _NOT_ERE.search(value):
        raise ValueError(f"{value!r} is not POSIX ERE: write [0-9], [[:space:]], [A-Za-z0-9_] instead of \\d, \\s, \\w; no \\b or (?...)")
    re.compile(value)
    return value


class _Frozen(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Source(_Frozen):
    """A script the command runs: compiled before the launch; on a server, its copy there must have the same sha256."""
    local: str = Field(min_length=1, description="path relative to the plan folder")
    remote: str | None = Field(default=None, description="absolute path of the copy on the server")


class Progress(_Frozen):
    regex: str = Field(description="ERE of a progress line in the run's log")
    max_gap_minutes: int = Field(ge=10, le=120, description="an alarm when no new progress line appeared for this long")
    start_regex: str | None = Field(default=None, description="ERE of the line from which the gap counts (a run that first waits for another)")
    heartbeat_glob: str | None = Field(default=None, pattern=r"^[A-Za-z0-9_./*?-]+$",
                                       description="a library log (glob, relative to the workdir or absolute) whose growth also resets the gap: a run "
                                                   "whose own pyscf.log grows is not stuck, however far apart its progress lines are (19 Oct 2026)")

    _check_regex = field_validator("regex", "start_regex")(_ere)


class Estimate(_Frozen):
    hours: float = Field(gt=0)
    basis: str = Field(min_length=10, description="the measurement the hours come from; an estimate without one is not written down")


class Memory(_Frozen):
    peak_gb: float = Field(gt=0, le=64, description="the run's peak memory (all its processes, WSL included), GB")
    basis: str = Field(min_length=10, description="the measurement the peak comes from")
    budget_word: str | None = Field(default=None, min_length=20, description="the user's word, quoted with its date, that lets this run "
                                    f"pass the {LAPTOP_RUN_MEMORY_GB:g} GB laptop budget; such a run starts only with no other laptop run "
                                    "in progress, and every other laptop run waits for it")

    @model_validator(mode="after")
    def _word_only_past_the_budget(self) -> Memory:
        if self.budget_word is not None and self.peak_gb <= LAPTOP_RUN_MEMORY_GB:
            raise ValueError(f"budget_word is for a peak past {LAPTOP_RUN_MEMORY_GB:g} GB; {self.peak_gb:g} GB fits without one")
        return self


class RunSpec(_Frozen):
    name: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]{0,39}$")
    purpose: str = Field(min_length=10, description="the TASKS row or registration the run serves")
    host: str = Field(min_length=1, description=f"'{LAPTOP}' or a name in tools/hosts.tsv")
    workdir: str = Field(min_length=1, description="laptop: relative to the plan folder; server: absolute")
    command: str = Field(min_length=1)
    sources: tuple[Source, ...] = Field(min_length=1)
    progress: Progress
    marker_regex: str | None = Field(default=None, description="ERE of lines reported once each")
    end_regex: str | None = Field(default=None, description="ERE of the line a successful run ends with")
    fail_regex: str | None = Field(default=None, description="ERE of the line a run that failed on its own ends with. With it, a resumable "
                                   "laptop run whose exit is non-zero but whose log has neither this line nor its end line was killed from "
                                   "outside (a Windows restart, TASKS 83) and is resumed, not reported ended")
    dry_run_args: str | None = Field(default=None, description="appended to the command for the dry run before the launch")
    threads: int | None = Field(default=None, ge=1, le=64)
    estimate: Estimate | None = None
    memory: Memory | None = Field(default=None, description="laptop runs: required at launch and resume (the memory budget)")
    resumable: bool = Field(default=False, description="laptop only: the command skips finished work, so `resume` may relaunch it")

    _check_regex = field_validator("marker_regex", "end_regex", "fail_regex")(_ere)

    @model_validator(mode="after")
    def _paths_fit_the_host(self) -> RunSpec:
        on_laptop = self.host == LAPTOP
        if on_laptop and (PurePosixPath(self.workdir).is_absolute() or ".." in PurePosixPath(self.workdir).parts):
            raise ValueError("a laptop workdir is relative to the plan folder and stays inside it")
        if not on_laptop and not self.workdir.startswith("/"):
            raise ValueError("a server workdir is absolute")
        if on_laptop and any(s.remote for s in self.sources):
            raise ValueError("a laptop run has no remote copies of its sources")
        if self.resumable and not on_laptop:
            raise ValueError("resumable is for laptop runs (a server is not restarted under a run)")
        if self.fail_regex and not (self.resumable and self.end_regex):
            raise ValueError("fail_regex tells a killed run from a failed one for the resume task: it needs a resumable run with an end_regex")
        return self


def load_spec(path: Path) -> RunSpec:
    return RunSpec.model_validate_json(path.read_text(encoding="utf-8"))


def laptop_log(spec: RunSpec) -> Path:
    """The log a laptop run writes, <workdir>/<name>.log."""
    return ROOT / spec.workdir / f"{spec.name}.log"


# ---------------------------------------------------------------- the state and what a check sees

@dataclass(frozen=True)
class RunState:
    started_at: datetime
    status: str = "running"                 # running | stopping (the stop at work) | stopped | ended
    phase_started_at: datetime | None = None  # when the progress gap began to count (the launch, or start_regex's first line)
    progress_count: int = 0
    progress_seen_at: datetime | None = None  # the last check at which the count (or the heartbeat's size) changed
    heartbeat_bytes: int = 0                  # the heartbeat files' total size at the last check
    unreachable: int = 0
    gone_seen_at: datetime | None = None      # a resumable run first seen gone (cleared when it is alive again)
    relaunches: int = 0
    stopped_at: datetime | None = None
    stop_reported: bool = False               # the check has reported the stop once

    def to_json(self) -> str:
        """The stop's two fields are written only once a stop set them: the file of a run nobody stopped keeps the keys the reader
        from before the stop command knows, so that reader still loads it after a rollback (`cls(**raw)` refuses an unknown key)."""
        raw = {k: v for k, v in asdict(self).items() if not (k in _STOP_FIELDS and v == _STOP_FIELDS[k])}
        return json.dumps({k: v.isoformat() if isinstance(v, datetime) else v for k, v in raw.items()}, indent=1)

    @classmethod
    def from_json(cls, text: str) -> RunState:
        raw = json.loads(text)
        return cls(**{k: datetime.fromisoformat(v) if k.endswith("_at") and v else v for k, v in raw.items()})


_STOP_FIELDS = {"stopped_at": None, "stop_reported": False}   # with their defaults, which to_json leaves out


@dataclass(frozen=True)
class Observation:
    reachable: bool = True
    wrong_machine: bool = False
    host_gone: bool = False
    workdir_missing: bool = False
    exit_code: int | None = None
    alive: bool = False
    progress_count: int = 0
    heartbeat_bytes: int = 0
    started: bool = False
    ended_marker: bool = False
    failed_marker: bool = False
    lived_s: int | None = None                # exit file's mtime minus pid file's: how long the run lived (with fail_regex only)
    markers: tuple[str, ...] = ()


def _unreachable(spec: RunSpec, state: RunState, obs: Observation) -> tuple[list[str], RunState] | None:
    """The check's outcome when the host or the run's folder cannot be read, None when they can."""
    who = f"run {spec.name}"
    if obs.host_gone:
        return [f"ANOMALY {who}: host {spec.host} is no longer in tools/hosts.tsv and the run never ended"], state
    if obs.wrong_machine:
        return [f"ANOMALY {who}: host {spec.host} answers with another machine (re-used IP?) - see tools/hosts.tsv"], state
    if not obs.reachable:
        state = replace(state, unreachable=state.unreachable + 1)
        return ([f"ANOMALY {who}: host {spec.host} unreachable twice"] if state.unreachable >= 2 else []), state
    if obs.workdir_missing:
        return [f"ANOMALY {who}: workdir {spec.workdir} missing on {spec.host}"], replace(state, unreachable=0)
    return None


def interrupted(spec: RunSpec, obs: Observation) -> bool:
    """A resumable laptop run killed from outside (22 Oct: a Windows restart let the wrapper write a non-zero exit file after the python
    died): exit non-zero, neither its end line nor its failure line, and alive long enough not to be a start-up failure."""
    return (spec.fail_regex is not None and obs.exit_code not in (None, 0) and not obs.ended_marker and not obs.failed_marker
            and obs.lived_s is not None and obs.lived_s >= INTERRUPTED_MIN_LIFE_S)


def _ended(spec: RunSpec, state: RunState, obs: Observation, events: list[str]) -> tuple[list[str], RunState]:
    """A run with an exit file: ended, cleanly or not. The launch time is in the text: the watch reports a text once, and a relaunch
    that ends the same way must be reported again (l5_apt_field, 31 Oct: the second exit 1 went unreported)."""
    who = f"run {spec.name}"
    launched = f" (launched {state.started_at:%d %b %H:%M})"
    state = replace(state, status="ended")
    if obs.exit_code != 0:
        return [*events, f"ANOMALY {who} ended with exit {obs.exit_code}{launched}"], state
    if spec.end_regex and not obs.ended_marker:
        return [*events, f"ANOMALY {who} exited 0 without its end line /{spec.end_regex}/{launched}"], state
    return [*events, f"MARKER {who} ended (exit 0){launched}"], state


def _vanished(spec: RunSpec, state: RunState, events: list[str], now: datetime) -> tuple[list[str], RunState]:
    """A run neither ended nor alive: the resume task's business for RESUME_GRACE when it is resumable, an anomaly otherwise."""
    who = f"run {spec.name}"
    if not spec.resumable:
        return [*events, f"ANOMALY {who} gone without an exit file (launched {state.started_at:%d %b %H:%M})"], state
    gone = state.gone_seen_at or now
    state = replace(state, gone_seen_at=gone)
    if now - gone < RESUME_GRACE:
        return events, state
    return [*events, f"ANOMALY {who} gone since {gone:%d %b %H:%M} and not resumed (see probes/watch_state/resume.log)"], state


def _progress(spec: RunSpec, state: RunState, obs: Observation, events: list[str], now: datetime) -> tuple[list[str], RunState]:
    """A live run: its progress lines against the allowed gap, and its time against the estimate."""
    who = f"run {spec.name}"
    if state.phase_started_at is None:                       # still waiting for start_regex
        if not obs.started:
            return events, state
        state = replace(state, phase_started_at=now, progress_count=obs.progress_count, heartbeat_bytes=obs.heartbeat_bytes, progress_seen_at=now)
    if obs.progress_count != state.progress_count or obs.heartbeat_bytes != state.heartbeat_bytes:
        state = replace(state, progress_count=obs.progress_count, heartbeat_bytes=obs.heartbeat_bytes, progress_seen_at=now)
    seen = state.progress_seen_at or state.phase_started_at
    if now - seen > timedelta(minutes=spec.progress.max_gap_minutes):
        what = "no progress line and no heartbeat growth" if spec.progress.heartbeat_glob else "no progress line"
        events = [*events, f"ANOMALY {who}: {what} since {seen:%d %b %H:%M} (the spec allows {spec.progress.max_gap_minutes} min)"]
    if spec.estimate and now - state.phase_started_at > timedelta(hours=ESTIMATE_OVERRUN * spec.estimate.hours):
        events = [*events, f"MARKER {who} past {ESTIMATE_OVERRUN}x its estimate of {spec.estimate.hours:g} h - read its log"]
    return events, state


def assess(spec: RunSpec, state: RunState, obs: Observation, now: datetime) -> tuple[list[str], RunState]:
    """The events of one check and the state after it. No I/O: everything the decision needs is in the arguments."""
    early = _unreachable(spec, state, obs)
    if early is not None:
        return early
    state = replace(state, unreachable=0)
    events = [f"MARKER run {spec.name}: {m[:MARKER_WIDTH]}" for m in obs.markers]
    if obs.exit_code is not None and not interrupted(spec, obs):
        return _ended(spec, state, obs, events)
    if not obs.alive:
        return _vanished(spec, state, events, now)
    return _progress(spec, replace(state, gone_seen_at=None), obs, events, now)


def summary(spec: RunSpec, state: RunState) -> str:
    if state.phase_started_at is None:
        return f"{spec.name} waiting"
    seen = state.progress_seen_at or state.phase_started_at
    return f"{spec.name} {state.progress_count} lines, last {seen:%H:%M}"


# ---------------------------------------------------------------- the shell: everything that touches a machine

def probe_script(spec: RunSpec) -> str:
    """The shell lines a check runs where the log lives (the same lines on the laptop and on a server)."""
    q = shlex.quote
    log = q(f"{spec.name}.log")
    lines = [f"cd {q(spec.workdir)} 2>/dev/null || {{ echo workdir=missing; exit 0; }}",
             f'echo "exit=$(cat {q(spec.name + ".exit")} 2>/dev/null)"',
             f'p=$(cat {q(spec.name + ".pid")} 2>/dev/null); if [ -n "$p" ] && kill -0 "$p" 2>/dev/null; then echo alive=1; else echo alive=0; fi',
             f'echo "progress=$(grep -cE {q(spec.progress.regex)} {log} 2>/dev/null)"']
    if spec.progress.heartbeat_glob:                         # unquoted so the shell expands it; the field's pattern admits no other syntax
        lines.append(f"echo \"heartbeat=$(ls -l {spec.progress.heartbeat_glob} 2>/dev/null | awk '{{s += $5}} END {{print s + 0}}')\"")
    for key, rx in (("started", spec.progress.start_regex), ("ended", spec.end_regex), ("failed", spec.fail_regex)):
        if rx:
            lines.append(f"grep -qE {q(rx)} {log} 2>/dev/null && echo {key}=1")
    if spec.fail_regex:
        exit_file, pid_file = q(spec.name + ".exit"), q(spec.name + ".pid")
        lines.append(f'[ -f {exit_file} ] && [ -f {pid_file} ] && echo "lived=$(( $(stat -c %Y {exit_file}) - $(stat -c %Y {pid_file}) ))"')
    if spec.marker_regex:
        lines.append(f"grep -E {q(spec.marker_regex)} {log} 2>/dev/null | tail -n 30 | sed 's/^/marker=/'")
    return "\n".join(lines) + "\n"


def parse_probe(spec: RunSpec, out: str) -> Observation:
    fields: dict[str, str] = {}
    markers = []
    for line in out.splitlines():
        key, _, value = line.partition("=")
        if key == "marker":
            markers.append(value.strip())
        elif key:
            fields[key] = value.strip()
    if fields.get("workdir") == "missing":
        return Observation(workdir_missing=True)
    code, lived = fields.get("exit", ""), fields.get("lived", "")
    return Observation(exit_code=int(code) if code.lstrip("-").isdigit() else None, alive=fields.get("alive") == "1",
                       progress_count=int(fields.get("progress") or 0), heartbeat_bytes=int(fields.get("heartbeat") or 0),
                       started=spec.progress.start_regex is None or fields.get("started") == "1",
                       ended_marker=fields.get("ended") == "1", failed_marker=fields.get("failed") == "1",
                       lived_s=int(lived) if lived.lstrip("-").isdigit() else None, markers=tuple(markers))


class Shell:
    """The real machines. Tests pass a stand-in with the same methods."""

    def __init__(self, bash: str | None = None):
        self.bash = bash or shutil.which("bash") or "bash"

    def _run(self, args: list[str], timeout: float = 120, cwd: Path | None = None) -> subprocess.CompletedProcess:
        # stdin from /dev/null: the scheduled resume task has no console, and inheriting its invalid stdin handle raised WinError 6 (16 Oct).
        # UTF-8 explicitly: Windows' default code page failed on a dry run's φ after the job had started, so no state was saved (28 Oct)
        return subprocess.run(args, cwd=cwd or ROOT, stdin=subprocess.DEVNULL, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=timeout, check=False)

    def host_row(self, host: str) -> tuple[str, str] | None:
        """(ip, machine-id) from tools/hosts.tsv, None when the name is not there."""
        table = Path(os.environ.get("HOSTS_FILE", TOOLS / "hosts.tsv"))
        for line in table.read_text(encoding="utf-8").splitlines() if table.exists() else []:
            cols = line.split("\t")
            if line and not line.startswith("#") and cols[0] == host and len(cols) >= 3:
                return cols[1], cols[2]
        return None

    def run(self, host: str, script: str, timeout: float = 120) -> tuple[int, str]:
        """script on host (the laptop's bash, or host_ssh with its machine-id check): (rc, stdout). rc 3 = another machine, 4 = no such host."""
        if host == LAPTOP:
            r = self._run([self.bash, "-c", script], timeout)
        else:
            r = self._run([self.bash, "-c", '. "$0" && host_ssh "$1" "$2"', (TOOLS / "hosts.sh").as_posix(), host, script], timeout)
        return r.returncode, r.stdout

    def tracked(self, paths: list[Path]) -> list[Path]:
        """The paths git tracks. A tracked log is a hazard under a running job: a commit's pre-commit stash rewrites a tracked file with
        unstaged changes, and the job writes on into the replaced file, unseen by the watch (TASKS 195, 10 Nov 2026)."""
        if not paths:
            return []
        r = self._run(["git", "ls-files", "--", *(p.as_posix() for p in paths)])
        if r.returncode != 0:
            raise RuntimeError(f"git ls-files failed (exit {r.returncode}): {r.stderr.strip()[-300:]}")
        listed = {(ROOT / line).resolve() for line in r.stdout.splitlines() if line}
        return [p for p in paths if p.resolve() in listed]

    def launch_laptop(self, spec: RunSpec, append: bool = False) -> tuple[int, str]:
        n = shlex.quote(spec.name)
        tag = f'export {RUN_TAG}={n} WSLENV="${{WSLENV:+$WSLENV:}}{RUN_TAG}"; '   # WSLENV carries the tag into every wsl.exe below
        env = RUN_ENV + tag + (f"export OMP_NUM_THREADS={spec.threads} MKL_NUM_THREADS={spec.threads} OPENBLAS_NUM_THREADS={spec.threads}; "
                         if spec.threads else "")
        # The job writes into a pipe and one `cat` appends to the log, so no process of the job holds the log's own handle.
        # On 14 Nov 2026 two runs lost the first kilobytes of their logs, and probes/log_append_smoke.sh reproduces it: with a
        # child under probes/wsl_capped.sh and /usr/bin/time, a plain ">" loses four of the child's first lines to the shell's
        # closing ones and ">>" still clips one, because something in that chain writes at an offset of its own that O_APPEND
        # does not govern. Through the pipe the log is whole. PIPESTATUS[0] keeps the job's exit status, not cat's.
        empty = "" if append else f": > {n}.log; "
        wrapped = (f"echo $$ > {n}.pid; rm -f {n}.exit; {empty}( {env}{spec.command} ) 2>&1 | cat >> {n}.log; "
                   f"echo ${{PIPESTATUS[0]}} > {n}.exit")
        r = self._run([self.bash, (TOOLS / "launch_outside_app.sh").as_posix(), spec.name, (ROOT / spec.workdir).as_posix(), wrapped])
        return r.returncode, r.stdout + r.stderr

    def launch_remote(self, spec: RunSpec, ip: str) -> tuple[int, str]:
        args = [self.bash, (TOOLS / "remote_launch.sh").as_posix(), f"root@{ip}", spec.workdir, spec.name]
        if spec.threads:
            args += ["--threads", str(spec.threads)]
        if spec.dry_run_args is not None:
            args += ["--dry-run", spec.dry_run_args]
        r = self._run([*args, "--", spec.command], timeout=DRY_RUN_TIMEOUT_S + 120)
        return r.returncode, r.stdout + r.stderr


def observe(spec: RunSpec, shell: Shell) -> Observation:
    if spec.host != LAPTOP and shell.host_row(spec.host) is None:
        return Observation(host_gone=True)
    rc, out = shell.run(spec.host, probe_script(spec))
    if rc == 3:
        return Observation(wrong_machine=True)
    if not out.strip():
        return Observation(reachable=False)
    return parse_probe(spec, out)


# ---------------------------------------------------------------- launch

class LaunchRefused(Exception):
    pass


def _state_path(name: str, state_dir: Path) -> Path:
    return state_dir / f"{name}.json"


def load_state(name: str, state_dir: Path = STATE_DIR) -> RunState | None:
    p = _state_path(name, state_dir)
    return RunState.from_json(p.read_text(encoding="utf-8")) if p.exists() else None


def save_state(name: str, state: RunState, state_dir: Path = STATE_DIR) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    p = _state_path(name, state_dir)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(state.to_json(), encoding="utf-8")
    os.replace(tmp, p)


def _source_problems(spec: RunSpec, shell: Shell) -> list[str]:
    """Local sources exist and compile (Python) or parse (bash -n)."""
    problems = []
    for s in spec.sources:
        path = ROOT / s.local
        if not path.is_file():
            problems.append(f"source {s.local} not found")
            continue
        if path.suffix == ".py":
            try:
                compile(path.read_bytes(), str(path), "exec")       # no byte-code file is written
            except SyntaxError as e:
                problems.append(f"source {s.local} does not compile: line {e.lineno}: {e.msg}")
        elif path.suffix == ".sh":
            rc, _ = shell.run(LAPTOP, f"bash -n {shlex.quote(path.as_posix())} 2>&1")
            if rc != 0:
                problems.append(f"source {s.local} fails bash -n")
    return problems


def _server_problems(spec: RunSpec, shell: Shell) -> list[str]:
    """A server run's host is the pinned machine, its workdir exists and its source copies equal the local files (sha256)."""
    if shell.host_row(spec.host) is None:
        return [f"host {spec.host} is not in tools/hosts.tsv"]
    remote = [s for s in spec.sources if s.remote]
    rc, out = shell.run(spec.host, f"test -d {shlex.quote(spec.workdir)} && echo workdir=ok; "
                        + "; ".join(f"sha256sum {shlex.quote(s.remote)} 2>/dev/null || echo 'none {s.remote}'" for s in remote))
    if rc == 3:
        return [f"host {spec.host} answers with another machine"]
    problems = []
    if "workdir=ok" not in out:
        problems.append(f"workdir {spec.workdir} missing on {spec.host} (or the host is unreachable)")
    there = {line.split()[-1]: line.split()[0] for line in out.splitlines() if len(line.split()) == 2}
    for s in remote:
        here = hashlib.sha256((ROOT / s.local).read_bytes()).hexdigest() if (ROOT / s.local).is_file() else None
        if there.get(s.remote) != here:
            problems.append(f"source {s.remote} on {spec.host} differs from {s.local} (or is missing)")
    return problems


def preflight(spec: RunSpec, shell: Shell) -> list[str]:
    """Every reason not to launch, empty when there is none. Local sources compile; a server is the pinned machine and has the same copies."""
    problems = _source_problems(spec, shell)
    if spec.host != LAPTOP:
        return problems + _server_problems(spec, shell)
    if not (ROOT / spec.workdir).is_dir():
        problems.append(f"workdir {spec.workdir} does not exist")
    if shell.tracked([laptop_log(spec)]):
        problems.append(f"log {spec.workdir}/{spec.name}.log is tracked by git: a commit would rewrite it under the run (TASKS 195); "
                        "`git rm --cached` it and ignore it first")
    return problems


def measure_free_commit_gb() -> float | None:
    from free_memory import free_commit_gb
    return free_commit_gb()


_HOLDS_THE_LAPTOP = ("running", "stopping")   # a stop that has not finished may have left processes: they keep the memory and the log


def laptop_runs_in_progress(name: str, spec_dir: Path, state_dir: Path) -> tuple[float, list[str]]:
    """(the stated peaks of the laptop runs past their start line, other than `name`; those that state none or do not load)."""
    others, unknown = 0.0, []
    for path in sorted(spec_dir.glob("*.json")):
        state = load_state(path.stem, state_dir)
        if path.stem == name or state is None or state.status not in _HOLDS_THE_LAPTOP or state.phase_started_at is None:
            continue
        try:
            other = load_spec(path)
        except ValidationError:
            unknown.append(path.stem)
            continue
        if other.host != LAPTOP:
            continue
        if other.memory is None:
            unknown.append(other.name)
        else:
            others += other.memory.peak_gb
    return others, unknown


def running_laptop_logs(spec_dir: Path = SPEC_DIR, state_dir: Path = STATE_DIR) -> list[Path]:
    """The logs of the laptop runs whose state is running, waiting ones included: each is open for writing by its job."""
    logs = []
    for path in sorted(spec_dir.glob("*.json")):
        state = load_state(path.stem, state_dir)
        if state is not None and state.status in _HOLDS_THE_LAPTOP and (spec := load_spec(path)).host == LAPTOP:
            logs.append(laptop_log(spec))
    return logs


def measured_room_problems(peak_gb: float) -> list[str]:
    free = measure_free_commit_gb()
    if free is None or free - peak_gb >= FREE_COMMIT_MARGIN_GB:
        return []
    return [f"memory: {free:.1f} GB can be committed now; {peak_gb:g} GB for this run would leave {free - peak_gb:.1f} GB beside the runs "
            f"in progress (< {FREE_COMMIT_MARGIN_GB:g} GB)"]


def over_budget_problems(peak_gb: float, others: float) -> list[str]:
    """A run past the budget on the user's word runs alone; its bound is the cap its command states (a WSL run's wsl_capped.sh inside the
    VM's .wslconfig limit), as for a first run alone, which the measured free commit does not hold either."""
    if others == 0:
        return []
    return [f"memory: {peak_gb:g} GB passes the {LAPTOP_RUN_MEMORY_GB:g} GB budget on the user's word and so runs alone; {others:g} GB of "
            "laptop runs are in progress"]


def memory_problems(spec: RunSpec, spec_dir: Path, state_dir: Path) -> list[str]:
    """Why a laptop run may not start now for memory, empty when it may: it states its measured peak, and that peak plus the peaks of the
    laptop runs in progress fits LAPTOP_RUN_MEMORY_GB. A run still waiting for its start line holds no memory yet and is not counted (the
    chains wait for one another, so one trains at a time). Beside a laptop run in progress, the measured free commit must also leave
    FREE_COMMIT_MARGIN_GB after this run's peak (the user, 21 Oct 2026: the stated peaks fitted on 20-21 Oct while the commit limit ran out,
    the WSL VM and the rest of Windows hold memory no spec states). A run whose memory carries the user's budget_word may pass the budget
    when it is the only laptop run in progress (the user, 8 Nov 2026, TASKS 184); its stated peak still counts against every later run."""
    if spec.host != LAPTOP:
        return []
    if spec.memory is None:
        return [f"{spec.name} states no measured peak memory (memory.peak_gb with its basis); a laptop run needs one"]
    others, unknown = laptop_runs_in_progress(spec.name, spec_dir, state_dir)
    problems = [f"laptop run {n} is in progress without a stated peak memory, so the budget cannot be checked" for n in unknown]
    if spec.memory.budget_word is not None:
        return problems + over_budget_problems(spec.memory.peak_gb, others)
    if others > 0 or unknown:
        problems += measured_room_problems(spec.memory.peak_gb)
    total = others + spec.memory.peak_gb
    if total > LAPTOP_RUN_MEMORY_GB:
        problems.append(f"memory: {spec.memory.peak_gb:g} GB + {others:g} GB of laptop runs in progress = {total:g} GB "
                        f"> {LAPTOP_RUN_MEMORY_GB:g} GB")
    return problems


def keep_earlier_log(spec: RunSpec, now: datetime) -> Path | None:
    """A laptop run's log from an earlier launch, renamed <name>.<launch time>.log so the new launch does not overwrite it (19 Oct 2026:
    chain 41's relaunch overwrote its history). Returns the new path, None when there was no log."""
    log = laptop_log(spec)
    if spec.host != LAPTOP or not log.exists():
        return None
    kept = log.with_name(f"{spec.name}.{now:%Y%m%d-%H%M%S}.log")
    if kept.exists():
        raise LaunchRefused(f"{kept.name} exists already: two launches in the same second")
    log.rename(kept)
    return kept


def launch(spec_path: Path, shell: Shell, now: datetime, state_dir: Path = STATE_DIR) -> str:
    spec = load_spec(spec_path)
    if spec_path.stem != spec.name:
        raise LaunchRefused(f"the spec file is named {spec_path.name} but the run is {spec.name}")
    old = load_state(spec.name, state_dir)
    if old is not None and old.status == "running":
        raise LaunchRefused(f"run {spec.name} is already running (launched {old.started_at:%d %b %H:%M})")
    if old is not None and old.status == "stopping":
        raise LaunchRefused(f"a stop of {spec.name} began {old.stopped_at:%d %b %H:%M} and did not finish: run `runspec.py stop` again first")
    problems = preflight(spec, shell) + memory_problems(spec, spec_path.parent, state_dir)
    if problems:
        raise LaunchRefused("; ".join(problems))
    if spec.host == LAPTOP:
        if spec.dry_run_args is not None:
            rc, out = shell.run(LAPTOP, f"set -o pipefail; cd {shlex.quote(spec.workdir)} && {spec.command} {spec.dry_run_args} 2>&1 | tail -n 5",
                                timeout=DRY_RUN_TIMEOUT_S)
            if rc != 0:
                raise LaunchRefused(f"dry run failed (exit {rc}): {out.strip()[-300:]}")
        keep_earlier_log(spec, now)
        rc, out = shell.launch_laptop(spec)
    else:
        rc, out = shell.launch_remote(spec, shell.host_row(spec.host)[0])
    if rc != 0:
        raise LaunchRefused(f"the launch wrapper failed (exit {rc}): {out.strip()[-300:]}")
    save_state(spec.name, RunState(started_at=now, phase_started_at=None if spec.progress.start_regex else now), state_dir)
    return out.strip()


# ---------------------------------------------------------------- resume

def _resume_reason(spec: RunSpec, shell: Shell) -> str | None:
    """Why a resumable laptop run is to be relaunched now: gone without an exit file, or interrupted; None when it is not."""
    obs = observe(spec, shell)
    if not obs.reachable or obs.workdir_missing or obs.alive:
        return None
    if obs.exit_code is None:
        return "gone without an exit file"
    if interrupted(spec, obs):
        return f"interrupted (exit {obs.exit_code} without its end or failure line, after {obs.lived_s} s)"
    return None


def resume(shell: Shell, now: datetime, spec_dir: Path = SPEC_DIR, state_dir: Path = STATE_DIR, dry: bool = False,
           second_look: float = RESUME_SECOND_LOOK_S) -> list[str]:
    """Relaunch every resumable laptop run that is gone; one line per run acted on (or that would be, with dry)."""
    lines = []
    for path in sorted(spec_dir.glob("*.json")):
        state = load_state(path.stem, state_dir)
        if state is None or state.status != "running":
            continue
        try:
            spec = load_spec(path)
        except ValidationError as e:
            lines.append(f"{path.stem}: spec invalid, not resumed: {str(e).splitlines()[0]}")
            continue
        reason = _resume_reason(spec, shell) if spec.host == LAPTOP and spec.resumable else None
        if reason is None:
            continue
        time.sleep(second_look)
        if _resume_reason(spec, shell) is None or not still_running(spec.name, state_dir):   # a stop in the 30 s holds it
            continue
        if dry:
            lines.append(f"{spec.name}: {reason} - would relaunch: {spec.command}")
            continue
        problems = preflight(spec, shell) + memory_problems(spec, spec_dir, state_dir)
        if problems:
            lines.append(f"{spec.name}: NOT relaunched: {'; '.join(problems)}")
            continue
        rc, out = shell.launch_laptop(spec, append=True)
        if rc != 0:
            lines.append(f"{spec.name}: RELAUNCH FAILED (exit {rc}): {out.strip()[-200:]}")
            continue
        save_state(spec.name, replace(state, relaunches=state.relaunches + 1, gone_seen_at=None), state_dir)
        lines.append(f"{spec.name}: RELAUNCHED (pid {out.strip()}, relaunch {state.relaunches + 1}): {spec.command} - {reason}")
    return lines


# ---------------------------------------------------------------- stop

class StopRefused(Exception):
    pass


def still_running(name: str, state_dir: Path) -> bool:
    """The state on disk says running now: a stop that came while the run was being looked at wins over what the look saw."""
    latest = load_state(name, state_dir)
    return latest is not None and latest.status == "running"


def _key_values(out: str) -> dict[str, str]:
    return {key: value.strip() for key, _, value in (line.partition("=") for line in out.splitlines()) if key}


def wrapper_pattern(spec: RunSpec) -> str:
    """ERE of the run's own wrapper in a command line: launch_outside_app.sh's launch/<name>_<date>_<time>.sh on the laptop,
    remote_launch.sh's <name>.cmd.sh on a server. Anchored on both sides of the name, so chain35 is not chain35_read."""
    if spec.host == LAPTOP:
        return r"launch[\\/]" + spec.name + r"_[0-9]{8}_[0-9]{6}\.sh"
    return "(^|[/'\"])" + spec.name + r"\.cmd\.sh"


def kill_script(spec: RunSpec) -> str:
    """Shell lines that end the tree behind <name>.pid where the run lives; they print was_alive= (before) and alive= (after).
    The pid counts as the run only when its command line names this run's own wrapper - launch_outside_app.sh's launch/<name>_<time>.sh
    on the laptop, remote_launch.sh's <name>.cmd.sh on a server: Git Bash numbers its processes anew after a restart, so a pid file from
    before one can name the watch's bash or another run, and a tree kill there would take that. Such a pid is printed as stale_pid=
    and left alone."""
    q = shlex.quote
    wrapper = q(wrapper_pattern(spec))
    if spec.host == LAPTOP:   # the pid is Git Bash's; /T from its Windows process takes the Windows tree, python and wsl.exe included
        end = 'w=$(cat /proc/"$p"/winpid 2>/dev/null); [ -n "$w" ] && MSYS2_ARG_CONV_EXCL="*" taskkill /PID "$w" /T /F > /dev/null 2>&1'
        alive = 'kill -0 "$p" 2>/dev/null'
    else:                     # remote_launch.sh starts the job with setsid: its pid leads the run's own process group
        end = (f'kill -TERM -- -"$p" 2>/dev/null; for i in $(seq {2 * STOP_WAIT_S}); do kill -0 -- -"$p" 2>/dev/null || break; '
               'sleep 0.5; done; kill -KILL -- -"$p" 2>/dev/null')
        alive = 'kill -0 -- -"$p" 2>/dev/null'
    lines = [f"cd {q(spec.workdir)} || exit 1",
             f"p=$(cat {q(spec.name + '.pid')} 2>/dev/null)",
             f"""mine=0; [ -n "$p" ] && {{ tr '\\0' ' ' < /proc/"$p"/cmdline; }} 2>/dev/null | grep -qE {wrapper} && mine=1""",
             '[ "$mine" = 0 ] && [ -n "$p" ] && kill -0 "$p" 2>/dev/null && echo "stale_pid=$p"',
             f'alive() {{ [ "$mine" = 1 ] && {alive}; }}',
             f"if alive; then echo was_alive=1; {end}; else echo was_alive=0; fi",
             "for i in $(seq 20); do alive || break; sleep 0.5; done",
             "if alive; then echo alive=1; else echo alive=0; fi"]
    return "\n".join(lines) + "\n"


# Run inside WSL with "RUNSPEC_RUN=<name>" and STOP_WAIT_S: TERM to every process that carries the tag (to its whole process group when it
# leads one: `wsl -e` gives each command its own session), KILL to what is left after the wait; prints wsl_tagged= and wsl_left=.
_WSL_STOP = r"""tag=$1; half_seconds=$(( $2 * 2 ))
tagged() {
  for e in /proc/[0-9]*/environ; do
    p=${e#/proc/}; p=${p%/environ}
    [ "$p" != "$$" ] && tr '\0' '\n' < "$e" 2>/dev/null | grep -qxF -- "$tag" && echo "$p"
  done
}
signal() {
  for p in $(tagged); do
    g=$(ps -o pgid= -p "$p" | tr -d ' ')
    if [ "$g" = "$p" ]; then kill -"$1" -- -"$g"; else kill -"$1" "$p"; fi
  done 2>/dev/null
}
echo "wsl_tagged=$(tagged | wc -l)"
signal TERM
for i in $(seq "$half_seconds"); do [ -z "$(tagged)" ] && break; sleep 0.5; done
[ -n "$(tagged)" ] && { signal KILL; sleep 1; }
echo "wsl_left=$(tagged | wc -l)"
"""


def wsl_stop_script(name: str) -> str:
    """Laptop shell lines that end the run's WSL processes; a WSL that is not running is not started for the look."""
    q = shlex.quote
    return ("if [ -n \"$(wsl.exe --list --running --quiet 2>/dev/null | tr -d '\\0\\r[:space:]')\" ]; then "
            f"MSYS_NO_PATHCONV=1 wsl.exe -e bash -c {q(_WSL_STOP)} wsl_stop {q(f'{RUN_TAG}={name}')} {STOP_WAIT_S}; "
            "else echo wsl=off; echo wsl_left=0; fi\n")


def stop_line(spec: RunSpec, now: datetime, reason: str) -> str:
    return f"=== runspec stop: {spec.name} stopped by hand {now:%Y-%m-%d %H:%M:%S}, exit {STOP_EXIT}" + (f": {reason}" if reason else "")


def _refuse_unstoppable(spec: RunSpec, shell: Shell, retry: bool) -> None:
    """A run whose host or folder cannot be read is not stopped blind; one that ended by itself keeps its own exit code (on a retry the
    exit file may be the first stop's own)."""
    obs = observe(spec, shell)
    if obs.host_gone or obs.wrong_machine or not obs.reachable or obs.workdir_missing:
        raise StopRefused(f"run {spec.name}: its host {spec.host} or its workdir cannot be read - see `check --peek`")
    if not retry and obs.exit_code is not None and not obs.alive and not interrupted(spec, obs):
        raise StopRefused(f"run {spec.name} has ended by itself (exit {obs.exit_code}); the check reports it")


def _end_tree(spec: RunSpec, shell: Shell) -> tuple[list[str], list[str]]:
    """Ends the run's processes: (what the caller should know about how it went, what is left of them - empty when nothing is)."""
    rc, out = shell.run(spec.host, kill_script(spec), timeout=4 * STOP_WAIT_S + 60)
    seen = _key_values(out)
    left = [] if seen.get("alive") == "0" else [f"the tree behind {spec.name}.pid is still alive after the kill (rc {rc})"]
    notes = []
    if "stale_pid" in seen:
        notes.append(f"(process {seen['stale_pid']} of {spec.name}.pid is not this run's launch wrapper and was left alone: the pid file "
                     "is from before a restart)")
    if seen.get("was_alive") != "1":
        notes.append("(no process of it was alive: the stop holds a run that had gone)")
    if spec.host == LAPTOP:
        _, out = shell.run(LAPTOP, wsl_stop_script(spec.name), timeout=4 * STOP_WAIT_S + 60)
        wsl = _key_values(out)
        if wsl.get("wsl_left", "unknown") != "0":
            left.append(f"WSL processes tagged {RUN_TAG}={spec.name} left: {wsl.get('wsl_left', 'unknown')}")
        elif wsl.get("wsl_tagged") == "0":
            notes.append(f"(WSL runs and no process in it carries {RUN_TAG}={spec.name}: the WSL processes of a run launched before the "
                         "tag existed, 19 Nov 2026, cannot be swept - look with `wsl.exe -e ps -ef`)")
    return notes, left


def _record_stop(spec: RunSpec, shell: Shell, line: str) -> None:
    q = shlex.quote
    _, out = shell.run(spec.host, f"cd {q(spec.workdir)} && printf '%s\\n' {q(line)} >> {q(spec.name + '.log')} && "
                                  f"echo {STOP_EXIT} > {q(spec.name + '.exit')} && echo recorded=1\n")
    if _key_values(out).get("recorded") != "1":
        raise StopRefused(f"the processes of {spec.name} are gone, but its stop line and exit file could not be written")


def stop(spec_path: Path, shell: Shell, now: datetime, state_dir: Path = STATE_DIR, reason: str = "") -> str:
    """Ends a running run (or finishes a stop that did not) and holds it until its next launch; returns the stop line. Past the first
    look the state is 'stopping', and a failure leaves it so: the run stays held from resume and the check reports it after STOP_STALE."""
    spec = load_spec(spec_path)
    if spec_path.stem != spec.name:
        raise StopRefused(f"the spec file is named {spec_path.name} but the run is {spec.name}")
    old = load_state(spec.name, state_dir)
    if old is None or old.status not in ("running", "stopping"):
        raise StopRefused(f"run {spec.name} is not running ({'never launched' if old is None else old.status})")
    _refuse_unstoppable(spec, shell, retry=old.status == "stopping")
    save_state(spec.name, replace(old, status="stopping", stopped_at=now), state_dir)   # first: a check or resume meanwhile leaves it
    notes, left = _end_tree(spec, shell)
    if left:
        raise StopRefused("; ".join(left) + " - the run stays 'stopping'; `runspec.py stop` again tries again")
    line = stop_line(spec, now, reason)
    _record_stop(spec, shell, line)
    save_state(spec.name, replace(old, status="stopped", stopped_at=now), state_dir)
    return "\n".join([line, *notes])


def held(name: str, state: RunState, now: datetime, state_dir: Path, peek: bool) -> str | None:
    """The check's line for a run a stop holds: one MARKER when it is stopped (with peek it stays for the watch), an ANOMALY while a
    stop has not finished for STOP_STALE; None otherwise."""
    if state.status == "stopped" and not state.stop_reported:
        if not peek:
            save_state(name, replace(state, stop_reported=True), state_dir)
        return f"MARKER run {name} stopped by hand {state.stopped_at:%d %b %H:%M} (launched {state.started_at:%d %b %H:%M})"
    if state.status == "stopping" and now - state.stopped_at > STOP_STALE:
        return f"ANOMALY run {name}: a stop began {state.stopped_at:%d %b %H:%M} and did not finish - `runspec.py stop` it again"
    return None


# ---------------------------------------------------------------- check

def check(shell: Shell, now: datetime, spec_dir: Path = SPEC_DIR, state_dir: Path = STATE_DIR, peek: bool = False) -> list[str]:
    """One line per event of every running run, then the QUIET summary. With peek the states are not saved: an event that is reported
    once (an end, a marker) stays for the watch."""
    lines, quiet = [], []
    for path in sorted(spec_dir.glob("*.json")):
        state = load_state(path.stem, state_dir)
        line = None if state is None else held(path.stem, state, now, state_dir, peek)
        if line is not None or (state is not None and state.status == "stopping"):
            lines += [line] if line else []
            quiet.append(f"{path.stem} {state.status}")
            continue
        if state is None or state.status != "running":
            continue
        try:
            spec = load_spec(path)
            events, state = assess(spec, state, observe(spec, shell), now)
        except (ValidationError, OSError, subprocess.SubprocessError, ValueError) as e:
            lines.append(f"ANOMALY run {path.stem}: the check failed: {type(e).__name__}: {str(e).splitlines()[0][:MARKER_WIDTH]}")
            continue
        if not still_running(spec.name, state_dir):         # stopped while it was looked at: the stop is reported at the next check
            continue
        if not peek:
            save_state(spec.name, state, state_dir)
        lines += events
        quiet.append(summary(spec, state) if state.status == "running" else f"{spec.name} ended")
    return [*lines, "QUIET " + ("; ".join(quiet) or "no runs")]


def _now() -> datetime:
    return datetime.now().astimezone()


def _cmd_validate(a: argparse.Namespace, shell: Shell) -> int:
    try:
        spec = load_spec(a.spec)
    except ValidationError as e:
        print(e)
        return 1
    problems = preflight(spec, shell)
    print("\n".join(problems) or f"{spec.name}: valid, sources compile" + ("" if spec.host == LAPTOP else ", server copies match"))
    return 1 if problems else 0


def _cmd_launch(a: argparse.Namespace, shell: Shell) -> int:
    try:
        print(launch(a.spec, shell, _now()))
    except (LaunchRefused, ValidationError) as e:
        print(f"NOT launched: {e}")
        return 1
    return 0


def _cmd_check(a: argparse.Namespace, shell: Shell) -> int:
    print("\n".join(check(shell, _now(), peek=a.peek)))
    return 0


def _cmd_resume(a: argparse.Namespace, shell: Shell) -> int:
    print("\n".join(resume(shell, _now(), dry=a.dry_run)) or "no run to resume")
    return 0


def _cmd_stop(a: argparse.Namespace, shell: Shell) -> int:
    try:
        print(stop(a.spec, shell, _now(), reason=a.reason))
    except (StopRefused, ValidationError) as e:
        print(f"NOT stopped: {e}")
        return 1
    return 0


def _cmd_list(_: argparse.Namespace, __: Shell) -> int:
    for path in sorted(SPEC_DIR.glob("*.json")):
        state = load_state(path.stem)
        print(f"{path.stem}\t{'never launched' if state is None else state.status}\t"
              f"{'' if state is None else state.started_at.strftime('%Y-%m-%d %H:%M')}")
    return 0


def main(argv: list[str] | None = None) -> int:
    # markers quote run logs verbatim; a '≈' in one stopped the watch's check under Windows' cp1252 console (30 Oct 2026)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("validate", "launch"):
        sub.add_parser(name).add_argument("spec", type=Path)
    sub.add_parser("check").add_argument("--peek", action="store_true", help="do not save the state (a look by hand)")
    sub.add_parser("resume").add_argument("--dry-run", action="store_true")
    sub.add_parser("list")
    stopper = sub.add_parser("stop", help="end a running run's process tree and hold it until its next launch")
    stopper.add_argument("spec", type=Path)
    stopper.add_argument("--reason", default="", help="why, appended to the stop line in the run's log")
    a = ap.parse_args(argv)
    commands = {"validate": _cmd_validate, "launch": _cmd_launch, "check": _cmd_check, "resume": _cmd_resume, "list": _cmd_list,
                "stop": _cmd_stop}
    return commands[a.cmd](a, Shell())


if __name__ == "__main__":
    sys.exit(main())
