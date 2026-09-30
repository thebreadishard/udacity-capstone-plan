/*
 * (T) density intermediates of pyscf's CCSD(T) gradient in C.
 *
 * Reproduces, element for element, what pyscf/cc/ccsd_t_rdm.py (pyscf 2.14.0) computes in
 * _gamma1_intermediates (goo, gvv, the (T) part of dvo) and _gamma2_intermediates (the (T) parts
 * of dovov, dooov, dovvv), but per virtual triple (a,b,c) with thread-private nocc^3 buffers, on
 * the pattern of the (T) energy kernel (pyscf/lib/cc/ccsd_t.c: get_wv + add_and_permute).
 * No six-index tensor is materialised.  Design note: GoalGathering/notes/Design_Note_2026-09-29_T_Density_C_Kernel.md.
 *
 * Layouts (all row-major, doubles, active space only; nmo = nocc + nvir):
 *   mo_energy[nmo]                     eris.mo_energy
 *   t1T[nvir][nocc]                    t1.T
 *   t2T[nvir][nvir][nocc][nocc]        t2.transpose(2,3,1,0):  t2T[c][f][j][k] = t2[k,j,c,f]
 *   vooo[nvir][nocc][nocc][nocc]       ovoo.transpose(1,0,2,3): vooo[a][i][j][m] = ovoo[i,a,j,m]
 *   vvop[nvir][nvir][nocc][nmo]        vvop[a][b][i][j] = ovov[i,a,j,b] (j < nocc); vvop[a][b][i][nocc+f] = ovvv[i,a,f,b]
 *   fvo[nvir][nocc]                    fock[nocc:, :nocc]
 * Outputs are accumulated (+=; dooov -=) into caller-provided arrays:
 *   goo[nocc][nocc], gvv[nvir][nvir], dvo[nvir][nocc],
 *   dovov[nocc][nvir][nocc][nvir], dooov[nocc][nocc][nocc][nvir], dovvv[nocc][nvir][nvir][nvir].
 *
 * Per triple: W = the twelve connected terms, V = the six disconnected terms (the energy kernel's
 * six half-weighted permutations equal the density code's three full terms), both divided by
 * D3 = e_i + e_j + e_k - e_a - e_b - e_c; then with P(x) = 4x_ijk + x_jki + x_kij - 2x_kji - 2x_ikj - 2x_jik
 * (t3_symm_ip pattern "4-2-211-2"):
 *   gamma1: U = V + W, Wp = P(W):  goo[i][j] += sum_{kl} U(ikl) Wp(jkl);  gvv[a][a'] += sum_{ijk} U_abc Wp_a'bc;
 *           dvo[c][k] += 1/2 sum_{ij} t2[i,j,a,b] Wp(ijk)
 *   gamma2: V2 = P(V + 2W) = P(V) + 2 Wp, W2 = Wp / 2:
 *           dovov[i][a][j][b] += sum_k t1[k,c] W2(ijk);  dooov[j][m][i][a] -= sum_k t2[m,k,b,c] V2(ijk);
 *           dovvv[i][a][f][b] += sum_{jk} t2[k,j,c,f] V2(ijk)
 * Jobs are the middle virtual index b (OpenMP, dynamic): the slices dovov[:,:,:,b] and dovvv[:,:,:,b]
 * are then private to a job; goo, gvv, dvo, dooov are reduced under a critical section.
 */
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <omp.h>

void dgemm_(const char *, const char *, const int *, const int *, const int *, const double *,
            const double *, const int *, const double *, const int *, const double *, double *, const int *);
void dgemv_(const char *, const int *, const int *, const double *, const double *, const int *,
            const double *, const int *, const double *, double *, const int *);

static const char TN = 'N';
static const char TT = 'T';
static const int INC1 = 1;
static const double D0 = 0.0;
static const double D1 = 1.0;
static const double DN1 = -1.0;
static const double DHALF = 0.5;

