# Design note: an analytic DF-MP2 nuclear gradient for pyscf (PR candidate, TASKS 321)

Written 26 Nov 2026, 08:30, on the user's word ('Ja, maak de ontwerpnotitie maar'); rewritten the same morning to route C after
the user asked which route pyscf's own team would choose ('Ja, lees dfmp2.py na en schrijf om naar route C'). A design, not
code: nothing is written in pyscf's tree and nothing is posted. Upstream state read on 26 Nov from pyscf's master and the tags
v2.14.0 and v2.15.1.

## The rule this work stands under

The user, 26 Nov: all code we write for a package must not only meet the standards the package publishes, it must also look,
in style, like what is already in the repository — **as if that team had written it themselves** — and the independent reviewer
must check exactly that. The same question decides the design: not 'what serves our run' but 'what would this team want in
their package'.

So for this pull request:

- **pyscf's rules replace ours inside pyscf's tree.** Our own Python rules (type hints on every public function, our function-size
  limits, ruff's project set) are for our repository. In pyscf the neighbours have no type hints, write compact scientific code
  and follow pyscf's own lint configuration; we write as they do.
- **Every choice is settled by the nearest neighbour first**, then by pyscf's published guidance, never by our habits. The
  neighbours here are `pyscf/df/grad/ccsd.py` and `ccsd_t.py` (the newest density-fitted post-HF gradients, pull request 3426,
  September 2026), `pyscf/grad/mp2.py` with `pyscf/grad/test/test_mp2.py`, and `pyscf/mp/dfmp2.py`.
- **The independent reviewer gets a style brief of its own**, beside the correctness review: the diff, the neighbour files, and
  pyscf's `agent-recipes/skills/pyscf-coding-style.template.md` and `pyscf-pr-review.template.md` (its own PR checklist). The
  question put to the reviewer: *which lines would a pyscf maintainer recognise as not theirs?* Every such line is a finding.
  Marks to compare, taken from the neighbours as read on 26 Nov:
  - the Apache licence header with 'The PySCF Developers', and an `Author:` line where the file's neighbours carry one;
  - a module docstring in `'''…'''` that says what the module is and, where it copies a pattern, from which module
    (`df/grad/ccsd.py`: 'Copied from pyscf.grad.ccsd.py. The four-index ERI derivatives are replaced by …');
  - the gradient modules' shape: a module-level `grad_elec(mp_grad, t2, atmlst=None, verbose=logger.INFO)`, a `Gradients` class
    with `grad_elec = grad_elec`, `Grad = Gradients`, and the method attached to the energy class with `lib.class_as_method`;
  - `numpy` or `np` as the file's package neighbours import it (the `grad` modules write `numpy`);
  - memory handled as the neighbours do: block sizes from `max_memory`, `lib.prange`, `balance_partition`, HDF5 temporaries
    through `lib.H5TmpFile`; diagnostics through `lib.logger` with `log.timer_debug1`, never `print`;
  - docstrings by PEP 257 with a summary line that is a command ending in a period — the user's standing rule since a pyscf
    review of 5 Nov ('comment can be simpler'), the one place where we do not copy the neighbours' older noun phrases;
  - compact conventions the lint configuration permits (`if t2 is None: t2 = mp.t2`), comments that say why;
  - tests in `unittest` with `setUpModule`/`tearDownModule`, a `KnownValues` class, `mol.output = '/dev/null'`, small molecules,
    `lib.fp` fingerprints and `assertAlmostEqual(…, 6)`, a finite-difference check through the scanner;
  - a runnable example in `examples/` — pyscf's PR checklist asks for one with every new feature.
- **pyscf's AI policy binds the user, not me** (`AI_POLICY.md`). In its words: the contributor is responsible for the code and
  'must understand and be able to explain' it and the related existing code; AI use is disclosed in a `Notes` section of the
  pull request, naming the tool and what it did; nobody uses AI 'to speak for' them in issues and pull requests; an agent that
  writes code and submits a pull request by itself is not permitted — a human reviews and submits. Drafting an issue
  description is among the uses the policy allows. For us: I draft code and texts; the user reads the code until he can explain
  it, makes the texts his own, posts himself and answers reviewers in his own words. This is the standing rule of our earlier
  pyscf pull requests and stays so.

## What is missing upstream, and what exists

- **The main DF-MP2 class cannot give a gradient.** `pyscf/mp/dfmp2.py` is what a user gets from `mf.density_fit().MP2()` and
  `mf.DFMP2()`; the core team rewrote it in 2024. Its class `DFRMP2(mp2.RMP2)` ends in `nuc_grad_method: raise
  NotImplementedError` and `Gradients = NotImplemented`. There is no `pyscf/df/grad/mp2.py` and no open pull request for one; the
  feature tracker (issue 1371) lists gradients with density fitting among its open items.
- **What that class already holds** (read in `dfmp2.py` on 26 Nov):
  - the amplitudes `t2` (occupied² × virtual²), kept in memory by default (`with_t2`, config `mp_dfmp2_with_t2`); `make_rdm1`
    and `make_rdm2` already require them (`assert t2 is not None`);
  - the three-index integrals of the occupied–virtual pairs, `eris.ovL`, in memory or on disk, served in occupied blocks
    (`get_occ_blk`);
  - its fitting basis in `mp.with_df`: the reference's when the reference is density fitted, otherwise one of its own built
    with `df.make_auxbasis(mol, mp2fit=True)`; a user may set another;
  - frozen orbitals through the base class (`_mo_splitter`, `split_mo_coeff`).
- **The gradient pattern the team accepted two months ago**: `pyscf/df/grad/ccsd.py` (pull request 3426) is the conventional
  gradient's `grad_elec` with the four-index derivative block replaced; it reuses `pyscf.grad.mp2`'s frozen-orbital helpers,
  takes the fitting basis from `mycc.with_df` or the reference's, has an `auxbasis_response` switch, delegates the Hartree–Fock
  part to `mycc._scf.nuc_grad_method()`, and insists on a density-fitted reference.
- **A second DF-MP2 implementation exists**: `pyscf/mp/dfmp2_native.py` (an outside contribution of 2021, pull request 963),
  with relaxed densities from a three-index two-particle density. It is not what the factory methods return.

## Three routes, and the one pyscf's team would want

**Route A — route 3426 copied literally.** Build the MP2 two-particle density as `pyscf/grad/mp2.py` does, transform it to the
atomic-orbital basis and reuse `df/grad/ccsd.py`'s contraction. Smallest diff. But it stores the four-index density on disk
(basis-function pairs × pairs): for naphthalene in ano-pVQZ, 790 functions, 312,445² numbers — about 780 GB. For CCSD that
price is defensible beside CCSD itself; for MP2 it removes the reason density fitting exists, and a maintainer who knows the
method sees that.

**Route B — on `dfmp2_native.py`'s three-index density.** Efficient, and what this note first recommended. Seen from pyscf's
side it is the wrong place: the gradient would work on the side module and still raise on the class everybody uses; the diff
is the largest and in another style than the gradient modules. That recommendation came from our need, not from their view.

**Route C — the shape of A with the substance of B, on the main class (chosen).**
- the gradient on `dfmp2.DFRMP2`, so that `mf.density_fit().MP2().nuc_grad_method()` works where it raises today;
- a small module beside `df/grad/ccsd.py`, written as that file is: `pyscf/grad/mp2.py`'s `grad_elec` with its four-index
  block replaced, the same helpers, the same `auxbasis_response` switch;
- the two-particle density kept three-index: built from the amplitudes the class already stores and the `ovL` integrals it
  already has, contracted with three-index derivative integrals — the method's own formulation
  ([Weigend & Häser 1997](https://doi.org/10.1007/s002140050269); [DiStasio et al. 2007](https://doi.org/10.1002/jcc.20604));
- **an issue first**, with the proposal, before a line of code: a new capability's place and interface are the team's to decide.

Route A stays useful to us as the independent second route in our own validation (a few dozen lines on existing functions;
never in the pull request).

## Route C in outline

- **Where.** `pyscf/df/grad/mp2.py`, attached as `dfmp2.DFRMP2.Gradients = lib.class_as_method(Gradients)`, with
  `DFRMP2.nuc_grad_method` returning it — the placement of `df/grad/ccsd.py` and its last two lines. Proposed in the issue, not
  assumed.
- **`grad_elec(mp_grad, t2, atmlst=None, verbose=logger.INFO)`**, following `pyscf/grad/mp2.py` step by step:
  1. the one-particle density blocks from `t2`, as today;
  2. in place of the four-index two-particle density: Γ(ia, L) = Σ_jb (2 t_ij^ab − t_ij^ba)-type amplitudes × (jb|L), built in
     occupied blocks with `eris.get_occ_blk`, the block size from `max_memory`; stored occupied·virtual × auxiliary, the size
     of `ovL` itself;
  3. the orbital Lagrangian (`Imat` in the neighbours' naming) from Γ and three-index integrals with one general index, then
     the existing `_response_dm1` (the Z-vector step of `grad/mp2.py`) and the existing frozen-orbital treatment
     (`_index_frozen_active`, `has_frozen_orbitals`);
  4. the non-separable two-electron gradient: Γ back-transformed to atomic orbitals one auxiliary block at a time and
     contracted with `int3c2e_ip1`, and — under `auxbasis_response` — with `int3c2e_ip2` and the metric derivative
     `int2c2e_ip1`, through the wrappers `df/grad/ccsd.py` imports from `pyscf.df.grad.rhf`;
  5. the separable part, the overlap and core-Hamiltonian terms through `mp._scf.nuc_grad_method()`, as in 3426.
- **Points that are the maintainers' call, to put in the issue rather than decide ourselves:**
  - *The reference.* 3426 refuses a reference that is not density fitted. `DFMP2(mf)` on a conventional reference is today's
    documented use and differentiates a well-defined energy (exact Hartree–Fock plus fitted correlation). Follow 3426's
    restriction, or support both?
  - *Two fitting sets.* A density-fitted reference in a JKFIT set with the correlation part in an RI set (set through
    `mp.with_df`) is the standard practice and what psi4 does; the gradient then carries two auxiliary responses. 3426's
    `_auxmol` already reads `with_df` from the method object first — the same here.
  - *The integrals' form.* `ovL` is stored with the fitting metric folded in, and its construction has a linear-dependence
    threshold (`THRESH_LINDEP`). The gradient needs the metric's derivative; whether to differentiate through the stored form
    or rebuild plain three-index integrals in the gradient, as `df/grad/ccsd.py` does, is to be read in
    `_init_mp_df_eris` before the issue is written — **not yet read**.
  - *Amplitudes.* First version: `t2` in memory, as `make_rdm1` and `make_rdm2` require today; a calculation run with
    `with_t2 = False` gets an informative error. Rebuilding the amplitudes block by block from `ovL` (which would lift the
    occupied² × virtual² memory) is a later improvement, said as such.
- **Stated limits**, each an informative error and never a silent fallback (pyscf's checklist): closed-shell RHF in this pull
  request (`dfump2.py` is a second one, and the one our cation rows would need); canonical orbitals; real orbitals (the
  integral objects assert `float64` today).
- **Scanner.** `pyscf/grad/mp2.py` has `as_scanner`; pyscf's checklist asks that `reset` and cached state are handled —
  `DFRMP2.reset` already resets `with_df`.

## Sizes for our own case (computed here, not measured)

Naphthalene in ano-pVQZ: 790 functions, 34 occupied of which 10 frozen, 756 virtual. Amplitudes 24² × 756² × 8 bytes = 2.6 GB.
The three-index density has the size of `ovL`: 24 × 756 × (auxiliary functions) × 8 bytes — 0.15 GB per thousand auxiliary
functions. Route A's four-index density: 780 GB.

## Tests and example, in pyscf's manner

- Tests beside the neighbours' (`pyscf/df/grad/test/` holds none for 3426 at v2.15.1 — where its tests live is to be looked up
  and followed). Water in a small basis, as `test_mp2.py`: the gradient against central finite differences of the DF-MP2 energy
  through the scanner; a `lib.fp` reference value; frozen core; `auxbasis_response` off; a separate fitting set on `mp.with_df`.
  One behaviour per test.
- An example `examples/mp/` or `examples/grad/` next to its neighbours, with comments on what each setting does.
- An independent expected value, as their style guide asks: the finite difference is one; psi4's DF-MP2 gradient with the same
  fitting sets is a second, given in the pull request's description with its input, not committed as a dependency.

## Validation on our side before the user sees a draft

By our own rules (two routes for every derived quantity; 'validated' only with number and counterpart):

1. against finite differences of the energy on water, line 1e-6 E_h/bohr (the check our psi4 route passed at 4.9e-8);
2. against route A (the four-index assembly) on water and benzene in cc-pVDZ, to 1e-8;
3. against psi4's DF-MP2 gradient with identical fitting sets on benzene in cc-pVTZ and on naphthalene, element by element;
4. one composite step through it: naphthalene's cc-pVTZ rows by the new gradient against the psi4 rows we hold, in cm⁻¹
   (the swap test of 20 Oct, line 0.5);
5. time and peak memory against psi4 on the same machine — reported in the pull request only as measured.

Then the independent review, twice over: correctness, and the style brief above.

## Order of work

1. Read `_init_mp_df_eris` and `_init_mp_df_eris_direct` (the integrals' form), `pyscf/grad/mp2.py` in full, and where 3426's
   tests are.
2. Draft the issue: what is missing, the proposed place and interface, the four questions above. The user makes it his own and
   posts it — on his word only.
3. On the maintainers' answer (or after a reasonable wait, the user decides): the module, its tests and example in a worktree
   of pyscf's master; the five validations; the two reviews.
4. The user reads it until he can explain it; he opens the pull request with its `Notes` section.

## What it is worth to us, and what it costs

- Worth: one engine for the whole composite; the ANO sets without a second program; a gradient we would use for the MP2 step
  of every anchor (TASKS 320) and for the basis-set work of TASKS 319.
- It does not shorten the run that is on the server now, and psi4 keeps working. This is `[LATER]` work: a contribution that
  fits the package, done when it does not take time from the proof.
- Size, estimated and not measured: a module of the size of `df/grad/ccsd.py` (about 330 lines) with tests and example;
  several working days including the five validations, before review rounds upstream.

## Questions for the user

1. Route C, with an issue first — agreed?
2. Scope of the first pull request: RHF only, with UHF as a second one — agreed?
3. When: now, beside the naphthalene run, or after the supervisor proposal (TASKS 311 step 2)?
4. Which name and e-mail address go on an `Author:` line, if the neighbours carry one, is the user's to give.
