# Methyl internal rotors inside VPT2/GVPT2 IR prediction: method families and software

Scope: nearly free CH3 torsions (V3 a few to a few hundred cm-1, harmonic torsion < ~150 cm-1) in methyl
(hetero)aromatics of 12-60 atoms, with B3LYP/6-31G* pyscf Hessians as the electronic-structure input.
Already known and not repeated: arXiv 2209.04392 (V30, VPT2+R), PMC4553754 (HDCPT2 automatic hindered
rotors), Nejad & Crittenden PCCP 2020 (d0cp03515g). Research budget: about 25 tool calls (4 Nov 2026);
gaps are named where a source was not reached.

## 1. Decoupling the torsion from VPT2 (zeroed cubic/quartic terms, reduced dimensionality, VPT2+R)

### Takeaway
Decoupling is done in practice by setting every cubic and quartic force constant that carries the torsion
index to zero (torsion kept harmonic, or replaced by a 1D model as in VPT2+R); this is the standard
practice for methylated PAHs. The experienced VPT2 practitioners report that reduced-dimensionality VPT2
seldom improves the high-frequency modes, and no source found quantifies the shift it causes in the
methyl C-H stretches or CH3 deformations of a methyl aromatic, so our 5.9 cm-1 shift of the methyl bends
is not checkable against a published number.

