"""tools/runspec.py (15 Oct 2026, TASKS 63): a run starts only with a progress contract, and the check turns a missing progress line, a
vanished process, a bad exit or an overrun into one stable event each. The decision (assess) is tested without I/O; the probe lines run in a
real bash on a scratch folder; launch and check run against a stand-in shell."""
import os
import re
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


def test_a_relaunch_that_ends_the_same_way_gets_its_own_text():
    s, obs = spec(), R.Observation(exit_code=1)
    first, _ = R.assess(s, run_state(), obs, T0 + timedelta(minutes=5))
    again, _ = R.assess(s, run_state(started_at=T0 + timedelta(minutes=30)), obs, T0 + timedelta(minutes=40))
    assert first[-1] != again[-1] and again[-1].endswith("(launched 15 Oct 18:30)")


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
    def __init__(self, hosts=None, probe_out="", rc=0, sha=None, tracked=()):
        self.hosts, self.probe_out, self.rc, self.sha = hosts or {}, probe_out, rc, sha or {}
        self.tracked_paths = set(tracked)
        self.launched = []

    def host_row(self, host):
        return self.hosts.get(host)

    def run(self, host, script, timeout=120):
        if script.startswith("bash -n"):
            return 0, ""
        if "sha256sum" in script or script.startswith("test -d"):
            return self.rc, "workdir=ok\n" + "".join(f"{h}  {p}\n" for p, h in self.sha.items())
        return self.rc, self.probe_out

    def tracked(self, paths):
        return [p for p in paths if p in self.tracked_paths]

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


def test_a_laptop_run_whose_log_git_tracks_is_not_launched(tmp_path):
    s = spec()
    sh = FakeShell(tracked={R.laptop_log(s)})
    with pytest.raises(R.LaunchRefused, match=r"log probes/demo\.log is tracked by git"):
        R.launch(write_spec(tmp_path / "specs", s), sh, T0, tmp_path / "state")
    assert sh.launched == [] and R.load_state("demo", tmp_path / "state") is None


def test_a_server_run_is_not_asked_about_its_log():
    s = spec(host="box", workdir="/root/x", sources=[{"local": "tools/stamp.py", "remote": "/root/x/stamp.py"}], memory=None)
    assert not any("tracked by git" in p for p in R.preflight(s, FakeShell(hosts={"box": ("1.2.3.4", "m")}, tracked={R.laptop_log(s)})))


def test_git_names_the_tracked_paths_only():
    if shutil.which("git") is None:
        pytest.skip("git is not on PATH")
    tracked, untracked = R.ROOT / "tools" / "runspec.py", R.ROOT / "probes" / "watch_state" / "no_such_run.log"
    assert R.Shell().tracked([tracked, untracked]) == [tracked] and R.Shell().tracked([]) == []


