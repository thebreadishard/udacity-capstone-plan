The (T) parts of the RCCSD(T) lambda intermediates (`cc/ccsd_t_lambda.py` `make_intermediates`) and of the response-density intermediates (`cc/ccsd_t_rdm.py` `_gamma1_intermediates`, `_gamma2_intermediates`) are computed today by blocked `lib.einsum` contractions over six-index `w_blk`/`v_blk` blocks. On benzene/cc-pVDZ these two steps dominate an RCCSD(T) nuclear gradient, and they use a small fraction of the available cores.

This PR moves the triple loops to C (`lib/cc/ccsd_t_rdm.c`), following the (T) energy kernel in `ccsd_t.c`: for each virtual triple (a,b,c), W (12 connected terms) and V (6 disconnected terms) are built in thread-private nocc³ buffers with the same `dgemm` pattern as `get_wv`. The `t3_symm_ip` permutations (`"4-2-211-2"`, `"2-1000-1"`) are applied per triple, and the contractions are accumulated with `dgemm`/`dgemv`. No six-index block is materialised, so the working memory per thread is a few nocc³ arrays. The inputs are the same arrays the Python code already loads (`ovvv`, `ovov`, `ovoo`, `fock`), sorted once into `vvop`/`vooo`/`t2T` as in `ccsd_t.py`.

- `CCsd_t_lambda_intermediates`: l1_t and the unsymmetrised joovv of `make_intermediates`. OpenMP jobs over the first virtual index, which owns its output slices, so no reduction is needed.
- `CCsd_t_rdm_intermediates`: goo, gvv, dvo (gamma1) and dovov, dooov, dovvv (gamma2) in one pass, with flags so that `_gamma1_intermediates` and `_gamma2_intermediates` each compute only their part. Jobs run over the middle virtual index.
- The Python functions keep their signatures and their finishing steps (`/ eia`, the pair transpose, the `for_grad` branch, `compress_vvvv`). `max_memory` no longer sets a block size, since there are no blocks.

### Numbers (benzene, cc-pVDZ, frozen 6: nocc 15, nvir 93; AMD Ryzen 7 260, 8 cores / 16 threads, WSL2 Ubuntu, `lib.num_threads(16)`)

| step | master | this PR |
|---|---|---|
| `ccsd_t_lambda.make_intermediates` | 397.1 s | 23.9 s (16.6×) |
| `ccsd_t_lambda.kernel` (whole lambda solve) | 491.6 s | 98.3 s (5.0×) |
| `grad.ccsd_t.Gradients(...).kernel(t1, t2, l1, l2, eris)` | 1003.7 s | 69.9 s (14.4×) |

Both columns come from the same build of this branch; the master column uses master's unchanged `ccsd_t_lambda.py` / `ccsd_t_rdm.py` loaded over the same `libcc`. The two runs solve CCSD independently (`conv_tol` 1e-10), so l1_t/l2_t and the converged lambdas differ at the amplitude-convergence level (5e-11 / 1.6e-10 and 3.7e-10 / 6.6e-10); the gradients agree to 9.3e-14. On identical amplitudes the kernels agree with the Python code to 1e-16 (below). The remaining time of the lambda solve is the CCSD-lambda iterations, unchanged by this PR.

### Tests

- [x] `pyscf/cc/test/test_rccsd_t_lambda.py`, which compares `make_intermediates` and both gammas element-wise with the `*_slow` implementations and against the fingerprints to 9 digits (including the small-`max_memory` cases), plus `cc/test/test_ccsd_t.py`, `test_ccsd_lambda.py`, `test_gccsd_lambda.py`, `grad/test/test_ccsd_t.py` (gradient vs `ccsd_t_slow` and finite differences) and `grad/test/test_ccsd.py`: **20 passed**.
- [x] Against the Python implementation on identical amplitudes: water/cc-pVDZ (frozen core and all-electron, with and without point-group symmetry) ≤ 3e-18 for l1_t/l2_t and ≤ 4e-18 for every density intermediate; benzene/cc-pVDZ 3.1e-17 (l1_t) and 1.1e-16 (l2_t).
- [x] `ruff check --config .ruff.toml pyscf` and the NPY check from `lint.yml`: clean for the changed Python files; the C file compiles without warnings under `-Wall`.

Real inputs only, as before (the complex-input `ValueError`s are kept); the UHF (T) code is untouched. We have been running the same kernels in our own RCCSD(T) Hessian workflow since 29 September, each run checked against the Python route on its first gradient. Happy to change names, file placement or the flag interface to fit your conventions.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
