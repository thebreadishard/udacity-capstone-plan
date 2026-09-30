"""Second route for the two imaginary modes of the benzonitrile CCSD(T)/cc-pVDZ FD Hessian (30 Sep 2026): the curvature along each mode
from CCSD(T) energies alone, E(q0 ± δ) in mass-weighted coordinates, against the Hessian eigenvalue. Central differences cancel the
gradient term (the geometry is the B3LYP corpus geometry, max |g| 3.6e-2 a.u. at CCSD(T)). Frozen 8, the E8 settings, tighter tolerances."""
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf

lib.num_threads(16)
D = sys.argv[1]
z = np.load(D + "/hessian_ccsd_t_INVALID.npz")
g = json.load(open(D + "/geometry.json"))
x0 = np.array(g["coords_bohr"], float)
sym = g["symbols"]
m = np.repeat(np.array(g["masses_amu"]) * 1822.888486209, 3)
sm = np.sqrt(m)
w, v = np.linalg.eigh(z["H_projected"] / np.outer(sm, sm))
order = np.argsort(w)[:2]
HARTREE2CM = 219474.6313705


def energy(x):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(sym, x.reshape(-1, 3))], unit="Bohr", basis="cc-pvdz", verbose=0, max_memory=14000)
    mf = scf.RHF(mol); mf.conv_tol = 1e-12; mf.kernel()
    mycc = cc.CCSD(mf, frozen=8); mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    eris = mycc.ao2mo(); mycc.kernel(eris=eris)
    return mycc.e_tot + mycc.ccsd_t(eris=eris)


t0 = time.time()
e0 = energy(x0)
print(f"E0 = {e0:.10f} (FD run's reference {float(z['energy']):.10f}); {time.time() - t0:.0f} s", flush=True)
for k in order:
    u = v[:, k]
    dq = 0.02 / np.abs(u / sm).max()          # largest Cartesian step 0.02 bohr
    ep = energy(x0.ravel() + dq * u / sm)
    em = energy(x0.ravel() - dq * u / sm)
    lam_e = (ep + em - 2 * e0) / dq ** 2
    f_e = np.sign(lam_e) * np.sqrt(abs(lam_e)) * HARTREE2CM
    f_h = np.sign(w[k]) * np.sqrt(abs(w[k])) * HARTREE2CM
    print(f"mode {k}: Hessian {f_h:8.1f} cm-1, energy route {f_e:8.1f} cm-1 (E+ − E0 {1e6 * (ep - e0):+.2f}, E− − E0 {1e6 * (em - e0):+.2f} µE_h)", flush=True)