def test_the_logs_of_running_laptop_runs_are_listed_waiting_ones_included(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    for name in ("waiting", "ended", "never"):
        write_spec(specs, spec(name=name))
    write_spec(specs, spec(name="remote", host="box", workdir="/root/x", memory=None,
                           sources=[{"local": "tools/stamp.py", "remote": "/root/x/stamp.py"}]))
    R.save_state("waiting", run_state(phase_started_at=None), state)
    R.save_state("ended", run_state(status="ended"), state)
    R.save_state("remote", run_state(), state)
    assert R.running_laptop_logs(specs, state) == [R.ROOT / "probes" / "waiting.log"]


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
    assert out == ["MARKER run demo ended (exit 0) (launched 15 Oct 18:00)", "QUIET demo ended"]
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
    """Since 14 Nov 2026 the job writes into a pipe and one `cat` appends, so two writers cannot overwrite each other;
    a fresh launch empties the log first and the exit code comes from the job, not from cat (TASKS 214)."""
    calls = []
    monkeypatch.setattr(R.Shell, "_run", lambda self, args, timeout=120, cwd=None: calls.append(args) or subprocess.CompletedProcess(args, 0, "1", ""))
    R.Shell("bash").launch_laptop(spec())
    R.Shell("bash").launch_laptop(spec(), append=True)
    fresh, again = calls[0][-1], calls[1][-1]
    assert ") 2>&1 | cat >> demo.log" in fresh and ": > demo.log;" in fresh
    assert ") 2>&1 | cat >> demo.log" in again and ": > demo.log;" not in again
    assert "${PIPESTATUS[0]} > demo.exit" in fresh


# ---------------------------------------------------------------- the memory budget and unbuffered output (19 Oct 2026)

def test_a_laptop_run_without_a_measured_peak_is_not_launched(tmp_path):
    p = write_spec(tmp_path / "specs", spec(memory=None))
    with pytest.raises(R.LaunchRefused, match="no measured peak memory"):
        R.launch(p, FakeShell(), T0, tmp_path / "state")


@pytest.fixture(autouse=True)
def _plenty_of_free_memory(monkeypatch):
    """The measured free commit is the laptop's state; every test here reads a fixed value unless it sets its own."""
    monkeypatch.setattr(R, "measure_free_commit_gb", lambda: 100.0)


def test_a_second_run_needs_measured_room_beside_the_runs_in_progress(tmp_path, monkeypatch):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec(name="training", memory={"peak_gb": 8.0, "basis": "peak working set of a test run"}))
    R.save_state("training", run_state(), state)
    monkeypatch.setattr(R, "measure_free_commit_gb", lambda: 7.0)            # 7 - 4 = 3 < 4
    assert R.memory_problems(spec(), specs, state) == [
        "memory: 7.0 GB can be committed now; 4 GB for this run would leave 3.0 GB beside the runs in progress (< 4 GB)"]
    monkeypatch.setattr(R, "measure_free_commit_gb", lambda: 8.0)            # 8 - 4 = 4: enough
    assert R.memory_problems(spec(), specs, state) == []


def test_a_first_run_alone_is_not_held_to_the_measured_room(tmp_path, monkeypatch):
    specs, state = tmp_path / "specs", tmp_path / "state"
    monkeypatch.setattr(R, "measure_free_commit_gb", lambda: 1.0)
    assert R.memory_problems(spec(), specs, state) == []                     # nothing in progress: the stated budget alone


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


WORD = "the user, 8 Nov 2026: '1 en 2 akkoord' (TASKS 184)"


def test_a_word_is_only_for_a_peak_past_the_budget():
    assert R.Memory(peak_gb=17.0, basis="the cap wsl_capped.sh sets", budget_word=WORD).budget_word == WORD
    with pytest.raises(ValidationError, match="fits without one"):
        R.Memory(peak_gb=13.0, basis="the cap wsl_capped.sh sets", budget_word=WORD)
    with pytest.raises(ValidationError, match="at least 20"):
        R.Memory(peak_gb=17.0, basis="the cap wsl_capped.sh sets", budget_word="ok")


def test_a_run_past_the_budget_on_the_users_word_runs_alone(tmp_path, monkeypatch):
    specs, state = tmp_path / "specs", tmp_path / "state"
    big = spec(name="check", memory={"peak_gb": 17.0, "basis": "the cap wsl_capped.sh sets", "budget_word": WORD})
    assert R.memory_problems(spec(memory={"peak_gb": 17.0, "basis": "the cap wsl_capped.sh sets"}), specs, state) == [
        "memory: 17 GB + 0 GB of laptop runs in progress = 17 GB > 13 GB"]          # without the word: refused
    monkeypatch.setattr(R, "measure_free_commit_gb", lambda: 1.0)
    assert R.memory_problems(big, specs, state) == []                                # alone: the stated cap is its bound
    write_spec(specs, spec(name="training"))
    R.save_state("training", run_state(), state)
    assert R.memory_problems(big, specs, state) == [
        "memory: 17 GB passes the 13 GB budget on the user's word and so runs alone; 4 GB of laptop runs are in progress"]


