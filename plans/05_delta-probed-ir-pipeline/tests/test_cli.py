"""The command line writes a report with a provenance block and the arrays next to it."""

import numpy as np
import pytest

from dpir.qff import main

pytestmark = pytest.mark.data


def test_cli_writes_report_and_arrays(water_cache, tmp_path):
    out = tmp_path / "water_qff.md"
    main([str(water_cache), "--disp", "0.05", "--out", str(out)])
    text = out.read_text(encoding="utf-8")
    assert text.startswith("# Quartic force field from 7 displaced Hessians")
    assert "## Noise diagnostics" in text and "## VPT2 fundamentals" in text
    assert "## Provenance" in text and "- command:" in text and "- numpy:" in text
    arrays = np.load(tmp_path / "water_qff.npz")
    assert set(arrays.files) >= {"omega_cm", "phi_ijk", "phi_iijj", "phi_iijj_route_a", "phi_iijj_route_b", "nu_raw", "nu_sym"}
    assert arrays["omega_cm"].shape == (3,)
