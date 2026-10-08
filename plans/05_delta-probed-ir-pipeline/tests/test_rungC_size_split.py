"""TASKS 35 (8 Oct 2026): the size split of the rung C trainer — large pool molecules become hold-out (s) and never train; the pool cap keeps only
small ones; the order is kept; an empty hold-out is refused."""
import sys
from pathlib import Path

import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "m05"))
pytest.importorskip("torch")
import rungC_train as RT  # noqa: E402

NAT = {"a": 12, "b": 20, "c": 21, "d": 27, "e": 30}


def test_size_split_holds_out_the_large_and_caps_the_pool():
    pool, test = RT.size_split(["e", "a", "d", "c", "b"], NAT, test_min_atoms=27, pool_max_atoms=20)
    assert test == ["e", "d"] and pool == ["a", "b"]


def test_size_split_off_and_control():
    assert RT.size_split(["a", "b"], NAT) == (["a", "b"], [])
    pool, test = RT.size_split(["e", "a", "d", "c"], NAT, test_min_atoms=27)   # the control: same hold-out, every size below it trains
    assert test == ["e", "d"] and pool == ["a", "c"]


def test_size_split_refuses_an_empty_holdout():
    with pytest.raises(SystemExit):
        RT.size_split(["a", "b"], NAT, test_min_atoms=40)
