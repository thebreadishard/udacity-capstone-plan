# Draft: pyscf issue and PR — the Hessian's CPHF iterations are never logged (19 Oct 2026)

**Status: POSTED 19 Oct 2026 08:4x on the user's word ('Ja, plaats issue en PR'): issue pyscf/pyscf#3530, PR pyscf/pyscf#3531** (branch pushed to the fork, 3342c336c). The texts below are what was posted; the PR body adds 'Fixes #3530' and the test count.

**Edited 19 Oct ≈ 11:5x on the user's word ('Ja, pas de alinea zo aan'), before any reply:** the issue's second paragraph said the CPHF stretch shows no output at high verbosity. On acenaphthylene's T Hessian (11:4x) a 'vj and vk' timer appeared once per iteration, so the paragraph now reads: 'At high verbosity the CPHF stage is not entirely silent: for DFT the response's `vj and vk` timer lines appear once per iteration. What is missing is the Krylov solver's own progress, the residual per cycle, so a long CPHF solve shows that it is running but not how close it is to convergence.' The PR text needed no change.

**Why we found it.** On 18–19 Oct an S1-TZ optimisation ran 12 h without one log line, and a slow run looked the same as a stuck one. The user
then decided: switch on the libraries' own log levels, rather than change their code (19 Oct: 'Als we hun eigen logniveau kunnen aanzetten, dan
is dat beter'). `probes/library_log.py` does that for pyscf. Measured on water: every SCF cycle and every Hessian step timer reach the log at
verbose 5. The CPHF equations inside an analytic Hessian stay silent at every level, and for our large Hessians they are a long part of the
run (a TZ Hessian of acenaphthylene: about 4,900 s estimated). The cause is a missing argument in pyscf, not a missing level.

**The fix**, branch `hessian-cphf-logger` in `~/pyscf-wt-cphflog` (from upstream master 3d8a52be8, 18 Oct 2026). Local commit 3342c336c, not
pushed. Diff: 4 files, +28 −4.
- `pyscf/hessian/rhf.py` and `pyscf/hessian/uhf.py`, `solve_mo1`: `log = logger.new_logger(mf, verbose)` and `verbose=log` passed to
  `cphf.solve` / `ucphf.solve`. `solve_mo1` already takes `verbose`, and `HessianBase.kernel` passes its Logger, but the argument went nowhere.
- Same two files, `gen_hop`: the logger already existed; it is now passed to the solver.
- `pyscf/hessian/test/test_rhf.py`, `test_uhf.py`: `test_cphf_iterations_are_logged` runs a Hessian at verbose 5 into a `StringIO` and
  asserts that 'krylov cycle' lines are there.

**Evidence** (WSL, the worktree on `PYTHONPATH`, compiled libraries of the built master checkout `~/pyscf-master` ed6684556, 2 threads):
the two new tests fail on master's `rhf.py`/`uhf.py` (2 failed) and pass with the fix (2 passed); `test_rhf.py` and `test_uhf.py` in full,
12 passed (4 deselected by their slow markers).

Already searched (19 Oct): `gh search issues/prs --repo pyscf/pyscf` for "solve_mo1 verbose", "cphf verbose", "krylov log hessian": nothing.

---

## Issue text

**Title:** Hessian: CPHF (Krylov) iterations are never logged, at any verbosity

`hessian.rhf.solve_mo1` and `hessian.uhf.solve_mo1` accept a `verbose` argument, and `HessianBase.kernel` passes its `Logger` to it. But the
argument is not forwarded to `cphf.solve` / `ucphf.solve`. These solvers therefore run with their default `verbose=logger.WARN`, and the
`'krylov cycle %d  r = %g'` lines of `lib.krylov` never reach the Hessian's output, even with `mol.verbose = 5` or higher. The same happens in
`gen_hop` of both modules, where the logger already exists but is not passed on.

For large systems the CPHF step is a long part of an analytic Hessian, so a run at high verbosity shows no output for that whole stretch. A
slow run then cannot be told from a stuck one.

Minimal check (pyscf 2.14.0 and master 3d8a52be8):

```python
import io
from pyscf import gto, scf
mol = gto.M(atom="O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587", basis="sto-3g", verbose=0)
mf = scf.RHF(mol).run()
h = mf.Hessian()
h.verbose = 5
h.stdout = io.StringIO()
h.kernel()
print("krylov cycle" in h.stdout.getvalue())   # False; True after the fix
```

## PR text

**Title:** Pass the Hessian's logger to the CPHF solver (hessian.rhf/uhf `solve_mo1`, `gen_hop`)

Fixes #<issue>.

`solve_mo1` in `hessian/rhf.py` and `hessian/uhf.py` receives `verbose` (the Logger from `HessianBase.kernel`) but called `cphf.solve` /
`ucphf.solve` without it, so the Krylov iterations ran at the default WARN level and were never logged. This PR creates the logger in
`solve_mo1` with `logger.new_logger(mf, verbose)` and passes it to the solver; `gen_hop` passes its existing logger too. No numerical change:
only the logging target and level.

Tests: `test_cphf_iterations_are_logged` in `hessian/test/test_rhf.py` and `test_uhf.py` checks that `krylov cycle` lines appear at verbose 5.
Both fail without the change and pass with it; `test_rhf.py` and `test_uhf.py` pass in full.

---

**After posting:** a Software_Changes_Ledger row, the TASKS 'Software' row (follow-up with the others ≈ 1 Nov), and `probes/library_log.py`'s
docstring gets the issue number. Until merged and released, our CPHF stretches stay silent. Their liveness is read from CPU time and, where
installed, `py-spy dump` (rule 4 of the 19 Oct preparation).
