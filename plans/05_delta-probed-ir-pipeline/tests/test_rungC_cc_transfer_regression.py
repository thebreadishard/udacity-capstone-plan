"""Regression pin of the T3 transfer script `m05/rungC_cc_transfer.py` (TASKS 72, 16 Oct 2026), written before its main is refactored under
the clean-code rule: one run on the frozen corpus that takes every switch must give the same record, table and saved predictions to the bit.

Inputs, all fixed: the frozen corpus (`tests/data/rungC_pin_corpus/`); a proxy model trained on it (`tests/data/rungC_cc_pin_model.pt`,
made once with `--make-model`: the carried recipe, smoke size, 3 epochs); two anchors, benzene and phenanthrene — the frozen set's only
molecules that are planar (the out-of-plane routines refuse fluorene's CH₂ and biphenyl's twist) and carry an analytic low level (an FD
one mixes in- and out-of-plane modes: phenylacetylene's stopped the second attempt), as every real anchor does — each with its analytic
ωB97X Hessian standing in for the coupled-cluster one (a valid input for the code, not physics), and phenanthrene's CPHF APT as its "CC
APT"; dibenzofuran as the molecule to predict. Each fold fine-tunes on one anchor. The switches: the folds' none / α / head / head-L2 /
rank-2 adapter modes, the out-of-plane couplings from the low level and the out-of-plane model, the intensity read-out, the fold
predictions and --predict. The run goes through `tests/cc_pin_runner.py`, which replaces only the model-registry gate. Bit-identity holds
in the pinning environment (as the trainer's pin).

History: pinned first (6ea10300) with the script as it was, without --lora-rank — its adapter drew its random start from torch's default
generator, which this torch seeds from the clock (the same fold gave 14.44 and 14.05 cm⁻¹ in two runs). The refactor (83d79448) matched
that pin to the bit and seeded the adapter; the pin was then rewritten with the adapter in and the table's α column named for the training
anchors rather than "3 anchors" — two deliberate changes, nothing else.

    python tests/test_rungC_cc_transfer_regression.py --make-model                 # once, before the first pin
    python tests/test_rungC_cc_transfer_regression.py --write-golden [SCRIPT]       # with the script as it is before a change
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
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

CC_SCRIPT = M05 / "rungC_cc_transfer.py"
RUNNER = Path(__file__).with_name("cc_pin_runner.py")
MODEL = DATA / "rungC_cc_pin_model.pt"
GOLDEN = DATA / "rungC_cc_transfer_golden.json"
ANCHORS = ("A_8448043181", "A_541c53d1a5")                      # benzene, phenanthrene: planar, analytic pair, APT
APT_ANCHOR = "A_541c53d1a5"
PREDICT = "A_20db5837c9"                                         # dibenzofuran, not an anchor
VOLATILE = frozenset({"date", "seconds"})
SWITCHES = ["--epochs", "3", "--head-l2", "0.1", "--lora-rank", "2", "--oop-couplings-low", "--oop-diagonal-model", "--save-fold-predictions",
            "--threads", "1", "--allow-any-model", "--allow-any-anchor", "--allow-mixed-tiers"]

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))


def cc_argv(work: Path) -> list[str]:
    """The script's command line, with its anchor and APT files written into `work`."""
    mols = PIN_CORPUS / "molecules"
    argv = [str(mols), str(MODEL), str(work / "t3")]
    for i in ANCHORS:
        shutil.copyfile(mols / i / "hessian_wb97x_analytic.npz", work / f"{i}_cc.npz")
        argv += ["--anchor", f"{i}={work / f'{i}_cc.npz'}"]
    g = json.loads((mols / APT_ANCHOR / "geometry.json").read_text(encoding="utf-8"))
    with np.load(mols / APT_ANCHOR / "dipole_b3lyp_cphf.npz") as z:
        np.savez(work / "apt.npz", coords_bohr=np.asarray(g["coords_bohr"], float), apt=np.asarray(z["apt"], float))
    return [*argv, "--apt", f"{APT_ANCHOR}={work / 'apt.npz'}", "--predict", PREDICT, *SWITCHES]


def anonymised(text: str, work: Path) -> str:
    """The text with the run's own folder and the model's location replaced, in every spelling they appear in (plain, JSON-escaped, posix)."""
    for place, name in ((MODEL, "<model>"), (work, "<work>")):
        for spelling in (json.dumps(str(place))[1:-1], str(place), place.as_posix()):
            text = text.replace(spelling, name)
    return text


def npz_summary(path: Path, work: Path) -> dict:
    """A saved prediction: a digest per float array, every other field as its value."""
    with np.load(path) as z:
        return {k: digest(z[k]) if z[k].dtype.kind == "f" and z[k].ndim else anonymised(json.dumps(z[k].tolist()), work) for k in z.files}


