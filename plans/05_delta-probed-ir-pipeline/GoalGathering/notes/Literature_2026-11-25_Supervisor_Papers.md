# The ten papers the supervisor gave on 25 November 2026: what each says for us

Written 25 Nov 16:14. The PDFs are in `Papers/` under the names given below. Martin, Taylor & Lee 1997 was read by the assistant
itself; the other nine were each read in full by a separate reader (Puzzarini 2019 selectively, the sections named there), with
questions drawn from our open problems. **Numbers from those nine are second-hand: check them in the PDF before they go into a
paper or onto a slide.** Two of slide 19's citations were wrong in the author, not in the number: 'Mackie 2026, JCP 165, 034104'
is Fleming et al., and 'Barone 2026, JCP 164, 114309' is right.

## 1. Martin, Taylor & Lee 1997 — benzene's harmonic frequencies and ANO basis sets

[Chem. Phys. Lett. 275, 414](https://doi.org/10.1016/s0009-2614(97)00735-5) · `Martin_Taylor_Lee_1997_harmonic_frequencies_benzene_ANO_CPL275_414.pdf`

- CCSD(T) harmonic frequencies of benzene at each level's own minimum, in cc-pVDZ, cc-pVTZ′ (cc-pVTZ without d on H, 234
  functions) and ANO4321′ ([4s3p2d1f/4s2p], 240 functions). The abstract: ω4 and ω5, and to a lesser extent ω17, show a
  pathological basis-set dependence 'due to basis set superposition error'; the ANO set reproduces the experimentally derived
  harmonics to 6 cm⁻¹ rms; ANO sets are recommended for unsaturated and aromatic systems.
- Table 1, CCSD(T), cc-pVDZ / cc-pVTZ′ / ANO4321′: ω4 (b2g) 624.9 / 677.3 / 708.8; ω5 (b2g) 947.5 / 972.3 / 1008.8; ω10 (e1g)
  847.2 / 858.5 / 865.1; ω11 (a2u) 676.6 / 685.6 / 687.2; ω16 (e2u) 394.6 / 401.9 / 405.8; ω2 (a1g C–H) 3212.1 / 3202.7 /
  3209.9. Against the HMA experimental set, cc-pVTZ′ is off by 37 (ω4), 28 (ω5), 16 (ω13), 14 (ω14) and 15 (ω17) cm⁻¹.
- Geometry: full CCSD(T)/cc-pVTZ r(CC) = 1.3975, r(CH) = 1.0831 Å; best estimate 1.392(2) and 1.081 Å.
- **For us.** (a) Our CCSD(T)/cc-pVTZ Hessian, taken at the B3LYP geometry and corrected with the first-order geometry term
  (25 Nov), gives ω4 674.1, ω5 967.3, ω10 856.0, ω11 684.7, ω16 401.2, ω12 1010.5 — within 1–5 cm⁻¹ of their cc-pVTZ′ values at
  the true cc-pVTZ minimum (ω3 and ω2 differ by 9 and 7): an independent confirmation of our Hessian and of the geometry term.
  Our B3LYP C–H length plus the Newton step, 1.0871 − 0.0033 = 1.0838 Å, against their 1.0831. (b) An ANO basis of the same
  size as cc-pVTZ cures ω4 and ω5 at the CCSD(T) level. Whether an ANO basis in an MP2 step does, the paper does not say.

## 2. Moran et al. 2006 — popular methods predict benzene and arenes nonplanar

