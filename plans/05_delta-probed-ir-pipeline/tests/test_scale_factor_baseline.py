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
