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

And the user, 26 Nov 08:41: **the proposal is made so that it solves our problems** — 'als wij blokken nodig hebben, omdat we
het anders niet kunnen runnen, dan blokken'. The two rules do not pull apart: what we need decides *what* the code must be able
to do, the team's habits decide *how it is written*. A contribution we cannot run on our own case is not worth our days,
however well it blends in.

**What it must be able to do (the requirement):** the composite's MP2 step for our anchors — naphthalene in ano-pVQZ (790
functions) as the stated case, larger anchors after it — on the machines we have: within the laptop's 13 GB budget for all
runs, or a 30 GB server. That is measured in the validation and stated in the pull request.

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
  - the Apache licence header with 'The PySCF Developers'; an `Author:` line only if the nearest neighbour has one
    (`grad/mp2.py` does, `df/grad/ccsd.py` does not);
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

## What the reads of 26 Nov found (the three points this note first left open)

- **`pyscf/grad/mp2.py` in full.** Its `grad_elec` has two halves. The first is one loop, '2e AO integrals dot 2pdm': it
  holds a half-transformed density (occupied² × basis², never the full four-index one) and contracts it atom by atom with the
  four-index integrals and their derivatives, giving three things — the gradient term `de`, the intermediate `Imat`, and the
  Hartree–Fock term `vhf1`. The second half (frozen orbitals, the Z-vector step `_response_dm1`, the overlap and
  core-Hamiltonian terms) is, line for line, what `df/grad/ccsd.py` has after its own contraction. So the conventional MP2
  gradient is lean in memory; its cost at 790 basis functions is the four-index derivative integrals. The file carries
  `# Author: Qiming Sun`; `df/grad/ccsd.py`, the newer neighbour, carries no `Author:` line.
- **The integrals' form in `dfmp2.py`.** `ovL` is the occupied–virtual three-index integral with the inverse square root of the
  fitting metric folded in. It is built one of two ways: from the reference's stored fitting vectors when they exist
  (`with_df._cderi`), or directly, with its own Cholesky factor of the metric — and, only when that factorisation fails, an
  eigen-decomposition that drops vectors under `THRESH_LINDEP` (1e-10). The factor is a local variable and is not kept. So
  the gradient cannot turn a density in `ovL`'s basis back into plain auxiliary functions. `df/grad/ccsd.py` meets the same
  situation and does not try: it recomputes plain three-index integrals and solves with the metric
  (`_gen_metric_solver`, which has the same Cholesky-then-eigenvalue fallback). The MP2 gradient does the same.
