# Project 11 — Anharmonic IR and Intensities (post-master’s)

> **ABSORBED 2026-08-23 — PROVENANCE ONLY, NOT A ROADMAP.**
> Per [Overarching_Goal.md](../GoalGathering/Overarching_Goal.md), this project's exit **is** the
> master's deliverable (**R3**): GVPT2-class anharmonic band families, relative intensities from a
> dipole moment surface, and the four-term error budget defined in section 3.4 below. Those
> requirements are now binding on Module 08. The file is kept as the specification of record for what
> R3 means; read "post-master's" as history.

**Not a Udacity module.** Not scored in Modules 02–09. Does not replace Module 08.

**Horizon role:** second wall. Given a size-extensive, gold-anchored PES from [Project 10](10_Size_Extensive_Aromatic_PES.md), produce **defensible** infrared band positions and **relative intensities** for large PAHs. Classical MD + dipole-ACF FFT stays an envelope diagnostic (Distilled Plan §9). It is not the precision path.

**Depends on:** Project 10 exit (quantified PES error vs a gold rung; transfer to the next ring did not fall apart; representation fork decided).

**Hands to:** [Project 12](12_Astrophysical_PAH_Identification.md).

---

## 1. Question

Given a transferable PES **and a dipole surface**, what nuclear-motion method produces IR that is allowed to use the word **precise** for large PAHs, and against what experiment?

“Chemically precise spectral lines” in the ExoMol / POKAZATEL sense is **not** this project. That is a line-list career. The honest product is **anharmonic band families** (3 μm, 6–9 μm, 11–12 μm) with relative intensities and a published error budget.

---

## 2. Why the master’s IR protocol is not this project

| Master’s object | What it is allowed to be here |
|---|---|
| Frozen-weight MD + dipole ACF FFT | Envelope **sanity check** only |
| 10–15 cm⁻¹ band-center gates on H₂O / benzene | Inherited diagnostic, not the precision claim |
| Intensities as relative MD envelopes | Must be replaced by a **dipole surface** + vibrational wavefunctions / VPT2 intensities |
| 300 K NVE | Not astrophysical emission (Project 12). Do not “fix” that by a longer trajectory |

Science already has small-molecule VPT2 / GVPT2 on ML PESs (MLAtom, Käser/Nandi). The new work is: **that class of nuclear motion, on the Project 10 PES, at PAH size, with intensities and a named experimental standard.**

---

## 3. Required work

### 3.1 Nuclear motion

Minimum for “chemically precise **frequencies**” in this literature:

- **GVPT2** (or VPT2 with an explicit resonance treatment)
- Hessians plus cubic / semidiagonal quartic derivatives from the Project 10 PES (analytic or well-converged numerical; same force recipe as the PES)
- A **dipole moment surface** (DMS) of documented quality for intensities

If strong resonances / congested PAH fingerprints break GVPT2, escalate to **selected VCI**. Do not escalate by running more classical MD.

Leave MD+FFT in the report as “envelope diagnostic, not the score.”

### 3.2 Intensities

- Relative band strengths from the DMS + the vibrational method above.
- Absolute line-list intensities (\(\lvert\langle f\lvert\mu\rvert i\rangle\rvert^2\) catalogs) are **out of scope** unless a third project takes on an ExoMol-grade DMS. Do not sneak them into the title.
- Report forbidden-mode residuals and charge-state intensity swaps (neutral vs cation).

### 3.3 Experimental standard (pick one and freeze it)

Compare to **one** named standard per claim:

- Gas-phase FTIR where it exists (same discipline as the master’s NIST benzene rule)
- Else NASA PAHdb matrix-isolated bands **plus a stated matrix-shift model** (Boersma et al.; Distilled Plan already cites 2–15 cm⁻¹). Do not mix uncorrected matrix and gas-phase numbers.

### 3.4 Error budget (required, or the word “precise” is banned)

Separate, as Distilled Plan §8 already demands for the master’s:

- (A) PES / ML error vs the Project 10 gold rung
- (B) electronic-structure remainder (gold vs a higher reference, where computable)
- (C) nuclear-motion error (GVPT2 vs selected VCI or vs experiment, named)
- (D) environment error (matrix shift, if used)

A single “we are within 5 cm⁻¹” number is a fail.

### 3.5 Scope of molecules

The Project 10 ladder, not a jump to C₄₈. Each size / charge that passed 10 gets an anharmonic spectrum here. If 10 stopped at a 4-ring, 11 stops there.

---

## 4. Exit criterion

You may say:

> Anharmonic band centers for [named PAH sizes and charge states] within a **stated** cm⁻¹ of [named dataset], with a published four-term error budget. Relative intensities of the diagnostic band families are reproduced to a stated integrated-intensity tolerance.

You may **not** say:

- chemically precise rovibrational **line lists**
- sub-wavenumber lines from MD+FFT
- “any size”
- JWST source identification (Project 12)

That is “chemically precise **enough for PAH band identification**,” which is what the horizon actually needs.

---

## 5. Forbidden

- Training on spectra (Wasserstein-on-FTIR, PAHdb matching as a loss). The PES remains energy-first.
- Calling MD+FFT the precision method because GVPT2 was hard.
- Shipping intensities without a DMS.
- Treating this as a Udacity module.

---

## 6. Deliverables

- Frozen Project 10 PES + documented DMS
- GVPT2 (and VCI where required) spectra for each scored size / charge
- MD+FFT envelopes retained only as a diagnostic appendix
- Error-budget table (A–D) next to every cm⁻¹ claim
- Go / no-go for Project 12 (only if band families are stable enough to confront an astrophysical excitation model)
