"""Wire CCsd_t_rdm_intermediates / CCsd_t_lambda_intermediates (pyscf/lib/cc/ccsd_t_rdm.c) into pyscf master (branch t3-intermediates-c)."""
import os
import sys
sys.path.insert(0, "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/tools")
from patch_file import patch  # noqa: E402

os.chdir("/home/thebreadishard/pyscf-master")

patch("pyscf/lib/cc/CMakeLists.txt", [
    ("  ccsd_pack.c ccsd_grad.c ccsd_t.c ccsd_t_lambda.c uccsd_t.c)\n",
     "  ccsd_pack.c ccsd_grad.c ccsd_t.c ccsd_t_lambda.c ccsd_t_rdm.c uccsd_t.c)\n")])

R = "pyscf/cc/ccsd_t_rdm.py"
text = open(R, encoding="utf-8").read()

# gamma1: everything between the eris line and the for_grad branch becomes one C call
g1_start = text.index("    if eris is None: eris = mycc.ao2mo()\n    nocc, nvir = t1.shape\n    eris_ovvv")
g1_end = text.index("    if not for_grad:\n")
assert g1_start < g1_end and text.count("    if not for_grad:\n") == 1
g1_new = ("    if eris is None: eris = mycc.ao2mo()\n"
          "    nocc, nvir = t1.shape\n"
          "    goo, gvv, dvo_t = _t3_intermediates(t1, t2, eris, with_gamma2=False)[:3]\n"
          "    dvo = dvo + dvo_t\n\n")
text = text[:g1_start] + g1_new + text[g1_end:]

g2_start = text.index("    if eris is None: eris = mycc.ao2mo()\n\n    nocc, nvir = t1.shape\n    eris_ovvv")
g2_end = text.index("    dvvov = dovvv.transpose(2,3,0,1)\n")
assert g2_start < g2_end
g2_new = ("    if eris is None: eris = mycc.ao2mo()\n\n"
          "    dovov_t, dooov_t, dovvv_t = _t3_intermediates(t1, t2, eris, with_gamma1=False)[3:]\n"
          "    dovov = dovov + dovov_t\n"
          "    dooov = dooov + dooov_t\n"
          "    dovvv = dovvv + dovvv_t\n\n")
text = text[:g2_start] + g2_new + text[g2_end:]

helpers = '''def _t3_kernel_args(t1, t2, eris):
    \'\'\'Sorted inputs of the (T) kernels in libcc (ccsd_t_rdm.c), active space.\'\'\'
    nocc, nvir = t1.shape
    nmo = nocc + nvir
    eris_ovvv = numpy.asarray(eris.get_ovvv())
    eris_ovov = numpy.asarray(eris.ovov)
    vvop = numpy.empty((nvir, nvir, nocc, nmo))
    vvop[:, :, :, :nocc] = eris_ovov.transpose(1, 3, 0, 2)
    vvop[:, :, :, nocc:] = eris_ovvv.transpose(1, 3, 0, 2)
    eris_ovvv = eris_ovov = None
    fock = numpy.asarray(eris.fock)
    return (numpy.asarray(eris.mo_energy, dtype=numpy.float64, order='C'),
            numpy.asarray(t1.T, dtype=numpy.float64, order='C'),
            numpy.asarray(t2.transpose(2, 3, 1, 0), dtype=numpy.float64, order='C'),
            numpy.asarray(numpy.asarray(eris.ovoo).transpose(1, 0, 2, 3), dtype=numpy.float64, order='C'),
            vvop,
            numpy.asarray(fock[nocc:, :nocc], dtype=numpy.float64, order='C'),
            numpy.asarray(fock[:nocc, nocc:], dtype=numpy.float64, order='C'))

def _t3_intermediates(t1, t2, eris, with_gamma1=True, with_gamma2=True):
    \'\'\'(T) contributions goo, gvv, dvo, dovov, dooov, dovvv of the CCSD(T) response
    density intermediates (libcc CCsd_t_rdm_intermediates; one pass over the virtual
    triples).  The arrays of a skipped gamma are returned as zeros.
    \'\'\'
    nocc, nvir = t1.shape
    mo_e, t1T, t2T, vooo, vvop, fvo = _t3_kernel_args(t1, t2, eris)[:6]
    goo = numpy.zeros((nocc, nocc))
    gvv = numpy.zeros((nvir, nvir))
    dvo = numpy.zeros((nvir, nocc))
    dovov = numpy.zeros((nocc, nvir, nocc, nvir))
    dooov = numpy.zeros((nocc, nocc, nocc, nvir))
    dovvv = numpy.zeros((nocc, nvir, nvir, nvir))
    drv = _ccsd.libcc.CCsd_t_rdm_intermediates
    drv.restype = ctypes.c_int
    err = drv(ctypes.c_int(nocc), ctypes.c_int(nvir),
              mo_e.ctypes.data_as(ctypes.c_void_p), t1T.ctypes.data_as(ctypes.c_void_p),
              t2T.ctypes.data_as(ctypes.c_void_p), vooo.ctypes.data_as(ctypes.c_void_p),
              vvop.ctypes.data_as(ctypes.c_void_p), fvo.ctypes.data_as(ctypes.c_void_p),
              goo.ctypes.data_as(ctypes.c_void_p), gvv.ctypes.data_as(ctypes.c_void_p),
              dvo.ctypes.data_as(ctypes.c_void_p), dovov.ctypes.data_as(ctypes.c_void_p),
              dooov.ctypes.data_as(ctypes.c_void_p), dovvv.ctypes.data_as(ctypes.c_void_p),
              ctypes.c_int(with_gamma1), ctypes.c_int(with_gamma2))
    if err:
        raise MemoryError('CCsd_t_rdm_intermediates: failed to allocate thread buffers')
    return goo, gvv, dvo, dovov, dooov, dovvv

def _gamma1_intermediates('''
assert text.count("def _gamma1_intermediates(") == 1
text = text.replace("def _gamma1_intermediates(", helpers, 1)
tmp = R + ".tmp"
open(tmp, "w", encoding="utf-8").write(text)
os.replace(tmp, R)

