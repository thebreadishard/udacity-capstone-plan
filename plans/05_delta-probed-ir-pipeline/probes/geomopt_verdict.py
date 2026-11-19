"""geomeTRIC through pyscf with its convergence verdict kept: the one optimisation call of the probes that optimise a geometry.

pyscf's `geometric_solver.optimize` is `kernel(...)[1]`: it returns the last geometry whether geomeTRIC converged or not, and
`assert_convergence` covers the SCF only. `kernel` returns the pair (converged, mol); upstream's use of it is
pyscf/geomopt/test/test_geometric_solver.py (test_optimize_with_hessian), `conv, mol_eq = geometric_solver.kernel(mf, hessian=True)`.
That file is in pyscf's repository, not in the wheel.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any


def criteria_text(params: dict[str, Any]) -> str:
    """The convergence criteria a run asked for, as an error message names them: the named set, else the explicit thresholds."""
    if "convergence_set" in params:
        return str(params["convergence_set"])
    explicit = {k: v for k, v in sorted(params.items()) if k.startswith("convergence_")}
    if not explicit:
        return "geomeTRIC's default criteria"
    return "(" + ", ".join(f"{k.removeprefix('convergence_')} {v:g}" for k, v in explicit.items()) + ")"


def converged_geometry(mf: Any, what: str, maxsteps: int, callback: Callable[[dict], None] | None = None, **params: Any) -> Any:
    """Optimise `mf`'s molecule with geomeTRIC and return the optimised pyscf Mole; an optimisation that did not converge raises.

    `what` names the optimisation in the error; `params` go to geomeTRIC unchanged (`convergence_set`, explicit `convergence_*`
    thresholds, `constraints`); `callback` receives geomeTRIC's environment after every gradient call. The SCF at every step must
    converge too (`assert_convergence=True`)."""
    from pyscf.geomopt import geometric_solver

    calls = 0

    def count(env: dict) -> None:
        nonlocal calls
        calls += 1
        if callback is not None:
            callback(env)

    converged, mol_eq = geometric_solver.kernel(mf, assert_convergence=True, callback=count, maxsteps=maxsteps, **params)
    if not converged:
        raise RuntimeError(f"{what}: geomeTRIC did not converge to {criteria_text(params)} within {maxsteps} steps "
                           f"({calls} gradient calls); no geometry is written")
    return mol_eq
