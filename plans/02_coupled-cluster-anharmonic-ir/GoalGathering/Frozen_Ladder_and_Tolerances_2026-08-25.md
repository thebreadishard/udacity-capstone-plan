# Frozen targets: molecule ladder, band families and tolerances

**Frozen 2026-08-25.** Committed **before** any gold-rung calculation, any model training and any
comparison against an experimental standard.

This document exists so that "close enough" is defined in advance. Deciding a tolerance after seeing
a result means picking the number the result happens to achieve, which converts a test into a
description. The commit date is the evidence that this was written first.

**This document may not be edited.** A change requires a **new dated document** that supersedes this
one, states what changed, and states why. Edits to this file are a protocol violation regardless of
their content.

Signed off by: *[repository owner, 2026-08-25]*

---

## 1. The molecule ladder

Climbed in order. Each rung is scored before the next begins.

| Rung | Species | Charge states | Named experimental standard | Notes |
|---|---|---|---|---|
| **0** | Benzene, C₆H₆ | neutral | One NIST Chemistry WebBook gas-phase FTIR dataset, **dataset ID and resolution recorded at G0** | Validation anchor, not a PAH — see §2 |
| **1** | Naphthalene, C₁₀H₈ | neutral **+ cation** | Gas-phase or He-tagged IR where it exists; otherwise NASA Ames PAHdb **experimental** library with the frozen matrix-shift model | First real transfer step; first open-shell rung |
| **2** | Anthracene **and** phenanthrene, C₁₄H₁₀ | neutral + cation | PAHdb experimental library with the frozen shift model | Isomer pair, chosen deliberately: identical formula, different spectra. Supplies the degeneracy case §5 needs |
| **3** | Pyrene, C₁₆H₁₀ | neutral + cation | IRMPD action spectroscopy (bibliography item 31) | Named modern standard at this size and charge |
| **NC** | **Negative control**, fixed at G5 from a species one rung beyond the last passing rung, or a wrong charge state of a passing species | — | Same standard as its nearest rung | **Must fail** the §5 identification. A fail-closed rule that never fails is untested |

**Not on the ladder, and not scored:** H₂O, D₂O and CO₂. They are regression tests for the toolchain
— cheap, exactly known, and loud when something breaks. No claim in this thesis rests on them.

## 2. Scored band families

| Family | Approximate range | Assignment |
|---|---|---|
| **3.3 μm** | ~3000–3100 cm⁻¹ | Aromatic C–H stretch |
| **6–9 μm** | ~1100–1650 cm⁻¹ | C–C stretch and C–H in-plane bend |
| **11–12 μm** | ~800–900 cm⁻¹ | C–H out-of-plane bend |

**Rung 0 is scored differently, and this is deliberate.** Benzene is a single ring; its out-of-plane
C–H bend does not sit in the 11–12 μm PAH window, and the family language does not apply cleanly to
it. Rung 0 is therefore scored on **all IR-active fundamentals listed in the chosen NIST dataset**,
and the dataset defines that list. Band-family scoring begins at rung 1.

Modes are assigned to families by frequency **and** by displacement-vector character, both recorded.
A mode that cannot be assigned is reported as unassigned rather than forced into the nearest family.

## 3. Tolerances

### 3.1 Band centres — two conditions, both required

| | Condition | Why this number |
|---|---|---|
| **Absolute** | ≤ **10 cm⁻¹** against a gas-phase or action-spectroscopy standard; ≤ **15 cm⁻¹** against matrix data with the frozen shift model | The looser matrix figure reflects reported matrix shifts of 2–15 cm⁻¹; it is not a lower standard of work, it is a wider ruler |
| **Relative** | Mean absolute error **no worse than the scaled-harmonic baseline** on the same modes | See below. This is the condition that actually bites |

**Why the relative condition exists.** ML-corrected harmonic scaling already reaches roughly
**5 cm⁻¹** MAE (bibliography item 14). A 10 cm⁻¹ absolute tolerance would therefore let this method
"pass" while being *worse than the status quo*. The absolute number licenses the R3 wording; the
relative condition is the real test. If the anharmonic, coupled-cluster-anchored pipeline does not
beat scaled-harmonic B3LYP on a band family, **the honest finding is that it did not pay for itself
on that family**, and that is what gets reported.

### 3.2 Relative intensities

- **≤ 20 %** error on integrated intensity *ratios within a band family*, on the modes scored for
  that family.
- **Neutral-to-cation intensity swap reproduced qualitatively** in the 6–9 μm and 11–12 μm families:
  the direction of the change must be right, at every rung where both charge states were computed.
- Absolute intensities are **not** claimed at any rung.

### 3.3 Label-level tolerances

