"""runspec — one door for long runs, each with a progress contract (15 Oct 2026, TASKS 63).

Why: the #2702 repro ran 37 h in a library fallback without one line in its log. The run rule said "a run longer than an hour prints a
progress line at least hourly"; the threshold needed an estimate, the estimate was wrong, and the job had been started by hand, past every
wrapper. Here a run cannot start without saying which log lines prove progress and how long they may stay away, whatever its expected length.

A run is a spec, probes/runspecs/<name>.json (committed: the launch record), and a state, probes/watch_state/runs/<name>.json (git-ignored).
  launch    refuses an invalid spec, a run already running, an unknown or re-used host, a source that does not compile or whose server copy
            differs (sha256), and a failed dry run; then starts the command through the existing wrappers — tools/remote_launch.sh on a server,
            tools/launch_outside_app.sh on the laptop. Both leave <name>.log, <name>.pid and, when the command ends, <name>.exit in the workdir.
  check     what probes/watch.sh runs every ten minutes. Per running run: marker lines, the exit file, the pid, the count of progress lines.
            One line per event on stdout — 'ANOMALY <text>' (a decision is needed), 'MARKER <text>' (news), a final 'QUIET <summary>'. The
            texts are stable while the situation lasts, so the watch's seen file reports each one once.

    python tools/runspec.py validate probes/runspecs/<name>.json
    python tools/runspec.py launch probes/runspecs/<name>.json
    python tools/runspec.py check
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

    _check_regex = field_validator("regex", "start_regex")(_ere)


class Estimate(_Frozen):
    hours: float = Field(gt=0)
    basis: str = Field(min_length=10, description="the measurement the hours come from; an estimate without one is not written down")


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
    dry_run_args: str | None = Field(default=None, description="appended to the command for the dry run before the launch")
    threads: int | None = Field(default=None, ge=1, le=64)
    estimate: Estimate | None = None

    _check_regex = field_validator("marker_regex", "end_regex")(_ere)

    @model_validator(mode="after")
    def _paths_fit_the_host(self) -> RunSpec:
        on_laptop = self.host == LAPTOP
        if on_laptop and (PurePosixPath(self.workdir).is_absolute() or ".." in PurePosixPath(self.workdir).parts):
            raise ValueError("a laptop workdir is relative to the plan folder and stays inside it")
        if not on_laptop and not self.workdir.startswith("/"):
            raise ValueError("a server workdir is absolute")
        if on_laptop and any(s.remote for s in self.sources):
            raise ValueError("a laptop run has no remote copies of its sources")
        return self


def load_spec(path: Path) -> RunSpec:
    return RunSpec.model_validate_json(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------- the state and what a check sees

@dataclass(frozen=True)
class RunState:
    started_at: datetime
    status: str = "running"                 # running | ended
    phase_started_at: datetime | None = None  # when the progress gap began to count (the launch, or start_regex's first line)
    progress_count: int = 0
    progress_seen_at: datetime | None = None  # the last check at which the count changed
    unreachable: int = 0

    def to_json(self) -> str:
        return json.dumps({k: v.isoformat() if isinstance(v, datetime) else v for k, v in asdict(self).items()}, indent=1)

    @classmethod
    def from_json(cls, text: str) -> RunState:
        raw = json.loads(text)
        return cls(**{k: datetime.fromisoformat(v) if k.endswith("_at") and v else v for k, v in raw.items()})


@dataclass(frozen=True)
class Observation:
    reachable: bool = True
    wrong_machine: bool = False
    host_gone: bool = False
    workdir_missing: bool = False
    exit_code: int | None = None
    alive: bool = False
    progress_count: int = 0
    started: bool = False
    ended_marker: bool = False
    markers: tuple[str, ...] = ()


def assess(spec: RunSpec, state: RunState, obs: Observation, now: datetime) -> tuple[list[str], RunState]:
    """The events of one check and the state after it. No I/O: everything the decision needs is in the arguments."""
    who = f"run {spec.name}"
    if obs.host_gone:
        return [f"ANOMALY {who}: host {spec.host} is no longer in tools/hosts.tsv and the run never ended"], state
    if obs.wrong_machine:
        return [f"ANOMALY {who}: host {spec.host} answers with another machine (re-used IP?) - see tools/hosts.tsv"], state
    if not obs.reachable:
        state = replace(state, unreachable=state.unreachable + 1)
        return ([f"ANOMALY {who}: host {spec.host} unreachable twice"] if state.unreachable >= 2 else []), state
    state = replace(state, unreachable=0)
    if obs.workdir_missing:
        return [f"ANOMALY {who}: workdir {spec.workdir} missing on {spec.host}"], state
    events = [f"MARKER {who}: {m[:MARKER_WIDTH]}" for m in obs.markers]

    if obs.exit_code is not None:
        state = replace(state, status="ended")
        if obs.exit_code != 0:
            return events + [f"ANOMALY {who} ended with exit {obs.exit_code}"], state
        if spec.end_regex and not obs.ended_marker:
            return events + [f"ANOMALY {who} exited 0 without its end line /{spec.end_regex}/"], state
        return events + [f"MARKER {who} ended (exit 0)"], state
    if not obs.alive:
        return events + [f"ANOMALY {who} gone without an exit file (launched {state.started_at:%d %b %H:%M})"], state

    if state.phase_started_at is None:                       # still waiting for start_regex
        if not obs.started:
            return events, state
        state = replace(state, phase_started_at=now, progress_count=obs.progress_count, progress_seen_at=now)
    if obs.progress_count != state.progress_count:
        state = replace(state, progress_count=obs.progress_count, progress_seen_at=now)
    seen = state.progress_seen_at or state.phase_started_at
    if now - seen > timedelta(minutes=spec.progress.max_gap_minutes):
        events.append(f"ANOMALY {who}: no progress line since {seen:%d %b %H:%M} (the spec allows {spec.progress.max_gap_minutes} min)")
    if spec.estimate and now - state.phase_started_at > timedelta(hours=ESTIMATE_OVERRUN * spec.estimate.hours):
        events.append(f"MARKER {who} past {ESTIMATE_OVERRUN}x its estimate of {spec.estimate.hours:g} h - read its log")
    return events, state


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
    for key, rx in (("started", spec.progress.start_regex), ("ended", spec.end_regex)):
        if rx:
            lines.append(f"grep -qE {q(rx)} {log} 2>/dev/null && echo {key}=1")
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
    code = fields.get("exit", "")
    return Observation(exit_code=int(code) if code.lstrip("-").isdigit() else None, alive=fields.get("alive") == "1",
                       progress_count=int(fields.get("progress") or 0),
                       started=spec.progress.start_regex is None or fields.get("started") == "1",
                       ended_marker=fields.get("ended") == "1", markers=tuple(markers))


class Shell:
    """The real machines. Tests pass a stand-in with the same methods."""

    def __init__(self, bash: str | None = None):
        self.bash = bash or shutil.which("bash") or "bash"

    def _run(self, args: list[str], timeout: float = 120, cwd: Path = ROOT) -> subprocess.CompletedProcess:
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)

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

    def launch_laptop(self, spec: RunSpec) -> tuple[int, str]:
        n = shlex.quote(spec.name)
        env = f"export OMP_NUM_THREADS={spec.threads} MKL_NUM_THREADS={spec.threads} OPENBLAS_NUM_THREADS={spec.threads}; " if spec.threads else ""
        wrapped = f"echo $$ > {n}.pid; rm -f {n}.exit; ( {env}{spec.command} ) > {n}.log 2>&1; echo $? > {n}.exit"
        r = self._run([self.bash, (TOOLS / "launch_outside_app.sh").as_posix(), spec.name, (ROOT / spec.workdir).as_posix(), wrapped])
        return r.returncode, r.stdout + r.stderr

    def launch_remote(self, spec: RunSpec, ip: str) -> tuple[int, str]:
        args = [self.bash, (TOOLS / "remote_launch.sh").as_posix(), f"root@{ip}", spec.workdir, spec.name]
        if spec.threads:
            args += ["--threads", str(spec.threads)]
        if spec.dry_run_args is not None:
            args += ["--dry-run", spec.dry_run_args]
        r = self._run(args + ["--", spec.command], timeout=DRY_RUN_TIMEOUT_S + 120)
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


def preflight(spec: RunSpec, shell: Shell) -> list[str]:
    """Every reason not to launch, empty when there is none. Local sources compile; a server is the pinned machine and has the same copies."""
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
    if spec.host == LAPTOP:
        if not (ROOT / spec.workdir).is_dir():
            problems.append(f"workdir {spec.workdir} does not exist")
        return problems
    if shell.host_row(spec.host) is None:
        return problems + [f"host {spec.host} is not in tools/hosts.tsv"]
    remote = [s for s in spec.sources if s.remote]
    rc, out = shell.run(spec.host, f"test -d {shlex.quote(spec.workdir)} && echo workdir=ok; "
                        + "; ".join(f"sha256sum {shlex.quote(s.remote)} 2>/dev/null || echo 'none {s.remote}'" for s in remote))
    if rc == 3:
        return problems + [f"host {spec.host} answers with another machine"]
    if "workdir=ok" not in out:
        problems.append(f"workdir {spec.workdir} missing on {spec.host} (or the host is unreachable)")
    there = {line.split()[-1]: line.split()[0] for line in out.splitlines() if len(line.split()) == 2}
    for s in remote:
        here = hashlib.sha256((ROOT / s.local).read_bytes()).hexdigest() if (ROOT / s.local).is_file() else None
        if there.get(s.remote) != here:
            problems.append(f"source {s.remote} on {spec.host} differs from {s.local} (or is missing)")
    return problems


def launch(spec_path: Path, shell: Shell, now: datetime, state_dir: Path = STATE_DIR) -> str:
    spec = load_spec(spec_path)
    if spec_path.stem != spec.name:
        raise LaunchRefused(f"the spec file is named {spec_path.name} but the run is {spec.name}")
    old = load_state(spec.name, state_dir)
    if old is not None and old.status == "running":
        raise LaunchRefused(f"run {spec.name} is already running (launched {old.started_at:%d %b %H:%M})")
    problems = preflight(spec, shell)
    if problems:
        raise LaunchRefused("; ".join(problems))
    if spec.host == LAPTOP:
        if spec.dry_run_args is not None:
            rc, out = shell.run(LAPTOP, f"set -o pipefail; cd {shlex.quote(spec.workdir)} && {spec.command} {spec.dry_run_args} 2>&1 | tail -n 5",
                                timeout=DRY_RUN_TIMEOUT_S)
            if rc != 0:
                raise LaunchRefused(f"dry run failed (exit {rc}): {out.strip()[-300:]}")
        rc, out = shell.launch_laptop(spec)
    else:
        rc, out = shell.launch_remote(spec, shell.host_row(spec.host)[0])
    if rc != 0:
        raise LaunchRefused(f"the launch wrapper failed (exit {rc}): {out.strip()[-300:]}")
    save_state(spec.name, RunState(started_at=now, phase_started_at=None if spec.progress.start_regex else now), state_dir)
    return out.strip()


# ---------------------------------------------------------------- check

def check(shell: Shell, now: datetime, spec_dir: Path = SPEC_DIR, state_dir: Path = STATE_DIR) -> list[str]:
    lines, quiet = [], []
    for path in sorted(spec_dir.glob("*.json")):
        state = load_state(path.stem, state_dir)
        if state is None or state.status != "running":
            continue
        try:
            spec = load_spec(path)
            events, state = assess(spec, state, observe(spec, shell), now)
        except (ValidationError, OSError, subprocess.SubprocessError, ValueError) as e:
            lines.append(f"ANOMALY run {path.stem}: the check failed: {type(e).__name__}: {str(e).splitlines()[0][:MARKER_WIDTH]}")
            continue
        save_state(spec.name, state, state_dir)
        lines += events
        quiet.append(summary(spec, state) if state.status == "running" else f"{spec.name} ended")
    return lines + ["QUIET " + ("; ".join(quiet) or "no runs")]


def _now() -> datetime:
    return datetime.now().astimezone()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("validate", "launch"):
        sub.add_parser(name).add_argument("spec", type=Path)
    sub.add_parser("check")
    sub.add_parser("list")
    a = ap.parse_args(argv)
    shell = Shell()
    if a.cmd == "validate":
        try:
            spec = load_spec(a.spec)
        except ValidationError as e:
            print(e)
            return 1
        problems = preflight(spec, shell)
        print("\n".join(problems) or f"{spec.name}: valid, sources compile" + ("" if spec.host == LAPTOP else ", server copies match"))
        return 1 if problems else 0
    if a.cmd == "launch":
        try:
            print(launch(a.spec, shell, _now()))
        except (LaunchRefused, ValidationError) as e:
            print(f"NOT launched: {e}")
            return 1
        return 0
    if a.cmd == "check":
        print("\n".join(check(shell, _now())))
        return 0
    for path in sorted(SPEC_DIR.glob("*.json")):
        state = load_state(path.stem)
        print(f"{path.stem}\t{'never launched' if state is None else state.status}\t"
              f"{'' if state is None else state.started_at.strftime('%Y-%m-%d %H:%M')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
