"""`build_deck(..., pool=)` (28 Sep 2026, wide-deck pre-registration): the wide pool holds a two-mode ± pair for every mode pair, contains the band deck's
pairs, keeps the same multi-mode block and single block, and leaves the registered band deck's hash untouched."""
import sys
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
import dryrun_dft_delta_recovery as P  # noqa: E402

A = {"molecule": "toy", "M": 7, "freq_low_cm": [400.0, 450.0, 700.0, 1000.0, 1010.0, 1500.0, 3000.0]}


def two_mode_pairs(deck):
    return sorted(tuple(p["modes"]) for p in deck["patterns"] if p["kind"] == "two-mode" and p["a"][p["modes"][1]] > 0)


def test_wide_pool_has_every_pair_and_contains_the_band_deck():
    band, wide = P.build_deck(A, quick=False), P.build_deck(A, quick=False, pool="all")
    M = A["M"]
    assert len(two_mode_pairs(wide)) == M * (M - 1) // 2
    assert set(two_mode_pairs(band)) < set(two_mode_pairs(wide))
    assert sum(p["kind"] == "two-mode" for p in wide["patterns"]) == M * (M - 1)          # ± for every pair
    assert wide["deck_pool"] == "all" and "deck_pool" not in band


def test_single_and_multi_blocks_are_identical_and_the_band_hash_is_stable():
    band, wide, again = P.build_deck(A, quick=False), P.build_deck(A, quick=False, pool="all"), P.build_deck(A, quick=False, pool="band")
    multis = lambda d: sorted(tuple(p["a"]) for p in d["patterns"] if p["kind"] == "multi")  # noqa: E731  (the deck order is a shuffle of all off-diagonal patterns)
    assert multis(band) == multis(wide) and len(multis(band)) == 4 * A["M"]
    assert sorted(p["modes"][0] for p in band["patterns"] if p["kind"] == "single") == sorted(p["modes"][0] for p in wide["patterns"] if p["kind"] == "single")
    assert band["deck_hash"] == again["deck_hash"] != wide["deck_hash"]
    n_off = sum(p["kind"] in ("two-mode", "multi") for p in wide["patterns"])
    assert sum(p["holdout"] for p in wide["patterns"]) == round(P.F_H * n_off)