### Cited Findings
- Mackie et al. (PCCP 2018, 20, 1189-1197) computed anharmonic QFF spectra of 9-methylanthracene,
  9,10-dimethylanthracene and four hydrogenated PAHs (Gaussian09 force fields, locally modified SPECTRO for
  VPT2 with polyads). Because of "known issues" with the low-barrier free-rotor methyl modes, they set the
  cubic and quartic force constants involving those modes to zero, treating them harmonically. They also
  report instability of the B97-1/TZ2P quartic force field for PAHs. — [Mackie et al. 2018, PCCP (open access)](https://pubs.rsc.org/en/content/articlehtml/2018/cp/c7cp06546a)
- Franke, Stanton & Douberly (J. Phys. Chem. A 2021, 125, 1301-1324, "How to VPT2"): "reduced-
  dimensionality schemes (i.e., VPT based on a force field that neglects low-frequency coordinates) have
  sometimes been used"; "in the experience of the authors, reduced dimensionality schemes seldom lead to
  higher-accuracy predictions for the high-frequency vibrations." They note that much LAM error is often
  isolated in the low-frequency normal coordinates, so high-frequency predictions remain "reasonable but
  diminished" for floppy alkyl radicals with methyl tops (n-/i-propyl). Examples of reduced-dimensionality
  use cited there: Biczysko, Bloino & Puzzarini, WIREs Comput. Mol. Sci. 2018, 8, e1349; Raston et al.,
  J. Chem. Phys. 2013, 138, 194303 (ethyl radical). — [Franke, Stanton, Douberly 2021 (NSF PAR copy)](https://par.nsf.gov/servlets/purl/10284833)
- Yang & Bloino (J. Phys. Chem. A 2022, 126, 9276-9302) restrict their automated resonance treatment to
  "sufficiently rigid molecules", state that LAM problems "cannot be overcome purely within VPT2" and need
  hybrid schemes, and describe bottom-up reduced-dimensionality models: choose active modes, build the
  anharmonic force field for them, add modes whose couplings to the active set are significant. No error
  numbers for the reduced-dimensionality step are given in the part read. — [Yang & Bloino 2022, PMC9761684](https://pmc.ncbi.nlm.nih.gov/articles/PMC9761684/)
- Mendolicchio & Barone (J. Chem. Phys. 2025, 162, 154114): soft modes are separated; hindered rotations
  get a 1D hindered-rotor model while the rest stays VPT2. For acetaldehyde's methyl torsion, Gaussian 16's
  automatic detection gives entropy 63.10 vs 63.06 cal/(mol K) experiment; treating the torsion with VPT2
  is off by about 0.39 cal/(mol K). Thermochemistry only; no spectral shift of the remaining modes. — [Mendolicchio & Barone 2025, JCP](https://pubs.aip.org/aip/jcp/article/162/15/154114/3344543/Vibrational-second-order-perturbation-theory-based)
- Gaussian keyword for mode selection: the search found only `Freq=(Anharmonic, ReadAnharm, HPModes)`
  inputs in the literature (iGVPT2 / ML-VPT2 papers); no documentation of a keyword named "ReadAnhMode"
  was found. — [iGVPT2, arXiv 1704.02144](https://arxiv.org/pdf/1704.02144); [arXiv 2103.05491](https://arxiv.org/pdf/2103.05491)

### Inferences
- The zeroing practice of Mackie et al. is the same operation as our "decouple the torsion" read; it is the
  established remedy in the astro-PAH line of work (the methylated-PAH paper is co-authored by A.
  Petrignani). It removes the torsion's contribution to the X matrix of the other modes (the chi_{t,i}
  terms and the cubic terms with the torsion index in the second-order sums), so the shift of the remaining
  fundamentals equals the sum of those removed terms. Our 5.9 cm-1 is therefore a direct measure of how large
  the rectilinear torsion couplings are on the bends, not an error estimate by itself.
- Inference from memory, unverified here: Gaussian 09 had `Freq=SelectAnharmonicModes`; Gaussian 16 moved
  mode selection into the `ReadAnharm` input section. The user's "ReadAnhMode" may be one of these; check
  the G16 Freq manual page before citing.

### Gaps
- No source found gives the error of reduced-dimensionality VPT2 on methyl C-H stretches (2850-3000 cm-1)
  or CH3 deformations (1400-1550 cm-1) against experiment for toluene, picolines, xylenes, methylimidazoles,
  methylnaphthalenes or methylpyrazines.
- Mackie et al. 2018's per-band effect of zeroing (with vs without) was not reached in the excerpt.

## 2. Hindered-rotor models (1D Pitzer/Fourier, HDCPT2 detection, grid-variational torsion)

### Takeaway
The 1D torsion is solved separately on a relaxed scan with a Fourier potential (V3, V6, ...) and an
effective or reduced moment of inertia, typically by periodic DVR; this fixes the torsional levels and
thermochemistry but leaves the torsion-vibration coupling out, and in toluene-type rotors that coupling is
large enough to shift fitted F and V6 substantially.

### Cited Findings
- Barone (arXiv 2610.20488, 14 Oct 2026, single author, preprint): torsions assigned to DVR are excluded
  from the VPT2 polyad indices; relaxed geometries at fixed torsion give potential, inertia and properties
  along the path ("adiabatic DVR"); selected transverse states can be kept as coupled channels. Methyloxirane
  (B3LYP/6-31G*): 24 relaxed points at 15 deg, threefold Fourier potential, barrier 890.46 cm-1, effective
  inertia matched to the 212.27 cm-1 harmonic torsion, first excited torsional manifold centroid 200.88
  cm-1. (S)-2-methylaziridine: barriers 830.59 / 963.59 cm-1, torsions 209.21 / 225.52 cm-1. Acetic acid's
  67.2 cm-1 torsion is taken out of the mid-IR polyad and given a separate DVR. A search summary of the same
  preprint states that methyl rotor levels shift only slightly between independent 1D DVRs and coupled
  DVRs (number not reached). Implementation called TRINITY; licence not stated. — [Barone 2026, arXiv 2610.20488](https://arxiv.org/html/2610.20488v1)
- Baiardi, Bloino & Barone (2017) coupled VPT2 to a 1D-DVR treatment of one large-amplitude vibration
  (applied to the methyl-cyclopropenyl cation); according to a 2020 Frontiers article the 1D-DVR is in the
  development version of Gaussian, not the release. — [Frontiers in Chemistry 2020, 10.3389/fchem.2020.584203](https://www.frontiersin.org/journals/chemistry/articles/10.3389/fchem.2020.584203/full)
- Toluene torsion-vibration coupling: it provides the dominant contribution to several torsion-rotation
  constants in toluene and is linked to methyl precession; including it revises the S1 barrier V6 from
  -26.376 to -5.59 cm-1 (Gascooke, Virgo & Lawrance); Gardner & Wright (J. Chem. Phys. 2011, 135, 114305)
  on toluene. A second aromatic with a quantified torsion / methyl out-of-plane wag interaction is reported. — [Aust. J. Chem. CH23122, "Evidence for widespread torsion-vibration interaction in substituted toluenes"](https://publish.csiro.au/CH/CH23122)
- Wright group (para-fluorotoluene): torsion-vibration interactions alter F (the methyl internal-rotation
  constant) and V6. — [Nottingham repository, internal rotor states pFT](https://nottingham-repository.worktribe.com/preview/809338/Internal%20rotor%20states%20pFT%20v16%20sub-revised-a.pdf)

### Inferences
- For our 12-60-atom methyl aromatics the V3 barriers are low (toluene's V6-type barrier is a few cm-1, by
  our knowledge; not sourced here), so a 1D Fourier/DVR torsion is close to a free rotor. It gives correct
  torsional levels but says nothing about how the torsion perturbs the CH3 bends and stretches, which is the
  quantity our noise flag concerns. The coupling the Wright/Lawrance spectroscopy measures is to the methyl
  out-of-plane wag and low ring modes, not to the 1400-1550 or 2850-3000 cm-1 bands.

### Gaps
- Explicit Pitzer reduced-moment formulas and V3/V6 fits for picolines, xylenes, methylimidazoles were not
  retrieved in this pass.

## 3. Hybrid schemes (VPT2 + variational torsion block; reduced VSCF/VCI; adiabatic separation; local-mode models)

### Takeaway
Three working routes exist: (a) VPT2 for small-amplitude modes plus a DVR torsion that can carry coupled
channels (Barone/Bloino line, Gaussian development or TRINITY); (b) variational VSCF/VCI in curvilinear
coordinates with a large-amplitude torsion (Rauhut/Molpro, Tew-Handy-Carter MULTIMODE); (c) for the
methyl C-H stretch region, Sibert-type local-mode effective Hamiltonians or VPT2+K large polyads that couple
CH stretches to doubly excited HCH scissor states. Route (c) targets exactly the 2850-3000 cm-1 band, and
none of the routes found gives a methyl-aromatic benchmark of the bends.

### Cited Findings
- Sibert, Tabor, Kidwell, Dean & Zwier (2014): stretch-bend Fermi resonance model extended to CH3 and
  methoxy groups; CH3 bends treated as local scissor vibrations; anharmonic couplings are fairly transferable
  between molecules, harmonic terms vary more. Based on the curvilinear local-mode Hamiltonian of J. Chem.
  Phys. 2013, 138, 064308. — [Sibert group publication page](https://sibert.chem.wisc.edu/publication/fermi-resonance-effects-in-the-vibrational-spectroscopy-of-methyl-and-methoxy-groups/); [IDEALS abstract](https://ideals.illinois.edu/items/90868)
- Tabor et al. (J. Chem. Phys. 2016, 144, 224310) modelled conformation-specific IR of ethyl-, n-propyl-
  and n-butylbenzene; in the "simple model" each methyl contributes three scissor coordinates, all
  (1/2)X(X+1) doubly excited scissor states are coupled to the CH stretch fundamentals. Franke et al. 2021
  adapt this as VPT2+K with large effective Hamiltonians in normal coordinates, which can also include
  [scissor + C=C stretch] states and Darling-Dennison terms (minor in the CH region). The local-mode model
  needs no anharmonic force field. — [Franke, Stanton, Douberly 2021](https://par.nsf.gov/servlets/purl/10284833)
- Franke et al. 2021: for severe LAM the normal-mode starting point "should be abandoned in favor of
  descriptions based on curvilinear internal coordinates and more expansive potential energy surfaces",
  citing DVR (Colbert & Miller) and VSCF extensions (Changala & Baraban, curvilinear VMP2); "more
  sophisticated ways of correcting for LAM" are cited as Tew, Handy & Carter, PCCP 2001, 3, 1958 (glyoxal
  with MULTIMODE, explicit large-amplitude motion), "not widely implemented". — [Franke et al. 2021](https://par.nsf.gov/servlets/purl/10284833)
- Franke et al. 2021: an additive hybrid (anharmonic correction from a small basis applied to a large-basis
  harmonic) is not recommended for CH stretches, since stretch-bend coupling is underestimated and CH
  harmonics in a small basis are too high by 10-20 cm-1 or more. — [Franke et al. 2021](https://par.nsf.gov/servlets/purl/10284833)
- Changala & Baraban: ab initio effective rotational/rovibrational Hamiltonians for non-rigid systems by
  curvilinear second-order vibrational Moller-Plesset theory. — [arXiv 1609.00430](https://arxiv.org/pdf/1609.00430)
- Annual Review of Physical Chemistry (2023, vol. 74): a Hamiltonian in one large-amplitude curvilinear
  torsion coordinate plus 3N-7 orthogonal normal coordinates; Zwier and Sibert groups developed effective
  Hamiltonians for the C-H stretch region. — [Annu. Rev. Phys. Chem. 74 (PDF)](https://www.annualreviews.org/docserver/fulltext/physchem/74/1/annurev-physchem-062422-021306.pdf)
- Nejad & Sibert (J. Chem. Phys. 2021, 154, 064301, trans-formic acid jet Raman): sixth-order canonical Van
  Vleck perturbation theory in curvilinear normal coordinates localised in one well; VPT2 energies are
  CVPT2 without resonances. — [JCP 2021](https://pubs.aip.org/aip/jcp/article/154/6/064301/199755/The-Raman-jet-spectrum-of-trans-formic-acid-and)
- Reduced-dimension variational + VPT2 combinations for methyl rotors in small molecules: pyruvic acid
  (variational reduced-dimensionality treatment alongside VPT2) and methylamine (3D flexible model). — [Pyruvic acid, PMC8303138](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8303138/); [Methylamine, PMC8495219](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8495219/)
- Methanol 12D variational and methanol IR/Raman with dihedral combinations for the torsion and curvilinear
  normal coordinates for the small-amplitude modes, torsion kept non-truncated. — [arXiv 2409.02505](https://arxiv.org/pdf/2409.02505); [arXiv 2602.17219](https://arxiv.org/pdf/2602.17219)

### Inferences
- For our use (B3LYP Hessians, 12-60 atoms, need for the 1400-1550 and 2850-3000 cm-1 bands), the cheapest
  scheme that addresses the actual coupling is: torsion out of the VPT2 indices (as now), plus an explicit
  check of the bends and stretches with a small Sibert/VPT2+K polyad that contains the CH stretches, the CH3
  scissor overtones and combinations, and optionally torsion-dependent harmonic frequencies along a relaxed
  scan (an adiabatic correction). This is my synthesis, not a published recipe for methyl aromatics.
- Full VSCF/VCI with a torsion coordinate scales poorly past ~15 atoms; MULTIMODE-style reaction-path work
  exists for small molecules only in what was found.

### Gaps
- Hanninen & Halonen and Kjaergaard local-mode CH3 papers, Suhm's methyl-aromatic jet spectra and Sibert's
  toluene/xylene CH-stretch fits were not retrieved in this pass.
- No coupled-channel (torsion + bends) number for any methyl aromatic was found.

## 4. Curvilinear / internal-coordinate VPT2 versus rectilinear normal coordinates

### Takeaway
Curvilinear VPT2 gives almost the same fundamentals for the CH3 stretches and deformations (1-4 cm-1
differences on acetic acid) but disentangles the torsion: in Cartesian coordinates the torsion's own
anharmonicity and its couplings to other modes are of comparable size, so separating it is unsafe; in
curvilinear coordinates the coupling is one to two orders of magnitude smaller. This is the most direct
published analogue of our noise observation.

### Cited Findings
- Mendolicchio, Bloino & Barone (J. Chem. Theory Comput. 2022, 18, 7603-7619), acetic acid, MP2/junTZ GVPT2
  (cm-1, harmonic / Cartesian / curvilinear / exp): CH3 torsion 75 / 85 / 85 / 93; CH3 a-str (A') 3227 /
  3083 / 3084 / 3051; CH3 s-str 3101 / 2992 / 2992 / 2944; CH3 a-str (A'') 3184 / 3044 / 3044 / 2996;
  CH3 a-def (A') 1490 / 1450 / 1448 / 1430; CH3 s-def 1421 / 1380 / 1377 / 1383; CH3 a-def (A'') 1498 /
  1440 / 1437 / 1430. The torsion without inter-mode couplings: Cartesian -5213 cm-1 ("completely
  unrealistic"), curvilinear 68 cm-1. In Cartesian coordinates the 1D anharmonicity of the CH3 rotation is
  comparable to its couplings with other modes, making LAM/SAM separation very difficult; in curvilinear
  coordinates it is far less entangled. The engine was added to the Gaussian platform. — [Mendolicchio, Bloino, Barone 2022, PMC9753597](https://pmc.ncbi.nlm.nih.gov/articles/PMC9753597/)
- Barone 2026 (preprint): methyloxirane, B3LYP/6-31G*: torsion-CH stretch (mode 19) coupling 1460.7 cm-1 in
  Cartesian-type coordinates vs 17.8 cm-1 in internal (ESALC-I); Euclidean partner norm 1761.6 -> 206.2
  cm-1; yet the mode 19 fundamental is 2916.19 vs 2916.41 cm-1. Mixed CH-stretch roots change intensity
  strongly with the representation (mode 23: 16.26 vs 36.44). — [arXiv 2610.20488](https://arxiv.org/html/2610.20488v1)
- Mendolicchio & Barone 2025: VPT2-C (curvilinear, generated from the bond pattern) and VPT2-R give identical
  total ZPVE (formaldehyde 5793 cm-1); HDCPT2 MAE ~7 (formic acid), ~9 cm-1 (methanol), C and R close;
  formamide's NH2 wag (exp 289 cm-1): rectilinear VCI 608, rectilinear PT 568, curvilinear 1D VCI 342 cm-1. — [JCP 2025, 162, 154114](https://pubs.aip.org/aip/jcp/article/162/15/154114/3344543/Vibrational-second-order-perturbation-theory-based)
- Rauhut (profile summary): for floppy molecules with internal rotations, curvilinear internal coordinates
  generally outperform rectilinear normal coordinates in vibrational structure calculations; optimized
  curvilinear coordinates in VSCF and VQDPT2. — [Rauhut ResearchGate profile](https://www.researchgate.net/profile/Guntram-Rauhut)

### Inferences
- The methyloxirane numbers (a 1460.7 cm-1 coupling in rectilinear coordinates collapsing to 17.8, with the
  fundamental unchanged to 0.2 cm-1) and the acetic-acid table suggest that in rectilinear VPT2 the large
  torsion couplings largely cancel in the final CH-stretch and CH3-deformation fundamentals. That fits our
  observation that the torsion's terms are the largest numerical-noise term: big, finite-difference-sensitive
  terms whose net effect is small. Zeroing them (decoupling) does not cancel them symmetrically, which may be
  why our bends move by up to 5.9 cm-1. A curvilinear VPT2 run on one methylimidazole would test this
  directly: if the curvilinear bends agree with the coupled rectilinear values, decoupling is the wrong
  remedy for us. This is an inference, not a published result.

### Gaps
- No curvilinear-VPT2 result for a methyl aromatic (toluene, picoline, methylimidazole) was found.
- Nejad's methyl-rotor VPT2 papers beyond formic acid and the PCCP 2020 paper were not reached.

## 5. Software: what implements what, and what runs on pyscf/psi4 inputs

### Takeaway
The hindered-rotor and curvilinear GVPT2 features are in Gaussian (closed, commercial; 1D-DVR in the
development version only); the only open, Python-scriptable VPT2 codes found are PyVPT2 (Psi4/QCEngine) and
Psience (McCoy group, VPT2 + DVR up to ~4D), and NITROGEN (Changala, Python, curvilinear coordinates) for
variational work. None found reads pyscf Hessians natively; with our finite-difference cubic/quartic
constants we would feed them in ourselves.

### Cited Findings
- Gaussian 16: GVPT2, DCPT2/HDCPT2, automatic hindered-rotor detection used for thermochemistry, curvilinear
  GVPT2 engine added to the platform; 1D-DVR hybrid in the development version. Closed source. — [JCTC 2022, PMC9753597](https://pmc.ncbi.nlm.nih.gov/articles/PMC9753597/); [JCP 2025](https://pubs.aip.org/aip/jcp/article/162/15/154114/3344543/Vibrational-second-order-perturbation-theory-based); [Frontiers 2020](https://www.frontiersin.org/journals/chemistry/articles/10.3389/fchem.2020.584203/full)
- TRINITY (Barone 2026): adiabatic DVR + perturb-then-diagonalize polyad transport; Gaussian supplies the
  fields; PySCF is mentioned as used for some controls; SI has a tensor archive and verification script;
  licence not stated. — [arXiv 2610.20488](https://arxiv.org/html/2610.20488v1)
- PyVPT2 (Philip Nelson): Python VPT2 on Psi4 (>= 1.8) or QCEngine, optional QCFractal parallel
  cubic/quartic constants; releases 0.0.1, 0.1.0, 0.1.1, 0.1.2; conda-forge; 2021-2024. A 2026 arXiv
  workflow built on PyVPT2 runs VPT2, DVPT2 and GVPT2 from a quartic force field (ML potential). — [PyPI pyvpt2](https://pypi.org/project/pyvpt2); [GitHub mirror philipmnel/pyvpt2](https://gh.r-mj.com/philipmnel/pyvpt2); [arXiv 2604.20040](https://arxiv.org/pdf/2604.20040)
- Psience (McCoy group, mccoygroup-psience on PyPI, Python >= 3.8): DVR, potential and dipole surfaces,
  VPT2 (arbitrary order supported), normal modes; DVR described as practical only for up to ~4 dimensions;
  documentation incomplete. — [Psience docs](https://mccoygroup.github.io/Psience); [PyPI](https://pypi.org/project/mccoygroup-psience); [GitHub fork rmhuch/Psience](https://github.com/rmhuch/Psience)
- NITROGEN (P. B. Changala): Python package for nuclear motion and rovibronic spectroscopy with general
  internal coordinates, `pip install nitrogen`; includes curvilinear vibrational analysis; older C version
  1.x. No methyl-specific feature found. — [PyPI Nitrogen](https://pypi.org/project/Nitrogen/); [NITROGEN docs](https://nitrogen-docs.readthedocs.io/en/latest/api/index.html)
- Molpro: automated anharmonic frequencies and ZPVE by VCI (Hrenar, Werner & Rauhut, J. Chem. Phys. 2007,
  126, 134108); configuration-selective VCI starting vectors for large-amplitude vibrations (Mathea &
  Rauhut). Commercial. — [Molpro manual](https://www.molpro.net/manual/doku.php?id=introduction_to_molpro); [search summary of a rovibrational paper citing Molpro VCI](https://www.sciencedirect.com/science/article/abs/pii/S0022285222000376)
- iGVPT2: interface to several quantum-chemistry packages for anharmonic corrections. — [arXiv 1704.02144](https://arxiv.org/pdf/1704.02144)
- SPECTRO (locally modified) used for VPT2 with polyads on methylated PAHs. — [Mackie et al. 2018](https://pubs.rsc.org/en/content/articlehtml/2018/cp/c7cp06546a)
- ElVibRot / MCTDH used variationally with bound quartic force fields. — [arXiv 2609.18654](https://arxiv.org/pdf/2609.18654)

### Inferences
- For a pyscf-based pipeline the realistic options are: keep our own VPT2 and add (i) a 1D periodic DVR of
  the torsion on a relaxed B3LYP scan (few dozen constrained optimisations per molecule; Psience's DVR or a
  hand-written sine/Fourier DVR), and (ii) a small polyad for the CH stretch / scissor region. A curvilinear
  VPT2 test needs either Gaussian 16 (the Mendolicchio-Bloino-Barone engine) or our own transformation of
  the force field to internal coordinates; NITROGEN can supply the curvilinear kinetic terms.

### Gaps
- Not verified in this pass: CFOUR (xvib2/VPT2), Q-Chem (TOSH, VPT2, VCI), MULTIMODE, SINDO, GAMESS VSCF,
  pyvibms, PyPES, Mitchell/Sibert codes; their hindered-rotor handling and versions remain open.
- Puzzarini, Bloino, Tasinato & Barone Chem. Rev. 2019 (10.1021/acs.chemrev.9b00007) recommendations were
  only seen second-hand through the Barone/Bloino papers above; the V30 benchmark's methyl handling was not
  re-read (already known).
