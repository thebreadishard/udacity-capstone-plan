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

- Branch: `uccsd-t-blocked-intermediates` (commit b787f7554, on top of A) · worktree `~/pyscf-wt-uccsdtblk`
- Compare (shows A + D until A is merged): https://github.com/pyscf/pyscf/compare/master...thebreadishard:pyscf:uccsd-t-blocked-intermediates
- Software ledger row 52 (steps 1–2, 4). Files: new `pyscf/cc/uccsd_t_blocked.py` (≈ 480 lines), `uccsd_t_lambda.py`, `uccsd_t_rdm.py`,
  two test files.
- Body: the commit message. **To correct before submitting:** its last sentence states the benzene⁺ bench's peak RSS (6.1 GB) for the whole
  gradient; at the time of the commit only UHF, UCCSD, the (T) energy and the (T) lambda had finished (peak 6.08 GB); the gradient stage was
  still running. The sentence is amended once the bench has ended (TASKS 98).
- Checks run: the blocked lambda/gamma1/gamma2 equal the whole-array code to 1e-12 at block sizes 1, 3, 100 and through the public functions
  at max_memory = 1; the UCCSD(T) gradient at max_memory = 1 equals the default to 1e-9; 43 tests of the UCCSD/UCCSD(T)/gradient files pass;
  a factor changed in the GAMMA1 table makes the new test fail; lint clean (pyscf's rules; also our project's stricter set).
- For the reviewer, said in the user's words: pyscf uses no dataclasses so far; the module's frozen dataclasses (Inputs, Case) can become
  plain classes if preferred. The blocked path is Python; a C kernel on the same blocks (as the RHF one of #3470) is the follow-up for speed.

## Not prepared as a PR

- The C kernel for the open-shell (T) intermediates: not finished to PR quality tonight (see TASKS 98).
- NO's UCCSD(T) gradient (TASKS 132): already fixed on master by #3333 (lindep passed to lib.krylov); nothing to submit — a comment on our
  issue #2702 that #3333 resolves the early stop for CPHF may be worth posting, in the user's words.
