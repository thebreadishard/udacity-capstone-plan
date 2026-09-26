"""Standout pattern proposer (pre-registration 26 September 2026), the registered export test: on a synthetic Δ₂ with a planted off-diagonal block the
deterministic deck's recovery must find the block (relative off-diagonal Frobenius error ≤ 10 %), the oracle ordering must get there with no more energies
than the hashed order, and the exact responses must be what ½ aᵀ Δ a says. No corpus file, no torch."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "modules" / "standout_pattern_proposer"))
from pp import core as C  # noqa: E402


def synthetic_export(M=10, seed=0):
    """A Δ₂ with a small diagonal, one planted strong off-diagonal block among near-degenerate modes and weak noise elsewhere; deck from the probe."""
    rng = np.random.default_rng(seed)
    freq = np.sort(rng.uniform(400, 1600, size=M))
    freq[3:6] = [1000.0, 1010.0, 1025.0]                                  # a near-degenerate triple inside the band
    D2 = np.diag(rng.uniform(1e-4, 5e-4, size=M))
    D2[3, 4] = D2[4, 3] = 2e-4
    D2[4, 5] = D2[5, 4] = -1.5e-4
    D2[3, 5] = D2[5, 3] = 1e-4
    noise = rng.normal(scale=2e-6, size=(M, M))
    D2 = D2 + np.triu(noise, 1) + np.triu(noise, 1).T
    a = {"M": M, "freq_low_cm": freq.tolist(), "molecule": "synthetic"}
    deck = C.PROBE.build_deck(a, quick=False)
    pairs, _ = C.PROBE.sym_index(M)
    d_true = C.pack(D2, pairs)
    pats = sorted((p for p in deck["patterns"] if p["kind"] != "q2"), key=lambda p: p["index"])
    A = np.array([p["a"] for p in pats])
    rows = np.array([C.PROBE.design_row_E(p["a"], pairs) for p in pats])
    return dict(id="synthetic", M=M, freq_cm=freq, D2=D2, participation=np.ones((4, M)) / 4, symbols=["C"] * 4, deck_hash=deck["deck_hash"],
                kinds=np.array([p["kind"] for p in pats]), modes=[p["modes"] for p in pats], holdout=np.array([bool(p["holdout"]) for p in pats]),
                A=A, rows=rows, R=rows @ d_true, pairs=pairs, d_true=d_true)


def test_responses_are_half_a_delta_a():
    e = synthetic_export()
    for n in range(0, len(e["A"]), 7):
        a = e["A"][n]
        assert e["R"][n] == pytest.approx(0.5 * a @ e["D2"] @ a, rel=1e-10)


def test_deterministic_deck_recovers_the_planted_block():
    e = synthetic_export()
    curve = C.rho_curve(e, C.order_p0(e), stride=2)
    n10 = C.k_off_at(curve, 0.10, e["M"], key=3)
    assert n10 is not None, curve[-1]
    assert curve[-1][3] < 0.05                                            # with the whole deck the off-diagonal block is essentially exact


def test_oracle_ordering_is_no_worse_than_hashed_order():
    e = synthetic_export()
    p0 = C.rho_curve(e, C.order_p0(e), stride=2)
    orc = C.rho_curve(e, C.order_oracle(e), stride=2)
    k0 = C.k_off_at(p0, 0.10, e["M"], key=3)
    k1 = C.k_off_at(orc, 0.10, e["M"], key=3)
    assert k0 is not None and k1 is not None and k1 <= k0, (k0, k1)


def test_ordering_is_a_permutation_of_the_same_pool():
    e = synthetic_export()
    p0, orc = C.order_p0(e), C.order_oracle(e)
    assert sorted(p0.tolist()) == sorted(orc.tolist()) and len(set(p0.tolist())) == len(p0)
    assert not any(e["holdout"][n] for n in p0) and all(e["kinds"][n] != "single" for n in p0)


def test_split_is_hashed_and_parents_are_evaluation():
    assert C.split_of("A_8448043181", "A") == "eval_parents"
    s = [C.split_of(f"B_{i:010d}", "B") for i in range(2000)]
    frac = {k: s.count(k) / len(s) for k in ("train", "val", "eval")}
    assert abs(frac["train"] - 0.7) < 0.05 and abs(frac["val"] - 0.1) < 0.03 and abs(frac["eval"] - 0.2) < 0.04
