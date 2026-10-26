"""v1.4 §7 (26 Oct 2026): the selection set and the weight decay. The selection set is drawn by whole scaffold cores with its own seed, never
splits a core, reaches its fraction, keeps the pool's order and is refused where it cannot work; the weight decay reaches AdamW."""
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
import rungC_train as RT  # noqa: E402
from rungC_config import MAX_SELECTION_FRACTION, WEIGHT_DECAY, TrainConfig, config_from_argv, parse_selection_split  # noqa: E402


def config(**kw) -> TrainConfig:
    return TrainConfig(molecules="mol", out_prefix="out", **kw)


def pool_of(cores: dict[str, int]) -> tuple[list, dict]:
    """A pool with `count` molecules per core, ids '<core>_<k>', in an order that interleaves the cores."""
    mols = {f"{c}_{k}": {"core": c} for c, count in cores.items() for k in range(count)}
    return sorted(mols, key=lambda i: (int(i.rsplit("_", 1)[1]), i)), mols


def test_the_split_takes_whole_cores_until_the_fraction():
    pool, mols = pool_of({"anthracene": 6, "pyrene": 5, "fluorene": 4, "phenanthrene": 3, "chrysene": 2})
    rest, sel = RT.selection_split(pool, mols, seed=7, fraction=0.25)
    sel_cores = {mols[i]["core"] for i in sel}
    assert not sel_cores & {mols[i]["core"] for i in rest}                      # no core on both sides
    assert len(sel) >= 0.25 * len(pool) and set(rest) | set(sel) == set(pool)
    assert rest == [i for i in pool if i in set(rest)]                          # the pool's order is kept
    assert RT.selection_split(pool, mols, seed=7, fraction=0.25) == (rest, sel)  # fixed by its seed


def test_the_split_refuses_to_take_every_core():
    pool, mols = pool_of({"a": 3})                                              # one core: any fraction takes it all
    with pytest.raises(SystemExit, match="takes every scaffold core"):
        RT.selection_split(pool, mols, seed=0, fraction=0.1)


@pytest.mark.parametrize("text", ["7", "x:0.1", "7:abc", "7:0", f"7:{MAX_SELECTION_FRACTION + 0.01}", "-1:0.1"])
def test_bad_selection_specs_are_refused(text):
    with pytest.raises(ValueError, match="selection_split"):
        parse_selection_split(text)


def test_the_selection_spec_parses_and_conflicts_are_refused():
    assert config(selection_split="7:0.15").selection == (7, 0.15) and config().selection is None
    with pytest.raises(ValueError, match="--selection-split draws from the e6 pool"):
        config(selection_split="7:0.15", split="layerB")
    with pytest.raises(ValueError, match="a selection set needs a pool"):
        config(selection_split="7:0.15", overfit_one="A_x")


def test_weight_decay_defaults_to_the_carried_value_and_reaches_adamw(monkeypatch):
    assert config().weight_decay == WEIGHT_DECAY == 1e-4
    assert config_from_argv(["mol", "out", "--weight-decay", "3e-5"]).weight_decay == 3e-5
    with pytest.raises(ValueError):
        config(weight_decay=-1e-4)
    seen = {}

    class Stop(Exception):
        pass

    def fake_adamw(params, lr, weight_decay):
        seen.update(lr=lr, weight_decay=weight_decay)
        raise Stop

    monkeypatch.setattr(RT.torch.optim, "AdamW", fake_adamw)
    fold = RT.Fold(tensors={}, fit_ids=[], val_ids=[])
    with pytest.raises(Stop):
        RT._fit(torch.nn.Linear(1, 1), None, config(weight_decay=3e-5, epochs=1), fold, 0, print)
    assert seen == {"lr": 1e-3, "weight_decay": 3e-5}