- **3426's tests and how it was proposed.** One new file, `pyscf/df/test/test_df_ccsd_grad.py` (124 lines, six tests, 8.6 s by
  its description): HF molecule in 6-31G, `make_mol` / `make_cc` / `numeric_grad` helpers, each analytic gradient against
  central differences of pyscf's own energy with `assertAlmostEqual(abs(g1 - ref).max(), 0, 6)`, a dispatch test, a test that
  the fitted and the conventional assembly differ, a test that a conventional reference is refused, a test that the
  unrestricted case raises. No example file. It answered an issue (3425, a bug report: the gradient of a density-fitted
  CCSD was silently the conventional one), its description has the sections 'The bug / The fix / Benchmark / Tests / Not
  addressed', and one core maintainer approved it. Under 'Not addressed' its author names the MP2 hole: `mp2.RMP2(df_mf)`
  built directly differentiates the wrong functional, while `mp.MP2` 'correctly returns the already-guarded `DFMP2`' — the
  guard being the `NotImplementedError` this proposal would replace. Nobody has an open pull request for it (checked 26 Nov;
  3426's author has merged fifteen others since, none on MP2).

## Route C in outline

- **Where.** `pyscf/df/grad/mp2.py`, attached as `dfmp2.DFRMP2.Gradients = lib.class_as_method(Gradients)`, with
  `DFRMP2.nuc_grad_method` returning it — the placement of `df/grad/ccsd.py` and its last two lines. Proposed in the issue, not
  assumed.
- **`grad_elec(mp_grad, t2, atmlst=None, verbose=logger.INFO)`** is `pyscf/grad/mp2.py`'s, with the same two substitutions 3426
  made to the CCSD one and nothing else changed:
  1. the loop '2e AO integrals dot 2pdm' is replaced by a density-fitted contraction that returns `de` and `Imat`: plain
     three-index integrals (P|μν); d = metric⁻¹ (P|μν); the fitted two-particle density
     Γ(P, μν) = Σ_ia C_μi C_νa Σ_jb T_ij^ab d(P, jb), with T the same combination of amplitudes the conventional code builds
     (4 t_ij^ab − 2 t_ij^ba) — an occupied² × virtual² × auxiliary contraction, the cost of the energy itself; then the
     contraction with `int3c2e_ip1`, and under `auxbasis_response` with `int3c2e_ip2` and `int2c2e_ip1`;
  2. the `vhf1` term goes through `mf_grad.get_jk`, which brings the reference's own auxiliary response, as in 3426.
- **Reuse.** 3426's `_contract_dfdm2` is exactly step 1's second half, but it builds its fitted density inside itself from a
  four-index file. pyscf's style guide: 'If broader reuse is needed, explicitly generalize the function's contract'. So the
  honest options are a small generalisation of `df/grad/ccsd.py` (the contraction takes the three arrays as arguments; the CCSD
  path unchanged in behaviour and covered by its six tests) or a copy with a comment saying why — the maintainers' call.
- **Block-wise from the start — decided by the requirement, not a question for the maintainers.** 3426 keeps three arrays of
  (auxiliary functions × basis-function pairs) in memory; written that way the MP2 gradient could not run our case (15 GB at
  two thousand auxiliary functions, before anything else). So the fitted density and the solved integrals are built and
  contracted one block of auxiliary shells at a time, with what must persist between the passes kept in the
  occupied–virtual basis (the size of `ovL`) in memory or in an `lib.H5TmpFile`, as `ovL` itself is. This is not a foreign
  style in pyscf: `dfmp2.py`, the class the gradient belongs to, is written exactly so — block sizes from `max_memory`,
  `lib.prange` over occupied blocks, `balance_partition` over auxiliary shells, an in-core and an out-of-core path chosen by
  available memory. The neighbour for the gradient's *assembly* stays `df/grad/ccsd.py`; the neighbour for its *memory
  handling* is `dfmp2.py`. The issue says this plainly, with the sizes, as the reason the module is not a line-for-line
  sibling of 3426. It also settles the reuse question below towards a contraction of our own that works on blocks (with a
  comment saying why 3426's in-memory one is not reused — pyscf's checklist asks for exactly that comment), unless the
  maintainers prefer 3426's function generalised to blocks.
- **Points that are the maintainers' call, to put in the issue rather than decide ourselves:**
  - *Generalise 3426's contraction, or copy it?* (above)
  - *The reference.* 3426 refuses a reference that is not density fitted, with a test and a reason in its comments (the
    Hartree–Fock half would differentiate exact integrals, the correlation half fitted ones). `DFMP2(mf)` on a conventional
    reference is today's documented use, and exact Hartree–Fock plus fitted correlation is a well-defined energy. Follow 3426's
    refusal for consistency, or support both?
  - *Two fitting sets.* A density-fitted reference in a JKFIT set with the correlation part in an RI set (through
    `mp.with_df`) is standard practice and what psi4 does; the gradient then carries two auxiliary responses. 3426's `_auxmol`
    already reads `with_df` from the method object first — the same here.
  - *Amplitudes.* `t2` in memory, as `make_rdm1` and `make_rdm2` require today; a calculation run with `with_t2 = False` gets
    an informative error. Rebuilding the amplitudes block by block from `ovL` is a later improvement, said as such.
- **Stated limits**, each an informative error and never a silent fallback (pyscf's checklist): closed-shell RHF in this pull
  request (`dfump2.py` is a second one, and the one our cation rows would need); canonical orbitals; real orbitals (the
  integral objects assert `float64` today). When the metric is so nearly singular that the eigenvalue fallback drops vectors,
  energy and gradient may each drop their own — 3426 has the same property; to be said in the description, not hidden.
- **Scanner.** `pyscf/grad/mp2.py` has `as_scanner`; pyscf's checklist asks that `reset` and cached state are handled —
  `DFRMP2.reset` already resets `with_df`, and 3426's description says it checked exactly this by hand.

## Sizes for our own case (computed here, not measured)

Naphthalene in ano-pVQZ: 790 functions, 34 occupied of which 10 frozen, 756 virtual, 312,445 basis-function pairs.
- Amplitudes: 24² × 756² × 8 bytes = 2.6 GB.
- Each (auxiliary × pairs) array: 2.5 GB per thousand auxiliary functions; the neighbour's way holds three, 7.5 GB per
  thousand. How many auxiliary functions our fitting sets have on naphthalene is not looked up here; with two thousand it is
  15 GB — more than psi4 needed on benzene (6.9 GB), and the reason the gradient is block-wise from the start.
- Block-wise: the amplitudes, two occupied–virtual × auxiliary arrays (0.15 GB each per thousand auxiliary functions,
  in memory or on disk) and one block of auxiliary shells at a time (2.5 GB per thousand functions in the block, set by
  `max_memory`).
- Copying 3426's CCSD route literally (route A): 780 GB.

## Tests and example, in pyscf's manner

- A new file `pyscf/df/test/test_df_mp2_grad.py` beside `test_df_ccsd_grad.py` and in its manner: the same small molecule and
  helpers' shape, each case against central differences of pyscf's own DF-MP2 energy, one behaviour per test — the gradient;
  frozen core; a separate fitting set on `mp.with_df`; `nuc_grad_method` returns the new class; the fitted and the
  conventional assembly differ; the unrestricted case still raises.
- An example: 3426 added none, pyscf's PR checklist asks for one with a new feature. Ours adds a short one next to
  `examples/mp/10-dfmp2.py`, and the issue asks whether they want it.
- The pull request's description in 3426's sections (what was missing / what it does / benchmark / tests / not addressed),
  with the benchmark as a table of analytic minus finite difference, and psi4's DF-MP2 gradient with the same fitting sets as
  an independent second value, its input given.

## Validation on our side before the user sees a draft

By our own rules (two routes for every derived quantity; 'validated' only with number and counterpart):

1. against finite differences of the energy on water, line 1e-6 E_h/bohr (the check our psi4 route passed at 4.9e-8);
2. against route A (the four-index assembly) on water and benzene in cc-pVDZ, to 1e-8;
3. against psi4's DF-MP2 gradient with identical fitting sets on benzene in cc-pVTZ and on naphthalene, element by element;
4. one composite step through it: naphthalene's cc-pVTZ rows by the new gradient against the psi4 rows we hold, in cm⁻¹
   (the swap test of 20 Oct, line 0.5);
5. time and peak memory against psi4 on the same machine — reported in the pull request only as measured;
6. the requirement itself: naphthalene's gradient in ano-pVQZ under a 13 GB cap (`max_memory` set accordingly), finished
   and equal to psi4's.

Then the independent review, twice over: correctness, and the style brief above.

## Order of work

1. Done on 26 Nov: the three reads (section above).
2. Draft the issue: what is missing (3426's own 'Not addressed' names it), the proposed place and interface, why it is
   block-wise, the four questions above. The user makes it his own and posts it — on his word only.
3. On the maintainers' answer (or after a reasonable wait, the user decides): the module, its tests and example in a worktree
   of pyscf's master; the six validations; the two reviews.
4. The user reads it until he can explain it; he opens the pull request with its `Notes` section.

## What it is worth to us, and what it costs

- Worth: one engine for the whole composite; the ANO sets without a second program; a gradient we would use for the MP2 step
  of every anchor (TASKS 320) and for the basis-set work of TASKS 319.
- It does not shorten the run that is on the server now, and psi4 keeps working. This is `[LATER]` work: a contribution that
  fits the package, done when it does not take time from the proof.
- Size, estimated and not measured: a module of the size of `df/grad/ccsd.py` (about 330 lines) with tests and example;
  several working days including the six validations, before review rounds upstream.

## Questions for the user

1. Route C, with an issue first — agreed?
2. Scope of the first pull request: RHF only, with UHF as a second one — agreed?
3. When: now, beside the naphthalene run, or after the supervisor proposal (TASKS 311 step 2)?
4. No `Author:` line: the newest neighbour (`df/grad/ccsd.py`) carries none. Agreed, or does the user want one as `grad/mp2.py` has?
