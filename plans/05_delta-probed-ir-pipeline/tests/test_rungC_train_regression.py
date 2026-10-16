"""Regression pin of the rung-C trainer (TASKS 72): small runs on a frozen corpus must give the same record and the same saved model to the
bit. The pins are written by the trainer as it stood before the refactor (master 95291f4b, 16 Oct 2026), on the frozen corpus.

The corpus is `tests/data/rungC_pin_corpus/` (built by `tests/data/make_rungC_pin_corpus.py`: 27 molecules, only the files the trainer reads,
a sha256 per file), so the pin reads the same bytes on every machine. Bit-identity of the training itself holds only in the environment the
pin was written in (platform, Python, torch, numpy, geomeTRIC, recorded in the golden): elsewhere the pin skips in CI and fails locally,
so an upgrade cannot switch the guard off unnoticed. It first ran on the live corpus, whose pool and class
scales moved when chain 40 merged 64 molecules into it (16 Oct 11:32): red without a code change, a pin that could not tell drift from a
regression. A changed or added file in the frozen corpus now fails as such, before any training.

Two cases, both the carried recipe exactly as `chain_runner` passes it (with `--save-model`, as every chain trains), cut to mechanics size
by `--smoke` (5 pool molecules, seed 0, hold-outs cut to 3): 'carried' as it is (3 epochs); 'chainlike' with the switches the queued chains
add — an excluded-ids file (chains 41, 43), a size hold-out (chain 42; at the frozen set's own scale) and the kfit target (chain 44) —
2 epochs. Each runs in a fresh single-threaded process: two runs with two torch threads differed by up to 1.4e-6 relative (float32
reductions), and the BLAS thread counts must be set before numpy is imported. Wall-clock fields, provenance and the run's own temporary
paths are dropped; everything else must match to the last bit — the record including its training history, and the checkpoint's settings
and a sha256 of every state tensor.

    python tests/test_rungC_train_regression.py --write-golden [TRAINER]   # with the old trainer before a refactor, or after a deliberate change
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
GOLDEN = PLAN / "tests" / "data" / "rungC_train_golden.json"
PIN_CORPUS = PLAN / "tests" / "data" / "rungC_pin_corpus"
TRAINER = PLAN / "modules" / "05_support_predictor" / "m05" / "rungC_train.py"
VOLATILE = frozenset({"date", "provenance", "seconds", "exclude_ids_file"})
RUN_PATHS = frozenset({"molecules", "out_prefix", "exclude_ids_file"})    # the run's own temporary paths, in the checkpoint's args
CASES = {"carried": ["--epochs", "3"],
         "chainlike": ["--epochs", "2", "--size-test-min-atoms", "{size_min_atoms}", "--aux-target", "kfit", "--exclude-ids-file", "{excluded}"]}

sys.path.insert(0, str(PLAN / "probes"))


def environment() -> dict:
    """What bit-identity depends on beyond the code: CI's Linux torch gave other checkpoint bytes than this laptop's (16 Oct 2026)."""
    import platform

    import geometric
    import numpy
    import torch

    return {"system": platform.system(), "python": platform.python_version(), "torch": torch.__version__, "numpy": numpy.__version__,
            "geometric": geometric.__version__}


def environment_mismatch(pinned: dict, here: dict) -> str | None:
    """None where the pin was written; elsewhere the reason bit-identity cannot be expected, naming what differs."""
    differs = {k: (pinned.get(k), here.get(k)) for k in pinned.keys() | here.keys() if pinned.get(k) != here.get(k)}
    return f"bit-identity holds in the pinning environment only; differs: {dict(sorted(differs.items()))}" if differs else None


def pin_record() -> dict:
    return json.loads((PIN_CORPUS / "pin_corpus.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_changes(root: Path, record: dict) -> list[str]:
    """What differs between the frozen corpus on disk and its record: changed, missing or extra files, extra molecule folders."""
    listed = record["sha256"]
    on_disk = {f"{p.parent.name}/{p.name}": p for p in (root / "molecules").glob("*/*") if p.is_file()}
    changes = [f"{k}: {'missing' if k not in on_disk else 'changed'}" for k, h in listed.items() if k not in on_disk or sha256(on_disk[k]) != h]
    changes += [f"{k}: not in the record" for k in sorted(on_disk.keys() - listed.keys())]
    folders = {p.name for p in (root / "molecules").iterdir() if p.is_dir()}
    changes += [f"{d}/: not in the record" for d in sorted(folders - {m["id"] for m in record["molecules"]})]
    return changes


def stable(record):
    """The record without its wall-clock, provenance and temporary-path fields, at any depth."""
    if isinstance(record, dict):
        return {k: stable(v) for k, v in record.items() if k not in VOLATILE}
    if isinstance(record, list):
        return [stable(v) for v in record]
    return record


def first_difference(a, b, path: str = "$") -> str | None:
    """The path of the first entry where two JSON trees differ (NaN equals NaN, as in the serialised record)."""
    if isinstance(a, dict) and isinstance(b, dict):
        if a.keys() != b.keys():
            return f"{path}: keys {sorted(a.keys() ^ b.keys())}"
        return next((d for k in a if (d := first_difference(a[k], b[k], f"{path}.{k}"))), None)
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            return f"{path}: length {len(a)} vs {len(b)}"
        return next((d for i, (x, y) in enumerate(zip(a, b, strict=True)) if (d := first_difference(x, y, f"{path}[{i}]"))), None)
    if json.dumps(a) != json.dumps(b):
        return f"{path}: {a!r} vs {b!r}"
    return None


def tensor_digest(x) -> str:
    return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def checkpoint_summary(path: Path) -> dict:
    """The saved model as JSON: every setting, the args without the run's paths, a digest per state tensor."""
    import torch

    ck = torch.load(path, map_location="cpu", weights_only=False)
    out = {k: v for k, v in ck.items() if k not in {"state", "args", "provenance", "aux_class_scale"}}
    out["args"] = {k: v for k, v in ck["args"].items() if k not in RUN_PATHS}
    out["aux_class_scale"] = None if ck["aux_class_scale"] is None else ck["aux_class_scale"].tolist()
    out["state"] = {k: [list(v.shape), str(v.dtype), tensor_digest(v)] for k, v in ck["state"].items()}
    return json.loads(json.dumps(out))


