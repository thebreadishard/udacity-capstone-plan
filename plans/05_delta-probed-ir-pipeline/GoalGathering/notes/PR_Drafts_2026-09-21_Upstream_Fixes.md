# Pull requests to upstream projects — drafts and quality control (21 September 2026)

*Status, 08:2x: the user (07:5x) asked for the quality control and then submission. Done: [pyscf/pyscf-forge#212](https://github.com/pyscf/pyscf-forge/pull/212) ready for review after the clean-environment test run; [pyscf/pyscf-forge#213](https://github.com/pyscf/pyscf-forge/pull/213) (new: `setup.py` passes `PYSCF_SOURCE_DIR`; four-case build check, see the PR body). pyVPT2: upstream suite 27 passed / 10 skipped with the change, real-data replay matches the independent assembly → issue [philipmnel/pyvpt2#57](https://github.com/philipmnel/pyvpt2/issues/57) and PR [philipmnel/pyvpt2#58](https://github.com/philipmnel/pyvpt2/pull/58), 09:3x. Earlier text kept below.* *Status, 07:5x: the user asked (07:2x) to hold all PRs until the cover text and the quality control are discussed. One PR had already been
opened three minutes earlier and is now a **draft**: [pyscf/pyscf-forge#212](https://github.com/pyscf/pyscf-forge/pull/212). The pyVPT2
change is committed in the local fork branch only (not pushed). Both changes are archived as patch files in `probes/patches/` so they
survive the scratchpad. This note holds the texts as they stand and the quality-control list, for the conversation.*

## 1. pyscf-forge — `lno/lnoccsd.py` compatibility with pyscf ≥ 2.14 and NumPy 2

**Branch** `thebreadishard/pyscf-forge:lno-pyscf214-compat`, one commit, 8 insertions / 1 deletion. **PR #212, draft.**

**Review and rework, 29 September 08:1x.** M. Hermes (24/25 Sep): the shipped suite passes on pyscf 2.14.0 / NumPy 2 — show inputs that raise the errors, inspect the pyscf version instead of a try/except, add regression tests (changes requested). Cause found: both fixes sit in the DF-CCSD fragment solver (`MODIFIED_DFCCSD` / `_make_df_eris` / `_DFChemistsERIs`), chosen by `lnoccsd.CCSD` only when a fragment's vvvv block does not fit 70 % of the available memory; the water-dimer tests never reach it, our naphthalene cc-pVTZ runs did. Reproducer on the test molecule: `MODIFIED_DFCCSD(mf, frozen=2)` with `max_memory = 1` → unpatched `ValueError` in `_cp` (NumPy 2, non-contiguous Lov slice), with `_cp` fixed `AttributeError` in `dfccsd._contract_vvvv_t2` (t2 arrives as VVL), both fixed → e_corr = `cc.CCSD` to 1.2e-8 (clean venv, pyscf 2.14.0, NumPy 2.5.3, unpatched forge master via PYSCF_EXT_PATH). pyscf's seven-argument signature exists since at least v2.10, so the six-argument call was wrong for every supported version: rework calls it unconditionally (no inspect, no version check), keeps `_cp` → `np.asarray`, adds `test_dfccsd_solver_blocked_df_eris` (fails on master, passes on the branch). Full `pyscf/lno/test` (6 tests, `test_ulnoccsd_t` included) passes on hel1-23 with `liblno` built from the branch (cmake + OpenBLAS installed there, niced beside the CC run; the pyscf lib dir on LD_LIBRARY_PATH). Commit 1141631 pushed to the PR branch (the user: 'Concept is goed'); the reply text is in the session (`pr212_reply.md`) — posted 08:1x after the user's explicit permission for this comment (https://github.com/pyscf/pyscf-forge/pull/212#issuecomment-5884744000). Side finding for a separate issue: `max_memory` below the process RSS makes `make_lno_rdm1._mp2_rdm1_occblksize` take a square root of a negative number (`np.floor` TypeError).

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

## 4. Candidate (29 September 07:0x, the user: "op de takenlijst") — pyscf `grad/ccsd_t`: thread scaling of the (T) gradient

**What is measured, not yet diagnosed.** pyscf 2.14's CCSD(T) gradient (`pyscf.grad.ccsd_t.Gradients`, `pyscf.grad.uccsd_t`) runs the (T) energy and the
λ / density contractions through `libcc` (C), yet a benzene gradient takes 695 s at 24 threads against 663–692 s at 16 (CCX53 vs CPX62, 24 September), and
benzonitrile's gradient keeps ≈ 3.4 of 16 cores busy on average (hel1-23, 29 September; 42 min per gradient, 15 GB). The loss is thread scaling, not
"Python": `grad/ccsd_t.py` is 149 lines of orchestration. Nothing of ours converts this to Fortran or C; the project's own levers so far are symmetry-unique
displacements and parallel partial runs.

**Before any PR (quality control, in order):** (1) a profile of one benzene gradient at 1, 4, 8, 16 threads (`cProfile` + `lib.num_threads`) that names the
serial time: `ccsd_t_lambda` blocks, `ccsd_t_rdm` blocks, the `numpy.einsum` calls (22 and 60 of them) against the `libcc` kernels, and the CCSD λ
equations; (2) if one block carries most of the serial time, a patch (lib.einsum / blocked contraction / OpenMP in the C kernel) with the shipped tests
and a before/after timing on benzene and naphthalene; (3) only then a draft PR to pyscf with the numbers. Until (1) exists this note makes no claim about
the cause. Cheaper for us either way: several gradients per molecule in parallel with fewer threads each (task board).

**Profile, 29 September 11:2x** (`probes/results_m1/profiles/profile_t_grad_{4,1}.txt`, script `profile_ccsd_t_gradient.py` in the session; benzene,
corpus geometry, cc-pVDZ, frozen 6, 114 basis functions, hel1-23 niced beside the CC run, cProfile on the gradient stage only):

| threads | SCF | CCSD | (T) energy (C kernel) | (T) gradient: λ + densities + gradient | total |
|---|---|---|---|---|---|
| 4 | 1 s | 18 s | 14 s | **979 s** | 1,012 s |
| 1 | 3 s | 42 s | 49 s | **1,386 s** | 1,479 s |

Inside the gradient stage at 4 threads: `ccsd_t_rdm._gamma1_intermediates` 528 s cumulative of which **295 s own time**, `_gamma2_intermediates` 423 s
of which **292 s own time** — Python-level numpy work in the blocked triple loops over virtual blocks (the permutation sums, the division by the
energy denominators, transposes), single-threaded; `lib.einsum` → `_dgemm` 233 s (BLAS, the part that does scale: 667 s at one thread), `numpy.einsum`
85 s (serial), `reshape` copies 37 s. The own time of the two functions is the same at one thread (267 + 272 s): a serial floor of ≈ 650 s that no
thread count removes, which is why 16 threads on the CPX62 and 24 on the CCX53 gave the same 663–695 s per benzene gradient (24 Sep). The (T) energy
does the same t₃ work in the C kernel in 14 s; the (T) densities do it in Python in ≈ 950 s.

**PR candidate, sharpened:** a C kernel for the (T) density intermediates of `ccsd_t_rdm.py` (`_gamma1_intermediates`, `_gamma2_intermediates`), in the
manner of the (T) energy kernel and `t3_symm_ip` which already exists in `libcc`. Expected: the benzene gradient from ≈ 11 min to 3–4 min at 16 threads
(the BLAS part alone), the anchor throughput ×3 on every machine. Before a PR: a reference implementation that reproduces the present densities to
1e-10 on water and benzene, timing on naphthalene, and pyscf's own tests. This is a day or two of work, not an hour; it goes on the board as its
own task, after the anchors.

## 5. Candidate (29 September 21:1x) — pyscf `grad/ccsd_t.py`, `grad/uccsd_t.py`: `Gradients(mycc).kernel()` silently uses the CCSD lambda

**Observation.** `grad.ccsd_t.Gradients` overrides only `grad_elec`. Its inherited `ccsd_grad.Gradients.kernel` fills missing l1, l2 with
`mycc.solve_lambda(eris=eris)` — the CCSD lambda equations — and passes them to `ccsd_t_rdm`. The returned vector is not the derivative of the
CCSD(T) energy. Water, RHF/cc-pVDZ, frozen 1, pyscf 2.14.0: against the central finite difference of E_CCSD(T) (h = 1e-3 bohr) the bare call is
off by 1.5e-3, 6.4e-4 and 7.6e-4 a.u. on three components; with `ccsd_t_lambda.kernel(mycc, eris, t1, t2)`'s l1, l2 the agreement is ≤ 1.5e-7.
pyscf's own `grad/test/test_ccsd_t.py` avoids the trap by solving the (T) lambda explicitly; the `__main__` block of `grad/ccsd_t.py` does the
same. Nothing warns a user who writes the natural `Gradients(mycc).kernel()` (we did, from 23 to 29 September; every E8 anchor of this project
had to be recomputed).

**Proposed change (small).** In `grad/ccsd_t.py` (and the UHF twin) give `Gradients` a `kernel` — or better a `solve_lambda` hook the base
class calls — that solves `ccsd_t_lambda` when l1/l2 are not supplied, and a test that the bare call equals the explicit one. Alternative if the
maintainers prefer no behaviour change: raise a clear error when l1/l2 are missing. Reproducer: `probes/results_m1/lambda_incident_2026-09-29/`.
Status: to be drafted after the benzene rerun confirms the size of the effect at PAH scale; the user's word before submission, as for every PR.

**§5 draft (30 September, 07:4x; the user agreed the proposal 07:0x).** Local branch `ccsd-t-grad-solve-t-lambda` on pyscf master `e47d127`
(WSL `~/pyscf-master`; no fork yet — creating one is the user's call). Diff: `grad/ccsd_t.py`, `grad/uccsd_t.py` (+36/−2 each: `_solve_t_lambda`,
a `kernel` override, `grad_elec` no longer falls back to `mycc.l1/l2`), one regression test per file (+20, +17; own molecule, because
`test_ccsd_t_grad` leaves the module's `mol` displaced). Local commit `3ed3646`; patch in `pr_patches/pyscf_ccsd_t_grad_solve_t_lambda_2026-09-30.patch`.
**Checked 07:3x** (pyscf master built from source in WSL `~/pyscf-dev`): the new tests fail without the fix (9.0e-4 a.u. RHF, 6.6e-4 UHF, water/6-31G)
and pass with it; 28 tests of `grad/test/test_ccsd*.py`, `test_uccsd_t.py`, `cc/test/test_{ccsd,uccsd}_t.py`, `test_rccsd_t_lambda.py`,
`test_{ccsd,uccsd}_lambda.py` pass; `ruff check --config .ruff.toml` and the NPY check as in their `lint.yml` pass (tests are excluded there).

> **Title:** CCSD(T) gradients: solve the (T) lambda when l1/l2 are not given
>
> `grad.ccsd_t.Gradients(mycc).kernel()` and `grad.uccsd_t.Gradients(mycc).kernel()` without `l1`, `l2` inherit
> `ccsd.Gradients.kernel`, which takes `mycc.l1/l2` or calls `mycc.solve_lambda()` — the CCSD lambda — and passes it to the
> (T) density code. The result is not the derivative of the CCSD(T) energy. Water, RHF/cc-pVDZ, frozen core: 1.5e-3 a.u. off the
> central finite difference of E_CCSD(T); with `ccsd_t_lambda.kernel`'s l1, l2 it agrees to 1.5e-7. The existing tests and the
> `__main__` examples pass the (T) lambda explicitly, so nothing flags the natural call.
>
> This PR makes both classes solve the (T) lambda (`ccsd_t_lambda` / `uccsd_t_lambda`) when `l1` or `l2` is missing, in `kernel`
> and in `grad_elec`. Explicitly passed multipliers are used unchanged. New tests: the bare call equals the explicit one after
> `mycc.solve_lambda()` has stored the CCSD lambda (RHF and UHF), and matches the finite difference (UHF). Without the change the
> new tests fail by 9.0e-4 (RHF) and 6.6e-4 a.u. (UHF) on water/6-31G.
>
> Related, not changed here: `Gradients.as_scanner()` solves the CCSD lambda and passes it explicitly, and returns `cc.e_tot`
> without (T) — on water/6-31G the scanner's energy misses E_(T) (9.96e-4 E_h) and its gradient is 9.0e-4 a.u. off the CCSD(T)
> gradient. A CCSD(T) gradient scanner would need its own `__call__`. Happy to follow up if wanted.

**07:4x:** fork `thebreadishard/pyscf` created by the user (app); branch `ccsd-t-grad-solve-t-lambda` pushed on the user's word ('Push maar'),
same commit `3ed3646` on `e47d127`. No PR opened. Before submission: the user's word on this text and on the attribution line. Scanner
numbers: `pr_patches/pyscf_scanner_check_2026-09-30.py`.

**§4 status (same evening).** The C kernel of the design note exists (`probes/t_density_kernel/ccsd_t_rdm_kernel.c`, `t_density_fast.py`): water
intermediates equal to pyscf's to 4e-18, gradient to 1e-8, symmetry on and off; timings on benzene and naphthalene from the reruns of 29 Sep.

**30 September 07:2x — no UHF PR.** Gate 1 found pyscf 2.14.0's UCCSD(T) gradient 4.9e-3 a.u. off dE/dx; the cause (missing ½ on the mixed-spin
`dvvVV` block in `uccsd_t_rdm`'s `compress_vvvv` branch) is already fixed upstream (pyscf#3305, PR #3387, commit `aa2ad208`, after v2.14.0). We
carry a version-independent wrapper until a release has it (Software_Changes_Ledger row 20). §5's lambda trap applies to `grad/uccsd_t.py` as well;
its PR covers both classes, drafted as agreed with the user (30 Sep 07:0x): the CCSD(T) gradient classes solve the (T) lambda themselves when
l1/l2 are missing.

## 6. Submitted (30 September 07:5x) — psi-rking/optking#116, fixes #115: silent infinite loop on linear-bend cycles

Issue #115 (posted 07:3x) and PR #116 (branch `thebreadishard/optking:linear-bend-cycle-guard`, 5829c0b on master 855aa8d). Two changes: a near-0°
interior angle in `v3d.linear_torsion_check` resets (`back_transformation=True`) instead of adding terminal-vertex linear bends; the two LINEAR-bend
walks in `addIntcos.add_tors_from_connectivity` keep a visited set and raise on a cycle. Regression tests: near-0°, near-180°, and a four-atom LINEAR-bend
cycle that loops forever on the unpatched tree (60 s timeout) and raises on the branch. Our five installations carry the same fix
(`probes/optking_patches/apply_optking_fix.py`). Status: awaiting review; replies only after consulting the user. Session B opened pyscf#3469 for the
(T)-lambda default of `grad.ccsd_t.Gradients` (§5) the same morning.

**30 September 09:3x — §4 submitted as pyscf/pyscf#3470; §5 as pyscf/pyscf#3469 (07:5x).** Both on the user's standing authorisation of 07:4x
(open a PR when no upstream fix exists and the tests and explanation are right). #3470: `lib/cc/ccsd_t_rdm.c` (the project kernels, generated
from `probes/t_density_kernel/ccsd_t_rdm_kernel.c` by `make_pyscf_c.py` with pyscf names and gamma1/gamma2 flags), `cc/ccsd_t_rdm.py` and
`cc/ccsd_t_lambda.py` call it (+433/−337). Upstream check: master identical to 2.14 in those files, no open PR. Benzene/cc-pVDZ, 16 threads,
same build: `make_intermediates` 397.1 → 23.9 s, lambda solve 491.6 → 98.3 s, gradient with given lambda 1003.7 → 69.9 s; gradients equal to
9.3e-14; 20 upstream tests pass (including element-wise comparisons with the `*_slow` implementations). Body and scripts:
`probes/t_density_kernel/evidence/pr3470_bench/`; #3469's body: `pr_patches/pyscf_3469_body.md`. Remaining drafts: §1 #212 (review answered), §2 pyVPT2.

**30 September 09:4x — correction to §2:** the pyVPT2 change is not local only: issue philipmnel/pyvpt2#57 (21 Sep 06:55 UTC) and PR
philipmnel/pyvpt2#58 (07:29 UTC, branch `quartic-route-consistency` on the fork, +122/−6) are open, no comments, no checks, upstream `main`
unchanged since 16 May. The QC items of §2 (pyVPT2's own suite with psi4, the real-data benzene check) would go into a follow-up comment —
a conversation, so only on the user's word.

**30 September 11:1x — first CI results, both fixed on our side (no approval needed: our own PR code).** #3469: flake8 F811 — the `__main__`
blocks re-imported the lambda module that the change now imports at module level; the two lines dropped (`e239879`, flake8/ruff clean, 7 tests).
#3470: `test_rccsd_t_lambda.py` `allclose(d2, d2_ref, rtol=1e-12, atol=1e-15)` failed on linux-build (passed locally at 1–16 threads): random
integrals, d2 up to ~5e2, the reordered C summation leaves ~1e-14 on elements that cancel to near zero (locally 7e-15 at |ref| 4e-2, margin
0.18 of the tolerance, `evidence/pr3470_bench/margin_3470.py`); atol → 1e-12 on the three d2 comparisons (`ed66845`), fingerprints unchanged;
PR text updated to say so. I also had not run flake8 on #3470 before opening it — clean now; add `flake8 --config .flake8` to the pre-PR list.

**30 September 13:1x — §2 QC done on the laptop** (`probes/results_vpt2/pyvpt2_pr58_qc_2026-09-30/README.md`): suite branch 27 passed / main 24
passed (10 skipped each; the difference = the 3 new tests); real data 61/61 cache hits, report 22.40 / 107.04 / 1264.46 cm⁻¹ = the independent
implementation; numerics unchanged to 2e-10 cm⁻¹. The follow-up comment is drafted below; posting waits for the user's word.

> Follow-up QC on this branch (psi4 1.10.2, qcelemental 0.30.1, qcengine 0.34.2, Python 3.13):
>
> - pyVPT2's test suite: 27 passed, 10 skipped on this branch; 24 passed, 10 skipped on `main` (2eae571). The difference is the three new tests in `test_quartic_routes.py`.
> - Real case through the normal `vpt2_from_schema` path: benzene, B3LYP/6-31G*, 61 psi4 Hessians (psi4 DFT Hessians are finite differences of gradients) at `DISP_SIZE` 0.05. The new report prints median 22.40, 90th percentile 107.04 and max 1264.46 cm⁻¹ disagreement between the two routes to φ_iijj, which matches an independent implementation of the same comparison (22.4 / 107.0 / 1264.5). `check_quartic` right after it still prints "No inconsistencies found".
> - Numerics unchanged: against pyVPT2 0.1.2 on the same Hessians, ω and φ_ijk are bitwise equal and φ_iijj, χ and ν agree to 3e-10 cm⁻¹ (the two routes are now averaged explicitly rather than summed in one expression).
>
> The gradient route (`assemble_quartic_from_gradients`) has the analogous two routes; happy to add the same report there in a follow-up if that is useful.
