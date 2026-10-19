"""tools/runspec.py (15 Oct 2026, TASKS 63): a run starts only with a progress contract, and the check turns a missing progress line, a
vanished process, a bad exit or an overrun into one stable event each. The decision (assess) is tested without I/O; the probe lines run in a
real bash on a scratch folder; launch and check run against a stand-in shell."""
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

pytest.importorskip("pydantic")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "tools"))
import runspec as R  # noqa: E402
from pydantic import ValidationError  # noqa: E402

BASH = shutil.which("bash")
T0 = datetime(2026, 10, 15, 18, 0).astimezone()


def spec(**over) -> R.RunSpec:
    base = dict(name="demo", purpose="TASKS 63 test run", host="laptop", workdir="probes", command="python probes/demo.py",
                sources=[{"local": "tools/stamp.py"}], progress={"regex": "^  progress ", "max_gap_minutes": 60},
                memory={"peak_gb": 4.0, "basis": "peak working set of a test run"})
    return R.RunSpec.model_validate(base | over)


# ---------------------------------------------------------------- the spec refuses what the rule forbids

@pytest.mark.parametrize("over, words", [
    ({"progress": {"regex": "^p", "max_gap_minutes": 180}}, "less than or equal to 120"),       # the hourly rule, with check slack
    ({"progress": {"regex": r"step \d+", "max_gap_minutes": 60}}, "not POSIX ERE"),             # grep -E reads \d differently
    ({"marker_regex": "(?i)done"}, "not POSIX ERE"),
    ({"sources": []}, "at least 1"),                                                         # nothing to compile is no preflight
    ({"workdir": "/root/x"}, "relative to the plan folder"),
    ({"workdir": "../elsewhere"}, "relative to the plan folder"),
    ({"host": "labels", "workdir": "probes"}, "absolute"),
    ({"sources": [{"local": "tools/stamp.py", "remote": "/root/stamp.py"}]}, "no remote copies"),
    ({"estimate": {"hours": 2, "basis": "guess"}}, "at least 10"),                              # an estimate names its measurement
    ({"eta": "soon"}, "Extra inputs"),
    ({"name": "has space"}, "pattern"),
    ({"progress": {"regex": "^p", "max_gap_minutes": 60, "heartbeat_glob": "x; rm -rf /"}}, "pattern"),   # expanded by the shell: no syntax
])
def test_spec_refusals(over, words):
    with pytest.raises(ValidationError, match=words):
        spec(**over)


def test_progress_is_required():
    raw = spec().model_dump()
    del raw["progress"]
    with pytest.raises(ValidationError, match="progress"):
        R.RunSpec.model_validate(raw)


# ---------------------------------------------------------------- assess: the decision without I/O

def run_state(**over) -> R.RunState:
    return R.RunState(**(dict(started_at=T0, phase_started_at=T0) | over))


def alive(count=0, **over) -> R.Observation:
    return R.Observation(**(dict(alive=True, progress_count=count) | over))


def test_progress_resets_the_gap_and_silence_is_one_stable_anomaly():
    s = spec()
    ev, st = R.assess(s, run_state(), alive(1), T0 + timedelta(minutes=50))
    assert ev == [] and st.progress_count == 1 and st.progress_seen_at == T0 + timedelta(minutes=50)
    ev, st = R.assess(s, st, alive(1), T0 + timedelta(minutes=100))
    assert ev == []                                                               # 50 min of silence is inside 60
    ev1, st = R.assess(s, st, alive(1), T0 + timedelta(minutes=111))
    ev2, st = R.assess(s, st, alive(1), T0 + timedelta(minutes=121))
    assert len(ev1) == 1 and ev1[0].startswith("ANOMALY run demo: no progress line since 15 Oct 18:50") and ev1 == ev2   # same text: seen once
    ev, st = R.assess(s, st, alive(2), T0 + timedelta(minutes=131))
    assert ev == []


def test_a_growing_heartbeat_resets_the_gap_and_a_still_one_does_not():
    s = spec(progress={"regex": "^  progress ", "max_gap_minutes": 60, "heartbeat_glob": "hess/pyscf.log"})
    ev, st = R.assess(s, run_state(), alive(0, heartbeat_bytes=100), T0 + timedelta(minutes=50))
    assert ev == [] and st.heartbeat_bytes == 100 and st.progress_seen_at == T0 + timedelta(minutes=50)
    ev, st = R.assess(s, st, alive(0, heartbeat_bytes=900), T0 + timedelta(minutes=105))
    assert ev == [] and st.progress_seen_at == T0 + timedelta(minutes=105)        # no progress line for 105 min, but the log grew
    ev, st = R.assess(s, st, alive(0, heartbeat_bytes=900), T0 + timedelta(minutes=170))
    assert len(ev) == 1 and "no progress line and no heartbeat growth since 15 Oct 19:45" in ev[0]


