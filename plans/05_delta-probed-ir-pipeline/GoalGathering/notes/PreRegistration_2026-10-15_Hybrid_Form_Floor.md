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

## Outcome (15 Oct 2026, 21:0x)

Read through `tools/runspec.py` (run `hybrid_floor`, 19:55–21:0x, exit 0) on the frozen 534; `probes/results_m1/hybrid_floor_2026-10-15/`
(`floor.md`, `floor.json`); line 1's bound 24 atoms (30 molecules). Beside, exploratory and written after the read:
`probes/hybrid_floor_by_size.py` → `by_size.md`.

**Line 1 (≥ 24 atoms, pooled):**

| read-out | form floor | target bound | line |
|---|---|---|---|
| ring-ip | 0.107 | **1.126** | 1.0 cm⁻¹ |
| other | 0.022 | 0.267 | 1.0 cm⁻¹ |
| CH-stretch | 0.020 | 0.024 | 1.0 cm⁻¹ |
| CH-oop | 0.000 | 0.117 | 1.0 cm⁻¹ |
| ring-coupling ratio | 0.017 | **0.122** | 0.10 |

The form misses line 1 everywhere by a factor of ten or more; the trained target meets it in ring-ip and in the ring couplings.

**Line 2 has no valid reading, for the form or for the target.** The script printed forecasts of 10⁷–10¹² cm⁻¹ at 60 atoms. The cause is
in this registration, not in the molecules: the fit rule left out only floors that are exactly zero, and on the small molecules the floor is
numerically zero (74 of the 93 below 15 atoms are below 10⁻⁶ cm⁻¹ for the form), so a straight line in log–log through 10⁻¹⁰ and 10⁻¹ has a
slope of tens. My prediction said the floor 'rises from near zero', and I did not draw the consequence for the fit. The mechanical verdict
('the form costs') comes only from these invalid forecasts and is not used.

**What the sizes show (beside, by_size.md):** the pattern has more free entries than K has conditions in every size bin (median 1,483 against
465 below 15 atoms, 12,597 against 3,321 at 28 or more), so the form fits almost everything; its pooled ring-ip floor stays at or below 0.14
cm⁻¹ in every bin with no rise (0.008 at 28 or more atoms). The trained target loses more as the molecules grow: ring-ip 0.016 / 0.73 / 0.81 /
0.87 / 1.42 cm⁻¹ and ring-coupling ratio 0.004 / 0.078 / 0.088 / 0.107 / 0.138 over the bins below 15, 15–19, 20–23, 24–27 and 28 or more atoms.

**Reading:** pattern f is not the limit; the projected target the recipe trains is a limit, a growing one. At 24 or more atoms it costs
1.1 cm⁻¹ in ring-ip before any learning error — about a tenth of the carried model's error variance there (3.78 cm⁻¹ on chain 39's size
hold-out, another set), and rising with size. **What follows, the registration's second branch** ('no form line met but a target line met'),
taken instead of the mechanical first branch for the reason above: a target comparison — projected against the ridge target
(`--aux-target ls`) — read on hold-outs (a), (b) and the size hold-out. It joins TASKS 59 (the ridge target along a curve, which chain 10
closed on one size on 1 Oct when the ridge target trained worse at 750 although its bound is lower): the learnability question stays open,
and this read gives it a size reason. To be registered before it runs; laptop time from about the end of October.

My prediction: right that the form is not the limit at these sizes and that line 1 is not met for it; wrong that the pattern is
over-constrained above the smallest molecules (it is under-constrained at every size here) and silent on the target, which carries the finding.

## Amendment (15 Oct 2026, 21:2x) — line 2's fit rule for the registered re-read on lever 5's large-PAH labels, before those data exist

The outcome found line 2 unreadable: the fit took numerically-zero floors from the exact-fit regime. For the re-read (lever 5's 34–60-atom
labels and layer T, same script) line 2 is read as follows, fixed now: a molecule enters a read-out's fit only if its value is ≥ 1e-6 (cm⁻¹,
or the ratio) **and** it has ≥ 15 atoms; the power law is fitted to the 15-atom-and-larger part of the frozen 534 together with the new
molecules and evaluated at 60 atoms; the lines (1.25 cm⁻¹ / 0.15) are unchanged. The new molecules are also read directly — pooled, by the
same bins — beside the forecast, since at 34–60 atoms the forecast is no longer needed. A synthetic test with an exact-fit regime below 15
atoms is written with the change, before the re-read.