def test_every_other_laptop_run_waits_for_the_run_past_the_budget(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec(name="check", memory={"peak_gb": 17.0, "basis": "the cap wsl_capped.sh sets", "budget_word": WORD}))
    R.save_state("check", run_state(), state)
    assert R.memory_problems(spec(), specs, state) == ["memory: 4 GB + 17 GB of laptop runs in progress = 21 GB > 13 GB"]


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
    assert R.check(ended, T0, specs, state, peek=True)[0] == "MARKER run demo ended (exit 0) (launched 15 Oct 18:00)"
    assert R.load_state("demo", state).status == "running"
    assert R.check(ended, T0, specs, state)[0] == "MARKER run demo ended (exit 0) (launched 15 Oct 18:00)"   # the watch still sees it
    assert R.load_state("demo", state).status == "ended"


# ---------------------------------------------------------------- an interrupted run is resumed (TASKS 83, 25 Oct 2026)

def resumable_spec(**over) -> R.RunSpec:
    return spec(**({"resumable": True, "end_regex": "^=== \\(T\\) run done", "fail_regex": "^=== \\(T\\) RUN FAILED"} | over))


@pytest.mark.parametrize("over, words", [
    ({"resumable": False}, "needs a resumable run with an end_regex"),
    ({"end_regex": None}, "needs a resumable run with an end_regex"),
    ({"fail_regex": r"failed \d"}, "not POSIX ERE"),
])
def test_fail_regex_refusals(over, words):
    with pytest.raises(ValidationError, match=words):
        resumable_spec(**over)


@pytest.mark.parametrize("obs, expect", [
    (R.Observation(exit_code=4, lived_s=3600), True),                         # a restart killed it after its wrapper wrote the exit file
    (R.Observation(exit_code=4, lived_s=30), False),                          # died at once: a start-up failure, not a restart
    (R.Observation(exit_code=1, lived_s=3600, failed_marker=True), False),    # failed on its own and said so
    (R.Observation(exit_code=4, lived_s=3600, ended_marker=True), False),     # its end line is there: an exit code to read, not a kill
    (R.Observation(exit_code=0, lived_s=3600), False),
    (R.Observation(exit_code=4), False),                                      # no lifetime known
])
def test_what_counts_as_interrupted(obs, expect):
    assert R.interrupted(resumable_spec(), obs) is expect


def test_without_fail_regex_a_bad_exit_stays_an_ending():
    assert not R.interrupted(spec(resumable=True), R.Observation(exit_code=4, lived_s=3600))


def test_an_interrupted_run_gets_the_resume_grace_and_is_not_ended():
    s, obs = resumable_spec(), R.Observation(exit_code=4, lived_s=3600)
    ev, st = R.assess(s, run_state(), obs, T0)
    assert ev == [] and st.status == "running" and st.gone_seen_at == T0
    ev, st = R.assess(s, st, obs, T0 + timedelta(minutes=41))
    assert ev == ["ANOMALY run demo gone since 15 Oct 18:00 and not resumed (see probes/watch_state/resume.log)"] and st.status == "running"
    ev, st = R.assess(s, run_state(), R.Observation(exit_code=1, lived_s=3600, failed_marker=True), T0)
    assert ev == ["ANOMALY run demo ended with exit 1 (launched 15 Oct 18:00)"] and st.status == "ended"


def test_resume_relaunches_an_interrupted_run_and_names_why(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, resumable_spec(name="killed"))
    R.save_state("killed", run_state(), state)
    sh = FakeShell(probe_out="exit=4\nalive=0\nprogress=3\nlived=3600\n")
    out = R.resume(sh, T0, specs, state, second_look=0)
    assert out == ["killed: RELAUNCHED (pid 4242, relaunch 1): python probes/demo.py - "
                   "interrupted (exit 4 without its end or failure line, after 3600 s)"] and sh.launched == [("laptop", "killed", True)]
    assert R.resume(FakeShell(probe_out="exit=1\nalive=0\nprogress=3\nlived=3600\nfailed=1\n"), T0, specs, state, second_look=0) == []
    assert R.resume(FakeShell(probe_out="exit=4\nalive=0\nprogress=3\nlived=20\n"), T0, specs, state, second_look=0) == []


