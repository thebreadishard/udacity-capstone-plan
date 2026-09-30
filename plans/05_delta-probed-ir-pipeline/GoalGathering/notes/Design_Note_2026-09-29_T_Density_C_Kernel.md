# Design note, 29 September 2026 — a C kernel for the (T) density intermediates of pyscf's CCSD(T) gradient

*Desk work while the anchors run. The measurement that motivates it: benzene's CCSD(T)/cc-pVDZ gradient spends 979 of 1,012 s (4 threads) in the
gradient stage, and ≈ 650 s of that is single-threaded Python/numpy inside `pyscf/cc/ccsd_t_rdm.py` (`_gamma1_intermediates` 295 s own time,
`_gamma2_intermediates` 292 s), identical at 1 and 4 threads; the (T) energy does the same t₃ work in the C kernel of `pyscf/lib/cc/ccsd_t.c` in 14 s
(`probes/results_m1/profiles/`, 29 Sep). Plan on the task board: Wed 30 Sep kernel + water, Thu 1 Oct correctness and timing, Fri 2–3 Oct naphthalene
timing and PR concept. The kernel is ours to use before any upstream decision (standalone shared library, loaded by our own module).*

## 1. What the Python code does (read 29 Sep, pyscf 2.14.0)

Both functions build, block by block over virtual triples (a,b,c) with all occupied triples (i,j,k), the same two six-index tensors the (T) energy uses:

- `W_abc(ijk)` = six `ovvv·t2` permutations minus six `ovoo·t2` permutations (the connected triples), then divided by `D3 = e_ia + e_jb + e_kc`;
- `V_abc(ijk)` = three `ovov·t1` terms plus three `fock_vo·t2` terms (the disconnected triples), divided by `D3`.

Then, per block:

| function | after W, V | symmetrisation (`t3_symm_ip`, pattern "4-2-211-2", already C) | contractions accumulated |
|---|---|---|---|
| `_gamma1_intermediates`, pass 1 (virtual blocks) | `V += W` | `W ← P(W)` with factor 1 | `goo[i,j] += Σ_{abc,kl} V_abc(ikl) W_abc(jkl)` |
| `_gamma1_intermediates`, pass 2 (occupied blocks, W and V rebuilt as (ijk,abc)) | `V += W` | `W ← P(W)` | `gvv[a,b] += Σ V(ijk,acd) W(ijk,bcd)`; `dvo[c,k] += ½ Σ t2(ijab) W(ijk,abc)` |
| `_gamma2_intermediates` (virtual blocks) | `V += 2W` | `V ← P(V)` factor 1; `W ← P(W)` factor ½ | `dovov[i,a,j,b] += Σ_k t1(kc) W_abc(ijk)`; `dooov[j,m,i,a] −= Σ t2(mkbc) V_abc(ijk)`; `dovvv[i,a,f,b] += Σ t2(kjcf) V_abc(ijk)` |

`P` is `add_and_permute` of the energy kernel: `4·x_ijk + x_jki + x_kij − 2·x_kji − 2·x_ikj − 2·x_jik`. Everything else is elementwise work on tensors
of size nocc³·nvir³ (benzene frozen 6: 15³·93³ ≈ 2.7·10⁹ doubles per pass, touched several times) — that is the 650 s.

## 2. Kernel design

One C routine per function, same structure as `CCsd_t_contract`:

1. **Loop over virtual triples (a,b,c)** (gamma1 pass 1 and gamma2: `a ≥ b ≥ c` with the permutational weights of the energy kernel; gamma1 pass 2 needs
   the (ijk,abc) layout — transpose the accumulation instead of rebuilding: `gvv` and `dvo` are also sums over (a,b,c) triples of W_abc(ijk), so one loop
   serves both passes; to be verified numerically on water first, it is the one place where the two passes could differ by a permutation factor).
