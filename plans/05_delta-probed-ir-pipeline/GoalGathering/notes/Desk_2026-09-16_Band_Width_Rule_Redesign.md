# The band-width rule: what a truth-free replacement can and cannot do (desk work, 16 September 2026)

*No new energies: the stage B responses of `naphthalene_sym` refitted at eight widths with five folds.
Instrument: `probes/bandwidth_rule_redesign.py`; numbers `results_dryrun/naphthalene_sym/bandwidth_rule_redesign.json`.*

## The rule as it stands, read from the code rather than from memory

`dryrun_dft_delta_recovery.py` selects the **smallest** candidate width whose worst-family frequency RMS
**against the direct Δ₂** clears τ₇ = 5.0 cm⁻¹. The hold-out residual ρ selects λ at fixed w; it never
selects w. Two faults: the criterion reads a quantity that does not exist on a real molecule, and
"smallest that clears a tolerance" stops at the first acceptable answer rather than the best available.

## The replacement, and why it is the natural one

Two numbers, both from fitted quantities only, both in cm⁻¹ and aggregated the way the go/no-go is:

- **σ(w)** — worst-family frequency RMS between a fold-out fit and the full-data fit at the same width.
  How far the answer moves when a fifth of the training data is dropped: the noise the data carries.
- **drift(w)** — worst-family frequency RMS between the fit at width w and the fit at the widest width.
  What the truncation costs, measured against the least truncated answer available.

Rule: the smallest w with drift(w) ≤ σ(w) — the narrowest band the data cannot distinguish from the
widest. If only w_max qualifies, the ladder is too short and the run says so.

## What it returns on naphthalene

| w (cm⁻¹) | 25 | 50 | 100 | 200 | 400 | 800 | 1600 | 3200 |
|---|---|---|---|---|---|---|---|---|
| σ | 3.60 | 3.57 | 3.27 | 4.68 | 2.34 | 2.96 | 3.66 | 4.26 |
| drift vs w_max | 2.59 | 2.59 | 2.60 | 2.62 | 4.19 | 1.22 | 0.40 | 0.00 |
| *true error (rehearsal only)* | *3.37* | *3.37* | *3.36* | *3.36* | *0.82* | *2.86* | *3.99* | *4.06* |

The rule selects w = 25 — the same width the old rule chose, for an honest reason instead of a lucky one:
every width except 400 sits inside its own noise, so the narrowest is the parsimonious choice.

## Three things this settles

1. **The old rule's 4× loss was overstated, and I should not have reported it as I did.** On the
   afternoon's five-point ladder, w = 400 (0.82 cm⁻¹) looked four times better than w = 25 (3.37). On the
   extended ladder it is an **isolated dip**: its neighbours give 3.36 at w = 200 and 2.86 at w = 800, and
   the fit's own fold-to-fold noise at w = 400 is 2.34 cm⁻¹ — three times the advantage it appears to
   have. Holding λ fixed at 1e-7 across the ladder reproduces the dip (0.73), so it is not an artefact of
   the λ choice, but a single point with no neighbourhood is a coincidence, not a feature. The defect in
   the width rule is that it reads the truth, not that it left a reliable improvement unclaimed.
2. **A truth-free score can detect disagreement but cannot rank.** The diagnostic sees that w = 400
   disagrees with the widest fit by more than its own noise. Nothing in the data says which of the two is
   closer to the right answer — that is exactly what the old rule was using the direct Δ₂ for. **There is
   no drop-in replacement that keeps the ranking and drops the peek.** The honest options are to fix the
   width a priori on physical grounds (a resonance criterion, pre-registered, not tuned), to buy a small
   validation set on a molecule small enough to afford the direct Δ₂ and transfer the width under a
   stated assumption, or to drop the band altogether and control the fit with λ alone — w = 3200 is no
   banding at all, and it costs 4.06 cm⁻¹ against 3.37, so the band is buying very little here.
3. **No width rescues this deck.** The whole ladder spans 0.82–4.06 cm⁻¹ of true worst-family error where
   the project needs 0.5. The width is not the binding constraint; the off-diagonal signal sitting at the
   model floor is. **The width question is therefore blocked on the amplitude test, not independent of
   it** — which is a change to this morning's plan, where the redesign was listed as free-standing desk
   work. The instrument is built and tested; it should be re-run on the half-amplitude block when that
   exists, because only then is there a signal for any rule to select on.
