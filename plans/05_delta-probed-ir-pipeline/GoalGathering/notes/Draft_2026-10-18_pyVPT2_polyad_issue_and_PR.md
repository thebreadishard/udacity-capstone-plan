# pyVPT2 issue + PR: the GVPT2 polyad solver (drafted 18 Oct 2026; **posted 18 Oct 14:0x on the user's word, 'push en/of plaats je bug fixes maar': issue philipmnel/pyvpt2#60, PR philipmnel/pyvpt2#61**)

*Branch `polyad-assignment-and-merge` in the WSL worktree `~/pyvpt2-wt-polyad`, one commit eb353ab on upstream main 2eae571; not pushed.
Separate from PR #59 (branch `check-routes-before-averaging`). Found in S2 amendment 2 §1 (GVPT2 labels from our force fields): upstream's
solver raised KeyError or left polyads unmerged on S2's molecules; 7 of 14 had a bridging interaction. The reproducer below needs only
`pyvpt2.fermi_solver`; its numbers were run on 2eae571 and on the branch the same day.*

---

## Issue

**Title:** GVPT2: `Polyad.solve` can raise KeyError, and `fermi_solver` does not merge polyads that an interaction connects

**Body:**

I ran into two problems in `fermi_solver.py` while computing GVPT2 fundamentals for substituted PAHs of 12–20 atoms (B3LYP/6-31G*,
default thresholds, `FERMI` and `GVPT2` on). Both can be reproduced without psi4:

```python
import numpy as np
from pyvpt2.fermi_solver import Interaction, Polyad, State, fermi_solver

# 1. three strongly mixed states
p = Polyad(Interaction(left=State(state=(0,), nu=1000.0), right=State(state=(1, 1), nu=1002.0), phi=400.0, ftype=1))
p.add(Interaction(left=State(state=(0,), nu=1000.0), right=State(state=(2, 3), nu=1001.0), phi=400.0, ftype=2))
p.solve()          # KeyError: 2

# 2. an interaction that connects two polyads
a = Interaction(left=State(state=(0,), nu=1000.0), right=State(state=(4, 4), nu=1010.0), phi=50.0, ftype=1)
b = Interaction(left=State(state=(1,), nu=1500.0), right=State(state=(5, 6), nu=1490.0), phi=60.0, ftype=2)
bridge = Interaction(left=State(state=(1,), nu=1500.0), right=State(state=(4, 4), nu=1010.0), phi=40.0, ftype=1)
fermi_solver([a, b, bridge])
# {(0,): 991.47, (1,): 1516.92, (4, 4): 1009.8, (5, 6): 1473.29}
# eigenvalues of the single 4x4 polyad: 991.47, 1018.32, 1473.29, 1516.92
```

1. `Polyad.solve` maps each eigenvector to its largest component (`np.argmax` per eigenvector). When a polyad of three or more states is
   strongly mixed, two eigenvectors can have their largest component on the same state. In example 1 one state has squared
   coefficients of 0.333 in all three eigenvectors and is never the largest, while two eigenvectors (0.502 and 0.498) both pick the same
   other state. That state gets two eigenvalues, the first gets none, and building `freqs` raises `KeyError`.
2. `fermi_solver` adds an interaction to every existing polyad that holds one of its two states, but never merges those polyads. When an
   interaction connects two polyads, each is solved as an incomplete Hamiltonian, and a shared state gets the value of whichever polyad is
   solved last. In example 2 the overtone (4, 4) comes out at 1009.8 instead of 1018.3, with no error. With stronger couplings the
   incomplete polyads also hit the KeyError of point 1.

In our runs (12–20 atoms) 7 of 14 molecules had such a connecting interaction. I have a fix with tests and can open a PR if
that is useful.

---

## PR

**Title:** fermi_solver: merge the polyads an interaction connects, and assign eigenvalues to states one-to-one

**Body:**

Fixes #<issue>.

- `fermi_solver` collects every polyad that holds either state of an interaction. With none it starts a new polyad; with one it adds
  the interaction as before; with several it merges them (new `Polyad.merge`) and then adds the interaction. Each polyad is therefore a
  connected group of states and is solved once.
- `Polyad.solve` assigns eigenvalues to states one-to-one: it repeatedly takes the largest remaining squared coefficient (state,
  eigenvector) and retires that state and that eigenvector. When every eigenvector already has a distinct largest component, this gives
  the same result as before.

No new dependency (no scipy). Nothing outside `fermi_solver.py` changes.

**Tests** (`pyvpt2/tests/test_polyad.py`):
- `test_polyad_two_eigenvectors_peaking_on_one_state`: example 1 above. Every state gets exactly one eigenvalue, and the set equals the
  eigenvalues of the Hamiltonian. It raises KeyError on main.
- `test_fermi_solver_merges_polyads_an_interaction_bridges`: example 2 above. The result equals the single 4×4 polyad. It fails on main
  (overtone 1009.8 against 1018.3).

On main both new tests fail. On this branch they pass, and so do the existing `test_polyad.py` (3), `test_fermi_solver.py` and
`test_h2co.py` (GVPT2 on, references unchanged): 10 passed locally with psi4 1.10.2. The other molecule tests were not run.

---

*To post (on the user's word): push the branch to the fork (`git -C ~/pyvpt2-wt-polyad push -u origin polyad-assignment-and-merge`), open
the issue, then the PR against philipmnel/pyvpt2 main with the issue number filled in.*
