# Note, 5 October 2026 — the layers of truth: what the network is trained on, what it is calibrated to, and what decides its correctness in 2028

*Written at the user's request (5 Oct 07:3x: "we willen wel de meest 'juiste' methode als we trainen, toch? Hoe gaan we daarmee om?"). The principle
the plan has used since the Ladder, stated in one place; README decision 60 points here.*

**The network's correctness is set by the top layer it is calibrated to, not by the level it pretrains on.** Four layers, from cheap to true:

| layer | what it is | how many molecules | its job | how it is judged |
|---|---|---|---|---|
| 1. input | B3LYP/6-31G*, the cheap calculation anyone can afford for a large PAH | every molecule | the network's input; stays in production | — |
| 2. stepping stone | a proxy target (today ωB97X/6-31G*; MP2 is registered as a candidate) | thousands | the network learns the *shape* of the correction — families, couplings, scaffolds — on data no anchor set can match | not by its own correctness but by how little the anchors have to correct afterwards (T3's 'network as is' and 'head tuned') |
| 3. anchors | CCSD(T) Hessians (cc-pVDZ today; the composite DZ→TZ under test; cc-pVTZ where affordable; LNO beyond ≈ 26 atoms) | four today, 100–200 in the estimate of 4 Oct | the calibration layer: α and head tuning on the stone-trained network; the level that defines "correct" for the harmonic correction | two routes per anchor (pair checks, energy route), basis read against TZ, the anchor curve 3 → 5 → 8 |
| 4. the world | gas-phase laboratory spectra (module 03), astronomical bands | tens of molecules | the external check of the whole chain and of the third layer that anchors cannot give — anharmonic shifts, widths, temperature | module 03's scoreboard; the reading rules of the Ladder |

**Consequences for the choices in front of us.**
- *Changing the stepping stone* (ωB97X → MP2) is a question of **how much the anchors still have to do**, measured, not a question of taste; it is
  registration 2 of `Design_2026-10-05_Analytic_Labels_and_Stepping_Stone.md`.
- *Making the labels analytic* removes noise from layer 2 without changing its level; it is worth it only if the noise is what limits the network
  there — the measured case for the low modes (floor 4.8 cm⁻¹ against an error of 3.2) — and it changes how every future row is made, so the
  investment outlives this stone. Registration 1 of the same note.
- *Raising the anchor level* (lever 2's finding: the cc-pVDZ anchors are not the truth out of plane; the composite route; dearer anchors on the user's
  word) raises the ceiling of layer 3 and therefore of the whole network; nothing in layers 1–2 can substitute for it.
- *"Most correct in 2028"* therefore means: the best affordable anchor level at that time, the anchor count the curve says is enough, the stone that
  leaves the anchors least to do, and a measured agreement with layer 4 on the molecules where it exists — each with two routes and a number on
  record, never a method chosen because it sounds better.

**What this is not.** It is not a licence to train on cheap labels forever: when the anchor layer grows past a few hundred molecules, the stone can be
retired or replaced by the anchors themselves; the Ladder's reading rules decide that moment, not a date.
