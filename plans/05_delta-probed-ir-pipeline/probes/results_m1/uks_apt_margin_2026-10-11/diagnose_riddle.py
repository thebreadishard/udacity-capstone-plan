"""The riddle of 12 Oct 2026: pyscf's DFT Hessian agrees with the frozen-grid FD of the gradient (0.06 cm⁻¹), yet the dipole derivatives
contracted from the same CPHF response do not (benzene PBE 2.2e-4 e). Locate it by measuring the response's pieces against frozen-grid finite
differences, for carbon atom 0 of benzene (x, y, z), PBE/6-31G*, grid (99, 590) unpruned:
  h1  = ∂F/∂R with the AO density fixed            — pyscf `make_h1`              against  [F(R+h; D0) − F(R−h; D0)] / 2h
  dD  = ∂D/∂R (AO, moving basis)                    — from the CPHF `mo1`          against  [D(R+h) − D(R−h)] / 2h     (SCF on the frozen grid)
  APT column                                        — route C (`apt_from_mo1`)     against  FD of the dipole on the frozen grid, and the field route
Each difference is reported as a max |·|; for dD also its contraction with the dipole integrals (the part the APT sees).

    python probes/results_m1/uks_apt_margin_2026-10-11/diagnose_riddle.py   (WSL, qc05; ≈ 20 min at 4 threads)
"""
import json
import os
import sys

import numpy as np
from pyscf import gto, lib

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(PLAN, "probes"))
sys.path.insert(0, os.path.join(PLAN, "modules", "05_support_predictor", "corpus"))
from apt import apt_from_mo1, hessian_with_response  # noqa: E402
from apt_field_route import apt_field  # noqa: E402
from hessian_fixed_grid_fd import frozen_grids, make_mf  # noqa: E402

lib.num_threads(4)
XC, GRID, H, A = "pbe", (99, 590), 0.005, 0
D = os.path.join(PLAN, "modules", "05_support_predictor", "corpus", "molecules", "A_8448043181")
g = json.load(open(os.path.join(D, "geometry.json")))
mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(g["symbols"], g["coords_bohr"], strict=True)], unit="Bohr", basis="6-31g*",
            cart=True, symmetry=False, verbose=0, max_memory=4000)
ref = make_mf(mol, XC, grid=GRID)
ref.kernel()
assert ref.converged
D0 = ref.make_rdm1()
mocc = ref.mo_coeff[:, ref.mo_occ > 0]
r_int = mol.intor("int1e_r", comp=3)

hobj = ref.Hessian()
h1ao = hobj.make_h1(ref.mo_coeff, ref.mo_occ, None, [A])                 # list over atmlst: h1ao[0] has shape (3, nao, nao)
_, mo1 = hessian_with_response(ref.Hessian())
P_c = apt_from_mo1(ref, mo1)
P_f, _ = apt_field(mol, {"xc": XC, "grid": GRID}, 1e-3, log=lambda *a, **k: None)

x0 = mol.atom_coords(unit="Bohr")
out = {"xc": XC, "atom": A, "step": H, "per_direction": []}
for d in range(3):
    F, Dm, mu = [], [], []
    for s in (+1, -1):
        x = x0.copy()
        x[A, d] += s * H
        m = mol.set_geom_(x, unit="Bohr", inplace=False)
        mf = make_mf(m, XC, grids=frozen_grids(ref.grids, m))
        F.append(mf.get_hcore(m) + mf.get_veff(m, D0))                    # the Fock matrix with the AO density held at D0
        mf.kernel(D0)
        assert mf.converged
        Dm.append(mf.make_rdm1())
        mu.append(mf.dip_moment(unit="AU", verbose=0))
    h1_fd = (F[0] - F[1]) / (2 * H)
    dD_fd = (Dm[0] - Dm[1]) / (2 * H)
    dD_c = 2.0 * (mo1[A][d] @ mocc.T)
    dD_c = dD_c + dD_c.T
    col = 3 * A + d
    row = {
        "direction": "xyz"[d],
        "h1_max_abs": float(np.abs(h1ao[0][d]).max()), "h1_vs_fd": float(np.abs(h1ao[0][d] - h1_fd).max()),
        "dD_max_abs": float(np.abs(dD_fd).max()), "dD_vs_fd": float(np.abs(dD_c - dD_fd).max()),
        "dD_dot_r_vs_fd": float(np.abs(np.einsum("pq,tpq->t", dD_c - dD_fd, r_int)).max()),
        "apt_routeC_vs_fd_frozen": float(np.abs(P_c[:, col] - (mu[0] - mu[1]) / (2 * H)).max()),
        "apt_field_vs_fd_frozen": float(np.abs(P_f[:, col] - (mu[0] - mu[1]) / (2 * H)).max()),
        "apt_routeC_vs_field": float(np.abs(P_c[:, col] - P_f[:, col]).max()),
    }
    out["per_direction"].append(row)
    print(json.dumps(row), flush=True)
json.dump(out, open(os.path.join(HERE, "diagnose_riddle.json"), "w"), indent=1)