def run_cc(work: Path, script: Path = CC_SCRIPT) -> dict:
    """Run the script once in a fresh single-threaded process; its stable record, table and saved predictions."""
    subprocess.run([sys.executable, str(RUNNER), str(script), *cc_argv(work)], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True)
    record = stable(json.loads(anonymised((work / "t3.json").read_text(encoding="utf-8"), work)), VOLATILE)
    table = anonymised((work / "t3.md").read_text(encoding="utf-8"), work)
    table = re.sub(r"\(\d{4}-\d\d-\d\d \d\d:\d\d\)", "(<date>)", table)
    table = re.sub(r"\n\d+ s\.\n*$", "\n", table)
    outputs = {p.name: npz_summary(p, work) for p in sorted(work.glob("t3_*.npz"))}
    return {"record": record, "table": table, "outputs": outputs}


def test_the_model_and_its_corpus_are_present():
    assert MODEL.is_file(), f"make the pin's model first: python {Path(__file__).name} --make-model"
    assert corpus_changes(PIN_CORPUS, pin_record()) == []


def test_the_pinned_transfer_is_unchanged(tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing the script")
    require_frozen_corpus()
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert (diff := first_difference(golden["run"], run_cc(tmp_path))) is None, diff


def test_the_run_takes_every_switch():
    """The pin covers the script only if its record shows each switch at work."""
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    run = json.loads(GOLDEN.read_text(encoding="utf-8"))["run"]
    folds = run["record"]["folds"]
    assert sorted(folds) == sorted(ANCHORS) and run["record"]["predict"][PREDICT]["mode"] == "head_l2"
    fold = folds[APT_ANCHOR]
    for column in ("network_none", "network_alpha", "network_head", "network_head_l2", "network_lora", "network_head_ooplow",
                   "network_head_l2_oopmodel", "oop_model_only", "alpha_scaling", "zero_rule"):
        assert column in fold, column
    assert "intensity" in fold["network_head"] and fold["saved_prediction"]
    assert len(run["outputs"]) == len(ANCHORS) + 1


def test_held_runs_only_the_named_fold_and_it_equals_the_pinned_one(tmp_path):
    """Anchor set three's R-A (--held, 20 Oct 2026): holding out one anchor runs that fold alone; its pool is the other anchors, as in the
    full run, so the fold is the pinned run's fold to the bit (without --predict, which is outside the folds)."""
    pytest.importorskip("torch")
    pytest.importorskip("geometric")
    if not GOLDEN.exists():
        pytest.skip("no pin yet")
    require_frozen_corpus()
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    argv = cc_argv(tmp_path)
    at = argv.index("--predict")
    argv = [*argv[:at], *argv[at + 2:], "--held", APT_ANCHOR]
    subprocess.run([sys.executable, str(RUNNER), str(CC_SCRIPT), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True)
    record = stable(json.loads(anonymised((tmp_path / "t3.json").read_text(encoding="utf-8"), tmp_path)), VOLATILE)
    assert record["held"] == [APT_ANCHOR] and sorted(record["folds"]) == [APT_ANCHOR]
    assert (diff := first_difference(golden["run"]["record"]["folds"][APT_ANCHOR], record["folds"][APT_ANCHOR])) is None, diff


def make_model() -> None:
    """The pin's proxy model: the carried recipe on the frozen corpus, smoke size, 3 epochs, by the trainer as it is (pinned itself)."""
    import tempfile

    import chain_runner

    with tempfile.TemporaryDirectory() as tmp:
        argv = [str(PIN_CORPUS / "molecules"), str(Path(tmp) / "m"), *chain_runner.BASE, *chain_runner.RECIPE_V11, "--smoke", "--epochs", "3",
                "--threads", "1", "--seeds", "0", "--save-model"]
        subprocess.run([sys.executable, str(M05 / "rungC_train.py"), *argv], env=single_thread_env(), stdin=subprocess.DEVNULL, check=True)
        shutil.copyfile(Path(tmp) / "m_model_n5_seed0.pt", MODEL)
    print(f"model written: {MODEL} ({MODEL.stat().st_size / 1e6:.2f} MB)")


if __name__ == "__main__":
    import tempfile

    if sys.argv[1:] == ["--make-model"]:
        make_model()
        sys.exit(0)
    if not sys.argv[1:] or sys.argv[1] != "--write-golden" or len(sys.argv) > 3:
        sys.exit(__doc__)
    if changes := corpus_changes(PIN_CORPUS, pin_record()):
        sys.exit(f"the frozen corpus differs from its record: {changes[:5]}")
    script = Path(sys.argv[2]) if len(sys.argv) == 3 else CC_SCRIPT
    with tempfile.TemporaryDirectory() as tmp:
        pin = {"environment": environment(), "run": run_cc(Path(tmp), script)}
    GOLDEN.write_text(json.dumps(pin, indent=1, sort_keys=True), encoding="utf-8")
    print(f"pinned with {script} to {GOLDEN}")
