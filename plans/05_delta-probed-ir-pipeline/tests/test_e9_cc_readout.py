"""E9 at CC level (anchor set two, R2/R3, 29 Sep 2026): the proxy path reproduces E9's objects (truth K, ΔH) for the benzene → benzonitrile pair,
the E8-npz path with the ωB97X Hessian itself gives the same numbers, a foreign geometry is refused, the element map carries benzene onto itself
and onto a ring with a nitrogen, and the corrected-frequency helper factored out of E7's basis_free is the function basis_free uses."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

PLAN = Path(__file__).resolve().parents[1]
M05 = PLAN / "modules" / "05_support_predictor" / "m05"
MOLS = PLAN / "modules" / "05_support_predictor" / "corpus" / "molecules"
sys.path.insert(0, str(M05))

rdkit = pytest.importorskip("rdkit")
pytest.importorskip("torch")
import e7_t2_sqm as T2  # noqa: E402
import e9_cc_readout as R  # noqa: E402
import embedding_skipgram_E5 as E5  # noqa: E402

BENZENE, BENZONITRILE = "A_8448043181", "A_3100da3761"
needs_corpus = pytest.mark.skipif(not (MOLS / BENZONITRILE / "hessian_wb97x.npz").exists(), reason="corpus rows not on this machine")


@needs_corpus
def test_proxy_path_is_e9s_object():
    m = R.load_molecule(MOLS, BENZONITRILE)
    lo = np.load(MOLS / BENZONITRILE / "hessian_b3lyp.npz")["H_projected"]
    hi = np.load(MOLS / BENZONITRILE / "hessian_wb97x.npz")["H_projected"]
    assert np.allclose(m["dH_true"], hi - lo)
    assert np.allclose(m["K"], E5.coupling_matrix(MOLS / BENZONITRILE), atol=1e-3)     # E5 stores float32
    assert m["high_source"].startswith("wB97X")


@needs_corpus
def test_npz_override_with_the_proxy_hessian_reproduces_the_proxy(tmp_path):
    z = np.load(MOLS / BENZONITRILE / "hessian_wb97x.npz")
    g = json.load(open(MOLS / BENZONITRILE / "geometry.json"))
    p = tmp_path / "hessian_ccsd_t.npz"
    np.savez(p, H_projected=z["H_projected"], coords_bohr=np.asarray(g["coords_bohr"]))
    a, b = R.load_molecule(MOLS, BENZONITRILE), R.load_molecule(MOLS, BENZONITRILE, p)
    assert np.array_equal(a["K"], b["K"]) and b["high_source"].startswith("hessian_ccsd_t.npz")
    np.savez(p, H_projected=z["H_projected"], coords_bohr=np.asarray(g["coords_bohr"]) + 0.01)
    with pytest.raises(ValueError, match="geometry differs"):
        R.load_molecule(MOLS, BENZONITRILE, p)


@needs_corpus
def test_cli_proxy_pair(tmp_path):
    out = tmp_path / "e9cc"
    assert R.main([str(MOLS), BENZENE, BENZONITRILE, str(out), "--radii", "0,2", "--label", "test"]) == 0
    res = json.load(open(str(out) + ".json"))
    v = res["variants"]
    assert v["exact"]["corrected_freq_rms"] < 1e-6 and v["zero"]["corrected_freq_rms"] > 1.0
    assert v["probe_only_r2"]["dH_residual_ratio"] <= v["probe_only_r0"]["dH_residual_ratio"] + 1e-12   # more probed columns, never worse
    assert v["transfer_probe_r2"]["column_fraction"] > v["transfer_probe_r0"]["column_fraction"]
    assert v["transfer_only_r0"]["column_fraction"] == 2 / 13 and v["transfer_probe_r2"]["n_near"] == 5   # N, C(N); + ipso and both ortho
    assert len(v["transfer_probe_r2"]["per_mode_error_cm"]) == 3 * 13 - 6
    assert res["verdict_r2"] in ("PASS", "BETWEEN", "FAIL") and (out.parent / "e9cc.md").read_text(encoding="utf-8").startswith("# E9 at CC level")


def _ring(smiles):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    m = Chem.AddHs(Chem.MolFromSmiles(smiles))
    AllChem.EmbedMolecule(m, randomSeed=7)
    AllChem.MMFFOptimizeMolecule(m)
    x = np.asarray(m.GetConformer().GetPositions()) / 0.529177210903
    return x, [a.GetSymbol() for a in m.GetAtoms()]


def test_element_map_benzene_onto_itself_and_onto_pyridine():
    xB, sB = _ring("c1ccccc1")
    xP, sP = _ring("c1ccncc1")
    mp, R_, subst, D = R.element_map("c1ccccc1", "c1ccccc1", xB, xB, sB, sB)
    assert len(mp) == 12 and subst == [] and sorted(mp.values()) == list(range(12))
    mp, R_, subst, D = R.element_map("c1ccccc1", "c1ccncc1", xB, xP, sB, sP)
    assert len(mp) == 11                                    # 6 ring atoms + 5 hydrogens; the H that the nitrogen lost is unmapped
    assert sorted(mp[k] for k in range(6)) == list(range(6)) and D.shape == (11, 11)
    assert R.atom_map("c1ccccc1", "c1ccncc1", xB, xP, sB, sP) is None    # E9's element-strict map refuses the pair; that is why the wildcard map exists


@needs_corpus
def test_molecule_features_arrays_reproduce_the_files():
    from learning_curve_layerA import molecule_features
    d = MOLS / BENZONITRILE
    a = molecule_features(d)
    b = molecule_features(d, lo=np.load(d / "hessian_b3lyp.npz")["H_projected"], hi=np.load(d / "hessian_wb97x.npz")["H_projected"])
    assert a["family"] == b["family"] and np.allclose(a["freq"], b["freq"]) and np.allclose(a["tokens"], b["tokens"]) and np.allclose(a["target"], b["target"])


@pytest.mark.skipif(not (MOLS / BENZENE / "hessian_wb97x_analytic.npz").exists(), reason="benzene's analytic pair not on this machine")
def test_use_analytic_takes_the_pyscf_pair_and_refuses_a_folder_without_it():
    fd, an = R.load_molecule(MOLS, BENZENE), R.load_molecule(MOLS, BENZENE, use_analytic=True)
    assert an["low_source"].startswith("B3LYP pyscf analytic") and "analytic" in an["high_source"] and "psi4" in fd["high_source"]
    assert not np.allclose(an["K"], fd["K"], atol=1e-3)                       # the two routes differ on benzene (the psi4 FD pair is noise-dominated)
    if not (MOLS / BENZONITRILE / "hessian_b3lyp_analytic.npz").exists():
        with pytest.raises(FileNotFoundError):
            R.load_molecule(MOLS, BENZONITRILE, use_analytic=True)


def test_run_export_select_dirs():
    sys.path.insert(0, str(PLAN / "modules" / "standout_pattern_proposer"))
    from run_export import select_dirs
    dirs = [Path("x") / n for n in ("A_1", "A_2", "B_3")]
    assert select_dirs(dirs, None) == dirs and select_dirs(dirs, "") == dirs
    assert [d.name for d in select_dirs(dirs, "B_3, A_1")] == ["A_1", "B_3"] and select_dirs(dirs, "nope") == []


def test_corrected_frequencies_is_what_basis_free_uses():
    rng = np.random.default_rng(0)
    M = 5
    w = np.linspace(500, 1500, M)
    K = rng.normal(size=(M, M))
    K = 0.5 * (K + K.T)
    m = {"freq": w, "family": ["ring-ip"] * 3 + ["other"] * 2, "K": K}
    wt, _ = T2.corrected_frequencies(m, K)
    wp, _ = T2.corrected_frequencies(m, 0.5 * K)
    r = T2.basis_free({"x": 0.5 * K}, {"x": m}, ["x"])
    assert np.isclose(r["corrected_freq_rms"], np.sqrt(np.mean((wp - wt) ** 2)))
    assert np.allclose(T2.corrected_frequencies(m, np.zeros_like(K))[0], w)      # K = 0 leaves the harmonic frequencies
