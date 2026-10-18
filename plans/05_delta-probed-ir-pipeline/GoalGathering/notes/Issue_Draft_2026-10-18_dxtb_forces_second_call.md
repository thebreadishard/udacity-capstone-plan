# dxtb issue + PR: a second positions tensor reuses component caches, and the forces are wrong (drafted 18 Oct 2026; **not posted — waits for the user's word**)

*Found while validating dxtb's GFN2-xTB against the xtb 6.7.1 binary for S2 amendment 4 (memory 'reference-dxtb-pitfalls'). Reproduced
on dxtb 0.4.0 from PyPI (WSL env `dxtb`, Python 3.11, numpy 1.26.4, tad pins of 0.4.0) and on `main` 2070660 (env `dxtb-np2`), torch
2.14.1 CPU. Fix: branch `driver-setup-graph` in the WSL worktree `~/dxtb-wt-cache`, one commit 3cda67e on `main` 2070660, not pushed (the
branch name predates the final fix, which is in the calculator decorator, not the driver). Our own code uses a fresh calculator per
quantity and was never affected.*

---

## Issue

**Title:** Forces are wrong when the calculator already holds caches from another positions tensor with the same values

**Body:**

On the same calculator, a second `forces` call returns different forces from the first, and the second result is wrong. This happens after
`energy()` and after an earlier `forces()`. Calling `reset()` in between gives the correct result again. Minimal example (water, positions in bohr):

```python
import torch
from dxtb import GFN2_XTB
from dxtb.calculators import AutogradCalculator

dd = {"dtype": torch.double, "device": torch.device("cpu")}
numbers = torch.tensor([8, 1, 1])
positions = torch.tensor([[0.0, 0.0, 0.2217], [0.0, 1.4309, -0.8867], [0.0, -1.4309, -0.8867]], **dd)
opts = {"int_driver": "libcint", "verbosity": 0}

def forces(calc):
    return calc.forces(positions.clone().requires_grad_(True), 0).detach()

a = forces(AutogradCalculator(numbers, GFN2_XTB, opts=opts, **dd))   # A: fresh calculator

c = AutogradCalculator(numbers, GFN2_XTB, opts=opts, **dd)
c.energy(positions.clone(), 0)
b = forces(c)                                                          # B: energy first, then forces

c = AutogradCalculator(numbers, GFN2_XTB, opts=opts, **dd)
c.energy(positions.clone(), 0)
c.reset()
r = forces(c)                                                          # C: energy, reset(), forces

c = AutogradCalculator(numbers, GFN2_XTB, opts=opts, **dd)
forces(c)
s = forces(c)                                                          # D: forces called twice
```

| case | force z(O) (E_h/bohr) | max abs difference from A |
|---|---|---|
| xtb 6.7.1 binary (`--grad --acc 0.0001`), as −gradient | −0.002972 | — |
| A fresh calculator | −0.002972 | — |
| B `energy`, then `forces` | +0.075518 | 7.9e-2 |
| C `energy`, `reset()`, then `forces` | −0.002972 | 1e-16 |
| D `forces` twice (second call) | +0.075518 | 7.9e-2 |

GFN1 is affected the same way, with both the PyTorch and the libcint integral driver. This holds on 0.4.0 and on `main`.

**Cause, as far as I can see.** The classical, interaction and integral caches are reused when the *values* of the positions match. For
example, the integral driver's `is_latest()` compares values. `forces` gets a new tensor each time, and so does `energy`, which builds
the caches without a graph. Autograd then cannot see how the reused caches depend on the new positions, so those terms are missing from
the forces. `reset()` clears exactly those caches, which is why case C is right.

**Workaround** until it is fixed: call `calc.reset()` (or use a new calculator) before computing forces on a new positions tensor.

I have a small fix with a regression test and will open a PR.

---

## PR

**Title:** Reset component caches when forces get a new positions tensor

**Body:**

Fixes #<issue>.

`requires_positions_grad` now keeps a weak reference to the positions tensor that the last graph was built for. When `forces` (or
another method behind that decorator) gets a different tensor, it first clears the classical, interaction and integral caches. These are
the caches `Calculator.reset()` clears, apart from the result cache, which is already keyed on the tensor id. Calls with the same tensor
keep using the caches, so repeated derivatives of one graph are not slowed down.

**Test:** `test/test_calculator/test_cache/test_positions_graph.py` covers forces after `energy`, and `forces` twice with a new tensor,
for GFN1 with the PyTorch driver and, when libcint is available, for GFN1 and GFN2 with libcint. All 6 cases fail on `main` (2070660) and
pass on this branch.

**Other tests run locally** (Python 3.11, torch 2.14.1 CPU, the tad versions `main` pins, tad-libcint 0.3.0):
- `test/test_calculator`: 60 passed
- `test/test_singlepoint/test_grad_gfn1.py`: 42 passed
- `test/test_singlepoint/test_grad_gfn2.py`: 18 passed
- `test/test_singlepoint/test_hess.py`: 3 passed
- `test/test_properties/test_hessian.py`: 7 passed
- `test/test_properties/test_vibration.py`: 3 passed
- `test/test_properties/test_dipole_deriv.py`: 8 passed

The rest of the suite was not run.

---

*To post (on the user's word): push the branch to a fork of grimme-lab/dxtb (none exists yet: `gh repo fork grimme-lab/dxtb`), open the
issue, then the PR against `main` with the issue number filled in. The numpy-2 work (ledger row 49) is a separate change.*
