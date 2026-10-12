import numpy
from pyscf import gto, lib
from pyscf.hessian import rhf as rhf_hess

mol = gto.M(atom="""C 0.000 1.396 0.000; C 1.209 0.698 0.000; C 1.209 -0.698 0.000; C 0.000 -1.396 0.000; C -1.209 -0.698 0.000;
                    C -1.209 0.698 0.000; H 0.000 2.479 0.000; H 2.147 1.240 0.000; H 2.147 -1.240 0.000; H 0.000 -2.479 0.000;
                    H -2.147 -1.240 0.000; H -2.147 1.240 0.000""", basis="6-31g*", verbose=0)
mf = mol.RKS(xc="pbe").run(conv_tol=1e-11)
hobj = mf.Hessian()
mo_coeff, mo_energy, mo_occ = mf.mo_coeff, mf.mo_energy, mf.mo_occ
h1ao = hobj.make_h1(mo_coeff, mo_occ)
mo1, _ = hobj.solve_mo1(mo_energy, mo_coeff, mo_occ, h1ao)

occ, vir = mo_occ > 0, mo_occ == 0
mocc = mo_coeff[:, occ]
fx = rhf_hess.gen_vind(mf, mo_coeff, mo_occ)
e_ai = 1 / (mo_energy[vir][:, None] - mo_energy[occ])
s1a = -mol.intor("int1e_ipovlp", comp=3)
ovlp = mf.get_ovlp()
worst = 0.0
for ia, (_, _, p0, p1) in enumerate(mol.aoslice_by_atom()):
    s1ao = numpy.zeros((3,) + ovlp.shape)
    s1ao[:, p0:p1] += s1a[:, p0:p1]
    s1ao[:, :, p0:p1] += s1a[:, p0:p1].transpose(0, 2, 1)
    s1 = lib.einsum("pq,xqr,ri->xpi", mo_coeff.T, s1ao, mocc)
    h1 = lib.einsum("pq,xqr,ri->xpi", mo_coeff.T, h1ao[ia], mocc)
    x = lib.einsum("pq,qr,xri->xpi", mo_coeff.T, ovlp, mo1[ia])
    resid = (mo_energy[vir][:, None] - mo_energy[occ]) * x[:, vir] + h1[:, vir] - s1[:, vir] * mo_energy[occ] + fx(x)[:, vir]
    worst = max(worst, abs(resid * e_ai).max())
print(f"requested tol {mf.conv_tol_cpscf * mol.natm:.1e}, true residual {worst:.1e}")
