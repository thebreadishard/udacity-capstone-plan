# Software changes made in this project — ledger for possible upstream contributions

*Started 2026-09-12 on the user's request: a list of every change we make to third-party software, of every piece of our own code that fills a gap
upstream, and of the findings worth reporting, so that we can decide which to offer as pull requests. One register line per change with a reviewed
status, and one section per line with the full record. Pull requests are submitted only on the user's word; the status column says where each item
stands. Earlier versions of this text are in the git history.*

## Register

One line per change; the numbered section below the register carries every original cell. Status words: **done** = complete, no action required; **pr-open** = submitted upstream, waiting for the maintainers; **waiting-upstream** = nothing to do until an upstream release, then a small action; **pr-candidate** = a pull request or report could be drafted, waits for the user's word; **planned** = decided, not started. Groups: A patch to third-party code · B own layer · C finding · D Lean 4 / Mathlib. (Reshaped 3 October 2026 by `tools/reshape_software_ledger.py`; every original cell is in the sections, verbatim.)

| # | date | group | software | title | status |
|---|---|---|---|---|---|
| 1 | 2026-09-10 | A | pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py`), against pyscf 2.14.0 | the call into pyscf's DF vvvv routine updated to pyscf 2.14's seven-argument signature | done |
| 2 | 2026-09-12 | A | pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py::_cp`) | np.array(a, copy=False, order='C') → np.asarray(a, order='C') | done |
| 3 | 2026-09-12 | B | pyscf-forge LNO-CCSD(T) | CheckpointedLNOCCSD_T | pr-candidate |
| 4 | 2026-09-10/12 | B | (shell) | probes/launch_detached.sh | done |
| 5 | 2026-09-09/10 | B | pyscf-forge LNO (semantics, not code) | frozen-space arms A/B/C and the composite energy in m1_frozen_spaces.py (holding LNO spa… | done |
| 6 | 2026-09-10 | C | PAHdb theoretical library v4.00 as served | the served XML carries the v3.00 scale factors (0.9794/0.9691/0.9597), not the three the… | pr-candidate |
| 7 | 2026-09-12 | C | Hessian QM9 (Williams et al. 2025) | fetch script's expected size was the whole figshare record, not the archive (6,281,831,4… | done |
| 8 | 2026-09-12 | D | Mathlib `v4.34.0-rc2` | exists_proper_on_finset + colorable_maxDegree_succ | pr-candidate |
| 9 | 2026-09-13 | A | PySCFAD 0.3.3 (PyPI 2026-06-29; jax ≥ 0.9.1 < 0.11, pyscfadlib ≥ 0.3.3… | pinned as the engine of milestone M2a (the gradient-to-energy cost ratio g), installed 2… | done |
| 10 | 2026-09-14 | C | pyVPT2 0.1.2 (conda-forge `pyhd8ed1ab_0`, tag 2024-09-10; BSD-3-Clause… | installed in its own environment | pr-candidate |
| 11 | 2026-09-14 | C | pyVPT2 0.1.2 → port to qcelemental 0.51 / pydantic 2 / psi4 1.11 (**co… | inventory of the 2,317-line package | pr-candidate |
| 12 | 2026-09-15 | C | pyscf-forge 1.1.1 `pyscf/lno/test/test_ulnoccsd.py` (the shipped unit … | the shipped test fails on this pyscf | done |
| 13 | 2026-09-15 | B | pyscf-forge 1.1.1 `pyscf/lno/ulnoccsd_t_slow.py` (NumPy/einsum (T) ref… | an unrestricted (T) kernel of the compiled kind for the LNO fragment partition, modelled… | planned |
| 14 | 2026-09-16 | B | pyVPT2 0.1.2 (`pyvpt2/task_base.py`, `AtomicComputer.compute`) | a checkpoint layer (probes/vpt2_checkpoint.py, ≈ 60 lines | pr-candidate |
| 15 | 2026-09-21/22 | B | own package `dpir` (tier 2 of `QUALITY_POLICY.md`) | src/dpir/qff.py (two-route QFF, degenerate-subspace alignment, fixed mode conventions, V… | done |
| 16 | 2026-09-22 | B | own tools | tools/modules_fresh_check.sh (fresh venv + pip install -r requirements.txt + notebook ex… | done |
| 17 | 2026-09-22 | B | own probes around the R0 deck | r0_diagonal_reading.py --harm/--exp (Goodman 1991 / Miani 2000 references from probes/da… | done |
| 18 | 2026-09-23 | B | own scripts of the E6/E7 day (module 05) | m05/e6_learning_curve.py (pre-registered curve, M1–M5, two hold-outs, --exclude-imaginar… | done |
| 19 | 2026-09-23 | B | corpus second route and guards | corpus/analytic_hessians.py (pyscf analytic Hessians beside the psi4 FD files), the sort… | done |
| 20 | 2026-09-30 | B | pyscf 2.14.0 `cc/uccsd_t_rdm.py::_gamma2_intermediates` (UCCSD(T) grad… | install_uccsd_t_dvvvv_fix() in probes/e8_cc_hessian_fd.py | waiting-upstream |
| 21 | 2026-09-29/30 | B | pyscf 2.14.0 `cc/ccsd_t_rdm.py` (T) densities and `cc/ccsd_t_lambda.py… | C kernels t_density_intermediates and t_lambda_intermediates (probes/t_density_kernel/),… | waiting-upstream |
| 22 | 2026-09-30 → 10-03 | A | upstream state of rows 1–2, 20, 21 | rows 1–2 merged upstream as pyscf-forge PR #212 (30 Sep, approved) | waiting-upstream |
| 23 | 2026-10-01 | B | own (module 05 trainer) | m05/rungC_targets.py | done |
| 24 | 2026-10-02 | B | own (E8 probe) | two-route-check {inline,separate,only} | done |
| 25 | 2026-10-02 | B | own (module 05) | m05/rungC_cc_transfer.py (leave-one-anchor-out transfer to CCSD(T) | done |
| 26 | 2026-10-02 | B | own (intensities) | probes/dipole_derivs_fd.py (APT by FD of analytic SCF dipoles, sum rule + two steps | done |
| 27 | 2026-10-03 | B | pyscf 2.14.0 `grad/ccsd.py::grad_elec` (semantics, no upstream file to… | gradient_with_dipole in the E8 probe and probes/cc_dipole_capture.py | waiting-upstream |
| 28 | 2026-10-03 | B | own (design input) | probes/cc_lambda_profile.py (cProfile of solve_lambda | done |
| 29 | 2026-10-02 | C | pyscf-properties 0.1.0 (`pyscf.prop`) | no infrared module in the installed release (magnetizability, nmr, nsr, polarizability, … | done |
| 30 | 2026-10-03 | C | pyscf 2.14.0 `pyscf/lib/CMakeLists.txt` (and forge's copy of the patte… | the pyscf lookup python3 -c "import pyscf | done |
| 31 | 2026-09-29/30 | B | pyscf 2.14.0 `grad/ccsd_t.py`, `grad/uccsd_t.py` (`Gradients.kernel` w… | our E8 probe solves the (T) lambda explicitly (ccsd_t_lambda.kernel) before calling the … | waiting-upstream |
| 32 | 2026-09-30 | B | optking (psi4's optimiser) `linear-bend` cycle handling | our corpus runner optimises molecules with a triple bond in Cartesian coordinates (RETRY… | done |
| 33 | 2026-09-21 → 09-30 | C | pyVPT2 (`philipmnel/pyvpt2`, `quartic.py`) | the two finite-difference routes to the semi-diagonal quartic constants disagree on psi4 FD Hessians | done |
| 34 | 2026-10-03 | C | pyscf (`cc/test/test_uccsdt_highm.py::test_zero_beta_electrons`, Windows CI) | the test fails intermittently on pyscf's Windows wheel job with a NaN in the first DIIS matrix; not reproducible outside that build | done |
| 36 | 2026-10-04 | C | pyscf (`grad/mp2.py::grad_elec`) | the MP2 gradient's AO block size can fall below a shell's size → empty block, ValueError | pr-candidate |
| 35 | 2026-10-04 | C | pyscf (`cc/ccsd_t_rdm.py::_gamma2_outcore`, used by `grad/ccsd_t.py`) | the CCSD(T) gradient's 'outcore' two-particle density is an alias of the in-core one: a dense nvir⁴ dvvvv copied three times (28 GB each for benzene/cc-pVTZ) — our fast path now takes the CCSD part from `ccsd_rdm._gamma2_outcore`; PR candidate | workaround done; PR on the user's word |
| 37 | 2026-10-09 | A | optking 0.5.0 as installed (`v3d.py`, `addIntcos.py`) | the #116 fix applied to the installs made after 30 Sep (pool 3 CPX62, laptop qc env); bootstraps apply it | waiting-upstream |
| 38 | 2026-10-09 | C | pyscf (`grad/ccsd_t.py` + #3477; issue #1272) | CO/cc-pVTZ relaxed CCSD(T) dipole: dip_moment() = finite field = 0.17029 D; Molpro's 0.2135 D is not that energy's field derivative | done |
| 39 | 2026-10-09 | C | optking docs (`devtools/conda-envs/docs.yaml`, Read the Docs) | the docs build fails importing qcelemental under the current pydantic (master's last build 1 June) | done |
| 40 | 2026-10-11 | C | pyscf-properties master 4eee5a43 (`prop/infrared/rhf.py`, `uhf.py`: `proc_hessian_`) | an explicit mo_energy, mo_coeff, mo_occ or h1ao_grad raises ValueError (`x if x else default` on an array) | pr-open |
| 41 | 2026-10-11 | C | pyscf-properties master 4eee5a43 (`prop/infrared/test/test_ir_inten.py`) | a reference-free check of the four infrared classes: analytic APT against finite differences of the dipole (UKS test 'a little bit loose') | pr-open |
| 42 | 2026-10-11 | C | pyscf-properties 0.1.0 on PyPI | the published release has no infrared module; master has had it since June 2022 (row 29) — an issue asking for a release | done |
| 43 | 2026-10-11 | C | pyscf master (`hessian/thermo.py::harmonic_analysis`) | the Hessian goes to `numpy.linalg.eigh` unsymmetrised; eigh reads one triangle, so an asymmetric analytic Hessian (UKS: 6.2e-5) shifts modes and heights | waiting-upstream |
| 44 | 2026-10-12 | C | pyscf 2.14.0 (`lib/linalg_helper.py::krylov`, via `scf/cphf.py solve_withs1` and the Hessian's `solve_mo1`) | the Krylov solver stops 7e-5 off its own system for DFT CPHF, whatever tol/max_cycle, without a warning; dipole derivatives from that solution are off by 1e-4 (benzene), the Hessian is insensitive; our #3508, upstream's #3384 solves it too (#3508 closed for it) | waiting-upstream |
| 45 | 2026-10-13 | C | pyVPT2 main 2eae571 (`FD: HESSIAN`, `assemble_quartic_from_hessians`, `check_cubic` / `check_quartic`) | the consistency checks compare routes that were averaged before the check, so they always pass; one route per element, then the same symmetrisation — philipmnel/pyvpt2#59 | pr-open |
| 46 | 2026-10-13 | C | pyscf 2.14.0 `dft/gen_grid.py` (`Grids.symmetry`, `get_partition`) | the molecular DFT grid is not invariant under the molecule's point group (one lab-frame Lebedev orientation for every atom); `Grids.symmetry` is documented 'whether to symmetrize mesh grids (TODO)' — a symmetry-adapted orientation per atom orbit would fill it | pr-candidate |
| 47 | 2026-10-14 | B | pyscf-properties master (`prop/infrared`: RHF/UHF/RKS/UKS only) | a CCSD(T) atomic polar tensor by finite field — central differences of the CCSD(T) gradient in ±F along x, y, z, with the field's core-Hamiltonian derivative in the gradient; our `probes/cc_apt_field.py` + `apt_field_route.field_hcore_generator` + `cc_dipole_capture` | pr-candidate |
| 48 | 2026-10-18 | C | pyVPT2 main 2eae571 (`fermi_solver.py`: `fermi_solver`, `Polyad.solve`) | GVPT2 on S2's molecules: an interaction that connects two polyads is added to both and never merged (7 of 14 molecules), and the eigenvalue-to-state map (argmax per eigenvector) raises KeyError when two eigenvectors peak on one state; merge the polyads, assign one-to-one by largest remaining overlap — issue philipmnel/pyvpt2#60, PR philipmnel/pyvpt2#61 (branch `polyad-assignment-and-merge`, eb353ab; our S2 GVPT2 labels run on it, solver sha256 recorded) | pr-open |
| 49 | 2026-10-18 | C | dxtb 0.4.0 / main 2070660 (`setup.cfg` exact pins tad-mctc==0.7.0, tad-dftd3==0.6.0, tad-dftd4==0.8.0, tad-multicharge==0.5.0) | the pins hold numpy < 2 (tad-mctc 0.7.0 requires it), so dxtb cannot share an environment with numpy 2 (our laptop Python: numpy 2.5, Python 3.14). The newer tad set agrees on tad-mctc 0.8.0 (no numpy pin): tad-dftd3 0.7.0, tad-multicharge 0.6.0, tad-dftd4 `main` (unreleased; PyPI 0.8.0 still pins tad-mctc 0.7.0). Trial env `dxtb-np2` (WSL, numpy 2.5.4, torch 2.14.1): one API break — tad-dftd3 0.7.0's `atomic_c6` takes no `chunk_size` (dxtb `classicals/dispersion/d3.py`); with that line changed, test_classical 441 passed, test_coulomb 210 passed, test_singlepoint 262 passed (one file over the 140 s window, no failure); the other test groups not run yet. PR = the four pins + the d3.py line, after a tad-dftd4 release on tad-mctc 0.8.0 (issue there first) | pr-candidate |
| 50 | 2026-10-18 | C | dxtb 0.4.0 / main 2070660 (`calculators/types/decorators.py`, `requires_positions_grad`) | a new positions tensor with equal values (after `energy()`, or a second `forces()`) reused the classical, interaction and integral caches built for another tensor or without a graph, so autograd forces missed their terms (water GFN2 z(O) +0.0755 against −0.0030, GFN1 too); clear those caches when the tensor changes — issue grimme-lab/dxtb#277, PR grimme-lab/dxtb#278 (fork thebreadishard/dxtb, branch `reset-caches-new-positions`, 3cda67e; regression test 6 cases fail on main, pass on the branch; 141 other tests pass). Our S2 xtb path never depended on it (a fresh calculator per quantity) | pr-open |
| 51 | 2026-10-19 | C | pyscf 2.14.0 / master 3d8a52be8 (`hessian/rhf.py`, `hessian/uhf.py`: `solve_mo1`, `gen_hop`) | the logger `solve_mo1` receives (and gen_hop's own) is not passed to `cphf.solve` / `ucphf.solve`, so the CPHF (Krylov) iterations of an analytic Hessian are never logged at any verbosity — the long silent stretch of our large Hessians (found switching on pyscf's own log, `probes/library_log.py`, TASKS 79); pass `verbose=log` — issue pyscf/pyscf#3530, PR pyscf/pyscf#3531 (fork thebreadishard/pyscf, branch `hessian-cphf-logger`, 3342c336c; two new tests fail on master and pass on the branch; test_rhf.py and test_uhf.py 12 passed). Until released our CPHF stretches stay silent; liveness from CPU time | pr-open |

## Sections

### 1 — the call into pyscf's DF vvvv routine updated to pyscf 2.14's seven-argument signature

**Group:** A, patch to third-party code. **Date:** 2026-09-10. **Status:** done. *Status note (3 Oct 2026):* the cell still says 'PR candidate: yes'; it was merged upstream as pyscf-forge #212 on 30 Sep 2026 (row 22) — nothing left to do.

**Software:** pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py`), against pyscf 2.14.0

**Change:** the call into pyscf's DF `vvvv` routine updated to pyscf 2.14's seven-argument signature

**Why:** pyscf 2.14 changed the signature; pyscf-forge 1.1.1 still calls the old one and crashes on every DF-LNO run

**Files:** `probes/patches/apply_pyscf_forge_dfvvvv_patch.py`, `pyscf_forge_1.1.1_lnoccsd_dfvvvv_pyscf2.14.patch`

**PR candidate:** **yes** — a plain compatibility fix; check first whether pyscf-forge `master` already has it (it may, if they track pyscf releases)

### 2 — np.array(a, copy=False, order='C') → np.asarray(a, order='C')

**Group:** A, patch to third-party code. **Date:** 2026-09-12. **Status:** done. *Status note (3 Oct 2026):* the cell still says 'PR candidate: yes'; merged upstream as pyscf-forge #212 on 30 Sep 2026 (row 22) — nothing left to do.

**Software:** pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py::_cp`)

**Change:** `np.array(a, copy=False, order='C')` → `np.asarray(a, order='C')`

**Why:** under NumPy 2, `copy=False` raises when a copy is unavoidable — it is, when the fragment's Lov block is an h5py slice on disk (`max_memory` below its size); the out-of-core path was dead under NumPy 2

**Files:** `probes/patches/apply_pyscf_forge_numpy2_cp_patch.py`, `pyscf_forge_1.1.1_lnoccsd_numpy2_cp.patch`

**PR candidate:** **yes** — the NumPy migration guide's prescribed fix; one line; likely unknown upstream because it only triggers out of core

### 3 — CheckpointedLNOCCSD_T

**Group:** B, own layer around third-party code. **Date:** 2026-09-12. **Status:** pr-candidate. *Status note (3 Oct 2026):* a proposal upstream (a `chkfile` attribute on the LNO kernel) is possible and was never sent; it waits for the user's word.

**Software:** pyscf-forge LNO-CCSD(T)

**What we built:** `CheckpointedLNOCCSD_T`: per-fragment JSON checkpoint written after each fragment's solve; restored fragments are returned without solving on a resumed run; localised orbitals saved/reloaded so the fragments are identical

**Gap it fills:** upstream `lno.py` has "[ ] chkfile / restart" on its own TODO list (line 53); we lost a 3.5-hour run to a host crash

**Files:** `probes/lno_checkpoint.py`; used by `anchor_single_point_timing.py --resume` (tested exact on benzene cc-pVDZ, 2026-09-12 16:46) and, since the same evening, by `m1_frozen_spaces.py` (both arms; one checkpoint per point and arm under `fragments/`, per-point localisations cached; **built, untested** — smoke test on the benzene cc-pVDZ chain owed after the naphthalene timing)

**PR candidate:** **yes, as a proposal** — the natural upstream form is a `chkfile` attribute on the kernel; ours is a subclass, which upstream would rewrite; the value is the design and the test

### 4 — probes/launch_detached.sh

**Group:** B, own layer around third-party code. **Date:** 2026-09-10/12. **Status:** done.

**Software:** (shell)

**What we built:** `probes/launch_detached.sh`: setsid/nohup launcher with an hourly heartbeat line (elapsed, CPU, RSS, scratch size)

**Gap it fills:** none upstream; project tooling

**Files:** `probes/launch_detached.sh`

**PR candidate:** no

### 5 — frozen-space arms A/B/C and the composite energy in m1_frozen_spaces.py (holding LNO spa…

**Group:** B, own layer around third-party code. **Date:** 2026-09-09/10. **Status:** done. *Status note (3 Oct 2026):* no pull request intended; a paper or example later — nothing pending in this ledger.

**Software:** pyscf-forge LNO (semantics, not code)

**What we built:** frozen-space arms A/B/C and the composite energy in `m1_frozen_spaces.py` (holding LNO spaces fixed across geometries, semicanonicalisation at each geometry, transported orbital blocks)

**Gap it fills:** a research object of plan 05, not a fix

**Files:** `probes/m1_frozen_spaces.py`

**PR candidate:** not as a PR; possibly as a paper/example later

### 6 — the served XML carries the v3.00 scale factors (0.9794/0.9691/0.9597), not the three the…

**Group:** C, finding about third-party software. **Date:** 2026-09-10. **Status:** pr-candidate. *Status note (3 Oct 2026):* a question to the PAHdb maintainers is still to be asked (item on the user's list).

**Software:** PAHdb theoretical library v4.00 as served

**Finding:** the served XML carries the v3.00 scale factors (0.9794/0.9691/0.9597), not the three the v4.00 paper describes

**Where recorded:** `modules/02_opponent_atlas/REPORT.md`; plan 05 decision 30

**Action:** ask the PAHdb maintainers when the module is submitted (item on the user's list, not done)

### 7 — fetch script's expected size was the whole figshare record, not the archive (6,281,831,4…

**Group:** C, finding about third-party software. **Date:** 2026-09-12. **Status:** done.

**Software:** Hessian QM9 (Williams et al. 2025)

**Finding:** fetch script's expected size was the whole figshare record, not the archive (6,281,831,499 B); frequencies column 1 is the imaginary magnitude; translation/rotation modes not projected

**Where recorded:** `modules/05_support_predictor/out/HESSIAN_QM9_SUMMARY.md`

**Action:** none needed (documentation notes, not bugs)

### 8 — exists_proper_on_finset + colorable_maxDegree_succ

**Group:** D, Lean 4 / Mathlib. **Date:** 2026-09-12. **Status:** pr-candidate.

**Software:** Mathlib `v4.34.0-rc2`

**What we proved / built:** `exists_proper_on_finset` + `colorable_maxDegree_succ`: a finite simple graph with maximum degree Δ is (Δ+1)-colourable (greedy bound)

**Gap upstream:** Loogle on 2026-09-12: no declaration mentions both `SimpleGraph.Colorable` and `SimpleGraph.maxDegree`; `Coloring/Vertex.lean` has no degree bound, no greedy colouring, no Brooks

**Files:** `plans/06_…/lean/Plan06/T1/MeasurementAlgebra.lean`

**PR candidate:** **yes** — small, general, in Mathlib style already; would go to `Mathlib/Combinatorics/SimpleGraph/Coloring/` after re-checking `master` (Mathlib moves fast); the rest of T1 (patterns, probes, symmetric consistency) is project-specific and stays here

### 9 — pinned as the engine of milestone M2a (the gradient-to-energy cost ratio g), installed 2…

**Group:** A, patch to third-party code. **Date:** 2026-09-13. **Status:** done. *Status note (3 Oct 2026):* adopted as is; nothing to send unless our use needs a patch.

**Software:** PySCFAD 0.3.3 (PyPI 2026-06-29; jax ≥ 0.9.1 < 0.11, pyscfadlib ≥ 0.3.3, pyscf ≥ 2.3, pyscf-properties; Apache-2.0)

**Change:** **adopted, not changed**: pinned as the engine of milestone M2a (the gradient-to-energy cost ratio g), **installed 2026-09-13 ≈ 01:10 with the user's permission** in the separate WSL env `~/qcad` (Python 3.12.14 from qc05's base; `pip install --only-binary=:all:`, low priority, beside the running anchor job): jax 0.10.2, jaxlib 0.10.2, pyscf 2.14.0, pyscfad 0.3.3, pyscfadlib 0.3.3, ml_dtypes 0.6.0; `pyscf-properties 0.1.0` from its pure-Python sdist (79 kB, no wheel on PyPI); 894 MB; `qc05` untouched; `pyscfad.lno` exports `LNOMP2`, `LNOCCSD`, `LNOCCSD_T`

**Why:** the evidence ladder's step 4: no paper prints g; decision 34's substitution layer, X11 and mode G all hang on it

**Files:** `notes/PreRegistration_2026-09-13_M2a_Gradient_Cost_Ratio.md`, `probes/m2a_gradient_cost_ratio.py`

**PR candidate:** none yet; a PR candidate only if the LNO threshold convention or the checkpointing needs a patch for our use

### 10 — installed in its own environment

**Group:** C, finding about third-party software. **Date:** 2026-09-14. **Status:** pr-candidate.

**Software:** pyVPT2 0.1.2 (conda-forge `pyhd8ed1ab_0`, tag 2024-09-10; BSD-3-Clause; upstream `main` last commit 2026-05-16)

**What:** **not changed; installed in its own environment.** 0.1.2 and `main` use pydantic-1-era qcelemental API (`qcel.models.ProtoModel.Config`, `qcel.models.molecule.GEOMETRY_NOISE`, `@validator`, `conlist(min_items=)`), which qcelemental ≥ 0.50 (the pydantic-2 rewrite) no longer provides; the conda recipe pins nothing, so `conda install pyvpt2` into an environment with qcelemental 0.51 / psi4 1.11 installs cleanly and fails at import. A driver-side shim (presenting `qcelemental.models.v1` as `qcelemental.models`) breaks psi4 1.11's own import. Working route: environment `vpt2` = pyvpt2 0.1.2 + qcelemental 0.30.1 + qcengine 0.34.2 + psi4 1.10.2 + pydantic 2.13.5 (116 MB), **plus libxc-c pinned to 7.0.0**, because psi4 1.10.2's conda build fails at import with libxc-c 7.1.2 ("Could not find required LibXC functional", XC_GGA_XC_TH_FL) — a second conda-forge packaging fault. Self-test: water B3LYP/6-31G*, harmonic 1683.6 / 3871.0 / 3997.7 → VPT2 1631.6 / 3701.2 / 3809.5 cm⁻¹, no Fermi resonance, harmonic intensities returned (`probes/results_vpt2/`).

**Why:** the anharmonic step of plan 05 (ideas I6, I11, I13) needs VPT2 positions on psi4 Hessians

**Files / where:** conda environment `vpt2` (outside the repo); nothing in the repo changed

**Action:** **two upstream reports**: (a) pyVPT2 issue: incompatible with qcelemental ≥ 0.50 — pin `qcelemental <0.50` in the recipe or port the code; (b) conda-forge psi4 feedstock: the 1.10.2 build against libxc-c 7.1.2 lacks TH_FL

### 11 — inventory of the 2,317-line package

**Group:** C, finding about third-party software. **Date:** 2026-09-14. **Status:** pr-candidate.

**Software:** pyVPT2 0.1.2 → port to qcelemental 0.51 / pydantic 2 / psi4 1.11 (**cost estimate on the user's question of 16:4x; not done**)

**What:** inventory of the 2,317-line package: `schema.py` (VPTInput/VPTResult — `Field` fine; `conlist(min_items=1)` → `min_length=1`), `task_base.py` (`class Config(ProtoModel.Config)` ×2 → `model_config = ConfigDict(...)`; `@validator` ×3 → `@field_validator`; `.dict()` ×2 still work with a deprecation warning; `qcel.models.molecule.GEOMETRY_NOISE = 13` → set on `qcelemental.models.v1.molecule` and `.v2.molecule`; `qcng.compute(..., task_config=)` unchanged in 0.51), `quartic.py` (`@validator` ×2); the qcportal branches are optional imports and stay. Every imported name still exists in qcelemental 0.51 (`models.types.Array`, `basemodels.ProtoModel`, `procedures.QCInputSpecification`, `common_models.Model`). **Estimate: about 30 changed lines in three files; one desk-day including the shipped test suite (11 files: h2o, hcn, hf, h2co, Fermi solver, polyad, multilevel, cbs, qcng) and an acceptance test against the `vpt2` environment's water and benzene numbers to 0.01 cm⁻¹; risk: pydantic-1 behaviour hidden in the results dataclass (upstream issues 26 and 28 of 2023 touched it once).** Value: one environment — psi4 1.11 for the corpus and the anharmonic step alike, no 1.10.2 / 1.11 mixing — and a PR upstream (CI last ran 2025-08-04, green on the pins of that day; nothing open on pydantic; one open issue, #46 linear degeneracies).

**Why:** asked by the user 2026-09-14

**Files / where:** would touch `pyvpt2/schema.py`, `task_base.py`, `quartic.py` in a fork

**Action:** **yes, a clean PR candidate**; do it if the 1.10.2 / 1.11 split proves to matter for the anharmonic step, or if upstream does not answer the issue report

### 12 — the shipped test fails on this pyscf

**Group:** C, finding about third-party software. **Date:** 2026-09-15. **Status:** done. *Status note (3 Oct 2026):* fixed on upstream master on 26 Jul 2026 (forge #199, 'compatibility with PySCF v2.14.0': the tests now unpack `stability_jacobi(return_status=True)` in pyscf 2.14's order); the 1.1.1 release predates it — nothing to send.

**Software:** pyscf-forge 1.1.1 `pyscf/lno/test/test_ulnoccsd.py` (the shipped unit test of `ULNOCCSD_T`) against pyscf 2.14.0

**Finding:** **the shipped test fails on this pyscf** — it unpacks `PipekMezey.stability_jacobi()` as `(stable, mo_coeff)`, while pyscf 2.14's `pipek_stability_jacobi` returns `mo_coeff` (or `(mo_coeff, stable)` with `return_status=True`): `ValueError: too many values to unpack (expected 2)` after 3.8 s, before any LNO code runs; the `ULNOCCSD_T` class itself is unaffected (our own CH₃ check in `probes/m4_cation_timing.py` uses `return_status=True`). Same-day rule: found 13:55, recorded 14:0x

**Where recorded:** `probes/results_m4/smoke_2026-09-15_attempt1_failed.log`, `probes/m4_cation_timing.py` (comment at `pm_localise`)

**Action:** a two-line upstream fix in the test (and in the module's `__main__` example if it shares the idiom); **not sent** — the user decides on upstream reports; until then the test is not evidence for or against `ULNOCCSD_T`, our CH₃ comparison against canonical UCCSD(T) is

### 13 — an unrestricted (T) kernel of the compiled kind for the LNO fragment partition, modelled…

**Group:** B, own layer around third-party code. **Date:** 2026-09-15. **Status:** planned. *Status note (3 Oct 2026):* decided (decision 41) and not started; once built and passing it becomes a pr-candidate.

**Software:** pyscf-forge 1.1.1 `pyscf/lno/ulnoccsd_t_slow.py` (NumPy/einsum (T) reference kernel of `ULNOCCSD_T`)

**What we built:** **decided (decision 41), not started:** an unrestricted (T) kernel of the compiled kind for the LNO fragment partition, modelled on PySCF's compiled restricted kernel; acceptance: benzene⁺ energy equal to the slow kernel's to 1e-8 E_h on identical fragments, time ≤ 1.5 × the restricted compiled (T) of the neutral, CH₃ vs canonical UCCSD(T) unchanged

**Gap it fills:** measured 2026-09-15: the slow kernel is 3,832 s of the 5,096 s benzene⁺ energy (c = 31 → ≈ 8–9 with the port); without it no cation deck fits the laptop

**Files:** `probes/m4_cation_timing.py`, `probes/results_m4/`, P27 §5

**PR candidate:** yes, once it passes — the user decides whether and when to offer it upstream

### 14 — a checkpoint layer (probes/vpt2_checkpoint.py, ≈ 60 lines

**Group:** B, own layer around third-party code. **Date:** 2026-09-16. **Status:** pr-candidate.

**Software:** pyVPT2 0.1.2 (`pyvpt2/task_base.py`, `AtomicComputer.compute`)

**What we built:** **built and tested: a checkpoint layer** (`probes/vpt2_checkpoint.py`, ≈ 60 lines; installed at run time by `vpt2_benzene.py`, the package untouched): every QC task's AtomicInput (driver, model, keywords, molecule geometry rounded to 1e-6 bohr with −0.0 → 0.0) is hashed; a stored AtomicResult is reloaded (its untyped `extras["qcvars"]` lists restored to 2-D arrays, which psi4's `set_variable` needs) and the task skipped, otherwise the task runs and its result is written atomically; the optimised reference geometry is cached too so a rerun uses the same reference. **Tests (water, B3LYP/6-31G*, 7 tasks):** all-hits rerun bit-identical to the original table (twice: runs 7 and A2); 3 of 7 tasks deleted → exactly 4 hits + 3 computed; two bugs found on the way and fixed (keys unstable through −0.0 on symmetry-zero coordinates; lists instead of arrays after the JSON round trip). **Measured beside it:** psi4 1.10.2's own run-to-run noise of the finite-difference DFT Hessians is **0.1 cm⁻¹ on the VPT2 ν** at 4 threads (two fresh runs, same geometry, no cache) — the cache never adds to it, a recomputed task carries that noise as any run would

**Gap it fills:** a Windows Update restart on 16 Sep 02:32 lost a 9 h benzene run; pyVPT2 keeps results only in memory and offers restart only through a QCFractal server

**Files:** `probes/vpt2_checkpoint.py`, `probes/vpt2_benzene.py`, `probes/results_vpt2/water_*.log`

**PR candidate:** possible: a `cache_dir` option in `AtomicComputer.compute`; the user decides whether and when

### 15 — src/dpir/qff.py (two-route QFF, degenerate-subspace alignment, fixed mode conventions, V…

**Group:** B, own layer around third-party code. **Date:** 2026-09-21/22. **Status:** done.

**Software:** own package `dpir` (tier 2 of `QUALITY_POLICY.md`)

**What we built:** `src/dpir/qff.py` (two-route QFF, degenerate-subspace alignment, fixed mode conventions, VPT2) and `provenance.py`; 26 tests (`tests/`: model quartic potential, Morse, H₂, water vs pyVPT2 to 1e-5, benzene T2 pin), CI `.github/workflows/plan05-ci.yml`, pre-commit hooks; second-reader review recorded

**Gap it fills:** the probe's numbers become reproducible on any machine (Linux ≠ Windows mode conventions caught by the first CI run)

**Files:** `plans/05_delta-probed-ir-pipeline/src`, `tests`, `pyproject.toml`, `.pre-commit-config.yaml`

**PR candidate:** no (ours)

### 16 — tools/modules_fresh_check.sh (fresh venv + pip install -r requirements.txt + notebook ex…

**Group:** B, own layer around third-party code. **Date:** 2026-09-22. **Status:** done.

**Software:** own tools

**What we built:** `tools/modules_fresh_check.sh` (fresh venv + `pip install -r requirements.txt` + notebook executed per module; found module 02's missing 51 MB input), `tools/sync_architecture_md.py` (ARCHITECTURE.md fences = sheet files, `--check`), `tools/check_staged_paths.py` (pre-commit path guard), `tools/stamp.py`

**Gap it fills:** the guards of the incident table of `QUALITY_POLICY.md`

**Files:** `plans/05_delta-probed-ir-pipeline/tools/`

**PR candidate:** no (ours)

### 17 — r0_diagonal_reading.py --harm/--exp (Goodman 1991 / Miani 2000 references from probes/da…

**Group:** B, own layer around third-party code. **Date:** 2026-09-22. **Status:** done.

**Software:** own probes around the R0 deck

**What we built:** `r0_diagonal_reading.py --harm/--exp` (Goodman 1991 / Miani 2000 references from `probes/data/benzene_benchmark_goodman1991_miani2000.json`), `r0_convention_check.py`, `r0_geometry_check*.py` (the geometry term, decision 48), `r0_table_2026-09-28.py`, `benzene_benchmark_map.py`

**Gap it fills:** the reading of the deck validated independently; the geometry term found and predicted

**Files:** `probes/`

**PR candidate:** no (ours)

### 18 — m05/e6_learning_curve.py (pre-registered curve, M1–M5, two hold-outs, --exclude-imaginar…

**Group:** B, own layer around third-party code. **Date:** 2026-09-23. **Status:** done.

**Software:** own scripts of the E6/E7 day (module 05)

**What we built:** `m05/e6_learning_curve.py` (pre-registered curve, M1–M5, two hold-outs, `--exclude-imaginary`), `e7_t1_sign_test.py`, `e7_t2_sqm.py` (SQM scale factors in geomeTRIC primitives), `e7_t2_posthoc.py`, `e7_t2_ceilings.py` (parameter-free locality projections), `e7_rungB_pairs.py` (pairwise local target, MLP + GBT, `--use-analytic`), `e7_rungB_diag_a.py`, `e7_rungB_reread_analytic.py`

**Gap it fills:** the couplings learned once the target is local (decision 49); every number of the demonstration note and blog post 11

**Files:** `plans/05_delta-probed-ir-pipeline/modules/05_support_predictor/m05/`

**PR candidate:** no (ours)

### 19 — corpus/analytic_hessians.py (pyscf analytic Hessians beside the psi4 FD files), the sort…

**Group:** B, own layer around third-party code. **Date:** 2026-09-23. **Status:** done.

**Software:** corpus second route and guards

**What we built:** `corpus/analytic_hessians.py` (pyscf analytic Hessians beside the psi4 FD files), the sorted-pair shift screen in `corpus/check_results.py`, `corpus/fd_grid_test_benzene.py` (mechanism: psi4 default grid 75/302 × 0.005 bohr step), `m05/build_release.py --prefer-analytic`; E8 scripts `probes/e8_cc_hessian_fd.py` (checkpointed FD CCSD(T) Hessian) and `probes/e8_cc_locality.py`

**Gap it fills:** benzene's corrupted target found and replaced (decision 50); E8 running

**Files:** `modules/05_support_predictor/corpus/`, `probes/`

**PR candidate:** no (ours)

### 20 — install_uccsd_t_dvvvv_fix() in probes/e8_cc_hessian_fd.py

**Group:** B, own layer around third-party code. **Date:** 2026-09-30. **Status:** waiting-upstream. *Status note (3 Oct 2026):* the fix exists upstream (pyscf #3387); our wrapper is dropped when a release carries it — the only action left, and it waits for upstream.

**Software:** pyscf 2.14.0 `cc/uccsd_t_rdm.py::_gamma2_intermediates` (UCCSD(T) gradient)

**What we built:** `install_uccsd_t_dvvvv_fix()` in `probes/e8_cc_hessian_fd.py`: wraps the function, takes the uncompressed blocks and compresses vvvv/vvVV/VVVV itself with the ½

**Gap it fills:** v2.14.0 drops the ½ on the mixed-spin `dvvVV` block in the `compress_vvvv` branch → UCCSD(T) gradient 4.9e-3 a.u. off dE/dx (H2O⁺); after: 1.5e-7; found by gate 1

**Files:** `probes/e8_cc_hessian_fd.py`, `probes/results_m1/gate1_water_2026-09-30/`

**PR candidate:** **no — fixed upstream** (pyscf#3305, PR #3387, `aa2ad208`, 9 Aug 2026; test `grad/test/test_uccsd_t.py`); drop the wrapper once a release carries it

### 21 — C kernels t_density_intermediates and t_lambda_intermediates (probes/t_density_kernel/),…

**Group:** B, own layer around third-party code. **Date:** 2026-09-29/30. **Status:** waiting-upstream. *Status note (20:1x 9 Oct 2026):* **#3470 merged 6 Oct** (pyscf master); our `probes/t_density_kernel/` stays until the next pyscf release, then the rebuild drops it.

**Software:** pyscf 2.14.0 `cc/ccsd_t_rdm.py` (T) densities and `cc/ccsd_t_lambda.py::make_intermediates`

**What we built:** C kernels `t_density_intermediates` and `t_lambda_intermediates` (`probes/t_density_kernel/`), swapped in by `t_density_fast.install()` / `install_lambda()`, each with a two-route check against pyscf's Python

**Gap it fills:** pyscf's (T) gradient spends its time in blocked `lib.einsum` over six-index blocks and keeps ≈ 3.4 of 16 cores busy; per-triple C with thread-private nocc³ buffers: density water 4e-18, lambda water 3e-18 / benzene 1e-16 and 44 s vs 373 s

**Files:** `probes/t_density_kernel/`, `tests/test_t_density_kernel.py`, `tests/test_e8_fast_t_*.py`

**PR candidate:** **submitted: pyscf/pyscf#3470** (30 Sep 2026; upstream master was unchanged in these files, no open PR)

### 22 — rows 1–2 merged upstream as pyscf-forge PR #212 (30 Sep, approved)

**Group:** A, patch to third-party code. **Date:** 2026-09-30 → 10-09. **Status:** waiting-upstream. *Status note (21:2x 13 Oct 2026):* optking #116 merged 13 Oct 21:07 (row 32); of the pull requests of this row only releases are awaited now. *Status note (20:1x 9 Oct 2026):* #212 merged 30 Sep, #3469 and #3470 merged 6 Oct; #3477 approved (row 27), forge #213 and optking #116 open (rows 30, 32). *Planned (3 Oct 2026):* at the next environment rebuild pin pyscf-forge to master ≥ 1f1b65f (rows 1–2 become upstream code) and install pyscf-properties from master for its `infrared` module as a second route beside our CPHF APT; pyscf-core stays on our kernel branch until #3469/#3470 are merged. *Status note (3 Oct 2026):* the state row: #212 merged, #213 (reworked 3 Oct, replied), pyscf #3469 and #3470, optking #116 open — all waiting for maintainers.

**Software:** upstream state of rows 1–2, 20, 21

**Change:** **rows 1–2 merged upstream** as pyscf-forge PR #212 (30 Sep, approved): on forge master ≥ 1f1b65f the two patches are no longer needed (our clone's `lno-pyscf214-compat` branch is upstream). Row 20's fix is pyscf #3305/#3387 (upstream after 2.14.0; our wrapper stays until the next release). Row 21's kernels: pyscf PR #3470 (opened 30 Sep, CI green on all platforms, no review yet); the lambda fallback fix: pyscf PR #3469 (same). forge PR #213 (build: pyscf lookup with the build interpreter) reworked 3 Oct along the maintainer's review and replied to on the user's word. optking PR #116 (linear-bend cycle guard, 30 Sep) open, no CI there.

**Why:** —

**Files:** `PR_Drafts_2026-09-21_Upstream_Fixes.md`, `PR_Draft_2026-09-30_optking_linear_bend_cycle_guard.md`

**PR candidate:** #212 merged (30 Sep); #3469, #3470 merged (6 Oct); #213 merged (9 Oct); #3477 merged (12 Oct); optking #116 approved twice by psi-rking, who pushed CI fixes to it (22:4x, 12 Oct), open

### 23 — m05/rungC_targets.py

**Group:** B, own layer around third-party code. **Date:** 2026-10-01. **Status:** done.

**Software:** own (module 05 trainer)

**What we built:** `m05/rungC_targets.py`: the ridge-anchored least-squares internal-coordinate target (Wilson G, Cholesky, `PINV_RCOND`, `SCALE_LIMIT` store guard, sha-keyed cache); patterns d/e/f (`PATTERN_REACH`) in the pair model; `--aux both`, `--kring-weight`, `--kdiag-weight` in `rungC_train.py`

**Gap it fills:** the 0.4 floor was the pattern term's target and support (investigation log 1 Oct)

**Files:** `m05/rungC_targets.py`, `m05/e7_rungB_pairs.py`, `m05/rungC_train.py`, tests `test_rungC_targets.py`, `test_rungB_target_switch.py`

**PR candidate:** no

### 24 — two-route-check {inline,separate,only}

**Group:** B, own layer around third-party code. **Date:** 2026-10-02. **Status:** done.

**Software:** own (E8 probe)

**What we built:** `--two-route-check {inline,separate,only}`: the (T)-kernel comparisons against pyscf's slow route run in a lane beside the production lanes; the assembly refuses an unchecked reference without a passing `two_route_check.json`

**Gap it fills:** anthracene's reference would otherwise have carried the slow route serially

**Files:** `probes/e8_cc_hessian_fd.py`, `probes/run_anchors_hel23_parallel.sh`, `tests/test_e8_two_route_separate.py`

**PR candidate:** no

### 25 — m05/rungC_cc_transfer.py (leave-one-anchor-out transfer to CCSD(T)

**Group:** B, own layer around third-party code. **Date:** 2026-10-02. **Status:** done.

**Software:** own (module 05)

**What we built:** `m05/rungC_cc_transfer.py` (leave-one-anchor-out transfer to CCSD(T): `substitute_cc`, α / head / L2-head / rank-r adapter fine-tunes, per-family ω), `rungC_train.py --save-model` + `load_hybrid_model` + `freeze_for_transfer` + `molecule_tensors` + `load_corpus` + `record_paths` + `--exclude-ids-file`; `probes/rungC_error_map.py`; `probes/rungC_eval_saved.py`

**Gap it fills:** T3, the error map, the coverage ablations

**Files:** the files named; tests `test_rungC_cc_transfer.py` (10)

**PR candidate:** no

### 26 — probes/dipole_derivs_fd.py (APT by FD of analytic SCF dipoles, sum rule + two steps

**Group:** B, own layer around third-party code. **Date:** 2026-10-02. **Status:** done. *Status note (3 Oct 2026):* pyscf-properties' upstream master carries an `infrared` module (rhf/rks/uhf/uks); the installed 0.1.0 predates it — nothing to offer; our CPHF APT is cross-checked against it (3 Oct, water B3LYP/6-31G*: max difference 7e-12 e, intensities identical to 0.01 km/mol) - a third route beside the FD APT and the sum rule.

**Software:** own (intensities)

**What we built:** `probes/dipole_derivs_fd.py` (APT by FD of analytic SCF dipoles, sum rule + two steps; `conv_tol_grad` 1e-8 after the seeded-SCF incident), `probes/dipole_derivs_cphf.py` (APT from `hessian.rhf` `make_h1`/`solve_mo1` + `int1e_irp`; water 1.3e-5 vs FD, 7 s vs 108 s; sum-rule limit 5e-4 set by benzene's two-route measurement), `m05/rungC_intensities.py` (double-harmonic intensities, Lorentzian spectra, overlap, weighted relative error) wired into the trainer's read-outs

**Gap it fills:** lever 5

**Files:** the files named; tests `test_rungC_intensities.py`

**PR candidate:** pyscf-properties lacks an `infrared` module in 0.1.0 — a CPHF APT could be offered there (not drafted)

### 27 — gradient_with_dipole in the E8 probe and probes/cc_dipole_capture.py

**Group:** B, own layer around third-party code. **Date:** 2026-10-03. **Status:** waiting-upstream — *status note (12 Oct 22:4x):* **#3477 merged into pyscf master by sunqm, 12 Oct 19:11 UTC.** Our capture (`gradient_with_dipole`) stays until a release carries `Gradients.dip_moment()`; the upgrade checklist then swaps it for the upstream call with a two-route check on water. *Status note (20:1x 9 Oct 2026):* **approved by sunqm 6 Oct**, CI green, awaiting merge; jeanwsr's question (does it fix #1272?) answered 9 Oct on the user's word (row 38). — **submitted 3 Oct 10:33 as pyscf/pyscf#3477** on the user's word ("Akkoord op PR-kandidaat 27, post maar"). *CI, 3 Oct 11:5x–12:0x:* the first run failed four builds (linux 3.8/3.12, macOS, windows wheel) on test order, not on the code: `test_ccsd_t_grad` moves the O atom of the module-level `mol` in place, so the (T) dipole test, run after it, built eris from a stale `mf` and tripped the canonical-HF check (reproduced locally: alone pass, whole file fail). Fix f092234 pushed 12:02: both dipole tests build their own molecule and RHF; the two files pass in full locally (10 tests, 185 s). *CI after the fix, 16:2x:* 8 of 9 checks green (both Linux builds, macOS, aarch64, multithread, three style checks). The Windows-wheel job fails on `pyscf/cc/test/test_uccsdt_highm.py::test_zero_beta_electrons` (ValueError: NaNs) — a test outside our four files that also failed on three other pull requests' Windows runs this week (runs 37070358945, 36986042296, 36868472041); our branch sits on current master. No action from our side; a maintainer can rerun the job. The CI note was posted on the PR at 16:36 on the user's word (issuecomment-5970157506). *Prepared 3 Oct 10:1x:* branch `ccsd-grad-relaxed-dm1` on the fork (commit 06468d3, on upstream master) — `cc_grad.rdm1_relaxed` kept by `grad_elec`, `Gradients.dip_moment()`, the (T) gradient calls `grad_elec` on the caller's object; tests water/6-31G against finite field (CCSD and CCSD(T), 4e-8); not opened, waits for the user's word.

**Software:** pyscf 2.14.0 `grad/ccsd.py::grad_elec` (semantics, no upstream file touched)

**What we built:** `gradient_with_dipole` in the E8 probe and `probes/cc_dipole_capture.py`: the fully relaxed CCSD(T) one-particle density is recorded from grad_elec's own `get_veff(mol, dm1 + dm1.T)` call (the last of its get_veff calls) and turned into the dipole; validated against the finite-field derivative on water (6.1e-8 / 1.0e-7 a.u.; gate 1 `check_dipole_capture`); the probe stores `dipole` with the reference and `dip_<k>_<sign>.npy` per displacement; `e8_symmetry.reconstruct_apt` / `apt_self_check` (vector ⊗ vector) and the assembly's `apt_ccsd_t.npz`

**Gap it fills:** CC-level intensities without extra compute

**Files:** `probes/e8_cc_hessian_fd.py`, `probes/e8_symmetry.py`, `probes/cc_dipole_capture.py`, tests `test_e8_symmetry_apt.py`, `test_acceptance_water.py`

**PR candidate:** **candidate:** pyscf's `grad_elec` could return or expose the relaxed dm1 (and `Gradients` a `dip_moment`), as the SCF gradient classes do — one line, saves every CC dipole derivative a second solve; not drafted

### 28 — probes/cc_lambda_profile.py (cProfile of solve_lambda

**Group:** B, own layer around third-party code. **Date:** 2026-10-03. **Status:** done.

**Software:** own (design input)

**What we built:** `probes/cc_lambda_profile.py` (cProfile of `solve_lambda`: BLAS-bound in blocks), `probes/lno_curvature_check.py` (LNO-CCSD(T) curvatures against a canonical anchor), `probes/cc_basis_oop_check.py` (cc-pVTZ vs cc-pVDZ curvatures)

**Gap it fills:** levers 3 and 2

**Files:** the files named

**PR candidate:** no

### 29 — no infrared module in the installed release (magnetizability, nmr, nsr, polarizability, …

**Group:** C, finding about third-party software. **Date:** 2026-10-02. **Status:** done. *Status note (3 Oct 2026):* the module exists on upstream master (last commit 7 Nov 2024); 0.1.0 is simply old — nothing to report; install from master when a third route is wanted. *Status note (3 Oct 2026):* a report to pyscf-properties ('no infrared module') was not filed; the CPHF APT of row 26 is our own answer — the report waits for the user's word.

**Software:** pyscf-properties 0.1.0 (`pyscf.prop`)

**Finding:** no `infrared` module in the installed release (magnetizability, nmr, nsr, polarizability, rotational_gtensor, ssc, trans_dip_moment, zfs only); IR intensities need an APT the package does not provide at this version

**Where recorded:** investigation log 2 Oct 06:5x

**Action:** our own CPHF APT (row 26); no report filed

### 30 — the pyscf lookup python3 -c "import pyscf

**Group:** C, finding about third-party software. **Date:** 2026-10-03. **Status:** done. *Status note (12 Oct 13:3x):* the user gave the
word for the second pull request ('Akkoord op forge #213'); checked first: pyscf-core's `pyscf/lib/CMakeLists.txt` has **no** pyscf lookup — it
builds pyscf itself (none in v2.8.0, v2.10.0, v2.14.0 or master 52f5737; only a commented-out numpy lookup). Of our checkouts only pyscf-forge
carried the pattern, and #213 fixed it there. No second pull request: the note below assumed a pattern that is not in core. *Status note (12 Oct 08:0x):* forge #213 was **merged on 9 Oct 2026 (17:53 UTC, MatthewRHermes)** — noticed only now; the forge half is done. The same lookup pattern in pyscf-core's CMakeLists is the second pull request the note below names, now due (waits for the user's word). *Status note (20:1x 9 Oct 2026):* forge #213 had changes requested on 6 Oct (cmake_minimum_required ≥ 3.15 for policy CMP0094; an unintended mode change on setup.py); pushed 84230da and replied 9 Oct on the user's word; open. *Status note (3 Oct 2026):* the same lookup pattern in pyscf-core's CMakeLists would be a second pull request once forge #213 is merged.

**Software:** pyscf 2.14.0 `pyscf/lib/CMakeLists.txt` (and forge's copy of the pattern)

**Finding:** the pyscf lookup `python3 -c "import pyscf; ..."` is PATH- and CWD-sensitive; from a checkout with a namespace-package `pyscf/`, an interpreter without pyscf answers with the checkout itself, silently

**Where recorded:** forge PR #213 (reworked); pyscf-core's own CMakeLists has the same pattern — a second PR once #213 is merged

**Action:** after #213

### 31 — our E8 probe solves the (T) lambda explicitly (ccsd_t_lambda.kernel) before calling the …

**Group:** B, own layer around third-party code. **Date:** 2026-09-29/30. **Status:** waiting-upstream. *Status note (20:1x 9 Oct 2026):* **#3469 merged 6 Oct**; our explicit (T)-lambda call stays until the next pyscf release. A branch that predates #3469 still takes the CCSD lambda by default: on CO/cc-pVTZ (row 38) it gives a dipole of 0.0851 D against the true 0.17029 D.

**Software:** pyscf 2.14.0 `grad/ccsd_t.py`, `grad/uccsd_t.py` (`Gradients.kernel` without l1/l2)

**What we built:** our E8 probe solves the (T) lambda explicitly (`ccsd_t_lambda.kernel`) before calling the gradient; upstream, `kernel()` without l1/l2 falls back to the CCSD lambda and returns a gradient that is not dE/dx of the CCSD(T) energy (the lambda incident of 29 Sep 2026: six days of invalid Hessians)

**Gap it fills:** correctness of every CCSD(T) gradient taken through the default path

**Files:** `probes/e8_cc_hessian_fd.py` (`gradient()`), tests `test_acceptance_water.py` (gate 1, gradient vs energy FD)

**PR candidate:** **submitted: pyscf/pyscf#3469** (30 Sep 2026; +104 −6; CI green; no review yet)

### 32 — our corpus runner optimises molecules with a triple bond in Cartesian coordinates (RETRY…

**Group:** B, own layer around third-party code. **Date:** 2026-09-30. **Status:** done. *Status note (21:2x 13 Oct 2026):* **psi-rking/optking#116 merged 13 Oct 21:07 (19:07 UTC)** by Rollin King, after he repaired the CI test environments and two one-atom tests on our branch himself (head 72abc97, all four Python builds green; Read the Docs still red, row 39); issue #115 closed with it. Codecov: patch coverage 80.5 %, six of our lines (the guard's outward walk from k) not reached by a test — the user: a second test only if the maintainer asks. The runner's Cartesian retry stays (defence in depth, no cost); the local patch is row 37. *Status note (20:1x 9 Oct 2026):* the maintainer (Rollin King) reviewed on 6 Oct, pushed d72bac0 to our branch himself (libxc in the CI test environments) and dismissed his review; the CI run waits for his approval; the Read the Docs failure is the docs environment, not this change (row 39) — noted on the PR 9 Oct on the user's word. Pull d72bac0 before any change to `~/optking-pr`.

**Software:** optking (psi4's optimiser) `linear-bend` cycle handling

**What we built:** our corpus runner optimises molecules with a triple bond in Cartesian coordinates (`RETRY_OPT_OPTIONS`, 30 Sep) because optking's internal coordinates stall in a silent infinite loop on a near-linear bend (B_4a601408a5, five hours without a line)

**Gap it fills:** the layer-B factory lost a server-day to it

**Files:** `modules/05_support_predictor/corpus/run_corpus.py` (`opt_options_for`), `PR_Draft_2026-09-30_optking_linear_bend_cycle_guard.md`

**PR candidate:** **submitted: psi-rking/optking#116** (30 Sep 2026; guard against the loop, near-0° angle treated as a reset; no CI on that project; no review yet)

### 33 — the two finite-difference routes to the semi-diagonal quartic constants disagree on psi4 FD Hessians

**Group:** C, finding about third-party software. **Date:** 2026-09-21 → 09-30. **Status:** done. *Status note (3 Oct 2026):* pyVPT2 PR #58 (https://github.com/philipmnel/pyvpt2/pull/58, 'quartic: report the disagreement between the two finite-difference routes to phi_iijj (Hessian route)') was opened on 21 Sep and closed by us on 30 Sep: a report in the output detects the problem but does not solve it — a warning still lets a user carry on with noisy constants; the remedy is on the input side (analytic Hessians, where the two routes agree), as our own benzene tests showed (blog post 9, 21 Sep). Nothing pending upstream.

**Software:** pyVPT2 (`philipmnel/pyvpt2`, `quartic.py`; the Hessian route to φ_iijj)

**Finding:** on psi4 finite-difference B3LYP Hessians at the default `DISP_SIZE`, the semi-diagonal quartic constants of benzene from the two FD routes differ by up to 1264 cm⁻¹; with analytic Hessians the routes agree. Recorded in `PR_Drafts_2026-09-21_Upstream_Fixes.md` §2 and in `probes/results_vpt2/`.

**Where recorded:** PR_Drafts §2; blog post 9 ('Two roads to the same number'); the obstacle ledger of 21 and 30 Sep.

**Action:** PR #58 closed by us (detection-only); our own QFF (`src/dpir/qff.py`) carries the two-route check; no upstream action pending.

### 34 — pyscf's flaky Windows test `test_zero_beta_electrons`: a NaN in the first DIIS matrix, not reproducible outside the CI's own build

**Group:** C, finding about third-party software. **Date:** 2026-10-03. **Status:** done — nothing pending on our side; pyscf's own issue #3245 lists the flaky tests. *Status note (3 Oct 2026):* found while our PR #3477's Windows job failed on it (twice; three other pull requests' Windows runs failed on it the same week); a CI note on #3477 was posted on the user's word at 16:36; a 35-minute timebox (the user's word, 16:3x) found no local reproduction.

**Software:** pyscf master, `pyscf/cc/uccsdt_highm.py` (UCCSDT for high multiplicity) under the `CI Windows` workflow: wheel built with msys2 ucrt64 gcc and its OpenBLAS DLL, Python 3.13, numpy 2.5.3, scipy 1.18.1, after ≈ 3,000 other tests in one pytest process.

**Finding:** the CI artifact (`windows-installed-wheel-evidence/pytest-results.xml`) places the error at `lib/diis.py:254` → `scipy.linalg.eigh` on the DIIS B-matrix `[[1, nan]]` in the helium zero-beta case (spin 2, no β electrons): the error vector already carries NaN at the first DIIS update. Reproduction attempts, all passing: the case on Windows (conda-forge pyscf 2.14.0, Python 3.11, OpenBLAS, 1 and 4 threads, 6/6, fresh process and heap poisoned with NaN blocks), the same with every `numpy.empty` / `empty_like` NaN-filled, on Windows and against master's code on Linux (qc05), and master's test file in order on Linux. Excluded as causes: uninitialised numpy allocations (the `empty_like` residual arrays are overwritten — the einsum wrapper does `out[:] = alpha * result` when beta = 0), and the empty contraction dimension (`NPdgemm` zeroes C when k = 0). Not testable here: the CI's own build (numpy 2.5.3 needs Python ≥ 3.12; no Windows pyscf build exists for it on PyPI or conda-forge, and the laptop has no C compiler). Remaining candidates: C-level buffers in `libcc`/`libccsdt`, or that msys2 OpenBLAS build. Blind probing through 50-minute CI runs is the case we agreed not to pursue.

**Where recorded:** obstacle ledger 3 Oct 16:5x; PR-drafts §7 (the CI note); the Windows conda env `pyscfwin` (`~/.conda/envs/pyscfwin`, pyscf 2.14.0) stays for a later attempt.

**Action:** none; a maintainer reruns the job. If pyscf publishes a Windows build for Python ≥ 3.12, the NaN-filled-allocation probe (`scratchpad/zbe/he_nanempty.py`, kept in the obstacle ledger's description) is the first thing to run.

### 35 — pyscf's CCSD(T) gradient has no out-of-core two-particle density: `ccsd_t_rdm._gamma2_outcore` is the in-core function under another name

**Group:** C, finding about third-party software, with a workaround in our code. **Date:** 2026-10-04. **Status:** workaround done in
`probes/t_density_kernel/t_density_fast.py` (the fast path pyscf's gradient calls when installed); an upstream PR is a candidate for the user's word.

**Software:** pyscf 2.14.0, `pyscf/cc/ccsd_t_rdm.py` lines 296–330 (`_gamma2_intermediates` with `compress_vvvv`, `_gamma2_outcore` = one-line alias)
called by `pyscf/grad/ccsd_t.py::grad_elec` with an H5 temp file and `compress_vvvv=True`.

**Finding:** the (T) gradient takes the CCSD two-particle intermediates from the *in-core* `ccsd_rdm._gamma2_intermediates`, whose `dvvvv` is a
dense nvir⁴ array, and then symmetrises it twice (`dvvvv + dvvvv.transpose(...)`) before compressing — three nvir⁴ arrays. Benzene/cc-pVTZ
(nvir = 243): 28 GB each. On the laptop's 20 GB WSL the run of 3 Oct (19:32) died at 21:30:45 and its relaunch (23:02) at 00:48:11, both right
after the (T) lambda converged, both without a traceback (an OOM kill; the last `bash -c` command is exec'd, so no shell was left to print
'Killed'), with 11 GB free at the last one-minute memory sample. pyscf's CCSD gradient does not have this problem: `grad/ccsd.py` uses
`ccsd_rdm._gamma2_outcore`, which writes dvvvv blockwise into the H5 file, compressed.

**Workaround (ours):** `t_density_fast._gamma2_outcore` now calls `ccsd_rdm._gamma2_outcore(mycc, t1, t2, l1, l2, h5fobj, compress_vvvv)` for the
CCSD part and adds the (T) increments — which touch only dovov, dooov and dovvv — in memory; `dvvvv` stays an H5 dataset, which `grad/ccsd.py`'s
`_rdm2_mo2ao` already reads in blocks. Validated by gate 1 on water (dgrad_fast_kernel 7.1e-15; the production gradient through the new route against pyscf's
plain CCSD(T) gradient), stamp renewed, TZ run relaunched 00:58 (a first attempt at 00:56 died in 4 s: HOME expanded on the Windows side inside a nested bash -c; probes/tz_relaunch_1004.sh since).

**Where recorded:** obstacle ledger 4 Oct 01:0x; the lever-2 registration (rung C pre-registration, amendment 3 Oct 08:1x, dated note 4 Oct);
TASKS row 'Odds lever 2'.

**Action:** upstream, the same change in `ccsd_t_rdm._gamma2_outcore` (plus a test that the gradient is unchanged) — a small PR beside #3469/#3470;
the user decides whether and when (GitHub replies and PRs on the user's word).

### 36 — the MP2 gradient's AO block size can fall below a shell's size → empty block, ValueError

**Group:** C, finding about third-party software. **Date:** 2026-10-04. **Status:** pr-candidate (register cell of 4 Oct: 'workaround done; issue/PR on the user's word'; section added 9 Oct, the text was in the register only).

**Software:** pyscf (`grad/mp2.py::grad_elec`)

**Finding:** the MP2 gradient sizes its AO blocks from the memory left in the process (`max_memory − current_memory`), `blksize = max(1, …)`, and `_shell_prange` with a block smaller than a shell's function count yields an empty block → `ValueError: cannot reshape array of size 0` (benzene/cc-pVTZ after B3LYP work in the same process at max_memory 6000). Fix candidate: a floor of the largest shell size on `blksize`, or a clear error; our workaround: MP2 first in a fresh process, max_memory 12000 (`probes/cc_composite_basis_check.py`)

### 37 — the #116 fix applied to the installs made after 30 Sep (pool 3 CPX62, laptop qc env); bootstraps apply it

**Group:** A, patch to third-party code. **Date:** 2026-10-09. **Status:** waiting-upstream (drop at the first optking release that carries #116). *Status note (21:2x 13 Oct 2026):* #116 is merged; no release carries it yet (optking 0.5.0). At the first environment rebuild on a release with it: drop `probes/optking_patches/apply_optking_fix.py` from the bootstraps and keep the regression test's molecule as a check.

**Software:** optking 0.5.0 as installed in the psi4 environments (`v3d.py`, `addIntcos.py`)

**Change:** `probes/optking_patches/apply_optking_fix.py` (30 Sep, the user: 'los het issue op in onze versie van de code') had been applied to the
five installations of that day. `--check` on 20:1x 9 Oct said **NOT patched** on the two made since: the pool 3 CPX62 (4 ethynyl rows pending) and the
laptop's `qc` env (15 ethynyl rows in the five-ring pool, TASKS 38). Applied on both (atomic file replace, between molecules); `--check` now
'already patched' on both; laptop water smoke 50 s after it. `probes/bootstrap_pool3_cpx62.sh` and `probes/bootstrap_nextpool_1002.sh` now apply the
fix and stop unless `--check` confirms both files.

**Why:** the stall guard (90 min) and the Cartesian retry (row 32) covered the hang; the patch removes the lost time.

**Files:** `probes/optking_patches/`, the two bootstrap scripts (commit 3c7a1a34)

### 38 — CO/cc-pVTZ relaxed CCSD(T) dipole: dip_moment() = finite field = 0.17029 D; Molpro's 0.2135 D is not that energy's field derivative

**Group:** C, finding about third-party software. **Date:** 2026-10-09. **Status:** done (reported on pyscf#3477, 9 Oct, the user's word).

**Software:** pyscf `grad/ccsd_t.py` with #3477 (`Gradients.dip_moment()`); issue pyscf#1272 (2022)

**Finding:** CO, cc-pVTZ, all electrons, R = 1.128 Å (the issue's input): relaxed CCSD(T) dipole from #3477 +0.17029 D after a gradient with the (T)
lambda; central differences of the CCSD(T) energy in a uniform field (h = 1e-3 and 2e-3 a.u., Richardson) +0.17029 D (difference < 1e-5 D). SCF,
CCSD and CCSD(T) energies equal the Molpro values quoted in the issue to 1e-8 Eh, so Molpro's 0.2135 D (`ccsd(t);core,0;cphf,1`) is not the field
derivative of that energy. The issue's unrelaxed (T) density gives 0.17674 D, unchanged. On the PR branch without #3469 the default `kernel()` takes
the CCSD lambda: 0.0851 D (row 31).

**Where recorded:** pyscf#3477 comment of 9 Oct; scratchpad scripts `co_dipole_1272.py`, `co_dipole_1272b.py` (61 s at 4 threads).

**Action:** none; it also confirms the route our CC APTs use (explicit (T) lambda, row 27) on a second molecule.

### 39 — the optking docs build fails importing qcelemental under the current pydantic

**Group:** C, finding about third-party software. **Date:** 2026-10-09. **Status:** done (noted on optking#116, 9 Oct, the user's word).

**Software:** optking documentation (`devtools/conda-envs/docs.yaml`, Read the Docs; sphinx-automodapi imports the package)

**Finding:** every docs build of #116 (30 Sep, 6 Oct) fails in `import qcelemental` → pydantic schema generation (`ValueError: not enough values to
unpack` in a NumPy-array annotation); #116 does not touch the docs environment; master's last docs build is from 1 June, so a fresh master build would
likely fail the same way.

**Action:** none unless the maintainer asks; a pin in `docs.yaml` would be a separate small PR (not drafted).

### 40 — an explicit argument to `proc_hessian_` raises ValueError

**Group:** C, finding about third-party software. **Date:** 2026-10-11. **Status:** pr-open. *Status note (11 Oct 15:4x):* opened as
pyscf/properties#16 on the user's word ('Dien ze maar in'); the repository's last commit is 7 Nov 2024 and pull requests #13 (Mar 2026) and
#15 (Jun 2026) have no maintainer reply, so review may not come.

**Software:** pyscf-properties master 4eee5a43 (`pyscf/prop/infrared/rhf.py` and `uhf.py`, `proc_hessian_`, lines 41–44 of rhf.py); upstream master
is the same commit (checked 11 Oct 2026), no open pull request on it.

**Finding:** `mo_energy = mo_energy if mo_energy else mf.mo_energy` (and the same for mo_coeff, mo_occ, h1ao_grad) takes the truth value of a NumPy
array; any explicit argument raises `ValueError: The truth value of an array with more than one element is ambiguous`. Only the default path works
(`kernel_dipderiv` passes no arguments). Measured 11 Oct on water/STO-3G RHF in qc05 (pyscf 2.14.0): explicit `mo_energy` → ValueError, defaults → ok.
Our route C (`corpus/apt.py`, `hessian_with_response`) follows this function's pattern with its own code.

**Action:** a two-line pull request (`is None` instead of the truth value, in rhf.py and uhf.py) with a test that passes explicit arrays.

### 41 — a reference-free test for the infrared module

**Group:** C, finding about third-party software. **Date:** 2026-10-11. **Status:** pr-open. *Status note (11 Oct 15:4x):* opened as
pyscf/properties#17 on the user's word. Measured for the PR (NH3/6-31G, step 1e-3 bohr): max |analytic − FD| RHF 5.1e-6, UHF 9.2e-6, RKS 8.0e-5,
UKS 2.8e-4 e; the DFT part equals the sum-rule residual (no grid response in the analytic DFT terms); tolerances 5e-5 (HF), 1e-3 (DFT); a response
term scaled by 1/2 makes it fail; 45 s.

**Software:** pyscf-properties master 4eee5a43 (`pyscf/prop/infrared/test/test_ir_inten.py`).

**Finding:** the four upstream tests compare intensities with Q-Chem at rtol 5e-4 (RHF, UHF, RKS) and 1e-3 (UKS, with the comment "this criteria is a
little bit loose … could be grid setting, grid response, atomic mass"). The APT can be checked without an external program: central finite
differences of the SCF dipole and the translation sum rule. Ours (`tests/test_apt_route_props.py`, 11 Oct): H2O⁺ UKS/B3LYP/6-31G against
upstream's UKS APT within 1e-4 e, sum rules < 5e-4 e, seconds; at the labels settings water 1.2e-5 e, benzene 4.4e-4 e against FD
(`probes/results_m1/apt_route_props_2026-10-11/`).

**Action:** a pull request adding the FD check for all four classes (small basis, small grid); it separates the APT from the masses and grids
that the Q-Chem comparison mixes.

### 42 — the PyPI release has no infrared module

**Group:** C, finding about third-party software. **Date:** 2026-10-11. **Status:** done. *Status note (11 Oct 15:4x):* not filed — issue #10
('Make new release?', 26 Apr 2025, no reply) already asks for it; a duplicate would add nothing.

**Software:** pyscf-properties 0.1.0 as installed by pip (row 29); the infrared module came with pull request #1 (merged June 2022); the repository
has no GitHub releases.

**Finding:** `pip install pyscf-properties` gives a package without `infrared`; users find the module only on master. Upstream's own tests of the
module pass on pyscf 2.14.0 (11 Oct, 4 of 4, through `probes/upstream_infrared.py`).

**Action:** an issue asking for a release from master.

### 43 — `harmonic_analysis` diagonalises the Hessian without symmetrising it

**Group:** C, finding about third-party software. **Date:** 2026-10-11. **Status:** waiting-upstream. *Status note (17 Oct 10:02):* **pyscf/pyscf#3507 approved and merged into master by sunqm, 16 Oct 23:24 UTC** (two commits: the symmetrisation, and a note-level log line with the largest |H − Hᵀ| after his review; the asymmetric-input test was removed at his request, `test_thermo.py` unchanged). Nothing to change on our side now — the labels route symmetrises before its own diagonalisation (`corpus/analytic_hessians.py`); with the first pyscf release after 2.14.0 (PyPI's newest on 17 Oct: 2.14.0, 18 Jul) `harmonic_analysis` does it too, and the upgrade checklist ('How to use') closes this row. *Earlier status note (12 Oct 22:4x):* sunqm reviewed (17:02 UTC): the test should catch meaningful errors, not cover code; and an enforced symmetrization should be logged with the discrepancy. Prepared locally, **not pushed** (aedb34b87 in ~/pyscf-wt-thermo): `lib.logger.note` with max |H − Hᵀ| in Eh/bohr² (water B3LYP/6-31G: 8.39e-08), the asymmetric-Hessian test removed; `test_thermo.py` passes, 5 tests. **Pushed and replied 22:4x on the user's word** ('Ja, push en plaats het antwoord maar'). *Status note (11 Oct 21:3x):* opened as
pyscf/pyscf#3507 on the user's word ('Ja, doe beide maar'): `h = (h + h.T) * .5` before the projection and eigh, and a test (water/STO-3G
RHF Hessian plus an antisymmetric part of 1e-3: frequencies and |modes| unchanged to 1e-8; fails without the change); the six thermo tests
pass against pyscf 2.14.0 with the branch's thermo.py; ruff as in lint.yml clean. Branch `thermo-symmetrize-hessian` in ~/pyscf-wt-thermo.

**Software:** pyscf 2.14.0 and master (`pyscf/hessian/thermo.py`, `harmonic_analysis`: `h = mass_hess.transpose(0,2,1,3).reshape(...)`, then
`numpy.linalg.eigh(bvec.T h bvec)`); used by pyscf-properties' infrared module for its normal modes.

**Finding:** the analytic UKS/B3LYP/6-31G* Hessian of 3-hydroxypyridine⁺ (12 atoms, grid 99/590) is asymmetric, max |H − Hᵀ| = 6.2e-5 Eh/bohr²;
`eigh` uses one triangle, so the modes depend on which. Heights from these modes differ from those on the symmetrised Hessian by 3.2e-3 relative and
the frequencies by 3.1e-2 cm⁻¹; on the symmetrised Hessian the two codes agree to 9e-8 (benzene, RKS: 1.5e-6). Measured in
`probes/results_m1/apt_route_props_2026-10-11/` (REGISTRATION.md, outcome 16:3x).

**Action:** a small pull request: symmetrise `hess` in `harmonic_analysis` (½(H + Hᵀ) over the (atom, atom, x, y) layout) with a test on an
asymmetric input; draft only on the user's word.

### 44 — pyscf's multi-root Krylov CPHF stops before its solution satisfies its equations

**Group:** C, finding about third-party software. **Date:** 2026-10-12. **Status:** waiting-upstream. *Status note (13 Oct 21:2x):* two of 20 refined APTs missed the 1e-6 bound after three batched rounds (B_1194d7a42a 1.1e-6, B_127dd8c4ed 2.1e-6); the diagnosis read 'solver' — batched rounds flat at 1.7e-6 → 2.1e-6, scipy GMRES on each of the twelve worst columns alone 2e-12 to 1.2e-11 (`probes/results_m1/apt_refine_install_2026-10-12/floor_B_127dd8c4ed/diagnose_floor.log`). **Built:** `refine_response(per_column=True)`, a per-column GMRES fallback for the columns still above the bound (installed on the labels server 13 Oct 09:22); both pass (9.4e-7 with 1 single-column solve, 8.8e-7 with 5). #3384 measured on B_127: it detects the stall but ends at 8.1e-5 (2.14.0: 8.2e-5), because its per-root solve stops at `fallback_tol` = 1000·tol (`pr3384_check.log`); reported on #2702 on the user's word (issuecomment-6146230747), asking whether the per-root solve could run to `tol`. jeanwsr asked for the extra cost or a repro script: `repro_2702.py` (standalone, counts operator calls and vectors) — water B3LYP 1.5e-6 → 9.3e-11 at 50 vs 38 operator vectors, benzene PBE unchanged (no fallback) in `repro_2702_small.log`; the 22-atom case runs (`repro_2702_large.log`); the reply goes out on the user's word. *Status note (12 Oct 13:4x):* on the user's word ('Ja, plaats het antwoord en sluit #3508') the reply is posted on #2702 (https://github.com/pyscf/pyscf/issues/2702#issuecomment-6123530151) and #3508 is closed in favour of #3384. Next: when #3384 is merged and released, the upgrade checklist; `refine_response` stays as the guard. *Status note (12 Oct 13:3x):* **pull request [pyscf/pyscf#3508](https://github.com/pyscf/pyscf/pull/3508)** opened 12:5x on the user's word ('Je mag de PR indienen als je wilt'): `solve_withs1` checks the true residual with the induced potential it computes anyway and solves once more on it (defect correction), with `test_cphf_residual` (fails without the change). Measured on master 52f5737 → #3508: labels case (benzene PBE/6-31G* Cartesian, (99, 590)) 5.5e-5 → 5.8e-8 (solve_mo1 298 → 392 s), the #2702 reproduction 6.4e-7 → 3.2e-8, water B3LYP 5.7e-6 → 4.0e-9. On full master the reproduction is already 6.4e-7 (2.14.0: 9.2e-5; master's `lindep` change since 2.14.0) — the comment's 'master does not fix it' was measured on the labels case, which master still misses in full (5.5e-5). **jeanwsr asked on #2702 (09:16 UTC) whether their open PR #3384** (per-RHS fallback inside `lib.krylov`) solves our problem; merged locally onto master and measured: labels case 5.4e-8 at 313 s, reproduction 1.9e-8 at 58 s, water B3LYP 1.5e-6 (inside their relaxed fallback_tol), water HF 3.9e-9. It solves it, in the solver itself, for every caller and cheaper than #3508. Draft reply (yes, numbers, close #3508 in favour of #3384) in `probes/results_m1/krylov_report_2026-10-12/reply_3384_draft.md`, waits for the user's word. Our `refine_response` stays as the guard (decision c). *Status note (12 Oct 10:5x):* **reported on pyscf issue #2702** (open since 2025, no reply before ours; https://github.com/pyscf/pyscf/issues/2702#issuecomment-6121024352) on the user's word ('Ja, doe beide maar'): a standalone reproduction (benzene PBE/6-31G*, default grid: requested tol 1.2e-7, true residual 9.2e-5; ~100 s), the tol/max_cycle insensitivity, master's #3334 overlaid (5.6e-5, not fixed — as its description says), the exact pieces, the Hessian's insensitivity and the APT's sensitivity, and one round of batched defect correction as a cheap fix (7.8e-8, APT 3.8e-5, ≈ 120 s on a 780 s Hessian); a pull request offered. Files: `probes/results_m1/krylov_report_2026-10-12/`. *Status note (12 Oct 09:3x):* the cause is the Krylov solver, not the XC terms the first text below names — see the addendum of `probes/results_m1/uks_apt_margin_2026-10-11/REGISTRATION.md`: h1 and the response kernel are exact, pyscf's solution misses its own system by 7e-5, GMRES on the same system (7e-14) brings the APT to the field route (5.9e-6 from 1.6e-4).

**Software:** pyscf 2.14.0 and master — `lib/linalg_helper.py::krylov` with many right-hand sides, as `scf/cphf.py solve_withs1` calls it for
the analytic Hessian's `solve_mo1` (all 3N directions at once); used by our route C (`corpus/apt.py`) and by pyscf-properties' infrared module.

**Finding:** for DFT the returned response misses its own equations by 1e-5 to 1e-4 (benzene B3LYP/6-31G*, (99, 590): 1.3e-4), whatever
`tol` and `max_cycle` say, without a warning; the solver stops on the norm of its last trial vector. The Hessian is insensitive (benzene
0.06 cm⁻¹ against the frozen-grid FD of the gradient: the labels are not affected); dipole derivatives contracted from the response are
not (benzene 4.3e-4 e against the field route, heights ≤ 0.6 %). Proven by GMRES on the same system (route C onto the field route); an earlier
attribution to the XC part was withdrawn. Measured in `probes/results_m1/uks_apt_margin_2026-10-11/` (REGISTRATION.md with addendum) and
`probes/results_m1/krylov_report_2026-10-12/`.

**What we built:** `corpus/apt.py refine_response` (batched defect correction, bound 1e-6), installed on the labels server 12 Oct 11:51
(TASKS 44 a); the route-C APTs written before it are recomputed (b); it stays as a guard after an upstream fix (c).

### 45 — pyVPT2's FD: HESSIAN consistency checks compare averaged numbers, so they always pass

**Group:** C, finding about third-party software, with a fix submitted. **Date:** 2026-10-13. **Status:** pr-open.

**Software:** pyVPT2 main 2eae571 (`assemble_quartic_from_hessians`, `check_cubic`, `check_quartic`), the `FD: HESSIAN` route.

**Finding:** the assembly averages the finite-difference routes into every element before the checks run: φ_iijj from the displacements
along i and along j, φ_ijk from those along i, j and k. The compared elements are then equal by construction and the checks print "No
inconsistencies found" — also on benzene (B3LYP/6-31G*, psi4 FD Hessians), where the two quartic routes disagree by a median of 22 cm⁻¹ and up
to 1,265 cm⁻¹ (issue #57, row 33).

**Change:** one route per element (φ_ijk[i, j, k] from the displacement along i, φ_iijj[i, j] from the one along j), the checks on the
independent routes, then the same symmetrisation as before: returned constants unchanged up to rounding (≤ 1.2e-10 cm⁻¹ in the test, tolerance
1e-9). Three tests. Branch `check-routes-before-averaging` (7cba69c) in `~/pyvpt2-fork`; text in
`GoalGathering/notes/Draft_2026-10-13_pyVPT2_PR_check_routes.md`.

**PR:** **philipmnel/pyvpt2#59**, opened 13 Oct on the user's word ('Ja, push en open de PR maar'); refs #57, which stays open (this fixes the
check, not the noise; our own QFF `src/dpir/qff.py` carries the two-route check and refuses a noisy force field). Maintainer Philip Nelson, a
one-person project; polite follow-up ≈ 27 Oct (TASKS, the software tasks row).

### 46 — pyscf's DFT grid is not invariant under the molecule's point group; `Grids.symmetry` is an unimplemented TODO

**Group:** C, finding about third-party software, with a fix designed (TASKS 55). **Date:** 2026-10-13. **Status:** pr-candidate (nothing
built; the user wants to understand it first: 'We gaan het waarschijnlijk wel doen, maar eerst moet ik het beter begrijpen').

**Software:** pyscf 2.14.0 `dft/gen_grid.py`: `gen_atomic_grids` builds one atomic grid per element in the laboratory axes, `get_partition`
translates it onto every atom of that element; `Grids.symmetry` (set from `mol.symmetry`) is documented as 'whether to symmetrize mesh grids
(TODO)' and not used.

**Finding:** the molecular grid has at most the octahedral group's operations (signed permutations of the axes), not the molecule's group.
For a hexagonal molecule a C₆ or C₃ image of a computed Hessian is therefore not the Hessian at the image geometry. Measured on the 21 Sep
benzene B3LYP/6-31G* set (99/590, `probes/results_m1/qff_symmetry_rebuild_dev_2026-10-13/image_errors.json`): image against computed
Hessian 3.0e-3 of the displacement signal (median of 14) for grid-compatible operations, 2.4e-2 (median of 82) for the others. Consequence
here: the quartic force field's pair saving fails (Δ_anh 0.56 / 1.06 cm⁻¹ against the direct set), while the method is exact on symmetric
model data (`tests/test_qff_symmetry_rebuild.py`).

**Fix designed (not built):** orient each atom's grid so that the molecular grid is invariant under the point group — the atomic grid of
one atom per orbit aligned with the atom's stabiliser (for PAH atoms at most C₂v, contained in the octahedral grid), the others obtained by
the group's operations; the Becke partition depends only on positions. Same points, no extra cost. Cannot serve an atom on a C₆ axis.
Tests planned: energy invariance under every operation, Hessian covariance, image errors at the noise floor for all operations.

**PR candidate:** implementing the TODO in `Grids` (orientation per atom from `mol.symmetry`'s operations), with those tests — only after
our own version passes on benzene, and on the user's word. Before drafting: re-check pyscf master and open issues/PRs for symmetric grids.

### 47 — a CCSD(T) atomic polar tensor by finite field, for pyscf-properties' infrared module

**Group:** B, own layer around third-party code, offered upstream later. **Date:** 2026-10-14. **Status:** pr-candidate (the user, 14 Oct:
'Ja' to listing it; to be proposed after anchor set three's read, on the user's word).

**Software:** pyscf-properties master, `prop/infrared` — infrared intensities for RHF, UHF, RKS and UKS through the analytic CPHF APT (rows
29, 40–42); nothing for coupled cluster. pyscf itself has CCSD(T) gradients (`grad/ccsd_t.py`) but no CC dipole derivatives.

**What we built:** `probes/cc_apt_field.py` (12 Oct 2026, lever 6): P[t, 3A+x] = −∂g_Ax/∂F_t by central differences of the CCSD(T) gradient in
a uniform field ±F along x, y, z — six gradients instead of the 6N of finite differences of the dipole. The field enters the core
Hamiltonian (+F·r per electron, −Z_A F·R_A for the nuclei) and, through `apt_field_route.field_hcore_generator`, the gradient's
core-Hamiltonian derivative (`int1e_irp`); the CC chain is `cc_dipole_capture._cc_with_lambda` (RHF → CCSD → (T) → the explicit (T) lambda,
then `grad.ccsd_t.Gradients(mycc).kernel(t1, t2, l1, l2, eris)`, the call pyscf/grad/test/test_ccsd_t.py makes). Since 14 Oct each field's
gradient is cached and reused on a re-run, and the CCSD/lambda cycle limit is 200 at unchanged tolerances.

**Validation (numbers with their counterparts):** water/6-31G against central differences of the relaxed CCSD(T) dipole, 1.8e-5 e
(`tests/test_cc_apt_field.py`); benzene against the E8 run's FD APT, 1.0e-4 e (line 1e-3); translation sum rule ≤ 1e-10 e on every anchor
so far, against ≈ 3e-4 for the dipole route; quinoxaline field against FD dipole 1.6e-4 e (anchor set three).

**PR candidate:** a function in `prop/infrared` (or a small `prop/apt_cc` module) taking a CCSD or CCSD(T) object and returning the APT by
finite field, with the water test against FD of the relaxed dipole and the sum-rule check. Before drafting: re-check pyscf-properties and
pyscf master for a CC dipole-derivative route, read their contribution guide, and keep the (T) lambda explicit (the lambda incident of 29
Sep). Size: one module of ≈ 150 lines plus tests; decided by the user.

## How to use this ledger

- Add a row the day a change is made; never after the fact from memory.
- **Python versions (3 Oct 2026, the user: 'Zet die regel maar in het software-ledger'):** per environment the newest Python the heaviest dependency supports, pinned, and raised only at a rebuild of that environment — never mid-run, because the gate-1 stamps and the running jobs belong to the environment they were made in. Standing 3 Oct 2026: Windows system 3.14.6 (torch 2.14, rdkit; modules 05/06), `.venv` 3.13.9 (LangGraph; module 07), WSL `qc05` 3.12.14 (our pyscf branch, anchors, gate 1), conda `qc` on the servers 3.11/3.12 (psi4 1.11). Compatibility checked: psi4 1.11 has conda-forge builds for 3.10–3.14 on Linux; pyscf we build from our branch (its CI tests 3.14 on macOS); torch and rdkit run on 3.14 here; pyscf has no Windows build beyond conda-forge's 3.11, which does not matter (Windows is not a compute platform for us). At the next rebuild (new server or the PC) the chemistry environments go to 3.14, gate 1 on water after it; 3.14 is the newest series today (3.14.8).
- When upstream carries our fix (merged pull request, or master was ahead of us), the next environment rebuild moves to that upstream version and drops the
  local patch; the swap is recorded in the row. Never mid-run: the environments under running anchors and the gate-1 stamps stay as they are (3 Oct 2026).
- **Upgrade checklist (11 Oct 2026, the user: pyscf may publish releases during the project, some with our pull requests in them).** `state.sh`
  shows the newest PyPI release of pyscf and pyscf-forge against the pinned versions (`tools/upstream_releases.py`). A newer release:
  (1) read its changelog for our pull requests and for changes to the calls we use (Hessians, CPHF, grids, CC gradients, dip_moment);
  (2) build it in a new environment beside the old one — the running jobs and the corpus layer in progress stay on the old one;
  (3) in the new environment run upstream's tests of the modules we call and our own two-route checks against their saved numbers: gate 1 on
  water, route C on water and benzene (`probes/apt_route_c_probe.py`, limits in its file), the analytic Hessian against the saved one, and
  `tests/` in WSL; (4) for every waiting-upstream row the release closes, remove our patch or fallback and keep a test that upstream now
  behaves; (5) record the move in the row and in the environment listing (`tools/freeze_environments.py`). One corpus layer is computed with
  one version: a layer started on the old environment finishes on it.
- Before proposing any PR: re-check the upstream `master` (the fix may exist), write a minimal test, and
  follow the project's contribution guide. The user decides which to submit and when; nothing here commits
  us to anything.

**Dated note, 21 September 2026 (benzene run on hel1-14, `probes/results_vpt2/benzene_b3lyp_631gs_vpt2*.md`).** pyVPT2 0.1.2 gives unusable fundamentals for a symmetric top: exactly degenerate pairs split asymmetrically and an accidental near-degeneracy (a1g/b1u, 0.7 cm⁻¹) produces shifts of −217 cm⁻¹; a polyad rerun with `FERMI_K_THRESH 0` does not repair it. Required before benzene/coronene are scored: a degenerate-mode treatment (symmetric-top VPT2 formulas, or the Mills/Aliev–Watson degenerate case) or another VPT2 engine on the same quartic force field (the 61 Hessians are cached). Own change or replacement to be decided after 28 September; `vpt2_benzene.py` gained `--fermi-k-thresh`, `--fermi-omega-thresh`, `--tag` (21 Sep, no package change).

**Update 21 September 08:2x (the user, 07:5x: "Doe de kwaliteitscontrole op de PR's en dien ze dan in").** Row 15: #212 quality control passed (clean pyscf 2.14 environment, branch built from source, `pytest -q pyscf/lno/test` 5 passed in 183 s) → **ready for review**. Row 16: pyVPT2 branch pushed to the fork; upstream suite with the change 27 passed / 10 skipped; real-data replay prints the independent assembly's numbers (22.40 / 107.04 / 1264.46) → issue [philipmnel/pyvpt2#57](https://github.com/philipmnel/pyvpt2/issues/57), PR [philipmnel/pyvpt2#58](https://github.com/philipmnel/pyvpt2/pull/58), 09:3x. **Row 17 (new):** pyscf-forge `setup.py` — `-DPYSCF_SOURCE_DIR` passed from the build interpreter, because `pyscf/lib/CMakeLists.txt` otherwise asks the first `python3` on PATH and, from a non-activated environment, resolves the checkout's own `pyscf/` namespace directory (configure fails on `config.h.in`); four-case build check on hel1-14 → [pyscf/pyscf-forge#213](https://github.com/pyscf/pyscf-forge/pull/213). Row 12 closed: upstream's shipped LNO tests already call `stability_jacobi(return_status=True)` and pass on pyscf 2.14.

**Rows 15–16, 21 September 2026 (upstream, prepared; the user holds submission until the cover text and quality control are discussed).** 15: pyscf-forge `lno/lnoccsd.py`, our engine patches 1–2 as an upstream PR — pyscf/pyscf-forge#212, opened 07:2x, **converted to draft 07:3x**; patch archived as `probes/patches/pyscf_forge_lno_pyscf214_numpy2_compat_2026-09-21.patch`. 16: pyVPT2 `quartic.py` route-consistency report before averaging, docstring, tutorial DISP_SIZE guidance, three synthetic tests (pass) — local fork branch `quartic-route-consistency`, **not pushed**; patch archived as `probes/patches/pyvpt2_quartic_route_consistency_2026-09-21.patch`. Quality-control list and draft texts: `notes/PR_Drafts_2026-09-21_Upstream_Fixes.md`. Local correction pending: our `stability_jacobi()[1]` edit in the `__main__` block of `lnoccsd.py` is wrong for pyscf 2.14 (harmless, demo code) — revert.
