# Pull requests to upstream projects — drafts and quality control (21 September 2026)

*Status, 08:2x: the user (07:5x) asked for the quality control and then submission. Done: [pyscf/pyscf-forge#212](https://github.com/pyscf/pyscf-forge/pull/212) ready for review after the clean-environment test run; [pyscf/pyscf-forge#213](https://github.com/pyscf/pyscf-forge/pull/213) (new: `setup.py` passes `PYSCF_SOURCE_DIR`; four-case build check, see the PR body). pyVPT2: upstream suite 27 passed / 10 skipped with the change, real-data replay matches the independent assembly → issue [philipmnel/pyvpt2#57](https://github.com/philipmnel/pyvpt2/issues/57) and PR [philipmnel/pyvpt2#58](https://github.com/philipmnel/pyvpt2/pull/58), 09:3x. Earlier text kept below.* *Status, 07:5x: the user asked (07:2x) to hold all PRs until the cover text and the quality control are discussed. One PR had already been
opened three minutes earlier and is now a **draft**: [pyscf/pyscf-forge#212](https://github.com/pyscf/pyscf-forge/pull/212). The pyVPT2
change is committed in the local fork branch only (not pushed). Both changes are archived as patch files in `probes/patches/` so they
survive the scratchpad. This note holds the texts as they stand and the quality-control list, for the conversation.*

## 1. pyscf-forge — `lno/lnoccsd.py` compatibility with pyscf ≥ 2.14 and NumPy 2

**Branch** `thebreadishard/pyscf-forge:lno-pyscf214-compat`, one commit, 8 insertions / 1 deletion. **PR #212, draft.**

**Title:** lno: compatibility with pyscf >= 2.14 (dfccsd._contract_vvvv_t2 signature) and NumPy 2 (_cp)

**Body as posted:**

> Two small compatibility fixes in `pyscf/lno/lnoccsd.py`, both hit in production LNO-CCSD(T) runs (benzene and naphthalene, cc-pVDZ/cc-pVTZ, pyscf 2.14.0, NumPy 2):
> 1. `DFLNOCCSD` / `_DFChemistsERIs._contract_vvvv_t2`: pyscf 2.14 changed `dfccsd._contract_vvvv_t2` to `(mycc, mol, vvL, VVL, t2, out=None, verbose=None)`. The existing six-argument call shifts the arguments (t2 arrives as `out`) and every DF-LNO-CCSD run fails. The call now inspects the installed signature and passes `vvL` twice on pyscf ≥ 2.14, keeping the old call for older pyscf.
> 2. `_cp`: `np.array(a, copy=False, order='C')` raises under NumPy 2 when a copy is unavoidable, which happens on the out-of-core path when the fragment's `Lov` block is an h5py slice (`max_memory` below its size). `np.asarray(a, order='C')` keeps the NumPy 1.x meaning.
>
> Test plan: py_compile ✓; DF-LNO-CCSD(T) on benzene and naphthalene with pyscf 2.14.0 / NumPy 2 since 2026-09-10 ✓; the shipped `pyscf/lno/test` suite on pyscf 2.14 ☐ (note on `test_ulnoccsd.py` failing independently: it unpacks `stability_jacobi()` as a pair).
> 🤖 Generated with Claude Code

**Quality control still open before it leaves draft:**
- Run the shipped `pyscf/lno/test` suite in a clean pyscf 2.14 environment on hel1-14 (the `qc05` env has pyscf 2.14 + our lno tree; a clean install of upstream main plus this patch is the honest test). Expected: everything passes except `test_ulnoccsd.py`'s pre-existing unpacking error.
- Check the pyscf-forge contributing guidelines (commit style, changelog entry, CI expectations) and the license header conventions.
- Decide on the attribution line ("Generated with Claude Code") — the user's call; the code change itself was ours since 10 September.
- Our local third edit (`stability_jacobi()[1]` in the `__main__` demo block) is wrong for pyscf 2.14 and stays out; revert it locally.

## 2. pyVPT2 — route-consistency report for the semi-diagonal quartic constants

**Branch** `thebreadishard/pyvpt2:quartic-route-consistency` (local only), one commit: `pyvpt2/quartic.py` +60/−6, `docs/tutorial.md` DISP_SIZE
entry, new `pyvpt2/tests/test_quartic_routes.py` (three tests, all pass in the `vpt2` environment: exact synthetic Hessians → zero
disagreement and φ_ijk, φ_iijj reproduced to 1e-6; 0.05 cm⁻¹ noise on one displaced Hessian → flagged at ≈ 20–25 cm⁻¹; single-mode edge case).

**Draft title:** quartic: report the disagreement between the two finite-difference routes to phi_iijj (Hessian route)

**Draft body:** the commit message (in the patch file): what the two routes are, why `check_quartic` cannot see the noise after averaging,
what is added (report with median/p90/max and worst pairs, warning above 10 cm⁻¹, `findifrec['quartic_route_report']`), the docstring and
tutorial changes, the tests, and the benzene motivation (median 22, max 1,265 cm⁻¹ with psi4 FD Hessians at DISP_SIZE 0.05 while the run
printed "No inconsistencies found"). Numerics of φ unchanged.

**Quality control still open:**
- Run pyVPT2's own test suite with the change (`pytest pyvpt2/tests`; several tests need psi4 and take minutes; the `vpt2` env lacks pytest — install it there or run on hel1-14 after the current jobs).
- A real-data check: run the patched assembly on the benzene cache (61 psi4 Hessians) through pyVPT2's normal path and confirm the report prints the same statistics as `probes/qff_from_hessians.py` (median 22.4, p90 107, max 1,264.5).
- Consider the gradient route too (`assemble_quartic_from_gradients` has the analogous two routes via gradient components i and j); out of scope for the first PR, mention in the text.
- An accompanying **issue** with the benzene numbers and the psi4 background, so the maintainer sees the evidence before the diff.
- Same attribution decision as above.

## 3. What is deliberately not proposed upstream (yet)

- A degenerate-mode (symmetric-top) treatment in pyVPT2: not until clean constants show it is needed (this morning's finding moved the cause to noise).
- Polyad eigenvector export for intensity redistribution: our own patch after 28 September, then possibly upstream.
- psi4: nothing to fix; the useful contribution would be a documentation sentence that DFT Hessians are finite differences of gradients — worth an issue, not a PR.
