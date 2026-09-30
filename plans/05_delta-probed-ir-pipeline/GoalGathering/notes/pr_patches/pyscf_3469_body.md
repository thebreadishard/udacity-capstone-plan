`grad.ccsd_t.Gradients(mycc).kernel()` and `grad.uccsd_t.Gradients(mycc).kernel()` called without `l1`, `l2` inherit `ccsd.Gradients.kernel`, which takes `mycc.l1`/`mycc.l2` or calls `mycc.solve_lambda()` — the **CCSD** lambda — and passes it to the (T) density code. The returned vector is then not the derivative of the CCSD(T) energy. Nothing warns: the existing tests and the `__main__` examples pass the (T) lambda explicitly, so only the natural bare call is affected.

How we ran into it: water, RHF-CCSD(T)/cc-pVDZ, frozen core, against the central finite difference (h = 1e-3 bohr) of E_CCSD(T): the bare call is off by 1.5e-3 a.u.; with `ccsd_t_lambda.kernel`'s `l1`, `l2` it agrees to 1.5e-7. Harmonic frequencies from finite differences of the two gradients differ by 2.5–7.7 cm⁻¹.

### Change

- `grad/ccsd_t.py`, `grad/uccsd_t.py`: `Gradients.kernel` and `grad_elec` solve `ccsd_t_lambda` / `uccsd_t_lambda` when `l1` or `l2` is not given, instead of falling back to `mycc.l1`/`mycc.l2` or `mycc.solve_lambda()`. Explicitly passed multipliers are used unchanged. A warning is logged if the (T) lambda equations do not converge.
- Tests: `test_ccsd_t_grad_solves_t_lambda` and `test_uccsd_t_grad_solves_t_lambda` store the CCSD lambda with `mycc.solve_lambda()`, then check that the bare `Gradients(mycc).kernel()` (and, for RHF, `grad_elec()`) equals the gradient with the explicit (T) lambda; the UHF test also compares with the finite difference. Each test builds its own molecule, because `test_ccsd_t_grad` leaves the module-level `mol` displaced after its finite difference.

### Related, not changed here

`Gradients.as_scanner()` solves the CCSD lambda itself and passes it explicitly, and returns `cc.e_tot` without (T). With `grad.ccsd_t.Gradients(mycc).as_scanner()` on water/6-31G the returned energy misses E_(T) (9.96e-4 Eh) and the gradient is 9.0e-4 a.u. off the CCSD(T) gradient. A CCSD(T) gradient scanner would need its own `__call__`; happy to follow up if you want one.

### Tests

- [x] The two new tests fail on `master` without the change (max deviation 9.0e-4 a.u. RHF, 6.6e-4 a.u. UHF, water/6-31G) and pass with it.
- [x] `pytest -q pyscf/grad/test/test_ccsd.py pyscf/grad/test/test_ccsd_t.py pyscf/grad/test/test_uccsd_t.py pyscf/cc/test/test_ccsd_t.py pyscf/cc/test/test_uccsd_t.py pyscf/cc/test/test_rccsd_t_lambda.py pyscf/cc/test/test_ccsd_lambda.py pyscf/cc/test/test_uccsd_lambda.py`: **28 passed** (branch built from source, Python 3.12, WSL Ubuntu).
- [x] `ruff check --config .ruff.toml pyscf` and `ruff check --select NPY --ignore NPY002 pyscf` as in `lint.yml`: no findings in the changed files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