/* out = fac * P(v) over the trailing (i,j,k) cube of edge n */
static void permute_into(double *out, const double *v, int n, double fac)
{
        const int nn = n * n;
        int i, j, k;
        for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
        for (k = 0; k < n; k++) {
                out[i*nn+j*n+k] = fac * (v[i*nn+j*n+k] * 4
                                       + v[j*nn+k*n+i]
                                       + v[k*nn+i*n+j]
                                       - v[k*nn+j*n+i] * 2
                                       - v[i*nn+k*n+j] * 2
                                       - v[j*nn+i*n+k] * 2);
        } } }
}

/* One permutation (a,b,c) of the triple: the energy kernel's get_wv with the half-weighted t1T and fvo.
 * cache[i][j][k] = sum_f ovvv[i,a,f,b] t2[k,j,c,f] - sum_m ovoo[i,a,j,m] t2[m,k,b,c];
 * added into w at position i*si + j*sj + k*sk (the occupied indices in the canonical order of the triple). */
static void wv_term(double *w, double *v, double *cache, int nocc, int nvir,
                    const double *vvop, const double *vooo, const double *t2T,
                    const double *t1Th, const double *fvoh,
                    int a, int b, int c, int si, int sj, int sk)
{
        const int nmo = nocc + nvir;
        const int noo = nocc * nocc;
        const size_t nooo = (size_t)nocc * noo;
        const size_t nvoo = (size_t)nvir * noo;
        const double *vv_op = vvop + ((size_t)a * nvir + b) * nocc * nmo;
        const double *pt2T = t2T + b * nvoo + a * noo;
        const double *t1c = t1Th + (size_t)c * nocc;
        const double *fc = fvoh + (size_t)c * nocc;
        int i, j, k, n, idx;

        dgemm_(&TN, &TN, &noo, &nocc, &nvir, &D1, t2T + c * nvoo, &noo, vv_op + nocc, &nmo, &D0, cache, &noo);
        dgemm_(&TN, &TN, &nocc, &noo, &nocc, &DN1, t2T + c * nvoo + b * noo, &nocc, vooo + a * nooo, &nocc, &D1, cache, &nocc);

        for (n = 0, i = 0; i < nocc; i++) {
        for (j = 0; j < nocc; j++) {
        for (k = 0; k < nocc; k++, n++) {
                idx = i * si + j * sj + k * sk;
                w[idx] += cache[n];
                v[idx] += vv_op[i*nmo+j] * t1c[k] + pt2T[i*nocc+j] * fc[k];
        } } }
}

