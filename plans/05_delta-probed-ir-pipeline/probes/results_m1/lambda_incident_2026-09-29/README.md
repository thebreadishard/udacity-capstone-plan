# Lambda incident, 29 September 2026 — pyscf's CCSD(T) gradient without an explicit (T) lambda is not dE/dx

Found while smoke-testing the (T) density C kernel on water (20:5x): the probe's reference gradient (explicit `ccsd_t_lambda`) and its displaced
gradients (`Gradients(mycc).kernel()`, no l1/l2) failed the pair check at 1.5e-3 a.u. The cause is in pyscf, not in the kernel: `grad.ccsd_t.Gradients`
overrides only `grad_elec`; its inherited `kernel` solves `mycc.solve_lambda`, the CCSD lambda (`cc/ccsd.py`), whenever l1/l2 are not passed.

## Evidence (water, RHF/cc-pVDZ, frozen 1, geometry `water_lambda_routes.py`; pyscf 2.14.0, WSL)

Finite differences of E_CCSD(T) (h = 1e-3 bohr, central) against the two analytic routes:

| component | FD of E_CCSD(T) | `Gradients(mycc).kernel()` (CCSD lambda) | with `ccsd_t_lambda` l1, l2 |
|---|---|---|---|
| O z | −0.01464913 | −0.01312475 (+1.5e-3) | −0.01464904 (+8.5e-8) |
| H y | −0.00355541 | −0.00291474 (+6.4e-4) | −0.00355527 (+1.5e-7) |
| H z | +0.00732456 | +0.00656237 (−7.6e-4) | +0.00732452 (−3.8e-8) |

FD Hessians of both routes (step 0.005 bohr, all 9 coordinates; `water_lambda_routes.npz`, `.log`): frequencies 1651.3 / 3930.5 / 4054.3 cm⁻¹
(CCSD lambda) against 1643.6 / 3925.3 / 4051.8 (CCSD(T) lambda), shifts −7.7 / −5.2 / −2.5 cm⁻¹; max |ΔH| 2.5e-3 a.u. pyscf's own test
(`pyscf/grad/test/test_ccsd_t.py`, master) calls `ccsd_t_lambda.kernel(mycc, eris, t1, t2)` before `Gradients(mycc).kernel(t1, t2, l1, l2, eris=eris)`
and compares with finite differences to 5 decimals.

Benzene, E8 of 24 September (CCSD-lambda route) against the empirical harmonic frequencies of Goodman 1991 (`probes/data/benzene_benchmark_…json`):
sorted differences −20, −20, −2, −2, −42, −74, −21, −21, −27, −27, −47, 10, 36, 28, 28, 1, 9, 9, 46, 20, 32, 32, 92, 92, 100, 111, 111, 122, 122, 123 cm⁻¹
(rms 62). A CCSD(T)/cc-pVDZ harmonic set should sit within ≈ 10–40 cm⁻¹ of these values; the rerun decides how much of the 62 was the lambda.

## Consequences

- `probes/e8_cc_hessian_fd.py` solves the (T) lambda explicitly for every gradient (RHF `ccsd_t_lambda`, UHF `uccsd_t_lambda`; constant `LAMBDA_TOL`)
  and logs the lambda and gradient seconds; the `--fast-t-density` kernel is unaffected (its two-route check compares densities at the same l1, l2).
- All E8 results before 29 Sep 21:05 are marked INVALID in their directories; the runs of benzonitrile (hel1-23, 22 of 78 gradients) and
  naphthalene f10 (CCX53, 27 of 30) were stopped by pid at 21:05 and the reruns with the corrected route started at 21:10 (benzene, hel1-23,
  16 threads, symmetry: 12 + 1 gradients) and 21:12 (naphthalene f10, CCX53, 32 threads, symmetry).
- Upstream candidate: `grad.ccsd_t.Gradients` (and `grad.uccsd_t`) should solve the (T) lambda when l1/l2 are not given, or refuse; see
  `PR_Drafts_2026-09-21_Upstream_Fixes.md`.
