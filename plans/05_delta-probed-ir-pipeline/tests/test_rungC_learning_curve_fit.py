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