int t_density_intermediates(int nocc, int nvir, const double *mo_energy,
                            const double *t1T, const double *t2T, const double *vooo,
                            const double *vvop, const double *fvo,
                            double *goo, double *gvv, double *dvo,
                            double *dovov, double *dooov, double *dovvv)
{
        const int noo = nocc * nocc;
        const int nooo = noo * nocc;
        const size_t nvoo = (size_t)nvir * noo;
        const size_t nov = (size_t)nvir * nocc;
        double *eijk = malloc(sizeof(double) * nooo);
        double *t1Th = malloc(sizeof(double) * nov * 2);
        double *fvoh = t1Th + nov;
        int failed = 0;
        size_t n;
        int i, j, k;

        if (eijk == NULL || t1Th == NULL) return 1;
        for (n = 0, i = 0; i < nocc; i++) {
        for (j = 0; j < nocc; j++) {
        for (k = 0; k < nocc; k++, n++) {
                eijk[n] = mo_energy[i] + mo_energy[j] + mo_energy[k];
        } } }
        for (n = 0; n < nov; n++) {
                t1Th[n] = t1T[n] * .5;
                fvoh[n] = fvo[n] * .5;
        }

#pragma omp parallel shared(failed)
{
        double *w = malloc(sizeof(double) * (size_t)nooo * 5);
        double *v = w + nooo;
        double *cache = v + nooo;
        double *vp = cache + nooo;
        double *v2 = vp + nooo;
        double *Umat = malloc(sizeof(double) * (size_t)nvir * nooo * 2);
        double *Wpmat = (Umat == NULL) ? NULL : Umat + (size_t)nvir * nooo;
        double *goo_p = calloc((size_t)noo + (size_t)nvir * nvir + nov, sizeof(double));
        double *gvv_p = goo_p + noo;
        double *dvo_p = gvv_p + (size_t)nvir * nvir;
        double *dooov_p = calloc((size_t)nvir * nooo, sizeof(double));       /* [a][i][j][m] */
        double *dovov_b = malloc(sizeof(double) * ((size_t)nvir * noo + (size_t)nvir * nocc * nvir));
        double *dovvv_b = (dovov_b == NULL) ? NULL : dovov_b + (size_t)nvir * noo;   /* [a][i][j] and [a][i][f] */
        int a, b, c, m, f, i, j;
        size_t nn;

        if (w == NULL || Umat == NULL || goo_p == NULL || dooov_p == NULL || dovov_b == NULL) {
#pragma omp atomic write
                failed = 1;
        }
#pragma omp barrier
        if (!failed) {
#pragma omp for schedule(dynamic, 1)
        for (b = 0; b < nvir; b++) {
                memset(dovov_b, 0, sizeof(double) * ((size_t)nvir * noo + (size_t)nvir * nocc * nvir));
                for (c = 0; c < nvir; c++) {
                        for (a = 0; a < nvir; a++) {
                                double *wp = Wpmat + (size_t)a * nooo;
                                double *u = Umat + (size_t)a * nooo;
                                const double eabc = mo_energy[nocc+a] + mo_energy[nocc+b] + mo_energy[nocc+c];
                                memset(w, 0, sizeof(double) * (size_t)nooo * 2);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, b, c, noo, nocc, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, c, b, noo, 1, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, a, c, nocc, noo, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, c, a, nocc, 1, noo);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, a, b, 1, noo, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, b, a, 1, nocc, noo);
                                for (nn = 0; nn < (size_t)nooo; nn++) {
                                        const double d = 1.0 / (eijk[nn] - eabc);
                                        w[nn] *= d;
                                        v[nn] *= d;
                                        u[nn] = v[nn] + w[nn];
                                }
                                permute_into(wp, w, nocc, 1.0);
                                permute_into(vp, v, nocc, 1.0);
                                for (nn = 0; nn < (size_t)nooo; nn++) v2[nn] = vp[nn] + 2.0 * wp[nn];

                                /* goo[i][j] += sum_m U[i][m] Wp[j][m] */
                                dgemm_(&TT, &TN, &nocc, &nocc, &noo, &D1, wp, &noo, u, &noo, &D1, goo_p, &nocc);
                                /* dvo[c][k] += 1/2 sum_{ij} t2T[b][a][i][j] Wp[i][j][k] */
                                dgemv_(&TN, &nocc, &noo, &DHALF, wp, &nocc, t2T + b * nvoo + a * noo, &INC1, &D1, dvo_p + (size_t)c * nocc, &INC1);
                                /* dovov_b[a][i][j] += 1/2 sum_k Wp[i][j][k] t1T[c][k] */
                                dgemv_(&TT, &nocc, &noo, &DHALF, wp, &nocc, t1T + (size_t)c * nocc, &INC1, &D1, dovov_b + (size_t)a * noo, &INC1);
                                /* dooov_p[a][i][j][m] += sum_k t2T[b][c][k][m] V2[i][j][k]   (subtracted at the end) */
                                dgemm_(&TN, &TN, &nocc, &noo, &nocc, &D1, t2T + b * nvoo + c * noo, &nocc, v2, &nocc, &D1, dooov_p + (size_t)a * nooo, &nocc);
                                /* dovvv_b[a][i][f] += sum_{jk} V2[i][j][k] t2T[c][f][j][k] */
                                dgemm_(&TT, &TN, &nvir, &nocc, &noo, &D1, t2T + c * nvoo, &noo, v2, &noo, &D1, dovvv_b + (size_t)a * nocc * nvir, &nvir);
                        }
                        /* gvv[a][a'] += sum_n U[a][n] Wp[a'][n] over the shared trailing pair (b,c) */
                        dgemm_(&TT, &TN, &nvir, &nvir, &nooo, &D1, Wpmat, &nooo, Umat, &nooo, &D1, gvv_p, &nvir);
                }
                /* the slices with trailing index b belong to this job alone */
                for (a = 0; a < nvir; a++) {
                        for (i = 0; i < nocc; i++) {
                                for (j = 0; j < nocc; j++)
                                        dovov[(((size_t)i * nvir + a) * nocc + j) * nvir + b] += dovov_b[((size_t)a * nocc + i) * nocc + j];
                                for (f = 0; f < nvir; f++)
                                        dovvv[(((size_t)i * nvir + a) * nvir + f) * nvir + b] += dovvv_b[((size_t)a * nocc + i) * nvir + f];
                        }
                }
        }
#pragma omp critical
        {
                for (nn = 0; nn < (size_t)noo; nn++) goo[nn] += goo_p[nn];
                for (nn = 0; nn < (size_t)nvir * nvir; nn++) gvv[nn] += gvv_p[nn];
                for (nn = 0; nn < nov; nn++) dvo[nn] += dvo_p[nn];
                for (a = 0; a < nvir; a++)
                for (i = 0; i < nocc; i++)
                for (j = 0; j < nocc; j++)
                for (m = 0; m < nocc; m++)
                        dooov[(((size_t)j * nocc + m) * nocc + i) * nvir + a] -= dooov_p[(((size_t)a * nocc + i) * nocc + j) * nocc + m];
        }
        }
        free(w); free(Umat); free(goo_p); free(dooov_p); free(dovov_b);
}
        free(eijk); free(t1Th);
        return failed;
}

