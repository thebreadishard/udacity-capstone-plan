"""The Ladder's stop rule and its read-out (28 Sep 2026, wide-deck pre-registration amendment): the rule fires at the second of two consecutive
checkpoints under τ, the budget stops at the last checkpoint within it, an exhausted pool is neither; the reader's seed median and false-stop count;
`run_simulation.select_orders` keeps P0 and the prefixes asked for."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "modules" / "standout_pattern_proposer"))
from pp import core as C  # noqa: E402
from run_simulation import select_orders  # noqa: E402
from stop_rule_readout import read  # noqa: E402


def curve(rho_offs, frobs=None, M=2, step=10):
    frobs = frobs or [r for r in rho_offs]
    return [(2 * M + n * step, 0.5 * r, r, f, 1e-6, f) for n, (r, f) in enumerate(zip(rho_offs, frobs, strict=True))]


def test_rule_fires_at_the_second_consecutive_checkpoint():
    c = curve([1.0, 0.5, 0.28, 0.35, 0.29, 0.25, 0.2])
    r = C.stop_rule(c, tau=0.3, M=2)
    assert r["stopped"] is True and r["reason"] == "rule" and r["checkpoint"] == 5 and r["cost"] == 50
    assert C.k_off_at(c, 0.3, 2) == 20          # the first crossing is three checkpoints earlier: the hysteresis costs what the dip cost


def test_budget_stops_at_the_last_checkpoint_within_it():
    c = curve([1.0, 0.8, 0.7, 0.6, 0.5])
    r = C.stop_rule(c, tau=0.3, b_max=25, M=2)
    assert r["stopped"] is False and r["reason"] == "budget" and r["cost"] == 20 and r["rho_off"] == 0.7


def test_exhausted_pool_is_neither():
    r = C.stop_rule(curve([1.0, 0.8, 0.7]), tau=0.3, M=2)
    assert r["stopped"] is None and r["cost"] == 20


def test_reader_seed_median_and_false_stop():
    ok = curve([1.0, 0.5, 0.2, 0.2], frobs=[1.0, 0.5, 0.3, 0.3])
    late = curve([1.0, 0.5, 0.4, 0.2, 0.2], frobs=[1.0, 0.5, 0.4, 0.3, 0.3])
    lying = curve([1.0, 0.2, 0.2], frobs=[1.0, 0.6, 0.6])           # held-out says done, the truth says 0.6: a false stop
    wide = {"per_molecule": {
        "a": dict(split="eval", M=2, P0=dict(curve=late), P12_seed0=dict(curve=ok), P12_seed1=dict(curve=late), P12_seed2=dict(curve=ok)),
        "b": dict(split="eval_parents", M=2, P0=dict(curve=lying), P12_seed0=dict(curve=lying), P12_seed1=dict(curve=lying),
                  P12_seed2=dict(curve=curve([1.0, 0.9])))}}
    band_curve = curve([1.0, 0.9, 0.8])
    band = {"per_molecule": {"a": dict(split="eval", M=2, P0=dict(curve=band_curve)), "b": dict(split="eval_parents", M=2, P0=dict(curve=band_curve))}}
    res = read(wide, band, tau=0.3, bmax_factor=2.0, orders=["P0", "P12"], seeds=[0, 1, 2], false_stop=0.4)
    a, b = res["per_molecule"]["a"]["orderings"]["P12"], res["per_molecule"]["b"]["orderings"]["P12"]
    assert a["stopped"] and a["cost"] == 30 and not a["false_stop"]            # seeds stop at 30, 40, 30 → median 30
    assert b["stopped"] and b["false_stop"]                                    # two of three seeds stop, both on a lying held-out set
    assert res["summary"]["all"]["P12"]["n_false_stops"] == 1 and res["summary"]["all"]["P12"]["n_stopped"] == 2
    assert res["per_molecule"]["a"]["b_max"] == 48                             # 2 × the band deck's 24 energies


def test_select_orders_keeps_p0_and_prefixes():
    named = {"P0": 0, "P1_seed0": 1, "P12_seed0": 2, "P3_oracle": 3, "P2_seed0": 4}
    assert select_orders(named, None) == named
    assert set(select_orders(named, "P12,P3_oracle")) == {"P0", "P12_seed0", "P3_oracle"}
    assert set(select_orders(named, "P3")) == {"P0", "P3_oracle"}
