# The anharmonic step in the pipeline — design

**Written 14 November 2026**, before the step is built. TASKS 211 and 178. The decision it implements was registered the same day in
`PreRegistration_2026-11-14_Printed_Band_Position.md`; what each family's step is worth was read in S2b and S3, the CH-stretch family
on 14 November (TASKS 219).

## 1. What is to be built

The pipeline prints a band at the harmonic position today, with `HARMONIC_NOTE` saying so. It is to print

    ν = ω(ΔH network) + Δ_anh(family),

with Δ_anh the family's estimate and the family's measured rms as the stated bar, and no licence claimed. Per family, measured on
coronene and tetracene:

| family | printed model | bar (cm⁻¹) | the harmonic position costs | better by |
|---|---|---|---|---|
| ring-ip | x2* | 3.37 | 26.23 | 7.8× |
| other | x2* | 3.84 | 8.20 | 2.1× |
| CH-oop | x2* | 8.38 | 12.48 | 1.5× |
| CH-stretch | x2* | 6.21 | 134.24 | 21.6× |

`probes/anharmonic_route_rule.py` writes that table beside the licensing table, from the same two reads, since 14 November. The two
records are `route_rule.json` (the window 550–2000 cm⁻¹) and `route_rule_ch.json` (2800 cm⁻¹ and up); the families are disjoint.

## 2. What the pipeline must have, per molecule

x2* is kernel ridge on **FX** = F1 + Δ_xtb: the family one-hot, ω/1000, the mode's hydrogen share h, its out-of-plane share o, and
**the anharmonic shift of the matched GFN2-xTB mode** (S2 amendment 4). F1 the pipeline can compute from what it already has — the
network's spectrum gives ω and the mode vectors give h and o. Δ_xtb it cannot: that is a GFN2-xTB quartic force field of the
molecule, and then a mode-by-mode match to the B3LYP modes with the overlap rule of `s2_xtb_read.match_modes`.

So the step needs three new things in `m08/pipeline.py`:

1. a GFN2-xTB QFF of the molecule (`probes/xtb_anharmonic.sh`'s steps: the xtb minimum, dxtb Hessians at ±0.10 along every mode,
   `dpir.qff` with its noise guard);
2. the match to the B3LYP modes, and the refusal of a mode whose overlap is below `MIN_OVERLAP`;
3. the fitted x2* per family, as an artefact the pipeline loads rather than a fit it repeats.

## 3. What that costs, measured

From the project's own log of 19 October (`probes/results_m1/s2_xtb_2026-10-18/s2_xtb.log`), at SHARDS=2 × OMP=2, four cores:

    B_0603418c5b  53 min     B_410ac0fb2f  51 min     B_a41f4cff9d  87 min
    B_079e66d017  90 min     B_78f8233b4c  98 min

The demo of 25 November (decision 64) gives the whole pipeline half an hour on a molecule the supervisor picks. The DFT side of that
budget is already spent: furan+vinyl, 13 atoms, was estimated at 9 minutes on 14 November. How the QFF scales with cores is not
measured; `probes/runspecs/xtb_qff_timing.json` measures it on the same molecule at eight.

## 4. The choice, if it does not fit

The feature-free models need no xtb at all. On the same targets:

| family | x2* (needs xtb) | best without xtb | the cost of going without |
|---|---|---|---|
| ring-ip | 3.37 | (b) 3.65 | 0.28 cm⁻¹ |
| other | 3.84 | (b) 3.97 | 0.13 |
| CH-oop | 8.38 | (c) 9.27 | 0.89 |
| CH-stretch | 6.21 | (b) 6.49 | 0.28 |

Every one of them still beats the harmonic position by the margins of section 1. So the choice is between an hour or more of GFN2-xTB
per molecule and about half a wavenumber, and it is the user's: the printed model is registered, and changing it needs a dated
amendment to `PreRegistration_2026-11-14_Printed_Band_Position.md` with these numbers in it. A third shape exists — x2* where the xtb
is affordable or already computed, the feature-free model otherwise — and it costs a certificate that says which route each band took,
which is a thing the certificate already does for other reasons.

## 5. The shape of the code

- **The artefact.** One file per family with the fitted model and the recipe that made it: the configuration S2b's nested read chose,
  the training molecules by id, the feature set, the bar, and the read it comes from. Written by a probe, never by the pipeline, and
  loaded read-only. A model the pipeline cannot trace to a read it refuses to use.
- **The step.** One function that takes the network's spectrum and the molecule's features and returns, per mode, the printed
  position, the bar and the route taken. It never looks at a file; what it needs is passed in.
- **The certificate.** `HARMONIC_NOTE` goes. Each band's line names the route (model with its bar, no step because the mode is marked
  outside VPT2's domain, no step because the family is unmeasured) and the uncertainty that goes with it.
- **The refusals.** A molecule whose xtb match falls below the overlap line for a mode gets no step on that mode, and says so. A
  family without an artefact gets no step. Nothing silently falls back to the harmonic position without saying it did.

## 6. How it is checked

- The artefact reproduces S3's published numbers: fitted on the training molecules and applied to coronene and tetracene, it gives
  the bars of section 1 to the digits printed there. This is the test that catches a wrong feature or a wrong configuration.
- A pipeline run of a molecule in S3's target set reproduces that molecule's row.
- The certificate of a molecule with a marked mode shows the harmonic position for that mode and the step for the others.
- The acceptance test of the printed-position registration, which was written before any of this.