/* out = fac * Q(v), Q(x) = 2 x_ijk - x_ikj - x_kji (t3_symm_ip pattern "2-1000-1") */
static void permute_q_into(double *out, const double *v, int n, double fac)
{
        const int nn = n * n;
        int i, j, k;
        for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) {
        for (k = 0; k < n; k++) {
                out[i*nn+j*n+k] = fac * (v[i*nn+j*n+k] * 2
                                       - v[i*nn+k*n+j]
                                       - v[k*nn+j*n+i]);
        } } }
}

/*
 * (T) intermediates of pyscf's CCSD(T) lambda equations (pyscf/cc/ccsd_t_lambda.py::make_intermediates, pyscf 2.14.0):
 * the same W (twelve connected terms) and V (six disconnected terms) per ordered virtual triple (a,b,c), divided by D3, then
 *   X  = Q(V + 2W):   joovv[i,j,a,e] += sum_{bck} ovvv[k,c,e,b] X(ijk)          ('kceb,abcijk->ijae')
 *                     joovv[i,j,a,b] -= sum_{cmn} ovoo[n,c,m,j] X(imn)          ('ncmj,abcimn->ijab')
 *   Wr = P(W)/2:      l1t[i,a]      += sum_{bcjk} ovov[j,b,k,c] Wr(ijk)        ('jbkc,abcijk->ia')
 *   Wq = Q(W)/2:      joovv[i,j,a,b] += sum_{ck} fock[k,nocc+c] Wq(ijk)        ('kc,abcijk->ijab')
 * Outputs (accumulated, caller zeroes them): l1t[nocc][nvir], joovv[nocc][nocc][nvir][nvir] — before pyscf's final
 * l1t /= eia and joovv + joovv.transpose(1,0,3,2), which the Python side applies. Inputs as t_density_intermediates, plus
 * fov[nocc][nvir] = fock[:nocc, nocc:]. Jobs are the first virtual index a (OpenMP, dynamic): every output element carries
 * a, so a job owns joovv[:,:,a,:] and l1t[:,a] and there is no reduction.
 */
