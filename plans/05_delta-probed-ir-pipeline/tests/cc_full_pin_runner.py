"""Run a `cc_composite_full_check.py` (the path given first; the rest is its command line) with this checkout as its data root.

The pin's inputs (corpus geometries and DFT Hessians, CC anchors, MP2 rows) are mostly not in git, so a copy of the script in a worktree
finds none of them under its own folder. This runner loads the script from the path given and points its `PLAN` at this checkout before
calling its main; the script's own imports (e8_symmetry, anchor_deck_rehearsal, module 05) resolve from its folder, which tracks them.

    python tests/cc_full_pin_runner.py <path/to/cc_composite_full_check.py> <subcommand> <its arguments>
"""
import importlib.util
import sys
from pathlib import Path

DATA_ROOT = Path(__file__).resolve().parents[1]
script = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("cc_composite_full_check", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.PLAN = DATA_ROOT
sys.argv = [str(script), *sys.argv[2:]]
sys.exit(module.main())
