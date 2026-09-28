"""Rung C, 28 September 2026: element embeddings the pretraining never trained (Hessian QM9 has no S, Cl) are reset to the trained mean at
fine-tune time, a checkpoint without an element list is refused unless the elements are named, and the design check can probe the body as the
fine-tune sees it. Synthetic checkpoints only."""
import subprocess
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import design_check as DC  # noqa: E402
import rungC_equivariant as RC  # noqa: E402
import rungC_pretrain as PT  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)
QM9 = [1, 6, 7, 8, 9]


def _checkpoint(tmp_path, elements):
    torch.manual_seed(0)
    model = RT.Scaled(RC.DeltaHessianModel(aggregation="mean"), 1.0, [1.0, 2.0, 3.0])
    with torch.no_grad():
        model.model.emb.weight.mul_(0.1)                                  # "trained" rows small …
        model.model.emb.weight[16] = 5.0                                   # … an untrained row large, as in the 27 Sep checkpoint
    path = tmp_path / "ck.pt"
    PT.save_checkpoint(path, model, {"elements": elements})
    return path, model.model.emb.weight.detach().clone()


def test_unseen_element_rows_are_reset_to_the_trained_mean(tmp_path):
    path, ref = _checkpoint(tmp_path, QM9)
    body = RT.load_pretrained_body(path, reinit_head=False, aggregation="mean", target_elements=[1, 6, 16])
    assert body.reset_elements == [16]
    assert torch.allclose(body.emb.weight[16], ref[QM9].mean(0)) and torch.equal(body.emb.weight[6], ref[6]) and torch.equal(body.emb.weight[17], ref[17])
    same = RT.load_pretrained_body(path, reinit_head=False, aggregation="mean", target_elements=[1, 6, 8])
    assert same.reset_elements == [] and torch.equal(same.emb.weight, ref)
    none = RT.load_pretrained_body(path, reinit_head=False, aggregation="mean")                   # no target list: nothing touched
    assert none.reset_elements == [] and torch.equal(none.emb.weight, ref)


def test_checkpoint_without_element_list_is_refused_unless_named(tmp_path):
    path, ref = _checkpoint(tmp_path, None)
    with pytest.raises(ValueError, match="no element list"):
        RT.load_pretrained_body(path, reinit_head=False, aggregation="mean", target_elements=[1, 6, 16])
    body = RT.load_pretrained_body(path, reinit_head=False, aggregation="mean", target_elements=[1, 6, 16], pretrained_elements=QM9)
    assert body.reset_elements == [16] and torch.allclose(body.emb.weight[16], ref[QM9].mean(0))


def test_design_check_probes_the_body_as_the_finetune_sees_it(tmp_path):
    path, _ = _checkpoint(tmp_path, QM9)
    stored, d1 = DC.load_body(str(path), "mean", 0)
    reset, d2 = DC.load_body(str(path), "mean", 0, target_elements=[1, 6, 16])
    assert "as stored" in d1 and "reset [16]" in d2
    assert float(stored.emb.weight[16].abs().mean()) == 5.0 and float(reset.emb.weight[16].abs().mean()) < 1.0


def test_cli_switches_are_wired():
    h = subprocess.run([sys.executable, str(M05 / "rungC_train.py"), "--help"], capture_output=True, text=True, timeout=120).stdout
    assert "--pretrained-elements" in h
    h = subprocess.run([sys.executable, str(M05 / "design_check.py"), "--help"], capture_output=True, text=True, timeout=120).stdout
    assert "--as-finetune" in h and "--pretrained-elements" in h
