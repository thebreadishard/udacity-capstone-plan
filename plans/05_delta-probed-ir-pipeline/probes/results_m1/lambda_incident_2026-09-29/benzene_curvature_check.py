"""Second route at benzene scale (29 Sep 2026): curvature of E_CCSD(T) along three normal-mode directions at the corpus geometry, by central
differences of the energy (h = 0.01 and 0.02 bohr, Richardson), against d^T H d for the new Hessian (explicit (T) lambda) and the old one
(CCSD lambda, 24 Sep). Same RHF/CCSD/(T) settings as e8_cc_hessian_fd.py, tighter CCSD convergence. Runs on hel1-23 (16 threads, ~20 min)."""
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf

geom, new_npz, old_npz, out = sys.argv[1:5]
lib.num_threads(16)
g = json.load(open(geom)); sym = g["symbols"]; x0 = np.array(g["coords_bohr"], float); masses = np.array(g["masses_amu"])
Hn = np.load(new_npz)["H_raw"]; Ho = np.load(old_npz)["H_raw"]
AMU2AU = 1822.888486209; HARTREE2CM = 219474.6313705
m = np.repeat(masses * AMU2AU, 3); sm = np.sqrt(m)
w, V = np.linalg.eigh(Hn / np.outer(sm, sm))
freqs = np.sign(w) * np.sqrt(np.abs(w)) * HARTREE2CM
order = np.argsort(freqs)
picks = [order[6], order[10], order[-1]]          # lowest mode, the fifth (out-of-plane region), the highest C-H stretch


def energy(x):
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis="cc-pvdz", symmetry=False, verbose=0, max_memory=26000)
    mf = scf.RHF(mol); mf.conv_tol = 1e-12; e_hf = mf.kernel()
    mycc = cc.CCSD(mf, frozen=6); mycc.conv_tol = 1e-10; mycc.conv_tol_normt = 1e-8; e_corr = mycc.kernel()[0]
    assert mycc.converged
    return e_hf + e_corr + mycc.ccsd_t()


t0 = time.time(); e0 = energy(x0); print(f"E0 {e0:.10f} ({time.time() - t0:.0f} s)", flush=True)
rows = []
for k in picks:
    d = V[:, k] / sm; d /= np.linalg.norm(d)              # Cartesian direction, unit norm in bohr
    c = {}
    for h in (0.01, 0.02):
        ep = energy(x0 + (h * d).reshape(-1, 3)); em = energy(x0 - (h * d).reshape(-1, 3))
        c[h] = (ep - 2 * e0 + em) / h ** 2
        print(f"mode {k} ({freqs[k]:.0f} cm-1) h {h}: curvature {c[h]:.8f}", flush=True)
    c_fd = (16 * c[0.01] - c[0.02]) / 15
    cn = float(d @ Hn @ d); co = float(d @ Ho @ d)
    rows.append((k, freqs[k], c_fd, cn, co))
    print(f"mode {k} ({freqs[k]:.0f} cm-1): FD {c_fd:.8f} | new (T)-lambda {cn:.8f} (rel {cn / c_fd - 1:+.2e}) | old CCSD-lambda {co:.8f} (rel {co / c_fd - 1:+.2e})", flush=True)
with open(out, "w") as f:
    f.write("| mode | ω_new (cm⁻¹) | curvature FD of E_CCSD(T) (E_h/bohr²) | dᵀH_new d | rel. | dᵀH_old d | rel. | Δω old−FD (cm⁻¹) | Δω new−FD (cm⁻¹) |\n|---|---|---|---|---|---|---|---|---|\n")
    for k, fr, c_fd, cn, co in rows:
        f.write(f"| {k} | {fr:.1f} | {c_fd:.8f} | {cn:.8f} | {cn / c_fd - 1:+.1e} | {co:.8f} | {co / c_fd - 1:+.1e} | {fr * (co / c_fd - 1) / 2:+.1f} | {fr * (cn / c_fd - 1) / 2:+.1f} |\n")
print("CURVATURE CHECK DONE", time.time() - t0, "s")