@pytest.mark.skipif(BASH is None, reason="bash not available")
def test_shell_output_is_read_as_utf8(tmp_path):
    (tmp_path / "say.sh").write_bytes("printf 'φ cm⁻¹'\n".encode())
    assert R.Shell(BASH)._run([BASH, (tmp_path / "say.sh").as_posix()]).stdout == "φ cm⁻¹"


@pytest.mark.skipif(BASH is None, reason="bash not available")
def test_the_probe_reads_the_failure_line_and_the_lifetime(tmp_path):
    s = resumable_spec(workdir="probes")
    (tmp_path / "demo.log").write_text("=== (T) armed\n=== (T) RUN FAILED at train: exit 3\n", encoding="utf-8", newline="\n")
    for name, mtime in (("demo.pid", 1_000_000), ("demo.exit", 1_000_900)):
        (tmp_path / name).write_text("1\n", encoding="utf-8")
        os.utime(tmp_path / name, (mtime, mtime))
    script = R.probe_script(s).replace("cd probes", f"cd {tmp_path.as_posix()}", 1)
    out = subprocess.run([BASH, "-c", script], capture_output=True, text=True, check=True).stdout
    obs = R.parse_probe(s, out)
    assert obs.failed_marker and obs.lived_s == 900 and obs.exit_code == 1
# ---------------------------------------------------------------- stop: a deliberate stop holds the run until a fresh launch (TASKS 251)

class StopShell(FakeShell):
    """The stand-in for the stop's three steps: the kill where the run lives, the WSL sweep, the stop line and exit file."""

    def __init__(self, probe_out="exit=\nalive=1\nprogress=0\n", kill_out="was_alive=1\nalive=0\n", wsl_out="wsl=off\nwsl_left=0\n",
                 recorded="recorded=1\n"):
        super().__init__(probe_out=probe_out)
        self.kill_out, self.wsl_out, self.recorded = kill_out, wsl_out, recorded
        self.scripts = []

    def run(self, host, script, timeout=120):
        self.scripts.append(script)
        for word, out in (("was_alive", self.kill_out), ("wsl.exe", self.wsl_out), ("recorded=1", self.recorded)):
            if word in script:
                return 0, out
        return super().run(host, script, timeout)


def test_a_stop_holds_the_run_until_a_fresh_launch(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec(resumable=True))
    sh = StopShell()
    R.launch(p, sh, T0, state)
    line = R.stop(p, sh, T0 + timedelta(hours=2), state, reason="room for v14_data")
    assert line == "=== runspec stop: demo stopped by hand 2026-10-15 20:00:00, exit 143: room for v14_data"
    assert any(R.shlex.quote(line) in s and "echo 143 > demo.exit" in s for s in sh.scripts)
    st = R.load_state("demo", state)
    assert st.status == "stopped" and st.stopped_at == T0 + timedelta(hours=2)
    marker = "MARKER run demo stopped by hand 15 Oct 20:00 (launched 15 Oct 18:00)"
    assert R.check(sh, T0 + timedelta(hours=3), specs, state, peek=True) == [marker, "QUIET demo stopped"]   # a peek leaves it for the watch
    assert R.check(sh, T0 + timedelta(hours=3), specs, state) == [marker, "QUIET demo stopped"]
    assert R.check(sh, T0 + timedelta(hours=4), specs, state) == ["QUIET no runs"]                            # reported once
    gone = StopShell(probe_out="exit=\nalive=0\nprogress=0\n")
    assert R.resume(gone, T0, specs, state, second_look=0) == [] and gone.launched == []
    assert R.laptop_runs_in_progress("other", specs, state) == (0.0, []) and R.running_laptop_logs(specs, state) == []
    R.launch(p, sh, T0 + timedelta(hours=5), state)
    assert R.load_state("demo", state).status == "running" and sh.launched[-1] == ("laptop", "demo", False)


