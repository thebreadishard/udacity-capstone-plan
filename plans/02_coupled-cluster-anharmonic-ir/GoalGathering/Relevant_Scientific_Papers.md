# Contextual Scientific Bibliography

This document captures the relevant scientific papers discussed during the goal gathering phase. This bibliography traces the explicit computational track record of achieving chemically precise infrared spectra for molecules, culminating in the goal of decoding Polycyclic Aromatic Hydrocarbons (PAHs).

> **Updated 2026-08-23 for the R3 pivot.** Items 26–35 were added, and items 12, 14, 15, 16, 17 and 19
> were re-weighted, after a literature check on 2026-08-23. Three of the pre-existing entries turned
> out to describe work that the **old** plan's Module 08 exit had already been overtaken by — that
> discovery is what motivated the pivot. Every arXiv identifier and journal reference below was
> fetched, not recalled.

## Foundational Quantum Machine Learning
1. **Quantum chemistry structures and properties of 134 kilo molecules** (Ramakrishnan et al., *Scientific Data*, 2014)
   - *Significance:* Introduces the baseline QM9 dataset used extensively for molecular ML training.
2. **SchNet: A continuous-filter convolutional neural network for modeling quantum interactions** (Schütt et al., *NeurIPS*, 2017)
   - *Significance:* Defined the requirement for continuous-filter architectures to ensure PES mathematical smoothness.
