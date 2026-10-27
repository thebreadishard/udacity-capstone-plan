# pyscf pull requests prepared on the night of 26–27 October 2026 — for the user to review and submit

*Prepared on the user's word (26 Oct, evening: "zet meerdere PR's klaar vannacht. Ik dien ze dan morgen in"). Nothing is opened: each branch is
pushed to the fork thebreadishard/pyscf only. pyscf's AI policy (AI_POLICY.md): the contributor reviews, understands and submits the code;
AI use is disclosed in the PR; discussion with maintainers is in the contributor's own words. Every branch starts from upstream master
44313dfb4 (26 Oct 2026), built in WSL (~/pyscf-wt-base), libraries linked into each worktree.*

**Order of submission:** C, B, A, then D (D is stacked on A). C and B are independent of everything else.

**Disclosure line for every PR body (suggested):** "AI disclosure: this change was developed with Claude Code (Anthropic's Claude Opus 5.5)
as an assistant — it read the code, wrote the change and the tests, and ran them; I reviewed the diff, the tests and the measurements
before submitting."

---

## C — `grad.mp2._shell_prange`: no empty block when a shell is wider than blksize

- Branch: `grad-shell-prange-empty-block` (commits e9d529854, 98f69edf9 the convention pass) · worktree `~/pyscf-wt-shellprange`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:grad-shell-prange-empty-block
- Software ledger row 36. Files: `pyscf/grad/mp2.py` (+2/−1), `pyscf/grad/test/test_mp2.py` (+22).
- Title: grad.mp2._shell_prange: no empty block when a shell is wider than blksize
- Body (then the disclosure line):

```
_shell_prange closed the current block as soon as adding a shell exceeded
blksize, including when the block was still empty. With the first shell of an
atom wider than blksize (a generally contracted shell, e.g. the s shells of
cc-pVDZ/cc-pVTZ, or little free memory so that blksize is small) the first
block had nf = 0, and the gradient's reshape(nf, nao, -1) of it raised
ValueError. Seen in the MP2 gradient of benzene/cc-pVTZ after B3LYP work in
the same process (max_memory 6000). A block is now closed only when it holds a
shell, so a wide shell forms a block of its own. _shell_prange is shared by
the MP2, UMP2, CCSD, UCCSD, CASCI and CASSCF gradients.

Tests: _shell_prange over all shells of water/cc-pVTZ at block sizes 1 to 1000,
one subtest each (no empty block, every shell covered once and in order), and
the MP2 gradient of water/cc-pVDZ at max_memory = 1 equal to the default to
1e-9. Both fail before the change.
```
- Checks run: both new tests fail before the fix (ValueError at grad/mp2.py:90; an empty block) and pass after; the gradient tests of every
  caller pass (test_mp2, test_ump2, test_ccsd, test_ccsd_t, test_uccsd_t, test_casscf, test_casci: 57 passed); pyscf's lint rules
  (ruff with .flake8's selection and 120 columns) clean. After the convention pass (27 Oct 04:4x, pyscf's agent-recipes, see the section below): the _shell_prange test takes all shells at once, one subtest per blksize; test_mp2 10 passed; with master's mp2.py both new tests fail.

## B — `ccsd_t_rdm._gamma2_outcore`: keep dvvvv in h5fobj

- Branch: `ccsd-t-gamma2-outcore` (commits 4fa261027, af6fec06f the convention pass) · worktree `~/pyscf-wt-ccsdtout`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:ccsd-t-gamma2-outcore
- Software ledger row 35. Files: `pyscf/cc/ccsd_t_rdm.py` (+25/−5), `pyscf/cc/test/test_rccsd_t_lambda.py` (+21).
- Title: ccsd_t_rdm._gamma2_outcore: keep dvvvv in h5fobj
- Body (then the disclosure line):

