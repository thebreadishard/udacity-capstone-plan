"""Lever 2a (1 Oct 2026): a `rungC_pretrain.py` checkpoint's body under the hybrid head — the weights arrive unchanged, an aggregation mismatch is
refused, unseen element rows are reset to the trained mean, and the trainer no longer refuses `--pretrained --head hybrid`."""
import re
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_hybrid as RH  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)


def _checkpoint(tmp_path, aggregation="mean", elements=(1, 6, 7, 8, 9)):
    torch.manual_seed(1)
    body = RC.DeltaHessianModel(aggregation=aggregation)
    path = tmp_path / "pre.pt"
    torch.save({"body_state": body.state_dict(), "aggregation": aggregation, "elements": list(elements), "class_scale": None, "scale": 1.0, "meta": {}}, path)
    return body, path


def test_pretrained_body_arrives_unchanged_under_the_hybrid_head(tmp_path):
    body, path = _checkpoint(tmp_path)
    torch.manual_seed(2)
    model = RH.HybridDeltaFModel(aggregation="mean")
    before = {k: v.clone() for k, v in model.body.state_dict().items()}
    assert any(not torch.equal(before[k], v) for k, v in body.state_dict().items())        # a fresh hybrid body differs from the checkpoint
    reset = RT.attach_pretrained_body(model, path, seed=0, aggregation="mean", target_elements=[1, 6, 7, 8, 9])
    assert reset == []
    for k, v in body.state_dict().items():
        assert torch.equal(model.body.state_dict()[k], v)                                    # every tensor of the body, head rows included


def test_unseen_elements_are_reset_and_mismatched_aggregation_refused(tmp_path):
    body, path = _checkpoint(tmp_path)
    model = RH.HybridDeltaFModel(aggregation="mean")
    reset = RT.attach_pretrained_body(model, path, seed=0, aggregation="mean", target_elements=[1, 6, 16, 17])
    assert reset == [16, 17]
    mean_row = body.emb.weight[[1, 6, 7, 8, 9]].mean(0)
    assert torch.allclose(model.body.emb.weight[16], mean_row) and torch.allclose(model.body.emb.weight[17], mean_row)
    with pytest.raises(ValueError, match="aggregation"):
        RT.attach_pretrained_body(RH.HybridDeltaFModel(aggregation="sum"), path, seed=0, aggregation="sum")


def test_trainer_guard_refuses_tensor_input_only():
    text = (M05 / "rungC_train.py").read_text(encoding="utf-8")
    assert re.search(r"if pretrained and tensor_input:\n\s+raise ValueError", text)
    assert "--tensor-input and --head hybrid are fresh-body variants" not in text
