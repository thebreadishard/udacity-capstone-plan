"""The conversion constants the trainer and its readouts use, from the one place they are defined (TASKS 221, 14 November 2026).

They live beside the label route that writes the Hessians, `corpus/constants.py`, because that is where the numbers enter the project.
Five m05 modules wrote them out again, and one of those copies differed in the eleventh digit - the drift the one-implementation rule
exists to catch. This module is the m05 side of the arrangement `probes/qc_common.py` provides for the probes: one place that reaches
across, and a plain `from units import ...` everywhere else.

It loads that file by its path rather than putting the corpus folder on `sys.path`, because a path entry stays for the life of the
process and would decide what every later `import constants` in the trainer means, dependencies included. Here nothing is ambiguous:
this file, or an error naming it.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

CONSTANTS = Path(__file__).resolve().parents[1] / "corpus" / "constants.py"


def _load():
    spec = importlib.util.spec_from_file_location("m05_corpus_constants", CONSTANTS)
    if spec is None or spec.loader is None:
        raise ImportError(f"{CONSTANTS} cannot be loaded: the corpus folder is the one definition of the constants (TASKS 221)")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_constants = _load()
AMU2AU: float = _constants.AMU2AU
HARTREE2CM: float = _constants.HARTREE2CM

__all__ = ["AMU2AU", "HARTREE2CM"]
