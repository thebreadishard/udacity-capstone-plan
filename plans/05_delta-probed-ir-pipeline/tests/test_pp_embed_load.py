"""5 Oct 2026: the standout's learned order scorer (P2) loads checkpoints saved before the ΔH-network's charge-state row existed (q_emb, 3 Oct 2026) —
the missing row is zero-filled (the neutral identity), everything else strict; a checkpoint with any other missing key is still refused."""
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
PP = PLAN / "modules" / "standout_pattern_proposer"
sys.path.insert(0, str(PP))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
from pp.embed_scorer import EmbedScorer  # noqa: E402


def test_load_zero_fills_only_the_charge_row(tmp_path):
    s = EmbedScorer(seed=0, n_embed=16, n_blocks=1)
    states = [m.state_dict() for m in s.modules()]
    body = states[0]
    key = next(k for k in body if k.endswith("q_emb.weight"))
    body[key] = body[key] + 1.0                                  # a non-zero row, to prove the loader restores the saved value when present
    torch.save(dict(cfg=s.cfg, states=states), tmp_path / "p2x_seed0.pt")
    loaded = EmbedScorer.load(tmp_path / "p2x", 0)
    assert torch.equal(dict(loaded.modules()[0].state_dict())[key], body[key])
    del body[key]                                                  # a 26 Sep checkpoint: no charge row at all
    torch.save(dict(cfg=s.cfg, states=states), tmp_path / "p2y_seed0.pt")
    loaded = EmbedScorer.load(tmp_path / "p2y", 0)
    assert torch.count_nonzero(dict(loaded.modules()[0].state_dict())[key]) == 0
    other = next(k for k in body if k != key and body[k].numel() > 0)
    del body[other]
    torch.save(dict(cfg=s.cfg, states=states), tmp_path / "p2z_seed0.pt")
    with pytest.raises(RuntimeError):
        EmbedScorer.load(tmp_path / "p2z", 0)


@pytest.mark.skipif(not (PP / "out" / "p2_seed0.pt").exists(), reason="standout checkpoints not present (CI)")
def test_the_26_sep_checkpoint_loads():
    s = EmbedScorer.load(PP / "out" / "p2", 0)
    assert s is not None
