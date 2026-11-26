# Design note: an analytic DF-MP2 nuclear gradient for pyscf (PR candidate, TASKS 321)

Written 26 Nov 2026, 08:30, on the user's word ('Ja, maak de ontwerpnotitie maar'). A design, not code: nothing is written in
pyscf's tree and nothing is posted. Upstream state read the same morning from pyscf's master and the tags v2.14.0 and v2.15.1.

## The rule this work stands under

The user, 26 Nov: all code we write for a package must not only meet the standards the package publishes, it must also look,
in style, like what is already in the repository — **as if that team had written it themselves** — and the independent reviewer
must check exactly that.

So for this pull request:

- **pyscf's rules replace ours inside pyscf's tree.** Our own Python rules (type hints on every public function, our function-size
  limits, ruff's project set) are for our repository. In pyscf the neighbours have no type hints, write compact scientific code
  and follow pyscf's own lint configuration; we write as they do.
- **Every choice is settled by the nearest neighbour first**, then by pyscf's published guidance, never by our habits. The
  neighbours for this work are `pyscf/mp/dfmp2_native.py` (where the density lives), `pyscf/df/grad/ccsd.py` and `ccsd_t.py`
  (the newest density-fitted post-HF gradients, pull request 3426, September 2026), `pyscf/grad/mp2.py` and
  `pyscf/grad/test/test_mp2.py`.
- **The independent reviewer gets a style brief of its own**, beside the correctness review: the diff, the neighbour files, and
  pyscf's `agent-recipes/skills/pyscf-coding-style.template.md` and `pyscf-pr-review.template.md` (its own PR checklist). The
  question put to the reviewer: *which lines would a pyscf maintainer recognise as not theirs?* Every such line is a finding.
  Marks to compare, taken from the neighbours as read today:
  - the Apache licence header with 'The PySCF Developers' and an `Author:` line as the file's neighbours carry it;
  - a module docstring in `'''…'''` that says what the module is and, where it copies a pattern, from which module;
  - the gradient modules' shape: a module-level `grad_elec(mp_grad, …, atmlst=None, verbose=logger.INFO)`, a `Gradients` class
    with `grad_elec = grad_elec`, `Grad = Gradients`, and the method attached to the energy class with `lib.class_as_method`;
  - `numpy` or `np` as the file's package neighbours import it (the `grad` modules write `numpy`, `dfmp2_native.py` writes `np`);
  - memory handled as the neighbours do: block sizes from `max_memory`, `lib.prange`, `balance_partition`, HDF5 temporaries
    through `lib.H5TmpFile`; diagnostics through `lib.logger` with `log.timer_debug1`, never `print`;
  - docstrings by PEP 257 with a summary line that is a command ending in a period — the user's standing rule since a pyscf
    review of 5 Nov ('comment can be simpler'), the one place where we do not copy the neighbours' older noun phrases;
  - compact conventions the lint configuration permits (`if t2 is None: t2 = mp.t2`), comments that say why;
  - tests in `unittest` with `setUpModule`/`tearDownModule`, a `KnownValues` class, `mol.output = '/dev/null'`, small molecules,
    `lib.fp` fingerprints and `assertAlmostEqual(…, 6)`, a finite-difference check through the scanner;
  - a runnable example in `examples/` — pyscf's PR checklist asks for one with every new feature.
- **pyscf's AI policy binds the user, not me** (`AI_POLICY.md`, read today). In its words: the contributor is responsible for the
  code and 'must understand and be able to explain' it and the related existing code; AI use is disclosed in a `Notes` section of
  the pull request, naming the tool and what it did; nobody uses AI 'to speak for' them in issues and pull requests; an agent
  that writes code and submits a pull request by itself is not permitted — a human reviews and submits. For us: I draft code
  and a pull-request text; the user reads the code until he can explain it, posts it himself, and answers reviewers in his own
  words (I may help him understand a reviewer's point; I do not write his replies). This is the standing rule of our earlier
  pyscf pull requests and stays so.

## What is missing upstream, and what exists

- `pyscf/mp/dfmp2.py` and `pyscf/mp/dfmp2_native.py`: `nuc_grad_method` raises `NotImplementedError`. No `pyscf/df/grad/mp2.py`.
  No open pull request. The feature tracker (issue 1371) lists gradients with density fitting among its open items.
- `dfmp2_native.py` (pull request 963, 2021) already computes, for RHF with frozen core and spin-component scaling: the
  three-index two-particle density Γ (occupied × auxiliary × virtual, on disk), the orbital Lagrangian from it
  (`orbgrad_from_Gamma`), the frozen-core relaxation, the Fock response, and the Z-vector solution — that is, the relaxed
  one-particle density. A gradient needs exactly these and then one more step: contracting them with derivative integrals.
- `pyscf/df/grad/ccsd.py` (pull request 3426) has the derivative-integral machinery for a density-fitted correlation energy:
  three-index derivative integrals (`int3c2e_ip1`, `int3c2e_ip2`), the metric derivative (`int2c2e_ip1`), the
  `auxbasis_response` switch, and the Hartree–Fock part delegated to the reference's own `nuc_grad_method().get_jk`.

## Two routes

**Route A — beside `df/grad/ccsd.py`.** Build the MP2 two-particle density as `pyscf/grad/mp2.py` does, transform it to the
atomic-orbital basis, and reuse `_contract_dfdm2`. Small diff, closest to the newest neighbour. But it stores the four-index
density on disk (pairs × pairs of basis functions). For the case we need the gradient for — naphthalene in ano-pVQZ, 790 basis
functions — that is 312,445² numbers, about 780 GB. Route A gives pyscf a DF-MP2 gradient that cannot do the large-basis step
density fitting exists for.

**Route B — on `dfmp2_native`'s three-index density (recommended).** Keep everything three-index, as the method's literature
does ([Weigend & Häser 1997](https://doi.org/10.1007/s002140050269);
[DiStasio et al. 2007](https://doi.org/10.1002/jcc.20604)): the non-separable part of the gradient is Γ contracted with the
derivatives of (ia|P) and of the metric (P|Q); the separable part is the relaxed density with the reference's Fock derivative.
Storage stays occupied × auxiliary × virtual. More new lines than route A, but it finishes what `dfmp2_native.py` started and it
is the only one of the two that is useful at the sizes density fitting is for.

Both differentiate the same energy, so route A — a few dozen lines on top of existing functions — is still worth writing **as the
independent second route in our own validation** (never in the pull request).

## Route B in outline

- **Where.** A new module `pyscf/df/grad/dfmp2.py`? or `pyscf/grad/dfmp2.py`? The neighbours disagree: density-fitted *variants*
  of a method's gradient live in `pyscf/df/grad/` (rhf, ccsd), but `dfmp2_native` is a method of its own under `pyscf/mp/`. To
  be settled by asking the maintainers in the pull request's description rather than guessed; my reading is `pyscf/df/grad/mp2.py`,
  attached as `DFRMP2.Gradients`, with `DFRMP2.nuc_grad_method` returning it instead of raising.
- **What it computes**, for a converged `DFRMP2` object (RHF reference, frozen core, the SCS factors `ps`, `pt` it already has):
  1. the relaxed one-particle density and Γ, from the existing functions — by calling them, with at most a small change so
     that Γ and the Z-vector stay available after `make_rdm1(relaxed=True)` instead of being discarded (the smallest change
     that does it; no refactor of the module);
  2. the energy-weighted density (the term with the overlap derivative), which the density code does not build today;
  3. the non-separable two-electron part: Γ back-transformed in one index at a time against `int3c2e_ip1`, `int3c2e_ip2`
     and `int2c2e_ip1`, in blocks sized from `max_memory`, with an `auxbasis_response` attribute as in the DF-CCSD gradient;
  4. the separable part and the Hartree–Fock gradient through `mp._scf.nuc_grad_method()` — so a density-fitted reference
     contributes its own fitting basis's response and a conventional reference its four-index derivatives. psi4 does the same
     with its two fitting sets (JKFIT for the reference, RI for the correlation part).
- **Stated limits**, each an informative error and not a silent fallback (pyscf's checklist): closed-shell RHF only in this pull
  request (a UHF version on `dfump2_native.py` is a second one, and the one our cation rows would need); canonical orbitals;
  no solvent or QM/MM claims beyond what the reference's own gradient object provides.
- **A scanner** (`as_scanner`) as `pyscf/grad/mp2.py` has it, because the tests' finite-difference check and geometry
  optimisers use it; pyscf's checklist asks that `reset` and cached state (here the integral file and Γ) are handled.

## Tests and example, in pyscf's manner

- In `pyscf/df/grad/test/` or `pyscf/mp/test/test_dfmp2_native.py` — the neighbour decides; pyscf prefers extending an
  existing test file. Water in a small basis, as `test_mp2.py`:
  - the gradient against central finite differences of the DF-MP2 energy through the scanner;
  - a fingerprint (`lib.fp`) reference value;
  - frozen core on; the SCS factors on; `auxbasis_response` off against a reference value; a conventional and a
    density-fitted reference.
- `examples/mp/12-dfmp2_gradients.py` (the next number after `11-dfmp2-density.py`), with comments on what each setting does.
- An independent expected value, as their style guide asks ('independent expected results rather than duplicating implementation
  logic'): the finite difference is one; psi4's DF-MP2 gradient with the same fitting sets is a second, stated in the pull
  request's description with the input, not committed as a test dependency.

## Validation on our side before the user sees a draft

By our own rules (two routes for every derived quantity; 'validated' only with number and counterpart):

1. against finite differences of the energy on water, line 1e-6 E_h/bohr (the check our psi4 route passed at 4.9e-8);
2. against route A (the four-index assembly) on water and benzene in cc-pVDZ, to 1e-8;
3. against psi4's DF-MP2 gradient with identical fitting sets on benzene in cc-pVTZ and on naphthalene, element by element;
4. one composite step through it: naphthalene's cc-pVTZ rows by the new gradient against the psi4 rows we hold, in cm⁻¹
   (the swap test of 20 Oct, line 0.5);
5. time and peak memory against psi4 on the same machine — reported in the pull request only as measured.

Then the independent review, twice over: correctness, and the style brief above.

## What it is worth to us, and what it costs

- Worth: one engine for the whole composite; the ANO sets without a second program; and a gradient we would use again for the
  MP2 step of every anchor (TASKS 320) and for the basis-set work of TASKS 319.
- It does not shorten the run that is on the server now, and psi4 keeps working. This is `[LATER]` work: a contribution that
  fits the package, done when it does not take time from the proof.
- Size, estimated and not measured: route B is a few hundred lines with tests and example; several working days including the
  five validations, before review rounds upstream.

## Questions for the user before any code

1. Route B (three-index, recommended) — agreed?
2. Scope of the first pull request: RHF only, with UHF as a second one — agreed?
3. When: now, beside the naphthalene run, or after the supervisor proposal (TASKS 311 step 2)?
4. The `Author:` line and the copyright header follow the neighbours; which name and e-mail address go on the `Author:` line
   is the user's to give.