def test_a_waiting_run_has_no_gap_until_its_start_line():
    s = spec(progress={"regex": "^  progress ", "max_gap_minutes": 60, "start_regex": "^=== start"})
    st = run_state(phase_started_at=None)
    ev, st = R.assess(s, st, alive(0, started=False), T0 + timedelta(days=5))
    assert ev == [] and st.phase_started_at is None and R.summary(s, st) == "demo waiting"
    later = T0 + timedelta(days=6)
    ev, st = R.assess(s, st, alive(0, started=True), later)
    assert ev == [] and st.phase_started_at == later
    ev, _ = R.assess(s, st, alive(0, started=True), later + timedelta(minutes=61))
    assert ev and "no progress line since" in ev[0]


@pytest.mark.parametrize("obs, end_regex, expect", [
    (R.Observation(exit_code=0), None, "MARKER run demo ended (exit 0)"),
    (R.Observation(exit_code=0, ended_marker=True), "^=== done", "MARKER run demo ended (exit 0)"),
    (R.Observation(exit_code=0), "^=== done", "ANOMALY run demo exited 0 without its end line"),
    (R.Observation(exit_code=137), None, "ANOMALY run demo ended with exit 137"),
    (R.Observation(alive=False), None, "ANOMALY run demo gone without an exit file"),
    (R.Observation(wrong_machine=True), None, "ANOMALY run demo: host laptop answers with another machine"),
    (R.Observation(host_gone=True), None, "ANOMALY run demo: host laptop is no longer"),
    (R.Observation(workdir_missing=True), None, "ANOMALY run demo: workdir probes missing"),
])
def test_endings_and_failures(obs, end_regex, expect):
    ev, st = R.assess(spec(end_regex=end_regex), run_state(), obs, T0 + timedelta(minutes=5))
    assert ev[-1].startswith(expect)
    assert st.status == ("ended" if obs.exit_code is not None else "running")


def test_unreachable_once_is_quiet_twice_is_an_anomaly():
    s, st = spec(), run_state()
    ev, st = R.assess(s, st, R.Observation(reachable=False), T0)
    assert ev == [] and st.unreachable == 1
    ev, st = R.assess(s, st, R.Observation(reachable=False), T0)
    assert ev == ["ANOMALY run demo: host laptop unreachable twice"]
    _, st = R.assess(s, st, alive(0), T0)
    assert st.unreachable == 0


def test_markers_and_the_estimate_overrun():
    s = spec(estimate={"hours": 2, "basis": "measured: 2 h on hel1-6, 14 Oct"})
    ev, _ = R.assess(s, run_state(), alive(5, markers=("=== (X) step 1 done",)), T0 + timedelta(minutes=170))
    assert ev == ["MARKER run demo: === (X) step 1 done"]
    ev, _ = R.assess(s, run_state(progress_count=5, progress_seen_at=T0 + timedelta(minutes=170)), alive(5), T0 + timedelta(minutes=181))
    assert ev == ["MARKER run demo past 1.5x its estimate of 2 h - read its log"]


def test_state_round_trip():
    st = run_state(progress_count=3, progress_seen_at=T0 + timedelta(minutes=7))
    assert R.RunState.from_json(st.to_json()) == st
    assert R.RunState.from_json(R.RunState(started_at=T0).to_json()) == R.RunState(started_at=T0)


# ---------------------------------------------------------------- the probe lines in a real bash

@pytest.mark.skipif(BASH is None, reason="bash not available")
def test_probe_lines_read_a_real_run_folder(tmp_path):
    s = spec(workdir="w", progress={"regex": "^  progress ", "max_gap_minutes": 60, "start_regex": "^=== \\(X\\) start"},
             marker_regex="^=== \\(X\\) ", end_regex="^=== \\(X\\) all done")
    w = tmp_path / "w"
    w.mkdir()
    (w / "demo.log").write_text("=== (X) start\n  progress 1\nnoise 'quoted' $x\n  progress 2\n=== (X) all done\n", encoding="utf-8", newline="\n")
    script = R.probe_script(s)
    running = subprocess.run([BASH, "-c", "cd w && echo $$ > demo.pid && cd .. && " + script], cwd=tmp_path, capture_output=True, text=True, check=True)
    obs = R.parse_probe(s, running.stdout)
    assert obs == R.Observation(alive=True, progress_count=2, started=True, ended_marker=True,
                                markers=("=== (X) start", "=== (X) all done"))
    (w / "demo.pid").write_text("999999\n", encoding="utf-8")
    (w / "demo.exit").write_text("0\n", encoding="utf-8")
    obs = R.parse_probe(s, subprocess.run([BASH, "-c", script], cwd=tmp_path, capture_output=True, text=True, check=True).stdout)
    assert obs.exit_code == 0 and not obs.alive
    shutil.rmtree(w)
    obs = R.parse_probe(s, subprocess.run([BASH, "-c", script], cwd=tmp_path, capture_output=True, text=True, check=True).stdout)
    assert obs.workdir_missing


