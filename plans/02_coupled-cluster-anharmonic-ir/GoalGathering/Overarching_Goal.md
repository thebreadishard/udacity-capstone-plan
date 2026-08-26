# Overarching Objective: Anharmonic IR Band Families for Named PAHs, Anchored to a Measured Coupled-Cluster Reference

**Terminology note (2026-08-23).** This repository uses **"gold rung"** and **"gold-anchored"** as internal
shorthand, inherited from [Project 10](Horizon/10_Size_Extensive_Aromatic_PES.md). *"Gold
standard"* for CCSD(T) is established literature usage; **"gold-anchored" is not** — it is this
project's own term. It is defined here once and may be used freely inside these documents, but a
thesis chapter, abstract or paper title must instead say **"anchored to a measured coupled-cluster
reference"** or **"CCSD(T)-quality"**.

> **Gold rung** — the highest level of electronic-structure theory that is actually computed for a
> given molecule (canonical CCSD(T) where affordable), against which every cheaper method used on
> that molecule has a **measured**, published error. A rung that is assumed rather than measured is
> not a gold rung.

**Status (2026-08-23):** Rewritten to adopt **R3** (§1) as the definition of "chemically precise", per
[Restructure_Proposal_2026-08-23_Project12_in_Module08.md](Restructure_Proposal_2026-08-23_Project12_in_Module08.md)
decisions 1–3. Supersedes the 2026-08-22 version, whose deliverable was small-molecule band envelopes
plus a field-vs-GNN representation verdict.

This file is the prime directive of **this thesis**. Every other document must agree with it. It must
not be quotable as a rovibrational line-list promise.

**There is no post-master's horizon.** Projects 10–12 are absorbed into Modules 03–08. The files
[10](Horizon/10_Size_Extensive_Aromatic_PES.md),
[11](Horizon/11_Anharmonic_IR_and_Intensities.md) and
[12](Horizon/12_Astrophysical_PAH_Identification.md) are retained as **provenance** — they
record why the walls exist — not as a roadmap. Whatever R3 does not reach is named as a **limitation
in Module 08**, never as a queued project.

---

## 1. The deliverable: R3, and only R3

Three readings of "chemically precise IR spectra" exist. Naming which one is meant is not pedantry;
it is the difference between a defensible thesis and a lost defense.

| | Reading | Status |
|---|---|---|
| **R1** | Rovibrational **line lists** — ExoMol/POKAZATEL grade, sub-cm⁻¹ positions, \(I\propto\lvert\langle f\lvert\boldsymbol\mu\rvert i\rangle\rvert^2\) | **Forbidden.** Not achievable for any PAH by anyone inside a master's. Claiming it is a free kill. |
| **R2** | Band **envelopes** from classical MD + dipole-ACF FFT, ±10–15 cm⁻¹ | **Not the deliverable.** Already published at 216-carbon scale (Mai et al. 2025). Retained only as a temperature diagnostic. |
| **R3** | **Anharmonic band families** — quantum (GVPT2-class) band centers within a stated cm⁻¹ of a **named** experimental standard, **plus** relative integrated intensities from a dipole moment surface, **plus** a four-term error budget | **This is the objective.** |

**Frozen 2026-08-26 in [Frozen_Ladder_and_Tolerances_2026-08-26.md](Frozen_Ladder_and_Tolerances_2026-08-26.md)**, which supersedes the 2026-08-25 freeze after Round 4 Pass B. Committed before any gold-rung calculation:

- **Promised: benzene and naphthalene, neutral.** Cations, anthracene/phenanthrene and pyrene are
  **bonus, not promise** — attempted in ladder order if measured cost allows, and their absence is a
  stated limitation rather than a broken claim. The scope of this thesis got smaller on 2026-08-26,
  and that sentence belongs in the thesis.
- Band centers ≤ **10 cm⁻¹** against gas-phase experiment where it exists; ≤ **15 cm⁻¹** against
  matrix data **with** a stated, frozen matrix-shift model. Never mix corrected and uncorrected.
