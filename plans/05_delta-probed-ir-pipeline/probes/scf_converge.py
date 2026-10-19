"""One SCF convergence for every pyscf DFT path of the S1/S2 runners: DIIS, and when DIIS does not converge, the second-order solver from
DIIS's orbitals to near convergence, then DIIS again from its density to the tight thresholds (pyscf examples/scf/22-newton.py: xc and grid
first, then .newton()).

Acenaphthylene at B3LYP/def2-TZVP stalled under DIIS twice: in the optimisation (18 Oct 2026, fixed then in s1_anharmonic_level.py) and at
the reference Hessian of the optimised geometry (19 Oct, pyscf_hessians_for_qff.py had no fallback; the run ended FAILED). One function, so
that the next path does not miss it. Checked on water with DIIS cut to 3 cycles: `check_scf_newton_fallback.py`.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

DIIS_CYCLES = 200               # an SCF step's DIIS budget; beyond it the second-order solver continues
NEWTON_CYCLES = 100
NEWTON_CONV_TOL_GRAD = 1e-6     # the second-order solver's orbital gradient stalls near 3e-7 on a DFT grid; DIIS finishes


class SCFNotConverged(RuntimeError):
    """Neither DIIS nor the second-order solver followed by DIIS reached the thresholds."""


def converged_scf(mf: Any, diis_cycles: int = DIIS_CYCLES, log: Callable[[str], None] = print) -> tuple[Any, Any]:
    """Run mf to convergence: (the converged SCF object, its energy). The object is a new one when the fallback ran (undo_newton), so the
    caller takes gradients and Hessians from the one returned. Raises SCFNotConverged."""
    if diis_cycles < 1:
        raise ValueError(f"diis_cycles {diis_cycles} must be positive")
    mf.max_cycle = diis_cycles
    e = mf.kernel()
    if mf.converged:
        return mf, e
    log(f"  SCF: DIIS not converged in {diis_cycles} cycles; second-order solver")
    mo, occ = mf.mo_coeff, mf.mo_occ
    nf = mf.newton()
    nf.max_cycle, nf.conv_tol_grad = NEWTON_CYCLES, NEWTON_CONV_TOL_GRAD
    nf.kernel(mo, occ)
    if not nf.converged:
        raise SCFNotConverged("SCF not converged (DIIS, then the second-order solver)")
    mf = nf.undo_newton()
    mf.max_cycle = diis_cycles
    e = mf.kernel(dm0=mf.make_rdm1())
    if not mf.converged:
        raise SCFNotConverged("SCF not converged (DIIS after the second-order solver)")
    return mf, e