def test_the_probe_sums_the_heartbeat_files(tmp_path):
    s = spec(workdir="w", progress={"regex": "^  progress ", "max_gap_minutes": 60, "heartbeat_glob": "*/pyscf.log"})
    for sub, text in (("a", "x" * 300), ("b", "y" * 45)):
        (tmp_path / "w" / sub).mkdir(parents=True)
        (tmp_path / "w" / sub / "pyscf.log").write_text(text, encoding="utf-8")
    script = R.probe_script(s)
    assert R.parse_probe(s, subprocess.run([BASH, "-c", script], cwd=tmp_path, capture_output=True, text=True, check=True).stdout).heartbeat_bytes == 345
    assert "heartbeat" not in R.probe_script(spec())                              # no glob, no line


# ---------------------------------------------------------------- launch and check against a stand-in shell

class FakeShell:
    def __init__(self, hosts=None, probe_out="", rc=0, sha=None):
        self.hosts, self.probe_out, self.rc, self.sha = hosts or {}, probe_out, rc, sha or {}
        self.launched = []

    def host_row(self, host):
        return self.hosts.get(host)

    def run(self, host, script, timeout=120):
        if script.startswith("bash -n"):
            return 0, ""
        if "sha256sum" in script or script.startswith("test -d"):
            return self.rc, "workdir=ok\n" + "".join(f"{h}  {p}\n" for p, h in self.sha.items())
        return self.rc, self.probe_out

    def launch_laptop(self, s, append=False):
        self.launched.append(("laptop", s.name, append))
        return 0, "4242"

    def launch_remote(self, s, ip):
        self.launched.append((ip, s.name))
        return 0, f"launched {s.name}"


def write_spec(d: Path, s: R.RunSpec) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    p = d / f"{s.name}.json"
    p.write_text(s.model_dump_json(indent=1), encoding="utf-8")
    return p


def test_launch_records_the_state_and_refuses_a_second_launch(tmp_path):
    p = write_spec(tmp_path / "specs", spec())
    sh = FakeShell()
    R.launch(p, sh, T0, tmp_path / "state")
    st = R.load_state("demo", tmp_path / "state")
    assert sh.launched == [("laptop", "demo", False)] and st.started_at == T0 and st.phase_started_at == T0 and st.status == "running"
    with pytest.raises(R.LaunchRefused, match="already running"):
        R.launch(p, sh, T0, tmp_path / "state")


def test_launch_refuses_a_source_that_does_not_compile(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "ROOT", tmp_path)
    (tmp_path / "w").mkdir()
    (tmp_path / "bad.py").write_text("def f(:\n", encoding="utf-8")
    p = write_spec(tmp_path / "specs", spec(workdir="w", sources=[{"local": "bad.py"}, {"local": "absent.py"}]))
    with pytest.raises(R.LaunchRefused, match=r"bad\.py does not compile.*absent\.py not found"):
        R.launch(p, FakeShell(), T0, tmp_path / "state")
    assert R.load_state("demo", tmp_path / "state") is None


def test_launch_on_a_server_checks_the_pinned_host_and_the_copies(tmp_path):
    local = PLAN / "tools" / "stamp.py"
    import hashlib
    good = hashlib.sha256(local.read_bytes()).hexdigest()
    s = spec(host="labels", workdir="/root/x", sources=[{"local": "tools/stamp.py", "remote": "/root/x/stamp.py"}])
    p = write_spec(tmp_path / "specs", s)
    with pytest.raises(R.LaunchRefused, match=r"not in tools/hosts\.tsv"):
        R.launch(p, FakeShell(), T0, tmp_path / "state")
    with pytest.raises(R.LaunchRefused, match="differs"):
        R.launch(p, FakeShell(hosts={"labels": ("192.0.2.1", "aaaa")}, sha={"/root/x/stamp.py": "0" * 64}), T0, tmp_path / "state")
    with pytest.raises(R.LaunchRefused, match="another machine"):
        R.launch(p, FakeShell(hosts={"labels": ("192.0.2.1", "aaaa")}, rc=3), T0, tmp_path / "state")
    sh = FakeShell(hosts={"labels": ("192.0.2.1", "aaaa")}, sha={"/root/x/stamp.py": good})
    R.launch(p, sh, T0, tmp_path / "state")
    assert sh.launched == [("192.0.2.1", "demo")]