Frozen as of this date in Distilled Plan §5.5, and repeated here only so that this document is a
complete record of what was fixed on 2026-08-25:

| Quantity | Pass condition |
|---|---|
| Relative energy | RMSE ≤ 1.0 kcal/mol, max ≤ 2.0 kcal/mol |
| Directional derivative | RMSE ≤ 1.0 meV/Å |
| Audited harmonic modes | frequency shift ≤ 5 cm⁻¹ |

## 4. The stop rule

Climbing stops at the **first rung where any scored band family exceeds its §3.1 absolute
tolerance**, for either charge state.

That rung is published as **the measured limit of the method**. It is a result, not a failure, and
the report states the measured error that triggered it.

- A rung may not be retried with different settings after it has failed, unless the retry and its
  reason are recorded in a new dated document **before** the retry runs.
- A species may be marked **UNRESOLVED** for a band family whose nuclear-motion treatment did not
  converge (Distilled §6.4). UNRESOLVED is not a pass and does not permit climbing.
- Passing a rung requires **both** charge states to pass, unless the shrink ladder has already
  reduced that rung to neutrals-only in writing.

## 5. Identification rule

Frozen here in outline. The full pre-registration — including the observational product identifier —
is written at G6 and must itself predate the opening of that product.

- **Target list:** only species and charge states that passed G5. Restricting the list *before* the
  product is opened is legitimate; restricting it *after* is a fail.
- **Verdicts, and only these:** **Supported** / **Rejected** / **Unidentified-degenerate**.
- **Degeneracy rule:** if two or more target species fit within the match tolerance, the verdict is
  Unidentified-degenerate and **both are named**. Choosing the more interesting one is a fail.
- **Negative control** must return Rejected.
- The observational product is evaluated **once**.

## 6. Deliberately not frozen, and why

Freezing something that has to be measured would be pretending to knowledge. These remain open, with
the point at which each closes:

| Open | Closes at | Why it cannot close now |
|---|---|---|
| Number of Δ-ML training points per rung | The G1 cost pilot | It is an output of a measurement, not an input to a plan |
| Which shrink-ladder rung fires | G1, in writing | Depends on measured cost |
| Which attachment design (Δ-model vs fine-tune) | G2 bake-off | Decided on cubic-constant stability, which cannot be predicted |
| Which DMS leg carries intensities | G4 bake-off | Same |
| **The GVPT2 resonance criterion and its parameters** | **G0, in a dated amendment to this document, before any GVPT2 result on any species is computed** | The criterion must follow the selected toolchain's convention, and the toolchain is chosen at G0. **If no such amendment exists, no GVPT2 result may be reported.** |
| The NIST dataset ID and resolution for rung 0 | G0 | Must be a specific dataset, recorded once |
| The observational product for G6 | G6 pre-registration | Must be named before it is opened, not before it is chosen |

## 7. Form of an amendment

Several items in §6 close in a **dated amendment to this document**. Round-4 Pass A noted that the
required form was never shown, so here it is. An amendment is a new file named
`Amendment_<date>_<subject>.md` in this folder, containing exactly:

```
# Amendment to Frozen_Ladder_and_Tolerances_2026-08-25 — <subject>

Date: <ISO date>
Closes: <which §6 open item>
Gate: <the gate at which this closes>

## What is now fixed
<the value, criterion or identifier, stated so it can be checked>

## Convention it follows
<the toolchain, dataset or literature convention, cited>

## What this does not change
<explicit: nothing else in the frozen document moves>
```

Worked example, for the item most likely to be fudged:

> **Closes:** the GVPT2 resonance criterion.
> **What is now fixed:** Fermi resonances identified by the Martin test with thresholds
> \(K_{\text{test}} > X\) cm⁻¹ and \(\lvert\omega_i-\omega_j-\omega_k\rvert < Y\) cm⁻¹; Darling–Dennison
> pairs by \(\lvert 2\omega_i-2\omega_j\rvert < Z\) cm⁻¹. Resonant terms deperturbed from the
> perturbative sum and the resulting polyads diagonalised variationally.
> **Convention it follows:** as implemented in \<selected toolchain, version\>.

The amendment's commit date is the evidence. An amendment written after the result it governs is not
an amendment.

## 8. Checklist for a reviewer

- [ ] Is this document's commit date earlier than the first gold-rung calculation?
- [ ] Does a dated resonance-criterion amendment exist, and does it predate the first GVPT2 result?
- [ ] Is every reported band centre accompanied by both the absolute **and** the relative condition?
- [ ] Is the four-term error budget present per molecule, charge state and band family — not pooled?
- [ ] Was the stop rung published with the measured error that triggered it?
- [ ] Did the negative control fail?
- [ ] Was each experimental standard opened once, after the corresponding model was frozen?