def test_a_server_stop_ends_the_process_group_and_sweeps_no_wsl(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec(host="labels", workdir="/root/x", memory=None))
    R.save_state("demo", run_state(), state)
    sh = StopShell()
    sh.hosts = {"labels": ("1.2.3.4", "m-id")}
    R.stop(p, sh, T0, state)
    kill = next(s for s in sh.scripts if "was_alive" in s)
    assert 'kill -TERM -- -"$p"' in kill and 'kill -KILL -- -"$p"' in kill and "taskkill" not in kill
    assert "/proc/\"$p\"/cmdline" in kill and "grep -qE 'demo\\.cmd\\.sh'" in kill          # remote_launch.sh's wrapper of this run
    assert not any("wsl.exe" in s for s in sh.scripts)


def test_a_laptop_stop_kills_the_windows_tree_then_the_tagged_wsl_processes(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec())
    R.save_state("demo", run_state(), state)
    sh = StopShell()
    R.stop(p, sh, T0, state)
    kill, wsl = next(s for s in sh.scripts if "was_alive" in s), next(s for s in sh.scripts if "wsl.exe" in s)
    assert sh.scripts.index(kill) < sh.scripts.index(wsl)
    assert 'taskkill /PID "$w" /T /F' in kill and "/proc/\"$p\"/winpid" in kill
    assert "/proc/\"$p\"/cmdline" in kill and "grep -qE 'launch[\\\\/]demo_'" in kill      # only this run's own wrapper is killed
    assert "RUNSPEC_RUN=demo" in wsl and "--list --running" in wsl


@pytest.mark.parametrize("make, words", [
    (lambda: StopShell(probe_out="exit=0\nalive=0\nprogress=3\n"), "ended by itself (exit 0)"),          # its own exit code stays the record
    (lambda: StopShell(probe_out=""), "cannot be read"),
])
def test_a_run_that_cannot_be_stopped_stays_running(tmp_path, make, words):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec())
    R.save_state("demo", run_state(), state)
    with pytest.raises(R.StopRefused, match=re.escape(words)):
        R.stop(p, make(), T0, state)
    assert R.load_state("demo", state) == run_state()


@pytest.mark.parametrize("make, words", [
    (lambda: StopShell(kill_out="was_alive=1\nalive=1\n"), "still alive after the kill"),
    (lambda: StopShell(wsl_out="wsl_tagged=2\nwsl_left=1\n"), "RUNSPEC_RUN=demo left: 1"),
    (lambda: StopShell(wsl_out=""), "left: unknown"),                                                      # no answer is not 'none left'
    (lambda: StopShell(recorded=""), "could not be written"),
])
def test_a_stop_that_does_not_finish_holds_the_run_and_is_reported(tmp_path, make, words):
    """Held from resume (a relaunch beside what is left would double it), refused by launch, an anomaly once stale, and stop again
    finishes it - also when the first try had written the exit file already."""
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec(resumable=True))
    R.save_state("demo", run_state(), state)
    with pytest.raises(R.StopRefused, match=re.escape(words)):
        R.stop(p, make(), T0, state)
    assert R.load_state("demo", state) == run_state(status="stopping", stopped_at=T0)
    assert R.laptop_runs_in_progress("other", specs, state) == (4.0, [])                    # what is left still holds its memory
    assert R.running_laptop_logs(specs, state) == [R.laptop_log(spec(resumable=True))]      # and its log
    gone = StopShell(probe_out="exit=\nalive=0\nprogress=0\n")
    assert R.resume(gone, T0, specs, state, second_look=0) == [] and gone.launched == []
    with pytest.raises(R.LaunchRefused, match="did not finish"):
        R.launch(p, gone, T0, state)
    assert R.check(gone, T0 + timedelta(minutes=10), specs, state) == ["QUIET demo stopping"]
    stale = "ANOMALY run demo: a stop began 15 Oct 18:00 and did not finish - `runspec.py stop` it again"
    assert R.check(gone, T0 + timedelta(minutes=16), specs, state) == [stale, "QUIET demo stopping"]
    R.stop(p, StopShell(probe_out="exit=143\nalive=0\nprogress=0\n"), T0 + timedelta(minutes=20), state)
    assert R.load_state("demo", state).status == "stopped"


