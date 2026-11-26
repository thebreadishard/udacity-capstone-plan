# Reading guide: the two pyscf drafts, so that the author can explain them

Written 26 Nov 2026 for the user, who posts the pull requests himself. pyscf's policy asks that the contributor 'must understand
and be able to explain the code' and the related existing code. This guide is the order to read in and what each part does; it
is not a substitute for reading. Code: WSL, `~/pyscf-wt-dfmp2scan` (the scanner fix) and `~/pyscf-wt-dfmp2grad2` (the gradient).
Texts: `Draft_2026-11-26_pyscf_PRs_DFMP2.md`. Design and its reasons: `Design_2026-11-26_pyscf_DFMP2_Gradient.md`.

To see a draft: `git -C ~/pyscf-wt-dfmp2scan show` and `git -C ~/pyscf-wt-dfmp2grad2 show` in WSL.

## Part 1 — the scanner fix (ten minutes)

**What a scanner is.** `pt.as_scanner()` gives a function of the geometry: call it with a new molecule and it reruns the SCF and
the MP2 and returns the energy. Geometry optimisers use it.

**The bug.** The conventional MP2 class reads the orbital energies from the SCF object each time. The density-fitted class
`dfmp2.DFRMP2` keeps its own copy, `self.mo_energy`, made once in `__init__`. The scanner (`MP2_Scanner.__call__` in
`pyscf/mp/mp2.py`) copies the new `mo_coeff` and `mo_occ` from the SCF after each geometry — and nothing else. So at a second
geometry DF-MP2 uses new orbitals with the first geometry's orbital energies. The MP2 energy divides by differences of orbital
energies, so it is wrong: −6.3e-4 Eh on water after moving two hydrogens.

**The fix.** Three lines in that `__call__`: if the object has a `mo_energy`, take the SCF scanner's. One test: scanner at a second
geometry equals a fresh calculation.

**Questions you may get.**
- *Why `getattr(self, 'mo_energy', None) is not None` and not a change in `dfmp2.py`?* The scanner is where `mo_coeff` and
  `mo_occ` are already refreshed; one place for all DF variants (RMP2, UMP2, GMP2). An alternative they may prefer: `DFRMP2`
  overriding `reset`. Either is fine with us.
- *Does it change anything else?* A `mo_energy` passed by hand to `DFMP2(mf, mo_energy=…)` is replaced by the scanner, as
  `mo_coeff` already is. Conventional MP2 scanners are untouched (no such attribute).

## Part 2 — the gradient (an evening)

### The physics in five sentences

The MP2 energy is the Hartree–Fock energy plus a correlation energy built from amplitudes `t2`. Its derivative with respect to a
nuclear position needs three kinds of term: (1) the derivative of the two-electron integrals, weighted by a 'two-particle
density' made of the amplitudes; (2) the response of the orbitals, which nobody computes directly — one linear equation (the
Z-vector or CPHF equation) is solved once instead; (3) the Hartree–Fock-like terms with a 'relaxed' one-particle density.
Density fitting writes every two-electron integral as a product of three-index integrals and the inverse of a two-index
'metric'; so the derivative of a fitted integral has three pieces: the derivative of each three-index integral with respect to
the orbital basis centres, with respect to the auxiliary basis centres, and the derivative of the metric.

### Read in this order

1. **`pyscf/grad/mp2.py`, `grad_elec`** (upstream, 150 lines) — the conventional gradient. Its first half is one loop over
   atoms ('2e AO integrals dot 2pdm') that produces `de` (the gradient piece), `Imat` (an intermediate matrix that feeds the
   Z-vector equation and the overlap-derivative term) and `vhf1` (the Hartree–Fock-like piece). Its second half uses them.
2. **`pyscf/df/grad/ccsd.py`** (upstream, pull request 3426) — the same for CCSD with density fitting. Note its two
   substitutions; ours are the same two.
