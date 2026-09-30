"""Generate pyscf/lib/cc/ccsd_t_rdm.c from the verified project kernel (asserted anchors; the math is not edited)."""
SRC = "/mnt/c/Users/thebr/Documents/CapstonePlan/plans/05_delta-probed-ir-pipeline/probes/t_density_kernel/ccsd_t_rdm_kernel.c"
DST = "/home/thebreadishard/pyscf-master/pyscf/lib/cc/ccsd_t_rdm.c"
src = open(SRC, encoding="utf-8").read()


def rep(t, old, new, n=1):
    assert t.count(old) == n, (old[:70], t.count(old))
    return t.replace(old, new)


HEADER = """/* Copyright 2014-2026 The PySCF Developers. All Rights Reserved.

   Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

 *
 * Author: Frederic Petrignani <frederic.petrignani@gmail.com>
 *
 * (T) intermediates of the RCCSD(T) lambda equations and response densities
 * (cc/ccsd_t_lambda.py make_intermediates, cc/ccsd_t_rdm.py _gamma1/_gamma2_intermediates),
 * per virtual triple (a,b,c) with thread-private nocc^3 buffers, on the pattern of the (T)
 * energy kernel in ccsd_t.c (get_wv, add_and_permute).  No six-index block is materialised.
 *
 * Layouts (row-major doubles, active space; nmo = nocc + nvir):
 *   mo_energy[nmo], t1T[nvir][nocc] = t1.T, t2T[nvir][nvir][nocc][nocc] = t2.transpose(2,3,1,0),
 *   vooo[nvir][nocc][nocc][nocc] = ovoo.transpose(1,0,2,3),
 *   vvop[nvir][nvir][nocc][nmo]: vvop[a][b][i][j] = ovov[i,a,j,b] (j < nocc), vvop[a][b][i][nocc+f] = ovvv[i,a,f,b],
 *   fvo[nvir][nocc] = fock[nocc:,:nocc], fov[nocc][nvir] = fock[:nocc,nocc:].
 * Per triple: W = the twelve connected terms, V = the six disconnected terms, both divided by
 * D3 = e_i + e_j + e_k - e_a - e_b - e_c, and the permutation operators of t3_symm_ip:
 *   P(x) = 4 x_ijk + x_jki + x_kij - 2 x_kji - 2 x_ikj - 2 x_jik   ("4-2-211-2")
 *   Q(x) = 2 x_ijk - x_ikj - x_kji                                  ("2-1000-1")
 */
#include <stdlib.h>
#include <string.h>
#include "config.h"
#include "vhf/fblas.h"

"""

t = HEADER + src[src.index("static const char TN = 'N';"):]
t = rep(t, "int t_density_intermediates(int nocc, int nvir, const double *mo_energy,\n"
           "                            const double *t1T, const double *t2T, const double *vooo,\n"
           "                            const double *vvop, const double *fvo,\n"
           "                            double *goo, double *gvv, double *dvo,\n"
           "                            double *dovov, double *dooov, double *dovvv)\n",
        "/*\n"
        " * gamma1 (with_gamma1): U = V + W, Wp = P(W):  goo[i][j] += sum_{kl} U(ikl) Wp(jkl); gvv[a][a'] += sum_{ijk} U_abc Wp_a'bc;\n"
        " *     dvo[c][k] += 1/2 sum_{ij} t2[i,j,a,b] Wp(ijk)\n"
        " * gamma2 (with_gamma2): V2 = P(V + 2W), W2 = Wp / 2:  dovov[i][a][j][b] += sum_k t1[k,c] W2(ijk);\n"
        " *     dooov[j][m][i][a] -= sum_k t2[m,k,b,c] V2(ijk);  dovvv[i][a][f][b] += sum_{jk} t2[k,j,c,f] V2(ijk)\n"
        " * Outputs are accumulated.  Jobs are the middle virtual index b: dovov[:,:,:,b] and dovvv[:,:,:,b] are private to a job;\n"
        " * goo, gvv, dvo, dooov are reduced under a critical section.  Returns 1 if a thread could not allocate its buffers.\n"
        " */\n"
        "int CCsd_t_rdm_intermediates(int nocc, int nvir, const double *mo_energy,\n"
        "                             const double *t1T, const double *t2T, const double *vooo,\n"
        "                             const double *vvop, const double *fvo,\n"
        "                             double *goo, double *gvv, double *dvo,\n"
        "                             double *dovov, double *dooov, double *dovvv,\n"
        "                             int with_gamma1, int with_gamma2)\n")
t = rep(t, "                                /* goo[i][j] += sum_m U[i][m] Wp[j][m] */\n",
        "                                if (with_gamma1) {\n                                /* goo[i][j] += sum_m U[i][m] Wp[j][m] */\n")
t = rep(t, "dvo_p + (size_t)c * nocc, &INC1);\n",
        "dvo_p + (size_t)c * nocc, &INC1);\n                                }\n                                if (with_gamma2) {\n")
t = rep(t, "dovvv_b + (size_t)a * nocc * nvir, &nvir);\n                        }\n",
        "dovvv_b + (size_t)a * nocc * nvir, &nvir);\n                                }\n                        }\n")
t = rep(t, "                        dgemm_(&TT, &TN, &nvir, &nvir, &nooo, &D1, Wpmat, &nooo, Umat, &nooo, &D1, gvv_p, &nvir);\n",
        "                        if (with_gamma1)\n"
        "                        dgemm_(&TT, &TN, &nvir, &nvir, &nooo, &D1, Wpmat, &nooo, Umat, &nooo, &D1, gvv_p, &nvir);\n")
t = rep(t, "                /* the slices with trailing index b belong to this job alone */\n                for (a = 0; a < nvir; a++) {\n",
        "                /* the slices with trailing index b belong to this job alone */\n                if (with_gamma2)\n                for (a = 0; a < nvir; a++) {\n")
t = rep(t, "                for (nn = 0; nn < nov; nn++) dvo[nn] += dvo_p[nn];\n                for (a = 0; a < nvir; a++)\n",
        "                for (nn = 0; nn < nov; nn++) dvo[nn] += dvo_p[nn];\n                if (with_gamma2)\n                for (a = 0; a < nvir; a++)\n")
t = rep(t, "int t_lambda_intermediates(int nocc, int nvir, const double *mo_energy,\n"
           "                           const double *t1T, const double *t2T, const double *vooo,\n"
           "                           const double *vvop, const double *fvo, const double *fov,\n"
           "                           double *l1t, double *joovv)\n",
        "int CCsd_t_lambda_intermediates(int nocc, int nvir, const double *mo_energy,\n"
        "                                const double *t1T, const double *t2T, const double *vooo,\n"
        "                                const double *vvop, const double *fvo, const double *fov,\n"
        "                                double *l1t, double *joovv)\n")
t = rep(t, " * (T) intermediates of pyscf's CCSD(T) lambda equations (pyscf/cc/ccsd_t_lambda.py::make_intermediates, pyscf 2.14.0):\n",
        " * (T) intermediates of the CCSD(T) lambda equations (cc/ccsd_t_lambda.py make_intermediates):\n")
t = rep(t, "Inputs as t_density_intermediates, plus\n", "Inputs as CCsd_t_rdm_intermediates, plus\n")
assert "t_density_intermediates(" not in t and "pyscf 2.14" not in t and "Design note" not in t
open(DST, "w", encoding="utf-8").write(t)
print("written", t.count("\n"), "lines")