def test_a_stop_of_a_run_that_had_gone_says_so(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec(resumable=True))
    R.save_state("demo", run_state(), state)
    out = R.stop(p, StopShell(probe_out="exit=\nalive=0\nprogress=0\n", kill_out="was_alive=0\nalive=0\n"), T0, state)
    assert out.endswith("(no process of it was alive: the stop holds a run that had gone)")


def test_only_a_running_run_is_stopped(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec())
    with pytest.raises(R.StopRefused, match="not running \\(never launched\\)"):
        R.stop(p, StopShell(), T0, state)
    for status in ("ended", "stopped"):
        R.save_state("demo", run_state(status=status), state)
        with pytest.raises(R.StopRefused, match=f"not running \\({status}\\)"):
            R.stop(p, StopShell(), T0, state)


def test_a_stop_while_the_check_or_the_resume_looks_wins(tmp_path):
    """The stop takes seconds; a check or a resume that loaded the state before it saves nothing and relaunches nothing."""
    specs, state = tmp_path / "specs", tmp_path / "state"
    write_spec(specs, spec(resumable=True))

    class StoppedDuringTheLook(FakeShell):
        def run(self, host, script, timeout=120):
            R.save_state("demo", run_state(status="stopping"), state)
            return 0, self.probe_out

    R.save_state("demo", run_state(), state)
    assert R.check(StoppedDuringTheLook(probe_out="exit=143\nalive=0\nprogress=0\n"), T0, specs, state) == ["QUIET no runs"]
    assert R.load_state("demo", state).status == "stopping"
    R.save_state("demo", run_state(), state)
    sh = StoppedDuringTheLook(probe_out="exit=\nalive=0\nprogress=0\n")
    assert R.resume(sh, T0, specs, state, second_look=0) == [] and sh.launched == []


def test_the_laptop_launch_tags_every_process_for_the_stop(monkeypatch):
    calls = []
    monkeypatch.setattr(R.Shell, "_run", lambda self, args, timeout=120, cwd=None: calls.append(args) or subprocess.CompletedProcess(args, 0, "1", ""))
    R.Shell("bash").launch_laptop(spec())
    assert 'export RUNSPEC_RUN=demo WSLENV="${WSLENV:+$WSLENV:}RUNSPEC_RUN"; ' in calls[0][-1]


def test_the_stop_line_names_the_run_the_time_and_the_reason():
    assert R.stop_line(spec(), T0, "x") == "=== runspec stop: demo stopped by hand 2026-10-15 18:00:00, exit 143: x"
    assert R.stop_line(spec(), T0, "") == "=== runspec stop: demo stopped by hand 2026-10-15 18:00:00, exit 143"


# ---------------------------------------------------------------- stop on the real machine: a WMI launch, a tree, WSL

def _windows_pid_alive(pid: int) -> bool:
    out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH", "/FO", "CSV"], capture_output=True, text=True, check=True).stdout
    return f'"{pid}"' in out


def _wait_for(predicate, seconds=60):
    deadline = R.time.monotonic() + seconds
    while R.time.monotonic() < deadline:
        if predicate():
            return True
        R.time.sleep(0.5)
    return False


class _NoGitShell(R.Shell):
    def tracked(self, paths):
        return []                                  # the scratch folder is outside the repository