3. **Our `pyscf/df/grad/mp2.py`.** Five functions and a class:

| function | what it is | what to be able to say |
|---|---|---|
| `make_df_rdm2` | builds the three-index two-particle density `dfdm2[P,ia]` and the matrix for the metric term | one pass over the auxiliary basis to get `(P|ia)`, a solve with the metric, then a contraction with `4 t2 − 2 t2ᵀ` — the same combination the conventional code uses; cost like the energy |
| `_contract_dfdm2` | substitution 1: replaces the four-index loop | per block of auxiliary shells: the density is taken to the atomic-orbital basis, contracted with `(P|uv)` for `Imat`, with the derivative integrals `int3c2e_ip1` (orbital centres), `int3c2e_ip2` (auxiliary centres), and at the end `int2c2e_ip1` with `metric`; only one block is ever in the large basis — this is why it is block-wise |
| `_contract_dfvhf1` | substitution 2 for a density-fitted reference | the Hartree–Fock-like term that mixes the SCF density with the relaxed MP2 density; written here because the reference's own `get_jk` keeps `(naux,nao,nao)` arrays in memory for a full-rank density (10.5 GB on benzene in ano-pVQZ, 3.5 GB with this function) |
| `_contract_vhf1` | substitution 2 for the other references | exactly 3426's lines through `mf_grad.get_jk`; used for a conventional reference and for `only_dfj` |
| `grad_elec` | `pyscf/grad/mp2.py`'s, with the loop replaced | everything after '2e-part grad' is upstream's text; two guards at the top (a non-converged reference, missing `t2`) |
| `Gradients` | the class | `auxbasis_response` switch as in 3426; attached to `dfmp2.DFRMP2` at the bottom |

4. **The companion edits**: `dfmp2.py` (`nuc_grad_method` now returns the class), `grad/mp2.py` (a warning when someone uses the
   conventional gradient on a density-fitted reference — 3426 added the same to `grad/ccsd.py`), `dfump2.py` and `dfgmp2.py`
   (the 'not available' errors now say so).
5. **`pyscf/df/test/test_df_mp2_grad.py`** — each test compares with finite differences of pyscf's own energy; read the comment
   of each to know what it guards.

### The three decisions that differ from 3426, and why

- **Block-wise, with the density kept three-index.** 3426 holds three `(naux, nao_pair)` arrays. For MP2 the density exists in
  the small occupied–virtual form, so only one auxiliary block has to be in the large basis at a time. Without this, density
  fitting's purpose — large basis sets — is lost.
- **Our own contraction for the Hartree–Fock-like term.** Same reason, measured: 10.5 GB → 3.5 GB on benzene in ano-pVQZ.
- **A conventional reference is accepted.** `DFMP2(mf)` on a conventional SCF is what the class computes today (exact
  Hartree–Fock, fitted correlation); its gradient is well defined and tested against finite differences. 3426 refuses that
  case for CCSD.

### Numbers to know

- Against finite differences (water, cc-pVDZ, five settings): 1.7e-7 Eh/Bohr at worst — the noise floor of a 1e-3 Bohr step;
  3426 reports 1.4e-7.
- Against Psi4, same fitting sets: benzene cc-pVTZ 6.2e-8 Eh/Bohr; benzene ano-pVQZ 4.4e-8, 167 s against Psi4's 764 s, peak
  3.5 GB. naphthalene ano-pVQZ (790 functions) 2.7e-7, 830 s against 2108 s, peak 7.7 GB under a 12 GB cap. The first draft peaked at 10.5 GB on benzene; that is why `_contract_dfvhf1` exists.
- What it does not do: open shells; a calculation without `t2` in memory.

### Honest answers to 'how was this made'

Drafted with an AI coding assistant; two independent AI reviews (correctness, and house style) and their findings were answered;
checked against finite differences and against Psi4. The pull request's `Notes` section says so, as pyscf's policy asks.
