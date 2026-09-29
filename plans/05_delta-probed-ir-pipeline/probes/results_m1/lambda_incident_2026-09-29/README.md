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

**Withdrawn 23:4x — not evidence:** benzene, E8 of 24 September (CCSD-lambda route) against the empirical harmonic frequencies of Goodman 1991 (`probes/data/benzene_benchmark_…json`):
sorted differences −20, −20, −2, −2, −42, −74, −21, −21, −27, −27, −47, 10, 36, 28, 28, 1, 9, 9, 46, 20, 32, 32, 92, 92, 100, 111, 111, 122, 122, 123 cm⁻¹
(rms 62). The rerun gave rms 65 against the same set: the Hessian stands on the B3LYP corpus geometry (reference gradient 7.7e-3 a.u.), not in the CCSD(T) minimum, and that geometry term, not the lambda, dominates the comparison. The valid check at benzene scale is the curvature check below.

## Consequences

- `probes/e8_cc_hessian_fd.py` solves the (T) lambda explicitly for every gradient (RHF `ccsd_t_lambda`, UHF `uccsd_t_lambda`; constant `LAMBDA_TOL`)
  and logs the lambda and gradient seconds; the `--fast-t-density` kernel is unaffected (its two-route check compares densities at the same l1, l2).
- All E8 results before 29 Sep 21:05 are marked INVALID in their directories; the runs of benzonitrile (hel1-23, 22 of 78 gradients) and
  naphthalene f10 (CCX53, 27 of 30) were stopped by pid at 21:05 and the reruns with the corrected route started at 21:10 (benzene, hel1-23,
  16 threads, symmetry: 12 + 1 gradients) and 21:12 (naphthalene f10, CCX53, 32 threads, symmetry).
- Upstream candidate: `grad.ccsd_t.Gradients` (and `grad.uccsd_t`) should solve the (T) lambda when l1/l2 are not given, or refuse; see
  `PR_Drafts_2026-09-21_Upstream_Fixes.md`.

## Benzene, 23:4x — the energy route at benzene scale (`benzene_curvature_check.py`, hel1-23, 338 s)

Central differences of E_CCSD(T) along three normal-mode directions of the new Hessian at the corpus geometry (unit Cartesian direction, h = 0.01 and 0.02 bohr, Richardson) against dᵀHd of the new Hessian (explicit (T) lambda, 22:47) and the old one (CCSD lambda, 24 Sep):

| mode | ω_new (cm⁻¹) | curvature FD of E_CCSD(T) (E_h/bohr²) | dᵀH_new d | rel. | dᵀH_old d | rel. | Δω old−FD (cm⁻¹) | Δω new−FD (cm⁻¹) |
|---|---|---|---|---|---|---|---|---|
| 6 | 361.9 | 0.01429773 | 0.01429745 | −1.9e-05 | 0.01557411 | +8.9e-02 | +16.2 | −0.0 |
| 10 | 609.4 | 0.01524684 | 0.01524807 | +8.0e-05 | 0.01638029 | +7.4e-02 | +22.7 | +0.0 |
| 35 | 3311.2 | 0.45711497 | 0.45711726 | +5.0e-06 | 0.45790455 | +1.7e-03 | +2.9 | +0.0 |

The new Hessian is the second derivative of the CCSD(T) energy to 2e-5 relative; the old one was 7–9 % off on the out-of-plane modes. New against old frequencies over all 30 modes: −3…−27 cm⁻¹, rms 14.