SLEEPER = """import subprocess, sys, time
from pathlib import Path
child = subprocess.Popen([sys.executable, "-c", "import time\\nwhile True: time.sleep(1)"])
Path("child.pid").write_text(str(child.pid))
while True:
    print("  progress tick", flush=True)
    time.sleep(1)
"""

real_windows = pytest.mark.skipif(sys.platform != "win32" or BASH is None, reason="the laptop's stop: Git Bash, WMI and taskkill")


@pytest.fixture
def real_run(tmp_path, monkeypatch):
    """A scratch plan folder for real launches; the launch wrappers this test leaves in probes/watch_state/launch are removed after it."""
    monkeypatch.setattr(R, "ROOT", tmp_path)
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "sleeper.py").write_text(SLEEPER, encoding="utf-8")
    name = f"stoptest_{os.getpid()}"
    yield tmp_path, name
    left = spec(name=name, workdir="w")                    # a test that failed half-way leaves no processes behind
    R.Shell().run(R.LAPTOP, R.kill_script(left))
    R.Shell().run(R.LAPTOP, R.wsl_stop_script(name))
    for wrapper in (PLAN / "probes" / "watch_state" / "launch").glob(f"{name}_*.sh"):
        wrapper.unlink()


@real_windows
def test_stop_ends_a_real_laptop_tree_and_a_launch_arms_it_again(real_run):
    root, name = real_run
    specs, state = root / "specs", root / "state"
    p = write_spec(specs, spec(name=name, workdir="w", command="python sleeper.py", sources=[{"local": "w/sleeper.py"}], resumable=True))
    sh = _NoGitShell()
    for launch in (1, 2):
        R.launch(p, sh, R._now(), state)
        assert _wait_for(lambda: (root / "w" / "child.pid").exists() and "progress tick" in (root / "w" / f"{name}.log").read_text())
        child = int((root / "w" / "child.pid").read_text())
        bash_pid = (root / "w" / f"{name}.pid").read_text().strip()
        line = R.stop(p, sh, R._now(), state, reason=f"test stop {launch}").splitlines()[0]     # a note on WSL may follow it
        assert not _windows_pid_alive(child)                                   # the tree, not only the wrapper
        assert subprocess.run([BASH, "-c", f"kill -0 {bash_pid}"], check=False).returncode != 0
        assert (root / "w" / f"{name}.exit").read_text().strip() == "143"
        assert (root / "w" / f"{name}.log").read_text().splitlines()[-1] == line
        assert R.load_state(name, state).status == "stopped"
        assert R.check(sh, R._now(), specs, state, peek=True)[0].startswith(f"MARKER run {name} stopped by hand ")
        assert R.resume(sh, R._now(), specs, state, second_look=0) == []
        (root / "w" / "child.pid").unlink()
        R.time.sleep(1.1)                                                      # the next launch keeps this log under another second


def _wsl_running() -> bool:
    if sys.platform != "win32" or shutil.which("wsl.exe") is None:
        return False
    out = subprocess.run(["wsl.exe", "--list", "--running", "--quiet"], capture_output=True, check=False).stdout
    return bool(out.replace(b"\0", b"").strip())


def _wsl_tagged(name: str) -> int:
    script = f"grep -la 'RUNSPEC_RUN={name}' /proc/[0-9]*/environ 2>/dev/null | wc -l"
    return int(subprocess.run(["wsl.exe", "-e", "sh", "-c", script], capture_output=True, text=True, check=True).stdout.strip())


@pytest.mark.skipif(not _wsl_running(), reason="a running WSL (this test does not start one)")
def test_stop_ends_the_wsl_processes_of_a_real_laptop_run(real_run):
    root, name = real_run
    specs, state = root / "specs", root / "state"
    p = write_spec(specs, spec(name=name, workdir="w", command="wsl.exe -e sh -c 'sleep 600 & sleep 600'", sources=[{"local": "w/sleeper.py"}]))
    sh = _NoGitShell()
    R.launch(p, sh, R._now(), state)
    assert _wait_for(lambda: _wsl_tagged(name) >= 2)                          # the sh and its two sleeps carry the tag
    R.stop(p, sh, R._now(), state)
    assert _wsl_tagged(name) == 0
    assert R.load_state(name, state).status == "stopped"
