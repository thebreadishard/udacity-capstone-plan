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

## Amendment 1 (19 November 2026, 20:1x — the bars of the artefact's format 3, before any certificate prints them; TASKS 255, 211)

**What changed under the bars.** Since 17 November the step runs on format 3 of its artefact (`probes/anharmonic_step/x2star_v3.json`,
written 09:43 at commit 46c7ba6d). Its training table is matched set-wise: where the one-to-one match refuses a mode for its basis
in a near-degenerate set, the mode is read against the set's partners (`probes/s2_xtb_read.match_sets`, merge 3dccea10). This added
one training row (a CH stretch at 3183.24 cm⁻¹, matched at 0.934) and left the 2,168 one-to-one modes unchanged. The bars of section 1
were read with the one-to-one match on format 2's table, so they measure a model that no longer runs.

**The bars side by side** (rms of step − GVPT2 label over the registered target rows of coronene and tetracene, cm⁻¹;
`probes/results_m1/anharmonic_step_2026-11-17/acceptance.md`, which also reproduces the registered match to 0.0013 in the first three
families):

| family | target rows | registered (format 2, one-to-one) | format 3 (set-wise) | coronene / tetracene on format 3 | harmonic position |
|---|---|---|---|---|---|
| ring-ip | 56 | 3.37 | 3.3694 | 4.25 / 2.35 | 26.23 |
| other | 23 | 3.84 | 3.8387 | 5.69 / 1.09 | 8.20 |
| CH-oop | 22 | 8.38 | 8.3809 | 11.91 / 4.55 | 12.48 |
| CH-stretch | 20 | 6.21 (6.2143) | 6.1994 | 6.92 / 5.67 | 134.24 |

The CH-stretch row was not in section 1. It was measured under TASKS 219
(`probes/results_m1/labels_domain_2026-11-13/route_rule/route_rule_ch.md`) and joined the printed families on 14 November, 19:2x (TASKS 211).
So section 2, item 3 no longer holds for that family: the CH stretches get the step, with this bar, and no licence.

**What the certificate prints.** The registered bars, unchanged: **ring-ip 3.37, 'other' 3.84, CH-oop 8.38, CH-stretch 6.21.** Format 3's own bars agree with them to 0.015 cm⁻¹ in every family (the table above); only CH-stretch would round differently (6.20), and the certificate keeps the registered, slightly larger 6.21.

**Why.** The difference is far below what two target molecules can resolve, and keeping the registered numbers means no certificate changes its stated uncertainty and no code or artefact changes for a hundredth of a wavenumber. This amendment is the record that the model now running (format 3, set-wise match) was read on the same target rows and gives the same bars; a later read that moves a bar by more than rounding replaces it here first, as section 5 requires.

**Not changed.** No ≤ 3 cm⁻¹ licence is claimed in any family. The bars still rest on two hydrocarbons. Section 4's acceptance test
now reads against the format-3 bars to 0.01 (`acceptance.md`: pass in all four families). The step's run-to-run tolerance in
`probes/results_m1/anharmonic_step_2026-11-17/first_run_checks.py` (0.3 × the family's bar, at most 2 cm⁻¹, plus 0.1, rounded to
0.01) stays at 1.96 cm⁻¹ for CH-stretch with either bar.