int t_lambda_intermediates(int nocc, int nvir, const double *mo_energy,
                           const double *t1T, const double *t2T, const double *vooo,
                           const double *vvop, const double *fvo, const double *fov,
                           double *l1t, double *joovv)
{
        const int nmo = nocc + nvir;
        const int noo = nocc * nocc;
        const int nooo = noo * nocc;
        const size_t nov = (size_t)nvir * nocc;
        double *eijk = malloc(sizeof(double) * nooo);
        double *t1Th = malloc(sizeof(double) * nov * 2);
        double *fvoh = (t1Th == NULL) ? NULL : t1Th + nov;
        int failed = 0;
        size_t n;
        int i, j, k;

        if (eijk == NULL || t1Th == NULL) { free(eijk); free(t1Th); return 1; }
        for (n = 0, i = 0; i < nocc; i++) {
        for (j = 0; j < nocc; j++) {
        for (k = 0; k < nocc; k++, n++) {
                eijk[n] = mo_energy[i] + mo_energy[j] + mo_energy[k];
        } } }
        for (n = 0; n < nov; n++) {
                t1Th[n] = t1T[n] * .5;
                fvoh[n] = fvo[n] * .5;
        }

#pragma omp parallel shared(failed)
{
        /* w, v, cache, x (Q(V+2W), later Q(W)/2), wr (P(W)/2), xt (x with the trailing pair swapped) */
        double *w = malloc(sizeof(double) * (size_t)nooo * 6);
        double *v = (w == NULL) ? NULL : w + nooo;
        double *cache = (w == NULL) ? NULL : v + nooo;
        double *x = (w == NULL) ? NULL : cache + nooo;
        double *wr = (w == NULL) ? NULL : x + nooo;
        double *xt = (w == NULL) ? NULL : wr + nooo;
        double *jo_a = malloc(sizeof(double) * ((size_t)noo * nvir + (size_t)noo + noo + nocc));   /* [i][j][e] */
        double *rb = (jo_a == NULL) ? NULL : jo_a + (size_t)noo * nvir;                          /* [i][j] for the current b */
        double *g = (jo_a == NULL) ? NULL : rb + noo;                                            /* ovov[j,b,k,c] as [j][k] */
        double *l1_a = (jo_a == NULL) ? NULL : g + noo;
        int a, b, c, e, m;
        size_t nn;

        if (w == NULL || jo_a == NULL) {
#pragma omp atomic write
                failed = 1;
        }
#pragma omp barrier
        if (!failed) {
#pragma omp for schedule(dynamic, 1)
        for (a = 0; a < nvir; a++) {
                memset(jo_a, 0, sizeof(double) * (size_t)noo * nvir);
                memset(l1_a, 0, sizeof(double) * nocc);
                for (b = 0; b < nvir; b++) {
                        memset(rb, 0, sizeof(double) * noo);
                        for (c = 0; c < nvir; c++) {
                                const double eabc = mo_energy[nocc+a] + mo_energy[nocc+b] + mo_energy[nocc+c];
                                memset(w, 0, sizeof(double) * (size_t)nooo * 2);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, b, c, noo, nocc, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, c, b, noo, 1, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, a, c, nocc, noo, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, c, a, nocc, 1, noo);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, a, b, 1, noo, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, b, a, 1, nocc, noo);
                                for (nn = 0; nn < (size_t)nooo; nn++) {
                                        const double d = 1.0 / (eijk[nn] - eabc);
                                        w[nn] *= d;
                                        v[nn] = v[nn] * d + 2.0 * w[nn];            /* v now holds V + 2W */
                                }
                                permute_q_into(x, v, nocc, 1.0);
                                /* jo_a[i][j][e] += sum_k X[i][j][k] ovvv[k,c,e,b],  ovvv[k,c,e,b] = vvop[c][b][k][nocc+e] */
                                dgemm_(&TN, &TN, &nvir, &noo, &nocc, &D1, vvop + ((size_t)c * nvir + b) * nocc * nmo + nocc, &nmo,
                                       x, &nocc, &D1, jo_a, &nvir);
                                /* rb[i][j] -= sum_{mn} X[i][m][n] ovoo[n,c,m,j],  ovoo[n,c,m,j] = vooo[c][n][m][j]; xt[i][n][m] = X[i][m][n] */
                                for (i = 0; i < nocc; i++)
                                for (m = 0; m < nocc; m++)
                                for (k = 0; k < nocc; k++)
                                        xt[(size_t)i*noo + k*nocc + m] = x[(size_t)i*noo + m*nocc + k];
                                dgemm_(&TN, &TN, &nocc, &nocc, &noo, &DN1, vooo + (size_t)c * nooo, &nocc, xt, &noo, &D1, rb, &nocc);
                                /* l1_a[i] += sum_{jk} P(W)/2 [i][j][k] ovov[j,b,k,c],  ovov[j,b,k,c] = vvop[b][c][j][k] */
                                permute_into(wr, w, nocc, 0.5);
                                for (j = 0; j < nocc; j++)
                                for (k = 0; k < nocc; k++)
                                        g[j*nocc + k] = vvop[(((size_t)b * nvir + c) * nocc + j) * nmo + k];
                                dgemv_(&TT, &noo, &nocc, &D1, wr, &noo, g, &INC1, &D1, l1_a, &INC1);
                                /* rb[i][j] += sum_k Q(W)/2 [i][j][k] fov[k][c] */
                                permute_q_into(x, w, nocc, 0.5);
                                dgemv_(&TT, &nocc, &noo, &D1, x, &nocc, fov + c, &nvir, &D1, rb, &INC1);
                        }
                        for (i = 0; i < noo; i++)
                                jo_a[(size_t)i * nvir + b] += rb[i];
                }
                for (i = 0; i < nocc; i++) {
                        l1t[(size_t)i * nvir + a] += l1_a[i];
                        for (j = 0; j < nocc; j++)
                        for (e = 0; e < nvir; e++)
                                joovv[(((size_t)i * nocc + j) * nvir + a) * nvir + e] += jo_a[((size_t)i * nocc + j) * nvir + e];
                }
        }
        }
        free(w); free(jo_a);
}
        free(eijk); free(t1Th);
        return failed;
}

