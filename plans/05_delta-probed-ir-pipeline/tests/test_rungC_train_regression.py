"""Regression pin of the rung-C trainer (TASKS 72): small runs must give the same record and the same saved model through the refactor.
The pins were written by the trainer as it stood before the refactor (master 95291f4b, 16 Oct 2026).

Two cases, both the carried recipe exactly as `chain_runner` passes it (with `--save-model`, as every chain trains), cut to mechanics size
by `--smoke` (5 pool molecules, seed 0, hold-outs cut to 3): 'carried' as it is (3 epochs); 'chainlike' with the switches the queued chains
add — an excluded-ids file (chains 41, 43), a size hold-out (chain 42) and the kfit target (chain 44) — 2 epochs. Each runs in a fresh
single-threaded process: two runs with two torch threads differed by up to 1.4e-6 relative (float32 reductions), and the BLAS thread counts
must be set before numpy is imported. Wall-clock fields, provenance and the run's own temporary paths are dropped; everything else must
match to the last bit — the record including its training history, and the checkpoint's settings and a sha256 of every state tensor.

    python tests/test_rungC_train_regression.py --write-golden [TRAINER]   # before a refactor (with the old trainer), or after a deliberate change

The corpus is not in git: the test reads it from RUNGC_CORPUS, or from the plan's own corpus folder, and skips when neither exists."""
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
TRAINER = PLAN / "modules" / "05_support_predictor" / "m05" / "rungC_train.py"
VOLATILE = frozenset({"date", "provenance", "seconds", "exclude_ids_file"})
RUN_PATHS = frozenset({"molecules", "out_prefix", "exclude_ids_file"})    # the run's own temporary paths, in the checkpoint's args
EXCLUDED = ("A2_233ec9a78f", "B_83267b6b89")                              # the first two pool molecules: the smoke cut moves past them
CASES = {"carried": ["--epochs", "3"],
         "chainlike": ["--epochs", "2", "--size-test-min-atoms", "28", "--aux-target", "kfit", "--exclude-ids-file", "{excluded}"]}

sys.path.insert(0, str(PLAN / "probes"))


def corpus_dir() -> Path:
    return Path(os.environ.get("RUNGC_CORPUS", PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"))


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
    """Run one case in a fresh single-threaded process; the stable record and the checkpoint."""
    import chain_runner

    excluded = workdir / "excluded.txt"
    excluded.write_text("\n".join(EXCLUDED) + "\n", encoding="utf-8")
    prefix = workdir / case
    extra = [a.format(excluded=excluded) for a in CASES[case]]
    argv = [str(corpus_dir()), str(prefix), *chain_runner.BASE, *chain_runner.RECIPE_V11, "--smoke", "--threads", "1", "--seeds", "0",
            "--save-model", *extra]
    env = os.environ | {v: "1" for v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS")} | {"PYTHONUTF8": "1"}
    subprocess.run([sys.executable, str(trainer), *argv], env=env, stdin=subprocess.DEVNULL, check=True)
    record = stable(json.loads(Path(f"{prefix}.json").read_text(encoding="utf-8")))
    return {"record": record, "checkpoint": checkpoint_summary(Path(f"{prefix}_model_n5_seed0.pt"))}


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_run_is_unchanged(case, tmp_path):
    pytest.importorskip("torch")
    if not corpus_dir().is_dir():
        pytest.skip(f"corpus not present: {corpus_dir()}")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the trainer")
    pinned = json.loads(GOLDEN.read_text(encoding="utf-8"))[case]
    assert (diff := first_difference(pinned, run_pin(case, tmp_path))) is None, diff


def test_the_chainlike_case_exercises_its_switches():
    """The second pin covers the queued chains' paths only if its record shows them: the exclusion, the size hold-out, the kfit target."""
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    rec = json.loads(GOLDEN.read_text(encoding="utf-8"))["chainlike"]["record"]
    assert rec["excluded_ids"] == list(EXCLUDED) and rec["holdout_s"] and rec["aux_target"] == "kfit"
    assert rec["target_residuals"] and all("readout_target" in v for v in rec["target_residuals"].values())


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

    trainer = Path(sys.argv[2]) if len(sys.argv) == 3 else TRAINER
    pins = {}
    for case in sorted(CASES):
        with tempfile.TemporaryDirectory() as tmp:
            pins[case] = run_pin(case, Path(tmp), trainer)
    GOLDEN.parent.mkdir(exist_ok=True)
    GOLDEN.write_text(json.dumps(pins, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned {sorted(pins)} with {trainer} to {GOLDEN}")
