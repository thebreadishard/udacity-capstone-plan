# Presentation dependence: the proposed repair

23 November 2026. TASKS 287. A proposal, agreed by the user on 23 November ('Ja, werk rij 287 bij'); nothing of it is built or
measured beyond what is cited below.

## The issue and its name

The network's answer for one molecule changes when the same molecule is presented differently: turned in space, mirrored, or with
its atoms listed in another order. The user named it **presentation dependence** on 23 November. A rotation, the mirror image and an
atom listing are three presentations of one molecule; aromir's code already uses 'presentation' and 'own spread'.

Measured on 19 November with v1.4's release networks, largest band change in cm⁻¹
(`probes/results_m1/frame_audit_2026-11-19/table.md`, `probes/results_m1/linear_angle_rotation_2026-11-19/README.md`):

| molecule | mirror | atom listing | rotation |
|---|---|---|---|
| 9-methylanthracene | 9.95 | 10.00 | 0.000 |
| diphenylacetylene | 4.46 | 11.03 | 11.20 over eight rotations |
| biphenyl | 2.67 | 2.85 | 0.000 |
| benzonitrile | 0.24 | 0.97 | 2.42 |
| benzene | 0.08 | 0.18 | 0.000 |

The equivariant body is not the cause: with the stored inputs carried through the reflection the change is 0.000 for every molecule.
Every change comes from the inputs prepared on the internal-coordinate side, which the hybrid head reads.

## Do others have it

Not in this form. geomeTRIC is made for geometry optimisation, where a reference direction taken from the coordinate axes does no
harm; it becomes a defect only when the coordinates are the input of a learned model that must answer the same for a turned
molecule. The sign part is a known class in machine learning on molecules: a number whose sign rests on a convention (a dihedral, an
out-of-plane coordinate, an eigenvector) makes the answer follow the convention. Models that work on positions alone and are fully
equivariant do not have it. Ours is a mixture, an equivariant body with a head on force constants in internal coordinates, and the
leak is on that seam. It is a consequence of our own design choice.

## The proposal

Repair it at the source: make the network's inputs free of the presentation by construction, prove it with a fixed test, then retrain
once. Not an average over presentations, and not another architecture.

1. **Linear group.** The reference direction of a linear bend comes from the molecule, not from the coordinate axes: one shared
   function in m05 and aromir, applied after `PrimitiveInternalCoordinates`. Tested with v1.4's own weights: diphenylacetylene
   11.20 → 1.5e-5, benzonitrile 2.38 → 7e-6, phenylacetylene 1.52 → 1.3e-5 cm⁻¹; the 947 molecules without a linear group are
   unchanged.
2. **Signs.** The network sees sign-free numbers only (the cosine of a dihedral, the magnitude of a force constant); the sign is put
   on the output afterwards, so the output follows the convention. The switch exists (`parity_odd`, built and tested 13 October,
   TASKS 52) and is in no version. **The open design work is here:** `parity_odd` does not combine with the 66 pair features, which
   carry signed primitive values; those features must be made sign-free first.
3. **Atom order.** Every choice that now follows the listing becomes a choice made from the molecule: the `canonical` angle and
   out-of-plane choice (exists, not carried), ties broken by geometry instead of input order (NO₂ oxygens, methyl hydrogens), the
   `cos` encoding against the 2π jump at ±π.
4. **A test as a gate.** A fixed set of molecules (a linear group, out-of-plane coordinates, a symmetric molecule, ties) on which
   the inputs, up to a declared convention, and the printed band positions, to 0.01 cm⁻¹, stay the same under every presentation,
   in m05 and in aromir. No training before it passes.

Then one retraining of the measurement and the release networks on the repaired inputs, with TASKS 236's pseudo-inverse cutoff in
the same run, a new invariance record, and the licence per group returning by itself (TASKS 288).

## Why this one

Three routes exist; the reasons are our own measurements first, the literature second.

**Averaging over presentations (frame averaging; Puny et al. 2021).** Our read of 16 November
(`probes/results_m1/order_mean_2026-11-16/`, partial: hold-out (a) and 12 of 39 of (b)): the mean over rotations, the mirror image and
the product's own order is stable, not better (ring in-plane / CH-stretch / CH out-of-plane / other 1.45 / 0.95 / 1.60 / 2.74 at
K = 1, 1.42 / 0.95 / 1.62 / 2.76 at K = 64); K = 64 is needed to stay within 0.5 cm⁻¹ between two draws; an arbitrary atom order
gives 3.47 on ring in-plane against 1.43, and no mean repairs that. In theory too: for permutations no finite frame keeps the averaged
function continuous (Dym, Lawrence and Siegel 2024). And a mean leaves a network standing that was trained on arbitrary conventions.

**A fully equivariant head on positions.** Recent models predict the Hessian directly from equivariant features up to l = 2 (HIP,
Burger et al. 2025) and cannot have this defect. For us it gives up the project's core: the correction in local coordinates, chosen
because it carries from small to large molecules. We had a Cartesian head and moved to the hybrid one; that comparison was not
re-measured for this note. Kept as a second route to check the first, not as a replacement.

**Invariance built into what the network reads.** The work on eigenvectors with an arbitrary sign (SignNet, Lim et al. 2022) argues
the same: build the invariance in rather than approximate it by random sign flips in training. For a dihedral, cosine and sine
together keep the whole angle: the cosine is sign-free, the sine carries the sign, which is the split of item 2. It is the only route
that makes the answer equal rather than nearly equal, and the test can prove it. Half of it exists already.

## Cost and what is not known

- One retraining of six networks; at the present 3–5 hours per training on the laptop, more than a day.
- Not known: whether the error per kind of vibration stays where it is when the network no longer sees the signs. It may improve,
  since part of what it fits now is convention, or get somewhat worse. Read on both hold-outs after the retraining.
- Order: design and test at the desk, on a branch in its own worktree, with a review; the retraining after the v1.4 search, so after
  25 November.

## Sources

- Lim et al., Sign and Basis Invariant Networks for Spectral Graph Representation Learning, arXiv:2202.13013.
- Puny et al., Frame Averaging for Invariant and Equivariant Network Design, arXiv:2110.03336.
- Dym, Lawrence and Siegel, Equivariant Frames and the Impossibility of Continuous Canonicalization, arXiv:2402.16077.
- Ma et al., A Canonicalization Perspective on Invariant and Equivariant Learning, arXiv:2405.18378.
- Burger et al., Shoot from the HIP: Hessian Interatomic Potentials without derivatives, arXiv:2509.21624.
- arXiv:2109.11576, on sine and cosine of a dihedral as a network input.

The literature was searched on 23 November with four web queries and read from the result summaries, not from the papers' full
texts; a claim that rests on one of them is to be checked against the paper before it enters a manuscript.
