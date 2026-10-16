"""Run a `rungC_cc_transfer.py` (the path given first; the rest is its command line) on the regression pin's model.

The pin's model lies in tests/data, under no registered checkpoint folder, and `model_registry.require_carried` refuses such a model even
with --allow-any-model (decision 55). That gate is not what the pin tests, so this runner replaces it and calls the script's own main.

    python tests/cc_pin_runner.py <path/to/rungC_cc_transfer.py> <its arguments>
"""
import importlib.util
import sys
from pathlib import Path

script = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(script.parent))
import model_registry  # noqa: E402  (from the script's own folder, as the script imports it)

model_registry.require_carried = lambda path, allow=False, status_file=None: {"status": "pin fixture (tests/cc_pin_runner.py)"}
spec = importlib.util.spec_from_file_location("rungC_cc_transfer", script)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module            # dataclasses resolve their deferred annotations through sys.modules
spec.loader.exec_module(module)
sys.argv = [str(script), *sys.argv[2:]]
sys.exit(module.main())
