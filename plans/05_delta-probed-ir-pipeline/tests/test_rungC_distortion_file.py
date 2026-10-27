"""`--distortion-file` (the anchor price, TASKS 82, 27 Oct 2026): the label's family blocks rescaled in two parts — the mean first-order
shift and the rest — per molecule context; the file is checked before any data is loaded, the one-factor form of proxy check (a) is the
special case with equal parts, and the trainer refuses a molecule without a context before it trains."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig, load_distortion  # noqa: E402

FAMS = ["ring-ip", "CH-stretch", "CH-oop", "other"]


def cfg(**kw) -> TrainConfig:
    return TrainConfig(**{"molecules": "m", "out_prefix": "out/p", **kw})


def molecule(n_atoms: int = 5, seed: int = 0) -> dict:
    """Masses, an orthonormal mass-weighted mode basis of 3N − 6 vectors with four families, positive eigenvalues w, a symmetric ΔH."""
    rng = np.random.default_rng(seed)
    n = 3 * n_atoms
    Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    V = Q[:, : n - 6]
    A = rng.normal(size=(n, n))
    return {"masses": rng.uniform(1.0, 16.0, n_atoms), "V": V, "w": rng.uniform(0.5, 9.0, n - 6), "family": (FAMS * n)[: n - 6], "dH": A + A.T}


def mode_basis(m: dict, dH: np.ndarray) -> np.ndarray:
    sq = np.sqrt(np.repeat(m["masses"], 3))
    return m["V"].T @ (dH / np.outer(sq, sq)) @ m["V"]


def shifts(m: dict, dH: np.ndarray) -> np.ndarray:
    """First-order shifts up to a constant: B_kk / 2ω_k."""
    return np.diag(mode_basis(m, dH)) / (2 * np.sqrt(m["w"]))


def write(tmp_path: Path, body: dict) -> str:
    p = tmp_path / "distortion.json"
    p.write_text(json.dumps(body), encoding="utf-8")
    return str(p)


GOOD = {"about": "test", "contexts": {"x": "single", "y": "fused"},
        "families": {"CH-oop": {"mean": {"single": 0.0, "fused": -0.5}, "rest": -0.5}, "other": {"mean": -1.5, "rest": -0.3}}}


def test_the_one_factor_form_is_the_old_formula():
    m = molecule()
    sq = np.sqrt(np.repeat(m["masses"], 3))
    X = m["dH"] / np.outer(sq, sq)
    old = X.copy()
    for name, s in {"CH-oop": -0.43, "other": 2.0}.items():
        Vf = m["V"][:, np.array(m["family"]) == name]
        old += (s - 1.0) * Vf @ (Vf.T @ X @ Vf) @ Vf.T
    np.testing.assert_allclose(RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"CH-oop": -0.43, "other": 2.0}),
                               old * np.outer(sq, sq), rtol=0, atol=1e-12)


@pytest.mark.parametrize(("a", "b"), [(0.0, -0.5), (-1.5, -0.3), (0.7, 0.7)])
def test_the_mean_shift_takes_one_factor_and_the_rest_the_other(a, b):
    m = molecule(seed=1)
    out = RT.distort_blocks(m["dH"], m["masses"], m["V"], m["w"], m["family"], {"CH-oop": (a, b)})
    on = np.array(m["family"]) == "CH-oop"
    k0, k1 = shifts(m, m["dH"])[on], shifts(m, out)[on]
    np.testing.assert_allclose(k1.mean(), a * k0.mean(), atol=1e-10)                       # the family's mean shift
    np.testing.assert_allclose(k1 - k1.mean(), b * (k0 - k0.mean()), atol=1e-10)           # the centred shifts
    B0, B1 = mode_basis(m, m["dH"]), mode_basis(m, out)
    off = np.ix_(on, on)
    np.testing.assert_allclose((B1[off] - np.diag(np.diag(B1[off]))), b * (B0[off] - np.diag(np.diag(B0[off]))), atol=1e-10)
    np.testing.assert_allclose(B1[np.ix_(~on, ~on)], B0[np.ix_(~on, ~on)], atol=1e-10)    # the other families
    np.testing.assert_allclose(B1[np.ix_(on, ~on)], B0[np.ix_(on, ~on)], atol=1e-10)      # the blocks between families
    np.testing.assert_allclose(out, out.T, atol=1e-10)


def test_equal_factors_scale_the_whole_block_whatever_the_frequencies():
    m = molecule(seed=2)
    one = RT.distort_blocks(m["dH"], m["masses"], m["V"], m["w"], m["family"], {"other": (-1.2, -1.2)})
    np.testing.assert_allclose(one, RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"other": -1.2}), atol=1e-10)


def test_a_family_without_modes_is_left_alone():
    m = molecule(seed=3)
    m["family"] = ["ring-ip"] * len(m["family"])
    np.testing.assert_allclose(RT.distort_blocks(m["dH"], m["masses"], m["V"], m["w"], m["family"], {"CH-oop": (0.0, -0.5)}), m["dH"], atol=1e-12)


def test_a_good_file_gives_factors_per_molecule(tmp_path):
    d = load_distortion(write(tmp_path, GOOD))
    assert d.factors("x") == {"CH-oop": (0.0, -0.5), "other": (-1.5, -0.3)}
    assert d.factors("y") == {"CH-oop": (-0.5, -0.5), "other": (-1.5, -0.3)}
    assert d.missing({"x", "z"}) == ["z"]
    assert cfg(distortion_file=write(tmp_path, GOOD)).distortion == d
    assert cfg().distortion is None


@pytest.mark.parametrize(("change", "reason"), [
    ({"families": {"CH-op": {"mean": 1.0, "rest": 1.0}}}, "not of"),
    ({"families": {"CH-oop": {"mean": {"single": 0.0}, "rest": 1.0}}}, "no factor for the contexts"),
    ({"families": {"CH-oop": {"mean": float("inf"), "rest": 1.0}}}, "not finite"),
    ({"families": {"CH-oop": {"mean": 1.0}}}, "rest"),
    ({"extra": 1}, "extra"),
])
def test_a_wrong_file_is_refused_before_loading(tmp_path, change, reason):
    with pytest.raises(ValueError, match=reason):
        cfg(distortion_file=write(tmp_path, {**GOOD, **change}))


def test_a_missing_file_and_the_two_distortions_together_are_refused(tmp_path):
    with pytest.raises(ValueError, match="no such file"):
        cfg(distortion_file=str(tmp_path / "none.json"))
    with pytest.raises(ValueError, match="choose one"):
        cfg(distortion_file=write(tmp_path, GOOD), family_scale="CH-oop=-0.43")


def corpus_of(m: dict, ids: list[str]) -> SimpleNamespace:
    entry = {"masses": m["masses"], "V": m["V"], "w": m["w"], "family": m["family"]}
    return SimpleNamespace(pool=ids, sizes=[len(ids)], tests={"a": []}, mols=dict.fromkeys(ids, entry))


def test_the_trainer_distorts_each_molecule_by_its_context(monkeypatch, tmp_path):
    m = molecule(seed=4)
    seen = {}
    monkeypatch.setattr(RT, "load_molecule", lambda d, use_analytic: {"dH_true": m["dH"]})
    monkeypatch.setattr(RT, "molecule_tensors", lambda i, mm, mol, d, c, cache, res: seen.setdefault(i, mm["dH_true"]))
    RT.build_tensors(cfg(distortion_file=write(tmp_path, GOOD), out_prefix=str(tmp_path / "p")), corpus_of(m, ["x", "y"]))
    for i, ch_oop in (("x", (0.0, -0.5)), ("y", (-0.5, -0.5))):
        expected = RT.distort_blocks(m["dH"], m["masses"], m["V"], m["w"], m["family"], {"CH-oop": ch_oop, "other": (-1.5, -0.3)})
        np.testing.assert_allclose(seen[i], expected, atol=1e-12)


def test_the_trainer_refuses_a_molecule_without_a_context_before_any_label(monkeypatch, tmp_path):
    m = molecule(seed=5)
    loaded = []
    monkeypatch.setattr(RT, "load_molecule", lambda d, use_analytic: loaded.append(d) or {"dH_true": m["dH"]})
    with pytest.raises(ValueError, match="no context for 1 molecules"):
        RT.build_tensors(cfg(distortion_file=write(tmp_path, GOOD), out_prefix=str(tmp_path / "p")), corpus_of(m, ["x", "z"]))
    assert loaded == []