def run_pin(case: str, workdir: Path, trainer: Path = TRAINER) -> dict:
    """Run one case on the frozen corpus in a fresh single-threaded process; the stable record and the checkpoint."""
    import chain_runner

    record = pin_record()
    excluded = workdir / "excluded.txt"
    excluded.write_text("\n".join(record["excluded"]) + "\n", encoding="utf-8")
    prefix = workdir / case
    extra = [a.format(excluded=excluded, size_min_atoms=record["size_min_atoms"]) for a in CASES[case]]
    argv = [str(PIN_CORPUS / "molecules"), str(prefix), *chain_runner.BASE, *chain_runner.RECIPE_V11, "--smoke", "--threads", "1", "--seeds", "0",
            "--save-model", *extra]
    env = os.environ | {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")} | {"PYTHONUTF8": "1"}
    subprocess.run([sys.executable, str(trainer), *argv], env=env, stdin=subprocess.DEVNULL, check=True)
    out = stable(json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8")))
    return {"record": out, "checkpoint": checkpoint_summary(Path(f"{prefix}_model_n5_seed0.pt"))}


def test_the_frozen_corpus_is_as_recorded():
    assert (changes := corpus_changes(PIN_CORPUS, pin_record())) == [], changes


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_run_is_unchanged(case, tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the trainer")
    assert corpus_changes(PIN_CORPUS, pin_record()) == [], "the frozen corpus changed: rebuild it and re-pin with the old trainer"
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    if message := environment_mismatch(golden["environment"], environment()):
        if os.environ.get("CI"):
            pytest.skip(message)
        pytest.fail(message + " — re-pin here with the trainer as it was before the change under test")
    assert (diff := first_difference(golden[case], run_pin(case, tmp_path))) is None, diff


def test_the_chainlike_case_exercises_its_switches():
    """The second pin covers the queued chains' paths only if its record shows them: the exclusion, the size hold-out, the kfit target."""
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    rec = json.loads(GOLDEN.read_text(encoding="utf-8"))["chainlike"]["record"]
    assert rec["excluded_ids"] == pin_record()["excluded"] and rec["holdout_s"] and rec["aux_target"] == "kfit"
    assert rec["target_residuals"] and all("readout_target" in v for v in rec["target_residuals"].values())


def test_a_changed_or_added_file_is_named(tmp_path):
    (tmp_path / "molecules" / "m1").mkdir(parents=True)
    f = tmp_path / "molecules" / "m1" / "geometry.json"
    f.write_text("{}", encoding="utf-8")
    record = {"sha256": {"m1/geometry.json": sha256(f), "m1/result.json": "0"}, "molecules": [{"id": "m1"}]}
    assert corpus_changes(tmp_path, record) == ["m1/result.json: missing"]
    f.write_text("{ }", encoding="utf-8")
    (tmp_path / "molecules" / "m2").mkdir()
    assert corpus_changes(tmp_path, record) == ["m1/geometry.json: changed", "m1/result.json: missing", "m2/: not in the record"]


def test_an_other_environment_is_named():
    here = {"system": "Windows", "torch": "2.14.0+cpu"}
    assert environment_mismatch(here, dict(here)) is None
    msg = environment_mismatch(here, {"system": "Linux", "torch": "2.14.0+cpu"})
    assert "'system': ('Windows', 'Linux')" in msg and "torch" not in msg


def test_stable_drops_volatile_fields_at_any_depth():
    rec = {"date": "x", "a": [{"seconds": 1.0, "b": 2}], "provenance": {}, "c": {"seconds": 3, "d": None}}
    assert stable(rec) == {"a": [{"b": 2}], "c": {"d": None}}


def test_first_difference_names_the_path():
    assert first_difference({"a": [1, 2.0]}, {"a": [1, 2.0]}) is None
    assert first_difference({"a": [1, 2.0]}, {"a": [1, 2.5]}) == "$.a[1]: 2.0 vs 2.5"
    assert first_difference({"a": float("nan")}, {"a": float("nan")}) is None
    assert first_difference({"a": 1}, {"b": 1}).startswith("$: keys")


def test_tensor_digest_sees_one_bit():
    torch = pytest.importorskip("torch")
    x = torch.tensor([1.0, 2.0])
    y = x.clone()
    y[1] = torch.nextafter(y[1], torch.tensor(3.0))
    assert tensor_digest(x) == tensor_digest(x.clone()) != tensor_digest(y)


if __name__ == "__main__":
    if not sys.argv[1:] or sys.argv[1] != "--write-golden" or len(sys.argv) > 3:
        sys.exit(__doc__)
    import tempfile

    if changes := corpus_changes(PIN_CORPUS, pin_record()):
        sys.exit(f"the frozen corpus differs from its record: {changes[:5]}")
    trainer = Path(sys.argv[2]) if len(sys.argv) == 3 else TRAINER
    pins: dict = {"environment": environment()}
    for case in sorted(CASES):
        with tempfile.TemporaryDirectory() as tmp:
            pins[case] = run_pin(case, Path(tmp), trainer)
    GOLDEN.write_text(json.dumps(pins, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {sorted(pins)} with {trainer} to {GOLDEN}")
