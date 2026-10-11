"""pyscf-properties' infrared module (`pyscf/prop/infrared`, rhf/rks/uhf/uks) loaded from a pinned source checkout, for the third route of TASKS 44.

The qc05 environment carries an older pyscf-properties (`pyscf/prop/__init__.py` version 0.1.0, no `infrared`), and the labels route runs on that
environment, so nothing is installed into it: the checkout's `pyscf/prop` folder is appended to the `pyscf.prop` package path, which makes only
the subpackages missing from the installed copy (here: `infrared`) come from the checkout. The checkout must sit at the pinned commit; another
commit is refused, so a number measured with this module names the code that produced it.

Upstream's own check of the module is `pyscf/prop/infrared/test/test_ir_inten.py` (RHF, UHF, RKS/PBE0, UKS/PBE0 intensities of NH3 against
Q-Chem); `python probes/upstream_infrared.py` runs it through this loader.
"""
import os
import subprocess
import sys
import warnings

CHECKOUT = os.path.expanduser("~/pyscf-properties-master")
PINNED = "4eee5a430fb47eca5962f36fdcaf75c2b87e7ede"   # the checkout's master (7 Nov 2024), read and tested here on 11 Oct 2026


def load(checkout=CHECKOUT):
    """Return (the `pyscf.prop.infrared` module, the checkout's commit)."""
    commit = subprocess.run(["git", "-C", checkout, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    if commit != PINNED:
        raise RuntimeError(f"{checkout} is at {commit}, not the pinned {PINNED}")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Module .* is under testing")      # the installed pyscf.prop's import-time notes (efg, zfs, …)
        import pyscf.prop

    path = os.path.join(checkout, "pyscf", "prop")
    if path not in pyscf.prop.__path__:
        pyscf.prop.__path__.append(path)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Module infrared is not fully tested")   # upstream's own import-time warning
        from pyscf.prop import infrared
    if not os.path.abspath(infrared.__file__).startswith(os.path.abspath(path)):
        raise RuntimeError(f"pyscf.prop.infrared came from {infrared.__file__}, not from {path}")
    return infrared, commit


if __name__ == "__main__":
    import pytest

    _, sha = load()
    print(f"pyscf-properties infrared from {CHECKOUT} at {sha}", flush=True)
    sys.exit(pytest.main(["-q", "-p", "no:cacheprovider", os.path.join(CHECKOUT, "pyscf", "prop", "infrared", "test", "test_ir_inten.py")]))
