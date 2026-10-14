"""probes/s2_read.py (14 Oct 2026): the registered S2 read — routes (b) and (c), leave one scaffold out, amendment 1's curve and verdicts —
on synthetic molecules whose Δ_anh is known, and the loader on S1's benzene directory when it is present."""
import shutil
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import s2_read as R  # noqa: E402

S1_G = PLAN / "probes/results_m1/s1_anharmonic_benzene_2026-10-13/s1_benzene/G"
COEF = {"CH-stretch": (-150.0, 3.0), "CH-oop": (-5.0, -6.0), "ring-ip": (-5.0, -12.0), "other": (-2.0, -8.0)}
OMEGA_RANGE = {"CH-stretch": (1700, 1990), "CH-oop": (700, 1000), "ring-ip": (1000, 1700), "other": (560, 1500)}


def molecule(rng, noise=0.0, fams=R.FAMILIES):
    """A synthetic molecule: modes of the given families inside the window, Δ = a_f + b_f ω/1000 + 4 h − 3 o (+ noise)."""
    fam = np.array([f for f in fams for _ in range(4)])
    omega = np.array([rng.uniform(*OMEGA_RANGE[f]) for f in fam])
    h, o = rng.uniform(0, 1, len(fam)), rng.uniform(0, 1, len(fam))
    delta = np.array([COEF[f][0] + COEF[f][1] * w / 1000 for f, w in zip(fam, omega, strict=True)]) + 4 * h - 3 * o + noise * rng.standard_normal(len(fam))
    return {"omega": omega, "delta": delta, "family": fam, "h": h, "o": o, "planar": True}


def dataset(n_scaf=12, per=2, noise=0.0, seed=1):
    rng = np.random.default_rng(seed)
    return {f"s{i:02d}": [molecule(rng, noise) for _ in range(per)] for i in range(n_scaf)}


def test_route_b_recovers_an_exact_linear_shift_and_beats_the_family_constants():
    rows = R.curve(dataset(), n_subsets=5)
    a = rows["all"]
    assert a["b"] < 0.05 and a["c"] > 1.0 and a["unseen_family_modes"] == 0
    v = R.verdict(rows)
    assert v["line1_b_le_0.8c"] and "b" in v["licensed"] and v["reading"].startswith("line 2 met")


def test_the_curve_is_deterministic_and_has_every_k():
    d = dataset(noise=2.0)
    r1, r2 = R.curve(d, n_subsets=5), R.curve(d, n_subsets=5)
    assert r1 == r2 and set(r1) == {"4", "6", "8", "10", "all"} and r1["all"]["k"] == 11
    assert all(r1[k]["b_se"] > 0 for k in ("4", "6", "8", "10"))


def test_a_family_missing_from_training_is_predicted_by_the_training_mean_and_counted():
    rng = np.random.default_rng(3)
    train = R.concat([molecule(rng, fams=("CH-stretch", "ring-ip"))])
    test = R.concat([molecule(rng, fams=("ring-ip", "other"))])
    pb, pc, unseen = R.fit_predict(train, test)
    other = test["family"] == "other"
    assert unseen == other.sum() == 4
    assert np.allclose(pb[other], train["delta"].mean()) and np.allclose(pc[other], train["delta"].mean())
    assert np.allclose(pc[~other], train["delta"][train["family"] == "ring-ip"].mean())


def test_still_learning_needs_twice_the_combined_se_and_a_last_step_down():
    rows = {"6": {"b": 5.0, "b_se": 0.3}, "10": {"b": 4.2, "b_se": 0.2}, "all": {"b": 4.0, "b_se": 0.0}}
    assert R.still_learning(rows, "b")                       # 5.0 − 2·0.3 = 4.4 > 4.0, and 4.0 < 4.2
    rows["6"]["b_se"] = 0.6
    assert not R.still_learning(rows, "b")                   # 5.0 − 1.2 = 3.8 < 4.0
    rows["6"]["b_se"], rows["10"]["b"] = 0.3, 3.9
    assert not R.still_learning(rows, "b")                   # the last step went up


def test_a_missed_line_while_learning_reads_as_data_limited_with_an_extrapolation():
    a, b, c = 2.0, 12.0, 0.8
    rows = {str(k): {"b": a + b * k ** -c, "b_se": 0.05, "c": 9.0, "c_se": 0.05} for k in (4, 6, 8, 10)}
    rows["all"] = {"b": a + b * 11 ** -c, "b_se": 0.0, "c": 9.0, "c_se": 0.0, "k": 11}
    v = R.verdict(rows)
    assert rows["all"]["b"] > 3.0 and v["reading"].startswith("line 2 missed, route b still learning")
    e = v["extrapolation"]
    assert e["fit"]["a"] == pytest.approx(a, abs=1e-3) and e["scaffolds_needed"] == pytest.approx((b / (3.0 - a)) ** (1 / c), rel=1e-3)


def test_a_flat_curve_reads_as_search_first():
    rows = {str(k): {"b": 4.0, "b_se": 0.1, "c": 4.5, "c_se": 0.1} for k in (4, 6, 8, 10)}
    rows["all"] = {"b": 4.0, "b_se": 0.0, "c": 4.5, "c_se": 0.0, "k": 11}
    v = R.verdict(rows)
    assert v["reading"].startswith("line 2 missed, route b flat") and "(b) stops" in v["line1_reading"]


@pytest.mark.skipif(not (S1_G / "qff_report.npz").exists(), reason="S1's benzene results are not on this machine")
def test_the_loader_reads_s1_benzene_and_excludes_noisy_or_unfinished(tmp_path):
    rec, why = R.load_molecule(str(S1_G))
    assert why == "" and rec["planar"] and len(rec["omega"]) == 30
    assert (rec["family"] == "CH-oop").sum() == 6 and (rec["family"] == "CH-stretch").sum() == 6
    assert np.all((rec["h"] >= 0) & (rec["h"] <= 1 + 1e-9)) and np.all((rec["o"] >= 0) & (rec["o"] <= 1 + 1e-9))
    noisy = tmp_path / "noisy"
    shutil.copytree(S1_G, noisy, ignore=shutil.ignore_patterns("hess", "stubs", "refhess", "refstub"))
    (noisy / "NOISY").touch()
    assert R.load_molecule(str(noisy)) == (None, "NOISY (noise rule)")
    (noisy / "NOISY").unlink()
    (noisy / "qff_report.npz").unlink()
    assert R.load_molecule(str(noisy))[0] is None