/*
 * Both sets of (T) intermediates in one pass (30 Sep 2026): the response-density parts of t_density_intermediates and the lambda parts
 * of t_lambda_intermediates depend only on t1, t2 and the integrals, and both are built from the same W and V per ordered triple, so
 * they are computed together (half the W/V work of calling the two kernels).  Job structure of t_density_intermediates (middle
 * virtual index b); the lambda accumulators are thread-private (joovv: nocc^2 nvir^2, l1t: nocc nvir) and reduced at the end.
 * Outputs as the two kernels (all accumulated; the caller zeroes them and finishes l1t / joovv as for t_lambda_intermediates).
 */
int t_fused_intermediates(int nocc, int nvir, const double *mo_energy,
                          const double *t1T, const double *t2T, const double *vooo,
                          const double *vvop, const double *fvo, const double *fov,
                          double *goo, double *gvv, double *dvo,
                          double *dovov, double *dooov, double *dovvv,
                          double *l1t, double *joovv)
{
        const int nmo = nocc + nvir;
        const int noo = nocc * nocc;
        const int nooo = noo * nocc;
        const int nvv = nvir * nvir;
        const size_t nvoo = (size_t)nvir * noo;
        const size_t nov = (size_t)nvir * nocc;
        double *eijk = malloc(sizeof(double) * nooo);
        double *t1Th = malloc(sizeof(double) * nov * 2);
        double *fvoh = (t1Th == NULL) ? NULL : t1Th + nov;
        int failed = 0;
        size_t n;
        int i, j, k;

        if (eijk == NULL || t1Th == NULL) { free(eijk); free(t1Th); return 1; }
        for (n = 0, i = 0; i < nocc; i++) {
        for (j = 0; j < nocc; j++) {
        for (k = 0; k < nocc; k++, n++) {
                eijk[n] = mo_energy[i] + mo_energy[j] + mo_energy[k];
        } } }
        for (n = 0; n < nov; n++) {
                t1Th[n] = t1T[n] * .5;
                fvoh[n] = fvo[n] * .5;
        }

#pragma omp parallel shared(failed)
{
        /* w, v, cache, vp, v2 (density); x, xt, wq (lambda) */
        double *w = malloc(sizeof(double) * (size_t)nooo * 8);
        double *v = (w == NULL) ? NULL : w + nooo;
        double *cache = (w == NULL) ? NULL : v + nooo;
        double *vp = (w == NULL) ? NULL : cache + nooo;
        double *v2 = (w == NULL) ? NULL : vp + nooo;
        double *x = (w == NULL) ? NULL : v2 + nooo;
        double *xt = (w == NULL) ? NULL : x + nooo;
        double *wq = (w == NULL) ? NULL : xt + nooo;
        double *Umat = malloc(sizeof(double) * (size_t)nvir * nooo * 2);
        double *Wpmat = (Umat == NULL) ? NULL : Umat + (size_t)nvir * nooo;
        double *goo_p = calloc((size_t)noo + (size_t)nvir * nvir + nov, sizeof(double));
        double *gvv_p = (goo_p == NULL) ? NULL : goo_p + noo;
        double *dvo_p = (goo_p == NULL) ? NULL : gvv_p + (size_t)nvir * nvir;
        double *dooov_p = calloc((size_t)nvir * nooo, sizeof(double));       /* [a][i][j][m] */
        double *dovov_b = malloc(sizeof(double) * ((size_t)nvir * noo + (size_t)nvir * nocc * nvir));
        double *dovvv_b = (dovov_b == NULL) ? NULL : dovov_b + (size_t)nvir * noo;
        double *jo_t = calloc((size_t)noo * nvv + nov + noo + noo, sizeof(double));   /* joovv [i][j][a][e], then l1t [i][a], rb, g */
        double *l1_t = (jo_t == NULL) ? NULL : jo_t + (size_t)noo * nvv;
        double *rb = (jo_t == NULL) ? NULL : l1_t + nov;
        double *g = (jo_t == NULL) ? NULL : rb + noo;
        int a, b, c, m, f;
        size_t nn;

        if (w == NULL || Umat == NULL || goo_p == NULL || dooov_p == NULL || dovov_b == NULL || jo_t == NULL) {
#pragma omp atomic write
                failed = 1;
        }
#pragma omp barrier
        if (!failed) {
#pragma omp for schedule(dynamic, 1)
        for (b = 0; b < nvir; b++) {
                memset(dovov_b, 0, sizeof(double) * ((size_t)nvir * noo + (size_t)nvir * nocc * nvir));
                for (c = 0; c < nvir; c++) {
                        for (a = 0; a < nvir; a++) {
                                double *wp = Wpmat + (size_t)a * nooo;
                                double *u = Umat + (size_t)a * nooo;
                                const double eabc = mo_energy[nocc+a] + mo_energy[nocc+b] + mo_energy[nocc+c];
                                memset(w, 0, sizeof(double) * (size_t)nooo * 2);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, b, c, noo, nocc, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, a, c, b, noo, 1, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, a, c, nocc, noo, 1);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, b, c, a, nocc, 1, noo);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, a, b, 1, noo, nocc);
                                wv_term(w, v, cache, nocc, nvir, vvop, vooo, t2T, t1Th, fvoh, c, b, a, 1, nocc, noo);
                                for (nn = 0; nn < (size_t)nooo; nn++) {
                                        const double d = 1.0 / (eijk[nn] - eabc);
                                        w[nn] *= d;
                                        v[nn] *= d;
                                        u[nn] = v[nn] + w[nn];
                                        cache[nn] = v[nn] + 2.0 * w[nn];            /* V + 2W for the lambda part */
                                }
                                permute_into(wp, w, nocc, 1.0);
                                permute_into(vp, v, nocc, 1.0);
                                for (nn = 0; nn < (size_t)nooo; nn++) v2[nn] = vp[nn] + 2.0 * wp[nn];

                                /* ---- density parts, as t_density_intermediates ---- */
                                dgemm_(&TT, &TN, &nocc, &nocc, &noo, &D1, wp, &noo, u, &noo, &D1, goo_p, &nocc);
                                dgemv_(&TN, &nocc, &noo, &DHALF, wp, &nocc, t2T + b * nvoo + a * noo, &INC1, &D1, dvo_p + (size_t)c * nocc, &INC1);
                                dgemv_(&TT, &nocc, &noo, &DHALF, wp, &nocc, t1T + (size_t)c * nocc, &INC1, &D1, dovov_b + (size_t)a * noo, &INC1);
                                dgemm_(&TN, &TN, &nocc, &noo, &nocc, &D1, t2T + b * nvoo + c * noo, &nocc, v2, &nocc, &D1, dooov_p + (size_t)a * nooo, &nocc);
                                dgemm_(&TT, &TN, &nvir, &nocc, &noo, &D1, t2T + c * nvoo, &noo, v2, &noo, &D1, dovvv_b + (size_t)a * nocc * nvir, &nvir);

                                /* ---- lambda parts, as t_lambda_intermediates (triple (a,b,c); outputs indexed by a) ---- */
                                permute_q_into(x, cache, nocc, 1.0);
                                /* jo_t[i][j][a][e] += sum_k X[i][j][k] ovvv[k,c,e,b]  (rows ij at stride nvir^2) */
                                dgemm_(&TN, &TN, &nvir, &noo, &nocc, &D1, vvop + ((size_t)c * nvir + b) * nocc * nmo + nocc, &nmo,
                                       x, &nocc, &D1, jo_t + (size_t)a * nvir, &nvv);
                                /* rb[i][j] = -sum_{mn} X[i][m][n] ovoo[n,c,m,j] + sum_k Q(W)/2 [i][j][k] fov[k][c] -> jo_t[i][j][a][b] */
                                for (i = 0; i < nocc; i++)
                                for (m = 0; m < nocc; m++)
                                for (k = 0; k < nocc; k++)
                                        xt[(size_t)i*noo + k*nocc + m] = x[(size_t)i*noo + m*nocc + k];
                                dgemm_(&TN, &TN, &nocc, &nocc, &noo, &DN1, vooo + (size_t)c * nooo, &nocc, xt, &noo, &D0, rb, &nocc);
                                permute_q_into(wq, w, nocc, 0.5);
                                dgemv_(&TT, &nocc, &noo, &D1, wq, &nocc, fov + c, &nvir, &D1, rb, &INC1);
                                for (i = 0; i < noo; i++)
                                        jo_t[(size_t)i * nvv + (size_t)a * nvir + b] += rb[i];
                                /* l1_t[i][a] += sum_{jk} P(W)/2 [i][j][k] ovov[j,b,k,c]  (P(W) is wp) */
                                for (j = 0; j < nocc; j++)
                                for (k = 0; k < nocc; k++)
                                        g[j*nocc + k] = vvop[(((size_t)b * nvir + c) * nocc + j) * nmo + k];
                                dgemv_(&TT, &noo, &nocc, &DHALF, wp, &noo, g, &INC1, &D1, l1_t + a, &nvir);
                        }
                        dgemm_(&TT, &TN, &nvir, &nvir, &nooo, &D1, Wpmat, &nooo, Umat, &nooo, &D1, gvv_p, &nvir);
                }
                for (a = 0; a < nvir; a++) {
                        for (i = 0; i < nocc; i++) {
                                for (j = 0; j < nocc; j++)
                                        dovov[(((size_t)i * nvir + a) * nocc + j) * nvir + b] += dovov_b[((size_t)a * nocc + i) * nocc + j];
                                for (f = 0; f < nvir; f++)
                                        dovvv[(((size_t)i * nvir + a) * nvir + f) * nvir + b] += dovvv_b[((size_t)a * nocc + i) * nvir + f];
                        }
                }
        }
#pragma omp critical
        {
                for (nn = 0; nn < (size_t)noo; nn++) goo[nn] += goo_p[nn];
                for (nn = 0; nn < (size_t)nvir * nvir; nn++) gvv[nn] += gvv_p[nn];
                for (nn = 0; nn < nov; nn++) dvo[nn] += dvo_p[nn];
                for (a = 0; a < nvir; a++)
                for (i = 0; i < nocc; i++)
                for (j = 0; j < nocc; j++)
                for (m = 0; m < nocc; m++)
                        dooov[(((size_t)j * nocc + m) * nocc + i) * nvir + a] -= dooov_p[(((size_t)a * nocc + i) * nocc + j) * nocc + m];
                for (nn = 0; nn < (size_t)noo * nvv; nn++) joovv[nn] += jo_t[nn];
                for (nn = 0; nn < nov; nn++) l1t[nn] += l1_t[nn];
        }
        }
        free(w); free(Umat); free(goo_p); free(dooov_p); free(dovov_b); free(jo_t);
}
        free(eijk); free(t1Th);
        return failed;
}
