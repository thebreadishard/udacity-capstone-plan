"""Run an `e8_cc_hessian_fd.py` (the path given first; the rest is its command line) without its gate-1 check.

Gate 1 refuses any copy whose sha256 differs from the stamped files — by design, so a refactored copy in a worktree is refused before it
computes anything. The regression pin tests the computation, not the gate (which has its own test, tests/test_acceptance_water.py, and is
re-run after a merge), so this runner replaces only `gate1_problem` and calls the script's main.

    python tests/e8_pin_runner.py <path/to/e8_cc_hessian_fd.py> <its arguments>
"""
import importlib.util
import sys
from pathlib import Path

script = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(script.parent))
spec = importlib.util.spec_from_file_location("e8_cc_hessian_fd", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
module.gate1_problem = lambda *args, **kwargs: None
sys.argv = [str(script), *sys.argv[2:]]
sys.exit(module.main())