2. **Per triple**: `get_wv` six times (the energy kernel's routine: two `dgemm` calls per permutation, nocc²×nocc×nvir and nocc×nocc²×nocc), giving
   W(ijk) and V(ijk) of size nocc³ in thread-private buffers. Note the factors: the energy kernel passes `t1T·½` and `fvo·½` and adds W into V; the
   density code uses full `t1`, full `fock` and adds W (gamma1) or 2W (gamma2) **after** the division by D3. The kernel takes the un-halved arrays and
   applies the division and the addition itself; the first water test pins these factors against the Python result to 1e-12.
3. **Divide by D3, symmetrise** (reuse `add_and_permute` with the right factor), **accumulate** the contractions with `dgemm`/`daxpy` into thread-private
   copies of `goo` (nocc²), `gvv` (nvir²), `dvo` (nvir·nocc), and for gamma2 `dovov`, `dooov`, `dovvv` (the last is nocc·nvir³ per thread — for benzene
   12 MB, for naphthalene 40 MB; acceptable, otherwise accumulate `dovvv` under a critical section per triple).
4. **OpenMP over triples**, `schedule(dynamic)`, reduction of the private accumulators at the end. Memory per thread: 3·nocc³ doubles + the private
   accumulators; no six-index tensor is ever materialised.
5. **Inputs** prepared in Python exactly as `ccsd_t.kernel` does (`_sort_eri` → `vvop`, `_sort_t2_vooo_` → `t2T`, `vooo`, `fvo`, `t1T`), so the kernel
   reads the same sorted integrals as the energy kernel and the two agree on conventions by construction.

Expected: the ≈ 650 s serial floor disappears; what remains is the `dgemm` work (233 s at 4 threads for benzene, scaling with threads) plus the
accumulations. Benzene at 16 threads from ≈ 11 min to 3–4 min per gradient; anchors ×3 on every machine.

## 3. Build and use, before any PR

- One file `dpir/ext/ccsd_t_rdm_kernel.c` (OpenMP, BLAS through the symbols pyscf's own `libnp_helper`/`libcc` already link, or plain `dgemm_` from the
  environment's BLAS), compiled with one `gcc -O3 -fopenmp -shared -fPIC` line by `tools/build_ext.sh`; no pyscf rebuild.
- `dpir/ccsd_t_rdm_fast.py`: loads the library through `ctypes`, exposes `gamma1_intermediates(mycc, t1, t2, l1, l2, eris)` and `gamma2_…` with pyscf's
  signatures, and `install()` which replaces the two functions in `pyscf.cc.ccsd_t_rdm` (the gradient module imports the module, not the names, so the
  replacement is seen).
- `probes/e8_cc_hessian_fd.py --fast-t-density`: calls `install()`; on the **reference gradient of every run** it also computes the densities with pyscf's
  Python functions and refuses to continue if any element differs by more than 1e-10 (the noise principle applied to our own speed-up; the check costs
  one Python pass per run, ≈ 16 min on benzene at 16 threads, nothing against 54 gradients).
- Tests: water (RHF, frozen 1) and benzene (frozen 6) densities equal to 1e-10; gradient equal to 1e-8; `tests/test_t_density_kernel.py` skipped where
  the library is not built.

## 4. What could go wrong, and the checks

- Factor conventions between the energy kernel's halved arrays and the density code (§2.2): pinned on water first.
- gamma1 pass 2 accumulation through the (a,b,c) loop instead of the (i,j,k) loop: an exact identity if the permutational weights are right; checked on
  water and benzene (two point groups, two frozen-core sizes).
- Frozen core: the density functions work in the active space; the kernel must receive the active-space arrays only (as `ccsd_t.kernel` does).
- UHF (the cation): `pyscf.grad.uccsd_t` has its own `uccsd_t_rdm`; out of scope for this kernel — the cation runs on the Python path.
- Symmetry (`nirrep > 1`): the energy kernel has `sym_wv`; the first version handles `nirrep == 1` only (our runs use `symmetry=False`).

## 5. Upstream

The same kernel, placed in `pyscf/lib/cc/ccsd_t.c` beside the energy kernel, with `ccsd_t_rdm.py` calling it when the arrays are real and `nirrep == 1`,
is the PR (§4 of `PR_Drafts_2026-09-21_Upstream_Fixes.md`): a pull request with the before/after timings on benzene and naphthalene and the 1e-10
agreement, after the user's word.

## 6. Built the same evening (21:0x) — and what the water smoke found

`probes/t_density_kernel/ccsd_t_rdm_kernel.c` (one OpenMP pass over the middle virtual index b, all six (T) contributions at once, thread-private
nocc³ buffers, `dgemm`/`dgemv` accumulations, the slices with trailing index b private to a job, the rest reduced under a critical section),
`t_density_fast.py` (ctypes; `install()` swaps the three functions in `pyscf.cc.ccsd_t_rdm`; the result is cached per (t1, t2, eris) so gamma1
and gamma2 pay once; `check_against_pyscf` is the second route), `build.sh` (links against pyscf's bundled OpenBLAS and libgomp so the process
never carries two OpenMP runtimes; the WSL build loads unchanged on the CCX53 because the wheel is the same). Water: every intermediate equal to
pyscf's to 4e-18, gradient to 1e-8, with and without point-group symmetry; `tests/test_t_density_kernel.py` (4) and `tests/test_e8_fast_t_density.py`
(2, source level). `e8_cc_hessian_fd.py --fast-t-density` installs it and runs the two-route check on the reference gradient of every run
(`FAST_T_LIMIT` 1e-10; refuses otherwise).

The smoke also exposed that the probe's gradients had never been CCSD(T) gradients (`Gradients(mycc).kernel()` without l1, l2 uses the CCSD
lambda — §5 of the PR drafts, ledger 21:1x). The probe now solves the (T) lambda explicitly; the reruns of benzene and naphthalene f10 give the
first timings of lambda + kernel gradient at PAH size. Point §4's "factor conventions" check passed at the first attempt; the (a,b,c)-loop
accumulation of gvv (§2.1) is exact.

## Addendum 30 September 2026 — the (T)-lambda kernel

`t_lambda_intermediates` in the same C file computes the (T) part of `ccsd_t_lambda.make_intermediates` (pyscf 2.14): for every ordered virtual
triple (a,b,c) the same W and V as the density kernel (`wv_term` × 6, divided by D3), then X = Q(V + 2W) with Q(x) = 2x_ijk − x_ikj − x_kji
(`t3_symm_ip` pattern "2-1000-1", checked in pyscf's `lib/cc/ccsd_t_lambda.c`), P(W)/2 and Q(W)/2, contracted into joovv[i,j,a,e] (ovvv term),
joovv[i,j,a,b] (ovoo and fock-ov terms) and l1_t[i,a]. Jobs are the first virtual index a, so each job owns joovv[:,:,a,:] and l1_t[:,a]; the
Python side finishes as pyscf does (l1_t / eia; joovv + its pair transpose, / (eia + ejb)). No triple symmetry is used yet (every ordered triple
builds its own W — the same count as pyscf's blocked loop); computing W once per unordered triple would cut the dominant cost about six-fold if the
anchors need it. Verified against pyscf: water ≤ 3e-18, benzene/cc-pVDZ 1e-16 with 44 s against 373 s on the laptop (16 threads)
(`probes/t_density_kernel/evidence/`).

**Addendum 30 September 10:2x — fused pass.** `t_fused_intermediates` computes the density and lambda parts from one W/V per ordered triple (the
density parts do not depend on l1, l2), with the density kernel's jobs over b and thread-private lambda accumulators (joovv at row stride nvir²,
l1t at stride nvir); `lambda_kernel()` runs it and caches the density part for the gradient. Benzene/cc-pVDZ production: lambda + gradient 128.6 →
90.3 s; fused vs separate ≤ 1e-14, vs pyscf 3.4e-14 on the gradient. Not in pyscf/pyscf#3470 (which keeps pyscf's gamma/lambda API).
