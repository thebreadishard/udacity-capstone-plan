# Three ideas for getting coupled-cluster quality cheaper

Written 25 Nov 2026 23:50, on the user's request ('denk vannacht even goed na over mogelijke manieren … om CC sneller te maken …
3 uitgewerkte ideeën'). Ideas, not results: each names its first test, what that costs and what would kill it. Nothing here has
been run except the one check under idea 3, on Hessians we hold.

## Where the cost and the error sit (what the ideas rest on)

- Our reference is H = CCSD(T)/cc-pVDZ + (MP2/X − MP2/cc-pVDZ). The CCSD(T) part is the price; the MP2 step is minutes.
- On benzene the error against CCSD(T)/ano-pV5Z is 7.6 / 30.2 / 8.9 cm⁻¹ (C–H stretch / out of plane / other in plane), and the
  full CCSD(T)/cc-pVTZ Hessian is no cure: 3.7 / 27.0 / 6.1 (`ano_step_read.py`, 25 Nov).
- The out-of-plane fault is a known basis-set artefact of correlated methods on planar arenes, cured by ANO sets
  ([Martin, Taylor & Lee 1997](https://doi.org/10.1016/s0009-2614(97)00735-5); [Moran et al. 2006](https://doi.org/10.1021/ja0630285)).
  The 2023 benzene paper ([Semidalas & Martin 2023](https://doi.org/10.1080/00268976.2023.2263593)) reports, as read on 23 Nov
  (TASKS 300): ω4 / ω5 −4 / −6 cm⁻¹ with ano-pVTZ, still −17 / −14 with cc-pVTZ-F12, and a composite of MP2/ano-pVQZ with
  [CCSD(T) − MP2]/ano-pVTZ at 3.0 cm⁻¹ rms.
- Our own diagnostic (25 Nov, held Hessians): [CCSD(T) − MP2] changes from cc-pVDZ to cc-pVTZ by −1.6 / +7.1 / +8.1 cm⁻¹ on
  ω4 / ω5 / ω17. So part of the fault is in the difference itself, in the Dunning family.

So "faster CC" has two meanings here, and the ideas take both: the same quality from a **smaller** CC calculation (1, 2), and
**fewer** CC calculations (3).

## Idea 1 — The right small basis instead of a bigger one: [CCSD(T) − MP2] in a double-zeta ANO set

**The thought.** Everyone, we included, reads the out-of-plane fault as 'the basis is too small'. The literature says something
narrower: it is an imbalance of the Dunning sets on planar rings. If that is so, a double-zeta set of the ANO family
(C [3s2p1d], H [2s1p] — 114 functions on benzene, the same as cc-pVDZ) may give a [CCSD(T) − MP2] difference that is already
close to the converged one. The CCSD(T) calculation then costs exactly what it costs today; only the integrals are slower,
which is nothing beside the CC iterations. The published composite does this with ano-pVTZ; nobody we have read reports it
with the double-zeta member.

**The recipe.** H = MP2/ano-pVQZ (or the MP2 limit) + [CCSD(T) − MP2]/ano-pVDZ.

**First test, benzene.** One CCSD(T)/ano-pVDZ Hessian by our anchor route (6 symmetry-unique displacements; the cc-pVDZ one ran
on the laptop) and the MP2/ano-pVDZ rows (minutes). The MP2/ano-pVQZ rows are being computed tonight. Read with
`ano_step_read.py` after one more recipe is registered. **Lines to register beforehand:** the same three groups; success if out
of plane ≤ 10 and no group worse than the control.

**What we hold.** A Basis Set Exchange file named ano-pVTZ that has a double-zeta shape (25 Nov, `basis/SOURCE.md`); whether it
is the real ano-pVDZ must be settled against the paper's supporting information (the user's download) before use. pyscf must
read a generally contracted set for the CC part (its NWChem format does; to be checked on water against psi4, energy to 1e-8).

**What kills it.** The double-zeta ANO difference is as far off as the cc-pVDZ one. Then the artefact needs f functions on
carbon, and idea 2 is the next cheapest.

**If it holds.** Every anchor so far was made in cc-pVDZ, so the CC part would be recomputed — at the price already paid once
(18 anchors and wave 1), not at a triple-zeta price. That is a decision with a bill, for the user.

## Idea 2 — Split the expensive part: CCSD in the larger basis, (T) only in the small one

**The thought.** CCSD(T) is two calculations. CCSD scales with the sixth power of the size and has density-fitted gradients;
the (T) part scales with the seventh, and its gradient is the memory peak of our runs. The (T) contribution is small and is
known to converge with the basis faster than CCSD does. So: H = CCSD/large + [(T)]/small + the MP2 step beyond. If the
out-of-plane artefact sits in the CCSD part, the seventh-power step never has to leave the small basis.

**First test, free of new method work.** Take the difference apart on benzene: CCSD-only Hessians in cc-pVDZ and cc-pVTZ (the
CCSD gradient is an intermediate of every CCSD(T) gradient we ran, but we did not keep it — to be recomputed: cc-pVDZ on the
laptop, cc-pVTZ a server day at most, to be timed first). Then [(T)]/DZ against [(T)]/TZ on ω4, ω5, ω17, as the diagnostic of
25 Nov did for [CCSD(T) − MP2]. **Line:** the (T) part changes by less than 2 cm⁻¹ between the two sets on every mode.

**What it buys.** To be measured, not promised: the share of (T) in the wall time and memory of our own cc-pVTZ benzene run
(the logs of `e8_benzene_ccpvtz_oop_2026-10-03` hold both). If (T) is most of it, a CCSD/ano-pVTZ + (T)/DZ reference becomes
payable for the small anchors, and psi4's density-fitted CCSD gradient (the DFOCC module we already use for open-shell MP2)
is the candidate engine — an upstream test of that call has to be found and cited before any run (the rule of 29 Sep).

**What kills it.** The (T) part carries the artefact (changes by 5 cm⁻¹ or more). Then splitting saves nothing for these modes.

**It combines with idea 1:** CCSD/ano-pVTZ + (T)/ano-pVDZ is the natural pair.

## Idea 3 — Compute the missing piece once per building block and transport it

**The thought.** What the MP2 step misses is one object: R = [CCSD(T) − MP2]/large − [CCSD(T) − MP2]/small, a correction to the
Hessian. If R is local — made of blocks that belong to an atom and its near neighbours and look the same in every molecule
with that neighbourhood — it does not have to be computed per molecule at all. It is computed once, on the smallest molecules
that contain each building block (a ring C–H, a fusion carbon, an aza nitrogen, a nitrile …), at a level we could never pay
for a PAH (CCSD(T)/ano-pVQZ on benzene-sized molecules is a SURF-sized job, not a laptop one), and then added to every cheap
composite. This is the project's own mechanism — the family block with its couplings within two bonds carried a parent's
correction to 1.7 cm⁻¹ on the proxy task (E9, 24 Sep) — applied to the reference itself instead of to the network.

**Checked tonight on what we hold** (`probes/results_m1/cc_speed_ideas_2026-11-25/residual_locality_benzene.py`; benzene, R
between cc-pVDZ and cc-pVTZ, frequencies as computed, compared with the full CCSD(T)/cc-pVTZ Hessian):

| pairs of R kept | rms over the 20 modes (cm⁻¹) | rms out of plane (cm⁻¹) |
|---|---|---|
| none (the composite) | 4.62 | 6.23 |
| same atom only | 2.31 | 2.23 |
| within 1 bond | 1.32 | 1.55 |
| within 2 bonds | 0.61 | 0.73 |
| within 3 bonds | 0.19 | 0.34 |

So on benzene the missing piece is carried to 0.6 cm⁻¹ by blocks within two bonds. Benzene is small (its farthest atoms are 5
bonds apart) and this says nothing yet about transfer **between** molecules: an indication, not a test.

**First real test.** Transfer: take R's blocks from benzene and apply them, by the E9 mapping, to a second molecule for which
the full large-basis Hessian exists, and compare. We hold a full CCSD(T)/cc-pVTZ Hessian only for benzene, so this needs one
more: pyridine or fluorobenzene (benzene-sized; the cost of benzene's, to be read from its log). **Line:** the transported R
brings the second molecule's composite to within 2 cm⁻¹ rms of its own full Hessian, per group.

**What kills it.** R's blocks differ between molecules by as much as R itself (a ring C–H in pyridine is not a ring C–H in
benzene at this level). Then R is a property of the molecule and has to be learned by the network like everything else — which
is still a use: R on thirty small molecules as a training target of its own.

**Why it may matter most.** It is the only one of the three whose price does not grow with the size of the molecule, and it
turns SURF time into a few very good small calculations instead of many mediocre large ones.

## Smaller things, not counted among the three

- **Start each displaced CC calculation from the reference geometry's amplitudes** (t1, t2 and the lambdas). Whether our anchor
  runner already does this is to be checked in the code; if not, it may halve the CCSD and lambda iterations and costs a few
  lines. It does nothing for the (T) step.
- **Not pursued, and why:** explicitly correlated F12 sets (the 2023 paper: ω4 / ω5 still −17 / −14 with cc-pVTZ-F12, and no
  open-source CCSD(T)-F12 gradient that we know of); local-correlation CCSD(T) (no analytic gradient with triples in the
  open-source codes we use); a GPU port of the CC gradient (our own software project, months, and not our problem's bottleneck
  while the basis is).

## Order suggested

Idea 3's check was free and is done. Idea 1 is the cheapest real test (one benzene Hessian at today's price) and decides the
most; idea 2's diagnostic costs about a server day; idea 3's transfer test costs one more benzene-sized cc-pVTZ Hessian. Each
needs a registration before its run, and a paid server needs the user's word.
