# Drafts for pyscf: the DF-MP2 scanner fix and the DF-MP2 gradient (TASKS 321, 322)

Written 26 Nov 2026, 09:15. **Nothing here is posted.** The user posts, in his own words, when he can explain the code (pyscf's
`AI_POLICY.md`); these texts are drafts for him to rewrite, not messages from him. Design and rules:
`Design_2026-11-26_pyscf_DFMP2_Gradient.md`.

## Where the code is (WSL, local commits only, nothing pushed)

| branch | worktree | commit | what |
|---|---|---|---|
| `dfmp2-scanner-mo-energy` | `~/pyscf-wt-dfmp2scan` | `d308067a9` on upstream master `e0ab8634c` | the scanner fix: 3 lines in `pyscf/mp/mp2.py`, 1 test |
| `df-mp2-grad-v2` | `~/pyscf-wt-dfmp2grad2` | `ea79cce7c` on top of the scanner fix | the gradient: 8 files, +523 −3 |
| `df-mp2-grad` | `~/pyscf-wt-dfmp2grad` | `c2f6d8bfc` | the first draft, before the reviews; the run `dfmp2_grad_vs_psi4` reads it; to be removed after that run |

Order: the scanner fix first. The gradient's scanner is only right at a new geometry with it, and the gradient branch has a test
that says so. A bug report with its fix is also the natural first contact.

## Reviews (26 Nov, two fresh agents; their answers are in the branches, the answers were not re-reviewed)

- **Correctness** (ran its own finite-difference checks on water and HF): formulas and block logic correct in every case it could
  run, about 1.5e-7 Eh/bohr throughout — frozen lists with a virtual orbital and non-contiguous occupied ones, Cartesian
  functions, a prebuilt `_cderi`, `only_dfj`, a point-charge QM/MM reference, `atmlst`. Findings answered: the scanner dependency
  (stacked branches, a scanner test at a second geometry); a guard for a non-converged reference (the gradient was silently off
  by 4.0e-3 there); tests on a bent, asymmetric water instead of a linear molecule; the scanner test with tight SCF. Not
  verified by it: linearly dependent fitting sets, out-of-core energies, ECPs, X2C, solvent, `to_gpu`, large memory.
- **Style** (which lines would a maintainer recognise as not theirs): module and test file 'would pass for house code'; 16
  findings answered — the reference in house form with its DOI, one commit per branch with upstream-style subjects, `getattr`
  instead of a `__dict__` probe, the companion edits 3426 itself made (a warning in `pyscf/grad/mp2.py` for a density-fitted
  reference, worded errors for DF-UMP2 and DF-GMP2), the example without unused assignments and named like its neighbours.
  Left as it is and to be said in the pull request: `mp2.py` imports `_auxmol` and `_pair_weights` from `pyscf.df.grad.ccsd`,
  which imports `pyscf.cc`.

## Draft 1 — issue and pull request: the DF-MP2 scanner

**Title:** Fix stale mo_energy of DF-MP2 in MP2_Scanner

**The bug.** `dfmp2.DFRMP2` (and the unrestricted and generalised DF classes) store `mo_energy` when they are created.
`mp2.MP2_Scanner.__call__` updates `mo_coeff` and `mo_occ` after the SCF at the new geometry, but not `mo_energy`. So
`DFMP2(mf).as_scanner()` uses the orbital energies of the first geometry everywhere else. No warning, no error.

**Reproduce.** Water, 6-31G, `scf.RHF(mol).density_fit()`; scanner created at one geometry and called at a second
(`O 0 0 0; H 0 -0.8 0.55; H 0 0.7 0.6`): the scanner's energy differs from a fresh calculation by −6.3e-4 Eh. DF-UMP2: 5.2e-4.
After the fix: 6e-9 (the SCF tolerance).

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
2. The `vhf1` term goes through `mf_grad.get_jk`, as in #3426.

