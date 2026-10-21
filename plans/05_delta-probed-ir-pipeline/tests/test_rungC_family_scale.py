"""`--family-scale` (proxy check (a), 21 Oct 2026): the factor list is parsed and checked before any data is loaded, the distortion scales
exactly the named families' diagonal blocks in the mode basis, and the trainer applies it to the label every target is derived from."""
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import rungC_train as RT  # noqa: E402
from rungC_config import TrainConfig, parse_family_scale  # noqa: E402


def cfg(**kw) -> TrainConfig:
    return TrainConfig(**{"molecules": "m", "out_prefix": "out/p", **kw})


def test_the_factor_list_is_parsed():
    assert parse_family_scale("CH-oop=-0.43,other=-1.16") == {"CH-oop": -0.43, "other": -1.16}
    assert cfg(family_scale="ring-ip=0.5").family_scales == {"ring-ip": 0.5}
    assert cfg().family_scales == {}


@pytest.mark.parametrize(("text", "reason"), [("CH-op=-0.4", "a family of"), ("CH-oop", "a family of"), ("other=1,other=2", "twice"),
                                              ("other=x", "not a number"), ("other=inf", "not finite"), ("other=nan", "not finite")])
def test_a_wrong_factor_list_is_refused_before_loading(text, reason):
    with pytest.raises(ValueError, match=reason):
        cfg(family_scale=text)


def molecule(n_atoms: int = 4, seed: int = 0) -> dict:
    """Masses, an orthonormal mass-weighted mode basis of 3N − 6 vectors with four families, and a symmetric ΔH."""
    rng = np.random.default_rng(seed)
    n = 3 * n_atoms
    Q, _ = np.linalg.qr(rng.normal(size=(n, n)))
    V = Q[:, : n - 6]
    family = (["ring-ip", "CH-stretch", "CH-oop", "other"] * n)[: n - 6]
    A = rng.normal(size=(n, n))
    return {"masses": rng.uniform(1.0, 16.0, n_atoms), "V": V, "family": family, "dH": A + A.T}


def mode_basis(m: dict, dH: np.ndarray) -> np.ndarray:
    sq = np.sqrt(np.repeat(m["masses"], 3))
    return m["V"].T @ (dH / np.outer(sq, sq)) @ m["V"]


def test_only_the_named_diagonal_blocks_are_scaled():
    m = molecule()
    out = RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"CH-oop": -0.5, "other": 2.0})
    K0, K1 = mode_basis(m, m["dH"]), mode_basis(m, out)
    fam = np.array(m["family"])
    expected = K0.copy()
    for name, s in (("CH-oop", -0.5), ("other", 2.0)):
        on = fam == name
        expected[np.ix_(on, on)] *= s
    np.testing.assert_allclose(K1, expected, atol=1e-10)
    np.testing.assert_allclose(out, out.T, atol=1e-10)


def test_the_part_outside_the_modes_and_the_mass_unit_are_untouched():
    m = molecule(seed=1)
    out = RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"CH-oop": -0.43})
    sq = np.sqrt(np.repeat(m["masses"], 3))
    P = np.eye(len(sq)) - m["V"] @ m["V"].T                     # translations and rotations here: the complement of the modes
    np.testing.assert_allclose(P @ (out / np.outer(sq, sq)) @ P, P @ (m["dH"] / np.outer(sq, sq)) @ P, atol=1e-10)
    in_au = RT.distort_families(m["dH"], m["masses"] * 1822.9, m["V"], m["family"], {"CH-oop": -0.43})
    np.testing.assert_allclose(in_au, out, atol=1e-10)


def test_factor_one_and_no_factors_leave_the_label():
    m = molecule(seed=2)
    np.testing.assert_allclose(RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"other": 1.0}), m["dH"], atol=1e-10)
    np.testing.assert_allclose(RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {}), m["dH"], atol=1e-12)


def test_the_trainer_distorts_the_label_every_target_is_built_from(monkeypatch, tmp_path):
    m = molecule(seed=3)
    seen = {}
    monkeypatch.setattr(RT, "load_molecule", lambda d, use_analytic: {"dH_true": m["dH"]})
    monkeypatch.setattr(RT, "molecule_tensors", lambda i, mm, mol, d, c, cache, res: seen.setdefault(i, mm["dH_true"]))
    corpus = SimpleNamespace(pool=["x"], sizes=[1], tests={"a": []}, mols={"x": {"masses": m["masses"], "V": m["V"], "family": m["family"]}})
    RT.build_tensors(cfg(family_scale="CH-oop=-0.43", out_prefix=str(tmp_path / "p")), corpus)
    np.testing.assert_allclose(seen["x"], RT.distort_families(m["dH"], m["masses"], m["V"], m["family"], {"CH-oop": -0.43}))
    seen.clear()
    RT.build_tensors(cfg(out_prefix=str(tmp_path / "p")), corpus)
    assert seen["x"] is m["dH"]                                       # off: the loader's label itself