3. **Machine Learning Molecular Dynamics** (Gastegger et al., *Chemical Science*, 2017)
   - *URL:* [Machine-learning molecular dynamics](https://pubs.rsc.org/sc/article/8/10/6924/584158/Machine-learning-molecular-dynamics-for-the)
   - *Significance:* Bypassed stationary static derivatives by running MLMD simulations over time.

## Solving Exact Calculus (Chemical Precision)

> **Promoted 2026-08-23.** Items 4 and 5 were filed here during goal-gathering and then largely ignored
> while the plan pursued a voxel field PES. Under R3 they are no longer background — they *are* the
> method: transfer-learn an ML surface to CCSD(T) quality, then extract high-order derivatives from it.
> The section heading was right before the plan was.

4. **MP2 Is Not Good Enough: Transfer Learning ML Models for Accurate VPT2 Frequencies** (Käser, Boittier, Upadhyay & Meuwly, *JCTC*, 2021)
   - *URL:* [arXiv:2103.05491](https://arxiv.org/abs/2103.05491) · PDF: `Papers/04_Kaser2021_TransferLearning_CCSDT.pdf`
   - *Attribution corrected 2026-08-23:* this entry previously read *"Transfer Learning to CCSD(T): Accurate Anharmonic Frequencies from Machine Learning Models (Nandi et al., JCTC, 2021)"*. The stored PDF is arXiv:2103.05491, and [Papers/README.md](../../../Papers/README.md) has always named it correctly as Käser et al. The **title and authors in this bibliography were wrong**; the significance was right. Caught only because the R3 literature sweep re-added the same paper as a "new" item — a reminder that a bibliography entry written from recall is not a citation.
   - *Significance:* The "NN + VPT2" protocol: high-dimensional NN potentials learned at MP2, CCSD(T) and CCSD(T)-F12 levels, with transfer learning used for the largest molecules and highest levels, from which harmonic and VPT2 frequencies are extracted. Anharmonic frequencies land within 20 cm⁻¹ of experiment for ~90 % of modes and within 10 cm⁻¹ for >60 % at the best level; MP2-quality surfaces produce outliers up to 150 cm⁻¹. **Now load-bearing, and the title is the lesson:** the level of theory under the ML model, not the ML model, sets the ceiling. This is the mechanism by which the gold rung reaches the quartic force field.
5. **ANI-1ccx-gelu Universal Interatomic Potential and Its Fine-Tuning: Toward Accurate and Efficient Anharmonic Vibrational Frequencies** (Dral et al., *JPCL*, 2025)
   - *Significance:* The capstone architectural fix. Exchanged standard activation functions for GELU, completely resolving the "wrinkly PES" issue to allow error-free extraction of the Hessian/VPT2 highest-order derivatives. **Now a gate, not a remark:** G2 must measure step-size stability of the cubic force constants, and this paper is both the reason why and the declared fallback if the selected MLIP fails that test.

## Equivariant Neural Networks (The Analytical Hessian Solution)
6. **E(3)-Equivariant Neural Network Potentials** (e.g., NequIP, Allegro)
   - *Significance:* Rather than just ensuring mathematical smoothness via activation functions, these architectures explicitly preserve 3D rotational and translational symmetries. They require significantly less training data than standard continuous-filter models to achieve CCSD(T)-level accuracy when modeling complex PES features.
7. **NewtonNet: A Newtonian Message Passing Network**
   - *Significance:* Distinctly built to be efficiently differentiated to construct analytical Hessians. This provides an alternative structural solution by deriving exact vibrational frequencies orders of magnitude faster than traditional mathematical extraction methods.

## Astrochemical PAH Progress
8. **Early High-Throughput PAH Approximations** (*ApJ*, 2020)
   - *URL:* [High-Throughput Approximations](https://iopscience.iop.org/article/10.3847/1538-4357/abb5b6/meta)
   - *Significance:* Applied standard ML to PAH IR spectra matching (without true chemical quantum precision).
9. **Empirical Mapping of PAH Emissions** (Zhu et al., *ApJ*, 2021)
   - *URL:* [Empirical Mapping](https://iopscience.iop.org/article/10.3847/1538-4357/ac2c78/meta)
   - *Significance:* Interpreted correlations between observed PAH emission features to prioritize target extraction.
10. **Charge/Ionization Awareness** (Meng et al., *MNRAS Letters*, 2023)
   - *URL:* [Ionization Awareness](https://academic.oup.com/mnrasl/article/525/1/L29/7216507)
   - *Significance:* Introduced deep space charge-aware states (anions/cations/neutrals) crucial for mapping shifting PAH IR frequencies.
11. **Refining PAH Charge Models** (Zakuskin et al., *JCIM*, 2025)
   - *URL:* [Refining Charge Models](https://pubs.acs.org/doi/full/10.1021/acs.jcim.5c00372)
   - *Significance:* Implemented deep learning architectures bridging the gap between classical prediction and deep space charge demands.
12. **MLMD Meets PAHs** (Mai, Wang, Pan, Schörghuber, Kovács, Carrete & Madsen, *MNRAS* 541, 3073, 2025)
    - *URL:* [MLMD Meets PAHs](https://academic.oup.com/mnras/article/541/4/3073/8206142) · [arXiv:2503.05120](https://arxiv.org/abs/2503.05120)
    - *Significance (revised 2026-08-23):* **The single most important paper for scoping this thesis.** Anharmonic IR spectra via machine-learning MD for **1,704 PAHs from the NASA Ames PAHdb, up to 216 carbon atoms**, at several temperatures, scaling linearly with system size. This is the pre-pivot plan's Module 08 method (classical MD + dipole ACF) already executed far beyond anything that plan proposed. Delivering R2 on benzene would therefore not have been a contribution. Under R3 this paper is the **state of the art to be improved on**, and the improvement is the gold anchor plus quantum nuclear motion, not more MD.
13. **Targeting Cyanated PAHs** (Fortenberry et al., *ACS Earth Space Chem.*, 2025)
    - *URL:* [Targeting CN-PAHs](https://pubs.acs.org/doi/full/10.1021/acsearthspacechem.5c00249)
    - *Significance:* Expanded reference dataset generation to handle astrochemical targets like recently discovered CN-PAHs.
14. **The Pragmatic DFT Scaling Solution** (*ACS Omega*, 2025)
    - *URL:* [Pragmatic Scaling Solution](https://pubs.acs.org/doi/full/10.1021/acsomega.5c10225)
    - *Significance (revised 2026-08-23):* Used ML to systematically correct cheap DFT harmonic scaling factors to achieve a 5 cm⁻¹ MAE without massive perturbation overhead. Under R3 this is the **status-quo baseline that gate G0 must reproduce and that the thesis must beat**. A 5 cm⁻¹ MAE from scaled harmonic B3LYP is also the number that makes the R3 tolerance in [Overarching_Goal.md](Overarching_Goal.md) §1 non-trivial: an anharmonic method that lands at 10 cm⁻¹ has not earned its cost.
        
## Cosmic Application
15. **Observational Application to Current JWST Data** (*A&A*, 2026)
    - *URLs:* 
      - [JWST A&A Study 1](https://www.aanda.org/articles/aa/abs/2026/04/aa59248-26/aa59248-26.html)
      - [JWST A&A Study 2](https://www.aanda.org/articles/aa/abs/2026/06/aa59999-26/aa59999-26.html) = Wang (2026), [arXiv:2602.12531](https://arxiv.org/abs/2602.12531), DOI 10.1051/0004-6361/202659999
    - *Significance (corrected 2026-08-23):* The earlier summary here — "researchers directly identify the isotopic makeup of deep space PAHs" — **was wrong for Study 2** and is retracted. Study 2 is *Full-spectrum infrared fingerprinting*: a random-forest classifier trained on 23,000+ spectra that assigns PAH **size and charge categories** (F1 = 0.963 over 12 categories) and finds that size diagnostics are charge-dependent. That is spectral **classification into categories**, not identification of named species — which is precisely the gap R3's §3.C fail-closed identification is aimed at. Study 1 has not been re-verified; treat it as unchecked until it is.
16. **Infrared Spectroscopy of Matrix Isolated Polycyclic Aromatic Hydrocarbons. 1. PAHs Containing Two to Four Rings** (Hudgins & Sandford, *J. Phys. Chem. A* **102**(2), 329–343, 1998)
    - *URL:* [ACS](https://pubs.acs.org/doi/10.1021/jp9834816) · DOI:10.1021/jp9834816 · [Crossref record](https://api.crossref.org/works/10.1021/jp9834816)
    - *Bibliographic data verified 2026-08-28* against Crossref and Unpaywall: title, authors (both NASA Ames), volume, issue, pages and year are as stated. **Closed access — Unpaywall reports no open copy and no repository copy.** The freely available Hudgins papers on NASA NTRS are the *cation* studies (parts 1–3 of the cation series, Hudgins & Allamandola); this neutral two-to-four-ring paper is not among them.
    - *Significance (VERIFIED 2026-08-28, via PAHdb rather than the paper):* The article is closed, but the NASA Ames PAH IR Spectroscopic Database (item 18) carries the same laboratory spectra and names this paper as the source for each of them. Band positions were read from the experimental library, version 2.00, with the species uid recorded, and are reproduced in [pahdb_experimental_2026-08-28.py](../probes/pahdb_experimental_2026-08-28.py). Argon matrix, CsI window at 10–15 K, neutral species.
        - **The third-hand numbers were partly wrong.** Tetracene 742.9 cm⁻¹ was correct. Chrysene is **761.0** cm⁻¹ (114 km/mol, the strongest band in the window), not the "744–748" that was quoted. **Triphenylene has no experimental spectrum in this database at all**, so the quoted "740.8" has no source here and must not be used.
        - The measured quartet band across five molecules spans **60.2 cm⁻¹** (naphthalene 785.8, anthracene 725.6, phenanthrene 735.0, tetracene 742.9, chrysene 761.0) — *wider* than the 43.4 cm⁻¹ this repository computes. The failure of a class-keyed atlas is therefore a property of the molecules, not of B3LYP.
        - This repository's quartet bands sit 7.1 cm⁻¹ from the measurements on average, worst case naphthalene at 15.6 cm⁻¹ — just outside the 15 cm⁻¹ matrix tolerance — from harmonic B3LYP with a single scale factor fitted on benzene alone. Every error but one is negative, so that scale factor is slightly too small.

## Architecture and Prior Art (PDFs 16–20)

> **Re-scoped 2026-08-23.** Items 16, 17 and 19 underpinned the FNO-NCA **energy** functional, which is
> no longer the production PES. They remain relevant **only** to the dipole-moment-surface leg, where
> the deformation-density field competes against an equivariant-tensor DMS and a charge DMS under
> pre-registration. If that bake-off is lost, these three become history rather than method.

16. **Fourier Neural Operator for Parametric Partial Differential Equations** (Li et al., *arXiv:2010.08895*, 2020)
    - *Significance:* The core method underpinning the FNO half of the hybrid FNO-NCA architecture. **Now scoped to the DMS leg only.**
17. **V2Rho-FNO: Fourier Neural Operator for Electronic Density Prediction** (Jin et al., *arXiv:2603.15669*, 2026)
    - *Significance:* Closest prior art identified in the original novelty check — external-potential → density mapping, with none of the MD / force / spectral machinery. **Note:** it is *not* the closest prior art overall; see the density-functional lineage below, which the original check missed. **Now scoped to the DMS leg only.**
18. **The NASA Ames PAH IR Spectroscopic Database** (Boersma et al., *ApJS* 211, 8, 2014)
    - *Significance:* Matrix-shift correction reference for gas-phase vs matrix-isolation comparisons. **Promoted 2026-08-23:** under R3 this is no longer a footnote — PAHdb is the Module 02 dataset, the source of the scaled-harmonic status-quo baseline, and one of the two candidate frozen products for the §3.C identification.
19. **Growing Neural Cellular Automata** (Mordvintsev et al., *Distill*, 2020, DOI:10.23915/distill.00023)
    - *Significance:* Stabilization techniques (stochastic cell updates, gradient clipping) for the NCA half of the hybrid architecture. **Now scoped to the DMS leg only.**
20. **Aitomia: Intelligent Assistant for AI-Driven Atomistic and Quantum Chemical Simulations** (Hu, Dral et al., *arXiv:2505.08195*, 2025)
    - *Significance:* Background on the MLatom platform; cited as an example of the conventional atom-centric NN approach this project departs from.

## Machine-Learned Density Functionals — the lineage this thesis actually sits in

Added 2026-08-22 to close [round-2](../../01_voxel-field-pes/GoalGathering/Professor_Review_2026-08-22_Round2.md) blocking issue 9. The Distilled Plan's \(E=E_{\mathrm{es}}[\rho]+\int\varepsilon_\theta\,dV\) **is** machine-learned orbital-free DFT. Positioning against this lineage is in Distilled Plan §2.1.

21. **Finding Density Functionals with Machine Learning** (Snyder, Rupp, Hansen, Müller & Burke, *Phys. Rev. Lett.* 108, 253002, 2012)
    - *URL:* [arXiv:1112.5441](https://arxiv.org/abs/1112.5441) · DOI:10.1103/PhysRevLett.108.253002
    - *Significance:* Origin of the field. Machine-learns the kinetic-energy functional for 1D non-interacting fermions and confronts the functional-derivative problem — the same derivative this plan obtains by autograd.
22. **By-passing the Kohn–Sham equations with machine learning** (Brockherde, Vogt, Li, Tuckerman, Burke & Müller, *Nature Communications* 8, 872, 2017)
    - *URL:* [arXiv:1609.02815](https://arxiv.org/abs/1609.02815) · DOI:10.1038/s41467-017-00839-3
    - *Significance:* **The closest functional prior art to Route B.** Learns the density–potential *and* energy–density maps directly, then reproduces energies across geometries generated by molecular dynamics. That is \(\mathbf{R}\to\rho\to E\) plus MD — this plan's pipeline, at DFT label quality.
23. **Kohn–Sham equations as regularizer: building prior knowledge into machine-learned physics** (Li, Hoyer, Pederson, Sun, Cubuk, Riley & Burke, *Phys. Rev. Lett.* 126, 036401, 2021)
    - *URL:* [arXiv:2009.08551](https://arxiv.org/abs/2009.08551) · DOI:10.1103/PhysRevLett.126.036401
    - *Significance:* Embedding the physics solve inside training acts as an implicit regularizer and greatly improves generalization — direct evidence that *how much physics is fixed vs learned* is the variable that controls transferability, which is exactly this thesis's §2 question.
24. **Overcoming the Barrier of Orbital-Free Density Functional Theory for Molecular Systems Using Deep Learning (M-OFDFT)** (Zhang, Liu, You, Liu, Zheng, Lu, Wang, Zheng, Shao et al., *Nature Computational Science*, 2024)
    - *URL:* [arXiv:2309.16578](https://arxiv.org/abs/2309.16578) · DOI:10.1038/s43588-024-00605-8
    - *Significance:* Both the sharpest warning and the sharpest encouragement. Warning: they state that building **essential non-locality** into the functional was required, using density expansion coefficients in an atomic basis — a *local* \(\varepsilon_\theta(\rho,\lvert\nabla\rho\rvert)\) is the form the field already found insufficient. Encouragement: their model **extrapolates to molecules much larger than those seen in training**, i.e. part of the “density representations size-extend” claim is already demonstrated — which sharpens what this thesis may still claim as its own.
25. **On the Stability of Molecules in the Thomas–Fermi Theory** (Teller, *Rev. Mod. Phys.* 34, 627, 1962)
    - *URL:* DOI:10.1103/RevModPhys.34.627
    - *Significance:* Teller's theorem — in pure Thomas–Fermi theory, a purely *local* functional of \(\rho\), molecules do not bind at all. The historical boundary condition on any local kinetic-energy functional, and the reason §2.1 treats \(\varepsilon_\theta\) as a narrow-manifold interpolator rather than a universal KEDF.

*(Excluded: "Protein Spectra" (Ye et al., 2020) and "Isomer Clustering" (Fu & Hopkins, 2017) as they were explicitly identified in the review as unrelated to the overarching IR precision narrative.)*

---

## The R3 evidence base — what makes coupled-cluster-anchored anharmonic PAH IR reachable

Added 2026-08-23. These items are the technical justification for
[Restructure_Proposal_2026-08-23_Project12_in_Module08.md](Restructure_Proposal_2026-08-23_Project12_in_Module08.md).
All identifiers were fetched from arXiv on 2026-08-23.

### Nuclear motion at PAH size (the R3 method)

26. **VPT2 Calculations of Vibrational Energies of CH₃COOC₆H₄COOH Done in Seconds on a Laptop Using a Machine Learned Potential** (Kotaru, Qu, Nandi, Houston & Bowman, 2026)
    - *URL:* [arXiv:2604.20040](https://arxiv.org/abs/2604.20040)
    - *Significance:* **The enabler.** Released Fortran/Python software that builds a quartic force field and runs VPT2 **directly from a machine-learned potential**. Applied to 21-atom aspirin: 32,509 unique cubic force constants in roughly one minute, described by the authors as the first quantum anharmonic results for a molecule that size. Naphthalene (18 atoms), anthracene/phenanthrene (24) and pyrene (26) sit inside this envelope. The authors also state the point R3 rests on: quantum anharmonic energies for large molecules are "currently obtained overwhelmingly from classical molecular dynamics simulations, which cannot describe strong anharmonicity."

### Transfer learning to coupled-cluster quality (why the campaign is hundreds, not thousands)

27. **Transfer Learned Potential Energy Surfaces: Accurate Anharmonic Vibrational Dynamics and Dissociation Energies for the Formic Acid Monomer and Dimer** (Käser & Meuwly, *PCCP*, 2021)
    - *URL:* [arXiv:2109.08407](https://arxiv.org/abs/2109.08407) · DOI 10.1039/D1CP04393E
    - *Significance:* The companion demonstration to item 4, and the more honest one. VPT2 on a transfer-learned CCSD(T)-quality PES reproduces the experimental formic-acid OH stretch to within 22 cm⁻¹, and the dissociation energy to −0.01 kcal/mol of experiment — but it also documents where the method strains: the OH-stretch is the hard mode, finite-temperature MD shifts it in *opposite* directions for monomer and dimer, and above 1000 K the transfer-learned surface dissociates the dimer. Read as the realistic expectation for R3's hardest band family (3.3 μm C–H stretch), and as the reason MD+FFT is a diagnostic rather than the score.
    - **Note:** this slot originally held arXiv:2103.05491, which turned out to duplicate item 4 (see the correction there). It was replaced rather than left as a gap.
28. **Transfer-Learned Potential Energy Surfaces: Towards Microsecond-Scale Molecular Dynamics Simulations in the Gas Phase at CCSD(T) Quality** (Käser & Meuwly, *JCP* 158, 2023)
    - *URL:* [arXiv:2303.11685](https://arxiv.org/abs/2303.11685)
    - *Significance:* Transfer learning lifts a PES from a cheap level (even Hartree-Fock/double-zeta) to CCSD(T) quality using **on the order of 100 high-level points**, retaining barrier heights, harmonic frequencies and tunnelling splittings. This is what replaces the pre-pivot plan's ≥2,000 H₂O / ≥5,000 benzene volumetric campaigns.

### The gold rung (why a coupled-cluster anchor on PAHs is affordable)

29. **Explicitly correlated coupled cluster method for accurate treatment of open-shell molecules with hundreds of atoms** (Kumar, Neese & Valeev, *JCP* 153, 094105, 2020)
    - *URL:* [arXiv:2008.03237](https://arxiv.org/abs/2008.03237)
    - *Significance:* Near-linear-scaling DLPNO-CCSD(T)-F12, closed **and** open shell. Coupled-cluster energies near the CBS limit for systems above 550 atoms and 5,000 basis functions, on a single multi-core computer in under three days, RMSD 0.3 kcal/mol against extrapolated canonical CCSD(T). **A gold rung on PAH-sized aromatics, including cations, is a workstation job.** This single result retires most of what [Project 10](Horizon/10_Size_Extensive_Aromatic_PES.md) was created to solve.
30. **Performance of Localized Coupled Cluster Methods in a Moderately Strong Correlation Regime: Hückel-Möbius Interconversions in Expanded Porphyrins** (Sylvetsky, Banerjee, Alonso & Martin, *JCTC* 16, 3641, 2020)
    - *URL:* [arXiv:2001.08641](https://arxiv.org/abs/2001.08641)
    - *Significance:* **The caveat that makes gate G1 a measurement rather than a formality.** For delocalized, static-correlation-prone π systems, DLPNO-CCSD(T) and even DLPNO-CCSD(T1) carry significant errors unless TightPNO cutoffs are used, and LNO-CCSD(T) with tight settings is what reproduces canonical CCSD(T) to sub-kcal. Aromatics are exactly that regime, so the local-vs-canonical difference must be measured per band family and per charge state before the local method is trusted on larger rings. This is error term (B) of the four-term budget.

### PAH-specific state of the art (what must be beaten, and against which experiment)

31. **Anharmonic infrared spectra of cationic pyrene and superhydrogenated derivatives** (Tang, Doktor, Jaganathan, Palotás, Oomens, Hornekær & Hammer, *JCP* 163, 044304, 2025)
    - *URL:* [arXiv:2504.11898](https://arxiv.org/abs/2504.11898)
    - *Significance:* MLIP-accelerated anharmonic IR of **cationic pyrene** compared against gas-phase IRMPD action spectroscopy. Supplies a named modern experimental standard at exactly the size and charge state of ladder rung 3. Also reports the honest nuance: harmonic-plus-empirical-scaling already reproduces the band profile of pristine and partially superhydrogenated pyrene cations, and MD-based anharmonic treatment becomes *mandatory* only for the fully superhydrogenated case — a direct warning that R3 must demonstrate where anharmonicity actually pays.
32. **A Universal Deep Learning Force Field for Molecular Dynamic Simulation and Vibrational Spectra Prediction (DetaNet)** (Ji, Zhang, Zou, Jiang, Jiang, Luo & Hu, 2025)
    - *URL:* [arXiv:2510.04227](https://arxiv.org/abs/2510.04227)
    - *Significance:* Equivariant tensor-attention network trained on QMe14S (186,102 molecules with energies, forces, **dipoles and polarizabilities**), producing IR and Raman spectra from MLMD and RPMD, benchmarked on PAHs at near-experimental accuracy. Two consequences: it is further evidence that R2 is a solved problem, and its dipole/polarizability head is the archetype of the **DMS-tensor** leg in the dipole-surface bake-off.
33. **Anharmonic Infrared Emission of Cyano-Substituted Polycyclic Aromatic Hydrocarbon Molecules: Cyanonaphthalenes as a Case Study** (Chen, Li & Li, *A&A*, 2026)
    - *URL:* [arXiv:2607.20015](https://arxiv.org/abs/2607.20015)
    - *Significance:* **The template for §3.C, and the gap it leaves.** VPT2 anharmonic properties plus an optimized microcanonical sampling algorithm produce environment-dependent IR **cascade emission** spectra for neutral, cationic and anionic cyanonaphthalenes — the excitation machinery [Project 12](Horizon/12_Astrophysical_PAH_Identification.md) §3.1 demands, already built. It is computed at **B3LYP/N07D**. Every anharmonic PAH spectrum in this literature rests on DFT with an unquantified electronic-structure error; supplying a measured coupled-cluster anchor and the four-term budget underneath that machinery is what R3 contributes.

### The hybrid quartic force field — items 37–39 (added 2026-08-26, Round 4 Pass B)

These arrived through the review, not the original sweep, and they changed the architecture. They are
the reason §6.4 splits \(\omega\) from \(\delta_{\mathrm{anh}}\).

37. **Anharmonic force fields and thermodynamic functions using density functional theory** (Boese, Klopper & Martin, *Mol. Phys.* 103, 863, 2005)
    - *URL:* [arXiv:physics/0411065](https://arxiv.org/abs/physics/0411065) · DOI:10.1080/00268970512331339369
    - *Significance:* **The origin of the hybrid split this plan now uses.** Establishes DFT as a
      cost-effective source of **anharmonic** corrections *for use in conjunction with* benchmark ab
      initio methods for the rest. Same Jan Martin as item 30's local-coupled-cluster caveat — the
      plan was already citing him about where correlation matters, while ignoring him about where it
      does not.
38. **Combining quantum mechanics and machine-learning calculations for anharmonic corrections to vibrational frequencies** (Lam, Abdul-Al & Allouche, *JCTC* 15, 2020)
    - *URL:* [arXiv:1909.12661](https://arxiv.org/abs/1909.12661) · DOI:10.1021/acs.jctc.9b00964
    - *Significance:* **The closest published precedent for §6.4, and a warning attached to it.**
      Quantum mechanics for the harmonic part, machine learning for the anharmonic corrections, over
      37 molecules, with linear rather than quadratic scaling. It works — and it reports **RMSD
      21 cm⁻¹** against its reference level and **23 cm⁻¹** against experiment, which is *twice* this
      project's frozen 10 cm⁻¹ tolerance. Cited in the 2026-08-26 freeze precisely so the tolerance is
      not quietly relaxed to match it. Same group as item 8's PAH ML work.
39. **Anharmonic vibrational spectroscopy of Polycyclic Aromatic Hydrocarbons** (Mulas, Falvo, Cassam-Chenaï & Joblin, *JCP* 149, 2018)
    - *URL:* [arXiv:1809.05669](https://arxiv.org/abs/1809.05669) · DOI:10.1063/1.5050087
    - *Significance:* Anharmonic treatment of **pyrene and coronene** with full resonance handling —
      the size regime this plan's bonus rungs target. Two findings that cut both ways: band positions
      are *significantly improved* over harmonic DFT, and *"the main limitation being the accuracy of
      the underlying calculations of the quartic force field"*. The second is the sentence gate G1b
      exists to test.

**Reported but not yet verified.** Round 4 Pass B cited *Watrous et al. (2023)* for hybrid QFFs
reaching full-CC-QFF accuracy at under a quarter of the cost. The author and research programme are
verified — A. G. Watrous publishes quartic force fields for astrochemistry with Ryan Fortenberry
([arXiv:2109.11605](https://arxiv.org/abs/2109.11605)) — but the specific 2023 result is not on arXiv
and **has not been checked against its DOI**. It is recorded here as reviewer-reported and must not be
cited in the thesis until verified. The repository rule is never cite from recall, and that applies to
a reviewer's recall too.

### Tooling adopted (decision 5)

34. **MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields** (Batatia, Kovács, Simm, Ortner & Csányi, *NeurIPS*, 2022)
    - *URL:* [arXiv:2206.07697](https://arxiv.org/abs/2206.07697) · [OpenReview](https://openreview.net/forum?id=YPpSngE-ZU) · code [github.com/ACEsuit/mace](https://github.com/ACEsuit/mace) (**MIT**)
    - *Significance:* The architecture selected for the production PES. Four-body messages cut the required message-passing iterations to two. Exactly rotation-equivariant and size-extensive by construction — both properties the voxel field had to fight for and gate (see Distilled §8 item 13). float64 training is supported, which matters because a quartic force field needs numerically stable third and fourth derivatives.
35. **MACE-OFF: Transferable Short Range Machine Learning Force Fields for Organic Molecules** (Kovács, Moore, Browning, Batatia, Horton, Pu, Kapil, Witt, Magdău, Cole & Csányi, 2023, rev. 2025)
    - *URL:* [arXiv:2312.15211](https://arxiv.org/abs/2312.15211) · weights [github.com/ACEsuit/mace-off](https://github.com/ACEsuit/mace-off) (**ASL**, academic/non-commercial)
    - *Significance:* The organic-chemistry foundation-model line, and the **fallback** PES starting point. Verified 2026-08-23: MACE-OFF is short-range and covers **neutral** organics, so it cannot serve the cation rungs of the molecule ladder on its own. The **MACE-OMOL-0** checkpoint (OMol25, ωB97M-VV10, charge/spin embedding) is therefore the primary starting point. Note the paper reports reproducing a vibrational spectrum for a solvated protein — evidence the architecture is spectroscopy-capable, at envelope level.
36. **MACE-POLAR-1: A Polarisable Electrostatic Foundation Model for Molecular Chemistry** (Batatia, Baldwin, Kuryla, Hart, Kasoar, Elena, Moore, Gawkowski, Shi, Kapil, Kourtis, Magdău & Csányi, 2026)
    - *URL:* [arXiv:2602.19411](https://arxiv.org/abs/2602.19411)
    - *Significance:* **The DMS-tensor leg of the dipole-surface bake-off, and an unusually direct answer to two of this project's problems.** Extends MACE with explicit long-range electrostatics and induction: learnable charge **and spin** densities updated through polarisable iterations, then global charge equilibration via learnable Fukui functions to fix total charge and total spin. Trained on OMol25 (100 million hybrid-DFT calculations). Two consequences for R3: (i) variable **charge and spin states** are handled natively, which is exactly what the neutral/cation ladder needs and what MACE-OFF cannot do; (ii) it emits **interpretable spin-resolved charge densities** and responds to external fields — i.e. it is a learned electron-density model in the atomistic idiom, and therefore the honest competitor for the voxel deformation-density DMS rather than a strawman.
