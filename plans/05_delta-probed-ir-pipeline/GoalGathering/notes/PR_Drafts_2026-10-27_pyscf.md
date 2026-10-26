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

- Branch: `grad-shell-prange-empty-block` (commit e9d529854) · worktree `~/pyscf-wt-shellprange`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:grad-shell-prange-empty-block
- Software ledger row 36. Files: `pyscf/grad/mp2.py` (+2/−1), `pyscf/grad/test/test_mp2.py` (+24).
- Body: the commit message (what failed: the first block was empty when an atom's first shell was wider than blksize, and the
  gradient's `reshape(nf, nao, -1)` raised; seen in benzene/cc-pVTZ's MP2 gradient after B3LYP work in the same process; the fix; that
  `_shell_prange` serves the MP2, UMP2, CCSD, UCCSD, CASCI and CASSCF gradients).
- Checks run: both new tests fail before the fix (ValueError at grad/mp2.py:90; an empty block) and pass after; the gradient tests of every
  caller pass (test_mp2, test_ump2, test_ccsd, test_ccsd_t, test_uccsd_t, test_casscf, test_casci: 57 passed); pyscf's lint rules
  (ruff with .flake8's selection and 120 columns) clean.

## B — `ccsd_t_rdm._gamma2_outcore`: keep dvvvv in h5fobj

- Branch: `ccsd-t-gamma2-outcore` (commit 4fa261027) · worktree `~/pyscf-wt-ccsdtout`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:ccsd-t-gamma2-outcore
- Software ledger row 35. Files: `pyscf/cc/ccsd_t_rdm.py` (+25/−5), `pyscf/cc/test/test_rccsd_t_lambda.py` (+21).
- Body: the commit message (the CCSD(T) gradient's `_gamma2_outcore` called the in-core function, three nvir⁴ arrays, 28 GB each for
  benzene/cc-pVTZ, the OOM of 3 Oct on a 20 GB machine; now `ccsd_rdm._gamma2_outcore` plus the (T) terms added in h5fobj).
- Checks run: the new test fails before the fix and passes after; test_rccsd_t_lambda, test_ccsd_t (cc and grad), test_ccsd (grad): 20
  passed; the CCSD(T) gradient of water/aug-cc-pVTZ unchanged against master (6e-13), peak RSS 1.55 → 1.42 GB; lint clean.

## A — UCCSD and UCCSD(T) gamma2: keep the vvvv blocks in h5fobj

- Branch: `uccsd-gamma2-outcore` (commit a3b55f271) · worktree `~/pyscf-wt-uccsdout`
- Compare: https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:uccsd-gamma2-outcore
- Software ledger row 52 (step 3). Files: `pyscf/cc/uccsd_rdm.py`, `pyscf/cc/uccsd_t_rdm.py`, three test files.
- Body: the commit message (closes the TODO "hold d2 intermediates in h5fobj" for the vvvv blocks; the t1 contractions through l2·t1;
  `_add_t3_gamma2` shared by the in-core and out-of-core UCCSD(T) paths).
- Checks run: the out-of-core d2 test fails before and passes after; UCCSD gradient against FD (6 places); 57 tests of test_uccsd,
  test_uccsd_t, test_uccsd_lambda, test_dfuccsd and the CC gradient tests pass; the UCCSD(T) gradient of H₂O⁺/aug-cc-pVTZ unchanged against
  master (5e-13), peak RSS 4.09 → 3.38 GB; lint clean.

## D — UHF-CCSD(T) lambda and densities over blocks of the virtual indices when the whole arrays do not fit (stacked on A)

- Branch: `uccsd-t-blocked-intermediates` (commits b787f7554 and ce91273f5, on top of A) · worktree `~/pyscf-wt-uccsdtblk`
- Compare (shows A + D until A is merged): https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:uccsd-t-blocked-intermediates
- Software ledger row 52 (steps 1–2, 4). Files: new `pyscf/cc/uccsd_t_blocked.py` (≈ 480 lines), `uccsd_t_lambda.py`, `uccsd_t_rdm.py`,
  two test files.
- Two commits: the module (b787f7554) and the permutation-symmetry speed-up (ce91273f5, 21:1x; amending the first and force-pushing was
  refused by the session's permission check, so it is a commit on top). The second commit's message corrects the first's last sentence,
  which stated the benzene⁺ bench's 6.1 GB peak for the whole gradient while only the (T) lambda had finished. pyscf squash-merges
  (master's titles end in "(#nnnn)"), so the PR's title and body below become the commit; the last sentence is brought up to date when
  the bench has ended (TASKS 98).
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
virtual-virtual terms, which pair two blocks along one index). Its tables hold
the einsum strings, operands and factors of the existing code; r6 and the
j<->k swap of r4 stay inside a block, p6 and the (j,b)<->(k,c) swap of r4 are
evaluated at the permuted blocks. Where rw and wvd are symmetric under those
permutations (the lambda and gamma2 terms, gamma1's same-spin cases) they are
formed once per unordered block triple and the other orderings are read as
transposes: the (T) lambda of H2O+/aug-cc-pVDZ at block size 8 takes 1.2 s
instead of 2.3 s, at the same peak memory. block_size picks the path from
max_memory: the whole-array code runs unchanged when it fits (gamma1's moves
unchanged into _t3_gamma1), the blocked code otherwise, with the largest
block that fits.

Builds on "UCCSD and UCCSD(T) gamma2: keep the vvvv blocks in h5fobj"
(_add_t3_gamma2).

Tests: the blocked lambda, gamma1 and gamma2 terms equal the whole-array ones
to 1e-12 on triplet water/6-31G at block sizes 1, 3 and 100, and through the
public functions at max_memory = 1; the UCCSD(T) gradient at max_memory = 1
equals the default to 1e-9. The same blocked code, outside pyscf, ran the
UCCSD(T) lambda of benzene+/cc-pVDZ at a peak RSS of 6.1 GB, the UCCSD
integrals included.
```
- Checks run: the blocked lambda/gamma1/gamma2 equal the whole-array code to 1e-12 at block sizes 1, 3, 100 and through the public functions
  at max_memory = 1; the UCCSD(T) gradient at max_memory = 1 equals the default to 1e-9; 43 tests of the UCCSD/UCCSD(T)/gradient files pass;
  a factor changed in the GAMMA1 table makes the new test fail; lint clean (pyscf's rules; also our project's stricter set). After the speed-up (21:1x): 47 tests of test_uccsd, test_uccsd_lambda, test_uccsd_t (cc and grad), test_ccsd and test_ccsd_t (grad) pass; keeping only the first ordering of each orbit makes the new test fail; lint clean.
- For the reviewer, said in the user's words: pyscf uses no dataclasses so far; the module's frozen dataclasses (Inputs, Case) can become
  plain classes if preferred. The blocked path is Python; a C kernel on the same blocks (as the RHF one of #3470) is the follow-up for speed.

## Not prepared as a PR

- The C kernel for the open-shell (T) intermediates: not finished to PR quality tonight (see TASKS 98).
- NO's UCCSD(T) gradient (TASKS 132): already fixed on master by #3333 (lindep passed to lib.krylov); nothing to submit — a comment on our
  issue #2702 that #3333 resolves the early stop for CPHF may be worth posting, in the user's words.
