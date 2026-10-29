"""Run an `anchor_deck_rehearsal.py` (the path given first; the rest is its command line) with this checkout's data and dependencies.

The rehearsal reads git-ignored files (the scorer's p1_seed*.pt, the corpus) under its own folder, so a copy in a worktree finds none of them.
This runner imports the rehearsal's dependencies from this checkout first (module 05, the standout's pp, the probes), then loads the script
from the path given — its imports resolve to the modules already loaded — and points its PLAN and SCORER at this checkout.
The pin's models are chain 34's, whose registry status changes by design (superseded once v1.3 was carried); decision 55's gate is not
what the pin tests, so the runner replaces it, as tests/cc_pin_runner.py does.

    python tests/deck_pin_runner.py <path/to/anchor_deck_rehearsal.py> <its arguments>
"""
import importlib
import importlib.util
import sys
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parents[1]
for p in (DATA_ROOT / "probes", DATA_ROOT / "modules" / "standout_pattern_proposer", DATA_ROOT / "modules" / "05_support_predictor" / "m05"):
    sys.path.insert(0, str(p))
for name in ("e7_t2_sqm", "e8_symmetry", "model_registry", "pp.core", "pp.scorer", "qc_common", "rungC_equivariant", "rungC_train"):
    importlib.import_module(name)
sys.modules["model_registry"].require_carried = lambda path, allow=False, status_file=None: {"status": "pin fixture (tests/deck_pin_runner.py)"}
script = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("anchor_deck_rehearsal", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.PLAN = DATA_ROOT
module.SCORER = DATA_ROOT / "modules" / "standout_pattern_proposer" / "out"
sys.argv = [str(script), *sys.argv[2:]]
sys.exit(module.main())
