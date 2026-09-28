"""Rung C, dated amendment of 28 September 2026: neighbour-count normalisation of the interaction blocks (`aggregation="mean"`), recorded in the
checkpoint and refused on mismatch — the guard against a body setting travelling unexamined (the E8 lesson of 27 Sep). Synthetic clusters only."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_equivariant as RC  # noqa: E402
import rungC_pretrain as PT  # noqa: E402
import rungC_train as RT  # noqa: E402

torch.set_num_threads(1)


def _cluster(n_atoms: int, seed: int, spread_bohr: float = 3.0) -> dict:
    """A dense random carbon cluster: every atom within the cutoff of every other, so the neighbour count is n_atoms − 1."""
    rng = np.random.default_rng(seed)
    pos = torch.as_tensor(rng.uniform(-spread_bohr, spread_bohr, size=(n_atoms, 3)), dtype=torch.float32)
    Z = torch.full((n_atoms,), 6, dtype=torch.long)
    A = rng.normal(size=(3 * n_atoms, 3 * n_atoms)) * 0.01
    return {"Z": Z, "pos": pos, "H_low": torch.as_tensor(A + A.T, dtype=torch.float32)}


def test_aggregate_mean_is_sum_over_degree():
    msgs = torch.arange(12, dtype=torch.float32).reshape(6, 2)
    idx = torch.tensor([0, 0, 0, 1, 2, 2])                           # degrees 3, 1, 2 (atom 3 has none)
    total = RC.aggregate(msgs, idx, 4)
    assert torch.equal(total[0], msgs[:3].sum(0)) and torch.equal(total[3], torch.zeros(2))
    inv = 1.0 / torch.bincount(idx, minlength=4).clamp_min(1).float()
    mean = RC.aggregate(msgs, idx, 4, inv)
    assert torch.allclose(mean[0], msgs[:3].mean(0)) and torch.allclose(mean[2], msgs[4:6].mean(0)) and torch.equal(mean[3], torch.zeros(2))


def test_body_scale_does_not_grow_with_neighbour_count_under_mean():
    """The incident, in miniature: the same random body on an 8-atom and a 24-atom dense cluster (7 vs 23 neighbours). Under sum pooling the
    feature scale grows with the neighbour count (≈ 1.5× on a fresh body; trained QM9 weights amplified it to 1e18); under mean pooling it is
    independent of the count to within 10 %."""
    ratios = {}
    for agg in RC.AGGREGATIONS:
        torch.manual_seed(0)
        body = RC.DeltaHessianModel(aggregation=agg)
        with torch.no_grad():
            scale = [float(body.encode(**_cluster(n, seed=1))[0].abs().mean()) for n in (8, 24)]
        ratios[agg] = scale[1] / scale[0]
    assert abs(ratios["mean"] - 1.0) < 0.1 < ratios["sum"] - 1.0, ratios


def test_checkpoint_carries_aggregation_and_a_mismatch_is_refused(tmp_path):
    torch.manual_seed(0)
    model = RT.Scaled(RC.DeltaHessianModel(aggregation="mean"), 1.0, [1.0, 2.0, 3.0])
    path = tmp_path / "ck.pt"
    PT.save_checkpoint(path, model, {"note": "test"})
    assert torch.load(path, weights_only=False)["aggregation"] == "mean"
    assert RT.load_pretrained_body(path, aggregation="mean").aggregation == "mean"
    with pytest.raises(ValueError, match="mean aggregation, the run asks for sum"):
        RT.load_pretrained_body(path, aggregation="sum")
    legacy = tmp_path / "legacy.pt"                                    # a checkpoint from before 28 Sep has no key and is a sum body
    torch.save({"body_state": model.model.state_dict(), "class_scale": None, "scale": 1.0, "meta": {}}, legacy)
    assert RT.load_pretrained_body(legacy, aggregation="sum").aggregation == "sum"
    with pytest.raises(ValueError, match="sum aggregation, the run asks for mean"):
        RT.load_pretrained_body(legacy, aggregation="mean")


def test_invalid_aggregation_is_refused():
    with pytest.raises(ValueError, match="aggregation must be one of"):
        RC.DeltaHessianModel(aggregation="max")


def test_cli_switch_is_wired_in_both_drivers():
    for script in ("rungC_train.py", "rungC_pretrain.py"):
        out = subprocess.run([sys.executable, str(M05 / script), "--help"], capture_output=True, text=True, timeout=120).stdout
        assert "--aggregation {sum,mean}" in out, script