- **And**, separately required: mean absolute error **no worse than the scaled-harmonic baseline** on
  the same modes. ML-corrected scaling already reaches ~5 cm⁻¹, so the absolute number alone would
  let this method pass while being worse than the status quo.
- Relative integrated intensities within a band family ≤ **20 %**. The neutral-vs-cation intensity
  swap is reported as **untested** if no cation rung is reached.
- Scored band families, named in advance: **3.3 μm**, **6–9 μm**, **11–12 μm**.

**Four-term error budget, mandatory next to every cm⁻¹ claim.** A single pooled number is a fail.

| Term | What it measures |
|---|---|
| **(A)** | ML/PES error against the gold rung |
| **(B)** | Electronic-structure error — local coupled cluster against canonical CCSD(T) |
| **(C)** | Nuclear-motion error — GVPT2 against selected VCI or against experiment |
| **(D)** | Environment error — matrix shift and/or excitation model |

---

## 2. What carries the precision (the thing that changed)

**Precision lives in the theory ladder and the nuclear-motion method, not in the neural
architecture.** The ML model is an interpolator between gold-rung points. This is not a retreat from
ambition; it is the only arrangement in which R3 is reachable, and §6 has always said the ML pipeline
is a means.

Consequences, binding:

1. **The gold rung is measured, never asserted.** Canonical CCSD(T) is computed where it is
   computable, local coupled cluster (DLPNO/LNO) is computed on the same molecules, and the
   difference is published **per band family and per charge state** before the local method is used
   on anything larger. That difference is error term (B).
2. **The production surface is a fine-tuned equivariant machine-learned interatomic potential**,
   supplying the **cheap half** of a hybrid quartic force field. Since Round 4 Pass B its role is an
   *accelerator*, not a carrier of precision: the harmonic term comes from the measured gold rung,
   the anharmonic correction from a frozen cheaper level. Borrowing a mature architecture to avoid a
   comparison is required, not merely permitted.
3. **Nuclear motion is quantum.** GVPT2 with explicit resonance treatment, from a quartic force field
   derived from the ML surface. Selected VCI is the declared escalation. Running longer classical
   trajectories is **not** an escalation and may never be substituted for one.
4. **Intensities require a dipole moment surface.** Relative band strengths without a DMS are not
   shipped. Positions and intensities are gated **separately**, on purpose: an intensity failure
   withdraws intensity claims and leaves positions standing.
5. **Scaled-harmonic B3LYP — the status quo of the PAH spectral libraries — is the baseline that must
   be beaten**, and it is reproduced first. A result that cannot be compared to the status quo cannot
   be interpreted.

If a sentence cannot survive §1 and §2, it does not belong in this file.

---

## 3. Split the precision claims (do not glue these again)

Sub-wavenumber is **not** a property of a coupled-cluster energy table. \(1\,\text{kcal/mol}\approx
350\,\text{cm}^{-1}\). Putting them in one parenthetical is how the documents started lying to each
other. Three separate claims, three separate ladders.

### A. Labels (hard rule)

Every energy and every supervised derivative in the pipeline belongs to a **coupled-cluster**
surface — canonical CCSD(T) where computable, otherwise local CCSD(T) **with its measured error
against canonical**. Energies and derivatives must describe the **same** surface; a CCSD force may
never be paired with a CCSD(T) energy as a training target.

DFT appears only as (i) the cheap baseline of a Δ-learning pair, (ii) the reproduced status-quo
baseline, (iii) public reference libraries used for motivation and EDA. **None of those is a pipeline
label.**

"Chemically accurate" is allowed molecule-by-molecule and quantity-by-quantity **only after** the
gold-rung audit passes for that molecule and that quantity. Otherwise the wording is
"CCSD(T)-level", or "local-CCSD(T)-level with measured error (B)".

### B. Spectra

Allowed:

> Anharmonic band centers for [named species and charge states] within [stated] cm⁻¹ of [named
> dataset], with relative integrated intensities of the diagnostic band families reproduced to
> [stated] %, accompanied by the four-term error budget.

