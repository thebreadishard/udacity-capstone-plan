"""rungC_learning_curve_fit (1 Oct 2026): exact power-law points recover the slope and the extrapolation; a size present in two records is refused."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import rungC_learning_curve_fit as LC  # noqa: E402


def _record(path, sizes, slope=-0.3, scale=2.0):
    curve = {}
    for n in sizes:
        r = scale * n ** slope
        curve[str(n)] = {"per_seed": [{"seed": s, "a": {"coupling_ratio": r, "corrected_freq_rms": 10 * r},
                                       "b": {"coupling_ratio": 1.2 * r, "corrected_freq_rms": 12 * r}} for s in range(3)]}
    json.dump({"curve": curve}, open(path, "w"))
    return path


def test_exact_power_law_is_recovered(tmp_path):
    p1 = _record(tmp_path / "r1.json", [175])
    p2 = _record(tmp_path / "r2.json", [449, 750])
    out = LC.fit_curves([str(p1), str(p2)], targets=(5000,))
    a = out["a"]["ring_coupling_ratio"]
    assert out["a"]["sizes"] == [175, 449, 750]
    assert abs(a["slope"] + 0.3) < 1e-9
    assert abs(a["predictions"]["5000"]["point"] - 2.0 * 5000 ** -0.3) < 1e-9
    assert abs(out["b"]["corrected_freq_rms"]["predictions"]["5000"]["point"] - 12 * 2.0 * 5000 ** -0.3) < 1e-6
    assert abs(out["b"]["ring_coupling_ratio"]["predictions"]["5000"]["point"] - 1.2 * 2.0 * 5000 ** -0.3) < 1e-6


def test_duplicate_size_refused_and_two_sizes_needed(tmp_path):
    p1 = _record(tmp_path / "r1.json", [175, 750])
    p2 = _record(tmp_path / "r2.json", [750])
    with pytest.raises(ValueError, match="two records"):
        LC.fit_curves([str(p1), str(p2)], targets=(5000,))
    with pytest.raises(ValueError, match="at least two"):
        LC.fit_curves([str(p2)], targets=(5000,))
    assert np.isfinite(LC.fit_curves([str(p1)], targets=(5000,))["a"]["ring_coupling_ratio"]["slope"])


def _family_record(path, sizes, layers_at, slope=-0.3):
    """Exact power laws in every read-out and family; pool_ids whose layer shares are `layers_at(n)`."""
    curve = {}
    for n in sizes:
        r = 2.0 * n ** slope
        fam = {f: (k + 1) * r for k, f in enumerate(LC.FAMILIES)}
        one = {"coupling_ratio": r, "corrected_freq_rms": 10 * r, "diag_rms": fam}
        curve[str(n)] = {"per_seed": [{"seed": s, "a": one, "b": one} for s in range(3)]}
    n_max = max(sizes)
    ids = [f"{layers_at(i)}_{i:06d}" for i in range(n_max)]
    json.dump({"curve": curve, "pool_ids": ids}, open(path, "w"))
    return path


def test_family_readouts_and_composition(tmp_path):
    """--families (15 Oct 2026): every band family is fitted; the composition check passes a nested pool and flags a curve whose layers change."""
    nested = _family_record(tmp_path / "n.json", [100, 400], lambda i: "B" if i % 4 else "A2")
    out = LC.fit_curves([str(nested)], targets=(5000,), families=True)
    for k, f in enumerate(LC.FAMILIES):
        assert abs(out["a"][f"diag_rms_{f}"]["slope"] + 0.3) < 1e-9
        assert abs(out["b"][f"diag_rms_{f}"]["predictions"]["5000"]["point"] - (k + 1) * 2.0 * 5000 ** -0.3) < 1e-6
    assert "diag_rms_CH-oop" not in LC.fit_curves([str(nested)], targets=(5000,))["a"]
    assert LC.composition([str(nested)])["fixed"]
    small = _family_record(tmp_path / "s.json", [100], lambda i: "A2")
    big = _family_record(tmp_path / "b.json", [400], lambda i: "B" if i % 4 else "A2")
    c = LC.composition([str(small), str(big)])
    assert not c["fixed"] and c["max_spread"] == 0.75


def test_size_penalty_per_family(tmp_path):
    """probes/size_penalty_per_family.py (15 Oct 2026): exact per-seed numbers give exact ratios; a record of two sizes is refused."""
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
    import size_penalty_per_family as SP

    def rec(path, scale, sizes=(370,)):
        fam = {f: scale * (k + 1) for k, f in enumerate(SP.FAMILIES)}
        one = {"coupling_ratio": scale, "corrected_freq_rms": 10 * scale, "diag_rms": fam}
        json.dump({"curve": {str(n): {"per_seed": [{"s": one}, {"s": one}, {"s": one}]} for n in sizes}}, open(path, "w"))
        return str(path)
    out = SP.penalty(rec(tmp_path / "a.json", 2.0), rec(tmp_path / "b.json", 1.0))
    assert all(abs(v["ratio"] - 2.0) < 1e-12 and v["size_se"] == 0 for v in out.values()) and len(out) == 6
    with pytest.raises(ValueError, match="pool sizes"):
        SP.penalty(rec(tmp_path / "c.json", 1.0, sizes=(100, 370)), rec(tmp_path / "b.json", 1.0))
