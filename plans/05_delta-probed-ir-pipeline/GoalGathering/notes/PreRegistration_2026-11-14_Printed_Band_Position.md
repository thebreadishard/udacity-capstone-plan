# What the pipeline prints as a band position — registered before any number is recomputed

**Written 14 November 2026, before the step is built.** The decision is the user's, this morning: *"als de anharmonische posities
dichter bij de waarheid liggen dan de puur harmonische, dan tonen we die"*, under the rule that the pipeline carries every
quality-raising lesson (CLAUDE.md, *Improvements reach the end product*). TASKS 211, 178.

## 1. The two questions this note separates

`PreRegistration_2026-11-04_Anharmonic_Route_Rule.md` answers one question — **may we claim a band position to ≤ 3 cm⁻¹?** — and its
answer, read on 13 November, is no, in all three families. That rule stands, unchanged and unwidened.

It does not answer the other question: **which number is our best estimate of the band position?** Its rule 3 answered it by default,
by keeping the harmonic position, and that default is worse than the model it refuses in every family:

| family | window modes | Δ_anh model (x2*) rms | family mean (c) rms | harmonic position rms |
|---|---|---|---|---|
| ring-ip | 56 | **3.37** | 8.47 | 26.23 |
| other | 23 | **3.84** | 4.34 | 8.20 |
| CH-oop | 22 | **8.38** | 9.27 | 12.48 |

(`probes/results_m1/labels_domain_2026-11-13/route_rule/route_rule.md`; rms in cm⁻¹ over the target modes of coronene and tetracene
in the window 550–2000 cm⁻¹, a degenerate pair counted once.)

**So: the pipeline prints the anharmonic estimate, and licenses nothing.** Printing a number we believe is worse, in order to respect
a threshold about claims, would be answering the wrong question.

## 2. What is printed, per band

1. **A band in a family with a verdict model and a measured transfer** (today: ring-ip, 'other', CH-oop) is printed at
   ν = ω(ΔH network) + Δ_anh, where Δ_anh is that family's S2b verdict model — today `x2*`, kernel ridge on FX (F1 plus the matched
   GFN2-xTB mode's own shift, S2 amendment 4), fitted on all training molecules of the family. The stated uncertainty is the family's
   rms in the table above, named as measured, not as licensed.
2. **A band whose mode is marked out of VPT2's domain** (`Design_2026-11-13_VPT2_Domain_Marks.md`: strain > 0.10 or the partner share;
   8 modes in 5 of 36 force fields so far, plus coronene's 24 and 36) gets **no step**. It is printed at its harmonic position and
   marked as a mode this method cannot correct; TASKS 209 is the route that will solve such a mode without perturbation theory.
3. **A band in a family without a verdict model or with fewer than 6 target modes** gets no step, as rule 4 of the route rule says.
   Today that is the CH-stretch family, and section 5 says what we owe there.
4. **Every printed position states which of the three it is.** The certificate's per-band line names the route (model, no step because
   marked, no step because unmeasured) and the uncertainty that goes with it; `HARMONIC_NOTE` in `m08/pipeline.py` is replaced by a
   note that says the same for the spectrum as a whole.

## 3. What is not claimed

- **No ≤ 3 cm⁻¹ licence, in any family.** The registered line is not met and is not moved.
- **The bars rest on two molecules**, coronene and tetracene, and coronene carries every failure: its rms is 4.25 in ring-ip, 5.69 in
  'other' and 11.91 in CH-oop, against tetracene's 2.35, 1.09 and 4.55. They are the best numbers we have and they are thin; a reader
  is told so.
- **The bars are not a prediction interval per band.** They are the rms of the family over the measured modes.
- Nothing here says the anharmonic step helps a molecule unlike the two targets. The size trend and the scaffold trend stay open.

## 4. How a printed number is verified

The step is accepted into the pipeline only when, run on coronene and tetracene from the carried recipe, it reproduces the per-family
rms of `route_rule.md` above to within 0.01 cm⁻¹ — the same model, the same modes, the same pairing. A test pins that, and a second
test pins that a marked mode comes out with no step and its mark.

## 5. What we owe, and what changes a number here

- **The CH stretches have no measured bar at all**, because the S2b and S3 reads work in the window 550–2000 cm⁻¹ (`s2_read.WINDOW`)
  and a CH stretch sits well above it. Under rule 4 they are therefore printed harmonic — and that is where the harmonic error is largest
  in the whole spectrum: a CH stretch's VPT2 correction is about −170 cm⁻¹ and is sound by the strain measure (0.054–0.056). The
  labels for it are in hand. Measuring that family is TASKS 219, registered on its own before it is read.
- **A later read replaces a bar only by replacing this note.** When S2b or S3 is read again — more anchors, a repaired corpus, a new
  verdict model — the new bars are written in a dated amendment here before any certificate carries them. A printed estimate never
  changes its stated uncertainty quietly.
