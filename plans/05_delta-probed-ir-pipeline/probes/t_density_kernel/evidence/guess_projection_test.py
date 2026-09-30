"""Does projecting the reference CCSD amplitudes and (T) lambdas into the MO basis of a displaced geometry cut the iterations?
Benzene/cc-pVDZ, frozen 6, one Cartesian displacement of 0.005 bohr (the E8 step). Same final answers required (converged energies and
lambdas equal to the tolerances); qc05 = pyscf 2.14 wheel, production environment."""
import json
import sys
import time

import numpy as np
from pyscf import cc, gto, lib, scf
from pyscf.cc import ccsd_t_lambda

sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/t_density_kernel")
import t_density_fast as F  # noqa: E402

lib.num_threads(16)
F.install_lambda()
F.install()
from pyscf.grad import ccsd_t as ccsd_t_grad  # noqa: E402
g = json.load(open(sys.argv[1]))
x0 = np.array(g["coords_bohr"], float)
FROZEN = 6


def run(x, guess=None):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip(g["symbols"], x)], unit="Bohr", basis="cc-pvdz", verbose=0, max_memory=12000)
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-11
    dm0 = None if guess is None else guess["dm"]
    t = time.perf_counter(); mf.kernel(dm0=dm0); t_scf = time.perf_counter() - t
    mycc = cc.CCSD(mf, frozen=FROZEN)
    mycc.conv_tol, mycc.conv_tol_normt = 1e-9, 1e-7
    eris = mycc.ao2mo()
    t1 = t2 = l1 = l2 = None
    if guess is not None:
        # overlap of the active MOs of the two geometries (AO overlap at the new geometry; the step is 0.005 bohr)
        S = mol.intor("int1e_ovlp")
        C_new = mf.mo_coeff[:, FROZEN:]
        C_old = guess["C"]
        U = C_new.T @ S @ C_old                        # new x old
        no = guess["t1"].shape[0]
        Uo, Uv = U[:no, :no], U[no:, no:]
        t1 = Uo @ guess["t1"] @ Uv.T
        t2 = np.einsum("ip,jq,pqab,ca,db->ijcd", Uo, Uo, guess["t2"], Uv, Uv, optimize=True)
        l1 = Uo @ guess["l1"] @ Uv.T
        l2 = np.einsum("ip,jq,pqab,ca,db->ijcd", Uo, Uo, guess["l2"], Uv, Uv, optimize=True)
    cyc = {"n": 0}
    t = time.perf_counter(); mycc.kernel(t1=t1, t2=t2, eris=eris); t_cc = time.perf_counter() - t
    et = mycc.ccsd_t(eris=eris)
    t = time.perf_counter()
    conv, L1, L2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, l1=l1, l2=l2, tol=1e-8)
    t_lam = time.perf_counter() - t
    grad = ccsd_t_grad.Gradients(mycc).kernel(mycc.t1, mycc.t2, L1, L2, eris)
    return dict(e=mycc.e_tot + et, t1=mycc.t1, t2=mycc.t2, l1=L1, l2=L2, C=mf.mo_coeff[:, FROZEN:], dm=mf.make_rdm1(),
                grad=np.asarray(grad), t_scf=t_scf, t_cc=t_cc, t_lam=t_lam, cc_cycles=mycc.cycles if hasattr(mycc, "cycles") else -1)


ref = run(x0)
xd = x0.copy(); xd.flat[0] += 0.005
cold = run(xd)
warm = run(xd, guess=ref)
for name, r in (("cold", cold), ("warm", warm)):
    print(f"{name}: SCF {r['t_scf']:.1f} s, CCSD {r['t_cc']:.1f} s, lambda {r['t_lam']:.1f} s", flush=True)
print(f"|E_warm - E_cold| = {abs(warm['e'] - cold['e']):.1e} E_h; max |grad_warm - grad_cold| = {np.abs(warm['grad'] - cold['grad']).max():.1e} a.u.", flush=True)
