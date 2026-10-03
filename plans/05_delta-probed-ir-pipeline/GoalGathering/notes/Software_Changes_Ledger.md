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
| 21 | 2026-09-29/30 | B | pyscf 2.14.0 `cc/ccsd_t_rdm.py` (T) densities and `cc/ccsd_t_lambda.py… | C kernels t_density_intermediates and t_lambda_intermediates (probes/t_density_kernel/),… | pr-open |
| 22 | 2026-09-30 → 10-03 | A | upstream state of rows 1–2, 20, 21 | rows 1–2 merged upstream as pyscf-forge PR #212 (30 Sep, approved) | pr-open |
| 23 | 2026-10-01 | B | own (module 05 trainer) | m05/rungC_targets.py | done |
| 24 | 2026-10-02 | B | own (E8 probe) | two-route-check {inline,separate,only} | done |
| 25 | 2026-10-02 | B | own (module 05) | m05/rungC_cc_transfer.py (leave-one-anchor-out transfer to CCSD(T) | done |
| 26 | 2026-10-02 | B | own (intensities) | probes/dipole_derivs_fd.py (APT by FD of analytic SCF dipoles, sum rule + two steps | done |
| 27 | 2026-10-03 | B | pyscf 2.14.0 `grad/ccsd.py::grad_elec` (semantics, no upstream file to… | gradient_with_dipole in the E8 probe and probes/cc_dipole_capture.py | pr-candidate |
| 28 | 2026-10-03 | B | own (design input) | probes/cc_lambda_profile.py (cProfile of solve_lambda | done |
| 29 | 2026-10-02 | C | pyscf-properties 0.1.0 (`pyscf.prop`) | no infrared module in the installed release (magnetizability, nmr, nsr, polarizability, … | done |
| 30 | 2026-10-03 | C | pyscf 2.14.0 `pyscf/lib/CMakeLists.txt` (and forge's copy of the patte… | the pyscf lookup python3 -c "import pyscf | pr-candidate |
| 31 | 2026-09-29/30 | B | pyscf 2.14.0 `grad/ccsd_t.py`, `grad/uccsd_t.py` (`Gradients.kernel` w… | our E8 probe solves the (T) lambda explicitly (ccsd_t_lambda.kernel) before calling the … | pr-open |
| 32 | 2026-09-30 | B | optking (psi4's optimiser) `linear-bend` cycle handling | our corpus runner optimises molecules with a triple bond in Cartesian coordinates (RETRY… | pr-open |

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

**Group:** B, own layer around third-party code. **Date:** 2026-09-29/30. **Status:** pr-open.

**Software:** pyscf 2.14.0 `cc/ccsd_t_rdm.py` (T) densities and `cc/ccsd_t_lambda.py::make_intermediates`

**What we built:** C kernels `t_density_intermediates` and `t_lambda_intermediates` (`probes/t_density_kernel/`), swapped in by `t_density_fast.install()` / `install_lambda()`, each with a two-route check against pyscf's Python

**Gap it fills:** pyscf's (T) gradient spends its time in blocked `lib.einsum` over six-index blocks and keeps ≈ 3.4 of 16 cores busy; per-triple C with thread-private nocc³ buffers: density water 4e-18, lambda water 3e-18 / benzene 1e-16 and 44 s vs 373 s

**Files:** `probes/t_density_kernel/`, `tests/test_t_density_kernel.py`, `tests/test_e8_fast_t_*.py`

**PR candidate:** **submitted: pyscf/pyscf#3470** (30 Sep 2026; upstream master was unchanged in these files, no open PR)

### 22 — rows 1–2 merged upstream as pyscf-forge PR #212 (30 Sep, approved)

**Group:** A, patch to third-party code. **Date:** 2026-09-30 → 10-03. **Status:** pr-open. *Planned (3 Oct 2026):* at the next environment rebuild pin pyscf-forge to master ≥ 1f1b65f (rows 1–2 become upstream code) and install pyscf-properties from master for its `infrared` module as a second route beside our CPHF APT; pyscf-core stays on our kernel branch until #3469/#3470 are merged. *Status note (3 Oct 2026):* the state row: #212 merged, #213 (reworked 3 Oct, replied), pyscf #3469 and #3470, optking #116 open — all waiting for maintainers.

**Software:** upstream state of rows 1–2, 20, 21

**Change:** **rows 1–2 merged upstream** as pyscf-forge PR #212 (30 Sep, approved): on forge master ≥ 1f1b65f the two patches are no longer needed (our clone's `lno-pyscf214-compat` branch is upstream). Row 20's fix is pyscf #3305/#3387 (upstream after 2.14.0; our wrapper stays until the next release). Row 21's kernels: pyscf PR #3470 (opened 30 Sep, CI green on all platforms, no review yet); the lambda fallback fix: pyscf PR #3469 (same). forge PR #213 (build: pyscf lookup with the build interpreter) reworked 3 Oct along the maintainer's review and replied to on the user's word. optking PR #116 (linear-bend cycle guard, 30 Sep) open, no CI there.

**Why:** —

**Files:** `PR_Drafts_2026-09-21_Upstream_Fixes.md`, `PR_Draft_2026-09-30_optking_linear_bend_cycle_guard.md`

**PR candidate:** #212 merged; #213, #3469, #3470, #116 open

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

**Group:** B, own layer around third-party code. **Date:** 2026-10-03. **Status:** pr-candidate. *Prepared 3 Oct 10:1x:* branch `ccsd-grad-relaxed-dm1` on the fork (commit 06468d3, on upstream master) — `cc_grad.rdm1_relaxed` kept by `grad_elec`, `Gradients.dip_moment()`, the (T) gradient calls `grad_elec` on the caller's object; tests water/6-31G against finite field (CCSD and CCSD(T), 4e-8); not opened, waits for the user's word.

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

**Group:** C, finding about third-party software. **Date:** 2026-10-03. **Status:** pr-candidate. *Status note (3 Oct 2026):* the same lookup pattern in pyscf-core's CMakeLists would be a second pull request once forge #213 is merged.

**Software:** pyscf 2.14.0 `pyscf/lib/CMakeLists.txt` (and forge's copy of the pattern)

**Finding:** the pyscf lookup `python3 -c "import pyscf; ..."` is PATH- and CWD-sensitive; from a checkout with a namespace-package `pyscf/`, an interpreter without pyscf answers with the checkout itself, silently

**Where recorded:** forge PR #213 (reworked); pyscf-core's own CMakeLists has the same pattern — a second PR once #213 is merged

**Action:** after #213

### 31 — our E8 probe solves the (T) lambda explicitly (ccsd_t_lambda.kernel) before calling the …

**Group:** B, own layer around third-party code. **Date:** 2026-09-29/30. **Status:** pr-open.

**Software:** pyscf 2.14.0 `grad/ccsd_t.py`, `grad/uccsd_t.py` (`Gradients.kernel` without l1/l2)

**What we built:** our E8 probe solves the (T) lambda explicitly (`ccsd_t_lambda.kernel`) before calling the gradient; upstream, `kernel()` without l1/l2 falls back to the CCSD lambda and returns a gradient that is not dE/dx of the CCSD(T) energy (the lambda incident of 29 Sep 2026: six days of invalid Hessians)

**Gap it fills:** correctness of every CCSD(T) gradient taken through the default path

**Files:** `probes/e8_cc_hessian_fd.py` (`gradient()`), tests `test_acceptance_water.py` (gate 1, gradient vs energy FD)

**PR candidate:** **submitted: pyscf/pyscf#3469** (30 Sep 2026; +104 −6; CI green; no review yet)

### 32 — our corpus runner optimises molecules with a triple bond in Cartesian coordinates (RETRY…

**Group:** B, own layer around third-party code. **Date:** 2026-09-30. **Status:** pr-open.

**Software:** optking (psi4's optimiser) `linear-bend` cycle handling

**What we built:** our corpus runner optimises molecules with a triple bond in Cartesian coordinates (`RETRY_OPT_OPTIONS`, 30 Sep) because optking's internal coordinates stall in a silent infinite loop on a near-linear bend (B_4a601408a5, five hours without a line)

**Gap it fills:** the layer-B factory lost a server-day to it

**Files:** `modules/05_support_predictor/corpus/run_corpus.py` (`opt_options_for`), `PR_Draft_2026-09-30_optking_linear_bend_cycle_guard.md`

**PR candidate:** **submitted: psi-rking/optking#116** (30 Sep 2026; guard against the loop, near-0° angle treated as a reset; no CI on that project; no review yet)

## How to use this ledger

- Add a row the day a change is made; never after the fact from memory.
- When upstream carries our fix (merged pull request, or master was ahead of us), the next environment rebuild moves to that upstream version and drops the
  local patch; the swap is recorded in the row. Never mid-run: the environments under running anchors and the gate-1 stamps stay as they are (3 Oct 2026).
- Before proposing any PR: re-check the upstream `master` (the fix may exist), write a minimal test, and
  follow the project's contribution guide. The user decides which to submit and when; nothing here commits
  us to anything.

**Dated note, 21 September 2026 (benzene run on hel1-14, `probes/results_vpt2/benzene_b3lyp_631gs_vpt2*.md`).** pyVPT2 0.1.2 gives unusable fundamentals for a symmetric top: exactly degenerate pairs split asymmetrically and an accidental near-degeneracy (a1g/b1u, 0.7 cm⁻¹) produces shifts of −217 cm⁻¹; a polyad rerun with `FERMI_K_THRESH 0` does not repair it. Required before benzene/coronene are scored: a degenerate-mode treatment (symmetric-top VPT2 formulas, or the Mills/Aliev–Watson degenerate case) or another VPT2 engine on the same quartic force field (the 61 Hessians are cached). Own change or replacement to be decided after 28 September; `vpt2_benzene.py` gained `--fermi-k-thresh`, `--fermi-omega-thresh`, `--tag` (21 Sep, no package change).

**Update 21 September 08:2x (the user, 07:5x: "Doe de kwaliteitscontrole op de PR's en dien ze dan in").** Row 15: #212 quality control passed (clean pyscf 2.14 environment, branch built from source, `pytest -q pyscf/lno/test` 5 passed in 183 s) → **ready for review**. Row 16: pyVPT2 branch pushed to the fork; upstream suite with the change 27 passed / 10 skipped; real-data replay prints the independent assembly's numbers (22.40 / 107.04 / 1264.46) → issue [philipmnel/pyvpt2#57](https://github.com/philipmnel/pyvpt2/issues/57), PR [philipmnel/pyvpt2#58](https://github.com/philipmnel/pyvpt2/pull/58), 09:3x. **Row 17 (new):** pyscf-forge `setup.py` — `-DPYSCF_SOURCE_DIR` passed from the build interpreter, because `pyscf/lib/CMakeLists.txt` otherwise asks the first `python3` on PATH and, from a non-activated environment, resolves the checkout's own `pyscf/` namespace directory (configure fails on `config.h.in`); four-case build check on hel1-14 → [pyscf/pyscf-forge#213](https://github.com/pyscf/pyscf-forge/pull/213). Row 12 closed: upstream's shipped LNO tests already call `stability_jacobi(return_status=True)` and pass on pyscf 2.14.

**Rows 15–16, 21 September 2026 (upstream, prepared; the user holds submission until the cover text and quality control are discussed).** 15: pyscf-forge `lno/lnoccsd.py`, our engine patches 1–2 as an upstream PR — pyscf/pyscf-forge#212, opened 07:2x, **converted to draft 07:3x**; patch archived as `probes/patches/pyscf_forge_lno_pyscf214_numpy2_compat_2026-09-21.patch`. 16: pyVPT2 `quartic.py` route-consistency report before averaging, docstring, tutorial DISP_SIZE guidance, three synthetic tests (pass) — local fork branch `quartic-route-consistency`, **not pushed**; patch archived as `probes/patches/pyvpt2_quartic_route_consistency_2026-09-21.patch`. Quality-control list and draft texts: `notes/PR_Drafts_2026-09-21_Upstream_Fixes.md`. Local correction pending: our `stability_jacobi()[1]` edit in the `__main__` block of `lnoccsd.py` is wrong for pyscf 2.14 (harmless, demo code) — revert.
