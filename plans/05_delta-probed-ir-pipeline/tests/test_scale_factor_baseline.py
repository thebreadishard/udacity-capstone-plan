"""probes/scale_factor_baseline.py (TASKS 112, reading 1): the least-squares factors are exact when the shifts are a scale, the PAHdb regions
have the stated edges, the diagonal prediction is read by E6.readout like any prediction, and the lines compare family by family."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("torch")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import scale_factor_baseline as S  # noqa: E402, RUF100  (after the sys.path insert: pre-commit's pinned ruff flags it, the newer one not)

FAMS = ["CH-stretch", "CH-oop", "ring-ip", "other"]


def molecule(freq: list[float], shift: list[float], family: list[str]) -> dict:
    """A rung-B loader entry with what the read needs: B3LYP frequencies, the shift matrix K (its diagonal the first-order shifts), families."""
    return {"freq": np.array(freq), "K": np.diag(shift).astype(np.float32), "family": family}


def corpus(factor_of_family: dict[str, float]) -> dict:
    """Three molecules whose shifts are exactly (f_family − 1) ω."""
    mols = {}
    for k, base in enumerate((1.0, 1.05, 0.95)):
        freq = [3100 * base, 850 * base, 1400 * base, 400 * base]
        mols[f"m{k}"] = molecule(freq, [(factor_of_family[f] - 1) * w for f, w in zip(FAMS, freq, strict=True)], FAMS)
    return mols


def test_the_pahdb_factor_rows_are_bauschlicher_2018_table_2():
    """The 6-31G* row is our basis's; the 4-31G row (Mai's) once stood in its place in the product's baseline (TASKS 247)."""
    assert S.PAHDB_FACTORS == {"6-31G*": (0.979, 0.969, 0.960), "4-31G": (0.956, 0.952, 0.960)}


def test_pahdb_scaling_takes_the_row_of_the_basis_and_refuses_an_unknown_one():
    w = np.array([800.0, 1600.0, 3000.0])
    assert S.pahdb_scaled(w, "6-31G*", S.TABLE2_REGION_EDGES) == pytest.approx([800 * 0.979, 1600 * 0.969, 3000 * 0.960])
    assert S.pahdb_scaled(w, "4-31G", S.PAHDB_REGION_EDGES) == pytest.approx([800 * 0.956, 1600 * 0.952, 3000 * 0.960])
    with pytest.raises(ValueError, match="no PAHdb factor row for the basis '3-21G'"):
        S.pahdb_scaled(w, "3-21G", S.TABLE2_REGION_EDGES)


def test_table_2s_lower_edge_is_9_um_and_the_registered_grouping_keeps_1111():
    """A band at 1111.05 cm⁻¹ lies below Table 2's 10000/9: the low region's factor there, the middle one in the registered grouping."""
    w = np.array([1111.05])
    assert S.TABLE2_REGION_EDGES == (10000 / 9, 2500.0) and S.PAHDB_REGION_EDGES == (1111.0, 2500.0)
    assert S.pahdb_scaled(w, "6-31G*", S.TABLE2_REGION_EDGES) == pytest.approx([1111.05 * 0.979])
    assert S.pahdb_scaled(w, "6-31G*", S.PAHDB_REGION_EDGES) == pytest.approx([1111.05 * 0.969])


def test_the_regions_have_the_pahdb_edges():
    m = {"freq": np.array([1110.9, 1111.0, 2499.9, 2500.0, 2500.1])}
    assert S.pahdb_region(m).tolist() == [0, 1, 1, 1, 2]


def test_family_factors_are_recovered_exactly_and_read_as_zero_error():
    truth = {"CH-stretch": 0.97, "CH-oop": 1.01, "ring-ip": 0.99, "other": 1.02}
    mols = corpus(truth)
    ids = list(mols)
    factors = S.fit_factors(mols, ids, S.family_group)
    assert [factors[k] for k in range(4)] == pytest.approx([truth[f] for f in S.FAMILIES])
    rms = S.baseline_diag_rms(mols, ids, ids, factors, S.family_group)
    assert all(rms[f] == pytest.approx(0.0, abs=1e-4) for f in S.FAMILIES)


def test_one_factor_leaves_the_family_differences():
    mols = corpus({"CH-stretch": 0.97, "CH-oop": 1.01, "ring-ip": 0.99, "other": 1.02})
    ids = list(mols)
    factors = S.fit_factors(mols, ids, S.one_group)
    rms = S.baseline_diag_rms(mols, ids, ids, factors, S.one_group)
    assert len(factors) == 1 and all(rms[f] > 1.0 for f in S.FAMILIES)


def test_the_seed_records_must_read_the_same_molecules():
    rec = {"a": {"per_molecule": {"x": {}, "y": {}}}}
    assert S.record_ids([rec, rec], "a") == ["x", "y"]
    with pytest.raises(ValueError, match="different molecules"):
        S.record_ids([rec, {"a": {"per_molecule": {"x": {}}}}], "a")


def test_a_line_passes_only_when_every_family_is_below():
    net = dict.fromkeys(S.FAMILIES, 1.0)
    assert S.line("L", net, dict.fromkeys(S.FAMILIES, 2.0))["pass"]
    worse = dict.fromkeys(S.FAMILIES, 2.0) | {"other": 0.5}
    out = S.line("L", net, worse)
    assert not out["pass"] and out["per_family"]["other"] is False
