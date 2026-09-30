# PR draft, 30 September 2026 — psi-rking/optking, branch `thebreadishard/optking:linear-bend-cycle-guard` (commit 5829c0b on master 855aa8d)

*Prepared on the user's word ("als die werkt, mag je ook een PR voorbereiden"); **opened 30 Sep 07:5x as psi-rking/optking#116** on the user's authorisation of 07:4x (no existing fix upstream; tests; explanation). Fixes #115.*

## Title

Guard against a silent infinite loop on linear-bend cycles; treat a near-0° interior angle as a reset, not a linear bend (#115)

## Description (as it would be posted)

Fixes #115.

`linear_torsion_check` labelled an interior angle near 0° — the torsion running through a terminal atom, a connectivity artefact — as a linear bend
and added permuted "safety" bends with that terminal atom as vertex. The collinear-segment torsion search in `add_tors_from_connectivity` then walked
those LINEAR bends with `J = i; i = 0; continue`, without a visited set or a bound, and spun forever without logging once the LINEAR bends formed a
cycle (observed: five hours at one core on an ethynyl-naphthalene, psi4 1.11 / optking 0.5.0; details and logs in #115).

Changes:

- `v3d.linear_torsion_check`: an interior angle below `phi_lim` raises `AlgError(back_transformation=True)` — the existing reset path — instead of
  reporting new linear bends. Angles near 180° are handled as before.
- `addIntcos.add_tors_from_connectivity`: both outward walks keep a visited set and raise `AlgError(back_transformation=True)` when a LINEAR bend leads
  back to a visited atom, so an inconsistent coordinate set fails in the open instead of hanging.
- `tests/test_linear_bend_cycle.py` (pure python, no QC engine): near-0° resets; near-180° still reports linear bends; a four-atom coordinate set with
  LINEAR bends 0-1-3 and 1-0-3 fed to `add_tors_from_connectivity` raises instead of looping. The last test runs in a subprocess with a timeout, so a
  regression fails the suite instead of hanging it. On the unpatched tree the cycle test times out (60 s) and the near-0° test fails; on this branch
  all three pass.

Effect on the input of #115 with this branch applied to 0.5.0: no hang; 5 `AlgError`s instead of 19 (the remaining ones are the legitimate
back-transformation failures of that geometry); the optimisation still does not converge within 50 iterations in internal coordinates — that is now a
clean failure, and `opt_coordinates cartesian` optimises the molecule. I have not run the full test suite (it needs psi4 as the compute engine; the
three new tests were run with `--noconftest`); happy to adjust wording, placement of the guard, or the exception type if you prefer a different
behaviour.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Before opening

- [ ] the user's word
- [ ] rebase on upstream master at that moment
- [ ] run the three tests once more on the rebased branch
