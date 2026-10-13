# pyVPT2 PR: the FD: HESSIAN consistency checks compare independent routes (drafted 13 Oct 2026; **posted as philipmnel/pyvpt2#59 on the user's word, 'Ja, push en open de PR maar'**)

*Branch `check-routes-before-averaging` in `~/pyvpt2-fork` (WSL), one commit 7cba69c on upstream main 2eae571; not pushed. Posting needs the
user's word (GitHub). Replaces nothing: PR #58 was closed by us on 30 Sep; issue #57 stays open (this fixes the check, not the noise).*

---

**Title:** FD: HESSIAN: let check_cubic / check_quartic compare independent finite-difference routes

**Body:**

Refs #57.

With `FD: HESSIAN`, `assemble_quartic_from_hessians` averages the finite-difference routes into every element before calling the checks:

- φ_iijj (i ≠ j) is built from both the displacement along j (element ii) and the one along i (element jj);
- φ_ijk is built from the displacements along i, j and k.

So φ_iijj[i, j] and φ_iijj[j, i], and the permutations of φ_ijk, are equal by construction. `check_quartic` and `check_cubic` then compare
equal numbers and always print "No inconsistencies found". In #57 (benzene, B3LYP/6-31G*, psi4 finite-difference Hessians) the two quartic
routes disagreed by a median of 22 cm⁻¹ and up to 1,265 cm⁻¹ while the output said there were none.

This PR stores one route per element:
- φ_ijk[i, j, k] comes from the displacement along i;
- φ_iijj[i, j] comes from the displacement along j.

The other permutations hold the other routes. The checks now compare independent routes and then symmetrize exactly as before, so the
returned constants are unchanged up to rounding (≤ 1.2e-10 cm⁻¹ in the test). No other code path changes. The energy and gradient
assemblies are untouched.

**Tests** (`pyvpt2/tests/test_fd_hessian_checks.py`, synthetic quartic potential with known constants):
- exact Hessians: the constants are recovered (1e-6) and both checks report no inconsistency;
- 0.05 cm⁻¹ of noise on one displaced Hessian: the quartic check now lists the disagreeing pairs (25 cm⁻¹). The cubic check stays quiet,
  because the cubic difference is ~0.5 cm⁻¹, below its 1 cm⁻¹ line. The returned constants equal the previous assembly's;
- 0.5 cm⁻¹ of noise: both checks report.

On main the two noise tests fail and the exact one passes; on this branch all three pass. The existing Hessian-route tests (`test_h2o`,
`test_h2co`, `test_hcn`, `test_hf` with driver HESSIAN) pass unchanged: 18 passed locally with psi4 1.10.2. The qcengine, snowflake, CBS and
multilevel tests were not run (they need external setups).

---

Notes for us (not in the PR):
- Smaller than #58: no new report function, no new option, no behaviour change beyond the checks seeing what they were written to see.
- If the maintainer wants a hard failure on large disagreements, that is a follow-up. Our own code (`src/dpir/qff.py`) refuses above 10 cm⁻¹.
