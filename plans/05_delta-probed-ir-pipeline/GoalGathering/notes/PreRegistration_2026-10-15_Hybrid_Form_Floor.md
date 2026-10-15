# Pre-registration — the carried head's floor: what can pattern f hold, and does that shrink with size?

Registered 15 Oct 2026, 19:4x (the user, 19:4x: 'Ja, begin maar met de registratie', after 'Dat betekent dat je je eerste meting opnieuw
gaat doen, maar dan goed?'). It replaces, for the carried model, `PreRegistration_2026-10-15_Architecture_Floor.md`, which analysed the plain
equivariant head (not carried) and measured an element-wise projection that a network can compensate (its correction section says both).
No number of this test exists yet; the data are that test's frozen inputs.

## Why

The size levers bought so far (lever 5, rung 4, the PC question) assume the error on large molecules is a learning error. The carried head
(`m05/rungC_hybrid.py`, `--head hybrid`, pattern f — chain_runner's RECIPE_V11) predicts a correction ΔF between internal primitives only on
pattern f: the diagonal, pairs sharing an atom, same-ring bond–bond pairs, and pairs whose atom sets are at most three bonds apart
(`e7_rungB_pairs.PATTERN_REACH["f"] = 3`); the Cartesian correction is ΔH = Bᵀ ΔF B. A larger conjugated molecule has more primitive pairs
farther apart than three bonds. If their correction matters, no data closes that part; a wider pattern does.

## Two quantities, both exact for this head

The map from ΔF to the read-out's matrix K (mode basis, cm⁻¹) is linear: K = scale ∘ (C ΔF Cᵀ) (`e7_t2_posthoc.k_of`). So:

1. **The form floor** — the least-squares best ΔF on pattern f for the **whole of K** (every entry of the upper triangle, equal weight),
   solved directly in the read-out's metric (minimum-norm solution, relative singular-value cutoff 1e-10, as `rungC_targets.PINV_RCOND`). No
   network on this pattern can read better on these molecules; there is no compensation route around it, because the fit already uses every
   ΔF the form allows. From the fitted K: the read-outs below.
2. **The target bound** — the read-out of the target the carried recipe trains (the projected target `rungC_targets.projected_target` masked
   to pattern f), as `probes/rungC_target_bound_holdouts.py` measured it on hold-out (a) on 1 Oct (ring-coupling ratio 0.09). A network that
   learned its target perfectly reads this.

Read-outs (both quantities): per band family (CH-stretch, CH-oop, ring-ip, other) the rms of the diagonal error of K, and the ring-coupling
ratio (rms of the ring family's off-diagonal error over the rms of its true couplings) — the read-outs of `E6.readout`, which the carried
records report.

## Data

The 534 molecules of `probes/results_m1/arch_floor_2026-10-15/inputs.tsv` (frozen 15 Oct, sha256 per file, checked again at the read): every
corpus molecule with the analytic pair. Each is loaded exactly as the trainer loads an analytic molecule (geometry, projected analytic
Hessians, the loader's B matrix and primitives, pattern f from `molecule_pairs`, families from `molecule_features`); a test checks this path
against `T2.load` + `e7_rungB_reread_analytic.substitute` on a corpus folder that has both. A molecule that cannot be loaded stops the read.

## Lines

As in the first registration, on the form floor:
1. **The form costs now:** pooled over the molecules of ≥ 25 atoms (lowered one atom at a time until at least 30 are in), the form floor is
   ≥ 1.0 cm⁻¹ in a band family, or its ring-coupling ratio is ≥ 0.10 (about half of the carried recipe's 0.22 on hold-out (a) at pool size
   750, the record of 1 Oct 2026 22:3x).
2. **The form costs at the mandate's size:** a power law fitted to the per-molecule form floor against the atom count (molecules of ≥ 10
   atoms, log–log least squares; molecules with a zero floor in a family left out of that family's fit), evaluated at 60 atoms, is
   ≥ 1.25 cm⁻¹ in a band family or ≥ 0.15 in the ring-coupling ratio. Bootstrap interval beside (1,000 resamples, seed 0). Re-read on lever
   5's large-PAH labels and layer T when they are fetched, with the same script and lines.

The target bound is read with the same lines, beside.

**What follows (registered now):**
- a form line met → a wider pattern is registered as a training comparison: chain 34's recipe with pattern f against the same recipe with
  the reach raised (four bonds, and all pairs within one fused ring system), read on hold-outs (a), (b) and the size hold-out (s);
- no form line met but a target line met → the form can hold the correction but the trained target cannot: a target comparison is registered
  (projected against the ridge target, `--aux-target ls`), read the same way;
- neither met → pattern f and its target are not the limit at these sizes; the size penalty is a learning and data question, and the PC
  question is put with that sentence.
- No scope-reducing fallback: a met line in one family is not argued away by the others.

## Limits

- The form floor is exact for the read-out on these molecules; it says nothing about learnability (whether a network finds that ΔF from
  local features). A floor near zero means the form is not the limit, not that the limit is gone.
- The proxy target (ωB97X − B3LYP), not CC − DFT.
- The data reach 35 atoms; line 2 at 60 is a forecast until lever 5's labels arrive.

## My prediction (before any number)

The diagonal is easy for the form: per molecule pattern f has more free entries than the full K has conditions only for the smallest
molecules, so the floor rises from near zero with size. At ≥ 25 atoms: diagonal floors below 0.5 cm⁻¹ in every family, ring-coupling ratio
0.03–0.08 (line 1 not met); exponent between 1 and 2, giving at 60 atoms diagonal floors of 0.5–1.5 and a ratio of 0.06–0.15 (line 2 open,
most likely in the ring couplings). The target bound above the form floor everywhere (it is one point of the form, not the best one).

## Outcome

(to be appended)