L = "pyscf/cc/ccsd_t_lambda.py"
text = open(L, encoding="utf-8").read()
l_start = text.index("    nocc, nvir = t1.shape\n    eris_ovvv = numpy.asarray(eris.get_ovvv())")
l_end = text.index("    return imds\n\ndef update_lambda(")
assert l_start < l_end
l_new = '''    nocc, nvir = t1.shape
    mo_e, t1T, t2T, vooo, vvop, fvo, fov = ccsd_t_rdm._t3_kernel_args(t1, t2, eris)
    l1_t = numpy.zeros((nocc, nvir))
    joovv = numpy.zeros((nocc, nocc, nvir, nvir))
    drv = _ccsd.libcc.CCsd_t_lambda_intermediates
    drv.restype = ctypes.c_int
    err = drv(ctypes.c_int(nocc), ctypes.c_int(nvir),
              mo_e.ctypes.data_as(ctypes.c_void_p), t1T.ctypes.data_as(ctypes.c_void_p),
              t2T.ctypes.data_as(ctypes.c_void_p), vooo.ctypes.data_as(ctypes.c_void_p),
              vvop.ctypes.data_as(ctypes.c_void_p), fvo.ctypes.data_as(ctypes.c_void_p),
              fov.ctypes.data_as(ctypes.c_void_p), l1_t.ctypes.data_as(ctypes.c_void_p),
              joovv.ctypes.data_as(ctypes.c_void_p))
    if err:
        raise MemoryError('CCsd_t_lambda_intermediates: failed to allocate thread buffers')
    vvop = t2T = None
    log.timer_debug1('ccsd_t lambda make_intermediates (T) part', *time0)

    eia = lib.direct_sum('i-a->ia', mo_e[:nocc], mo_e[nocc:])
    imds.l1_t = l1_t / eia
    joovv = joovv + joovv.transpose(1, 0, 3, 2)
    imds.l2_t = joovv / lib.direct_sum('ia+jb->ijab', eia, eia)

'''
text = text[:l_start] + l_new + text[l_end:]
old_imds = "    imds = ccsd_lambda.make_intermediates(mycc, t1, t2, eris)\n"
assert text.count(old_imds) == 1
text = text.replace(old_imds, "    time0 = logger.process_clock(), logger.perf_counter()\n" + old_imds)
old_imp = "from pyscf.cc import ccsd, ccsd_lambda, _ccsd\n"
assert text.count(old_imp) == 1
text = text.replace(old_imp, "from pyscf.cc import ccsd, ccsd_lambda, ccsd_t_rdm, _ccsd\n")
tmp = L + ".tmp"
open(tmp, "w", encoding="utf-8").write(text)
os.replace(tmp, L)
print("ok")