**Not** allowed: line lists, sub-wavenumber lines, "any size", or any intensity claim not backed by a
DMS that passed its own gate. Experimental libraries (gas-phase FTIR, IRMPD action spectroscopy,
PAHdb) are **blind checks**, never a training loss.

### C. Identification

Allowed **only** inside the pre-registered target list, band families, match metric and verdict rule,
all committed **before** the frozen observational product is opened. Permitted verdicts:
**Supported / Rejected / Unidentified-degenerate**. A negative control that must fail is part of the
deliverable. "Consistent with PAHs" without a species list is a fail.

---

## 4. Rules for deviation

Deviate from §3.A only if there is **absolutely no other technical solution**, and only with an
extremely compelling written reason recorded in the artifact. Compromising label quality is the last
resort, never a scheduling tool.

Escalation ladders are declared **in advance**, and the rung that fired is reported in every
downstream claim. A rung that fired and went unmentioned is the fastest way to lose Module 09.

Ending the molecule ladder early is **not** a deviation. "Any size" means *transfer until the measured
error exceeds the band tolerance, then stop and report where.* Stopping at the measured limit is the
correct result; climbing past it is misconduct.

---

## 5. What Module 08 puts on the table

A gated system assembled from prior modules — **nothing debuts here**:

1. **Anharmonic band families and relative intensities** for the pre-registered molecule/charge
   ladder, from a gold-anchored surface and a gated dipole moment surface.
2. **The four-term error budget**, next to every number.
3. **A comparison against the scaled-harmonic status quo**, so the contribution is measurable rather
   than asserted.
4. **A pre-registered, fail-closed identification** against one frozen JWST/PAHdb product, including
   the isomer-degeneracy rule and the negative control.
5. **A reliability layer** that refuses a verdict without citing measured value against threshold.
6. **An honest limitations section** naming every species and every quantity the method cannot
   reach — size, charge, missing DMS, GVPT2 breakdown — and stating that line lists remain out of
   scope.

Industry frame: **reliability-gated spectral identification for astrochemistry.**

---

## 6. Approach constraints

- **Borrow the representation; own the anchor.** Established architectures (equivariant MLIPs),
  established local-correlation methods and established VPT2/VCI machinery are used as-is. The
  contribution is the **gold anchor**, the **error budget** and the **fail-closed rule** — not a new
  network. Reinventing a wheel to avoid a comparison is forbidden.
- **Reproduce before improving.** The published baseline is reproduced first. Nothing downstream is
  interpretable otherwise.
- **The electron-density field survives as the dipole surface, not the energy surface.** Because a
  promolecular reference gives \(\boldsymbol\mu=-\int\mathbf r\,\Delta\rho\,dV\) exactly, the field
  model competes as a DMS against an equivariant-tensor model and a charge model, under
  pre-registration, with "inconclusive" publishable. If it loses it is dropped and the spectra ship
  regardless. It is never on the critical path.
- **Every comparison is pre-registered.** Frozen split files with hashes, ≥3 seeds, tuning parity, a
  declared effect size and a frozen analysis — committed before any leg trains.
- **Measured, not guessed.** Every budget, tolerance and cost comes from a pilot with numbers in it.
  Estimates are re-baselined from observed velocity, never defended.
- **Start as small as necessary.** Public libraries may validate mechanics or motivate custom data.
  They are not eligible pipeline labels under §3.A.

---

## 7. Forbidden quotes (delete on sight)

- "Chemically precise infrared spectral **lines**" as a deliverable.
- "Sub-wavenumber precision" as a dataset or spectral requirement.
- "Arbitrarily large PAHs" or "any size" without the measured stop rung attached.
- "We identified PAHs in a JWST spectrum" without the pre-registered list, metric and verdict rule.
- "Within X cm⁻¹" as a single pooled number with no four-term budget beside it.
- "Chemically accurate labels" before the gold-rung audit passed for that molecule and quantity.
- Any intensity claim not backed by a DMS that passed its gate.
- Any reference to Projects 10–12 as future work rather than as absorbed scope.
