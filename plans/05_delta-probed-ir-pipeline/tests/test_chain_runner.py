"""probes/chain_runner.py (TASKS 41, 10 Oct 2026): a run is a JSON spec. The standard rung C chain registers all checkpoints of a run in one call, reads
on the frozen hold-out (b) and keeps everything in module 05's folder; commands never see the runner's stdin; a failing step or a missing declared
output fails the run with a marker; wait conditions on markers and on result files."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import chain_runner as CR  # noqa: E402


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
