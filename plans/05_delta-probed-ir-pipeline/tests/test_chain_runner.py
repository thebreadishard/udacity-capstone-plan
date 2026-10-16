"""probes/chain_runner.py (TASKS 41, 10 Oct 2026): a run is a JSON spec. The standard rung C chain registers all checkpoints of a run in one call, reads
on the frozen hold-out (b) and keeps everything in module 05's folder; commands never see the runner's stdin; a failing step or a missing declared
output fails the run with a marker; wait conditions on markers and on result files."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import chain_runner as CR


def test_rungc_expansion_registers_once_and_reads_frozen_b():
    spec = {"kind": "rungc", "chain": "40", "note": "test", "date": "2026-10-13",
            "trainings": [{"prefix": "out/A", "args": ["--sizes", "all"]}, {"prefix": "out/B", "args": ["--sizes", "853"]}]}
    steps = CR.rungc_steps(spec, "py")
    labels = [s["label"] for s in steps]
    assert labels[0] == "design check" and labels[1:3] == ["train A", "train B"]
    reg = [s for s in steps if s["label"] == "register candidates"]
    assert len(reg) == 1 and labels.index("register candidates") == 3        # after every training, before any eval
    assert sum(a.endswith(".pt") for a in reg[0]["argv"]) == 6                # 2 trainings × 3 seeds in one call
    train = steps[1]["argv"]
    assert "--save-model" in train and "--sizes" in train and CR.RECIPE_V11[0] in train and "--seeds" in train
    evals = [s for s in steps if s["label"].startswith("eval")]
    assert len(evals) == 6 and all(CR.HOLDOUT_B in s["argv"] for s in evals)
    assert all(Path(s["cwd"]) == CR.M05 and Path(s["log"]).is_absolute() for s in steps)


def test_results_condition(tmp_path):
    (tmp_path / "list.txt").write_text("a\nb\nc\n", encoding="utf-8")
    c = {"kind": "results", "list": str(tmp_path / "list.txt"), "first": 2, "dir": str(tmp_path / "mol")}
    assert not CR.condition_holds(c)
    for i in ("a", "b"):
        (tmp_path / "mol" / i).mkdir(parents=True)
        (tmp_path / "mol" / i / "result.json").write_text("{}", encoding="utf-8")
    assert CR.condition_holds(c)


@pytest.fixture(autouse=True)
def _state_in_tmp(tmp_path, monkeypatch):
    """Resume records go to the test's own folder, never the repository's watch_state."""
    monkeypatch.setattr(CR, "STATE_DIR", tmp_path / "chain_state")


def _spec(tmp: Path, steps: list[dict], outputs: list[str]) -> Path:
    (tmp / "gate.log").write_text("=== (X) ready\n", encoding="utf-8")
    spec = {"name": "T", "wait": [{"kind": "marker", "log": str(tmp / "gate.log"), "regex": r"^=== \(X\) ready"}], "steps": steps, "outputs": outputs}
    p = tmp / "spec.json"
    p.write_text(json.dumps(spec), encoding="utf-8")
    return p


def _cmd(tmp: Path, code: str, name: str) -> dict:
    return {"kind": "cmd", "label": name, "argv": [sys.executable, "-c", code], "cwd": str(tmp), "log": str(tmp / f"{name}.log")}


def test_run_done_failed_step_and_missing_output(tmp_path, capsys):
    out = tmp_path / "result.txt"
    reads_stdin = f"import sys; data = sys.stdin.read(); open(r'{out}', 'w').write('ok' + data)"   # stdin must be empty, never the runner's
    assert CR.main([str(_spec(tmp_path, [_cmd(tmp_path, reads_stdin, "write")], [str(out)]))]) == 0
    assert "run done" in capsys.readouterr().out and out.read_text() == "ok"
    assert CR.main([str(_spec(tmp_path, [_cmd(tmp_path, "import sys; sys.exit(3)", "boom"), _cmd(tmp_path, "pass", "never")], []))]) == 1
    o = capsys.readouterr().out
    assert "RUN FAILED at boom: exit 3" in o and "never done" not in o
    assert CR.main([str(_spec(tmp_path, [_cmd(tmp_path, "pass", "noop")], [str(tmp_path / "absent.json")]))]) == 1
    assert "declared outputs missing" in capsys.readouterr().out


def test_checkpoint_glob_must_match_exactly_one(tmp_path):
    (tmp_path / "x_model_n10_seed0.pt").write_text("", encoding="utf-8")
    assert CR._resolve(["x_model_n*_seed0.pt"], tmp_path) == ["x_model_n10_seed0.pt"]
    (tmp_path / "x_model_n20_seed0.pt").write_text("", encoding="utf-8")
    with pytest.raises(RuntimeError, match="matches 2 files"):
        CR._resolve(["x_model_n*_seed0.pt"], tmp_path)


def test_fd_labels_train_without_analytic_and_eval_stays_analytic():
    """Chain 35's half read (11 Oct 2026): one pool, analytic against FD training labels; the yardstick (evaluation) is analytic for both."""
    spec = {"kind": "rungc", "chain": "35h", "note": "t", "date": "2026-10-13",
            "trainings": [{"prefix": "out/A", "args": []}, {"prefix": "out/F", "args": [], "labels": "fd"}]}
    steps = {s["label"]: s["argv"] for s in CR.rungc_steps(spec, "py")}
    assert "--use-analytic" in steps["train A"] and "--use-analytic" not in steps["train F"]
    assert all("--use-analytic" in a for k, a in steps.items() if k.startswith("eval"))
    with pytest.raises(ValueError, match="labels must be"):
        CR.rungc_steps({**spec, "trainings": [{"prefix": "out/X", "labels": "psi4"}]}, "py")


