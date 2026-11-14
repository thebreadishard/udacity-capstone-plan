The second order SCF solver inherits `conv_tol_grad` from the object it decorates, and nothing says so

`_CIAH_SOSCF.__init__` copies the decorated object's `__dict__`, and `SecondOrderSCF.kernel` passes `self.conv_tol_grad` on to
`newton_ah.kernel`. A `conv_tol_grad` that the first order solver reached can be below what the CIAH solver can reach for the system
at hand, where its attainable orbital gradient is limited by the numerical noise of the integrals and, for KS methods, of the
exchange-correlation grid. The solver then spends all of `max_cycle` and reports no convergence although the energy has settled.

How we ran into it, twice on the same 60-atom PAH (C42H18, B3LYP and ωB97X/6-31G\* on a (99,590) grid, `conv_tol = 1e-11` and
`conv_tol_grad = 1e-8` set for the DIIS run, then `mf.newton()` as the fallback):

- **the gradient threshold.** The solver ran its 50 macro iterations in 2.8 hours and stopped at `|g| = 1.83e-8` with
  `delta_E = 4.5e-11`. With `conv_tol_grad` left unset on the Newton object it reaches the derived `sqrt(conv_tol)` in a few macro
  iterations, and the plain SCF restart from its density then converges.
- **the energy threshold**, on the other functional, where that remedy cannot help. The macro iterations show the calculation's own
  floor: `delta_E` oscillating at 1.0 to 1.4e-10 with the sign flipping and `|g|` flat at 2.75e-8. `conv_tol = 1e-11` is below that
  floor, so neither solver can ever report convergence, and `conv_tol_grad = None` makes no difference because the unmet criterion is
  the energy. Only raising `conv_tol` to something the calculation can reach helps, and unlike `conv_tol_grad` it has no derived
  default to fall back on.

Both cases cost us hours of a run that was, physically, converged. That is why the note mentions the attributes being copied rather
than only the one remedy.

### Change

- `pyscf/soscf/newton_ah.py`: the `_CIAH_SOSCF` docstring says that the decorated object's attributes are copied onto the Newton
  solver, `conv_tol` and `conv_tol_grad` included, what that costs when the tolerance is out of reach, and that
  `conv_tol_grad = None` on the Newton object restores the derived default.
- `examples/scf/22-newton.py`: the same in five lines, on the H2 object the surrounding blocks already use.

Documentation only; no behaviour changes.

### Considered and not included

A `logger.warn` when the solver ends unconverged with `|g|` above `conv_tol_grad` but below `sqrt(conv_tol)` would have saved us the
2.8 hours, and an extra `log.info` of the inherited value turned out to be redundant because `dump_flags` already prints
`conv_tol_grad` at verbose 4. Happy to add the warning if you would like it; it seemed a behaviour question rather than a
documentation one, so it is not in this PR.

### Tests

- [x] `pytest -q pyscf/soscf/test/test_newton_ah.py`: 26 passed.
- [x] `python examples/scf/22-newton.py` runs to the end; the four printed energies match their references to 1e-10 and the new block
      converges to the same energy as the neighbouring runs on that object.
- [x] `ruff check --config .ruff.toml` and `ruff check --select NPY --ignore NPY002` on both changed files: no findings.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