**Why not `df.grad.ccsd._contract_dfdm2`.** It holds three `(naux, nao_pair)` arrays in memory and takes a four-index AO 2-PDM
from a file. For MP2 the 2-PDM is available as `(naux, nocc*nvir)`, so the contraction here needs one auxiliary block in the AO
basis at a time. Example sizes: naphthalene, 790 basis functions, 24 active occupied orbitals — the AO pair route needs
2.5 GB per thousand auxiliary functions per array; the three-index 2-PDM is 0.15 GB per thousand.
*— measured numbers from the run `dfmp2_grad_vs_psi4` go here.*

**Differences from #3426, for discussion.**
- A conventional SCF reference is accepted (exact ERIs in the reference, fitted ERIs in the correlation energy — what
  `DFMP2(mf)` computes today). #3426 refuses one for CCSD. Both cases are tested against finite differences.
- A fitting basis on `mp.with_df` different from the reference's is supported; the gradient then has two auxiliary responses.
- `df.grad.mp2` imports `_auxmol` and `_pair_weights` from `df.grad.ccsd`, which imports `pyscf.cc`. They could move to
  `df/grad/rhf.py` if preferred.

**Companion edits, as #3426 made them.** `pyscf/grad/mp2.py` warns when the reference is density fitted; `dfump2` and `dfgmp2`
raise `NotImplementedError` with a message.

**Benchmark.** Water (distorted, no symmetry), cc-pVDZ, central differences with h = 1e-3 Bohr against PySCF's own DF-MP2 energy:

| reference | fitting of the correlation part | frozen | max abs(analytic − FD), Eh/Bohr |
|---|---|---|---|
| `density_fit()` cc-pVDZ-JKFIT | the reference's | — | ≤ 1.7e-07 (the run's worst is 1.70e-07; this row's own line to be re-read before posting) |
| `density_fit()` cc-pVDZ-JKFIT | cc-pVDZ-RI | — | 1.7e-07 |
| `density_fit()` cc-pVDZ-JKFIT | cc-pVDZ-RI | 1 | 1.7e-07 |
| conventional ERIs | cc-pVDZ-RI | — | 1.4e-07 |
| conventional ERIs | default | 1 | 1.4e-07 |

Against Psi4 1.10.2 (DF-MP2 gradient, same fitting sets, frozen core): benzene, cc-pVTZ — max abs difference 6.2e-08 Eh/Bohr,
energies equal to 1e-09 Eh. *— benzene and naphthalene in ano-pVQZ from the run go here, with time and peak memory.*

**Tests.** New `pyscf/df/test/test_df_mp2_grad.py`, 10 tests on a water molecule without symmetry: finite-difference checks for a
density-fitted reference, a frozen core plus a frozen virtual orbital, a separate RI basis, a conventional reference and the
smallest block size; the scanner at a second geometry; `auxbasis_response = False` changes the result; a non-converged reference
is refused; dispatch; the DF-UMP2 guard. Checked by hand and not in the test file: `mol.symmetry`, Cartesian functions, `atmlst`.

**Depends on** the scanner fix (draft 1): without it the gradient scanner is wrong at a new geometry.

**Not addressed.** DF-UMP2 gradients. Amplitudes are needed in memory (`with_t2`); rebuilding them block by block from `ovL`
would lift that. With a nearly singular fitting metric the energy (`dfmp2`'s own decomposition) and the gradient
(`_gen_metric_solver`) may drop different vectors, as in #3426.

**Notes (AI disclosure).** Developed with an AI coding assistant (Claude Code): code, tests and this description were drafted
with it; I reviewed the derivation and the code, ran the checks above and can explain them. — *wording to be the user's own.*

## Before the user posts anything

1. The run `dfmp2_grad_vs_psi4` (benzene and naphthalene in ano-pVQZ against psi4, under a 12 GB cap) — its numbers into the
   benchmark, and the requirement of the design note answered yes or no. It reads the first draft's code; the contraction is
   the same in the reviewed branch, and one case is repeated on that branch before posting.
2. The composite step in cm⁻¹ through the new gradient (design note, validation 4).
3. The user reads `pyscf/df/grad/mp2.py` against `pyscf/grad/mp2.py` and `pyscf/df/grad/ccsd.py` until he can explain each
   block; a walk-through for that is the next thing to write, on his word.
4. Rebase both branches on upstream master on the day of posting; run pyscf's lint (`ruff check --config .ruff.toml pyscf`) and
   the six test files again.