[J. Am. Chem. Soc. 128, 9342](https://doi.org/10.1021/ja0630285) · `Moran_2006_benzene_arenes_nonplanar_JACS128_9342.pdf`

- Correlated methods (MP2, MP3, CISD, CCSD) with Pople-type basis sets rich in s, p, d and without carbon f functions give
  imaginary out-of-plane frequencies for planar benzene (b2g, sometimes e2u and e1g); naphthalene, anthracene and pyridine fail
  at the same levels. MP2 with cc-pVDZ, cc-pVTZ, their augmented versions and 6-31G(d) is listed as safe; HF and DFT are always
  real. Cause: a geometry-dependent two-electron basis-set incompleteness error. ANO sets: one sentence, 'an even better choice'.
- **For us.** Our CCSD(T)/cc-pVDZ Hessian of anthracene has an imaginary out-of-plane mode (−51 cm⁻¹), beyond what the paper
  reports for cc-pVDZ (it has no CCSD(T) and no anthracene/cc-pVDZ numbers). The reader's inference, not the paper's: both parts
  of a composite carry the artefact, and an ANO basis in the MP2 step does not touch the [CCSD(T) − MP2]/cc-pVDZ difference.

## 3. Puzzarini, Bloino, Tasinato & Barone 2019 — the review

[Chem. Rev. 119, 8131](https://doi.org/10.1021/acs.chemrev.9b00007) · `Puzzarini_2019_accuracy_interpretability_computational_spectroscopy_ChemRev119_8131.pdf`
(sections read: 2.1, 2.2.3, 3.1.1, 4.2, parts of 6.1 and 6.2)

- The recommended composite for medium-sized molecules, 'cheap': CCSD(T)/cc-pVTZ + Δ(MP2/CBS) + Δ(MP2 core-valence). **No
  recommended scheme has its CCSD(T) part below cc-pVTZ**, and the review calls basis-set extrapolation and core-valence
  correlation mandatory for spectroscopic accuracy. Frozen-core CCSD(T)/cc-pVTZ harmonics: 13.8 cm⁻¹ mean error against the
  basis-set limit for two- to four-atom molecules.
- Accuracy against gas-phase experiment: 1–2 cm⁻¹ is shown only for four- and five-atom molecules at CBS-level CCSD(T); the best
  cases of 7–10 atoms are 4–7 cm⁻¹ mean error; targets are stated as 10 cm⁻¹ for medium resolution.
- Hybrid force fields: harmonic part at the high level, cubic and quartic at DFT, in normal coordinates, each at its own
  minimum, with a Duschinsky check that the two sets of modes correspond. A high-level Hessian at a lower-level geometry is not
  treated. For harmonics the review recommends a double hybrid (B2PLYP, triple-zeta); for the anharmonic part B3LYP with a
  double-zeta basis — the latter is what we do.

## 4. Barone et al. 2026 — anharmonic IR of graphene fragments and buckybowls

[J. Chem. Phys. 164, 114309](https://doi.org/10.1063/5.0313437) · `Barone_2026_anharmonicity_IR_graphene_fragments_buckybowls_JCP164_114309.pdf`

- Harmonic part: the double hybrid rev-DSD-PBEP86-D3BJ with a cc-pVTZ-F12-type basis at its own minimum; anharmonic part:
  B3LYP-D3/6-31+G* cubic, semi-diagonal quartic and dipole derivatives; GVPT2 with Fermi and Darling–Dennison resonances
  treated variationally, so overtones and combination bands have intensities. Molecules: indene, azulene, acenaphthylene,
  corannulene, sumanene (C21H12, 33 atoms, the largest). Errors against experiment: typically 5–10 cm⁻¹, mean about 5, maximum
  about 20. No CCSD(T) harmonics anywhere.
- Every out-of-plane anharmonic shift in its tables is small and negative (about −2 to −25 cm⁻¹).
- **For us.** Indene, azulene and acenaphthylene are among our reference molecules, with gas-phase data named here. Nothing in
  this paper resembles our +179 and +66 cm⁻¹ on coronene's out-of-plane skeletal modes: those are outliers against the
  literature, so our force field or our treatment is the first suspect. Their stated accuracy, 5–10 cm⁻¹, is the group's state
  of the art; 2 cm⁻¹ over 3–20 µm is beyond it.

## 5. Di Grande, Lazzari & Barone 2024 — templating fragments for geometries

[J. Chem. Theory Comput. 20, 9243](https://doi.org/10.1021/acs.jctc.4c00900) · `DiGrande_2024_templating_fragments_geometries_JCTC20_9243.pdf`

- Geometries only. A large molecule is optimised at a cheap level, cut into hydrogen-capped fragments, and each geometrical
  parameter gets the fragment's (accurate − cheap) difference; uncovered parameters get a regression per atom pair. With benzene
  as the only template, B3LYP's rotational constants of naphthalene and anthracene go from about −0.9 % to within ±0.06 %.
  B3LYP bonds are systematically long, 4.5 mÅ against the double hybrid. A database of accurate structures (PCS141) includes
  benzene, naphthalene, anthracene, fluorene, pyrazine and quinoline.
- **For us.** It is the geometry analogue of our learned Hessian correction, fixed instead of learned. Two uses: accurate
  structures to score our Newton-step geometries against, and a cheap way to supply the shift to the better minimum that the
  geometry term needs for a molecule the network has not seen.

## 6. Bloino, Biczysko & Barone 2012, and Bloino 2015 — GVPT2 and anharmonic intensities

[J. Chem. Theory Comput. 8, 1015](https://doi.org/10.1021/ct200814m) · `Bloino_2012_general_perturbative_approach_GVPT2_JCTC8_1015.pdf`
[J. Phys. Chem. A 119, 5269](https://doi.org/10.1021/jp509985u) · `Bloino_2015_VPT2_route_near_infrared_JPCA119_5269.pdf`

- The Fermi criteria of the 2015 paper are a 200 cm⁻¹ frequency window and a Martin parameter of at least 1 cm⁻¹: **identical
  to ours**. DVPT2 drops the resonant terms, GVPT2 puts them back variationally (the reference method). HDCPT2 is a
  threshold-free mix of VPT2 and a degeneracy-corrected form (α = 1.0, β = 5.0e5); on toluene it is within 3 cm⁻¹ of GVPT2.
- A '1-1' Darling–Dennison resonance in the 2015 paper is for modes within 2 cm⁻¹ of each other; our coronene pair is 164 cm⁻¹
  apart, so by that definition it is not one. Neither paper describes our pattern; both say VPT2 is for semirigid systems and
  that low-frequency anharmonic contributions are not reproduced well by perturbation theory.
- Degenerate modes: the 2012 paper lowers the symmetry by changing one atom's mass by about 1e-3 amu and uses asymmetric-top
  formulas; the 2015 paper excludes them. Our averaging of quartic constants over a degenerate pair is neither endorsed nor
  refuted. Leaving a resonance at a degenerate pair deperturbed is the truncated treatment they warn against.
- Hybrid schemes: either add the DFT anharmonic correction to the better harmonic frequency afterwards, or put the better
  harmonic frequencies into the VPT2 with DFT cubic and quartic constants (the conversion to dimensionless constants then uses
  the better frequencies). Stated accuracy: about 10 cm⁻¹ or better. Anharmonic intensities need second and semi-diagonal third
  dipole derivatives. Each level sits at its own minimum; nothing on a Hessian at another level's geometry.

## 7. Qu et al. 2026 — MULTIMODE and machine-learned potentials

[J. Chem. Phys. 164, 134116](https://doi.org/10.1063/5.0320718) · `Qu_2026_MULTIMODE_machine_learned_potentials_JCP164_134116.pdf`

- A short review and a software paper: variational VSCF/VCI on a full potential surface fitted per molecule (thousands of
  CCSD(T) energies, or MP2 transfer-learned to CCSD(T)), for molecules of about ten atoms; tens of core-hours per molecule; a
  three- against four-mode representation alone differs by 5–10 cm⁻¹; on formic acid dimer the low modes miss experiment by up
  to 30 cm⁻¹. No transferable correction across molecules.
- **For us.** Not our method and not scalable to PAHs, but its machinery takes a force field as input: a variational treatment
  of a chosen pair of modes on one- and two-dimensional cuts is the direct check of our coronene shifts. Closest prior work to
  cite for learning across levels: Käser & Meuwly (its reference 105).

## 8. Fleming et al. 2026 — vibrational carbon character of astronomical PAHs

[J. Chem. Phys. 165, 034104](https://doi.org/10.1063/5.0331629) · `Fleming_2026_vibrational_carbon_character_astronomical_PAHs_JCP165_034104.pdf`

- Splits every band into aromatic, aliphatic and ethynyl carbon character by local-mode theory (Konkoli–Cremer), on indene and
  2-ethynyltoluene at B3LYP/N07D with VPT2 and polyads in a modified SPECTRO. The 'aliphatic' 3.4 µm band of indene is 45.5 %
  aromatic; many bands near 6.2 µm are combination bands and overtones. It calls coupled-cluster frequencies for PAHs
  'computationally intractable'.
- **For us.** (a) The decomposition of each normal mode over bond, angle and dihedral coordinates needs only what we have (the
  Hessian, the modes, the Wilson B matrix): a continuous alternative to our four kinds by frequency window. (b) Satellite bands
  can be combination bands that borrow intensity; that should be excluded before the 6.0 µm band is put down to carbonyl. (c)
  Indene and 2-ethynyltoluene have gas-phase spectra (Esposito et al., MNRAS 535, 3239, 2024) and are test molecules outside
  our training families.

## 9. Hanson-Heine 2026 — scaling factors follow a power law (preprint)

[ChemRxiv](https://doi.org/10.26434/chemrxiv.15000348/v1) · `HansonHeine_2026_scaling_factors_power_law_chemrxiv_v1.pdf`

- ν = λ1 · ω^(λ2 + 1), fitted on 894 fundamentals of small molecules for B3LYP and B97-1 with three basis sets (not 6-31G*): for
  B3LYP/aug-cc-pVTZ the mean absolute deviation is 14.0 cm⁻¹ against 21.7 for one constant factor and 16.2 for three regional
  constants. Not peer reviewed; one of its tables looks shifted by a row. No aromatics.
- **For us.** A possible second baseline beside the three regional factors, after a refit of the two parameters at
  B3LYP/6-31G* on our own set. Low priority.

## What the ten together say about the goal

- No paper here shows 2 cm⁻¹ for a molecule of our size. The review shows 1–2 cm⁻¹ for four- and five-atom molecules at
  CBS-level CCSD(T); the group of four of these papers reports 5–10 cm⁻¹ typical for PAH-sized molecules with a double hybrid
  and GVPT2. This belongs in what we tell the supervisor when we ask what 2 cm⁻¹ must hold against.
- Our reference recipe differs from every recommended one in three ways: the CCSD(T) part is in a double-zeta basis, there is no
  extrapolation to the basis-set limit, and core-valence correlation is left out. The first is the price; the other two are MP2
  steps and cheap to test.
- The geometry route (a high-level Hessian at the cheap geometry, corrected in first order) is treated in none of them. Our own
  check against Martin, Taylor & Lee is, so far, its only outside confirmation.

## The learning points, by where they touch the project (25 Nov 18:07)

The list given to the user in the chat that evening, kept here in full. The user found it too long to share with the supervisor
as it is: a version of five to seven points for her is still to be made (TASKS 308). First-hand: Martin, Taylor & Lee; the rest
second-hand until checked in the PDF.

**The reference Hessian**
- Our geometry term is confirmed from outside: our CCSD(T)/cc-pVTZ Hessian of benzene, corrected to its own minimum, lies 1–5
  cm⁻¹ from the published cc-pVTZ values on six modes; our corrected C–H length is 1.0838 Å against their 1.0831. [Martin, Taylor & Lee 1997](https://doi.org/10.1016/s0009-2614(97)00735-5)
- An ANO basis of the size of cc-pVTZ cures benzene's ring puckering and C–H wag at the CCSD(T) level (709 and 1009 cm⁻¹ against
  677 and 972); the authors' cause is basis-set superposition. [Martin, Taylor & Lee 1997](https://doi.org/10.1016/s0009-2614(97)00735-5)
- The fault is not benzene's alone: correlated methods without carbon f functions give too low or imaginary out-of-plane modes
  for planar aromatics, naphthalene, anthracene and pyridine included; Hartree–Fock and DFT do not. [Moran et al. 2006](https://doi.org/10.1021/ja0630285)
- Our recipe differs from every recommended one in three ways: the CCSD(T) part is never below cc-pVTZ there, the basis set is
  extrapolated, and a core-valence term is added. The last two are MP2 steps, cheap to try. [Puzzarini et al. 2019](https://doi.org/10.1021/acs.chemrev.9b00007)
- A double hybrid is a serious alternative as the reference: used for the harmonics of PAHs up to 33 atoms, without CCSD(T). [Barone et al. 2026](https://doi.org/10.1063/5.0313437)
- Our route — a high-level Hessian at a cheaper method's geometry, corrected afterwards — is in none of the ten papers; each
  level sits at its own minimum.

**The goal of 2 cm⁻¹**
- Nobody shows it at our size: 1–2 cm⁻¹ only for four- and five-atom molecules at CBS-level CCSD(T); 4–7 for the best cases of
  seven to ten atoms. [Puzzarini et al. 2019](https://doi.org/10.1021/acs.chemrev.9b00007)
- For PAH-sized molecules 5–10 cm⁻¹ is the state of the art, up to 20. [Barone et al. 2026](https://doi.org/10.1063/5.0313437)
- Even variational calculations on a CCSD(T) surface miss experiment by up to 30 cm⁻¹ on low modes of a ten-atom system. [Qu et al. 2026](https://doi.org/10.1063/5.0320718)

**The anharmonic step**
- Our Fermi thresholds (200 cm⁻¹, 1 cm⁻¹) are the literature's. [Bloino 2015](https://doi.org/10.1021/jp509985u)
- Coronene's two modes are not a Darling–Dennison 1-1 resonance by the usual definition (164 cm⁻¹ apart against 2). [Bloino 2015](https://doi.org/10.1021/jp509985u)
- Our coronene shifts (+179, +66) are outliers: in comparable molecules every out-of-plane anharmonic shift is small and
  negative, −2 to −25 cm⁻¹. Our force field or treatment is the first suspect. [Barone et al. 2026](https://doi.org/10.1063/5.0313437)
- Perturbation theory is for semirigid molecules; low modes need a variational treatment of a few modes as the check. [Bloino et al. 2012](https://doi.org/10.1021/ct200814m) [Qu et al. 2026](https://doi.org/10.1063/5.0320718)
- HDCPT2 is a threshold-free variant within 3 cm⁻¹ of GVPT2: a second route beside ours. [Bloino et al. 2012](https://doi.org/10.1021/ct200814m)
- Our handling of degenerate modes is not backed by anything: we average over the pair, the literature lowers the symmetry by
  a small mass change; leaving a resonance at a degenerate pair deperturbed is the truncation warned against. [Bloino et al. 2012](https://doi.org/10.1021/ct200814m)
- Combination bands and overtones need second and third dipole derivatives, which we do not compute. [Bloino 2015](https://doi.org/10.1021/jp509985u)
- The hybrid we use — harmonic part at a high level, anharmonic part from B3LYP in a small basis — is the common one.

**Large molecules**
- A cheap geometry can be corrected per fragment: with benzene alone as template, naphthalene's and anthracene's rotational
  constants go from −0.9 % to within 0.06 %. The geometry analogue of our learned correction, and a way to supply the shift to
  the better minimum for an unseen molecule. A database of accurate structures (benzene, naphthalene, anthracene, fluorene,
  pyrazine, quinoline) to score our corrected geometries against. [Di Grande et al. 2024](https://doi.org/10.1021/acs.jctc.4c00900)
- Nobody treats more than 33 atoms spectroscopically; none of the ten covers the carry to 30–80 carbon atoms. [Barone et al. 2026](https://doi.org/10.1063/5.0313437)

**Kinds of vibration and satellite bands**
- A mode has no sharp character: local modes split each normal mode over bonds, angles and torsions, from what we already
  hold — a continuous alternative to our four kinds by window. [Fleming et al. 2026](https://doi.org/10.1063/5.0331629)
- Bands are often not one mode: near 6.2 µm in indene many are combination bands and overtones borrowing intensity. To be
  excluded before the 6.0 µm satellite is put down to carbonyl. Indene's 'aliphatic' 3.4 µm band is 45 % aromatic. [Fleming et al. 2026](https://doi.org/10.1063/5.0331629)

**Test molecules and data**
- Indene, azulene and acenaphthylene are references of ours and are in Barone's tables with gas-phase data and GVPT2
  positions. [Barone et al. 2026](https://doi.org/10.1063/5.0313437) Indene and 2-ethynyltoluene have measured gas-phase spectra and lie outside our training families. [Fleming et al. 2026](https://doi.org/10.1063/5.0331629)

**The baseline**
- Scale factors may follow a power law instead of three regional constants (14.0 against 16.2 cm⁻¹ on small molecules): a
  preprint, no aromatics, not our basis set, one table apparently shifted. At most a second baseline after our own refit. [Hanson-Heine 2026](https://doi.org/10.26434/chemrxiv.15000348/v1)

**Beside the content**
- Slide 19 names the wrong author: 'Mackie 2026, JCP 165, 034104' is Fleming, Esposito, Fortenberry, Quintano & Kraka.
- Fleming et al. call coupled-cluster frequencies for PAHs 'computationally intractable': how the field will receive our
  reference Hessians.
