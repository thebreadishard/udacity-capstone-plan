import sys, json, time, numpy as np
sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes")
import e8_cc_hessian_fd as E
from pyscf import gto, scf, cc
from pyscf.cc import ccsd_t_lambda
from pyscf.grad import ccsd_t as G
S = "/mnt/c/Users/thebr/AppData/Local/Temp/claude/C--Users-thebr-Documents-CapstonePlan/080ff7ed-d45b-451f-8c06-e90bcbbe88a0/scratchpad"
g = json.load(open(S + "/water.json"))
x0 = np.array(g["coords_bohr"], float); sym = g["symbols"]; masses = np.array(g["masses_amu"])
def grads(x):
    mol = gto.M(atom=[(s.capitalize(), tuple(c)) for s, c in zip(sym, x)], unit="Bohr", basis="cc-pvdz", symmetry=False, verbose=0)
    mf = scf.RHF(mol); mf.conv_tol = 1e-12; mf.kernel()
    mycc = cc.CCSD(mf, frozen=1); mycc.conv_tol = 1e-11; mycc.conv_tol_normt = 1e-9; mycc.kernel(); mycc.ccsd_t()
    gp = G.Gradients(mycc).kernel()
    eris = mycc.ao2mo(); conv, l1, l2 = ccsd_t_lambda.kernel(mycc, eris, mycc.t1, mycc.t2, tol=1e-10)
    gt = G.Gradients(mycc).kernel(mycc.t1, mycc.t2, l1, l2, eris)
    return np.asarray(gp).ravel(), np.asarray(gt).ravel()
h = 0.005; n = 3 * len(sym); Hp = np.zeros((n, n)); Ht = np.zeros((n, n)); t0 = time.time()
for k in range(n):
    xp = x0.copy(); xp.flat[k] += h; xm = x0.copy(); xm.flat[k] -= h
    gpp, gtp = grads(xp); gpm, gtm = grads(xm)
    Hp[k] = (gpp - gpm) / (2 * h); Ht[k] = (gtp - gtm) / (2 * h)
    print("coordinate", k, "done", round(time.time() - t0), "s", flush=True)
Hp = 0.5 * (Hp + Hp.T); Ht = 0.5 * (Ht + Ht.T)
fp = E.frequencies(E.project_tr(Hp, masses, x0)[1]); ft = E.frequencies(E.project_tr(Ht, masses, x0)[1])
print("plain (CCSD lambda) freqs cm-1:", np.round(fp[-3:], 2))
print("(T)-lambda        freqs cm-1:", np.round(ft[-3:], 2))
print("difference cm-1:", np.round(ft[-3:] - fp[-3:], 2))
print("max |dH| a.u.:", np.abs(Hp - Ht).max())
np.savez(S + "/water_lambda_routes.npz", Hp=Hp, Ht=Ht, fp=fp, ft=ft)
print("DONE")