def test_cmd_condition_holds_on_exit_zero(tmp_path):
    assert CR.condition_holds({"kind": "cmd", "argv": [sys.executable, "-c", "pass"], "cwd": str(tmp_path)})
    assert not CR.condition_holds({"kind": "cmd", "argv": [sys.executable, "-c", "import sys; sys.exit(1)"], "cwd": str(tmp_path)})
    assert not CR.condition_holds({"kind": "cmd", "argv": ["no-such-program-xyz"], "cwd": str(tmp_path)})
    with pytest.raises(ValueError, match="unknown wait kind"):
        CR.condition_holds({"kind": "tea"})


def test_eval_args_reach_every_eval():
    """Chain 42 (12 Oct 2026): the size-test ids go to every rungC_eval_saved call; the trainings do not see them."""
    spec = {"kind": "rungc", "chain": "42", "note": "t", "date": "2026-10-13", "eval_args": ["--eval-ids-file", "T=corpus/t.txt"],
            "trainings": [{"prefix": "out/A", "args": []}, {"prefix": "out/D", "args": ["--pool-layers", "A,A2,B,D"]}]}
    steps = {s["label"]: s["argv"] for s in CR.rungc_steps(spec, "py")}
    evals = [a for k, a in steps.items() if k.startswith("eval")]
    assert len(evals) == 6 and all(a[-2:] == ["--eval-ids-file", "T=corpus/t.txt"] for a in evals)
    assert "--eval-ids-file" not in steps["train D"] and steps["train D"][-3:-1] == ["--pool-layers", "A,A2,B,D"]


def test_a_training_s_own_eval_args_replace_the_spec_s():
    """Chain 41 (13 Oct 2026): the size arm reads s5 and s4N, each control fold only its own test list."""
    spec = {"kind": "rungc", "chain": "41", "note": "t", "date": "2026-10-13", "eval_args": ["--eval-ids-file", "s5=all.txt"],
            "trainings": [{"prefix": "out/S", "args": []}, {"prefix": "out/K1", "args": [], "eval_args": ["--eval-ids-file", "s5=fold1.txt"]}]}
    steps = {s["label"]: s["argv"] for s in CR.rungc_steps(spec, "py")}
    assert steps["eval S seed 0"][-2:] == ["--eval-ids-file", "s5=all.txt"]
    assert steps["eval K1 seed 0"][-2:] == ["--eval-ids-file", "s5=fold1.txt"] and "s5=all.txt" not in steps["eval K1 seed 0"]


