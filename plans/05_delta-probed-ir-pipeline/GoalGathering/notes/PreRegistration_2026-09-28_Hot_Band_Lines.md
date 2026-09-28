# Pre-registration 2026-09-28, 18:3x — hot-band lines as a reported output (task row 11)

**Why.** The pipeline scores the 0→1 fundamentals. The GVPT2 step already computes the anharmonic constants χ_ij (`src/dpir/qff.py`, `vpt2()`:
Mills' expressions, `chi` returned beside `nu`), and those constants also place the hot bands — the sequence bands ν_a + ν_b − ν_b that a
laboratory cell at room temperature shows beside every low-lying fundamental, and that an astronomical emission spectrum of a hot PAH is made
of. The user (27 Sep 16:4x) asked for this small extension to be on the list: report the hot-band positions per molecule, **unscored**, labelled
as *DFT-anharmonic offsets on the corrected harmonic part*. This note fixes, before any number is read, which transitions, which read-out and
which pass lines the first check uses. Two laboratory anchors exist and were found before this note (`Relevant_Scientific_Papers.md` items 53
and 89): benzene's ν₁₁ hot bands (Hollenstein, Piccirillo, Quack & Snels 1990) and naphthalene's ν₄₆ / ν₄₈ hot bands (Pirali et al. 2009).

## 1. The quantity

In Mills' convention, E(v)/hc = Σ_i ω_i (v_i + ½) + Σ_{i≤j} χ_ij (v_i + ½)(v_j + ½) (degeneracy terms aside), so:

- **sequence band** ν_a + ν_b − ν_b (a ≠ b; the molecule already carries one quantum of ν_b): origin = ν_a + χ_ab, i.e. an **offset of χ_ab** from the fundamental;
- **overtone sequence** 2ν_a − ν_a: origin = ν_a + 2 χ_aa, an **offset of 2 χ_aa**.

`vpt2()` returns χ with the same convention (ν_i = ω_i + 2 χ_ii + ½ Σ_{j≠i} χ_ij), so the offsets are read directly from the `chi` array of a QFF
record; for a doubly degenerate ν_b the two Cartesian components carry equal χ_ab by symmetry and the reported offset is their mean, with the
spread printed as a check. The **reported output per molecule** is, for every fundamental ν_a the pipeline scores: the offsets χ_ab for the low-
lying modes b with ω_b ≤ 1,000 cm⁻¹ (the thermally populated ones), the overtone-sequence offset 2 χ_aa, and the Boltzmann weight
exp(−hc ω_b / kT) at 300 K as the relative population of the lower level (an indication of intensity, not a computed intensity). The positions
are **DFT offsets added to the pipeline's corrected fundamental** (ω′-based ν_a), never a corrected χ: the correction of layer B touches the
harmonic part; the anharmonic part stays at the DFT level and is labelled so in every table.

## 2. First check — benzene, on the record that exists (desk test, minutes)

Record: `probes/results_vpt2/qff_benzene_pyscf_analytic_d010_2026-09-21.npz` (two-route QFF from pyscf analytic B3LYP/6-31G* Hessians,
`chi_sym` and `chi_raw`; the benchmark of 22 Sep maps modes 0/1 = ν₁₆ (e2u), 2/3 = ν₆ (e2g), 4 = ν₁₁ (a2u), 5 = ν₄ (b2g)). Script:
`probes/hot_band_desk_benzene.py` (written with this note; prints the table and writes `probes/results_vpt2/hot_bands_benzene_2026-09-28.json`).

Measured (Hollenstein et al. 1990, abstract; fundamental 673.97465 cm⁻¹): ν₁₁+ν₆−ν₆ at −0.466, ν₁₁+ν₁₆−ν₁₆ at −1.099, 2ν₁₁−ν₁₁ at +0.127 cm⁻¹
(the effective x₁₁,₆, x₁₁,₁₆ and 2x₁₁,₁₁ to 10⁻⁴ cm⁻¹). Read-out: our χ₁₁,₆ (mean of components 2/3), χ₁₁,₁₆ (mean of 0/1) and 2 χ₁₁,₁₁ from
`chi_sym`, with `chi_raw` beside them as the noise check of the two routes.

**Pass lines, fixed now.**
- P1 (sign): the three offsets carry the measured sign, 3 of 3. One wrong sign = fail; the reported output is then labelled "sign not validated"
  until a higher level of theory is tried.
- P2 (size): each predicted offset lies within a factor of 2 of the measured one or within 0.3 cm⁻¹ of it, whichever is wider. The 0.3 cm⁻¹
  floor is the resolution a B3LYP/6-31G* quartic force field can be expected to have on constants of this size (the fundamentals themselves sit
  8–11 cm⁻¹ above experiment in the benchmark of 22 Sep). 3 of 3 = pass; 2 of 3 = "reported with the miss named"; fewer = fail.
- P3 (noise): |χ_sym − χ_raw| ≤ 0.1 cm⁻¹ for the three constants; otherwise the two-route noise, not the physics, sets the number, and the
  reading of P1–P2 is suspended until the d005/d010 comparison of 21 Sep is repeated on these constants.

**Prediction on record (before the numbers).** P1 passes (the signs of low-mode sequence constants are dominated by the cubic coupling to
the ring-breathing mode and rarely change with the functional); P2 passes for x₁₁,₁₆ and x₁₁,₆ and is undecided for 2x₁₁,₁₁, which is small
(0.127) and sits near the noise floor.

## 3. Second check — naphthalene, after a DFT QFF exists (laptop, hours)

Pirali et al. 2009 (item 53, on disk; numbers read from the paper before this step runs and copied here in a dated amendment): the ν₄₆ (C–H
out-of-plane, 782.3 cm⁻¹) sequence bands ν₄₆+ν₁₆−ν₁₆ at 779.7 and ν₄₆+ν₁₃−ν₁₃ at 782.9 (offsets −2.6 and +0.6 cm⁻¹) and the ν₄₈ sequence
spaced −0.3 cm⁻¹. The DFT QFF for naphthalene does not exist yet: the two-route pyscf route of 21 Sep costs 2 × 48 analytic Hessians at
B3LYP/6-31G* — to be timed on one Hessian before the run, after the section-11 audit of module 05 has left the laptop. Same pass lines as §2,
with the naphthalene mode mapping fixed by symmetry class and rank as in the benzene benchmark. This second check is what makes the output
a *PAH* statement rather than a benzene one.

## 4. What is reported afterwards, and where

- A per-molecule table `hot_bands_<molecule>.json/.md` beside the VPT2 record: fundamental (DFT ν, and corrected ν′ where layer B has a
  correction), lower-level mode, offset χ_ab, hot-band position, Boltzmann weight at 300 K and at the R1 temperature grid; label "DFT-anharmonic
  offset on the corrected harmonic part".
- The reading copy, §5 (outputs) one dated sentence with the benzene check's outcome, and §11 risk table only if P1 fails.
- Nothing is scored: the hot bands enter no pass line of the pipeline; they are context for the R1 temperature correction (item 53 as the
  second pinnable source) and for the emission tier, which remains inherited machinery.

## 5. Stop rule

If P1 fails on benzene, the output is still reported (labelled) and the next step is one χ at a higher level, not a search; if the naphthalene
QFF costs more than a laptop night, it waits for a free server and this note gets a dated amendment with the measured cost.