# ---------------------------------------------------------------- the review of the stop (19 Nov 2026)

def test_the_state_of_a_run_nobody_stopped_keeps_the_keys_of_the_reader_before_the_stop():
    """The watch's check rewrites a live run's state file; after a rollback the earlier reader (`cls(**raw)`) must still load it."""
    before_the_stop = {"started_at", "status", "phase_started_at", "progress_count", "progress_seen_at", "heartbeat_bytes", "unreachable",
                       "gone_seen_at", "relaunches"}
    assert set(R.json.loads(run_state(progress_count=3).to_json())) == before_the_stop
    stopped = run_state(status="stopped", stopped_at=T0, stop_reported=True)
    assert set(R.json.loads(stopped.to_json())) == before_the_stop | {"stopped_at", "stop_reported"}
    assert R.RunState.from_json(stopped.to_json()) == stopped


@pytest.mark.parametrize("wsl_out, note", [
    ("wsl=off\nwsl_left=0\n", None),
    ("wsl_tagged=3\nwsl_left=0\n", None),
    ("wsl_tagged=0\nwsl_left=0\n", "cannot be swept"),                  # WSL runs, nothing tagged: a run from before the tag?
])
def test_a_stop_says_when_it_could_not_have_seen_the_runs_wsl_processes(tmp_path, wsl_out, note):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec())
    R.save_state("demo", run_state(), state)
    out = R.stop(p, StopShell(wsl_out=wsl_out), T0, state)
    assert ("cannot be swept" in out) is (note is not None) and R.load_state("demo", state).status == "stopped"


def test_a_stale_pid_is_named_and_not_killed(tmp_path):
    specs, state = tmp_path / "specs", tmp_path / "state"
    p = write_spec(specs, spec())
    R.save_state("demo", run_state(), state)
    out = R.stop(p, StopShell(kill_out="stale_pid=4711\nwas_alive=0\nalive=0\n"), T0, state)
    assert "process 4711 of demo.pid is not this run's launch wrapper and was left alone" in out
    assert "no process of it was alive" in out


@real_windows
def test_a_pid_file_naming_an_unrelated_live_process_kills_nothing(real_run):
    """After a restart Git Bash numbers its processes anew: the pid in an old pid file can be anyone's. Here it is a bystander's."""
    root, name = real_run
    specs, state = root / "specs", root / "state"
    p = write_spec(specs, spec(name=name, workdir="w", command="python sleeper.py", sources=[{"local": "w/sleeper.py"}]))
    bystander = subprocess.Popen([BASH, "-c", "echo $$ > bystander.pid; sleep 120; true"], cwd=root / "w")
    pid = ""
    try:
        assert _wait_for(lambda: (root / "w" / "bystander.pid").exists() and (root / "w" / "bystander.pid").read_text().strip())
        pid = (root / "w" / "bystander.pid").read_text().strip()
        (root / "w" / f"{name}.pid").write_text(pid + "\n", encoding="utf-8")
        R.save_state(name, run_state(), state)
        out = R.stop(p, _NoGitShell(), R._now(), state)
        assert f"process {pid} of {name}.pid is not this run's launch wrapper and was left alone" in out
        assert subprocess.run([BASH, "-c", f"kill -0 {pid}"], check=False).returncode == 0 and bystander.poll() is None
        assert R.load_state(name, state).status == "stopped" and (root / "w" / f"{name}.exit").read_text().strip() == "143"
    finally:
        if pid:
            subprocess.run([BASH, "-c", f"kill $(ps -ef | awk '$3 == {pid} {{print $2}}') {pid}"], check=False, capture_output=True)
        else:
            bystander.kill()
        bystander.wait(timeout=30)
