# The CH-stretch family's anharmonic shift — registered before the read

**Written 14 November 2026, before any CH-stretch mode has been fitted or read.** TASKS 219, found while registering what the
pipeline prints (`PreRegistration_2026-11-14_Printed_Band_Position.md`, section 5).

## 1. Why this read exists

S2b and S3 work in the window 550–2000 cm⁻¹ (`s2_read.WINDOW`). A CH stretch sits well above it, so the CH-stretch family never
entered either read: it has no verdict model, no measured transfer, and under rule 4 of
`PreRegistration_2026-11-04_Anharmonic_Route_Rule.md` a family without a verdict model gets no anharmonic step.

That is the worst place in the spectrum to have no step. A CH stretch's VPT2 correction is about **−170 cm⁻¹**, and it is sound
anharmonicity by our own domain measure: those modes sit at a strain of 0.054 to 0.056, far below the 0.10 that marks a breakdown
(`Design_2026-11-13_VPT2_Domain_Marks.md`). Printing a harmonic CH stretch is therefore an error of roughly 5 % on the band an
astronomer looks at first. The labels exist — 2,028 modes in 36 force fields — and only the window kept them out.

## 2. What will be read, and on what

The same machinery, unchanged, with one window added:

- **`CH_WINDOW = (2800, inf)` cm⁻¹**, read beside the existing window rather than instead of it; no read inside 550–2000 changes.
  The lower bound is not a choice made here: the corpus's own family classifier already calls a mode a CH stretch when it lies above
  2800 cm⁻¹ and more than half of its displacement is hydrogen (`m05/learning_curve_layerA.py`, the `family` assignment the training
  tokens carry). No upper bound is imposed, because the family assignment and not the window decides what a CH stretch is.
- **S2b's read** (`probes/s2b_read.py`), main scope 'no-large-amplitude': per family the learning curve of (c), (b), x1 and x2*,
  leave-one-scaffold-out, and the verdict model is the lowest rms at 'all', exactly as the existing rule says.
- **S3's read** (`probes/s3_read.py`): that verdict model and (c) on the CH-stretch modes of coronene and tetracene.
- **The read reports its own size first**: the number of CH-stretch modes per force field, the number of force fields, and the
  number of target modes on each of the two targets, printed before any model is fitted. If the targets carry fewer than 6
  CH-stretch modes between them, rule 4 of the route rule applies and the family gets no step — that is the registered rule and
  this note does not loosen it.

## 3. The criteria, registered in advance

1. **The verdict model** is the lowest leave-one-scaffold-out rms at 'all' among (c), (b), x1 and x2*, as in S2b.
2. **The licence** follows the route rule unchanged: the family may claim ≤ 3 cm⁻¹ only if the verdict model's target rms is at or
   below 3.0 **and** below (c)'s. Nobody expects that here — a −170 cm⁻¹ correction predicted to 3 cm⁻¹ would be 2 % — and the line
   is not moved to make it reachable.
3. **What is printed** follows `PreRegistration_2026-11-14_Printed_Band_Position.md`: the best estimate with its measured rms as the
   stated uncertainty, and no licence claimed. For this family that means the step is printed if, and only if, it beats the harmonic
   position — the rms of the true shift over the same modes — by the read's own numbers.
4. **A mode marked out of VPT2's domain gets no step**, as registered on 13 November. The strain of a CH stretch is 0.054–0.056, so
   none is expected to be marked; one that is, is printed harmonic and says so.

## 4. What is expected, so that a surprise is visible

Written before the numbers: the CH-stretch shift is large and systematic, so the family mean (c) should already capture most of it. I
expect **(c) within 15 cm⁻¹** and **the verdict model within 10**, both far above the 3.0 line and both far below the harmonic
position's error of about 170. I also expect the learned model to add *less* here than it does for the in-plane ring family, where it
takes 26.23 cm⁻¹ down to 3.37: a single systematic shift is the easy case, and if x2* cannot beat (c) on CH stretches then the honest
outcome is to print (c).

## 5. What this read does not do

It does not touch the existing reads or the 3.0 cm⁻¹ line; it says nothing about the overtones and combination bands that crowd the
3 µm region, since what we model is the fundamentals; and it makes no claim about CH stretches on molecules unlike the two targets.
The number of force fields that carry a CH stretch at all is the read's own first output, and if it is small the read says so instead
of fitting a curve through it.
