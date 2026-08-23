# Overarching Objective: Chemically Precise Static Labels; Frozen-Weight IR Band Envelopes

**Status (2026-08-22):** Rewritten to close professor-review blocking issue 4. §5 item 4 now names Workstream G1 (issue 6). This file is the prime directive of **this thesis**. It must agree with Distilled Plan §2 and §9. It must not be quotable as a rovibrational line-list promise.

Horizon work (very large PAHs, anharmonic band families, intensities, JWST-facing identification) is specified in post-master’s [Project 10](../CapstoneProjects/10_Size_Extensive_Aromatic_PES.md), [Project 11](../CapstoneProjects/11_Anharmonic_IR_and_Intensities.md), and [Project 12](../CapstoneProjects/12_Astrophysical_PAH_Identification.md). Those are **not** Udacity modules and are **not** scored in Modules 02–09.

---

## 1. Horizon (not scored)

The long-term scientific ambition is **chemically precise enough infrared band families and relative intensities for very large PAHs** — the object JWST / PAHdb identification actually needs — with a published error budget.

That ambition is **not** a master’s deliverable. Canonical CCSD(T) does not label arbitrarily large PAHs. A global \(N^3\) field PES does not automatically size-extend. Classical MD + dipole-ACF FFT does not produce ExoMol-style lines. Science already has a small-molecule IR-emulation stack (Gastegger ML-MD, MLAtom / ANI, VPT2). Reproducing that stack on H₂O is not a contribution.

The path from this thesis to the horizon is Projects 10 → 11 → 12, in that order.

---

## 2. This thesis (the only prime directive that counts)

Obtain a **conservative field PES and dipole surface**, trained only on static chemically precise **labels**, from which vibrational band positions and relative IR envelopes are predicted via frozen-weight classical MD. Band positions emerge from the PES; relative intensities use a statically supervised dipole surface. No spectrum, peak position or intensity is a training target.

- The scientific question is Distilled Plan §2: under identical \(E/F\) supervision and the same CCSD(T) splits, does the Field-EF architecture transfer better than MACE-EF, and what additional benefit comes from explicit density supervision (Field-EFρ vs Field-EF)?
- The scored molecules are **H₂O / D₂O / CO₂ / benzene**.
- IR is a **frozen-weight readout**. Static dipoles supervise the production dipole surface, but spectra, peak positions and intensities are never training losses.
- Large PAHs, naphthalene as a pass/fail, and “any size” are **outlook**.
- Module 08 delivers a **reliability-gated small-molecule IR-emulation stack** plus the pre-registered three-way conclusion: representation advantage, density-supervision advantage only, no demonstrated advantage, or inconclusive — not a PAH spectrometer.

If a sentence cannot survive this section, it does not belong in this file.

---

## 3. Split “chemical precision” (do not glue these again)

Sub-wavenumber is **not** a property of a CCSD(T) energy table. \(1\,\text{kcal/mol}\approx 350\,\text{cm}^{-1}\). Putting them in one parenthetical is how the documents started lying to each other.

### A. Labels (hard rule — this degree)

Train / validation / test **energies and supervised derivatives** belong to the same **CCSD(T)/cc-pVTZ** (or better) energy surface, per Distilled Plan §5.1. Derivatives may be complete gradients or seeded directional derivatives; CCSD forces must never be paired with CCSD(T) energies as targets. Density is the pinned 1-RDM recipe (default: relaxed CCSD), not a slogan “exact CCSD(T) density.”

- Module 06 sampling is **not** a deviation (proposal only; every trusted geometry is re-labelled).
- Distilled Plan §5.1 shrink-ladder **rung 3** (density proxy, energy/force still CCSD(T)) **is** a deviation and must use §4 below.

### B. Spectra (adopt Distilled Plan §9 here)

This thesis does **not** claim:

- chemically precise spectral **lines**
- rovibrational line-list precision
- sub-wavenumber line positions from classical MD + FFT

The allowed spectral claim is §9’s:

> Vibrational band positions and relative IR envelopes/intensities from a static-label-trained PES and dipole surface, within a **stated** cm⁻¹ tolerance (Phase 2/5: 10–15 cm⁻¹, not 0.1 cm⁻¹), for H₂O, D₂O, CO₂, and benzene.

ExoMol / HITRAN / NIST are **blind envelope checks**, never a training loss and never a line-list score. Intensities mean **relative envelopes** and forbidden-mode residuals, not \(\lvert\langle f\lvert\mu\rvert i\rangle\rvert^2\) line lists.

---

## 4. Rules for deviation (labels only)

Deviate from §3.A only if there is **absolutely no other technical solution**, and only with an extremely compelling, written reason. Compromising the mathematical accuracy of the baseline **label** sets is the last resort.

This clause is **not** a license to call an FFT a line list. It does not move large PAHs into the scored master’s scope.

Named use already in the plan: §5.1 shrink-ladder rung 3.

---

## 5. What Module 08 may put on the table

A gated system assembled from prior artifacts:

1. Conservative field PES (P1 on H₂O; 05 on benzene if the §5.1 pilot allows).
2. Band envelopes from frozen-weight MD + dipole ACF FFT, within the stated cm⁻¹, with no spectral fitting. Dipoles are statically supervised; dipole derivatives remain evaluation-only.
3. A fail-closed reliability layer (07). If P1 missed gates, 08 says the field claim is incomplete.
4. Evidence the field was worth it: 04 (simple NN) plus the pre-registered **Field-EF vs MACE-EF** equal-label test and **Field-EFρ vs Field-EF** density-supervision ablation. P1/05 train the field legs; **G1** trains MACE-EF on the same splits; 08 only assembles the table. If Field-EF or G1 is missing, say the §2 representation claim is incomplete.
5. A proposal mechanism (06), not a data source.
6. An honest scope sentence: JWST / large-PAH identification is **why anyone would care later**. It is not a capability that was built.

Industry frame: **reliability-gated spectral emulation for small molecules.** PAH identification is Projects 10–12.

---

## 6. Approach constraints (unchanged in spirit)

- Start as small as necessary. QM9 / ANI-1ccx may validate **mechanics** or motivate custom data (Module 02). They are not chemically precise pipeline labels.
- Leverage existing architecture families (FNO, NCA, equivariant GNNs as **baselines**). Do not reinvent a wheel to avoid a comparison.
- The ML pipeline is a means. Any method that honestly answers §2 on gold labels is valid. Glue without the field-vs-GNN test is not a thesis.

---

## 7. Forbidden quotes (delete if they reappear)

- “Chemically precise anharmonic infrared spectral lines” as a **this-thesis** deliverable.
- “Sub-wavenumber precision” as a **dataset** requirement.
- “Arbitrarily sized PAHs” as something Module 08 acquires.
- “We identified PAHs in a JWST spectrum” as a master’s result.
