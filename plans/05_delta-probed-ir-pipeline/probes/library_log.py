"""A long library call is never silent: pyscf's own progress log, switched on in a file of its own (the user, 19 Oct 2026: 'Als we hun eigen
logniveau kunnen aanzetten, dan is dat beter ... We willen kunnen zien of iets is vastgelopen of niet, zonder uren in onzekerheid te zitten').

Our scripts built every molecule with verbose=0 and so silenced pyscf themselves. On 18–19 Oct an S1-TZ optimisation then ran 12 h
without a line, and a slow run looked the same as a stuck one.

How pyscf logs (pyscf 2.14, read 19 Oct): `lib/logger.py` writes every line to `obj.stdout` and flushes it at once, when
`obj.verbose` ≥ the line's level. Its module docstring shows the same pattern: a logger on any object that carries `stdout` and
`verbose`. SCF, gradient and Hessian objects copy `stdout` and `verbose` from their parent at construction (`scf/hf.py`, `grad/rhf.py`,
`hessian/rhf.py`), so setting them on the Mole is enough. A Mole's own `output` is opened with mode 'w' in `Mole.build`, so one Mole per
geometry would wipe the log each time. Here the Mole is given a stream the caller opened once, in append mode, before it is built.

Levels: 4 (INFO) gives one line per SCF cycle. 5 (DEBUG, the default here) adds the timer of every step: each SCF cycle, the partial
Hessian, the whole Hessian. The CPHF equations inside an analytic Hessian stay silent at every level in pyscf 2.14. `hessian/rhf.py`
`solve_mo1` calls `cphf.solve` without its logger, so `lib.krylov` runs at the default WARN and its 'krylov cycle' lines never print (water,
19 Oct: the level-5 log gains two lines for the whole Hessian). That silent stretch is the CPHF part of each Hessian. A one-line upstream
fix, passing the logger on, is drafted for the user (TASKS 79).
"""
from __future__ import annotations

from typing import Any, TextIO

HEARTBEAT_LEVEL = 5          # pyscf.lib.logger.DEBUG
PYSCF_LOG_NAME = "pyscf.log"  # the library log's file name, next to the outputs of the step that writes it
FORBIDDEN_BUILD_KEYS = ("output", "verbose", "stdout")


def pyscf_mole(stream: TextIO, level: int = HEARTBEAT_LEVEL, **build: Any) -> Any:
    """A built pyscf Mole whose log, and the log of every object made from it, goes to `stream` at `level`.

    `build` takes the keyword arguments of `gto.M` (atom, basis, unit, …). The log's destination and level are set here only, so
    `output`, `verbose` and `stdout` are refused."""
    clash = [k for k in FORBIDDEN_BUILD_KEYS if k in build]
    if clash:
        raise ValueError(f"pyscf_mole sets the log itself; do not pass {', '.join(clash)}")
    if not 0 <= level <= 9:
        raise ValueError(f"pyscf verbose level {level} outside 0–9")
    from pyscf import gto
    mol = gto.Mole()
    mol.stdout = stream
    mol.build(verbose=level, dump_input=False, **build)
    return mol
