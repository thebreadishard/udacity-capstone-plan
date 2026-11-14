"""The S1/S2 runners' SCF convergence: the shared policy of `scf_policy.py`, with this unit's preset (TASKS 212, 14 Nov 2026).

The recipe — DIIS, then pyscf's second-order solver from DIIS's orbitals with a threshold of its own, then DIIS again from the solver's
density — is written once, in `modules/05_support_predictor/corpus/scf_policy.py`, because the label route needs the same thing and had
grown its own copy that never carried this one's lesson of 19 October. The two units ship separately, so that file is a leaf with no
imports of its own, and both lists carry it: `deploy_s1tz.sh` and `deploy_s2.sh` ship a git archive, which keeps the plan's folders, so
it lands under the corpus folder; `bootstrap_labels_ccx53.sh` copies the corpus's modules into one flat folder. This module looks
in both places, and stays the name the runners import with their signature unchanged.

Acenaphthylene at B3LYP/def2-TZVP stalled under DIIS twice: in the optimisation (18 Oct 2026, fixed then in s1_anharmonic_level.py) and
at the reference Hessian of the optimised geometry (19 Oct, pyscf_hessians_for_qff.py had no fallback; the run ended FAILED). Checked on
water with DIIS cut to 3 cycles: `check_scf_newton_fallback.py` and tests/test_scf_converge.py.
"""
from __future__ import annotations

import os
import sys
from collections.abc import Callable
from dataclasses import replace
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
# The leaf lives beside this file on a server (the deploy scripts copy it flat) and under the corpus folder in this checkout.
for candidate in (HERE, os.path.join(HERE, "..", "modules", "05_support_predictor", "corpus")):
    if os.path.isfile(os.path.join(candidate, "scf_policy.py")):
        sys.path.insert(0, candidate)
        break
else:
    raise ImportError("scf_policy.py is beside neither this file nor the corpus folder; the deploy set is incomplete (TASKS 212)")

from scf_policy import S1_S2_RUNNERS, SCFNotConverged  # noqa: E402
from scf_policy import converged_scf as _converged_scf  # noqa: E402

DIIS_CYCLES = S1_S2_RUNNERS.diis_cycles                      # an SCF step's DIIS budget; beyond it the second-order solver continues
NEWTON_CYCLES = S1_S2_RUNNERS.newton_cycles
NEWTON_CONV_TOL_GRAD = S1_S2_RUNNERS.newton_conv_tol_grad    # the solver's gradient stalls near 3e-7 on a DFT grid; DIIS finishes

__all__ = ["DIIS_CYCLES", "NEWTON_CONV_TOL_GRAD", "NEWTON_CYCLES", "SCFNotConverged", "converged_scf"]


def converged_scf(mf: Any, diis_cycles: int = DIIS_CYCLES, log: Callable[[str], None] = print,
                  dm0: Any = None) -> tuple[Any, float]:
    """Run mf to convergence by the shared policy: (the converged SCF object, its energy). `diis_cycles` is this call's DIIS budget —
    a runner that wants the fallback sooner says so, as the water check does with three. Raises SCFNotConverged."""
    return _converged_scf(mf, replace(S1_S2_RUNNERS, diis_cycles=diis_cycles), log, dm0)
