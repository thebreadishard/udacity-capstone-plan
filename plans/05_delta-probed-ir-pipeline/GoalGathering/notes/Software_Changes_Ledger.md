# Software changes made in this project — ledger for possible upstream contributions

*Started 2026-09-12 on the user's request: keep a list of every change we make to third-party software, and of
every piece of our own code that fills a gap upstream, so that we can decide later which to offer as pull
requests. One row per change; "status" says whether it is a local patch, a wrapper, or our own code; "PR
candidate" is an assessment, not a decision. Nothing has been submitted anywhere.*

## A. Patches to third-party code (applied in our environment, re-applied after every reinstall)

| # | date | software | change | why | files | PR candidate |
|---|---|---|---|---|---|---|
| 1 | 2026-09-10 | pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py`), against pyscf 2.14.0 | the call into pyscf's DF `vvvv` routine updated to pyscf 2.14's seven-argument signature | pyscf 2.14 changed the signature; pyscf-forge 1.1.1 still calls the old one and crashes on every DF-LNO run | `probes/patches/apply_pyscf_forge_dfvvvv_patch.py`, `pyscf_forge_1.1.1_lnoccsd_dfvvvv_pyscf2.14.patch` | **yes** — a plain compatibility fix; check first whether pyscf-forge `master` already has it (it may, if they track pyscf releases) |
| 2 | 2026-09-12 | pyscf-forge 1.1.1 (`pyscf/lno/lnoccsd.py::_cp`) | `np.array(a, copy=False, order='C')` → `np.asarray(a, order='C')` | under NumPy 2, `copy=False` raises when a copy is unavoidable — it is, when the fragment's Lov block is an h5py slice on disk (`max_memory` below its size); the out-of-core path was dead under NumPy 2 | `probes/patches/apply_pyscf_forge_numpy2_cp_patch.py`, `pyscf_forge_1.1.1_lnoccsd_numpy2_cp.patch` | **yes** — the NumPy migration guide's prescribed fix; one line; likely unknown upstream because it only triggers out of core |
| 9 | 2026-09-13 | PySCFAD 0.3.3 (PyPI 2026-06-29; jax ≥ 0.9.1 < 0.11, pyscfadlib ≥ 0.3.3, pyscf ≥ 2.3, pyscf-properties; Apache-2.0) | **adopted, not changed**: pinned as the engine of milestone M2a (the gradient-to-energy cost ratio g), **installed 2026-09-13 ≈ 01:10 with the user's permission** in the separate WSL env `~/qcad` (Python 3.12.14 from qc05's base; `pip install --only-binary=:all:`, low priority, beside the running anchor job): jax 0.10.2, jaxlib 0.10.2, pyscf 2.14.0, pyscfad 0.3.3, pyscfadlib 0.3.3, ml_dtypes 0.6.0; `pyscf-properties 0.1.0` from its pure-Python sdist (79 kB, no wheel on PyPI); 894 MB; `qc05` untouched; `pyscfad.lno` exports `LNOMP2`, `LNOCCSD`, `LNOCCSD_T` | the evidence ladder's step 4: no paper prints g; decision 34's substitution layer, X11 and mode G all hang on it | `notes/PreRegistration_2026-09-13_M2a_Gradient_Cost_Ratio.md`, `probes/m2a_gradient_cost_ratio.py` | none yet; a PR candidate only if the LNO threshold convention or the checkpointing needs a patch for our use |

## B. Our own layers around third-party code (no upstream file touched)

| # | date | software | what we built | gap it fills | files | PR candidate |
|---|---|---|---|---|---|---|
| 3 | 2026-09-12 | pyscf-forge LNO-CCSD(T) | `CheckpointedLNOCCSD_T`: per-fragment JSON checkpoint written after each fragment's solve; restored fragments are returned without solving on a resumed run; localised orbitals saved/reloaded so the fragments are identical | upstream `lno.py` has "[ ] chkfile / restart" on its own TODO list (line 53); we lost a 3.5-hour run to a host crash | `probes/lno_checkpoint.py`; used by `anchor_single_point_timing.py --resume` (tested exact on benzene cc-pVDZ, 2026-09-12 16:46) and, since the same evening, by `m1_frozen_spaces.py` (both arms; one checkpoint per point and arm under `fragments/`, per-point localisations cached; **built, untested** — smoke test on the benzene cc-pVDZ chain owed after the naphthalene timing) | **yes, as a proposal** — the natural upstream form is a `chkfile` attribute on the kernel; ours is a subclass, which upstream would rewrite; the value is the design and the test |
| 4 | 2026-09-10/12 | (shell) | `probes/launch_detached.sh`: setsid/nohup launcher with an hourly heartbeat line (elapsed, CPU, RSS, scratch size) | none upstream; project tooling | `probes/launch_detached.sh` | no |
| 5 | 2026-09-09/10 | pyscf-forge LNO (semantics, not code) | frozen-space arms A/B/C and the composite energy in `m1_frozen_spaces.py` (holding LNO spaces fixed across geometries, semicanonicalisation at each geometry, transported orbital blocks) | a research object of plan 05, not a fix | `probes/m1_frozen_spaces.py` | not as a PR; possibly as a paper/example later |

## C. Findings about third-party software worth reporting (no code change by us)

| # | date | software | finding | where recorded | action |
|---|---|---|---|---|---|
| 6 | 2026-09-10 | PAHdb theoretical library v4.00 as served | the served XML carries the v3.00 scale factors (0.9794/0.9691/0.9597), not the three the v4.00 paper describes | `modules/02_opponent_atlas/REPORT.md`; plan 05 decision 30 | ask the PAHdb maintainers when the module is submitted (item on the user's list, not done) |
| 7 | 2026-09-12 | Hessian QM9 (Williams et al. 2025) | fetch script's expected size was the whole figshare record, not the archive (6,281,831,499 B); frequencies column 1 is the imaginary magnitude; translation/rotation modes not projected | `modules/05_support_predictor/out/HESSIAN_QM9_SUMMARY.md` | none needed (documentation notes, not bugs) |

## D. Lean 4 / Mathlib (plan 06)

| # | date | software | what we proved / built | gap upstream | files | PR candidate |
|---|---|---|---|---|---|---|
| 8 | 2026-09-12 | Mathlib `v4.34.0-rc2` | `exists_proper_on_finset` + `colorable_maxDegree_succ`: a finite simple graph with maximum degree Δ is (Δ+1)-colourable (greedy bound) | Loogle on 2026-09-12: no declaration mentions both `SimpleGraph.Colorable` and `SimpleGraph.maxDegree`; `Coloring/Vertex.lean` has no degree bound, no greedy colouring, no Brooks | `plans/06_…/lean/Plan06/T1/MeasurementAlgebra.lean` | **yes** — small, general, in Mathlib style already; would go to `Mathlib/Combinatorics/SimpleGraph/Coloring/` after re-checking `master` (Mathlib moves fast); the rest of T1 (patterns, probes, symmetric consistency) is project-specific and stays here |

## How to use this ledger

- Add a row the day a change is made; never after the fact from memory.
- Before proposing any PR: re-check the upstream `master` (the fix may exist), write a minimal test, and
  follow the project's contribution guide. The user decides which to submit and when; nothing here commits
  us to anything.
