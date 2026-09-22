"""Smoke test for route 2 (22 Sep 2026): one analytic Hessian of naphthalene at Mackie's level, B97-1 with the Dunning TZ2P basis
(BSE 'CADPAC-TZ2P'), pyscf RKS grid (99, 590), to time the deck (2·M + 1 = 97 Hessians for the finite-difference quartic force field)
and to check memory. Also reports the B97-1/TZ2P single-point time and the harmonic frequencies from the analytic Hessian.
Usage: python naph_level_smoke.py <stageA.json> [threads]
"""
import json, os, sys, time, resource
import numpy as np
import basis_set_exchange as bse
from pyscf import gto, dft, lib
from pyscf.hessian import thermo

a = json.load(open(sys.argv[1]))
lib.num_threads(int(sys.argv[2]) if len(sys.argv) > 2 else 16)
symbols, coords = a["symbols"], np.array(a["coords_bohr"])
basis = {el: gto.basis.parse(bse.get_basis("CADPAC-TZ2P", elements=[el], fmt="nwchem", header=False)) for el in set(symbols)}
mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(symbols, coords)], unit="Bohr", basis=basis, verbose=0, symmetry=False, max_memory=24000)
print(f"naphthalene, {mol.natm} atoms, {mol.nao} basis functions (B97-1 / CADPAC-TZ2P)", flush=True)
t0 = time.time()
mf = dft.RKS(mol, xc="B97-1"); mf.grids.atom_grid = (99, 590); mf.conv_tol = 1e-11; e = mf.kernel()
t1 = time.time(); print(f"SCF: E = {e:.9f}, {t1 - t0:.0f} s", flush=True)
H = mf.Hessian().kernel()
t2 = time.time()
rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
print(f"analytic Hessian: {t2 - t1:.0f} s; peak RSS {rss:.1f} GB", flush=True)
freq = thermo.harmonic_analysis(mol, H, imaginary_freq=False)["freq_wavenumber"]
print("harmonic frequencies (cm-1):", np.round(np.sort(freq), 1).tolist(), flush=True)
print(f"deck estimate: 97 Hessians x {(t2 - t1) / 60:.1f} min = {97 * (t2 - t1) / 3600:.1f} h at this thread count; two step sizes share the reference: {(1 + 2 * 96) * (t2 - t1) / 3600:.1f} h")
