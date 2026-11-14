"""One SCF convergence policy for both deployment units (TASKS 212).

The recipe is one: DIIS; if DIIS does not converge, pyscf's second-order solver from DIIS's own orbitals, with a gradient threshold of
its own that is never the caller's tight one; then DIIS again from the solver's density, so the verdict and the thresholds are the
plain SCF object's and the Hessian is built on it (pyscf examples/scf/22-newton.py: xc and grid first, then .newton()).

Two incidents wrote that recipe, one in each unit, and neither carried to the other:

* 19 October 2026, the S1/S2 runners. Acenaphthylene at B3LYP/def2-TZVP stalled under DIIS, in the optimisation and again at the
  reference Hessian; the run ended FAILED because that path had no fallback. The solver's orbital gradient stalls near 3e-7 on a DFT
  grid, so it is stopped at 1e-6 and DIIS finishes to the tight threshold.
* 14 November 2026, the label route. T_76dfc434db (C42H18) spent 50 macro iterations and 2.8 h at |g| 1.83e-8 against the caller's
  conv_tol_grad of 1e-8, because `SecondOrderSCF.kernel` passes `self.conv_tol_grad` on (pyscf/soscf/newton_ah.py, 2.15.0) and
  `mf.newton()` copies the caller's settings. Left to itself the solver derives sqrt(conv_tol) (newton_ah.py:526-527).

The recipe is shared; the numbers are not merged. Each preset keeps the value measured in its own unit, because the two safe
directions differ: a threshold that is too tight leaves the solver unconverged, one that is too loose hands DIIS a poor density. A new
caller takes a preset or states its own with a reason.

This module is a leaf: no imports outside the standard library, so both units can carry the file itself. The corpus folder imports it
by name; `probes/scf_converge.py` re-exports it for the S1/S2 runners, whose deploy lists name it too.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

PYSCF_DEFAULT_MAX_CYCLE = 50     # pyscf's own SCF budget, for the presets that do not change it


class SCFNotConverged(RuntimeError):
    """Neither DIIS nor the second-order solver followed by DIIS reached the caller's thresholds."""


@dataclass(frozen=True)
class SCFPolicy:
    """How far each step of the recipe may go.

    diis_cycles: the DIIS budget, or None to leave the SCF object's own (pyscf's 50). It bounds how long a stalled DIIS runs before the
        solver is asked, which on a 60-atom molecule is the difference between minutes and hours.
    newton_cycles: the second-order solver's macro iterations.
    newton_conv_tol_grad: the solver's own orbital-gradient threshold, or None for pyscf's derived sqrt(conv_tol). Never the caller's:
        that is the whole point of this field, and both incidents above are one of its two faces.
    """

    diis_cycles: int | None
    newton_cycles: int
    newton_conv_tol_grad: float | None

    def __post_init__(self) -> None:
        if self.diis_cycles is not None and self.diis_cycles < 1:
            raise ValueError(f"diis_cycles {self.diis_cycles} must be positive, or None for the object's own budget")
        if self.newton_cycles < 1:
            raise ValueError(f"newton_cycles {self.newton_cycles} must be positive")
        if self.newton_conv_tol_grad is not None and not 0.0 < self.newton_conv_tol_grad < 1.0:
            raise ValueError(f"newton_conv_tol_grad {self.newton_conv_tol_grad} must lie in (0, 1), or be None for pyscf's own")


# The label route (modules/05_support_predictor/corpus): pyscf's DIIS budget, because a label's molecule is large and a long stall
# before the fallback costs hours; the solver's threshold left to pyscf, which is the value measured on 14 November.
LABEL_ROUTE = SCFPolicy(diis_cycles=None, newton_cycles=PYSCF_DEFAULT_MAX_CYCLE, newton_conv_tol_grad=None)

# The S1/S2 runners (probes/): 200 DIIS cycles and 100 macro iterations, with the solver stopped at the 1e-6 measured on 19 October.
S1_S2_RUNNERS = SCFPolicy(diis_cycles=200, newton_cycles=100, newton_conv_tol_grad=1e-6)


def converged_scf(mf: Any, policy: SCFPolicy, log: Callable[[str], None] = print, dm0: Any = None) -> tuple[Any, float]:
    """Run `mf` to convergence by the recipe above and return (the converged SCF object, its energy).

    The object returned is `mf` itself: the second-order solver works on a copy, and the plain object is restarted from that copy's
    density, so gradients and Hessians are taken from the object whose `converged` is the verdict. `dm0` is a start density, a
    neighbouring geometry's for instance. Raises SCFNotConverged with the step that failed.
    """
    if policy.diis_cycles is not None:
        mf.max_cycle = policy.diis_cycles
    energy = mf.kernel() if dm0 is None else mf.kernel(dm0=dm0)
    if mf.converged:
        return mf, energy
    log(f"  SCF: DIIS stopped unconverged at E = {energy:.12f}; the second-order solver continues from its orbitals")
    second = mf.newton()
    second.max_cycle = policy.newton_cycles
    second.conv_tol_grad = policy.newton_conv_tol_grad
    second.kernel(mf.mo_coeff, mf.mo_occ)
    if not second.converged:
        raise SCFNotConverged(f"SCF not converged: DIIS, then the second-order solver in {policy.newton_cycles} macro iterations")
    energy = mf.kernel(dm0=second.make_rdm1())
    if not mf.converged:
        raise SCFNotConverged("SCF not converged: DIIS from the second-order solver's density")
    return mf, energy
