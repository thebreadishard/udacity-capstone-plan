"""Run an `e8_cc_locality.py` (the path given first) with a stand-in for pyscf that returns stored DFT Hessians.

The script computes the B3LYP and ωB97X Hessians with pyscf and then reads them against the CC Hessian; no environment here has pyscf and
geomeTRIC together (it ran on a server). The regression pin needs the read, not the DFT: this runner puts a minimal `pyscf` (gto.M, lib,
dft.RKS whose Hessian().kernel() returns the stored analytic Hessian of that functional, in pyscf's (n, n, 3, 3) layout) in sys.modules and
calls the script's main.

    python tests/locality_pin_runner.py <path/to/e8_cc_locality.py> <b3lyp.npz> <wb97x.npz> <the script's arguments>
"""
import importlib.util
import sys
import types
from pathlib import Path
from types import SimpleNamespace

import numpy as np


def stored(path: str) -> np.ndarray:
    with np.load(path) as z:
        H = np.asarray(z["H_raw"], float)
    n = H.shape[0] // 3
    return H.reshape(n, 3, n, 3).transpose(0, 2, 1, 3)


script, b3lyp, wb97x, *args = sys.argv[1:]
STORED = {"b3lyp": stored(b3lyp), "wb97x": stored(wb97x)}


class _RKS:
    def __init__(self, mol):
        self.mol, self.xc, self.conv_tol = mol, None, None
        self.grids = SimpleNamespace(atom_grid=None, prune=None)

    def kernel(self):
        return 0.0

    def Hessian(self):                      # pyscf's name
        return SimpleNamespace(kernel=lambda: STORED[self.xc])


pyscf = types.ModuleType("pyscf")
pyscf.gto = SimpleNamespace(M=lambda **kw: SimpleNamespace(**kw))
pyscf.lib = SimpleNamespace(num_threads=lambda n: None)
pyscf.dft = SimpleNamespace(RKS=_RKS)
sys.modules["pyscf"] = pyscf
path = Path(script).resolve()
sys.path.insert(0, str(path.parent))
spec = importlib.util.spec_from_file_location("e8_cc_locality", path)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)
sys.argv = [str(path), *args]
sys.exit(module.main())
