"""PR D's benchmark for the PR description: the (T) lambda, gamma1 and gamma2 terms, whole arrays against blocks, on H2O+/cc-pVTZ.

    PYTHONPATH=~/pyscf-wt-uccsdtblk OMP_NUM_THREADS=4 python probes/pyscf_pr_d_bench.py      (in WSL, the PR branch's worktree)

Log of 27 Oct 2026: results_m1/pyscf_pr_d_bench_h2o_cation_ccpvtz_2026-10-27.log.

Wall time and tracemalloc peak (numpy's arrays are traced) of each step, one step at a time in one process; the blocked results are
compared with the whole-array ones.
"""
import time
import tracemalloc

import numpy
from pyscf import cc, gto, lib, scf
from pyscf.cc import uccsd_rdm, uccsd_t_blocked, uccsd_t_lambda, uccsd_t_rdm

ATOM = 'O 0 0 0.1173; H 0 0.7572 -0.4692; H 0 -0.7572 -0.4692'


def measured(f, *args):
    tracemalloc.start()
    t0 = time.perf_counter()
    out = f(*args)
    wall = time.perf_counter() - t0
    peak = tracemalloc.get_traced_memory()[1] / 1e6
    tracemalloc.stop()
    return out, wall, peak


def main():
    lib.num_threads(4)
    mol = gto.M(atom=ATOM, basis='cc-pvtz', charge=1, spin=1, verbose=0)
    mycc = cc.UCCSD(scf.UHF(mol).run(conv_tol=1e-10)).run(conv_tol=1e-9, conv_tol_normt=1e-7)
    eris = mycc.ao2mo()
    t1, t2 = mycc.t1, mycc.t2
    l1, l2 = mycc.solve_lambda(eris=eris)
    nocca, noccb, nvira, nvirb = t2[1].shape
    print(f'H2O+/cc-pVTZ: occ ({nocca}, {noccb}), vir ({nvira}, {nvirb}); one o**3 v**3 array '
          f'{max(nocca, noccb)**3 * max(nvira, nvirb)**3 * 8 / 1e6:.0f} MB', flush=True)

    def whole_lambda():
        m = uccsd_t_lambda.make_intermediates(mycc, t1, t2, eris)
        return m.l1a_t, m.l1b_t, m.l2aa_t, m.l2ab_t, m.l2bb_t

    def whole_gamma1():
        return uccsd_t_rdm._t3_gamma1(t1, t2, eris)

    if uccsd_t_blocked.block_size(mycc, t2[1]) is not None:
        raise SystemExit('the whole-array code does not fit in max_memory here; raise it for the benchmark')
    ref = {}
    d2 = uccsd_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2)    # built outside the measurement, as for the blocked runs
    for name, f, args in (('lambda', whole_lambda, ()), ('gamma1', whole_gamma1, ()),
                          ('gamma2', uccsd_t_rdm._add_t3_gamma2, (mycc, t1, t2, eris, d2))):
        ref[name], wall, peak = measured(f, *args)
        print(f'whole arrays  {name}: {wall:7.1f} s, peak {peak:7.0f} MB', flush=True)
    for blksize in (8, 16, 32):
        for name in ('lambda', 'gamma1', 'gamma2'):
            if name == 'lambda':
                got, wall, peak = measured(uccsd_t_blocked.lambda_intermediates, mycc, t1, t2, eris, blksize)
            elif name == 'gamma1':
                got, wall, peak = measured(uccsd_t_blocked.gamma1_intermediates, mycc, t1, t2, eris, blksize)
            else:
                d2 = uccsd_rdm._gamma2_intermediates(mycc, t1, t2, l1, l2)
                got, wall, peak = measured(uccsd_t_blocked.add_gamma2, mycc, t1, t2, eris, d2, blksize)
            flat = [x for g in got for x in (g if isinstance(g, tuple) else (g,)) if x is not None]
            flat_ref = [x for g in ref[name] for x in (g if isinstance(g, tuple) else (g,)) if x is not None]
            diff = max(abs(numpy.asarray(a) - b).max() for a, b in zip(flat, flat_ref, strict=True))
            print(f'block {blksize:3d}     {name}: {wall:7.1f} s, peak {peak:7.0f} MB, max diff {diff:.1e}', flush=True)


if __name__ == '__main__':
    main()
