"""Design check (`m05/design_check.py`, 28 September 2026): target extremes, the body probe at those extremes, the source-against-target transfer
table, and the CLI — on synthetic water and random clusters only; no corpus, no QM9."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

torch = pytest.importorskip("torch")
M05 = Path(__file__).resolve().parents[1] / "modules" / "05_support_predictor" / "m05"
sys.path.insert(0, str(M05))
import design_check as DC  # noqa: E402
import rungC_equivariant as RC  # noqa: E402

torch.set_num_threads(1)


def _cluster(n_atoms: int, seed: int, spread_bohr: float = 3.0, heavy: int = 6) -> dict:
    rng = np.random.default_rng(seed)
    Z = np.full(n_atoms, 6)
    Z[0] = heavy
    A = rng.normal(size=(3 * n_atoms, 3 * n_atoms)) * 0.01
    return {"id": f"c{n_atoms}_{seed}", "Z": Z, "pos": rng.uniform(-spread_bohr, spread_bohr, size=(n_atoms, 3)), "H_low": A + A.T}


def _mols() -> dict:
    return {"water": RC.water(), "c8": _cluster(8, 1), "c24": _cluster(24, 2), "c12s": _cluster(12, 3, heavy=16)}


def test_stats_and_extremes():
    s = DC.molecule_stats(RC.water())
    assert s["n_atoms"] == 3 and s["mean_degree"] == 2.0 and s["max_degree"] == 2 and s["max_Z"] == 8 and s["elements"] == [1, 8]
    stats = {k: DC.molecule_stats(m) for k, m in _mols().items()}
    ext = DC.extremes(stats)
    assert ext["n_atoms_min"] == "water" and ext["n_atoms_max"] == "c24" and ext["max_degree_max"] == "c24" and ext["max_Z_max"] == "c12s"
    assert set(ext) == {f"{p}_{w}" for p, w in DC.EXTREMES}


def test_probe_flags_the_sum_body_and_passes_the_mean_body():
    """The 27 Sep incident at design time: across 7 and 23 neighbours the sum body's feature scale moves, the mean body's does not."""
    mols = {"c8": _cluster(8, 1), "c24": _cluster(24, 2)}
    ratios = {}
    for agg in RC.AGGREGATIONS:
        torch.manual_seed(0)
        probe = DC.probe_body(RC.DeltaHessianModel(aggregation=agg), mols, list(mols))
        v = DC.verdict(probe, limit_abs=1e3, limit_ratio=1.2)
        ratios[agg] = v["scale_ratio"]
        assert v["finite"] and v["worst_output"] < 1e3
        assert v["pass"] == (agg == "mean"), (agg, v)
    assert ratios["mean"] < 1.1 < ratios["sum"]


def test_non_finite_body_fails():
    body = RC.DeltaHessianModel()
    with torch.no_grad():
        body.emb.weight.mul_(float("nan"))
    v = DC.verdict(DC.probe_body(body, {"w": RC.water()}, ["w"]), 1e3, 3.0)
    assert not v["finite"] and not v["pass"]


def test_transfer_table_marks_targets_outside_the_source():
    src = DC.ranges({k: DC.molecule_stats(m) for k, m in {"water": RC.water(), "c8": _cluster(8, 1)}.items()})     # 3–8 atoms, H C O
    tgt = DC.ranges({k: DC.molecule_stats(m) for k, m in {"c8b": _cluster(8, 4), "c12s": _cluster(12, 3, heavy=16)}.items()})
    rows = {r["property"]: r for r in DC.transfer_table(src, tgt)}
    assert not rows["n_atoms"]["inside"] and not rows["max_degree"]["inside"]
    assert not rows["elements"]["inside"] and rows["elements"]["missing"] == [16]
    same = {r["property"]: r for r in DC.transfer_table(src, src)}
    assert all(r["inside"] for r in same.values())


def test_cli_runs_on_a_synthetic_directory(tmp_path):
    """End to end on two fabricated corpus folders: the mean body passes, the record files exist, and --help names every switch."""
    for mid, n in (("A_small", 4), ("A_big", 20)):
        d = tmp_path / mid
        d.mkdir()
        m = _cluster(n, 7)
        (d / "geometry.json").write_text(__import__("json").dumps({"symbols": ["C"] * n, "coords_bohr": m["pos"].tolist(), "masses_amu": [12.0] * n}))
        for name in ("hessian_b3lyp.npz", "hessian_wb97x.npz"):
            np.savez(d / name, H_projected=m["H_low"])
    out = tmp_path / "check"
    r = subprocess.run([sys.executable, str(M05 / "design_check.py"), str(tmp_path), "--out", str(out), "--aggregation", "mean"],
                       capture_output=True, text=True, timeout=300, check=False)
    assert r.returncode == 0, r.stdout + r.stderr
    assert (out.parent / "check.md").exists() and (out.parent / "check.json").exists() and "PASS" in r.stdout
    h = subprocess.run([sys.executable, str(M05 / "design_check.py"), "--help"], capture_output=True, text=True, timeout=120, check=False)
    assert h.returncode == 0, h.stderr
    assert all(f in h.stdout for f in ("--checkpoint", "--source-qm9", "--limit-ratio", "--limit-abs", "--aggregation {sum,mean}"))
