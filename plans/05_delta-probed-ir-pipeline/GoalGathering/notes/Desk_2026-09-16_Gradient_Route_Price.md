# The price of the gradient route for the couplings (desk work, 16 September 2026)

*Written after stage C at naphthalene showed the energies-only route to the off-diagonal elements never
reaches its threshold. No new computation: every input below is measured elsewhere or is arithmetic on
measured numbers. Reproduce with `probes/price_gradient_route.py`.*

## The question

Stage C leaves two routes to the couplings: the **amplitude window** (repeat the off-diagonal block at
half the amplitude; pre-registered, ~12 h of stand-in DFT after the anchor run) and the **gradient
route** (mode G, which reached the declared threshold at 96 gradients on the same data). This note
prices the second, so the 26 September documents can quote a number rather than a promise.

## The one number everything turns on

A gradient costs **g** times an energy. M2a measured g on 14 September with PySCFAD's automatic
differentiation: **g = 2.84 at RHF and 3.20 at MP2**, inside the constant the AD literature reports.
For the method the project actually uses it was **not measurable on this laptop**: canonical CCSD(T)
took 21.0 GB resident plus 6.8 GB swap, and LNO-CCSD(T) drove the host below 1 GB free in the energy
step alone. The WSL ceiling has since been lowered from 25 GB to 20 GB (16 September), so that verdict
is now firmer, not weaker. **g at coupled-cluster level has never been printed.**

## The arithmetic

```
A. Naphthalene, the only molecule with a measured gradient count
   deck 291 energies = 114 diagonal + 177 couplings; gradient route = 114 energies + 96 gradients
   break-even g = 177/96 = 1.84

   g     energy-equivalents   vs 291   laptop-days tight   laptop-days xtight
    1.84              291     1.00x              14                   46
    2.84              387     1.33x              19                   61
    3.20              421     1.45x              20                   67
    6.00              690     2.37x              33                  109
   20.00             2034     6.99x              98                  322

B. Break-even g per molecule (ASSUMPTION: gradients needed scale with the mode count,
   anchored on naphthalene's 96. Only naphthalene is measured; the rest is arithmetic.)
   molecule        modes  coupling energies  gradients (assumed)  break-even g
   benzene           30                 67                   60          1.12
   naphthalene       48                177                   96          1.84
   anthracene        66                343                  132          2.60
   phenanthrene      66                837                  132          6.34
   pyrene            72                410                  144          2.85
   tetracene         84                561                  168          3.34
   perylene          90                646                  180          3.59
   pentacene        102                835                  204          4.09

C. Finite differences as a way to get gradients without new software
   one gradient by central differences in mode space = 2 x 48 = 96 energies, i.e. g = 96
   96 gradients = 9,216 energies against 177 for the energies route -> 52x worse. Ruled out by arithmetic, not by taste.
```

## What it says

1. **At naphthalene the gradient route is the more expensive one.** It pays only below g = 1.84, and
   the measured g at RHF/MP2 is about 3. At g = 3.2 the deck costs 1.45x the energies route: 20
   laptop-days at tight instead of 14, 67 instead of 46 at xtight. It is insurance, not a saving.
2. **It turns favourable with size**, because the pair count grows faster than the mode count: the
   break-even g rises to 2.6 at anthracene, 2.9 at pyrene, 4.1 at pentacene, and 6.3 at phenanthrene,
   whose C2v symmetry leaves far more same-irrep pairs. For the molecules the plan is built to reach,
   a gradient at g ~ 3 buys more than it costs. The gradient counts for those molecules are an
   assumption (proportional to the mode count, anchored on naphthalene's measured 96), not a
   measurement, and should be labelled as such wherever they are quoted.
3. **Finite differences are ruled out by arithmetic.** A mode-space gradient by central differences is
   2 x 48 = 96 energies at naphthalene, i.e. g = 96; the route would cost 52x the energies route.
   There is no cheap way around the missing software.

## What would have to happen for the gradient route to be usable

- **g measured at LNO-CCSD(T).** Not possible on this laptop at either ceiling. The recorded
  alternatives are PySCFAD's checkpointed LNO and a 64-128 GB machine (ledger, obstacle 7); neither is
  scheduled.
- **or frozen-space gradients built in-house** (M2, estimated 2-3 weeks), which the plan gates on
  g <= 20 - a gate that cannot be evaluated until g exists.

## Correction, 17 September 08:0x: this note priced the wrong construction

Reproducing X14 (`plans/06/experiments/x14_naphthalene_symmetry_pattern_products.py`, rerun today,
identical output) shows the 96 gradients above are its **row (d), the dense construction** — the note
says so in its own reading line: "row (d) is mode G's 2*M gradients". Row (a) uses the symmetry prior
instead: only the **141 same-irrep pairs** of naphthalene's 1,128 can be non-zero, so **9 pattern
products = 18 gradients** determine all 189 elements — the 48 diagonal ones included — with a recovery
error of **0.0e+00**, exact linear algebra rather than a fit.

That changes the arithmetic completely. The comparison is not "114 energies + 96 gradients against 291";
it is **18 gradients against the whole 291-energy deck**:

| | break-even g | at the measured g ~ 3 |
|---|---|---|
| this note's row (d) reading | 291 - 114 = 177 over 96 = **1.84** | 1.45x more expensive |
| X14 row (a), symmetry prior | 291 over 18 = **16.2** | about **5x cheaper** |

The prior that buys this is not a guess: only same-irrep pairs can couple, which is exact for a
symmetric molecule, and the plan already did the work that makes it usable — the symmetrised geometry
and irrep-projected modes of decision 37, confirmed at DFT level by I14 on 15 September. X14's rows (b)
and (c) go further on a frequency-proximity prior, to 8 and 10 gradients, but those are a guess about
the tensor and P25's loss removed the evidence for that kind of ordering; row (a) needs no such bet.

**Two things this correction does not buy.** X14 recovers with *exact* gradients; how the frozen
spaces' gradient noise propagates through a 9-product construction is untested, and is the next desk
item. And g at LNO-CCSD(T) is still unmeasured — but the bar it must clear moves from 1.84 to 16.2,
and the plan's own pre-registered gate for building in-house gradients was g <= 20, so the two are
consistent for the first time.

Also note what the 18 gradients do and do not replace: they give Delta_2 exactly. The energy deck also
supplies c0, the cubic phi_iii and the diagonal quartic used to correct the contamination; those need
their own accounting before the 291 is written off in full.

## Consequence for the 26 September documents

The amplitude test is now the cheapest decisive experiment the project owns: if the half-amplitude
block passes, the couplings stay on the energies route at naphthalene and the gradient question moves
to where it belongs, the larger molecules. If it fails, the couplings at naphthalene need either a
machine the project does not have or software it has not written - and that, stated plainly with this
table beside it, is a better thing to bring a supervisor than an unpriced fallback.
