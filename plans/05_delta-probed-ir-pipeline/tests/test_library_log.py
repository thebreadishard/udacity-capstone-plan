"""probes/library_log.py (19 Oct 2026): pyscf's own log, switched on in a stream of our own, so a long call is never silent. The argument
checks run anywhere; the pyscf part (one line per SCF cycle, the Hessian's step timers, two molecules appending to one stream instead of
wiping it) runs in WSL and is skipped where pyscf is missing."""
import io
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "probes"))
import library_log as L

WATER = [("O", (0.0, 0.0, 0.2217)), ("H", (0.0, 1.4309, -0.8867)), ("H", (0.0, -1.4309, -0.8867))]


@pytest.mark.parametrize("key", L.FORBIDDEN_BUILD_KEYS)
def test_the_log_destination_and_level_are_set_here_only(key):
    with pytest.raises(ValueError, match=key):
        L.pyscf_mole(io.StringIO(), atom=WATER, unit="Bohr", basis="sto-3g", **{key: 0})


@pytest.mark.parametrize("level", [-1, 10])
def test_a_level_outside_pyscfs_range_is_refused(level):
    with pytest.raises(ValueError, match="outside"):
        L.pyscf_mole(io.StringIO(), level, atom=WATER, unit="Bohr", basis="sto-3g")


def test_scf_and_hessian_cycles_reach_the_stream_and_two_molecules_append():
    pytest.importorskip("pyscf")
    from pyscf import scf
    stream = io.StringIO()
    for _ in range(2):
        mf = scf.RHF(L.pyscf_mole(stream, atom=WATER, unit="Bohr", basis="sto-3g", symmetry=False))
        mf.kernel()
    first_cycles = [s for s in stream.getvalue().splitlines() if s.startswith("cycle= 1 ")]
    assert len(first_cycles) == 2                                  # both molecules' first SCF cycle: nothing was overwritten
    mf.Hessian().kernel()
    assert "CPU time for RHF hessian" in stream.getvalue()         # the step timers (DEBUG level)
