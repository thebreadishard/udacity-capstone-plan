"""The pipeline's inference path (`m05/rungC_infer.py`, TASKS 146) against the training path, on the frozen corpus: the trainer's
per-molecule tensors pinned to the bit (written with the code before `molecule_tensors` was split), and the inference path — which reads
no ωB97X Hessian — giving the same input tensors and the same ΔH for every molecule with analytic labels. Pin model: the transfer pin's
(`tests/data/rungC_cc_pin_model.pt`), never a carried model's file.

    python tests/test_rungC_infer.py --write-golden     # with the code as it is before a change
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from pin_tools import DATA, M05, PIN_CORPUS, environment, first_difference, require_frozen_corpus, require_pinning_environment, single_thread_env

sys.path.insert(0, str(M05))
RUNNER = Path(__file__).with_name("molecule_tensors_pin_runner.py")
MODEL = DATA / "rungC_cc_pin_model.pt"
GOLDEN = DATA / "rungC_molecule_tensors_golden.json"
TRUTH = frozenset({"dH_true", "dF_true", "dF_norm", "K_true", "K_norm"})


def run_pin(work: Path, inference: bool = False) -> dict:
    """The runner on a copy of the frozen corpus (the least-squares target cache is written beside it), single-threaded."""
    shutil.copytree(PIN_CORPUS / "molecules", work / "molecules")
    argv = [sys.executable, str(RUNNER), str(work / "molecules"), str(MODEL), str(work / "cache")] + (["--inference"] if inference else [])
    out = subprocess.run(argv, env=single_thread_env(), stdin=subprocess.DEVNULL, capture_output=True, text=True, check=True)
    return json.loads(out.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def pinned(tmp_path_factory) -> dict:
    require_frozen_corpus()
    return run_pin(tmp_path_factory.mktemp("infer"), inference=True)


def test_the_training_path_is_unchanged(pinned):
    if not GOLDEN.exists():
        pytest.fail(f"no pin at {GOLDEN}: write it with --write-golden before changing molecule_tensors")
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    require_pinning_environment(golden)
    assert (diff := first_difference(golden["training"], pinned["training"])) is None, diff


def test_the_inference_path_gives_the_training_inputs_and_delta_h(pinned):
    assert pinned["inference"].keys() == pinned["training"].keys() and len(pinned["inference"]) >= 2
    for i, inf in pinned["inference"].items():
        train = pinned["training"][i]
        assert not TRUTH & inf["tensors"].keys(), f"{i}: the inference path carries the truth"
        assert inf["tensors"].keys() <= train["tensors"].keys()
        assert {k: train["tensors"][k] for k in inf["tensors"]} == inf["tensors"], i
        assert inf["dH"] == train["dH"], f"{i}: ΔH differs"


def test_a_folder_without_the_analytic_b3lyp_hessian_is_refused(tmp_path):
    import rungC_infer as RI

    d = tmp_path / "X"
    shutil.copytree(PIN_CORPUS / "molecules" / "A_8448043181", d)
    (d / "hessian_b3lyp_analytic.npz").unlink()
    with pytest.raises(FileNotFoundError, match=r"hessian_b3lyp_analytic\.npz"):
        RI.low_level(d)


if __name__ == "__main__":
    if sys.argv[1:] != ["--write-golden"]:
        raise SystemExit(__doc__)
    import tempfile

    require_frozen_corpus()
    with tempfile.TemporaryDirectory() as tmp:
        res = run_pin(Path(tmp))
    GOLDEN.write_text(json.dumps({"environment": environment(), "training": res["training"]}, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {GOLDEN}: {len(res['training'])} molecules")