def test_a_relaunch_skips_the_steps_an_earlier_run_finished(tmp_path, capsys):
    """13 Oct 2026: a chain killed after its first step (an app or Windows restart) resumes at the second; the first does not run again."""
    count = tmp_path / "count.txt"
    bump = f"import pathlib; p = pathlib.Path(r'{count}'); p.write_text(str(int(p.read_text()) + 1) if p.exists() else '1')"
    flag = tmp_path / "second_may_pass"
    second = f"import pathlib, sys; sys.exit(0 if pathlib.Path(r'{flag}').exists() else 5)"
    spec = _spec(tmp_path, [_cmd(tmp_path, bump, "first"), _cmd(tmp_path, second, "second")], [])
    assert CR.main([str(spec)]) == 1 and count.read_text() == "1"                 # the 'kill': the run stops after the first step
    flag.write_text("")
    assert CR.main([str(spec)]) == 0
    out = capsys.readouterr().out
    assert count.read_text() == "1" and "first skipped: done in an earlier run" in out and "resuming: 1 of 2" in out
    assert CR.main([str(spec), "--fresh"]) == 0 and count.read_text() == "2"      # --fresh runs everything again


def test_a_changed_spec_does_not_reuse_the_record(tmp_path, capsys):
    count = tmp_path / "count.txt"
    bump = f"import pathlib; p = pathlib.Path(r'{count}'); p.write_text(str(int(p.read_text()) + 1) if p.exists() else '1')"
    assert CR.main([str(_spec(tmp_path, [_cmd(tmp_path, bump, "first")], []))]) == 0
    assert CR.main([str(_spec(tmp_path, [_cmd(tmp_path, bump + "  # changed", "first")], []))]) == 0
    assert count.read_text() == "2" and "the spec changed" in capsys.readouterr().out


def test_a_running_step_reports_progress_only_while_its_log_grows(tmp_path, capsys, monkeypatch):
    """15 Oct 2026 (TASKS 63): the progress marker is the line a run spec's contract counts; a step whose log stands still prints none."""
    monkeypatch.setattr(CR, "PROGRESS_S", 0.3)
    grows = "import time\nfor i in range(4):\n    print(i, flush=True); time.sleep(0.4)\n"
    still = "import time\ntime.sleep(1.5)\n"
    for label, code in (("grows", grows), ("still", still)):
        CR.run_step(dict(label=label, argv=[sys.executable, "-c", code], cwd=str(tmp_path), log=str(tmp_path / f"{label}.log")), dict(os.environ),
                   "T", "1/1")
    out = capsys.readouterr().out
    assert "=== (T) progress: grows (1/1) running" in out and "progress: still" not in out


def test_a_failing_step_still_raises_with_its_exit_code(tmp_path):
    with pytest.raises(RuntimeError, match="exit 3"):
        CR.run_step(dict(label="x", argv=[sys.executable, "-c", "raise SystemExit(3)"], cwd=str(tmp_path), log=str(tmp_path / "x.log")),
                   dict(os.environ), "T", "1/1")


def test_a_rungc_step_without_a_date_is_refused():
    """16 Oct 2026: the date named the step logs; taken from the clock, it changed the resume hash on every new day."""
    with pytest.raises(ValueError, match="no 'date'"):
        CR.rungc_steps({"kind": "rungc", "chain": "x", "note": "t", "trainings": [{"prefix": "out/X"}]}, "py")


def test_every_chain_spec_in_the_repository_has_its_dates():
    for path in sorted((Path(__file__).resolve().parents[1] / "probes" / "runs").glob("chain*.json")):
        spec = json.loads(path.read_text(encoding="utf-8"))
        assert all(st.get("date") for st in spec["steps"] if st["kind"] == "rungc"), path.name


def end_marker_waits(spec: dict) -> set[str]:
    """The chains whose end marker a spec waits for: their log names without '.log'."""
    return {Path(w["log"]).stem for w in spec.get("wait", []) if w["kind"] == "marker" and "run done|RUN FAILED" in w["regex"]}


def test_the_target_comparison_runs_before_the_size_tests():
    """16 Oct 2026 (the user: 'Ja, doe punt 1 maar'): chain 44 may change the carried recipe the size tests train, so chain 41 (and through it
    42) waits for chain 44's end, and chain 44 waits for chain 35h and the gate line written after the merged labels are reviewed."""
    runs = Path(__file__).resolve().parents[1] / "probes" / "runs"
    c41, c42, c44 = (json.loads((runs / f"chain{n}.json").read_text(encoding="utf-8")) for n in (41, 42, 44))
    assert "chain44" in end_marker_waits(c41) and "chain41" in end_marker_waits(c42)
    assert "chain35h" in end_marker_waits(c44)
    assert any(w["kind"] == "marker" and w["log"].endswith("chain44_gate.log") for w in c44["wait"])
