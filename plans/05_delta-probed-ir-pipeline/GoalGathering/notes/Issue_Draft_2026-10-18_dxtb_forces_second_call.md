# dxtb issue: a second call on the same AutogradCalculator returns wrong forces (drafted 18 Oct 2026; **not posted — waits for the user's word**)

*Found while validating dxtb's GFN2-xTB against the xtb 6.7.1 binary for S2 amendment 4 (memory 'reference-dxtb-pitfalls'). Reproduced
the same day on dxtb 0.4.0 from PyPI (WSL env `dxtb`, Python 3.11, numpy 1.26.4) and on `main` 2070660 (env `dxtb-np2`, Python 3.12,
numpy 2.5.4, newer tad set), torch 2.14.1 CPU, tad-libcint 0.3.0. Our own code avoids it with a fresh calculator per quantity.*

---

**Title:** AutogradCalculator: `forces` returns a wrong result when the calculator has already computed `energy` or `forces` (unless `reset()` is called)

**Body:**

On the same `AutogradCalculator`, a second call returns a different force from the first, and the second one is wrong. Calling
`reset()` in between gives the correct result again. Here is a minimal example: water with GFN2-xTB, positions in bohr.

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

The same numbers come out with the options of `test/test_properties/test_hessian.py` (`scf_mode: full`, `mixer: anderson`,
`f_atol = x_atol = 1e-10`), on dxtb 0.4.0 from PyPI and on `main` (2070660), with torch 2.14.1 on CPU and the libcint driver. That
driver is needed for GFN2: with the PyTorch driver the constructor raises 'Multipole integrals not available'.

My guess is that the first call leaves a cached result, for example an SCF state with no autograd graph, which the second call reuses
instead of recomputing. If reuse is meant to happen, it would be safer to key the cache on the positions and on whether a graph is
needed. Otherwise the second call could raise an error rather than return a different number. I'm happy to help with a test.

---

*To post (on the user's word): `gh issue create --repo grimme-lab/dxtb` with the title and body above.*
