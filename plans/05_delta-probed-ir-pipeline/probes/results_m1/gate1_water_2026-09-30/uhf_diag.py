import numpy as np
from pyscf import gto, scf, cc, lib
from pyscf.cc import uccsd_t_lambda, ccsd_t_lambda
from pyscf.grad import uccsd_t as GUT, uccsd as GU, ccsd_t as GRT
lib.num_threads(8)
X = np.array([[0.0, 0.0, 0.229980], [0.0, 1.418995, -0.919730], [0.0, -1.418995, -0.919730]])
def run(x, charge, spin, frozen, triples, grad):
    mol = gto.M(atom=[(s, tuple(c)) for s, c in zip("OHH", x)], unit="Bohr", basis="cc-pvdz", charge=charge, spin=spin, verbose=0)
    mf = (scf.UHF if spin else scf.RHF)(mol).run(conv_tol=1e-12)
    mycc = (cc.UCCSD if spin else cc.CCSD)(mf, frozen=frozen); mycc.conv_tol, mycc.conv_tol_normt = 1e-11, 1e-9
    eris = mycc.ao2mo(); mycc.kernel(eris=eris)
    e = mycc.e_tot + (mycc.ccsd_t(eris=eris) if triples else 0.0)
    if not grad: return e, None
    if triples:
        conv, l1, l2 = (uccsd_t_lambda if spin else ccsd_t_lambda).kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-10)
        g = (GUT if spin else GRT).Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
    else:
        mycc.solve_lambda(eris=eris); g = mycc.nuc_grad_method().kernel()
    return e, np.asarray(g)
h = 1e-3
for charge, spin, frozen, triples in [(1,1,1,True),(1,1,0,True),(1,1,1,False),(1,1,0,False),(0,2,1,True)]:
    e0, g = run(X, charge, spin, frozen, triples, True)
    fd = []
    for k in (2, 4, 5):   # O z, H1 y, H1 z
        xp, xm = X.copy(), X.copy(); xp.flat[k] += h; xm.flat[k] -= h
        fd.append((run(xp, charge, spin, frozen, triples, False)[0] - run(xm, charge, spin, frozen, triples, False)[0]) / (2*h))
    an = g.ravel()[[2, 4, 5]]
    print(f"charge {charge} 2S {spin} frozen {frozen} (T) {triples}: max|an-fd| = {np.abs(an-np.array(fd)).max():.1e}  an {np.round(an,6)} fd {np.round(fd,6)}", flush=True)
