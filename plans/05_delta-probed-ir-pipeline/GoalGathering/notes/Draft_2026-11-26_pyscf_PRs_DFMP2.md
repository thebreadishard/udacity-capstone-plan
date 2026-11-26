# Drafts for pyscf: the DF-MP2 scanner fix and the DF-MP2 gradient (TASKS 321, 322)

Written 26 Nov 2026, 09:15; rewritten 10:25 with the measured numbers and the third review. **Nothing here is posted.** The user
posts, in his own words, when he can explain the code (pyscf's `AI_POLICY.md`); these texts are drafts for him to rewrite, not
messages from him. Design and rules: `Design_2026-11-26_pyscf_DFMP2_Gradient.md`. Reading guide for the author:
`Walkthrough_2026-11-26_pyscf_DFMP2_Gradient.md`.

## Where the code is (WSL, local commits only, nothing pushed)

| branch | worktree | commit | what |
|---|---|---|---|
| `dfmp2-scanner-mo-energy` | `~/pyscf-wt-dfmp2scan` | `d308067a9` on upstream master `e0ab8634c` | the scanner fix: 3 lines in `pyscf/mp/mp2.py`, 1 test |
| `df-mp2-grad-v2` | `~/pyscf-wt-dfmp2grad2` | `ffaec2595` on top of the scanner fix | the gradient: 8 files, +661 −3; module 427 lines, 12 tests in 4.5 s |
| `df-mp2-grad` | `~/pyscf-wt-dfmp2grad` | `c2f6d8bfc` | the first draft, before the reviews; kept as the record of the first comparison run; to be removed after posting |

Upstream master was still `e0ab8634c` at 10:20 on 26 Nov, so both branches are current. Order: the scanner fix first — the
gradient's scanner is only right at a new geometry with it, and the gradient branch has a test that says so.

## Reviews (26 Nov, three fresh agents; their findings are answered in the branches, the answers were not re-reviewed)

- **Correctness of the module** (its own finite-difference runs on water and HF): formulas and block logic correct in every case
  it could run, about 1.5e-7 Eh/bohr — frozen lists with a virtual orbital and non-contiguous occupied ones, Cartesian functions,
  a prebuilt `_cderi`, `only_dfj`, a point-charge QM/MM reference, `atmlst`. Answered: the scanner dependency (stacked branches,
  a scanner test at a second geometry); a guard for a non-converged reference (the gradient was silently off by 4.0e-3 there);
  tests on a bent, asymmetric water; the scanner test with tight SCF.
- **Style** (which lines would a maintainer recognise as not theirs): module and test file 'would pass for house code'; 16
  findings answered — the reference in house form with its DOI, one commit per branch with upstream-style subjects, `getattr`
  instead of a `__dict__` probe, the companion edits 3426 itself made, the example without unused assignments.
- **The block-wise vhf1 term** (added after the first comparison run; reviewed on its own): maths derived independently and
  found right; the block-wise route and the `get_jk` route agree to 2e-15 on the same input; no must-fix. Answered: a test for
  an `only_dfj` reference, a test pinning the two routes against each other, one-line docstring summaries.
- Not verified by any reviewer: linearly dependent fitting sets, out-of-core energies, ECPs, X2C, solvent models, `to_gpu`.

## Measured (the numbers for the texts)

Finite differences, water (distorted, no symmetry), cc-pVDZ, central differences with h = 1e-3 Bohr against PySCF's own DF-MP2
energy, on the final branch:

| reference | fitting of the correlation part | frozen | max abs(analytic − FD), Eh/Bohr |
|---|---|---|---|
| `density_fit()` cc-pVDZ-JKFIT | the reference's | — | 1.7e-07 |
| `density_fit()` cc-pVDZ-JKFIT | cc-pVDZ-RI | — | 1.7e-07 |
| `density_fit()` cc-pVDZ-JKFIT | cc-pVDZ-RI | 1 | 1.7e-07 |
| conventional ERIs | cc-pVDZ-RI | — | 1.7e-07 |
| conventional ERIs | default | 1 | 1.4e-07 |

`auxbasis_response = False` changes the gradient by 6.0e-04: the switch acts.

Against Psi4 1.10.2 (DF-MP2 gradient, frozen core, the same fitting sets: cc-pVXZ-JKFIT for the reference, cc-pVXZ-RI for the
correlation part), on a laptop with 8 threads; PySCF `max_memory` 7000 MB, Psi4 memory 8 GB:

| molecule, basis | basis functions | max abs difference, Eh/Bohr | energy difference, Eh | PySCF time, peak memory | Psi4 time |
|---|---|---|---|---|---|
| benzene, cc-pVTZ | 264 | 6.2e-08 | 1.1e-09 | 22 s, 2.4 GB (first draft, `max_memory` 8000) | 9 s |
| benzene, ano-pVQZ | 510 | 4.4e-08 | 3.9e-10 | 167 s, 3.5 GB | 764 s |
| naphthalene, ano-pVQZ | 790 | 2.7e-07 (rms 9.2e-08) | 1.5e-09 | 830 s, 7.7 GB | 2108 s |

The requirement of the design note — naphthalene in ano-pVQZ finished under a 12 GB cap and equal to psi4's — is met: 7.7 GB,
and 2.7e-07 Eh/bohr at worst against a largest element of 3.8e-03 (in a Hessian row with our 0.005 bohr step that is 2.7e-05
E_h/bohr², the size of the rows' own symmetry spread). Before the block-wise vhf1 term the first draft peaked at 10.5 GB on
benzene in ano-pVQZ. Records: `probes/results_m1/pyscf_dfmp2_grad_2026-11-26/` (first launch, stopped by hand) and
`…_v2/` (second launch, commit `a2474c90d`: the final branch differs from it by docstrings and two tests only).

## Draft 1 — issue and pull request: the DF-MP2 scanner

**Title:** Fix stale mo_energy of DF-MP2 in MP2_Scanner

**The bug.** `dfmp2.DFRMP2` (and the unrestricted and generalised DF classes) store `mo_energy` when they are created.
`mp2.MP2_Scanner.__call__` updates `mo_coeff` and `mo_occ` after the SCF at the new geometry, but not `mo_energy`. So
`DFMP2(mf).as_scanner()` uses the orbital energies of the first geometry everywhere else. No warning, no error.

**Reproduce.** Water, 6-31G, `scf.RHF(mol).density_fit()`; scanner created at one geometry
(`O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587`) and called at a second (`O 0 0 0; H 0 -0.8 0.55; H 0 0.7 0.6`): the scanner's
energy differs from a fresh calculation by −6.3e-4 Eh. DF-UMP2: 5.2e-4. After the fix: 6e-9 (the SCF tolerance).

**The fix.** Three lines in `MP2_Scanner.__call__`: refresh `mo_energy` from the SCF scanner when the object keeps one. The
conventional RMP2, UMP2 and GMP2 scanners keep none and are unchanged; ROMP2 keeps one and its result is unchanged.

**Behaviour change to mention.** A `mo_energy` passed by the user to `DFMP2(mf, mo_energy=…)` is now replaced by the scanner,
as `mo_coeff` already is.

**Tests.** One new test in `pyscf/mp/test/test_dfmp2.py` (scanner at a second geometry against a fresh calculation, 7 places);
`test_dfmp2.py`, `test_mp2.py`, `test_dfump2.py` pass (37).

**Notes (AI disclosure, required by pyscf's policy).** The bug was found and the fix drafted with an AI coding assistant
(Claude Code); I reviewed and tested the change and can explain it. — *wording to be the user's own.*

## Draft 2 — pull request: analytic nuclear gradients for DF-MP2

**Title:** Analytic nuclear gradients for DF-MP2

**What was missing.** `dfmp2.DFRMP2.nuc_grad_method` raises `NotImplementedError`, so `mf.density_fit().MP2()` has no
gradient. #3426 lists the MP2 case under 'Not addressed'.

**What this adds.** `pyscf/df/grad/mp2.py` mirrors `pyscf/grad/mp2.py`, following `pyscf/df/grad/ccsd.py`. Two substitutions:

1. The `int2e`/`int2e_ip1` loop is replaced by a DF contraction. The 2-PDM is kept in its three-index form:
   `dfdm2[P,ia] = sum_jb (4 t2[i,j,a,b] - 2 t2[i,j,b,a]) (P|Q)^-1 (Q|jb)`. It is transformed to the AO basis one block of
   auxiliary shells at a time and contracted with `int3c2e_ip1`, `int3c2e_ip2` and `int2c2e_ip1`. It returns the gradient term
   and the `Imat` intermediate, as the conventional loop does.
2. The `vhf1` term. For a conventional or `only_dfj` reference it goes through `mf_grad.get_jk`, as in #3426. For a
   density-fitted reference it is contracted in this module with `(naux,nocc,nao)` arrays (`_contract_dfvhf1`).

**Why not `df.grad.ccsd._contract_dfdm2`, and why not `get_jk` for a DF reference.** Memory. `_contract_dfdm2` holds three
`(naux, nao_pair)` arrays and takes a four-index AO 2-PDM from a file. `df.grad.rhf.get_jk` with `(hf_dm1, dm1p)` keeps
`(naux, rank_i, rank_j)` arrays for every pair of density matrices, and `dm1p` has full rank, so `(naux,nao,nao)`; only the terms
mixing the two matrices are needed. Measured on benzene / ano-pVQZ (510 basis functions): peak 10.5 GB through `get_jk`,
3.5 GB with the contraction here. The two routes agree to 2e-15 on the same input (a test pins this).

**Differences from #3426, for discussion.**
- A conventional SCF reference is accepted (exact ERIs in the reference, fitted ERIs in the correlation energy — what
  `DFMP2(mf)` computes today). #3426 refuses one for CCSD. Both cases are tested against finite differences.
- A fitting basis on `mp.with_df` different from the reference's is supported; the gradient then has two auxiliary responses.
- `df.grad.mp2` imports `_auxmol` and `_pair_weights` from `df.grad.ccsd`, which imports `pyscf.cc`. They could move to
  `df/grad/rhf.py` if preferred.

**Companion edits, as #3426 made them.** `pyscf/grad/mp2.py` warns when the reference is density fitted; `dfump2` and `dfgmp2`
raise `NotImplementedError` with a message.

**Benchmark.** The two tables under 'Measured' above.

**Tests.** New `pyscf/df/test/test_df_mp2_grad.py`, 12 tests in 4.5 s on a water molecule without symmetry: finite-difference
checks for a density-fitted reference, a frozen core plus a frozen virtual orbital, a separate RI basis, a conventional
reference, an `only_dfj` reference and the smallest block size; the block-wise `vhf1` term against `get_jk`; the scanner at a
second geometry; `auxbasis_response = False` changes the result; a non-converged reference is refused; dispatch; the DF-UMP2
guard. Checked by hand and not in the test file: `mol.symmetry`, Cartesian functions.
`test_df_ccsd_grad.py`, `test_dfmp2.py`, `test_dfump2.py` and `grad/test/test_mp2.py` still pass (49 with the new file).

**Depends on** the scanner fix (draft 1): without it the gradient scanner is wrong at a new geometry.

**Not addressed.**
- DF-UMP2 gradients.
- Amplitudes are needed in memory (`with_t2`); rebuilding them block by block from `ovL` would lift that.
- With a nearly singular fitting metric the energy (`dfmp2`'s own decomposition) and the gradient (`_gen_metric_solver`) may
  drop different vectors, as in #3426.
- Unrelated and pre-existing: `df.grad.rhf.get_jk` fails with `AttributeError: … no attribute 'aux'` for an `only_dfj`
  reference with `auxbasis_response = False`; the plain DF-RHF gradient fails the same way (TASKS 323).

**Notes (AI disclosure).** Developed with an AI coding assistant (Claude Code): code, tests and this description were drafted
with it; I reviewed the derivation and the code, ran the checks above and can explain them. — *wording to be the user's own.*

## To post (the user's steps; nothing happens before his word)

1. Read with the guide; rewrite the two texts in his own words.
2. Say 'push': the two branches go to his fork (`thebreadishard/pyscf`), which is public. Before that push: `git fetch` upstream
   and rebase both branches if master moved; `ruff check --config .ruff.toml pyscf` and the test files once more.
3. He opens the scanner pull request on GitHub from `dfmp2-scanner-mo-energy` (an issue first, or the pull request alone with the
   bug described in it — #3426 answered an issue).
4. He opens the gradient pull request from `df-mp2-grad-v2`. It contains the scanner commit until that one is merged; say so in
   the first line, or wait for the merge and rebase.
5. He answers reviewers himself; I can explain a reviewer's point to him and draft code changes, not his replies.

## Still open on our side (not blocking a post)

- The composite step in cm⁻¹ through the new gradient (design note, validation 4).
- Our comparison scripts `probes/upstream_dfmp2_grad/` are untracked until they have had their own review.
