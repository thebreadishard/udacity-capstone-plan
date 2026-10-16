"""Regression pin of the rung-C trainer (TASKS 72): small runs on the frozen corpus must give the same record and the same saved model to the
bit. The pins are written by the trainer as it stood before the refactor (master 95291f4b, 16 Oct 2026), on the frozen corpus.

The corpus is `tests/data/rungC_pin_corpus/` (built by `tests/data/make_rungC_pin_corpus.py`: 27 molecules, only the files the trainer reads,
a sha256 per file), so the pin reads the same bytes on every machine. Bit-identity of the training itself holds only in the environment the
pin was written in (platform, Python, torch, numpy, geomeTRIC, recorded in the golden): elsewhere the pin skips in CI and fails locally,
so an upgrade cannot switch the guard off unnoticed. It first ran on the live corpus, whose pool and class scales moved when chain 40 merged
64 molecules into it (16 Oct 11:32): red without a code change, a pin that could not tell drift from a regression.

Two cases, both the carried recipe exactly as `chain_runner` passes it (with `--save-model`, as every chain trains), cut to mechanics size
by `--smoke` (5 pool molecules, seed 0, hold-outs cut to 3): 'carried' as it is (3 epochs); 'chainlike' with the switches the queued chains
add — an excluded-ids file (chains 41, 43), a size hold-out (chain 42; at the frozen set's own scale) and the kfit target (chain 44) —
2 epochs. Each runs in a fresh single-threaded process. Wall-clock fields, provenance and the run's own temporary paths are dropped;
everything else must match to the last bit — the record including its training history, and the checkpoint's settings and a sha256 of
every state tensor. Shared tools: `tests/pin_tools.py`.

    python tests/test_rungC_train_regression.py --write-golden [TRAINER]   # with the old trainer before a refactor, or after a deliberate change
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from pin_tools import (
    DATA,
    M05,
    PIN_CORPUS,
    corpus_changes,
    digest,
    environment,
    first_difference,
    pin_record,
    require_frozen_corpus,
    require_pinning_environment,
    single_thread_env,
    stable,
)

GOLDEN = DATA / "rungC_train_golden.json"
TRAINER = M05 / "rungC_train.py"
VOLATILE = frozenset({"date", "provenance", "seconds", "exclude_ids_file"})
RUN_PATHS = frozenset({"molecules", "out_prefix", "exclude_ids_file"})    # the run's own temporary paths, in the checkpoint's args
CASES = {"carried": ["--epochs", "3"],
         "chainlike": ["--epochs", "2", "--size-test-min-atoms", "{size_min_atoms}", "--aux-target", "kfit", "--exclude-ids-file", "{excluded}"]}

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))


def checkpoint_summary(path: Path) -> dict:
    """The saved model as JSON: every setting, the args without the run's paths, a digest per state tensor."""
    import torch

    ck = torch.load(path, map_location="cpu", weights_only=False)
    out = {k: v for k, v in ck.items() if k not in {"state", "args", "provenance", "aux_class_scale"}}
    out["args"] = {k: v for k, v in ck["args"].items() if k not in RUN_PATHS}
    out["aux_class_scale"] = None if ck["aux_class_scale"] is None else ck["aux_class_scale"].tolist()
    out["state"] = {k: [list(v.shape), str(v.dtype), digest(v)] for k, v in ck["state"].items()}
    return json.loads(json.dumps(out))


def trainer_argv(case: str, workdir: Path) -> list[str]:
    """The trainer's command line for one case on the frozen corpus, its excluded-ids file written into `workdir`."""
    import chain_runner

    record = pin_record()
    excluded = workdir / "excluded.txt"
    excluded.write_text("\n".join(record["excluded"]) + "\n", encoding="utf-8")
    extra = [a.format(excluded=excluded, size_min_atoms=record["size_min_atoms"]) for a in CASES[case]]
    return [str(PIN_CORPUS / "molecules"), str(workdir / case), *chain_runner.BASE, *chain_runner.RECIPE_V11, "--smoke", "--threads", "1",
            "--seeds", "0", "--save-model", *extra]


def run_pin(case: str, workdir: Path, trainer: Path = TRAINER) -> dict:
    """Run one case in a fresh single-threaded process; the stable record and the checkpoint."""
    subprocess.run([sys.executable, str(trainer), *trainer_argv(case, workdir)], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True)
    out = stable(json.loads((workdir / f"{case}.json").read_text(encoding="utf-8")), VOLATILE)
    return {"record": out, "checkpoint": checkpoint_summary(workdir / f"{case}_model_n5_seed0.pt")}


def test_the_frozen_corpus_is_as_recorded():
    assert (changes := corpus_changes(PIN_CORPUS, pin_record())) == [], changes


@pytest.mark.parametrize("case", sorted(CASES))
def test_the_pinned_run_is_unchanged(case, tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the trainer")
    require_frozen_corpus()
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert (diff := first_difference(golden[case], run_pin(case, tmp_path))) is None, diff


def test_the_chainlike_case_exercises_its_switches():
    """The second pin covers the queued chains' paths only if its record shows them: the exclusion, the size hold-out, the kfit target."""
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    rec = json.loads(GOLDEN.read_text(encoding="utf-8"))["chainlike"]["record"]
    assert rec["excluded_ids"] == pin_record()["excluded"] and rec["holdout_s"] and rec["aux_target"] == "kfit"
    assert rec["target_residuals"] and all("readout_target" in v for v in rec["target_residuals"].values())


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