```
The CCSD(T) gradient calls ccsd_t_rdm._gamma2_outcore with an HDF5 file and
compress_vvvv=True, but the function only called _gamma2_intermediates, which
reads the whole nvir**4 dvvvv into memory (ccsd_rdm._gamma2_intermediates) and
forms two more nvir**4 arrays while compressing it. For benzene/cc-pVTZ
(nvir = 243) that is three arrays of 28 GB each; the gradient ran out of memory
on a 20 GB machine right after the (T) lambda converged.

_gamma2_outcore now takes the CCSD part from ccsd_rdm._gamma2_outcore, which
the CCSD gradient already uses and which writes dvvvv blockwise into h5fobj,
and adds the (T) terms to dovov, dooov and dovvv there. dvvov is None, as in
ccsd_rdm._gamma2_outcore. The check against complex inputs is shared with
_gamma2_intermediates.

Test: at max_memory = 1, every block of _gamma2_outcore equals
_gamma2_intermediates to 1e-12 for water/6-31G, compressed and not (subtests
naming the block); it fails before the change. The CCSD(T) gradient of
water/aug-cc-pVTZ is unchanged (max difference 6e-13); its peak RSS goes from
1.55 to 1.42 GB there (nvir = 87, a 0.46 GB dvvvv); the saving grows as
nvir**4.
```
- Checks run: the new test fails before the fix and passes after; test_rccsd_t_lambda, test_ccsd_t (cc and grad), test_ccsd (grad): 20
  passed; the CCSD(T) gradient of water/aug-cc-pVTZ unchanged against master (6e-13), peak RSS 1.55 → 1.42 GB; lint clean. After the convention pass (27 Oct 04:4x, pyscf's agent-recipes, see the section below): max_memory = 1 only, compressed and not as subtests; 20 passed; with master's ccsd_t_rdm.py the test fails.

## A — UCCSD and UCCSD(T) gamma2: keep the vvvv blocks in h5fobj

- Branch: `uccsd-gamma2-outcore` (commits a3b55f271, fee4e5fd3 after the review, 9969606cc the convention pass) · worktree `~/pyscf-wt-uccsdout`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:uccsd-gamma2-outcore
- Software ledger row 52 (step 3). Files: `pyscf/cc/uccsd_rdm.py`, `pyscf/cc/uccsd_t_rdm.py`, three test files.
- Title: UCCSD and UCCSD(T) gamma2: keep the vvvv blocks in h5fobj
- Body (then the disclosure line):

```
uccsd_rdm._gamma2_outcore took h5fobj but held every block in memory ("TODO:
hold d2 intermediates in h5fobj"): gvvvv, gvVvV and gVVVV were whole nvir**4
arrays, then transposed, symmetrized and compressed, several nvir**4 copies at
once. uccsd_t_rdm._gamma2_outcore, which the UCCSD(T) gradient calls with an
HDF5 file, only called the in-core _gamma2_intermediates.

With h5fobj, _gamma2_outcore now forms dvvvv, dvvVV and dVVVV per block of
their first virtual index and writes them to it, compressed or not, as the RHF
ccsd_rdm._gamma2_outcore does for dvvvv. A block needs two contractions per
slab of p, one for D1[p,q] and one for D1[q,p], where D1 is the antisymmetrized
(or, for the mixed block, doubled) g block of the in-core code, so no nvir**4
array is formed. A spin without virtual orbitals (all frozen, or nalpha = nmo)
gives empty datasets. The four contractions of the vvvv intermediates with t1
(into govvv, goVvV, gOvVv, gOVVV) go through l2*t1 instead (o**3*v), in both
paths. Without h5fobj the in-core blocks are formed as before
(_gamma2_vvvv_incore). In uccsd_t_rdm, the (T) terms move into
_add_t3_gamma2, which updates d2 and returns it; _gamma2_intermediates and
_gamma2_outcore both call it, the latter on uccsd_rdm._gamma2_outcore.

Tests: at max_memory = 1 (the vvvv blocks in many slabs), every block of
uccsd_rdm._gamma2_outcore (triplet water/6-31G) and of
uccsd_t_rdm._gamma2_outcore (triplet water/3-21G) equals _gamma2_intermediates
to 1e-12, compressed and not (subtests naming the block); the same with every
alpha virtual frozen; the UCCSD gradient against central differences of the
energy (5 places: at a 1e-3 A step the central difference itself is about
2e-7 off). The UCCSD(T) gradient of H2O+/aug-cc-pVTZ is unchanged (max
difference 5e-13); its peak RSS goes from 4.09 to 3.38 GB (the gradient now
adds 0.01 GB above the UCCSD step, 0.72 GB before; nvir = 87 and 88). The
saving grows as nvir**4.
```
- Checks run: the out-of-core d2 test fails before and passes after; UCCSD gradient against FD (6 places); 57 tests of test_uccsd,
  test_uccsd_t, test_uccsd_lambda, test_dfuccsd and the CC gradient tests pass; the UCCSD(T) gradient of H₂O⁺/aug-cc-pVTZ unchanged against
  master (5e-13), peak RSS 4.09 → 3.38 GB; lint clean. After the review (22:1x): a spin block without virtual orbitals no longer divides
  by zero in `_vvvv_to_h5` (new test, fails with ZeroDivisionError before); the FD test converges the amplitudes (conv_tol_normt 1e-8) and
  compares at 5 places — the central difference is itself 1.8–2.6e-7 off, and at 6 places it failed in one of three runs; 54 caller tests
  pass, four runs in a row. After the convention pass (27 Oct 04:4x, pyscf's agent-recipes, see the section below): `_add_t3_gamma2` returns d2 and its callers use it; the gamma2 tests run at max_memory = 1 with subtests naming the block, the UCCSD(T) one on the module's UHF; 54 passed, 136 subtests; with the guard removed the zero-virtual test fails.

## D — UHF-CCSD(T) lambda and densities over blocks of the virtual indices when the whole arrays do not fit (stacked on A)

- Branch: `uccsd-t-blocked-intermediates` · worktree `~/pyscf-wt-uccsdtblk`. Commits: b787f7554 the module, ce91273f5 the permutation
  symmetry, d62955356 a merge of A's second commit, 698959fcd Python 3.9 and the measured memory rule (22:1x), 66f667e86 the module in the neighbouring modules' style, 84eb378a8 a merge of A's third commit, 3a1452c68 array operands, BLKMIN, d2 returned, the tests split. Amending and force-pushing was
  refused by the session's permission check, so the fixes are commits on top; pyscf squash-merges (master's titles end in "(#nnnn)"), so
  the title and body below become the commit. Their benzene⁺ sentence is true for the whole gradient (the bench ended at 21:51).
- Compare (shows A + D until A is merged): https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:uccsd-t-blocked-intermediates
- Software ledger row 52 (steps 1–2, 4). Files: new `pyscf/cc/uccsd_t_blocked.py` (549 lines), `uccsd_t_lambda.py`, `uccsd_t_rdm.py`,
  two test files.
- Title: UHF-CCSD(T) lambda and densities over blocks of the virtual indices when the whole arrays do not fit
- Body (then the disclosure line):

```
uccsd_t_lambda.make_intermediates, uccsd_t_rdm._gamma1_intermediates and the
(T) terms of the UCCSD(T) gamma2 form w, v, d3, rw and wvd as whole ijkabc
arrays for the four spin cases, several o**3 v**3 arrays at once: about 22 GB
each for benzene+/cc-pVDZ (114 functions), 830 GB for acenaphthylene+ (208).
Any UCCSD(T) gradient beyond the smallest molecules ran out of memory there.

The new module uccsd_t_blocked computes the same terms over blocks of the
three virtual indices (o**3 B**3 numbers per step; o**3 v B**2 for gamma1's
virtual-virtual terms, which pair two blocks along one index). w and v are
written out with the einsum strings of the existing code; the contractions of
rw and wvd are listed per spin case, one line of the existing code per entry.
r6 and the j<->k swap of r4 stay inside a block; p6 and the (j,b)<->(k,c) swap
of r4 are evaluated at the permuted blocks. Where rw and wvd are symmetric
under those permutations (the lambda and gamma2 terms, gamma1's same-spin
cases) they are formed once per unordered block triple and the other
orderings are read as transposes.

block_size picks the path from max_memory: the whole-array code runs
unchanged when it fits (gamma1's moves unchanged into _t3_gamma1), the blocked
code otherwise, with the largest block whose step fits after the four unpacked
o*v**3 integral blocks, but at least ccsd.BLKMIN. A step counts 16 arrays of
o**3 B**3 and 10 of o**3 v B**2: the tracemalloc peaks of this code on
H2O+/aug-cc-pVDZ at five block sizes give at most 14 and 8.3. The whole-array
code is kept as it is: it is the faster path for gamma1 when it fits, and the
blocked terms are tested against it. For the lambda and gamma2 the blocked
path at block size 16 is faster than the whole arrays in the table below
(the permutation symmetry); whether to take it also when the arrays fit I
leave to you. The o*v**3 integrals are still read whole; they are smaller
than one o**3 v**3 array by a factor o**2.

Time and memory, H2O+/cc-pVTZ (occ 5/4, vir 53/54), 4 threads, tracemalloc
peak of each step (maximum difference to the whole-array result 7e-18):

                  lambda           gamma1           gamma2
  whole arrays    7.5 s, 894 MB    6.6 s, 893 MB    7.1 s, 893 MB
  blocks of 8     5.2 s,  35 MB   21.1 s,  36 MB    4.8 s,  32 MB
  blocks of 16    3.0 s, 102 MB   11.0 s, 107 MB    2.8 s, 100 MB
  blocks of 32    5.9 s, 327 MB   13.1 s, 303 MB    5.8 s, 324 MB

The same blocked code, outside pyscf and before the permutation symmetry,
ran the UCCSD(T) gradient of benzene+/cc-pVDZ (frozen core) at a peak RSS of
6.1 GB, the UCCSD integrals included: the (T) lambda in 1591 s, gamma1, gamma2
and the gradient in 5280 s, on 8 threads.

Builds on "UCCSD and UCCSD(T) gamma2: keep the vvvv blocks in h5fobj"
(_add_t3_gamma2).

Tests: the blocked lambda, gamma1 and gamma2 terms equal the whole-array ones
to 1e-12 on triplet water/3-21G at block sizes 1, 3 and 100 (one test each,
subtests naming the block size and the intermediate); with max_memory = 1 the
public functions take the blocked path and give the same results; for complex
amplitudes and integrals the blocked gamma1 and gamma2 terms equal the
whole-array ones; the UCCSD(T) gradient at max_memory = 1 equals the default
to 1e-9. Keeping only the first ordering of each symmetry orbit, dropping a
conjugation or reading rw* as rw makes a test fail.
```
- Checks run: the blocked lambda/gamma1/gamma2 equal the whole-array code to 1e-12 at block sizes 1, 3, 100 and through the public functions
  at max_memory = 1; the UCCSD(T) gradient at max_memory = 1 equals the default to 1e-9; 43 tests of the UCCSD/UCCSD(T)/gradient files pass;
  a factor changed in the GAMMA1 table makes the new test fail; lint clean (pyscf's rules; also our project's stricter set). After the speed-up (21:1x): 47 tests of test_uccsd, test_uccsd_lambda, test_uccsd_t (cc and grad), test_ccsd and test_ccsd_t (grad) pass; keeping only the first ordering of each orbit makes the new test fail; lint clean. After the review: 60 tests (with A's merged in, and test_ccsd_t) pass, the orbit mutation still fails the new test, `tools/py39_check.py` finds nothing, lint clean. After the convention pass (27 Oct 04:4x, pyscf's agent-recipes, see the section below): both rewrites bit-identical to the commit before them on one thread (216 arrays, `probes/pyscf_pr_d_pin.py`); 70 tests and 327 subtests pass; five mutations each make a test fail (orbit, two conjugations, rw* read as rw, None from the blocked branch); lint, ASCII and py39 clean; the benchmark in the body is `probes/pyscf_pr_d_bench.py`, log `probes/results_m1/pyscf_pr_d_bench_h2o_cation_ccpvtz_2026-10-27.log`.
- Open for the reviewers (in the body): whether to take the blocked path for the lambda and gamma2 also when the whole arrays fit. The blocked path is Python; a C kernel on the same blocks (as the RHF one of #3470) is the follow-up for speed (TASKS 136).

## Independent review (22:1x)

A fresh agent read the four diffs against 44313dfb4, ran the tests and tried mutations, without my conclusions. C and B: no defects
(mutations of C's old `_shell_prange` fail both new tests). A: the zero-virtual division — fixed as above. D: Python 3.10 forms where pyscf
supports 3.9 (CI tests 3.9; an `X | None` return annotation raised at import, eight `zip(strict=)`) — fixed, and `tools/py39_check.py`
finds nothing left on any branch; the memory rule undercounted — measured (`probes/uhf_t_blocked_arrays.py`: γ1's paired terms hold 8.3
o³·v·B² arrays where the rule counted 2) and set to 16/10 plus the unpacked integrals. One review point did not hold: numpy's `.conj()`
of a real array does not copy (`shares_memory` is True), so the integral "copies" cost nothing. Possible review comment, not a defect:
D's style (dataclasses, type hints, Unicode in docstrings) is unlike the rest of pyscf.

## Convention pass (27 Oct 04:4x)

The user asked whether the review had looked at pyscf's design patterns and conventions. It had not: the checks were lint, format and
Python 3.9. pyscf publishes its own rules for this, `agent-recipes/skills/pyscf-coding-style.template.md` and
`pyscf-pr-review.template.md` (#3489), which a maintainer applies. A fresh agent compared D with the neighbouring modules and those
rules; what changed, on all four branches:
- tests: one behaviour per test, no nested loops over options; closely related cases as `subTest`s that name the failing case (25 test
  files in pyscf use it); the module's fixtures where they fit; a complex test for D's conjugations (the review template asks for it);
- D's module: no dataclasses, type hints, postponed annotations or non-ASCII (pyscf has none); `import numpy`, single quotes,
  `lib.prange`, `log.timer_debug1`, `lib.direct_sum`, `ccsd.BLKMIN`; the tables hold the arrays themselves; `d2` returned (the style
  template: use the returned object); public docstrings with arguments and returns; no checks for cases that cannot occur; the
  docstring says why the whole-array code stays (the review template asks for that when two implementations exist);
- the benchmark of blocked against whole arrays in D's body (the review template asks for one when performance is a reason).
Not taken: making the whole-array code the one-block case of the blocked code (the style template asks for the smallest complete
change; the body asks the maintainers instead); `mycc` as the first argument of `_t3_gamma1` (it would be unused).
The related-issues search found none open; #3305 (UCCSD(T) gradients against finite differences) is closed and about correctness.
The merge of A's third commit into D left `_add_t3_gamma2`'s blocked branch returning None; it was seen on reading the merge, before
any test ran, and the new max_memory = 1 test fails on it (checked by putting it back).

## Not prepared as a PR

- The C kernel for the open-shell (T) intermediates: not finished to PR quality tonight (see TASKS 98).
- NO's UCCSD(T) gradient (TASKS 132): already fixed on master by #3333 (lindep passed to lib.krylov); nothing to submit — a comment on our
  issue #2702 that #3333 resolves the early stop for CPHF may be worth posting, in the user's words.
