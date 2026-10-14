"""probes/cc_apt_field.py (lever 6, 12 Oct 2026): the CCSD(T) APT from the field derivative of the CCSD(T) gradient agrees with central
differences of the relaxed CCSD(T) dipole (the E8 probe's route). Measured on water/6-31G, frozen 1s: 1.8e-5 e between the routes (most of it
the dipole route's step error: the field route moves 6.7e-6 when F halves), translation sum rule 1.6e-12 (field) against 3.6e-6 (dipole FD).
About 30 s; needs pyscf, so it runs in WSL and is skipped elsewhere."""
import sys
from pathlib import Path

import numpy as np
import pytest

pytest.importorskip("pyscf")
from pyscf import gto  # noqa: E402

PLAN = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PLAN / "probes"))
sys.path.insert(0, str(PLAN / "modules" / "05_support_predictor" / "corpus"))
from apt import sum_rule  # noqa: E402
from cc_apt_field import apt_cc_field, apt_fd_dipole  # noqa: E402

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


def test_the_cc_field_route_agrees_with_fd_of_the_relaxed_dipole():
    mol = gto.M(atom=WATER, unit="Bohr", basis="6-31g", symmetry=False, verbose=0)
    quiet = lambda *a, **k: None  # noqa: E731
    P_field = apt_cc_field(mol, 1, 1e-3, log=quiet)
    P_fd = apt_fd_dipole(mol, 1, 5e-3, log=quiet)
    assert np.abs(P_field - P_fd).max() < 5e-5
    assert sum_rule(P_field) < 1e-9 < sum_rule(P_fd)
    assert np.abs(apt_cc_field(mol, 1, 5e-4, log=quiet) - P_field).max() < 2e-5          # the field error is O(F²) and small


def test_a_stopped_field_run_resumes_from_its_cached_gradients(tmp_path):
    """14 Oct 2026: azulene's re-run was stopped after 4 of 6 fields and kept nothing; each field's gradient is now cached and reused, and
    a cache from another geometry is refused, not reused."""
    mol = gto.M(atom=WATER, unit="Bohr", basis="6-31g", symmetry=False, verbose=0)
    quiet = lambda *a, **k: None  # noqa: E731
    P1 = apt_cc_field(mol, 1, 1e-3, log=quiet, cache_dir=str(tmp_path))
    assert len(list(tmp_path.glob("grad_*.npz"))) == 6
    seen = []
    P2 = apt_cc_field(mol, 1, 1e-3, log=lambda *a, **k: seen.append(a[0]), cache_dir=str(tmp_path))
    assert np.array_equal(P1, P2) and sum("reused" in s for s in seen) == 6
    moved = gto.M(atom=[(s, (x, y, z + 0.01)) for s, (x, y, z) in WATER], unit="Bohr", basis="6-31g", symmetry=False, verbose=0)
    with pytest.raises(SystemExit):
        apt_cc_field(moved, 1, 1e-3, log=quiet, cache_dir=str(tmp_path))
