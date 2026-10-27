"""PR D's convention pass: the old and the new uccsd_t_blocked on the same amplitudes, in one process.

    PYTHONPATH=~/pyscf-wt-uccsdtblk python probes/pyscf_pr_d_pin.py <old module file>      (in WSL; the old file from git show)

Two runs of UHF + UCCSD need not give the same amplitudes to the bit (orbital phases), so the comparison runs both modules on one set:
triplet water/6-31G (the test's molecule) and a doublet water cation, block sizes 1, 3 and 100, every array of lambda_intermediates,
gamma1_intermediates and add_gamma2. Prints the largest difference and how many arrays are bit-identical; exit 1 above 1e-13.
"""
import importlib.util
import sys

import numpy
from pyscf import cc, gto, scf
from pyscf.cc import uccsd_rdm
from pyscf.cc import uccsd_t_blocked as new

ATOM = 'O 0 0 0.1173; H 0 0.7572 -0.4692; H 0 -0.7572 -0.4692'


def load(path):
    spec = importlib.util.spec_from_file_location('uccsd_t_blocked_old', path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # dataclasses look their module up here
    spec.loader.exec_module(module)
    return module


def arrays(m, mycc, eris, l1, l2, blk):
    t1, t2 = mycc.t1, mycc.t2
    out = list(m.lambda_intermediates(mycc, t1, t2, eris, blk)) + list(m.gamma1_intermediates(mycc, t1, t2, eris, blk))
    d2 = uccsd_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2)
    m.add_gamma2(mycc, t1, t2, eris, d2, blk)
    return out + [x for group in d2 for x in group if x is not None]


def main(old_path):
    old = load(old_path)
    worst, identical, total = 0.0, 0, 0
    for charge, spin in ((0, 2), (1, 1)):
        mol = gto.M(atom=ATOM, basis='631g', charge=charge, spin=spin, verbose=0)
        mycc = cc.UCCSD(scf.UHF(mol).run(conv_tol=1e-12)).run(conv_tol=1e-10, conv_tol_normt=1e-8)
        eris = mycc.ao2mo()
        l1, l2 = mycc.solve_lambda(eris=eris)
        for blk in (1, 3, 100):
            for a, b in zip(arrays(old, mycc, eris, l1, l2, blk), arrays(new, mycc, eris, l1, l2, blk), strict=True):
                a, b = numpy.asarray(a), numpy.asarray(b)
                worst = max(worst, abs(a - b).max())
                identical += numpy.array_equal(a, b)
                total += 1
    print(f'{total} arrays, largest difference {worst:.2e}, bit-identical {identical} of {total}')
    return 0 if worst < 1e-13 else 1


if __name__ == '__main__':
    raise SystemExit(main(*sys.argv[1:]))
