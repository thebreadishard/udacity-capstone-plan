We ran into this from the side of dipole derivatives (IR intensities) and can add numbers, a short reproduction, and a check that master's #3334 does not change it.

**Reproduction** (pyscf 2.14.0, ~100 s): the nuclear-Hessian CPHF solution of benzene, PBE/6-31G*, default grid, inserted back into the linear system `solve_withs1` solves.

```python
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
```

Output: `requested tol 1.2e-07, true residual 9.2e-05`.

**What we measured around it** (benzene, 6-31G* Cartesian, grid (99, 590)):
- Raising `max_cycle` to 200 and lowering `conv_tol_cpscf` to 1e-12 changes the solution by 7e-11: `lib.krylov` exits at the same point.
- With master's `lib/linalg_helper.py` and `scf/cphf.py` (52f5737, after #3334) laid over 2.14.0, the residual is 5.6e-5 (2.14.0: 6.8e-5), consistent with #3334's note that it does not address this issue.
- The pieces of the system are accurate: `make_h1` against finite differences of the Fock matrix on a frozen grid falls as h² (5e-5, 1.3e-5, 3.3e-6 at h = 0.01, 0.005, 0.0025); `gen_response(hermi=1)` against finite differences of `get_veff` agrees to 8e-10; HF converges (residual 3e-8).
- The Hessian itself is insensitive at this level (0.06 cm⁻¹ against central differences of the analytic gradient on the same frozen grid), but quantities linear in the response are not: dipole derivatives contracted from `mo1` differ from the field derivative of the analytic gradient by 4.3e-4 e (B3LYP).
- One round of defect correction fixes it cheaply: form the residual of all 3N right-hand sides in one batched `fx` call, solve the correction equation with the same multi-root `lib.krylov`, add. The residual goes from 1.3e-4 to 7.8e-8 and the dipole derivatives to 3.8e-5 of the finite-field values, for about 120 s on top of a 780 s Hessian (4 threads).

If useful, we could turn that defect-correction round (check the true residual after `lib.krylov` in `solve_withs1`, and solve once more on the residual when it exceeds `tol`) into a pull request with a test.
