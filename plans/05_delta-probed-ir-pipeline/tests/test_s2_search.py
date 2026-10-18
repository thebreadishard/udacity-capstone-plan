"""probes/s2_search.py on synthetic molecules: ridge-F1 is route (b) of the registered read, a label driven by a local feature is found
by F2 and not by F1, the nested read only chooses on inner folds, and the network stops early."""
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "src"))
import s2_read as R  # noqa: E402
import s2_search as S  # noqa: E402

pytest.importorskip("sklearn")


def molecule(rng, local_effect=0.0):
    """Four modes per family in the window; Δ = family term + local_effect · (C–H quartet share)² — a label F1 cannot see."""
    fam = np.array([f for f in ("CH-oop", "ring-ip", "other") for _ in range(4)])
    omega = np.array([rng.uniform(700, 1000) if f == "CH-oop" else rng.uniform(1000, 1700) if f == "ring-ip" else rng.uniform(560, 1500)
                      for f in fam])
    h, o = rng.uniform(0, 1, len(fam)), rng.uniform(0, 1, len(fam))
    local = rng.uniform(0, 1, (len(fam), len(R.FAMILIES) * 0 + 9))
    delta = np.where(fam == "CH-oop", -10.0, -20.0) - 5 * omega / 1000 + 3 * h + local_effect * local[:, 4] ** 2
    return {"omega": omega, "delta": delta, "family": fam, "h": h, "o": o, "local": local, "prox": rng.uniform(0, 3, (len(fam), 2))}


def dataset(n_scaf=7, local_effect=0.0, seed=2):
    rng = np.random.default_rng(seed)
    return {f"s{i}": [molecule(rng, local_effect) for _ in range(2)] for i in range(n_scaf)}


def test_ridge_f1_is_route_b_of_the_registered_read():
    d = dataset(local_effect=8.0)
    folds = S.loso_predictions(S.Config("ridge", "F1"), d, sorted(d))
    t, b, _c, _f, _u = R.loso(d)
    ours_t = np.concatenate([folds[s]["truth"] for s in sorted(d)])
    ours_p = np.concatenate([folds[s]["pred"] for s in sorted(d)])
    assert np.allclose(ours_t, t) and np.allclose(ours_p, b)


def test_a_local_feature_label_is_found_by_f2_not_f1():
    d = dataset(local_effect=30.0)
    f1 = S.family_rms(S.loso_predictions(S.Config("ridge", "F1"), d, sorted(d)), "CH-oop")[0]
    krr = S.family_rms(S.loso_predictions(S.Config("krr", "F2", 1e-2, 1.0), d, sorted(d)), "CH-oop")[0]
    assert krr < 0.5 * f1


def test_the_nested_read_chooses_per_family_on_inner_folds():
    d = dataset(local_effect=30.0)
    res = S.nested(d, [S.Config("ridge", "F1"), S.Config("ridge", "F2"), S.Config("krr", "F2", 1e-2, 1.0)])
    assert set(res) == {"CH-oop", "ring-ip", "other"}
    assert sum(res["CH-oop"]["chosen"].values()) == len(d)
    assert "ridge-F1" not in res["CH-oop"]["chosen"]                      # F1 cannot see the quartet term, on any inner fold


def test_the_network_stops_early_and_keeps_its_best_epoch():
    d = dataset(local_effect=10.0)
    folds = S.loso_predictions(S.Config("mlp", "F2", 1e-2), d, sorted(d)[:3])
    epochs = [f["epoch"] for f in folds.values()]
    assert all(1 <= e <= S.CAP_SHARE * S.MLP_MAX_EPOCHS for e in epochs)
