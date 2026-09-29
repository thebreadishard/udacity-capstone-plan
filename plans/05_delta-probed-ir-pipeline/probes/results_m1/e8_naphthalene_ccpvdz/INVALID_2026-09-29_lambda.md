# INVALID — computed with the CCSD lambda, not the CCSD(T) lambda (found 29 September 2026, 20:5x)

Every gradient in this directory came from `pyscf.grad.ccsd_t.Gradients(mycc).kernel()` called without l1, l2. That call inherits
`ccsd_grad.Gradients.kernel`, which solves `mycc.solve_lambda` — the **CCSD** lambda equations — and feeds those amplitudes to the (T) density
code. The result is not the derivative of the CCSD(T) energy: on water (RHF/cc-pVDZ, frozen 1) it differs from the finite difference of
E_CCSD(T) by up to 1.5e-3 a.u. (10 % of the gradient) while the gradient with `ccsd_t_lambda.kernel`'s l1, l2 agrees to 1e-7; the water
frequencies shift by 2.5–7.7 cm⁻¹, benzene's E8 frequencies sit 20–75 cm⁻¹ below the empirical harmonic values out of plane and 100–120 above
in the C–H stretches (rms 62 cm⁻¹ against Goodman 1991). pyscf's own test (grad/test/test_ccsd_t.py) calls `ccsd_t_lambda.kernel` first.

The Hessian, frequencies, locality/between read-outs and everything derived from them (R1–R5, the CC-level standout test's hi_override,
E9 at CC, R5, the stop rule's W3) are therefore not CCSD(T) numbers. Kept for the record; the rerun with the explicit (T) lambda writes to a
new directory (`e8_benzene_ccpvdz_tlambda`, `e8_naphthalene_ccpvdz_f10_tlambda`). Evidence: `probes/results_m1/lambda_incident_2026-09-29/`.
