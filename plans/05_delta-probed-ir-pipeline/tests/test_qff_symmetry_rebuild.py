"""probes/qff_symmetry_rebuild.py on exactly symmetric data (13 Oct 2026): a Morse pair potential over all atom pairs of staggered ethane
(D3d: degenerate pairs, and non-degenerate modes that are not totally symmetric) has analytic Hessians with no integration grid, so the
rebuilt set must give the direct set's force field up to the finite-difference truncation the two routes share. This separates the method
from the DFT grid's lack of symmetry (on benzene's B3LYP set of 21 Sep the pair rebuild moved Δ_anh by up to 1.06 cm⁻¹)."""
import json
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "probes"))
sys.path.insert(0, os.path.join(ROOT, "src"))
import qff_symmetry_rebuild as R  # noqa: E402

from dpir.qff import harmonic, load_results, qff_from_records  # noqa: E402

ANG = 1 / 0.529177210903


def _ethane():
    cc, ch = 1.53 * ANG, 1.09 * ANG
    tet = np.arccos(-1 / 3)
    x = [[0, 0, cc / 2], [0, 0, -cc / 2]]
    for k in range(3):
        phi = 2 * np.pi * k / 3
        x.append([ch * np.sin(np.pi - tet) * np.cos(phi), ch * np.sin(np.pi - tet) * np.sin(phi), cc / 2 + ch * np.cos(np.pi - tet) * -1])
    for k in range(3):
        phi = 2 * np.pi * k / 3 + np.pi / 3
        x.append([ch * np.sin(np.pi - tet) * np.cos(phi), ch * np.sin(np.pi - tet) * np.sin(phi), -cc / 2 - ch * np.cos(np.pi - tet) * -1])
    return ["C", "C"] + ["H"] * 6, np.array(x, float)


def _hessian(x, pairs, r0, D=0.2, a=1.2):
    """Analytic Hessian of Σ D (1 − exp(−a (r − r0)))² over the pairs."""
    n = len(x)
    H = np.zeros((3 * n, 3 * n))
    for (i, j), rr in zip(pairs, r0, strict=True):
        v = x[i] - x[j]
        r = np.linalg.norm(v)
        u = v / r
        e = np.exp(-a * (r - rr))
        f1 = 2 * D * a * e * (1 - e)
        f2 = 2 * D * a * a * e * (2 * e - 1)
        B = f2 * np.outer(u, u) + f1 / r * (np.eye(3) - np.outer(u, u))
        for p, q, s in ((i, i, 1), (j, j, 1), (i, j, -1), (j, i, -1)):
            H[3 * p:3 * p + 3, 3 * q:3 * q + 3] += s * B
    return H


def _write(path, symbols, x, H):
    json.dump({"driver": "hessian", "molecule": {"symbols": symbols, "geometry": x.ravel().tolist()}, "return_result": H.ravel().tolist()},
              open(path, "w", encoding="utf-8"))


def _direct_set(root, disp):
    sym, x0 = _ethane()
    n = len(sym)
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    r0 = [np.linalg.norm(x0[i] - x0[j]) for i, j in pairs]
    H0 = _hessian(x0, pairs, r0)
    harm = harmonic(H0, sym, x0.ravel())
    root.mkdir()
    _write(root / "ref.json", sym, x0, H0)
    for k in range(harm.A.shape[1]):
        for s, tag in ((1, "p"), (-1, "m")):
            xk = x0 + s * disp * harm.A[:, k].reshape(n, 3)
            _write(root / f"mode{k:02d}_{tag}.json", sym, xk, _hessian(xk, pairs, r0))
    return root


def _errors(tmp_path, disp, kinds):
    d = _direct_set(tmp_path / f"direct_{disp}_{kinds[0]}", disp)
    log = R.rebuild(str(d), str(tmp_path / f"rebuilt_{disp}_{kinds[0]}"), disp, kinds)
    q_d = qff_from_records(load_results(str(d)), disp, allow_noisy=True)[0]
    q_r = qff_from_records(load_results(str(tmp_path / f"rebuilt_{disp}_{kinds[0]}")), disp, allow_noisy=True)[0]
    return log, q_d, np.abs(q_r.phi3 - q_d.phi3).max(), np.abs(q_r.phi4 - q_d.phi4).max()


def test_the_pm_rebuild_is_exact_on_symmetric_data(tmp_path):
    log, q_d, e3, e4 = _errors(tmp_path, 0.10, ("pm",))
    assert log["pm_rebuilt"]                                         # D3d ethane has non-degenerate modes that are not totally symmetric
    assert e3 < 1e-8 * np.abs(q_d.phi3).max() and e4 < 1e-8 * np.abs(q_d.phi4).max()


def test_the_pair_rebuild_is_exact_up_to_the_shared_truncation(tmp_path):
    """The pair rebuild fits derivatives from images, so it carries the finite-difference truncation in another combination: its error is
    below the direct set's own route spreads and falls as δ² (×4 from δ = 0.10 to 0.05)."""
    log, q_d, e3, e4 = _errors(tmp_path, 0.10, ("pairs",))
    assert log["pairs_rebuilt"]
    assert e3 <= q_d.cubic_spread.max() and e4 <= q_d.route_disagreement.max()
    _, _, e3h, e4h = _errors(tmp_path, 0.05, ("pairs",))
    assert 3.5 < e3 / e3h < 4.5 and 3.5 < e4 / e4h < 4.5