def test_check_reports_events_once_per_run_and_skips_ended_runs(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec())
    write_spec(specs, spec(name="other"))
    R.save_state("demo", run_state(), state)
    R.save_state("other", run_state(status="ended"), state)
    write_spec(specs, spec(name="never"))
    out = R.check(FakeShell(probe_out="exit=\nalive=1\nprogress=0\n"), T0 + timedelta(minutes=61), specs, state)
    assert out == ["ANOMALY run demo: no progress line since 15 Oct 18:00 (the spec allows 60 min)", "QUIET demo 0 lines, last 18:00"]
    out = R.check(FakeShell(probe_out="exit=0\nalive=0\nprogress=4\n"), T0 + timedelta(minutes=70), specs, state)
    assert out == ["MARKER run demo ended (exit 0)", "QUIET demo ended"]
    assert R.check(FakeShell(), T0, specs, state) == ["QUIET no runs"]


def test_check_reports_a_broken_spec_instead_of_crashing(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    specs.mkdir()
    (specs / "demo.json").write_text('{"name": "demo"}', encoding="utf-8")
    R.save_state("demo", run_state(), state)
    out = R.check(FakeShell(), T0, specs, state)
    assert out[0].startswith("ANOMALY run demo: the check failed: ValidationError") and out[-1] == "QUIET no runs"


# ---------------------------------------------------------------- resume after a restart (TASKS 63 (b))

def test_resumable_is_for_the_laptop():
    with pytest.raises(ValidationError, match="laptop runs"):
        spec(host="labels", workdir="/root/x", resumable=True)


def test_a_resumable_run_gets_the_resume_interval_before_it_is_reported_gone():
    s, gone = spec(resumable=True), R.Observation(alive=False)
    ev, st = R.assess(s, run_state(), gone, T0)
    assert ev == [] and st.gone_seen_at == T0
    ev, st = R.assess(s, st, gone, T0 + timedelta(minutes=30))
    assert ev == []
    ev, _ = R.assess(s, st, gone, T0 + timedelta(minutes=41))
    assert ev == ["ANOMALY run demo gone since 15 Oct 18:00 and not resumed (see probes/watch_state/resume.log)"]
    _, st = R.assess(s, st, alive(0), T0 + timedelta(minutes=45))
    assert st.gone_seen_at is None


def test_resume_relaunches_only_a_gone_resumable_laptop_run(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    for name, over in (("gone", {"resumable": True}), ("plain", {}), ("finished", {"resumable": True})):
        write_spec(specs, spec(name=name, **over))
        R.save_state(name, run_state(status="ended" if name == "finished" else "running"), state)
    sh = FakeShell(probe_out="exit=\nalive=0\nprogress=3\n")
    assert R.resume(sh, T0, specs, state, dry=True, second_look=0) == ["gone: gone without an exit file - would relaunch: python probes/demo.py"]
    assert sh.launched == []
    out = R.resume(sh, T0, specs, state, second_look=0)
    assert out[0].startswith("gone: RELAUNCHED (pid 4242, relaunch 1)") and sh.launched == [("laptop", "gone", True)]
    assert R.load_state("gone", state).relaunches == 1
    assert R.resume(FakeShell(probe_out="exit=\nalive=1\nprogress=3\n"), T0, specs, state, second_look=0) == []
    assert R.resume(FakeShell(probe_out="exit=0\nalive=0\nprogress=3\n"), T0, specs, state, second_look=0) == []


def test_the_shell_never_inherits_stdin(monkeypatch):
    """16 Oct 2026: under the scheduled task (no console) an inherited stdin handle is invalid — every call must pass stdin=DEVNULL."""
    seen = {}
    monkeypatch.setattr(R.subprocess, "run", lambda args, **kw: seen.update(kw) or subprocess.CompletedProcess(args, 0, "", ""))
    R.Shell("bash").run(R.LAPTOP, "true")
    assert seen["stdin"] is subprocess.DEVNULL


def test_a_relaunch_appends_to_the_log(monkeypatch):
    calls = []
    monkeypatch.setattr(R.Shell, "_run", lambda self, args, timeout=120, cwd=None: calls.append(args) or subprocess.CompletedProcess(args, 0, "1", ""))
    R.Shell("bash").launch_laptop(spec())
    R.Shell("bash").launch_laptop(spec(), append=True)
    assert ") > demo.log 2>&1" in calls[0][-1] and ") >> demo.log 2>&1" in calls[1][-1]


# ---------------------------------------------------------------- the memory budget and unbuffered output (19 Oct 2026)

def test_a_laptop_run_without_a_measured_peak_is_not_launched(tmp_path):
    p = write_spec(tmp_path / "specs", spec(memory=None))
    with pytest.raises(R.LaunchRefused, match="no measured peak memory"):
        R.launch(p, FakeShell(), T0, tmp_path / "state")


def test_the_budget_counts_laptop_runs_in_progress_but_not_waiting_ones_or_servers(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    big = {"peak_gb": 8.0, "basis": "peak working set of a test run"}
    write_spec(specs, spec(name="training", memory=big))
    write_spec(specs, spec(name="waiting", memory=big))
    write_spec(specs, spec(name="remote", host="labels", workdir="/root/x", memory=big))
    R.save_state("training", run_state(), state)
    R.save_state("waiting", run_state(phase_started_at=None), state)       # armed, not yet at its start line
    R.save_state("remote", run_state(), state)
    assert R.memory_problems(spec(), specs, state) == []                   # 4 + 8 = 12 <= 13
    over = R.memory_problems(spec(memory={"peak_gb": 6.0, "basis": "peak working set of a test run"}), specs, state)
    assert over == ["memory: 6 GB + 8 GB of laptop runs in progress = 14 GB > 13 GB"]


def test_a_run_in_progress_without_a_peak_blocks_the_budget(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec(name="old", memory=None))
    R.save_state("old", run_state(), state)
    assert R.memory_problems(spec(), specs, state) == ["laptop run old is in progress without a stated peak memory, so the budget cannot be checked"]


def test_resume_does_not_relaunch_past_the_budget(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec(name="gone", resumable=True, memory={"peak_gb": 10.0, "basis": "peak working set of a test run"}))
    write_spec(specs, spec(name="busy"))
    R.save_state("gone", run_state(), state)
    R.save_state("busy", run_state(), state)
    sh = FakeShell(probe_out="exit=\nalive=0\nprogress=3\n")
    out = R.resume(sh, T0, specs, state, second_look=0)
    assert out == ["gone: NOT relaunched: memory: 10 GB + 4 GB of laptop runs in progress = 14 GB > 13 GB"] and sh.launched == []


def test_python_output_is_unbuffered_on_the_laptop_and_on_a_server(monkeypatch):
    calls = []
    monkeypatch.setattr(R.Shell, "_run", lambda self, args, timeout=120, cwd=None: calls.append(args) or subprocess.CompletedProcess(args, 0, "1", ""))
    R.Shell("bash").launch_laptop(spec())
    assert "export PYTHONUNBUFFERED=1; " in calls[0][-1]
    assert 'ENVLINE="export PYTHONUNBUFFERED=1"' in (PLAN / "tools" / "remote_launch.sh").read_text(encoding="utf-8")


def test_a_new_launch_keeps_the_earlier_log(tmp_path, monkeypatch):
    monkeypatch.setattr(R, "ROOT", tmp_path)
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "demo.log").write_text("the first run's history\n", encoding="utf-8")
    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "stamp.py").write_text("x = 1\n", encoding="utf-8")
    p = write_spec(tmp_path / "specs", spec(workdir="w"))
    R.launch(p, FakeShell(), T0, tmp_path / "state")
    kept = tmp_path / "w" / f"demo.{T0:%Y%m%d-%H%M%S}.log"
    assert kept.read_text(encoding="utf-8") == "the first run's history\n" and not (tmp_path / "w" / "demo.log").exists()


def test_a_peek_leaves_the_state_and_its_one_time_events_to_the_watch(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec())
    R.save_state("demo", run_state(), state)
    ended = FakeShell(probe_out="exit=0\nalive=0\nprogress=4\n")
    assert R.check(ended, T0, specs, state, peek=True)[0] == "MARKER run demo ended (exit 0)"
    assert R.load_state("demo", state).status == "running"
    assert R.check(ended, T0, specs, state)[0] == "MARKER run demo ended (exit 0)"      # the watch still sees the end
    assert R.load_state("demo", state).status == "ended"
